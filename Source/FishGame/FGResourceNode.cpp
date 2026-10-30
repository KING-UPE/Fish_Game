#include "FGResourceNode.h"

#include "FGGameData.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Materials/MaterialInstanceDynamic.h"

AFGResourceNode::AFGResourceNode()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetCollisionProfileName(UCollisionProfile::BlockAllDynamic_ProfileName);
	RootComponent = Mesh;
	Tags.Add(TEXT("ResourceNode"));
}

void AFGResourceNode::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (!Mesh->GetStaticMesh())
	{
		Mesh->SetStaticMesh(UFGGameData::CubeMesh());
	}
	ApplyTint();
}

void AFGResourceNode::BeginPlay()
{
	Super::BeginPlay();
	ApplyTint();
}

void AFGResourceNode::ApplyTint()
{
	if (!bTintFromItem)
	{
		return;
	}
	if (UMaterialInterface* Base = UFGGameData::ColorMaterial())
	{
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, this);
		MID->SetVectorParameterValue(TEXT("Color"), UFGGameData::ItemColor(Item));
		MID->SetScalarParameterValue(TEXT("Glow"), 0.4f);
		Mesh->SetMaterial(0, MID);
	}
}
