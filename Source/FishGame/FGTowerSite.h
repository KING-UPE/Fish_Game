#pragma once

#include "CoreMinimal.h"
#include "FGBuildable.h"
#include "FGTowerSite.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FFGPhaseEvent, int32, PhaseIndex);

/**
 * The Signal Tower. Placed in the level (not buildable). It takes the current phase's
 * requirements from belts or the player; finishing a phase adds a tower section and
 * fires OnPhaseCompleted (the player controller plays the message home + flashback).
 */
UCLASS()
class FISHGAME_API AFGTowerSite : public AFGBuildable
{
	GENERATED_BODY()

public:
	AFGTowerSite();

	/** Index into DT_Phases rows (0 = Phase 1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Story")
	int32 CurrentPhase = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Story")
	TMap<FName, int32> Delivered;

	UPROPERTY(BlueprintAssignable, Category = "Story")
	FFGPhaseEvent OnPhaseCompleted;

	UPROPERTY(BlueprintAssignable, Category = "Story")
	FFGPhaseEvent OnPhaseStarted;

	bool GetPhase(int32 Index, FFGPhaseRow& OutPhase) const;
	int32 NumPhases() const;
	bool IsFinished() const { return CurrentPhase >= NumPhases(); }
	int32 GetDelivered(FName Item) const;

	/** Player number of the current phase (1-based). */
	int32 GetPhaseNumber() const { return CurrentPhase + 1; }

	/** Debug / testing: complete the current phase immediately. */
	UFUNCTION(BlueprintCallable, Category = "Story")
	void CheatCompletePhase();

	virtual bool HasInputPort() const override { return true; }
	virtual bool AcceptsItemType(FName Item) const override;
	virtual bool AcceptsItem(FName Item) const override;
	virtual bool TryInsert(FName Item) override;
	virtual bool CanDismantle() const override { return false; }
	virtual FText GetDisplayName() const override;
	virtual FString GetStatusText() const override;
	virtual FVector GetInputPortLocationFor(const FVector& From) const override;
	virtual bool IsWorking() const override { return true; }

protected:
	virtual void BeginPlay() override;
	virtual void OnConstruction(const FTransform& Transform) override;
	void CheckComplete();
	void RebuildSections();

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> Sections;
};
