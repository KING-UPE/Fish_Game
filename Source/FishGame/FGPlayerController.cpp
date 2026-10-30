#include "FGPlayerController.h"

#include "FGBelt.h"
#include "FGBuildable.h"
#include "FGFishApi.h"
#include "FGGameData.h"
#include "FGResourceNode.h"
#include "FGSaveGame.h"
#include "FGTowerSite.h"
#include "FGWeather.h"
#include "FishGame.h"
#include "Kismet/GameplayStatics.h"
#include "Components/InputComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/DataTable.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"

#define LOCTEXT_NAMESPACE "FishGame"

namespace
{
	const FText Echo = LOCTEXT("Echo", "Echo");
	const FText Neela = LOCTEXT("Neela", "Neela");
	const FText FlashbackMarker = LOCTEXT("FlashbackMarker", "FLASHBACK");

	UClass* ClassForKind(EFGBuildableKind Kind)
	{
		switch (Kind)
		{
		case EFGBuildableKind::Extractor: return AFGExtractor::StaticClass();
		case EFGBuildableKind::Generator: return AFGGenerator::StaticClass();
		case EFGBuildableKind::Storage: return AFGStorage::StaticClass();
		case EFGBuildableKind::Platform: return AFGPlatform::StaticClass();
		case EFGBuildableKind::Translator: return AFGTranslator::StaticClass();
		case EFGBuildableKind::TradeBuoy: return AFGTradeBuoy::StaticClass();
		case EFGBuildableKind::Structure: return AFGBuildable::StaticClass();
		default: return AFGMachine::StaticClass();
		}
	}

	FIntPoint RotatedSize(const FIntPoint& Size, int32 Yaw)
	{
		return ((Yaw / 90) % 2 == 0) ? Size : FIntPoint(Size.Y, Size.X);
	}

	bool RectsOverlap(FIntPoint AOrigin, FIntPoint ASize, FIntPoint BOrigin, FIntPoint BSize)
	{
		return AOrigin.X < BOrigin.X + BSize.X && BOrigin.X < AOrigin.X + ASize.X
			&& AOrigin.Y < BOrigin.Y + BSize.Y && BOrigin.Y < AOrigin.Y + ASize.Y;
	}
}

AFGPlayerController::AFGPlayerController()
{
	PrimaryActorTick.bCanEverTick = true;
}

// ================================================================ Lifecycle

void AFGPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalController())
	{
		return;
	}

	for (TActorIterator<AFGTowerSite> It(GetWorld()); It; ++It)
	{
		Tower = *It;
		break;
	}
	if (Tower)
	{
		Tower->OnPhaseCompleted.AddUniqueDynamic(this, &AFGPlayerController::HandlePhaseCompleted);
		Tower->OnPhaseStarted.AddUniqueDynamic(this, &AFGPlayerController::HandlePhaseStarted);
	}
	else
	{
		UE_LOG(LogFishGame, Warning, TEXT("No AFGTowerSite in the level: phases and story won't run."));
	}

	if (LoadFactory())
	{
		RefreshHotbar();
		QueueLine(FText::GetEmpty(), LOCTEXT("GameTitle", "BLUE SIGNAL"), 3.f, EFGLineStyle::Title);
		QueueLine(Echo, LOCTEXT("WelcomeBack", "Welcome back. Everything is where you left it. Mostly."), 4.f);
		return;
	}

	RefreshHotbar();
	QueueLine(FText::GetEmpty(), LOCTEXT("GameTitle", "BLUE SIGNAL"), 3.5f, EFGLineStyle::Title);
	QueueLine(Echo, LOCTEXT("Prologue1", "Good news: we're alive. Bad news: everything else."), 4.5f);
	if (Tower)
	{
		HandlePhaseStarted(Tower->CurrentPhase);
	}
}

void AFGPlayerController::SaveFactory()
{
	if (!IsLocalController() || bNewGameRequested)
	{
		return;
	}
	UFGSaveGame* Save = Cast<UFGSaveGame>(UGameplayStatics::CreateSaveGameObject(UFGSaveGame::StaticClass()));
	TMap<const AFGBuildable*, int32> Indices;
	for (TActorIterator<AFGBuildable> It(GetWorld()); It; ++It)
	{
		if (It->bGhost || It->IsA<AFGTowerSite>() || It->RowName.IsNone())
		{
			continue;
		}
		FFGSavedBuildable& Saved = Save->Buildables.AddDefaulted_GetRef();
		Saved.Row = It->RowName;
		Saved.Transform = It->GetActorTransform();
		Saved.Input = It->InputBuffer;
		Saved.Output = It->OutputBuffer;
		Indices.Add(*It, Save->Buildables.Num() - 1);
	}
	for (TActorIterator<AFGBelt> It(GetWorld()); It; ++It)
	{
		auto IndexOf = [&](const AFGBuildable* Buildable) -> int32
		{
			if (Cast<AFGTowerSite>(Buildable))
			{
				return UFGSaveGame::TowerIndex;
			}
			const int32* Found = Indices.Find(Buildable);
			return Found ? *Found : INDEX_NONE;
		};
		FFGSavedBelt Belt;
		Belt.Source = IndexOf(It->Source.Get());
		Belt.Target = IndexOf(It->Target.Get());
		if (Belt.Source != INDEX_NONE && Belt.Target != INDEX_NONE)
		{
			Save->Belts.Add(Belt);
		}
	}
	Save->Inventory = Inventory;
	Save->HintsShown = HintsShown.Array();
	if (Tower)
	{
		Save->Phase = Tower->CurrentPhase;
		Save->Delivered = Tower->Delivered;
		Save->GlimmerTrust = Tower->GlimmerTrust;
		Save->OceanHealth = Tower->OceanHealth;
	}
	if (APawn* MyPawn = GetPawn())
	{
		Save->PlayerLocation = MyPawn->GetActorLocation();
		Save->PlayerRotation = GetControlRotation();
	}
	UGameplayStatics::SaveGameToSlot(Save, UFGSaveGame::SlotName, 0);
}

