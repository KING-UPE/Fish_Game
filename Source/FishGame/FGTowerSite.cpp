#include "FGTowerSite.h"

#include "FGGameData.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DataTable.h"
#include "Materials/MaterialInstanceDynamic.h"

AFGTowerSite::AFGTowerSite()
{
	PrimaryActorTick.bCanEverTick = true;
	Row.DisplayName = NSLOCTEXT("FishGame", "TowerName", "Signal Tower");
	Row.Size = FIntPoint(6, 6);
	Row.Height = 60.f;
	Row.Color = FLinearColor(0.08f, 0.35f, 0.45f);
	Row.AccentColor = FLinearColor(0.2f, 0.8f, 1.f);
	Row.Mesh = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
	Row.BufferSize = 100000;
}

void AFGTowerSite::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	ApplyVisuals();
}

void AFGTowerSite::BeginPlay()
{
	bRowInitialized = true; // the tower's row is built in, not from DT_Buildables
	Super::BeginPlay();
	RebuildSections();
}

int32 AFGTowerSite::NumPhases() const
{
	const UDataTable* Table = UFGGameData::Phases();
	return Table ? Table->GetRowNames().Num() : 0;
}

bool AFGTowerSite::GetPhase(int32 Index, FFGPhaseRow& OutPhase) const
{
	const UDataTable* Table = UFGGameData::Phases();
	if (!Table)
	{
		return false;
	}
	const TArray<FName> Names = Table->GetRowNames();
	if (!Names.IsValidIndex(Index))
	{
		return false;
	}
	if (const FFGPhaseRow* Found = Table->FindRow<FFGPhaseRow>(Names[Index], TEXT("FGPhase"), false))
	{
		OutPhase = *Found;
		return true;
	}
	return false;
}

int32 AFGTowerSite::GetDelivered(FName Item) const
{
	const int32* Count = Delivered.Find(Item);
	return Count ? *Count : 0;
}

bool AFGTowerSite::AcceptsItemType(FName Item) const
{
	FFGPhaseRow Phase;
	if (!GetPhase(CurrentPhase, Phase))
	{
		return false;
	}
	for (const FFGItemStack& Need : Phase.Requirements)
	{
		if (Need.Item == Item)
		{
			return true;
		}
	}
	return false;
}

bool AFGTowerSite::AcceptsItem(FName Item) const
{
	FFGPhaseRow Phase;
	if (!GetPhase(CurrentPhase, Phase))
	{
		return false;
	}
	for (const FFGItemStack& Need : Phase.Requirements)
	{
		if (Need.Item == Item)
		{
			return GetDelivered(Item) < Need.Count;
		}
	}
	return false;
}

bool AFGTowerSite::TryInsert(FName Item)
{
	if (!AcceptsItem(Item))
	{
		return false;
	}
	Delivered.FindOrAdd(Item)++;
	CheckComplete();
	return true;
}

void AFGTowerSite::CheckComplete()
{
	FFGPhaseRow Phase;
	if (!GetPhase(CurrentPhase, Phase))
	{
		return;
	}
	for (const FFGItemStack& Need : Phase.Requirements)
	{
		if (GetDelivered(Need.Item) < Need.Count)
		{
			return;
		}
	}
	const int32 Finished = CurrentPhase;
	CurrentPhase++;
	Delivered.Reset();
	RebuildSections();
	OnPhaseCompleted.Broadcast(Finished);
	if (!IsFinished())
	{
		OnPhaseStarted.Broadcast(CurrentPhase);
	}
}

void AFGTowerSite::CheatCompletePhase()
{
	FFGPhaseRow Phase;
	if (!GetPhase(CurrentPhase, Phase))
	{
		return;
	}
	for (const FFGItemStack& Need : Phase.Requirements)
	{
		Delivered.Add(Need.Item, Need.Count);
	}
	CheckComplete();
}

void AFGTowerSite::RebuildSections()
{
	for (UStaticMeshComponent* Section : Sections)
	{
		if (Section)
		{
			Section->DestroyComponent();
		}
	}
	Sections.Reset();

	UStaticMesh* Cylinder = UFGGameData::CylinderMesh();
	UMaterialInterface* Base = UFGGameData::ColorMaterial();
	if (!Cylinder || !Base || !GetWorld())
	{
		return;
	}

	// One section per finished phase, each narrower and taller: base, dish, mast, ring, core.
	float Z = Row.Height;
	for (int32 Index = 0; Index < CurrentPhase; ++Index)
	{
		const float Radius = FMath::Lerp(240.f, 70.f, Index / 4.f);
		const float Height = 260.f + Index * 60.f;
		UStaticMeshComponent* Section = NewObject<UStaticMeshComponent>(this);
		Section->SetStaticMesh(Cylinder);
		Section->SetupAttachment(SceneRoot);
		Section->RegisterComponent();
		Section->SetRelativeLocation(FVector(0.f, 0.f, Z + Height * 0.5f));
		Section->SetRelativeScale3D(FVector(Radius / 50.f, Radius / 50.f, Height / 100.f));
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, this);
		MID->SetVectorParameterValue(TEXT("Color"), Index % 2 == 0 ? Row.Color * 1.4f : Row.AccentColor);
		MID->SetScalarParameterValue(TEXT("Glow"), Index % 2 == 0 ? 0.f : 1.5f);
		Section->SetMaterial(0, MID);
		Sections.Add(Section);
		Z += Height;
	}
}

FText AFGTowerSite::GetDisplayName() const
{
	FFGPhaseRow Phase;
	if (GetPhase(CurrentPhase, Phase) && !Phase.TowerPart.IsEmpty())
	{
		return FText::Format(NSLOCTEXT("FishGame", "TowerPart", "Signal Tower: {0}"), Phase.TowerPart);
	}
	return Row.DisplayName;
}

FString AFGTowerSite::GetStatusText() const
{
	FFGPhaseRow Phase;
	if (!GetPhase(CurrentPhase, Phase))
	{
		return TEXT("Complete.");
	}
	TArray<FString> Lines;
	for (const FFGItemStack& Need : Phase.Requirements)
	{
		Lines.Add(FString::Printf(TEXT("%s  %d / %d"), *UFGGameData::ItemName(Need.Item).ToString(), GetDelivered(Need.Item), Need.Count));
	}
	return FString::Join(Lines, TEXT("\n"));
}

FVector AFGTowerSite::GetInputPortLocationFor(const FVector& From) const
{
	const FVector Center = GetActorLocation();
	FVector Dir = From - Center;
	Dir.Z = 0.f;
	if (!Dir.Normalize())
	{
		Dir = FVector::ForwardVector;
	}
	const float Radius = Row.Size.X * CellSize * 0.46f;
	return Center + Dir * Radius + FVector(0.f, 0.f, PortHeight);
}
