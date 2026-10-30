#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FGTypes.h"
#include "FGBelt.generated.h"

class AFGBuildable;
class UStaticMeshComponent;
class UInstancedStaticMeshComponent;

/** A straight floating belt from one buildable's output port to another's input port. */
UCLASS()
class FISHGAME_API AFGBelt : public AActor
{
	GENERATED_BODY()

public:
	AFGBelt();

	static constexpr float SegmentLength = 200.f;
	static constexpr float MaxLength = 3000.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<USceneComponent> BeltRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UStaticMeshComponent> BeltMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UInstancedStaticMeshComponent> ItemMeshes;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TWeakObjectPtr<AFGBuildable> Source;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TWeakObjectPtr<AFGBuildable> Target;

	/** cm per second. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float Speed = 180.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float Spacing = 45.f;

	/** Level-placed belts: connect these two at the start of play. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<AFGBuildable> StartActor;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<AFGBuildable> EndActor;

	/** What one segment cost (for the refund). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TArray<FFGItemStack> SegmentCost;

	/** Snapped in a storm: carries nothing until repaired (E, 1 Steel Bar). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	bool bBroken = false;

	void SetBroken(bool bInBroken);

	void Setup(AFGBuildable* InSource, AFGBuildable* InTarget, const TArray<FFGItemStack>& InSegmentCost);

	static int32 SegmentsFor(float Length) { return FMath::Max(1, FMath::CeilToInt(Length / SegmentLength)); }
	float GetLength() const { return Length; }
	int32 NumItems() const { return Queue.Num(); }
	void GetRefund(TArray<FFGItemStack>& Out) const;
	FString GetStatusText() const;

	virtual void Tick(float DeltaSeconds) override;

private:
	struct FBeltItem
	{
		FName Item;
		float Distance = 0.f;
	};

	/** Queue[0] is the item closest to the target. */
	TArray<FBeltItem> Queue;
	float Length = 100.f;
	bool bConnected = false;

	UPROPERTY(Transient)
	TObjectPtr<class UMaterialInstanceDynamic> BeltMID;

	void UpdateItemMeshes();
};
