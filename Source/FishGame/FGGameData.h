#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "FGTypes.h"
#include "FGGameData.generated.h"

class UDataTable;
class UMaterialInterface;
class UStaticMesh;

/** Static access to the game's data tables, shared meshes and materials (loaded once, kept alive). */
UCLASS()
class FISHGAME_API UFGGameData : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	static UDataTable* Items();
	static UDataTable* Recipes();
	static UDataTable* Buildables();
	static UDataTable* Phases();

	static const FFGItemRow* FindItem(FName Item);
	static const FFGBuildableRow* FindBuildable(FName RowName);

	UFUNCTION(BlueprintPure, Category = "Factory")
	static FText ItemName(FName Item);

	UFUNCTION(BlueprintPure, Category = "Factory")
	static FLinearColor ItemColor(FName Item);

	static void GetRecipesForMachine(FName MachineType, TArray<FFGRecipeRow>& OutRecipes);
	static FString StacksToString(const TArray<FFGItemStack>& Stacks);

	/** Base material with a "Color" vector parameter. */
	static UMaterialInterface* ColorMaterial();
	/** Material for belt items: colour from per-instance custom data 0-2. */
	static UMaterialInterface* ItemMaterial();
	/** Translucent build-preview material with a "Color" parameter. */
	static UMaterialInterface* GhostMaterial();
	static UMaterialInterface* BeltMaterial();

	static UStaticMesh* CubeMesh();
	static UStaticMesh* CylinderMesh();
	static UStaticMesh* LoadMesh(const TSoftObjectPtr<UStaticMesh>& Mesh);
};