bool AFGPlayerController::LoadFactory()
{
	if (!UGameplayStatics::DoesSaveGameExist(UFGSaveGame::SlotName, 0))
	{
		return false;
	}
	const UFGSaveGame* Save = Cast<UFGSaveGame>(UGameplayStatics::LoadGameFromSlot(UFGSaveGame::SlotName, 0));
	if (!Save)
	{
		return false;
	}

	TArray<AFGBuildable*> Spawned;
	FActorSpawnParameters Spawn;
	Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	for (const FFGSavedBuildable& Saved : Save->Buildables)
	{
		const FFGBuildableRow* Row = UFGGameData::FindBuildable(Saved.Row);
		AFGBuildable* Built = Row ? GetWorld()->SpawnActor<AFGBuildable>(ClassForKind(Row->Kind), Saved.Transform, Spawn) : nullptr;
		if (Built)
		{
			Built->InitFromRow(Saved.Row, *Row, false);
			Built->InputBuffer = Saved.Input;
			Built->OutputBuffer = Saved.Output;
		}
		Spawned.Add(Built);
	}
	const FFGBuildableRow* BeltRow = UFGGameData::FindBuildable(TEXT("Belt"));
	for (const FFGSavedBelt& Saved : Save->Belts)
	{
		auto Resolve = [&](int32 Index) -> AFGBuildable*
		{
			if (Index == UFGSaveGame::TowerIndex)
			{
				return Tower;
			}
			return Spawned.IsValidIndex(Index) ? Spawned[Index] : nullptr;
		};
		AFGBuildable* Source = Resolve(Saved.Source);
		AFGBuildable* Target = Resolve(Saved.Target);
		if (Source && Target)
		{
			AFGBelt* Belt = GetWorld()->SpawnActor<AFGBelt>(AFGBelt::StaticClass(), FTransform::Identity, Spawn);
			Belt->Setup(Source, Target, BeltRow ? BeltRow->Cost : TArray<FFGItemStack>());
		}
	}

	Inventory = Save->Inventory;
	HintsShown = TSet<FName>(Save->HintsShown);
	if (Tower)
	{
		Tower->RestoreState(Save->Phase, Save->Delivered, Save->GlimmerTrust, Save->OceanHealth);
	}
	if (!Save->PlayerLocation.IsNearlyZero())
	{
		bPendingPlayerRestore = true;
		RestoreLocation = Save->PlayerLocation;
		RestoreRotation = Save->PlayerRotation;
	}
	UE_LOG(LogFishGame, Log, TEXT("Loaded save: %d buildables, %d belts, phase %d."), Save->Buildables.Num(), Save->Belts.Num(), Save->Phase + 1);
	return true;
}

void AFGPlayerController::FGSave()
{
	SaveFactory();
	ShowToast(TEXT("Saved"));
}

void AFGPlayerController::FGNewGame()
{
	bNewGameRequested = true;
	UGameplayStatics::DeleteGameInSlot(UFGSaveGame::SlotName, 0);
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this)));
}

void AFGPlayerController::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (EndPlayReason == EEndPlayReason::Quit || EndPlayReason == EEndPlayReason::EndPlayInEditor)
	{
		SaveFactory();
	}
	if (Ghost)
	{
		Ghost->Destroy();
		Ghost = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void AFGPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
	check(InputComponent);

	InputComponent->BindKey(EKeys::E, IE_Pressed, this, &AFGPlayerController::OnInteract);
	InputComponent->BindKey(EKeys::E, IE_Repeat, this, &AFGPlayerController::OnInteractRepeat);
	InputComponent->BindKey(EKeys::LeftMouseButton, IE_Pressed, this, &AFGPlayerController::OnPrimary);
	InputComponent->BindKey(EKeys::RightMouseButton, IE_Pressed, this, &AFGPlayerController::OnCancel);
	InputComponent->BindKey(EKeys::Q, IE_Pressed, this, &AFGPlayerController::OnCancel);
	InputComponent->BindKey(EKeys::R, IE_Pressed, this, &AFGPlayerController::OnRotate);
	InputComponent->BindKey(EKeys::X, IE_Pressed, this, &AFGPlayerController::OnDismantle);
	InputComponent->BindKey(EKeys::Tab, IE_Pressed, this, &AFGPlayerController::OnNextPage);

	const FKey Numbers[] = { EKeys::One, EKeys::Two, EKeys::Three, EKeys::Four, EKeys::Five,
		EKeys::Six, EKeys::Seven, EKeys::Eight, EKeys::Nine, EKeys::Zero };
	for (int32 Index = 0; Index < UE_ARRAY_COUNT(Numbers); ++Index)
	{
		FInputKeyBinding Binding(FInputChord(Numbers[Index]), IE_Pressed);
		Binding.KeyDelegate.GetDelegateForManualSet().BindUObject(this, &AFGPlayerController::OnNumber, Index);
		InputComponent->KeyBindings.Emplace(MoveTemp(Binding));
	}
}

void AFGPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);
	if (!IsLocalController())
	{
		return;
	}

	GatherCooldown = FMath::Max(0.f, GatherCooldown - DeltaTime);
	ToastTime = FMath::Max(0.f, ToastTime - DeltaTime);

	if (bPendingPlayerRestore)
	{
		if (APawn* MyPawn = GetPawn())
		{
			MyPawn->TeleportTo(RestoreLocation, MyPawn->GetActorRotation());
			SetControlRotation(RestoreRotation);
			bPendingPlayerRestore = false;
		}
	}

	AutosaveTimer += DeltaTime;
	if (AutosaveTimer >= 60.f)
	{
		AutosaveTimer = 0.f;
		SaveFactory();
	}

	CheckFallIntoSea();
	UpdateLook();
	RefreshHotbar();
	UpdateGhost();
	UpdateStory(DeltaTime);
	UpdateHints();

	// Belt preview line while choosing the belt's end.
	if (AFGBuildable* Start = BeltStart.Get())
	{
		const FVector From = Start->GetOutputPortLocation();
		FVector To = LookPoint;
		if (AFGBuildable* Over = Cast<AFGBuildable>(LookActor.Get()))
		{
			if (Over != Start && Over->HasInputPort())
			{
				To = Over->GetInputPortLocationFor(From);
			}
		}
		const bool bTooLong = FVector::Dist(From, To) > AFGBelt::MaxLength;
		DrawDebugLine(GetWorld(), From, To, bTooLong ? FColor::Red : FColor(80, 200, 255), false, -1.f, 0, 6.f);
	}
}

