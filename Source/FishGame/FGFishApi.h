#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Interfaces/IHttpRequest.h"
#include "FGFishApi.generated.h"

class UTexture2D;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FFGPuzzleReady, UTexture2D*, Picture, int32, Fish, int32, Chests);

/** One Fish Game API picture and its true counts. */
USTRUCT(BlueprintType)
struct FFGPuzzle
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "FishApi")
	TObjectPtr<UTexture2D> Picture = nullptr;

	UPROPERTY(BlueprintReadOnly, Category = "FishApi")
	int32 Fish = 0;

	UPROPERTY(BlueprintReadOnly, Category = "FishApi")
	int32 Chests = 0;

	/** true = from the live API, false = bundled offline picture. */
	UPROPERTY(BlueprintReadOnly, Category = "FishApi")
	bool bLive = false;
};

/**
 * Talks to the Fish Game API (https://marcconrad.com/uob/fish/api.php).
 * RequestPuzzle() fetches a picture + counts and broadcasts OnPuzzleReady on the game thread.
 * If the API is slow or down it falls back to bundled pictures in /Game/Blue/FishApi
 * named T_Fish_F<fish>_C<chests>. Every puzzle is kept in History (Neela's repeated drawings).
 */
UCLASS()
class FISHGAME_API UFGFishApiSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "FishApi")
	void RequestPuzzle();

	/** Re-show a picture the player has already seen (used after the relay breaks). */
	UFUNCTION(BlueprintCallable, Category = "FishApi")
	void RequestRepeatPuzzle();

	UPROPERTY(BlueprintAssignable, Category = "FishApi")
	FFGPuzzleReady OnPuzzleReady;

	UPROPERTY(BlueprintReadOnly, Category = "FishApi")
	TArray<FFGPuzzle> History;

	UPROPERTY(BlueprintReadOnly, Category = "FishApi")
	bool bBusy = false;

	static constexpr const TCHAR* ApiUrl = TEXT("https://marcconrad.com/uob/fish/api.php?out=json&base64=no");

private:
	void OnJsonReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnected);
	void OnImageReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnected);
	void UseFallback(const TCHAR* Reason);
	void Finish(UTexture2D* Picture, int32 Fish, int32 Chests, bool bLive);

	int32 PendingFish = 0;
	int32 PendingChests = 0;
};
