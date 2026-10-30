#include "FGBuildable.h"

#include "FGGameData.h"
#include "FGResourceNode.h"
#include "FGTowerSite.h"
#include "FGWeather.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
	const FName ColorParam(TEXT("Color"));
	const FName GlowParam(TEXT("Glow"));
	const FLinearColor GhostOk(0.1f, 1.f, 0.35f, 0.4f);
	const FLinearColor GhostBad(1.f, 0.12f, 0.1f, 0.4f);
	const FLinearColor InPortColor(0.1f, 0.45f, 1.f);
	const FLinearColor OutPortColor(1.f, 0.5f, 0.05f);

	UStaticMeshComponent* MakeMeshComponent(AActor* Owner, USceneComponent* Parent, const TCHAR* Name)
	{
		UStaticMeshComponent* Comp = Owner->CreateDefaultSubobject<UStaticMeshComponent>(Name);
		Comp->SetupAttachment(Parent);
		return Comp;
	}

	/** Scale a mesh so its bounds fill Size (cm), sitting on Z = BaseZ. */
	void FitMesh(UStaticMeshComponent* Comp, UStaticMesh* Mesh, const FVector& Size, float BaseZ)
	{
		Comp->SetStaticMesh(Mesh);
		if (!Mesh)
		{
			return;
		}
		const FBox Bounds = Mesh->GetBoundingBox();
		const FVector Ext = Bounds.GetSize();
		const FVector Scale(Size.X / FMath::Max(Ext.X, 1.0), Size.Y / FMath::Max(Ext.Y, 1.0), Size.Z / FMath::Max(Ext.Z, 1.0));
		const FVector Center = Bounds.GetCenter();
		Comp->SetRelativeScale3D(Scale);
		Comp->SetRelativeLocation(FVector(-Center.X * Scale.X, -Center.Y * Scale.Y, BaseZ - Bounds.Min.Z * Scale.Z));
	}
}

AFGBuildable::AFGBuildable()
{
	PrimaryActorTick.bCanEverTick = true;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	// Dynamic, so the build-placement trace (static geometry only) sees the ground, not machines.
	Body = MakeMeshComponent(this, SceneRoot, TEXT("Body"));
	Body->SetCollisionProfileName(UCollisionProfile::BlockAllDynamic_ProfileName);

	Top = MakeMeshComponent(this, SceneRoot, TEXT("Top"));
	Top->SetCollisionProfileName(UCollisionProfile::BlockAllDynamic_ProfileName);
	Top->SetVisibility(false);

	InPort = MakeMeshComponent(this, SceneRoot, TEXT("InPort"));
	InPort->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	InPort->SetVisibility(false);

	OutPort = MakeMeshComponent(this, SceneRoot, TEXT("OutPort"));
	OutPort->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	OutPort->SetVisibility(false);
}

void AFGBuildable::InitFromRow(FName InRowName, const FFGBuildableRow& InRow, bool bInGhost)
{
	RowName = InRowName;
	Row = InRow;
	bGhost = bInGhost;
	bRowInitialized = true;
	ApplyVisuals();
	if (bGhost)
	{
		SetActorEnableCollision(false);
		SetActorTickEnabled(false);
	}
	OnRowInitialized();
}

void AFGBuildable::BeginPlay()
{
	Super::BeginPlay();
	// Level-placed buildables (test layouts, scripted scenes) only carry a row name.
	if (!bRowInitialized && !RowName.IsNone())
	{
		if (const FFGBuildableRow* Found = UFGGameData::FindBuildable(RowName))
		{
			InitFromRow(RowName, *Found, false);
		}
	}
}

void AFGBuildable::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (!RowName.IsNone() || !Row.Mesh.IsNull())
	{
		ApplyVisuals();
	}
}