void AFGPlayerController::CheckFallIntoSea()
{
	APawn* MyPawn = GetPawn();
	if (!MyPawn)
	{
		return;
	}
	const FVector Location = MyPawn->GetActorLocation();
	if (Location.Z > 120.f)
	{
		// Standing on dry ground: remember it (sampled, not every frame-perfect).
		SafeLocation = Location;
		bHasSafeLocation = true;
	}
	else if (Location.Z < -60.f && bHasSafeLocation)
	{
		MyPawn->TeleportTo(SafeLocation + FVector(0.f, 0.f, 50.f), MyPawn->GetActorRotation());
		Hint(TEXT("NoSwimming"), LOCTEXT("HintSwim", "Let's not swim. The suit isn't sealed, and neither are you."));
		ShowToast(TEXT("Back on the island"));
	}
}

// ================================================================ Inventory

int32 AFGPlayerController::CountItem(FName Item) const
{
	const int32* Count = Inventory.Find(Item);
	return Count ? *Count : 0;
}

bool AFGPlayerController::HasItems(const TArray<FFGItemStack>& Stacks, int32 Multiplier) const
{
	for (const FFGItemStack& Stack : Stacks)
	{
		if (CountItem(Stack.Item) < Stack.Count * Multiplier)
		{
			return false;
		}
	}
	return true;
}

void AFGPlayerController::RemoveItems(const TArray<FFGItemStack>& Stacks, int32 Multiplier)
{
	for (const FFGItemStack& Stack : Stacks)
	{
		AddItem(Stack.Item, -Stack.Count * Multiplier);
	}
}

void AFGPlayerController::AddItems(const TArray<FFGItemStack>& Stacks)
{
	for (const FFGItemStack& Stack : Stacks)
	{
		AddItem(Stack.Item, Stack.Count);
	}
}

void AFGPlayerController::AddItem(FName Item, int32 Count)
{
	if (Item.IsNone() || Count == 0)
	{
		return;
	}
	int32& Held = Inventory.FindOrAdd(Item);
	Held += Count;
	if (Held <= 0)
	{
		Inventory.Remove(Item);
	}
}

FString AFGPlayerController::MissingItemsText(const TArray<FFGItemStack>& Stacks, int32 Multiplier) const
{
	TArray<FString> Parts;
	for (const FFGItemStack& Stack : Stacks)
	{
		const int32 Missing = Stack.Count * Multiplier - CountItem(Stack.Item);
		if (Missing > 0)
		{
			Parts.Add(FString::Printf(TEXT("%d more %s"), Missing, *UFGGameData::ItemName(Stack.Item).ToString()));
		}
	}
	return FString::Join(Parts, TEXT(", "));
}

// ================================================================ Looking & building

void AFGPlayerController::UpdateLook()
{
	FVector ViewLocation;
	FRotator ViewRotation;
	GetPlayerViewPoint(ViewLocation, ViewRotation);
	const FVector End = ViewLocation + ViewRotation.Vector() * BuildRange;

	FCollisionQueryParams Params(SCENE_QUERY_STAT(FGLook), false);
	if (APawn* MyPawn = GetPawn())
	{
		Params.AddIgnoredActor(MyPawn);
	}
	if (Ghost)
	{
		Params.AddIgnoredActor(Ghost);
	}

	FHitResult Hit;
	bLookHit = GetWorld()->LineTraceSingleByChannel(Hit, ViewLocation, End, ECC_Visibility, Params);
	LookActor = bLookHit ? Hit.GetActor() : nullptr;
	LookPoint = bLookHit ? FVector(Hit.ImpactPoint) : End;
	LookDistance = bLookHit ? Hit.Distance : BuildRange;

	// Placement only cares about static level geometry (islands, platforms), not machines or nodes.
	FCollisionObjectQueryParams Ground(ECC_WorldStatic);
	FHitResult GroundHitResult;
	bGroundHit = GetWorld()->LineTraceSingleByObjectType(GroundHitResult, ViewLocation, End, Ground, Params);
	GroundActor = bGroundHit ? GroundHitResult.GetActor() : nullptr;
	GroundPoint = bGroundHit ? FVector(GroundHitResult.ImpactPoint) : End;
	GroundNormal = bGroundHit ? FVector(GroundHitResult.ImpactNormal) : FVector::UpVector;
}

bool AFGPlayerController::GetSelectedRow(FFGBuildableRow& OutRow, FName& OutName) const
{
	if (!Hotbar.IsValidIndex(SelectedSlot))
	{
		return false;
	}
	const FFGBuildableRow* Row = UFGGameData::FindBuildable(Hotbar[SelectedSlot]);
	if (!Row)
	{
		return false;
	}
	OutRow = *Row;
	OutName = Hotbar[SelectedSlot];
	return true;
}

void AFGPlayerController::RefreshHotbar()
{
	const int32 PhaseNumber = Tower ? Tower->GetPhaseNumber() : 1;
	TArray<FName> Rows;
	if (UDataTable* Table = UFGGameData::Buildables())
	{
		for (const FName& Name : Table->GetRowNames())
		{
			if (const FFGBuildableRow* Row = Table->FindRow<FFGBuildableRow>(Name, TEXT("FGHotbar"), false))
			{
				if (Row->Phase <= PhaseNumber)
				{
					Rows.Add(Name);
				}
			}
		}
	}
	HotbarAll = Rows;
	HotbarPage = FMath::Clamp(HotbarPage, 0, NumHotbarPages() - 1);

	TArray<FName> Page;
	for (int32 Index = HotbarPage * 10; Index < FMath::Min(HotbarAll.Num(), HotbarPage * 10 + 10); ++Index)
	{
		Page.Add(HotbarAll[Index]);
	}
	if (Page != Hotbar)
	{
		const FName Selected = Hotbar.IsValidIndex(SelectedSlot) ? Hotbar[SelectedSlot] : NAME_None;
		Hotbar = Page;
		SelectedSlot = Hotbar.IndexOfByKey(Selected);
	}
}

void AFGPlayerController::OnNextPage()
{
	HotbarPage = (HotbarPage + 1) % NumHotbarPages();
	ClearSelection();
	RefreshHotbar();
}

