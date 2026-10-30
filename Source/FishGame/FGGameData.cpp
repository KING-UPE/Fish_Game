#include "FGGameData.h"

#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

namespace FGGameDataPrivate
{
	template <typename T>
	T* LoadKept(T*& Cache, const TCHAR* Path)
	{
		if (!Cache)
		{
			Cache = LoadObject<T>(nullptr, Path, nullptr, LOAD_NoWarn | LOAD_Quiet);
			if (Cache)
			{
				Cache->AddToRoot();
			}
		}
		return Cache;
	}

	UDataTable* GItems = nullptr;
	UDataTable* GRecipes = nullptr;
	UDataTable* GBuildables = nullptr;
	UDataTable* GPhases = nullptr;
	UMaterialInterface* GColor = nullptr;
	UMaterialInterface* GItem = nullptr;
	UMaterialInterface* GGhost = nullptr;
	UMaterialInterface* GBelt = nullptr;
	UStaticMesh* GCube = nullptr;
	UStaticMesh* GCylinder = nullptr;
}

using namespace FGGameDataPrivate;

UDataTable* UFGGameData::Items() { return LoadKept(GItems, TEXT("/Game/Blue/Data/DT_Items.DT_Items")); }
UDataTable* UFGGameData::Recipes() { return LoadKept(GRecipes, TEXT("/Game/Blue/Data/DT_Recipes.DT_Recipes")); }
UDataTable* UFGGameData::Buildables() { return LoadKept(GBuildables, TEXT("/Game/Blue/Data/DT_Buildables.DT_Buildables")); }
UDataTable* UFGGameData::Phases() { return LoadKept(GPhases, TEXT("/Game/Blue/Data/DT_Phases.DT_Phases")); }

const FFGItemRow* UFGGameData::FindItem(FName Item)
{
	UDataTable* Table = Items();
	return Table ? Table->FindRow<FFGItemRow>(Item, TEXT("FGItem"), false) : nullptr;
}

const FFGBuildableRow* UFGGameData::FindBuildable(FName RowName)
{
	UDataTable* Table = Buildables();
	return Table ? Table->FindRow<FFGBuildableRow>(RowName, TEXT("FGBuildable"), false) : nullptr;
}

FText UFGGameData::ItemName(FName Item)
{
	const FFGItemRow* Row = FindItem(Item);
	return Row ? Row->DisplayName : FText::FromName(Item);
}

FLinearColor UFGGameData::ItemColor(FName Item)
{
	const FFGItemRow* Row = FindItem(Item);
	return Row ? Row->Color : FLinearColor::White;
}

void UFGGameData::GetRecipesForMachine(FName MachineType, TArray<FFGRecipeRow>& OutRecipes)
{
	OutRecipes.Reset();
	UDataTable* Table = Recipes();
	if (!Table || MachineType.IsNone())
	{
		return;
	}
	TArray<FFGRecipeRow*> Rows;
	Table->GetAllRows<FFGRecipeRow>(TEXT("FGRecipes"), Rows);
	for (const FFGRecipeRow* Row : Rows)
	{
		if (Row && Row->Machine == MachineType)
		{
			OutRecipes.Add(*Row);
		}
	}
}

FString UFGGameData::StacksToString(const TArray<FFGItemStack>& Stacks)
{
	TArray<FString> Parts;
	for (const FFGItemStack& Stack : Stacks)
	{
		Parts.Add(FString::Printf(TEXT("%d %s"), Stack.Count, *ItemName(Stack.Item).ToString()));
	}
	return FString::Join(Parts, TEXT(", "));
}

UMaterialInterface* UFGGameData::ColorMaterial()
{
	// Our own lit material (rougher, nicer) if it exists, else the engine's basic shape material.
	if (UMaterialInterface* Own = LoadKept(GColor, TEXT("/Game/Blue/Materials/M_Machine.M_Machine")))
	{
		return Own;
	}
	return LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
}

UMaterialInterface* UFGGameData::ItemMaterial()
{
	if (UMaterialInterface* Own = LoadKept(GItem, TEXT("/Game/Blue/Materials/M_Item.M_Item")))
	{
		return Own;
	}
	return ColorMaterial();
}

UMaterialInterface* UFGGameData::GhostMaterial()
{
	if (UMaterialInterface* Own = LoadKept(GGhost, TEXT("/Game/Blue/Materials/M_Ghost.M_Ghost")))
	{
		return Own;
	}
	return ColorMaterial();
}

UMaterialInterface* UFGGameData::BeltMaterial()
{
	if (UMaterialInterface* Own = LoadKept(GBelt, TEXT("/Game/Blue/Materials/M_Belt.M_Belt")))
	{
		return Own;
	}
	return ColorMaterial();
}

UStaticMesh* UFGGameData::CubeMesh() { return LoadKept(GCube, TEXT("/Engine/BasicShapes/Cube.Cube")); }
UStaticMesh* UFGGameData::CylinderMesh() { return LoadKept(GCylinder, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")); }

UStaticMesh* UFGGameData::LoadMesh(const TSoftObjectPtr<UStaticMesh>& Mesh)
{
	return Mesh.IsNull() ? nullptr : Mesh.LoadSynchronous();
}