void AFGBuildable::ApplyVisuals()
{
	UStaticMesh* Mesh = UFGGameData::LoadMesh(Row.Mesh);
	if (!Mesh)
	{
		Mesh = UFGGameData::CubeMesh();
	}
	const float SizeX = Row.Size.X * CellSize * 0.92f;
	const float SizeY = Row.Size.Y * CellSize * 0.92f;
	FitMesh(Body, Mesh, FVector(SizeX, SizeY, Row.Height), 0.f);

	UMaterialInterface* Base = bGhost ? UFGGameData::GhostMaterial() : UFGGameData::ColorMaterial();
	BodyMID = UMaterialInstanceDynamic::Create(Base, this);
	BodyMID->SetVectorParameterValue(ColorParam, bGhost ? GhostOk : Row.Color);
	Body->SetMaterial(0, BodyMID);

	if (UStaticMesh* TopMesh = UFGGameData::LoadMesh(Row.TopMesh))
	{
		FitMesh(Top, TopMesh, FVector(SizeX * Row.TopScale.X, SizeY * Row.TopScale.Y, Row.Height * Row.TopScale.Z), Row.Height);
		TopMID = UMaterialInstanceDynamic::Create(Base, this);
		TopMID->SetVectorParameterValue(ColorParam, bGhost ? GhostOk : Row.AccentColor);
		Top->SetMaterial(0, TopMID);
		Top->SetVisibility(true);
	}
	else
	{
		Top->SetVisibility(false);
	}

	// Port markers: blue = in, orange = out.
	UStaticMesh* Cube = UFGGameData::CubeMesh();
	const float HalfX = Row.Size.X * CellSize * 0.5f;
	auto SetupPort = [&](UStaticMeshComponent* Port, bool bShow, float X, const FLinearColor& Color)
	{
		Port->SetVisibility(bShow);
		if (!bShow)
		{
			return;
		}
		Port->SetStaticMesh(Cube);
		Port->SetRelativeLocation(FVector(X, 0.f, PortHeight));
		Port->SetRelativeScale3D(FVector(0.18f, 0.5f, 0.3f));
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, this);
		MID->SetVectorParameterValue(ColorParam, bGhost ? GhostOk : Color);
		MID->SetScalarParameterValue(GlowParam, bGhost ? 0.f : 2.f);
		Port->SetMaterial(0, MID);
	};
	SetupPort(InPort, HasInputPort(), -HalfX - 6.f, InPortColor);
	SetupPort(OutPort, HasOutputPort(), HalfX + 6.f, OutPortColor);
}

void AFGBuildable::SetGhostValid(bool bValid)
{
	const FLinearColor Color = bValid ? GhostOk : GhostBad;
	for (UStaticMeshComponent* Comp : { Body.Get(), Top.Get(), InPort.Get(), OutPort.Get() })
	{
		if (Comp)
		{
			if (UMaterialInstanceDynamic* MID = Cast<UMaterialInstanceDynamic>(Comp->GetMaterial(0)))
			{
				MID->SetVectorParameterValue(ColorParam, Color);
			}
		}
	}
}

void AFGBuildable::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bGhost)
	{
		UpdateWorkingLight(DeltaSeconds);
	}
}

void AFGBuildable::UpdateWorkingLight(float DeltaSeconds)
{
	// The top part glows softly while the machine works.
	const float Target = IsWorking() ? 1.f : 0.f;
	WorkGlow = FMath::FInterpTo(WorkGlow, Target, DeltaSeconds, 3.f);
	if (TopMID)
	{
		TopMID->SetScalarParameterValue(GlowParam, WorkGlow * 3.f);
	}
}

bool AFGBuildable::AcceptsItem(FName Item) const
{
	return AcceptsItemType(Item) && CountInput(Item) < Row.BufferSize;
}

bool AFGBuildable::TryInsert(FName Item)
{
	if (!AcceptsItem(Item))
	{
		return false;
	}
	InputBuffer.FindOrAdd(Item)++;
	return true;
}