bool AFGPlayerController::GetWaterPoint(FVector& OutPoint) const
{
	FVector ViewLocation;
	FRotator ViewRotation;
	GetPlayerViewPoint(ViewLocation, ViewRotation);
	const FVector Dir = ViewRotation.Vector();
	if (Dir.Z > -0.02f || ViewLocation.Z <= 0.f)
	{
		return false;
	}
	const float Distance = -ViewLocation.Z / Dir.Z;
	if (Distance > BuildRange)
	{
		return false;
	}
	OutPoint = ViewLocation + Dir * Distance;
	OutPoint.Z = 0.f;
	return true;
}

void AFGPlayerController::UpdateGhost()
{
	FFGBuildableRow Row;
	FName Name;
	if (!GetSelectedRow(Row, Name) || Row.Kind == EFGBuildableKind::Belt)
	{
		if (Ghost)
		{
			Ghost->Destroy();
			Ghost = nullptr;
			GhostRow = NAME_None;
		}
		return;
	}

	if (!Ghost || GhostRow != Name)
	{
		if (Ghost)
		{
			Ghost->Destroy();
		}
		FActorSpawnParameters Spawn;
		Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		Ghost = GetWorld()->SpawnActor<AFGBuildable>(ClassForKind(Row.Kind), FTransform::Identity, Spawn);
		Ghost->InitFromRow(Name, Row, true);
		GhostRow = Name;
	}

	const FIntPoint Footprint = RotatedSize(Row.Size, GhostYaw);
	FVector Anchor = GroundPoint;

	// Extractors snap onto the nearest matching resource node (aiming at a rock sends the
	// ground ray past it, so without this the footprint lands behind the node).
	if (Row.Kind == EFGBuildableKind::Extractor)
	{
		const AFGResourceNode* Looked = Cast<AFGResourceNode>(LookActor.Get());
		const FVector Probe = Looked ? Looked->GetActorLocation() : GroundPoint;
		const AFGResourceNode* Best = nullptr;
		float BestDistance = 350.f;
		for (TActorIterator<AFGResourceNode> It(GetWorld()); It; ++It)
		{
			if (It->Item == Row.ExtractItem)
			{
				const float Distance = FVector::Dist2D(It->GetActorLocation(), Probe);
				if (Distance < BestDistance)
				{
					BestDistance = Distance;
					Best = *It;
				}
			}
		}
		if (Best)
		{
			Anchor.X = Best->GetActorLocation().X;
			Anchor.Y = Best->GetActorLocation().Y;
		}
	}

	// Platforms float on the sea: use where the view meets the water unless dry ground is in the way.
	bGhostOnWater = false;
	if (Row.Kind == EFGBuildableKind::Platform)
	{
		const bool bDryGround = bGroundHit && GroundActor.IsValid() && GroundActor->ActorHasTag(TEXT("Buildable"))
			&& !GroundActor->IsA<AFGPlatform>() && GroundPoint.Z > 5.f;
		FVector Water;
		if (!bDryGround && GetWaterPoint(Water))
		{
			Anchor = Water;
			bGhostOnWater = true;
		}
	}

	const FIntPoint Origin(
		FMath::FloorToInt(Anchor.X / AFGBuildable::CellSize) - Footprint.X / 2,
		FMath::FloorToInt(Anchor.Y / AFGBuildable::CellSize) - Footprint.Y / 2);
	const FVector Center(
		(Origin.X + Footprint.X * 0.5f) * AFGBuildable::CellSize,
		(Origin.Y + Footprint.Y * 0.5f) * AFGBuildable::CellSize,
		bGhostOnWater ? PlatformZ : GroundPoint.Z);
	Ghost->SetActorLocationAndRotation(Center, FRotator(0.f, GhostYaw, 0.f));
	Ghost->SetActorHiddenInGame(!bGroundHit && !bGhostOnWater);

	bGhostValid = CheckPlacement(Row, Origin, Footprint, bGhostOnWater, GhostProblem);
	Ghost->SetGhostValid(bGhostValid);
}

bool AFGPlayerController::CheckPlacement(const FFGBuildableRow& Row, FIntPoint Origin, FIntPoint Footprint, bool bOnWater, FString& OutProblem) const
{
	OutProblem.Reset();
	const bool bIsPlatform = Row.Kind == EFGBuildableKind::Platform;
	if (bIsPlatform)
	{
		if (!bOnWater)
		{
			OutProblem = TEXT("Platforms go on the water");
			return false;
		}
	}
	else
	{
		if (!bGroundHit || !GroundActor.IsValid() || !GroundActor->ActorHasTag(TEXT("Buildable")))
		{
			OutProblem = TEXT("Aim at the island sand or a platform");
			return false;
		}
		if (GroundNormal.Z < 0.8f)
		{
			OutProblem = TEXT("Too steep");
			return false;
		}
	}
	if (Row.bNeedsWater && !(GroundActor.IsValid() && GroundActor->IsA<AFGPlatform>()) && GroundPoint.Z > 70.f)
	{
		OutProblem = TEXT("Must be at the water's edge or on a platform");
		return false;
	}

	const float PlaceZ = bOnWater ? PlatformZ : GroundPoint.Z;
	for (TActorIterator<AFGBuildable> It(GetWorld()); It; ++It)
	{
		// Buildings sit on platforms, so platforms only clash with other platforms.
		if (It->bGhost || It->IsA<AFGPlatform>() != bIsPlatform)
		{
			continue;
		}
		if (FMath::Abs(It->GetActorLocation().Z - PlaceZ) < 400.f
			&& RectsOverlap(Origin, Footprint, It->GetGridOrigin(), It->GetFootprint()))
		{
			OutProblem = FString::Printf(TEXT("Blocked by %s"), *It->GetDisplayName().ToString());
			return false;
		}
	}
	// Sea pumps draw from the sea and lightning rods from the sky: neither needs a node.
	if (Row.Kind == EFGBuildableKind::Extractor && !Row.bNeedsWater && !Row.bNoNode)
	{
		bool bOnNode = false;
		for (TActorIterator<AFGResourceNode> It(GetWorld()); It; ++It)
		{
			if (It->Item != Row.ExtractItem)
			{
				continue;
			}
			const FVector NodeLocation = It->GetActorLocation();
			const int32 CellX = FMath::FloorToInt(NodeLocation.X / AFGBuildable::CellSize);
			const int32 CellY = FMath::FloorToInt(NodeLocation.Y / AFGBuildable::CellSize);
			if (CellX >= Origin.X && CellX < Origin.X + Footprint.X && CellY >= Origin.Y && CellY < Origin.Y + Footprint.Y)
			{
				bOnNode = true;
				break;
			}
		}
		if (!bOnNode)
		{
			OutProblem = FString::Printf(TEXT("Must sit on a %s node"), *UFGGameData::ItemName(Row.ExtractItem).ToString());
			return false;
		}
	}
	if (!HasItems(Row.Cost))
	{
		OutProblem = TEXT("Need ") + MissingItemsText(Row.Cost);
		return false;
	}
	return true;
}

