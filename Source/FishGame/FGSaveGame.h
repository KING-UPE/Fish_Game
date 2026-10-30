#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "FGSaveGame.generated.h"

USTRUCT()
struct FFGSavedBuildable
{
	GENERATED_BODY()

	UPROPERTY()
	FName Row;

	UPROPERTY()
	FTransform Transform;

	UPROPERTY()
	TMap<FName, int32> Input;

	UPROPERTY()
	TMap<FName, int32> Output;
};

USTRUCT()
struct FFGSavedBelt
{
	GENERATED_BODY()

	/** Indices into UFGSaveGame::Buildables; -1 = the Signal Tower. */
	UPROPERTY()
	int32 Source = INDEX_NONE;

	UPROPERTY()
	int32 Target = INDEX_NONE;
};

/** One save slot: the whole factory, the player and the story progress. */
UCLASS()
class FISHGAME_API UFGSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	static constexpr const TCHAR* SlotName = TEXT("BlueSignal");
	static constexpr int32 TowerIndex = -2;

	UPROPERTY()
	int32 Version = 1;

	UPROPERTY()
	TArray<FFGSavedBuildable> Buildables;

	UPROPERTY()
	TArray<FFGSavedBelt> Belts;

	UPROPERTY()
	TMap<FName, int32> Inventory;

	UPROPERTY()
	TArray<FName> HintsShown;

	UPROPERTY()
	int32 Phase = 0;

	UPROPERTY()
	TMap<FName, int32> Delivered;

	UPROPERTY()
	int32 GlimmerTrust = 0;

	UPROPERTY()
	float OceanHealth = 1.f;

	UPROPERTY()
	FVector PlayerLocation = FVector::ZeroVector;

	UPROPERTY()
	FRotator PlayerRotation = FRotator::ZeroRotator;
};
