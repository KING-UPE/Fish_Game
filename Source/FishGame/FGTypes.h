#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "FGTypes.generated.h"

class UStaticMesh;

/** A number of one item, e.g. 2 Scrap Metal. */
USTRUCT(BlueprintType)
struct FFGItemStack
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FName Item;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	int32 Count = 1;
};

/** DT_Items row. Row name = item id (e.g. ScrapMetal). */
USTRUCT(BlueprintType)
struct FFGItemRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FText DisplayName;

	/** Colour of the item cubes riding on belts. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FLinearColor Color = FLinearColor::White;
};

/** DT_Recipes row. A machine crafts the first recipe whose inputs it has. */
USTRUCT(BlueprintType)
struct FFGRecipeRow : public FTableRowBase
{
	GENERATED_BODY()

	/** Machine type that crafts this (matches FFGBuildableRow::MachineType). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FName Machine;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	TArray<FFGItemStack> Inputs;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	TArray<FFGItemStack> Outputs;

	/** Seconds per craft at full power. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float CraftTime = 2.f;
};

UENUM(BlueprintType)
enum class EFGBuildableKind : uint8
{
	Machine,
	Extractor,
	Generator,
	Storage,
	Belt,
	/** Floating platform: extends the buildable ground over the water. */
	Platform,
	/** Lets you understand the Glimmers (needed for trades). */
	Translator,
	/** Where Glimmer trades happen (needs a working Translator). */
	TradeBuoy,
	/** Passive structure (breakwater, reef filter): no ports, works by being there. */
	Structure
};

/** DT_Buildables row: everything the player can build. Row order = hotbar order. */
USTRUCT(BlueprintType)
struct FFGBuildableRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	EFGBuildableKind Kind = EFGBuildableKind::Machine;

	/** Machines: which recipes they run (FFGRecipeRow::Machine). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FName MachineType;

	/** Build cost. For belts: cost per 2 m segment. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	TArray<FFGItemStack> Cost;

	/** Footprint in 1 m grid cells (X = length, along the input → output direction). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FIntPoint Size = FIntPoint(2, 2);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float Height = 200.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	TSoftObjectPtr<UStaticMesh> Mesh;

	/** Optional second mesh stacked on top of the body (chimney, dish, drill head...). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	TSoftObjectPtr<UStaticMesh> TopMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FVector TopScale = FVector(0.5f, 0.5f, 0.5f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FLinearColor Color = FLinearColor::Gray;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FLinearColor AccentColor = FLinearColor(1.f, 0.55f, 0.1f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float PowerUse = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float PowerOutput = 0.f;

	/** Extractors: the resource node item they must sit on and produce. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FName ExtractItem;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float ExtractInterval = 2.f;

	/** Must be placed at the waterline or on a platform (sea pumps). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	bool bNeedsWater = false;

	/** Extractors that don't need a resource node (lightning rods pull crystals from the storm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	bool bNoNode = false;

	/** Generators: item burned for power (None = free power, e.g. solar). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FName FuelItem;

	/** Generators: seconds of power per fuel item. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float FuelTime = 4.f;

	/** Darkens the sea while working (Ocean Health, Phase 3+). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	float Pollution = 0.f;

	/** Max items per input/output slot (storage: total capacity). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	int32 BufferSize = 10;

	/** Story phase (1-5) in which this unlocks. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	int32 Phase = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Factory")
	FText Description;
};

UENUM(BlueprintType)
enum class EFGLineStyle : uint8
{
	Normal,
	Flashback,
	/** A big centred card (scene heading / chapter title). */
	Title,
	/** Not shown as text: opens Skye's drawing (a Fish API puzzle). */
	Puzzle
};

USTRUCT(BlueprintType)
struct FFGStoryLine
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	FText Speaker;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	FText Text;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	float Duration = 4.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	EFGLineStyle Style = EFGLineStyle::Normal;
};

/** DT_Phases row: one Signal Tower phase. Row order = phase order. */
USTRUCT(BlueprintType)
struct FFGPhaseRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	FText Title;

	/** What the tower part needs. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	FText TowerPart;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	TArray<FFGItemStack> Requirements;

	/** Echo lines when the phase starts (goals, tutorial). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	TArray<FFGStoryLine> Intro;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	TArray<FFGStoryLine> MessageHome;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	FText FlashbackTitle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	TArray<FFGStoryLine> Flashback;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	TArray<FFGStoryLine> Reply;

	/** Skye's reply includes a drawing to count (a Fish API picture). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Story")
	bool bReplyHasDrawing = true;
};