void AFGPlayerController::SelectSlot(int32 Index)
{
	if (!Hotbar.IsValidIndex(Index))
	{
		return;
	}
	if (SelectedSlot == Index)
	{
		ClearSelection();
		return;
	}
	SelectedSlot = Index;
	BeltStart = nullptr;

	FFGBuildableRow Row;
	FName Name;
	if (GetSelectedRow(Row, Name) && Row.Kind == EFGBuildableKind::Belt)
	{
		Hint(TEXT("BeltHowTo"), LOCTEXT("HintBelt", "Belts: click a machine's orange output, then another machine's blue input. Longer belts cost more."));
	}
}

void AFGPlayerController::ClearSelection()
{
	SelectedSlot = INDEX_NONE;
	BeltStart = nullptr;
}

void AFGPlayerController::PlaceGhost()
{
	FFGBuildableRow Row;
	FName Name;
	if (!Ghost || !GetSelectedRow(Row, Name))
	{
		return;
	}
	if (!bGhostValid)
	{
		ShowToast(GhostProblem);
		return;
	}
	RemoveItems(Row.Cost);
	FActorSpawnParameters Spawn;
	Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AFGBuildable* Built = GetWorld()->SpawnActor<AFGBuildable>(ClassForKind(Row.Kind), Ghost->GetActorTransform(), Spawn);
	Built->InitFromRow(Name, Row, false);
	ShowToast(FString::Printf(TEXT("Built %s"), *Row.DisplayName.ToString()));

	switch (Row.Kind)
	{
	case EFGBuildableKind::Generator:
		Hint(TEXT("FirstPower"), LOCTEXT("HintPower", "Power! Machines share it. Next, a Salvage Crane on the scrap pile would save your hands."));
		break;
	case EFGBuildableKind::Extractor:
		Hint(TEXT("FirstExtractor"), LOCTEXT("HintExtractor", "Machines stop when they're full. Grab the output with E, or run a belt to the next machine."));
		break;
	case EFGBuildableKind::Translator:
		Hint(TEXT("FirstTranslator"), LOCTEXT("HintTranslatorBuilt", "The Translator is listening. Now build a Trade Buoy at the water's edge so they have somewhere to talk to us."));
		break;
	case EFGBuildableKind::TradeBuoy:
		Hint(TEXT("FirstBuoy"), LOCTEXT("HintBuoy", "A Glimmer is already circling it. Walk up and press E."));
		break;
	case EFGBuildableKind::Platform:
		Hint(TEXT("FirstPlatform"), LOCTEXT("HintPlatform", "It floats. Machines can stand on platforms, and you can build your way across the water."));
		break;
	default:
		if (Row.MachineType == TEXT("Smelter"))
		{
			Hint(TEXT("FirstSmelter"), LOCTEXT("HintSmelter", "The Smelter turns Scrap Metal into Steel Bars and Coral Ore into Coral Ingots. Feed it with E or a belt."));
		}
		break;
	}
}

void AFGPlayerController::ClickBelt(AFGBuildable* Clicked)
{
	FFGBuildableRow Row;
	FName Name;
	if (!GetSelectedRow(Row, Name))
	{
		return;
	}

	AFGBuildable* Start = BeltStart.Get();
	if (!Start)
	{
		if (!Clicked || !Clicked->HasOutputPort())
		{
			ShowToast(TEXT("Click something with an orange output first"));
			return;
		}
		BeltStart = Clicked;
		ShowToast(FString::Printf(TEXT("Belt from %s: now click where it goes"), *Clicked->GetDisplayName().ToString()));
		return;
	}

	if (!Clicked || Clicked == Start || !Clicked->HasInputPort())
	{
		ShowToast(TEXT("Click a machine with a blue input (or the Signal Tower)"));
		return;
	}
	for (TActorIterator<AFGBelt> It(GetWorld()); It; ++It)
	{
		if (It->Source.Get() == Start && It->Target.Get() == Clicked)
		{
			ShowToast(TEXT("Those two are already connected"));
			return;
		}
	}

	const FVector From = Start->GetOutputPortLocation();
	const float Length = FVector::Dist(From, Clicked->GetInputPortLocationFor(From));
	if (Length > AFGBelt::MaxLength)
	{
		ShowToast(FString::Printf(TEXT("Too long (%.0f m, max %.0f m)"), Length / 100.f, AFGBelt::MaxLength / 100.f));
		return;
	}
	const int32 Segments = AFGBelt::SegmentsFor(Length);
	if (!HasItems(Row.Cost, Segments))
	{
		ShowToast(TEXT("Need ") + MissingItemsText(Row.Cost, Segments));
		return;
	}

	RemoveItems(Row.Cost, Segments);
	FActorSpawnParameters Spawn;
	Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AFGBelt* Belt = GetWorld()->SpawnActor<AFGBelt>(AFGBelt::StaticClass(), FTransform::Identity, Spawn);
	Belt->Setup(Start, Clicked, Row.Cost);
	BeltStart = nullptr;
	ShowToast(FString::Printf(TEXT("Belt built (%.0f m)"), Length / 100.f));
}

void AFGPlayerController::DestroyBeltsOf(AFGBuildable* Buildable)
{
	TArray<AFGBelt*> ToRemove;
	for (TActorIterator<AFGBelt> It(GetWorld()); It; ++It)
	{
		if (It->Source.Get() == Buildable || It->Target.Get() == Buildable)
		{
			ToRemove.Add(*It);
		}
	}
	for (AFGBelt* Belt : ToRemove)
	{
		TArray<FFGItemStack> Refund;
		Belt->GetRefund(Refund);
		AddItems(Refund);
		Belt->Destroy();
	}
}

// ================================================================ Input