bool AFGBuildable::TakeOutputFor(const AFGBuildable* Target, FName& OutItem)
{
	FName Found;
	for (TPair<FName, int32>& Pair : OutputBuffer)
	{
		if (Pair.Value > 0 && (!Target || Target->AcceptsItem(Pair.Key)))
		{
			Found = Pair.Key;
			break;
		}
	}
	if (Found.IsNone())
	{
		return false;
	}
	int32& Count = OutputBuffer.FindChecked(Found);
	if (--Count <= 0)
	{
		OutputBuffer.Remove(Found);
	}
	OutItem = Found;
	return true;
}

int32 AFGBuildable::CountInput(FName Item) const
{
	const int32* Count = InputBuffer.Find(Item);
	return Count ? *Count : 0;
}

int32 AFGBuildable::CountOutput(FName Item) const
{
	const int32* Count = OutputBuffer.Find(Item);
	return Count ? *Count : 0;
}

int32 AFGBuildable::TotalOutput() const
{
	int32 Total = 0;
	for (const TPair<FName, int32>& Pair : OutputBuffer)
	{
		Total += Pair.Value;
	}
	return Total;
}

FVector AFGBuildable::GetInputPortLocation() const
{
	return GetActorTransform().TransformPosition(FVector(-Row.Size.X * CellSize * 0.5f - 12.f, 0.f, PortHeight));
}

FVector AFGBuildable::GetOutputPortLocation() const
{
	return GetActorTransform().TransformPosition(FVector(Row.Size.X * CellSize * 0.5f + 12.f, 0.f, PortHeight));
}

FIntPoint AFGBuildable::GetFootprint() const
{
	const int32 Quarter = FMath::RoundToInt(GetActorRotation().Yaw / 90.f);
	return (Quarter % 2 == 0) ? Row.Size : FIntPoint(Row.Size.Y, Row.Size.X);
}

FIntPoint AFGBuildable::GetGridOrigin() const
{
	const FIntPoint Footprint = GetFootprint();
	const FVector Location = GetActorLocation();
	return FIntPoint(
		FMath::RoundToInt(Location.X / CellSize - Footprint.X * 0.5f),
		FMath::RoundToInt(Location.Y / CellSize - Footprint.Y * 0.5f));
}

FString AFGBuildable::GetStatusText() const
{
	return FString();
}

void AFGBuildable::GetRefund(TArray<FFGItemStack>& Out) const
{
	Out = Row.Cost;
	for (const TPair<FName, int32>& Pair : InputBuffer)
	{
		Out.Add({ Pair.Key, Pair.Value });
	}
	for (const TPair<FName, int32>& Pair : OutputBuffer)
	{
		Out.Add({ Pair.Key, Pair.Value });
	}
}

void AFGBuildable::GetPowerTotals(const UWorld* World, float& OutSupply, float& OutDemand)
{
	OutSupply = 0.f;
	OutDemand = 0.f;
	if (!World)
	{
		return;
	}
	for (TActorIterator<AFGBuildable> It(const_cast<UWorld*>(World)); It; ++It)
	{
		OutSupply += It->GetPowerOutput();
		OutDemand += It->GetPowerUse();
	}
}

float AFGBuildable::GetPowerSatisfaction(const UWorld* World)
{
	static uint64 CachedFrame = MAX_uint64;
	static const UWorld* CachedWorld = nullptr;
	static float Cached = 1.f;
	if (CachedFrame != GFrameCounter || CachedWorld != World)
	{
		float Supply, Demand;
		GetPowerTotals(World, Supply, Demand);
		Cached = Demand <= KINDA_SMALL_NUMBER ? 1.f : FMath::Clamp(Supply / Demand, 0.f, 1.f);
		CachedFrame = GFrameCounter;
		CachedWorld = World;
	}
	return Cached;
}

