#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "FGTypes.h"
#include "FGPlayerController.generated.h"

class AFGBuildable;
class AFGBelt;
class AFGResourceNode;
class AFGTowerSite;
class UTexture2D;

/**
 * The player's factory brain: inventory, build mode (ghost preview on a 1 m grid), belts,
 * E-to-interact, dismantling, and the story queue (Echo lines, messages home, flashbacks,
 * Neela's replies and her Fish API drawings).
 *
 * Keys: 1-9 select a building · LMB place · R rotate · RMB/Q cancel · E gather / exchange ·
 * X dismantle · hold E on a resource to keep gathering.
 */
UCLASS()
class FISHGAME_API AFGPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	AFGPlayerController();

	static constexpr float BuildRange = 1600.f;
	static constexpr float InteractRange = 650.f;
	/** Platforms sit with their middle a little below the sea surface. */
	static constexpr float PlatformZ = -20.f;

	// ---------------------------------------------------------------- Inventory
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TMap<FName, int32> Inventory;

	int32 CountItem(FName Item) const;
	bool HasItems(const TArray<FFGItemStack>& Stacks, int32 Multiplier = 1) const;
	void RemoveItems(const TArray<FFGItemStack>& Stacks, int32 Multiplier = 1);
	void AddItems(const TArray<FFGItemStack>& Stacks);
	void AddItem(FName Item, int32 Count);
	FString MissingItemsText(const TArray<FFGItemStack>& Stacks, int32 Multiplier = 1) const;

	// ---------------------------------------------------------------- Building
	/** Every unlocked buildable, in table order. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TArray<FName> HotbarAll;

	/** The visible page of HotbarAll (10 slots, Tab flips pages). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TArray<FName> Hotbar;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	int32 HotbarPage = 0;

	int32 NumHotbarPages() const { return FMath::Max(1, (HotbarAll.Num() + 9) / 10); }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	int32 SelectedSlot = INDEX_NONE;

	UPROPERTY(Transient)
	TObjectPtr<AFGBuildable> Ghost;

	FName GhostRow;
	int32 GhostYaw = 0;
	bool bGhostValid = false;
	FString GhostProblem;
	TWeakObjectPtr<AFGBuildable> BeltStart;

	bool GetSelectedRow(FFGBuildableRow& OutRow, FName& OutName) const;

	// ---------------------------------------------------------------- Looking
	TWeakObjectPtr<AActor> LookActor;
	FVector LookPoint = FVector::ZeroVector;
	float LookDistance = 0.f;
	bool bLookHit = false;

	/** Ground under the crosshair (static level geometry only) for placement. */
	TWeakObjectPtr<AActor> GroundActor;
	FVector GroundPoint = FVector::ZeroVector;
	FVector GroundNormal = FVector::UpVector;
	bool bGroundHit = false;

	// ---------------------------------------------------------------- Story
	TArray<FFGStoryLine> LineQueue;
	FFGStoryLine CurrentLine;
	bool bLineActive = false;
	float LineTime = 0.f;

	bool bPuzzleWaiting = false;
	bool bPuzzleOpen = false;

	/** What the open picture is for: Neela's drawing, or a Glimmer trade (fish first, then chests). */
	enum class EPuzzleKind : uint8 { Drawing, TradeFish, TradeChests };
	EPuzzleKind PuzzleKind = EPuzzleKind::Drawing;
	int32 PuzzleFish = 0;
	int32 PuzzleChests = 0;
	TWeakObjectPtr<class AFGTradeBuoy> PuzzleBuoy;

	UPROPERTY(Transient)
	TObjectPtr<UTexture2D> PuzzlePicture;

	int32 PuzzleAnswer = 0;
	TArray<int32> PuzzleOptions;
	int32 PuzzlesSolved = 0;

	FString Toast;
	float ToastTime = 0.f;

	UPROPERTY(Transient)
	TObjectPtr<AFGTowerSite> Tower;

	void QueueLine(const FText& Speaker, const FText& Text, float Duration = 4.f, EFGLineStyle Style = EFGLineStyle::Normal);
	void QueueLines(const TArray<FFGStoryLine>& Lines, EFGLineStyle ForceStyle = EFGLineStyle::Normal);
	void ShowToast(const FString& Message);

	/** True while a flashback (or its title card) is on screen. */
	bool IsInFlashback() const;

	// ---------------------------------------------------------------- Console cheats (testing)
	UFUNCTION(Exec)
	void FGCompletePhase();

	UFUNCTION(Exec)
	void FGGive(FName Item, int32 Count);

	UFUNCTION(Exec)
	void FGSkipStory();

	/** Test hooks: run the same code as the keys (1-9, left click, E) from the console or scripts. */
	UFUNCTION(Exec)
	void FGSelect(int32 Slot);

	UFUNCTION(Exec)
	void FGClick();

	UFUNCTION(Exec)
	void FGInteract();

	/** Point the camera (pitch, yaw in degrees). */
	UFUNCTION(Exec)
	void FGLook(float Pitch, float Yaw);

	/** Teleport the player (feet position). */
	UFUNCTION(Exec)
	void FGTeleport(float X, float Y, float Z);

	/** Save now (the game also autosaves every minute and when you quit). */
	UFUNCTION(Exec)
	void FGSave();

	/** Delete the save and restart the level from the crash. */
	UFUNCTION(Exec)
	void FGNewGame();

	void SaveFactory();
	bool LoadFactory();

protected:
	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;
	virtual void PlayerTick(float DeltaTime) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	void UpdateLook();
	void CheckFallIntoSea();
	void UpdateGhost();
	void UpdateStory(float DeltaTime);
	void UpdateHints();
	void RefreshHotbar();
	bool CheckPlacement(const FFGBuildableRow& Row, FIntPoint Origin, FIntPoint Footprint, bool bOnWater, FString& OutProblem) const;
	bool bGhostOnWater = false;

	void OnInteract();
	void OnInteractRepeat();
	void OnPrimary();
	void OnCancel();
	void OnRotate();
	void OnDismantle();
	void OnNumber(int32 Index);
	void OnNextPage();
	void TalkToBuoy(class AFGTradeBuoy* Buoy);
	void BuildPuzzleOptions(int32 Answer);
	/** Where the view ray meets the sea surface (Z = 0). */
	bool GetWaterPoint(FVector& OutPoint) const;

	void SelectSlot(int32 Index);
	void ClearSelection();
	void PlaceGhost();
	void ClickBelt(AFGBuildable* Clicked);
	void Exchange(AFGBuildable* Buildable);
	void Gather(AFGResourceNode* Node);
	void DestroyBeltsOf(AFGBuildable* Buildable);
	void Hint(FName Key, const FText& Text);

	UFUNCTION()
	void HandlePhaseCompleted(int32 PhaseIndex);

	UFUNCTION()
	void HandlePhaseStarted(int32 PhaseIndex);

	UFUNCTION()
	void HandlePuzzleReady(UTexture2D* Picture, int32 Fish, int32 Chests);

	void StartPuzzle();
	void AnswerPuzzle(int32 Option);

	float GatherCooldown = 0.f;
	float AutosaveTimer = 0.f;
	int32 LastStormCount = 0;
	bool bPendingPlayerRestore = false;
	bool bNewGameRequested = false;
	FVector RestoreLocation = FVector::ZeroVector;
	FRotator RestoreRotation = FRotator::ZeroRotator;
	FVector SafeLocation = FVector::ZeroVector;
	bool bHasSafeLocation = false;
	float LowPowerTime = 0.f;
	TSet<FName> HintsShown;
};