void AFGPlayerController::OnInteract()
{
	if (bPuzzleOpen || bPuzzleWaiting)
	{
		return;
	}
	if (bLineActive && CurrentLine.Style != EFGLineStyle::Puzzle)
	{
		bLineActive = false; // skip the current line
		return;
	}
	if (!bLookHit || LookDistance > InteractRange)
	{
		return;
	}
	if (AFGResourceNode* Node = Cast<AFGResourceNode>(LookActor.Get()))
	{
		Gather(Node);
	}
	else if (AFGBelt* Belt = Cast<AFGBelt>(LookActor.Get()); Belt && Belt->bBroken)
	{
		if (CountItem(TEXT("SteelBar")) < 1)
		{
			ShowToast(TEXT("Repairing a belt needs 1 Steel Bar"));
			return;
		}
		AddItem(TEXT("SteelBar"), -1);
		Belt->SetBroken(false);
		ShowToast(TEXT("Belt repaired"));
	}
	else if (AFGTradeBuoy* Buoy = Cast<AFGTradeBuoy>(LookActor.Get()); Buoy && Buoy->State == EFGTradeState::Waiting && Buoy->TotalOutput() == 0)
	{
		TalkToBuoy(Buoy);
	}
	else if (AFGBuildable* Buildable = Cast<AFGBuildable>(LookActor.Get()))
	{
		Exchange(Buildable);
	}
}

void AFGPlayerController::TalkToBuoy(AFGTradeBuoy* Buoy)
{
	if (!AFGTranslator::FindWorking(GetWorld()))
	{
		ShowToast(TEXT("You can't understand the Glimmer. Build a powered Translator first."));
		Hint(TEXT("NeedTranslator"), LOCTEXT("HintTranslator", "They're talking, but it's just light and music to us. We need a Translator, and power for it."));
		return;
	}
	UGameInstance* GameInstance = GetGameInstance();
	UFGFishApiSubsystem* Api = GameInstance ? GameInstance->GetSubsystem<UFGFishApiSubsystem>() : nullptr;
	if (!Api || bPuzzleWaiting || bPuzzleOpen)
	{
		return;
	}
	PuzzleBuoy = Buoy;
	PuzzleKind = EPuzzleKind::TradeFish;
	Api->OnPuzzleReady.AddUniqueDynamic(this, &AFGPlayerController::HandlePuzzleReady);
	bPuzzleWaiting = true;
	Api->RequestPuzzle();
	Hint(TEXT("FirstTrade"), LOCTEXT("HintTrade", "It's showing us a picture. The fish are how many crates they want, the chests are what they'll give. Count carefully."));
}

void AFGPlayerController::OnInteractRepeat()
{
	if (bLookHit && LookDistance <= InteractRange)
	{
		if (AFGResourceNode* Node = Cast<AFGResourceNode>(LookActor.Get()))
		{
			Gather(Node);
		}
	}
}

void AFGPlayerController::OnPrimary()
{
	FFGBuildableRow Row;
	FName Name;
	if (!GetSelectedRow(Row, Name))
	{
		return;
	}
	if (Row.Kind == EFGBuildableKind::Belt)
	{
		ClickBelt(Cast<AFGBuildable>(LookActor.Get()));
	}
	else
	{
		PlaceGhost();
	}
}

void AFGPlayerController::OnCancel()
{
	if (BeltStart.IsValid())
	{
		BeltStart = nullptr;
		return;
	}
	ClearSelection();
}

void AFGPlayerController::OnRotate()
{
	GhostYaw = (GhostYaw + 90) % 360;
}

void AFGPlayerController::OnDismantle()
{
	if (!bLookHit || LookDistance > InteractRange * 1.5f)
	{
		return;
	}
	if (AFGBelt* Belt = Cast<AFGBelt>(LookActor.Get()))
	{
		TArray<FFGItemStack> Refund;
		Belt->GetRefund(Refund);
		AddItems(Refund);
		Belt->Destroy();
		ShowToast(TEXT("Belt removed"));
		return;
	}
	AFGBuildable* Buildable = Cast<AFGBuildable>(LookActor.Get());
	if (!Buildable || Buildable->bGhost || !Buildable->CanDismantle())
	{
		return;
	}
	if (Buildable->IsA<AFGPlatform>())
	{
		for (TActorIterator<AFGBuildable> It(GetWorld()); It; ++It)
		{
			if (!It->bGhost && !It->IsA<AFGPlatform>()
				&& RectsOverlap(Buildable->GetGridOrigin(), Buildable->GetFootprint(), It->GetGridOrigin(), It->GetFootprint())
				&& FMath::Abs(It->GetActorLocation().Z - Buildable->GetActorLocation().Z) < 400.f)
			{
				ShowToast(TEXT("Clear the platform first"));
				return;
			}
		}
	}
	DestroyBeltsOf(Buildable);
	TArray<FFGItemStack> Refund;
	Buildable->GetRefund(Refund);
	AddItems(Refund);
	ShowToast(FString::Printf(TEXT("Dismantled %s"), *Buildable->GetDisplayName().ToString()));
	Buildable->Destroy();
}

void AFGPlayerController::OnNumber(int32 Index)
{
	if (bPuzzleOpen)
	{
		if (PuzzleOptions.IsValidIndex(Index))
		{
			AnswerPuzzle(Index);
		}
		return;
	}
	SelectSlot(Index);
}

// ================================================================ Interaction

void AFGPlayerController::Gather(AFGResourceNode* Node)
{
	if (GatherCooldown > 0.f || !Node)
	{
		return;
	}
	GatherCooldown = 0.22f;
	AddItem(Node->Item, 1);
	ShowToast(FString::Printf(TEXT("+1 %s  (%d)"), *UFGGameData::ItemName(Node->Item).ToString(), CountItem(Node->Item)));
}

void AFGPlayerController::Exchange(AFGBuildable* Buildable)
{
	if (!Buildable || Buildable->bGhost)
	{
		return;
	}

	TMap<FName, int32> Took;
	FName Item;
	while (Buildable->TakeOutputFor(nullptr, Item))
	{
		AddItem(Item, 1);
		Took.FindOrAdd(Item)++;
	}

	TMap<FName, int32> Gave;
	if (Buildable->PlayerCanDeposit())
	{
		TArray<FName> Held;
		Inventory.GetKeys(Held);
		for (const FName& HeldItem : Held)
		{
			while (CountItem(HeldItem) > 0 && Buildable->TryInsert(HeldItem))
			{
				AddItem(HeldItem, -1);
				Gave.FindOrAdd(HeldItem)++;
			}
		}
	}

	TArray<FString> Parts;
	if (Took.Num())
	{
		Parts.Add(TEXT("Took ") + AFGBuildable::BufferToString(Took));
	}
	if (Gave.Num())
	{
		Parts.Add(TEXT("Gave ") + AFGBuildable::BufferToString(Gave));
	}
	ShowToast(Parts.Num() ? FString::Join(Parts, TEXT("  ·  ")) : TEXT("Nothing to exchange"));
}

