#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FGTypes.h"
#include "FGBuildable.generated.h"

class UStaticMeshComponent;
class UMaterialInstanceDynamic;

/**
 * Anything placed on the factory grid. Items enter through the input port (local -X side)
 * and leave through the output port (local +X side). Built from a DT_Buildables row.
 */
UCLASS()
class FISHGAME_API AFGBuildable : public AActor
{
	GENERATED_BODY()

public:
	AFGBuildable();

	static constexpr float CellSize = 100.f;
	static constexpr float PortHeight = 60.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UStaticMeshComponent> Top;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UStaticMeshComponent> InPort;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UStaticMeshComponent> OutPort;

	/** DT_Buildables row. Set it on a level-placed buildable and it builds itself at BeginPlay. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Factory")
	FName RowName;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	FFGBuildableRow Row;

	/** Build preview: no ticking, no collision, translucent. */
	UPROPERTY(BlueprintReadOnly, Category = "Factory")
	bool bGhost = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TMap<FName, int32> InputBuffer;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TMap<FName, int32> OutputBuffer;

	void InitFromRow(FName InRowName, const FFGBuildableRow& InRow, bool bInGhost);
	bool IsRowInitialized() const { return bRowInitialized; }
	void SetGhostValid(bool bValid);

	virtual bool HasInputPort() const { return false; }
	virtual bool HasOutputPort() const { return false; }
	/** Would this ever take the item (ignoring how full it is)? */
	virtual bool AcceptsItemType(FName Item) const { return false; }
	/** Can it take one more right now? */
	virtual bool AcceptsItem(FName Item) const;
	virtual bool TryInsert(FName Item);
	/** May the player hand items in with E? */
	virtual bool PlayerCanDeposit() const { return true; }

	/** Take one output item the target can use (Target == nullptr: any item). */
	bool TakeOutputFor(const AFGBuildable* Target, FName& OutItem);

	int32 CountInput(FName Item) const;
	int32 CountOutput(FName Item) const;
	int32 TotalOutput() const;

	FVector GetInputPortLocation() const;
	FVector GetOutputPortLocation() const;
	/** Where a belt coming from From should end (towers take belts from any side). */
	virtual FVector GetInputPortLocationFor(const FVector& From) const { return GetInputPortLocation(); }

	/** Footprint in cells after rotation. */
	FIntPoint GetFootprint() const;
	/** Lowest grid cell covered. */
	FIntPoint GetGridOrigin() const;

	virtual float GetPowerUse() const { return bGhost ? 0.f : Row.PowerUse; }
	virtual float GetPowerOutput() const { return bGhost ? 0.f : Row.PowerOutput; }
	virtual FText GetDisplayName() const { return Row.DisplayName; }
	virtual FString GetStatusText() const;
	virtual bool CanDismantle() const { return true; }
	/** Is it doing something right now (drives the working light). */
	virtual bool IsWorking() const { return false; }

	/** Build cost plus everything stored inside. */
	void GetRefund(TArray<FFGItemStack>& Out) const;

	/** Supply / demand of the whole grid, 0..1 (cached per frame). */
	static float GetPowerSatisfaction(const UWorld* World);
	static void GetPowerTotals(const UWorld* World, float& OutSupply, float& OutDemand);
	static FString BufferToString(const TMap<FName, int32>& Buffer);

	virtual void Tick(float DeltaSeconds) override;

protected:
	virtual void BeginPlay() override;
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void OnRowInitialized() {}

	bool bRowInitialized = false;
	void ApplyVisuals();
	void UpdateWorkingLight(float DeltaSeconds);

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> BodyMID;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> TopMID;

	float WorkGlow = 0.f;
};

/** Crafts recipes: takes inputs, waits CraftTime, produces outputs. */
UCLASS()
class FISHGAME_API AFGMachine : public AFGBuildable
{
	GENERATED_BODY()

public:
	virtual void Tick(float DeltaSeconds) override;
	virtual bool HasInputPort() const override { return true; }
	virtual bool HasOutputPort() const override { return true; }
	virtual bool AcceptsItemType(FName Item) const override;
	virtual FString GetStatusText() const override;
	virtual bool IsWorking() const override { return ActiveRecipe != INDEX_NONE; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	float Progress = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TArray<FFGRecipeRow> Recipes;

	int32 ActiveRecipe = INDEX_NONE;

protected:
	virtual void OnRowInitialized() override;
	bool CanStart(const FFGRecipeRow& Recipe) const;
};

/** Sits on a resource node and produces its item. */
UCLASS()
class FISHGAME_API AFGExtractor : public AFGBuildable
{
	GENERATED_BODY()

public:
	virtual void Tick(float DeltaSeconds) override;
	virtual bool HasOutputPort() const override { return true; }
	virtual FString GetStatusText() const override;
	virtual bool IsWorking() const override;

	float Timer = 0.f;
};

/** Makes power. */
UCLASS()
class FISHGAME_API AFGGenerator : public AFGBuildable
{
	GENERATED_BODY()

public:
	virtual FString GetStatusText() const override;
	virtual bool IsWorking() const override { return true; }
};

/** Holds any items; belts can feed it and pull from it. */
UCLASS()
class FISHGAME_API AFGStorage : public AFGBuildable
{
	GENERATED_BODY()

public:
	virtual bool HasInputPort() const override { return true; }
	virtual bool HasOutputPort() const override { return true; }
	virtual bool AcceptsItemType(FName Item) const override { return !Item.IsNone(); }
	virtual bool AcceptsItem(FName Item) const override;
	virtual bool TryInsert(FName Item) override;
	virtual bool PlayerCanDeposit() const override { return false; }
	virtual FString GetStatusText() const override;
};
