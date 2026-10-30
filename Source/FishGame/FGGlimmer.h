#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FGGlimmer.generated.h"

class UStaticMeshComponent;
class UMaterialInstanceDynamic;

/** A Glimmer: a glowing fish-like being that swims slow loops just under the surface and pulses. */
UCLASS()
class FISHGAME_API AFGGlimmer : public AActor
{
	GENERATED_BODY()

public:
	AFGGlimmer();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Glimmers")
	TObjectPtr<UStaticMeshComponent> BodyMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Glimmers")
	TObjectPtr<UStaticMeshComponent> TailMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Glimmers")
	float SwimRadius = 500.f;

	/** Degrees per second around the loop (negative = the other way). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Glimmers")
	float SwimSpeed = 14.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Glimmers")
	float Depth = 45.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Glimmers")
	FLinearColor GlowColor = FLinearColor(0.25f, 0.9f, 1.f);

	virtual void Tick(float DeltaSeconds) override;

protected:
	virtual void BeginPlay() override;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> GlowMID;

	FVector Center = FVector::ZeroVector;
	float Angle = 0.f;
	float Time = 0.f;
};
