#include "FGGlimmer.h"

#include "FGGameData.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"

AFGGlimmer::AFGGlimmer()
{
	PrimaryActorTick.bCanEverTick = true;

	BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
	RootComponent = BodyMesh;
	BodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	BodyMesh->SetRelativeScale3D(FVector(1.4f, 0.55f, 0.45f));
	BodyMesh->SetCastShadow(false);

	TailMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("TailMesh"));
	TailMesh->SetupAttachment(BodyMesh);
	TailMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	TailMesh->SetRelativeLocation(FVector(-60.f, 0.f, 0.f));
	TailMesh->SetRelativeRotation(FRotator(0.f, 0.f, 90.f));
	TailMesh->SetRelativeScale3D(FVector(0.5f, 0.08f, 0.9f));
	TailMesh->SetCastShadow(false);
}

void AFGGlimmer::BeginPlay()
{
	Super::BeginPlay();
	Center = GetActorLocation();
	Center.Z = -Depth;
	Angle = FMath::FRandRange(0.f, 360.f);
	Time = FMath::FRandRange(0.f, 10.f);

	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	BodyMesh->SetStaticMesh(Sphere);
	TailMesh->SetStaticMesh(Sphere);
	GlowMID = UMaterialInstanceDynamic::Create(UFGGameData::ColorMaterial(), this);
	GlowMID->SetVectorParameterValue(TEXT("Color"), GlowColor);
	GlowMID->SetScalarParameterValue(TEXT("Glow"), 6.f);
	BodyMesh->SetMaterial(0, GlowMID);
	TailMesh->SetMaterial(0, GlowMID);
}

void AFGGlimmer::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Time += DeltaSeconds;
	Angle += SwimSpeed * DeltaSeconds;

	const float Rad = FMath::DegreesToRadians(Angle);
	const FVector Offset(FMath::Cos(Rad) * SwimRadius, FMath::Sin(Rad) * SwimRadius, FMath::Sin(Time * 0.9f) * 18.f);
	const FVector Location = Center + Offset;

	// Face along the loop, with a lazy body wobble.
	const float Heading = Angle + (SwimSpeed >= 0.f ? 90.f : -90.f);
	SetActorLocationAndRotation(Location, FRotator(FMath::Sin(Time * 1.3f) * 6.f, Heading + FMath::Sin(Time * 3.f) * 8.f, 0.f));
	TailMesh->SetRelativeRotation(FRotator(0.f, FMath::Sin(Time * 6.f) * 25.f, 90.f));

	if (GlowMID)
	{
		GlowMID->SetScalarParameterValue(TEXT("Glow"), 4.f + 3.f * (0.5f + 0.5f * FMath::Sin(Time * 1.7f)));
	}
}