FString AFGBuildable::BufferToString(const TMap<FName, int32>& Buffer)
{
	TArray<FString> Parts;
	for (const TPair<FName, int32>& Pair : Buffer)
	{
		if (Pair.Value > 0)
		{
			Parts.Add(FString::Printf(TEXT("%d %s"), Pair.Value, *UFGGameData::ItemName(Pair.Key).ToString()));
		}
	}
	return Parts.Num() ? FString::Join(Parts, TEXT(", ")) : TEXT("empty");
}

// ---------------------------------------------------------------- Machine

void AFGMachine::OnRowInitialized()
{
	UFGGameData::GetRecipesForMachine(Row.MachineType, Recipes);
}

bool AFGMachine::AcceptsItemType(FName Item) const
{
	for (const FFGRecipeRow& Recipe : Recipes)
	{
		for (const FFGItemStack& In : Recipe.Inputs)
		{
			if (In.Item == Item)
			{
				return true;
			}
		}
	}
	return false;
}

bool AFGMachine::CanStart(const FFGRecipeRow& Recipe) const
{
	for (const FFGItemStack& In : Recipe.Inputs)
	{
		if (CountInput(In.Item) < In.Count)
		{
			return false;
		}
	}
	for (const FFGItemStack& Out : Recipe.Outputs)
	{
		if (CountOutput(Out.Item) + Out.Count > Row.BufferSize)
		{
			return false;
		}
	}
	return Recipe.Inputs.Num() > 0;
}

void AFGMachine::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bGhost)
	{
		return;
	}

	if (ActiveRecipe == INDEX_NONE)
	{
		for (int32 Index = 0; Index < Recipes.Num(); ++Index)
		{
			if (CanStart(Recipes[Index]))
			{
				for (const FFGItemStack& In : Recipes[Index].Inputs)
				{
					int32& Count = InputBuffer.FindChecked(In.Item);
					Count -= In.Count;
					if (Count <= 0)
					{
						InputBuffer.Remove(In.Item);
					}
				}
				ActiveRecipe = Index;
				Progress = 0.f;
				break;
			}
		}
	}

	if (ActiveRecipe != INDEX_NONE)
	{
		const FFGRecipeRow& Recipe = Recipes[ActiveRecipe];
		Progress += DeltaSeconds * GetPowerSatisfaction(GetWorld()) / FMath::Max(Recipe.CraftTime, 0.1f);
		if (Progress >= 1.f)
		{
			for (const FFGItemStack& Out : Recipe.Outputs)
			{
				OutputBuffer.FindOrAdd(Out.Item) += Out.Count;
			}
			ActiveRecipe = INDEX_NONE;
			Progress = 0.f;
		}
	}
}

FString AFGMachine::GetStatusText() const
{
	FString State;
	if (ActiveRecipe != INDEX_NONE && Recipes.IsValidIndex(ActiveRecipe))
	{
		const FFGRecipeRow& Recipe = Recipes[ActiveRecipe];
		const FName OutItem = Recipe.Outputs.Num() ? Recipe.Outputs[0].Item : NAME_None;
		State = FString::Printf(TEXT("Making %s  %d%%"), *UFGGameData::ItemName(OutItem).ToString(), FMath::RoundToInt(Progress * 100.f));
		if (GetPowerSatisfaction(GetWorld()) < 0.99f)
		{
			State += TEXT("  (low power)");
		}
	}
	else
	{
		TArray<FString> Makes;
		for (const FFGRecipeRow& Recipe : Recipes)
		{
			Makes.Add(FString::Printf(TEXT("%s -> %s"), *UFGGameData::StacksToString(Recipe.Inputs), *UFGGameData::StacksToString(Recipe.Outputs)));
		}
		State = TEXT("Idle. Recipes: ") + FString::Join(Makes, TEXT("  |  "));
	}
	return FString::Printf(TEXT("%s\nIn: %s\nOut: %s"), *State, *BufferToString(InputBuffer), *BufferToString(OutputBuffer));
}

