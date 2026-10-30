#include "FGWeather.h"

#include "FGBelt.h"
#include "FGBuildable.h"
#include "FGTowerSite.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "EngineUtils.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "Materials/MaterialParameterCollection.h"

AFGWeather::AFGWeather()
{
	PrimaryActorTick.bCanEverTick = true;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
}

void AFGWeather::BeginPlay()
{
	Super::BeginPlay();
	OceanMPC = LoadObject<UMaterialParameterCollection>(nullptr, TEXT("/Game/Blue/Materials/MPC_Ocean.MPC_Ocean"));
	for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It)
	{
		Sun = *It;
		BaseSunIntensity = It->GetLightComponent()->Intensity;
		break;
	}
	for (TActorIterator<AExponentialHeightFog> It(GetWorld()); It; ++It)
	{
		Fog = *It;
		BaseFogDensity = It->GetComponent()->FogDensity;
		break;
	}
}

AFGWeather* AFGWeather::Get(const UWorld* World)
{
	if (!World)
	{
		return nullptr;
	}
	for (TActorIterator<AFGWeather> It(const_cast<UWorld*>(World)); It; ++It)
	{
		return *It;
	}
	return nullptr;
}

float AFGWeather::GetIntensity(const UWorld* World)
{
	const AFGWeather* Weather = Get(World);
	return Weather ? Weather->Intensity : 0.f;
}

void AFGWeather::StartStorm(float Duration)
{
	bStorm = true;
	StormLeft = Duration;
	NextFlash = 2.f;
	StormCount++;
}

void AFGWeather::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	AFGTowerSite* Tower = nullptr;
	for (TActorIterator<AFGTowerSite> It(GetWorld()); It; ++It)
	{
		Tower = *It;
		break;
	}

	if (!bStorm)
	{
		if (Tower && Tower->CurrentPhase >= StartPhaseIndex)
		{
			if (!bScheduled)
			{
				bScheduled = true;
				Timer = FirstStormDelay;
			}
			Timer -= DeltaSeconds;
			if (Timer <= 0.f)
			{
				StartStorm(FMath::FRandRange(MinDuration, MaxDuration));
			}
		}
	}
	else
	{
		StormLeft -= DeltaSeconds;
		if (StormLeft <= 0.f)
		{
			bStorm = false;
			Timer = FMath::FRandRange(MinGap, MaxGap);
		}
	}

	Intensity = FMath::FInterpConstantTo(Intensity, bStorm ? 1.f : 0.f, DeltaSeconds, 0.12f);

	if (Tower)
	{
		UpdatePollution(Tower, DeltaSeconds);
	}
	UpdateVisuals(Tower, DeltaSeconds);
	if (Intensity > 0.5f)
	{
		SnapBelts(DeltaSeconds);
	}
}

void AFGWeather::UpdatePollution(AFGTowerSite* Tower, float DeltaSeconds)
{
	// Working polluters (burners) push the sea down; cleaners (negative Pollution) pull it up.
	float Rate = 0.f;
	for (TActorIterator<AFGBuildable> It(GetWorld()); It; ++It)
	{
		if (It->bGhost || It->Row.Pollution == 0.f)
		{
			continue;
		}
		const bool bCounts = It->Row.Pollution < 0.f || It->IsWorking();
		if (bCounts)
		{
			Rate += It->Row.Pollution;
		}
	}
	float Change = -Rate * 0.0008f * DeltaSeconds;
	if (Rate <= 0.f)
	{
		Change += 0.0003f * DeltaSeconds; // the sea slowly heals on its own
	}
	Tower->OceanHealth = FMath::Clamp(Tower->OceanHealth + Change, 0.f, 1.f);
}

void AFGWeather::UpdateVisuals(AFGTowerSite* Tower, float DeltaSeconds)
{
	// Lightning: short white flashes while the storm is strong.
	FlashLeft = FMath::Max(0.f, FlashLeft - DeltaSeconds);
	if (Intensity > 0.6f)
	{
		NextFlash -= DeltaSeconds;
		if (NextFlash <= 0.f)
		{
			FlashLeft = 0.18f;
			NextFlash = FMath::FRandRange(3.5f, 9.f);
		}
	}
	FlashAlpha = FlashLeft > 0.f ? FMath::Clamp(FlashLeft / 0.18f, 0.f, 1.f) : 0.f;

	if (ADirectionalLight* Light = Sun.Get())
	{
		const float Dim = FMath::Lerp(BaseSunIntensity, BaseSunIntensity * 0.15f, Intensity);
		Light->GetLightComponent()->SetIntensity(FlashLeft > 0.f ? BaseSunIntensity * 2.5f : Dim);
	}
	if (AExponentialHeightFog* FogActor = Fog.Get())
	{
		FogActor->GetComponent()->SetFogDensity(FMath::Lerp(BaseFogDensity, 0.045f, Intensity));
	}
	if (OceanMPC)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(this, OceanMPC, TEXT("Storm"), Intensity);
		UKismetMaterialLibrary::SetScalarParameterValue(this, OceanMPC, TEXT("Murk"), Tower ? 1.f - Tower->OceanHealth : 0.f);
	}
}

void AFGWeather::SnapBelts(float DeltaSeconds)
{
	TArray<FVector> Breakwaters;
	for (TActorIterator<AFGBuildable> It(GetWorld()); It; ++It)
	{
		if (!It->bGhost && It->RowName == TEXT("Breakwater"))
		{
			Breakwaters.Add(It->GetActorLocation());
		}
	}
	for (TActorIterator<AFGBelt> It(GetWorld()); It; ++It)
	{
		if (It->bBroken)
		{
			continue;
		}
		const FVector Middle = It->GetActorLocation() + It->GetActorForwardVector() * It->GetLength() * 0.5f;
		bool bSheltered = false;
		for (const FVector& Breakwater : Breakwaters)
		{
			if (FVector::Dist2D(Breakwater, Middle) < BreakwaterRadius)
			{
				bSheltered = true;
				break;
			}
		}
		if (!bSheltered && FMath::FRand() < 0.004f * DeltaSeconds * Intensity)
		{
			It->SetBroken(true);
		}
	}
}
