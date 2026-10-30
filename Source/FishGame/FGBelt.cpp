#include "FGBelt.h"

#include "FGBuildable.h"
#include "FGGameData.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Materials/MaterialInstanceDynamic.h"

AFGBelt::AFGBelt()
{
	PrimaryActorTick.bCanEverTick = true;

	BeltRoot = CreateDefaultSubobject<USceneComponent>(TEXT("BeltRoot"));
	RootComponent = BeltRoot;

	BeltMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BeltMesh"));
	BeltMesh->SetupAttachment(BeltRoot);
	BeltMesh->SetCollisionProfileName(UCollisionProfile::BlockAllDynamic_ProfileName);

	ItemMeshes = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("ItemMeshes"));
	ItemMeshes->SetupAttachment(BeltRoot);
	ItemMeshes->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	ItemMeshes->NumCustomDataFloats = 3;
}

void AFGBelt::Setup(AFGBuildable* InSource, AFGBuildable* InTarget, const TArray<FFGItemStack>& InSegmentCost)
{
	Source = InSource;
	Target = InTarget;
	SegmentCost = InSegmentCost;
	bConnected = true;

	const FVector Start = InSource->GetOutputPortLocation();
	const FVector End = InTarget->GetInputPortLocationFor(Start);
	const FVector Delta = End - Start;
	Length = FMath::Max(Delta.Size(), 10.f);

	// Root sits at the start, X points to the target. The belt body is a 100 cm cube stretched along X.
	SetActorLocationAndRotation(Start, Delta.Rotation());
	UStaticMesh* Cube = UFGGameData::CubeMesh();
	BeltMesh->SetStaticMesh(Cube);
	BeltMesh->SetRelativeLocation(FVector(Length * 0.5f, 0.f, 0.f));
	BeltMesh->SetRelativeScale3D(FVector(Length / 100.f, 0.55f, 0.08f));

	BeltMID = UMaterialInstanceDynamic::Create(UFGGameData::BeltMaterial(), this);
	BeltMID->SetVectorParameterValue(TEXT("Color"), FLinearColor(0.12f, 0.13f, 0.15f));
	BeltMID->SetScalarParameterValue(TEXT("Length"), Length / 100.f);
	BeltMesh->SetMaterial(0, BeltMID);

	ItemMeshes->SetStaticMesh(Cube);
	ItemMeshes->SetMaterial(0, UFGGameData::ItemMaterial());
}

void AFGBelt::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Level-placed belt: wait until both ends have built themselves, then connect.
	if (!bConnected && StartActor && EndActor && StartActor->IsRowInitialized() && EndActor->IsRowInitialized())
	{
		const FFGBuildableRow* BeltRow = UFGGameData::FindBuildable(TEXT("Belt"));
		Setup(StartActor, EndActor, BeltRow ? BeltRow->Cost : TArray<FFGItemStack>());
	}

	AFGBuildable* Src = Source.Get();
	AFGBuildable* Dst = Target.Get();
	if (!Src || !Dst || bBroken)
	{
		return;
	}

	// Move: each item advances, but never closer than Spacing to the one ahead (or past the end).
	for (int32 Index = 0; Index < Queue.Num(); ++Index)
	{
		const float Limit = (Index == 0) ? Length : Queue[Index - 1].Distance - Spacing;
		Queue[Index].Distance = FMath::Min(Queue[Index].Distance + Speed * DeltaSeconds, FMath::Max(Limit, 0.f));
	}

	// Deliver the front item if it reached the end and the target takes it.
	if (Queue.Num() > 0 && Queue[0].Distance >= Length - 1.f && Dst->TryInsert(Queue[0].Item))
	{
		Queue.RemoveAt(0);
	}

	// Pull a new item from the source when there is room at the start.
	if (Queue.Num() == 0 || Queue.Last().Distance >= Spacing)
	{
		FName Item;
		if (Src->TakeOutputFor(Dst, Item))
		{
			Queue.Add({ Item, 0.f });
		}
	}

	UpdateItemMeshes();
}

void AFGBelt::UpdateItemMeshes()
{
	while (ItemMeshes->GetInstanceCount() < Queue.Num())
	{
		ItemMeshes->AddInstance(FTransform::Identity);
	}
	while (ItemMeshes->GetInstanceCount() > Queue.Num())
	{
		ItemMeshes->RemoveInstance(ItemMeshes->GetInstanceCount() - 1);
	}
	const FTransform BeltTransform(GetActorRotation(), GetActorLocation());
	for (int32 Index = 0; Index < Queue.Num(); ++Index)
	{
		const FVector World = BeltTransform.TransformPosition(FVector(Queue[Index].Distance, 0.f, 14.f));
		const FTransform Instance(GetActorRotation(), World, FVector(0.22f));
		ItemMeshes->UpdateInstanceTransform(Index, Instance, true, false, true);
		const FLinearColor Color = UFGGameData::ItemColor(Queue[Index].Item);
		ItemMeshes->SetCustomDataValue(Index, 0, Color.R, false);
		ItemMeshes->SetCustomDataValue(Index, 1, Color.G, false);
		ItemMeshes->SetCustomDataValue(Index, 2, Color.B, false);
	}
	ItemMeshes->MarkRenderStateDirty();
}

void AFGBelt::GetRefund(TArray<FFGItemStack>& Out) const
{
	Out.Reset();
	const int32 Segments = SegmentsFor(Length);
	for (const FFGItemStack& Stack : SegmentCost)
	{
		Out.Add({ Stack.Item, Stack.Count * Segments });
	}
	for (const FBeltItem& Item : Queue)
	{
		Out.Add({ Item.Item, 1 });
	}
}

void AFGBelt::SetBroken(bool bInBroken)
{
	bBroken = bInBroken;
	if (BeltMID)
	{
		BeltMID->SetVectorParameterValue(TEXT("Color"), bBroken ? FLinearColor(0.6f, 0.08f, 0.05f) : FLinearColor(0.12f, 0.13f, 0.15f));
	}
}

FString AFGBelt::GetStatusText() const
{
	if (bBroken)
	{
		return TEXT("SNAPPED in the storm. Press E to repair (1 Steel Bar).");
	}
	return FString::Printf(TEXT("%.0f m long, carrying %d item(s)"), Length / 100.f, Queue.Num());
}