// ================================================================ Story

void AFGPlayerController::QueueLine(const FText& Speaker, const FText& Text, float Duration, EFGLineStyle Style)
{
	FFGStoryLine Line;
	Line.Speaker = Speaker;
	Line.Text = Text;
	Line.Duration = Duration;
	Line.Style = Style;
	LineQueue.Add(Line);
}

void AFGPlayerController::QueueLines(const TArray<FFGStoryLine>& Lines, EFGLineStyle ForceStyle)
{
	for (FFGStoryLine Line : Lines)
	{
		if (ForceStyle != EFGLineStyle::Normal && Line.Style == EFGLineStyle::Normal)
		{
			Line.Style = ForceStyle;
		}
		if (Line.Duration <= 0.f)
		{
			Line.Duration = FMath::Clamp(Line.Text.ToString().Len() * 0.065f, 2.5f, 8.f);
		}
		LineQueue.Add(Line);
	}
}

void AFGPlayerController::ShowToast(const FString& Message)
{
	Toast = Message;
	ToastTime = 2.8f;
}

bool AFGPlayerController::IsInFlashback() const
{
	return bLineActive && (CurrentLine.Style == EFGLineStyle::Flashback
		|| (CurrentLine.Style == EFGLineStyle::Title && CurrentLine.Speaker.EqualTo(FlashbackMarker)));
}

void AFGPlayerController::UpdateStory(float DeltaTime)
{
	if (!bLineActive && LineQueue.Num() > 0)
	{
		CurrentLine = LineQueue[0];
		LineQueue.RemoveAt(0);
		bLineActive = true;
		LineTime = 0.f;
		if (CurrentLine.Style == EFGLineStyle::Puzzle)
		{
			StartPuzzle();
		}
	}

	if (!bLineActive)
	{
		return;
	}
	if (CurrentLine.Style == EFGLineStyle::Puzzle)
	{
		if (!bPuzzleWaiting && !bPuzzleOpen)
		{
			bLineActive = false;
		}
		return;
	}
	LineTime += DeltaTime;
	if (LineTime >= CurrentLine.Duration)
	{
		bLineActive = false;
	}
}

void AFGPlayerController::UpdateHints()
{
	if (Tower && Tower->CurrentPhase == 0 && CountItem(TEXT("ScrapMetal")) >= 8)
	{
		Hint(TEXT("EnoughForSolar"), LOCTEXT("HintSolar", "That's enough scrap for a Solar Panel. Press 1, aim at the sand and Left Click. R rotates."));
	}

	float Supply, Demand;
	AFGBuildable::GetPowerTotals(GetWorld(), Supply, Demand);
	LowPowerTime = (Demand > Supply + 0.01f) ? LowPowerTime + GetWorld()->GetDeltaSeconds() : 0.f;
	if (LowPowerTime > 3.f)
	{
		Hint(TEXT("LowPower"), LOCTEXT("HintLowPower", "We're using more power than the panels make, so everything slows down. Build another Solar Panel."));
	}

	if (const AFGWeather* Weather = AFGWeather::Get(GetWorld()))
	{
		if (Weather->StormCount > LastStormCount)
		{
			LastStormCount = Weather->StormCount;
			ShowToast(TEXT("STORM"));
			Hint(TEXT("FirstStorm"), LOCTEXT("HintStorm", "Storm front! Solar drops to almost nothing in this, and belts without a Breakwater nearby can snap. Lightning Rods love it, though."));
		}
	}
	if (Tower && Tower->OceanHealth < 0.8f)
	{
		Hint(TEXT("Murk"), LOCTEXT("HintMurk", "Look at the water near the burners. It's going dark. And the Glimmers... they're dimmer than they were."));
	}
}

void AFGPlayerController::Hint(FName Key, const FText& Text)
{
	if (!HintsShown.Contains(Key))
	{
		HintsShown.Add(Key);
		QueueLine(Echo, Text, FMath::Clamp(Text.ToString().Len() * 0.06f, 3.5f, 8.f));
	}
}

void AFGPlayerController::HandlePhaseStarted(int32 PhaseIndex)
{
	FFGPhaseRow Phase;
	if (!Tower || !Tower->GetPhase(PhaseIndex, Phase))
	{
		return;
	}
	QueueLine(FText::GetEmpty(), FText::Format(LOCTEXT("PhaseCard", "PHASE {0}\n{1}"), FText::AsNumber(PhaseIndex + 1), Phase.Title), 3.5f, EFGLineStyle::Title);
	QueueLines(Phase.Intro);
	RefreshHotbar();
}

void AFGPlayerController::HandlePhaseCompleted(int32 PhaseIndex)
{
	FFGPhaseRow Phase;
	if (!Tower || !Tower->GetPhase(PhaseIndex, Phase))
	{
		return;
	}
	QueueLine(Echo, LOCTEXT("Sending", "Tower section complete. Sending your message home..."), 3.5f);
	QueueLines(Phase.MessageHome);
	if (Phase.Flashback.Num() > 0)
	{
		QueueLine(FlashbackMarker, Phase.FlashbackTitle, 4.f, EFGLineStyle::Title);
		QueueLines(Phase.Flashback, EFGLineStyle::Flashback);
	}
	if (Phase.Reply.Num() > 0)
	{
		QueueLine(Echo, LOCTEXT("Incoming", "Incoming reply. It's her."), 3.f);
		QueueLines(Phase.Reply);
	}
	if (Phase.bReplyHasDrawing)
	{
		QueueLine(Neela, FText::GetEmpty(), 0.f, EFGLineStyle::Puzzle);
	}
}