// ---------------------------------------------------------------- Extractor

bool AFGExtractor::IsWorking() const
{
	return CountOutput(Row.ExtractItem) < Row.BufferSize;
}

void AFGExtractor::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bGhost || Row.ExtractItem.IsNone())
	{
		return;
	}
	if (CountOutput(Row.ExtractItem) < Row.BufferSize)
	{
		// Lightning rods (no node) barely trickle in calm weather and charge fast in a storm.
		const float WeatherFactor = Row.bNoNode ? FMath::Lerp(1.f / 6.f, 1.f, AFGWeather::GetIntensity(GetWorld())) : 1.f;
		Timer += DeltaSeconds * GetPowerSatisfaction(GetWorld()) * WeatherFactor;
		if (Timer >= Row.ExtractInterval)
		{
			Timer = 0.f;
			OutputBuffer.FindOrAdd(Row.ExtractItem)++;
		}
	}
}

FString AFGExtractor::GetStatusText() const
{
	const FString Item = UFGGameData::ItemName(Row.ExtractItem).ToString();
	if (!IsWorking())
	{
		return FString::Printf(TEXT("Output full (%d %s). Connect a belt or press E."), CountOutput(Row.ExtractItem), *Item);
	}
	return FString::Printf(TEXT("Extracting %s  %d%%\nOut: %s"), *Item,
		FMath::RoundToInt(100.f * Timer / FMath::Max(Row.ExtractInterval, 0.1f)), *BufferToString(OutputBuffer));
}

// ---------------------------------------------------------------- Generator

void AFGGenerator::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bGhost || Row.FuelItem.IsNone())
	{
		return;
	}
	if (BurnLeft <= 0.f && CountInput(Row.FuelItem) > 0)
	{
		int32& Count = InputBuffer.FindChecked(Row.FuelItem);
		if (--Count <= 0)
		{
			InputBuffer.Remove(Row.FuelItem);
		}
		BurnLeft = Row.FuelTime;
	}
	if (BurnLeft > 0.f)
	{
		BurnLeft -= DeltaSeconds;
	}
}

float AFGGenerator::GetPowerOutput() const
{
	if (bGhost)
	{
		return 0.f;
	}
	if (Row.FuelItem.IsNone())
	{
		// Sun power: storms cut it to 30%.
		return Row.PowerOutput * FMath::Lerp(1.f, 0.3f, AFGWeather::GetIntensity(GetWorld()));
	}
	return BurnLeft > 0.f ? Row.PowerOutput : 0.f;
}

FString AFGGenerator::GetStatusText() const
{
	if (Row.FuelItem.IsNone())
	{
		return FString::Printf(TEXT("Producing %.0f power"), GetPowerOutput());
	}
	const FString Fuel = UFGGameData::ItemName(Row.FuelItem).ToString();
	if (BurnLeft > 0.f)
	{
		return FString::Printf(TEXT("Burning %s: %.0f power\nFuel left: %d"), *Fuel, Row.PowerOutput, CountInput(Row.FuelItem));
	}
	return FString::Printf(TEXT("Out of fuel. Feed it %s (belt or E)."), *Fuel);
}

// ---------------------------------------------------------------- Platform

void AFGPlatform::OnRowInitialized()
{
	if (bGhost)
	{
		return;
	}
	// Platforms are ground: static for the placement trace, tagged as buildable.
	Body->SetCollisionObjectType(ECC_WorldStatic);
	Tags.AddUnique(TEXT("Buildable"));
}

// ---------------------------------------------------------------- Translator

bool AFGTranslator::IsWorking() const
{
	return !bGhost && GetPowerSatisfaction(GetWorld()) > 0.5f;
}

