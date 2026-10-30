#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FGWeather.generated.h"

class ADirectionalLight;
class AExponentialHeightFog;
class AFGTowerSite;
class UMaterialParameterCollection;

/**
 * Storms and the health of the sea. Place one in the level.
 * - From StartPhaseIndex on, storms roll in: dark sky, fog, lightning, rain (drawn by the HUD).
 *   Solar output drops, lightning rods charge fast, unprotected belts can snap.
 * - Polluting machines (kelp burners) lower the tower's OceanHealth; cleaners raise it.
 *   Both drive MPC_Ocean (Storm, Murk) so the water itself changes.
 */
UCLASS()
class FISHGAME_API AFGWeather : public AActor
{
	GENERATED_BODY()

public:
	AFGWeather();

	UPROPERTY(EditAnywhere, Category = "Weather")
	int32 StartPhaseIndex = 2;

	UPROPERTY(EditAnywhere, Category = "Weather")
	float FirstStormDelay = 75.f;

	UPROPERTY(EditAnywhere, Category = "Weather")
	float MinGap = 300.f;

	UPROPERTY(EditAnywhere, Category = "Weather")
	float MaxGap = 480.f;

	UPROPERTY(EditAnywhere, Category = "Weather")
	float MinDuration = 60.f;

	UPROPERTY(EditAnywhere, Category = "Weather")
	float MaxDuration = 90.f;

	/** Belts within this distance of a Breakwater never snap. */
	UPROPERTY(EditAnywhere, Category = "Weather")
	float BreakwaterRadius = 1500.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Weather")
	bool bStorm = false;

	/** Smoothed 0..1 storm strength. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Weather")
	float Intensity = 0.f;

	/** 0..1 white flash for the HUD. */
	float FlashAlpha = 0.f;

	/** How many storms have started (the HUD/controller uses it to notice a new one). */
	int32 StormCount = 0;

	static AFGWeather* Get(const UWorld* World);
	static float GetIntensity(const UWorld* World);

	void StartStorm(float Duration);

	virtual void Tick(float DeltaSeconds) override;

protected:
	virtual void BeginPlay() override;

	void UpdatePollution(AFGTowerSite* Tower, float DeltaSeconds);
	void UpdateVisuals(AFGTowerSite* Tower, float DeltaSeconds);
	void SnapBelts(float DeltaSeconds);

	UPROPERTY(Transient)
	TObjectPtr<UMaterialParameterCollection> OceanMPC;

	TWeakObjectPtr<ADirectionalLight> Sun;
	TWeakObjectPtr<AExponentialHeightFog> Fog;
	float BaseSunIntensity = 9.f;
	float BaseFogDensity = 0.006f;
	float Timer = 0.f;
	float StormLeft = 0.f;
	float NextFlash = 3.f;
	float FlashLeft = 0.f;
	bool bScheduled = false;
};