void AFGPlayerController::StartPuzzle()
{
	UGameInstance* GameInstance = GetGameInstance();
	UFGFishApiSubsystem* Api = GameInstance ? GameInstance->GetSubsystem<UFGFishApiSubsystem>() : nullptr;
	if (!Api)
	{
		return;
	}
	Api->OnPuzzleReady.AddUniqueDynamic(this, &AFGPlayerController::HandlePuzzleReady);
	bPuzzleWaiting = true;
	PuzzleKind = EPuzzleKind::Drawing;

	// After the Phase 4 message the relay is secretly dead: Echo re-sends old drawings.
	const bool bRelayBroken = Tower && Tower->CurrentPhase >= 4;
	if (bRelayBroken)
	{
		Api->RequestRepeatPuzzle();
	}
	else
	{
		Api->RequestPuzzle();
	}
}

void AFGPlayerController::HandlePuzzleReady(UTexture2D* Picture, int32 Fish, int32 Chests)
{
	if (!bPuzzleWaiting)
	{
		return;
	}
	bPuzzleWaiting = false;
	if (!Picture && PuzzleKind != EPuzzleKind::Drawing)
	{
		ShowToast(TEXT("The Glimmer's picture didn't come through. Try again."));
		return;
	}
	if (!Picture)
	{
		FFGStoryLine Line;
		Line.Speaker = Echo;
		Line.Text = LOCTEXT("NoDrawing", "Her drawing didn't make it through the noise. Next time.");
		LineQueue.Insert(Line, 0);
		return;
	}

	PuzzlePicture = Picture;
	PuzzleFish = Fish;
	PuzzleChests = Chests;
	BuildPuzzleOptions(Fish);
	bPuzzleOpen = true;
}

void AFGPlayerController::BuildPuzzleOptions(int32 Answer)
{
	PuzzleAnswer = Answer;
	TArray<int32> Candidates;
	for (int32 Offset = -3; Offset <= 3; ++Offset)
	{
		const int32 Value = Answer + Offset;
		if (Offset != 0 && Value >= 0)
		{
			Candidates.Add(Value);
		}
	}
	PuzzleOptions = { Answer };
	while (PuzzleOptions.Num() < 4 && Candidates.Num() > 0)
	{
		PuzzleOptions.Add(Candidates[FMath::RandRange(0, Candidates.Num() - 1)]);
		Candidates.Remove(PuzzleOptions.Last());
	}
	for (int32 Index = PuzzleOptions.Num() - 1; Index > 0; --Index)
	{
		PuzzleOptions.Swap(Index, FMath::RandRange(0, Index));
	}
}

void AFGPlayerController::AnswerPuzzle(int32 Option)
{
	const int32 Chosen = PuzzleOptions[Option];

	// Glimmer trades: fish first, then chests; one wrong count and the Glimmer swims off.
	if (PuzzleKind != EPuzzleKind::Drawing)
	{
		AFGTradeBuoy* Buoy = PuzzleBuoy.Get();
		if (Chosen != PuzzleAnswer || !Buoy)
		{
			bPuzzleOpen = false;
			if (Buoy)
			{
				Buoy->Misunderstood();
			}
			ShowToast(TEXT("Wrong count. The Glimmer flickers, confused, and swims away."));
			return;
		}
		if (PuzzleKind == EPuzzleKind::TradeFish)
		{
			PuzzleKind = EPuzzleKind::TradeChests;
			BuildPuzzleOptions(PuzzleChests);
			return;
		}
		bPuzzleOpen = false;
		Buoy->StartTrade(PuzzleFish, PuzzleChests, Tower ? Tower->GetPhaseNumber() : 1);
		QueueLine(LOCTEXT("Glimmer", "Glimmer (translated)"), FText::Format(
			LOCTEXT("TradeOffer", "\"Bring {0} {1}. We give {2} pearl(s). We wait here.\""),
			FText::AsNumber(Buoy->WantCount), UFGGameData::ItemName(Buoy->WantItem), FText::AsNumber(Buoy->RewardPearls)), 5.f);
		return;
	}

	bPuzzleOpen = false;
	FFGStoryLine Line;
	Line.Speaker = Neela;
	Line.Duration = 4.5f;
	if (Chosen == PuzzleAnswer)
	{
		PuzzlesSolved++;
		Line.Text = FText::Format(LOCTEXT("PuzzleRight", "Yes! {0}! You counted right, Mum. You were really looking."), FText::AsNumber(PuzzleAnswer));
	}
	else
	{
		Line.Text = FText::Format(LOCTEXT("PuzzleWrong", "Wrong! It's {0}! You're not even looking!"), FText::AsNumber(PuzzleAnswer));
	}
	LineQueue.Insert(Line, 0);
}

// ================================================================ Cheats

void AFGPlayerController::FGCompletePhase()
{
	if (Tower)
	{
		Tower->CheatCompletePhase();
	}
}

void AFGPlayerController::FGGive(FName Item, int32 Count)
{
	AddItem(Item, Count);
}

void AFGPlayerController::FGSkipStory()
{
	LineQueue.Reset();
	bLineActive = false;
}

void AFGPlayerController::FGSelect(int32 Slot)
{
	// During a picture question, 100 + N answers with the value N.
	if (bPuzzleOpen && Slot >= 100)
	{
		const int32 Index = PuzzleOptions.IndexOfByKey(Slot - 100);
		AnswerPuzzle(Index != INDEX_NONE ? Index : 0);
		return;
	}
	// Slots past 10 live on later hotbar pages.
	if (!bPuzzleOpen && Slot > 10)
	{
		HotbarPage = (Slot - 1) / 10;
		RefreshHotbar();
		ClearSelection();
		OnNumber((Slot - 1) % 10);
		return;
	}
	OnNumber(Slot - 1);
}

void AFGPlayerController::FGClick()
{
	UpdateLook();
	UpdateGhost();
	OnPrimary();
}

void AFGPlayerController::FGInteract()
{
	UpdateLook();
	bLineActive = false; // don't let a subtitle swallow the test press
	OnInteract();
}

void AFGPlayerController::FGLook(float Pitch, float Yaw)
{
	SetControlRotation(FRotator(Pitch, Yaw, 0.f));
}

void AFGPlayerController::FGTeleport(float X, float Y, float Z)
{
	if (APawn* MyPawn = GetPawn())
	{
		MyPawn->TeleportTo(FVector(X, Y, Z + 100.f), MyPawn->GetActorRotation());
	}
}

#undef LOCTEXT_NAMESPACE