FString AFGTranslator::GetStatusText() const
{
	const AFGTowerSite* Tower = nullptr;
	for (TActorIterator<AFGTowerSite> It(GetWorld()); It; ++It)
	{
		Tower = *It;
		break;
	}
	const int32 Trust = Tower ? Tower->GlimmerTrust : 0;
	return FString::Printf(TEXT("%s\nUnderstood trades: %d"), IsWorking() ? TEXT("Listening to the Glimmers.") : TEXT("Needs power."), Trust);
}

AFGTranslator* AFGTranslator::FindWorking(const UWorld* World)
{
	if (!World)
	{
		return nullptr;
	}
	for (TActorIterator<AFGTranslator> It(const_cast<UWorld*>(World)); It; ++It)
	{
		if (It->IsWorking())
		{
			return *It;
		}
	}
	return nullptr;
}

// ---------------------------------------------------------------- Trade buoy

void AFGTradeBuoy::StartTrade(int32 Fish, int32 Chests, int32 PhaseNumber)
{
	// What the Glimmers ask for grows with the story.
	TArray<FName> Wants = { TEXT("Wire"), TEXT("CoralSheet"), TEXT("SteelPlate"), TEXT("Glass") };
	if (PhaseNumber >= 3)
	{
		Wants.Append({ TEXT("Frame"), TEXT("Lens"), TEXT("FreshWater") });
	}
	WantItem = Wants[FMath::RandRange(0, Wants.Num() - 1)];
	WantCount = FMath::Max(1, Fish) * ItemsPerFish;
	RewardPearls = FMath::Max(1, Chests);
	Delivered = 0;
	State = EFGTradeState::Active;
}

void AFGTradeBuoy::Misunderstood()
{
	State = EFGTradeState::Cooldown;
	Cooldown = 8.f;
}

void AFGTradeBuoy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (State == EFGTradeState::Cooldown)
	{
		Cooldown -= DeltaSeconds;
		if (Cooldown <= 0.f)
		{
			State = EFGTradeState::Waiting;
		}
	}
}

bool AFGTradeBuoy::TryInsert(FName Item)
{
	if (!AcceptsItem(Item))
	{
		return false;
	}
	if (++Delivered >= WantCount)
	{
		OutputBuffer.FindOrAdd(TEXT("GlimmerPearl")) += RewardPearls;
		for (TActorIterator<AFGTowerSite> It(GetWorld()); It; ++It)
		{
			It->GlimmerTrust++;
			break;
		}
		State = EFGTradeState::Cooldown;
		Cooldown = 20.f;
	}
	return true;
}

FString AFGTradeBuoy::GetStatusText() const
{
	FString Text;
	switch (State)
	{
	case EFGTradeState::Waiting:
		Text = TEXT("A Glimmer is waiting. Press E to talk (needs a working Translator).");
		break;
	case EFGTradeState::Active:
		Text = FString::Printf(TEXT("Trade: %d / %d %s  ->  %d Glimmer Pearl(s)"), Delivered, WantCount,
			*UFGGameData::ItemName(WantItem).ToString(), RewardPearls);
		break;
	case EFGTradeState::Cooldown:
		Text = FString::Printf(TEXT("The Glimmers are away. Back in %.0f s."), FMath::Max(Cooldown, 0.f));
		break;
	}
	if (TotalOutput() > 0)
	{
		Text += FString::Printf(TEXT("\nReady to collect: %s"), *BufferToString(OutputBuffer));
	}
	return Text;
}

// ---------------------------------------------------------------- Storage

bool AFGStorage::AcceptsItem(FName Item) const
{
	return AcceptsItemType(Item) && TotalOutput() < Row.BufferSize;
}

bool AFGStorage::TryInsert(FName Item)
{
	if (!AcceptsItem(Item))
	{
		return false;
	}
	OutputBuffer.FindOrAdd(Item)++;
	return true;
}

FString AFGStorage::GetStatusText() const
{
	return FString::Printf(TEXT("Stored %d / %d\n%s"), TotalOutput(), Row.BufferSize, *BufferToString(OutputBuffer));
}
