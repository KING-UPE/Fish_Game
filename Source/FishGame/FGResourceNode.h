#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FGResourceNode.generated.h"

class UStaticMeshComponent;

/** A spot the player can gather from by hand (E) or cover with an extractor. */
UCLASS()
class FISHGAME_API AFGResourceNode : public AActor
{
	GENERATED_BODY()

public:
	AFGResourceNode();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Factory")
	TObjectPtr<UStaticMeshComponent> Mesh;

	/** Item id from DT_Items (ScrapMetal, CoralOre...). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FName Item = TEXT("ScrapMetal");

	/** Tint the mesh with the item's colour. Off for nodes that use their own art. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	bool bTintFromItem = true;

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	void ApplyTint();
};
