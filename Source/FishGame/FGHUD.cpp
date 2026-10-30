#include "FGHUD.h"

#include "FGBelt.h"
#include "FGBuildable.h"
#include "FGGameData.h"
#include "FGPlayerController.h"
#include "FGResourceNode.h"
#include "FGTowerSite.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "Engine/Texture2D.h"

namespace
{
	const FLinearColor Cyan(0.35f, 0.85f, 1.f);
	const FLinearColor Warm(1.f, 0.82f, 0.45f);
	const FLinearColor Soft(0.82f, 0.88f, 0.92f);
	const FLinearColor Dim(0.55f, 0.62f, 0.68f);
	const FLinearColor Good(0.4f, 1.f, 0.55f);
	const FLinearColor Bad(1.f, 0.38f, 0.32f);

	FLinearColor SpeakerColor(const FString& Speaker)
	{
		if (Speaker == TEXT("Echo")) return Cyan;
		if (Speaker == TEXT("Neela")) return Warm;
		if (Speaker == TEXT("Ishani")) return FLinearColor::White;
		if (Speaker == TEXT("Ravi")) return FLinearColor(0.6f, 0.95f, 0.8f);
		return Soft;
	}
}

void AFGHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas)
	{
		return;
	}
	S = FMath::Max(Canvas->ClipY / 1080.f, 0.6f);

	AFGPlayerController* PC = Cast<AFGPlayerController>(GetOwningPlayerController());
	if (!PC)
	{
		return;
	}

	if (PC->IsInFlashback())
	{
		DrawStory(PC); // flashbacks take the whole screen
		return;
	}

	DrawCrosshair();
	DrawPhasePanel(PC);
	DrawPowerAndInventory(PC);
	DrawHotbar(PC);
	DrawLookInfo(PC);
	DrawToast(PC);
	DrawStory(PC);
	DrawPuzzle(PC);
}

// ---------------------------------------------------------------- helpers

void AFGHUD::DrawPanel(float X, float Y, float W, float H, const FLinearColor& Color)
{
	DrawRect(Color, X, Y, W, H);
}

float AFGHUD::TextWidth(const FString& Text, UFont* Font, float Scale)
{
	float W = 0.f, H = 0.f;
	GetTextSize(Text, W, H, Font, Scale);
	return W;
}

float AFGHUD::DrawWrapped(const FString& Text, float X, float Y, float MaxWidth, UFont* Font, float Scale, const FLinearColor& Color, bool bCentered)
{
	const float LineHeight = Font->GetMaxCharHeight() * Scale * 1.15f;
	TArray<FString> Paragraphs;
	Text.ParseIntoArray(Paragraphs, TEXT("\n"), false);
	for (const FString& Paragraph : Paragraphs)
	{
		TArray<FString> Words;
		Paragraph.ParseIntoArrayWS(Words);
		FString Line;
		auto Flush = [&]()
		{
			const float LineX = bCentered ? X - TextWidth(Line, Font, Scale) * 0.5f : X;
			DrawText(Line, Color, LineX, Y, Font, Scale);
			Y += LineHeight;
			Line.Reset();
		};
		for (const FString& Word : Words)
		{
			const FString Candidate = Line.IsEmpty() ? Word : Line + TEXT(" ") + Word;
			if (!Line.IsEmpty() && TextWidth(Candidate, Font, Scale) > MaxWidth)
			{
				Flush();
				Line = Word;
			}
			else
			{
				Line = Candidate;
			}
		}
		Flush();
	}
	return Y;
}

// ---------------------------------------------------------------- sections

void AFGHUD::DrawCrosshair()
{
	const float CX = Canvas->ClipX * 0.5f;
	const float CY = Canvas->ClipY * 0.5f;
	DrawRect(FLinearColor(1.f, 1.f, 1.f, 0.85f), CX - 2.f * S, CY - 2.f * S, 4.f * S, 4.f * S);
}

void AFGHUD::DrawPhasePanel(AFGPlayerController* PC)
{
	AFGTowerSite* Tower = PC->Tower;
	if (!Tower)
	{
		return;
	}
	UFont* Big = GEngine->GetMediumFont();
	UFont* Small = GEngine->GetSmallFont();
	const float X = 24.f * S;
	float Y = 24.f * S;
	const float W = 380.f * S;

	FFGPhaseRow Phase;
	if (!Tower->GetPhase(Tower->CurrentPhase, Phase))
	{
		DrawPanel(X, Y, W, 44.f * S);
		DrawText(TEXT("The Signal Tower is complete."), Cyan, X + 12.f * S, Y + 10.f * S, Big, S);
		return;
	}

	const float H = (70.f + Phase.Requirements.Num() * 34.f) * S;
	DrawPanel(X, Y, W, H);
	DrawText(FString::Printf(TEXT("PHASE %d  ·  %s"), Tower->GetPhaseNumber(), *Phase.Title.ToString()), Cyan, X + 12.f * S, Y + 10.f * S, Big, S);
	DrawText(FString::Printf(TEXT("Signal Tower: %s"), *Phase.TowerPart.ToString()), Dim, X + 12.f * S, Y + 36.f * S, Small, S * 1.3f);
	Y += 62.f * S;
	for (const FFGItemStack& Need : Phase.Requirements)
	{
		const int32 Have = Tower->GetDelivered(Need.Item);
		const float Ratio = Need.Count > 0 ? FMath::Clamp(float(Have) / Need.Count, 0.f, 1.f) : 1.f;
		DrawText(FString::Printf(TEXT("%s  %d / %d"), *UFGGameData::ItemName(Need.Item).ToString(), Have, Need.Count),
			Ratio >= 1.f ? Good : Soft, X + 12.f * S, Y, Small, S * 1.3f);
		const float BarY = Y + 18.f * S;
		DrawRect(FLinearColor(1.f, 1.f, 1.f, 0.12f), X + 12.f * S, BarY, W - 24.f * S, 6.f * S);
		DrawRect(UFGGameData::ItemColor(Need.Item), X + 12.f * S, BarY, (W - 24.f * S) * Ratio, 6.f * S);
		Y += 34.f * S;
	}
}

void AFGHUD::DrawPowerAndInventory(AFGPlayerController* PC)
{
	UFont* Big = GEngine->GetMediumFont();
	UFont* Small = GEngine->GetSmallFont();
	const float W = 280.f * S;
	const float X = Canvas->ClipX - W - 24.f * S;
	float Y = 24.f * S;

	float Supply, Demand;
	AFGBuildable::GetPowerTotals(GetWorld(), Supply, Demand);
	DrawPanel(X, Y, W, 40.f * S);
	DrawText(FString::Printf(TEXT("POWER  %.0f / %.0f"), Demand, Supply), Demand > Supply + 0.01f ? Bad : Good, X + 12.f * S, Y + 9.f * S, Big, S);
	Y += 48.f * S;

	TArray<FName> Items;
	PC->Inventory.GetKeys(Items);
	Items.Sort([](const FName& A, const FName& B) { return A.LexicalLess(B); });
	const float H = (36.f + FMath::Max(Items.Num(), 1) * 22.f) * S;
	DrawPanel(X, Y, W, H);
	DrawText(TEXT("INVENTORY"), Dim, X + 12.f * S, Y + 8.f * S, Small, S * 1.3f);
	Y += 32.f * S;
	if (Items.Num() == 0)
	{
		DrawText(TEXT("empty: gather with E"), Dim, X + 12.f * S, Y, Small, S * 1.3f);
	}
	for (const FName& Item : Items)
	{
		DrawRect(UFGGameData::ItemColor(Item), X + 12.f * S, Y + 4.f * S, 10.f * S, 10.f * S);
		DrawText(FString::Printf(TEXT("%s  %d"), *UFGGameData::ItemName(Item).ToString(), PC->CountItem(Item)), Soft, X + 30.f * S, Y, Small, S * 1.3f);
		Y += 22.f * S;
	}
}

void AFGHUD::DrawHotbar(AFGPlayerController* PC)
{
	UFont* Small = GEngine->GetSmallFont();
	const int32 Count = PC->Hotbar.Num();
	if (Count == 0)
	{
		return;
	}
	const float SlotW = 150.f * S;
	const float SlotH = 64.f * S;
	const float Gap = 6.f * S;
	const float Total = Count * SlotW + (Count - 1) * Gap;
	float X = (Canvas->ClipX - Total) * 0.5f;
	const float Y = Canvas->ClipY - SlotH - 20.f * S;

	for (int32 Index = 0; Index < Count; ++Index)
	{
		const FFGBuildableRow* Row = UFGGameData::FindBuildable(PC->Hotbar[Index]);
		if (!Row)
		{
			continue;
		}
		const bool bSelected = Index == PC->SelectedSlot;
		const bool bAffordable = PC->HasItems(Row->Cost);
		DrawPanel(X, Y, SlotW, SlotH, bSelected ? FLinearColor(0.05f, 0.35f, 0.45f, 0.85f) : FLinearColor(0.f, 0.02f, 0.04f, 0.6f));
		if (bSelected)
		{
			DrawRect(Cyan, X, Y, SlotW, 3.f * S);
		}
		DrawText(FString::Printf(TEXT("%d"), (Index + 1) % 10), Dim, X + 8.f * S, Y + 6.f * S, Small, S * 1.2f);
		DrawText(Row->DisplayName.ToString(), bAffordable ? FLinearColor::White : Dim, X + 24.f * S, Y + 6.f * S, Small, S * 1.3f);
		FString Cost = UFGGameData::StacksToString(Row->Cost);
		if (Row->Kind == EFGBuildableKind::Belt)
		{
			Cost += TEXT(" / 2 m");
		}
		DrawWrapped(Cost, X + 8.f * S, Y + 28.f * S, SlotW - 14.f * S, Small, S * 1.05f, bAffordable ? Soft : Bad);
		X += SlotW + Gap;
	}

	FString Help = TEXT("1-9 build  ·  E gather / exchange  ·  X dismantle");
	FFGBuildableRow Row;
	FName Name;
	if (PC->GetSelectedRow(Row, Name))
	{
		Help = Row.Kind == EFGBuildableKind::Belt
			? TEXT("Belt: click an orange OUTPUT, then a blue INPUT  ·  RMB cancel")
			: TEXT("LMB place  ·  R rotate  ·  RMB cancel");
		if (!Row.Description.IsEmpty())
		{
			DrawWrapped(Row.Description.ToString(), Canvas->ClipX * 0.5f, Y - 58.f * S, 700.f * S, Small, S * 1.25f, Dim, true);
		}
	}
	DrawWrapped(Help, Canvas->ClipX * 0.5f, Y - 28.f * S, 900.f * S, Small, S * 1.25f, Soft, true);
}

void AFGHUD::DrawLookInfo(AFGPlayerController* PC)
{
	UFont* Big = GEngine->GetMediumFont();
	UFont* Small = GEngine->GetSmallFont();
	const float CX = Canvas->ClipX * 0.5f;
	float Y = Canvas->ClipY * 0.5f + 28.f * S;

	// Build feedback first.
	FFGBuildableRow Row;
	FName Name;
	if (PC->GetSelectedRow(Row, Name))
	{
		if (Row.Kind == EFGBuildableKind::Belt)
		{
			const FString Text = PC->BeltStart.IsValid()
				? FString::Printf(TEXT("Belt from %s: click a blue INPUT"), *PC->BeltStart->GetDisplayName().ToString())
				: TEXT("Click an orange OUTPUT to start a belt");
			DrawWrapped(Text, CX, Y, 700.f * S, Small, S * 1.35f, Cyan, true);
		}
		else if (!PC->bGhostValid && !PC->GhostProblem.IsEmpty())
		{
			DrawWrapped(PC->GhostProblem, CX, Y, 700.f * S, Small, S * 1.35f, Bad, true);
		}
		return;
	}

	AActor* Actor = PC->LookActor.Get();
	if (!Actor || PC->LookDistance > AFGPlayerController::InteractRange * 1.5f)
	{
		return;
	}

	FString Title;
	FString Body;
	FString Keys;
	if (const AFGBuildable* Buildable = Cast<AFGBuildable>(Actor))
	{
		Title = Buildable->GetDisplayName().ToString();
		Body = Buildable->GetStatusText();
		Keys = Buildable->CanDismantle() ? TEXT("[E] take output / put inputs   [X] dismantle") : TEXT("[E] hand in items");
	}
	else if (const AFGResourceNode* Node = Cast<AFGResourceNode>(Actor))
	{
		Title = UFGGameData::ItemName(Node->Item).ToString();
		Body = TEXT("Resource node. Extractors can sit on it.");
		Keys = TEXT("[E] gather (hold to keep gathering)");
	}
	else if (const AFGBelt* Belt = Cast<AFGBelt>(Actor))
	{
		Title = TEXT("Belt");
		Body = Belt->GetStatusText();
		Keys = TEXT("[X] remove");
	}
	else
	{
		return;
	}

	TArray<FString> BodyLines;
	Body.ParseIntoArray(BodyLines, TEXT("\n"));
	const float W = 460.f * S;
	const float H = (44.f + BodyLines.Num() * 20.f + 26.f) * S;
	DrawPanel(CX - W * 0.5f, Y, W, H);
	DrawText(Title, Warm, CX - W * 0.5f + 12.f * S, Y + 8.f * S, Big, S);
	float LineY = Y + 38.f * S;
	for (const FString& Line : BodyLines)
	{
		DrawText(Line, Soft, CX - W * 0.5f + 12.f * S, LineY, Small, S * 1.25f);
		LineY += 20.f * S;
	}
	DrawText(Keys, Cyan, CX - W * 0.5f + 12.f * S, LineY + 4.f * S, Small, S * 1.2f);
}

void AFGHUD::DrawToast(AFGPlayerController* PC)
{
	if (PC->ToastTime <= 0.f || PC->Toast.IsEmpty())
	{
		return;
	}
	UFont* Small = GEngine->GetSmallFont();
	const float Alpha = FMath::Clamp(PC->ToastTime / 0.5f, 0.f, 1.f);
	DrawWrapped(PC->Toast, Canvas->ClipX * 0.5f, Canvas->ClipY * 0.5f - 60.f * S, 800.f * S, Small, S * 1.4f, FLinearColor(1.f, 1.f, 1.f, Alpha), true);
}

void AFGHUD::DrawStory(AFGPlayerController* PC)
{
	if (!PC->bLineActive)
	{
		return;
	}
	const FFGStoryLine& Line = PC->CurrentLine;
	if (Line.Style == EFGLineStyle::Puzzle)
	{
		return;
	}
	UFont* Large = GEngine->GetLargeFont();
	UFont* Medium = GEngine->GetMediumFont();
	const float CX = Canvas->ClipX * 0.5f;
	const float Fade = FMath::Clamp(FMath::Min(PC->LineTime / 0.4f, (Line.Duration - PC->LineTime) / 0.4f), 0.f, 1.f);

	if (PC->IsInFlashback())
	{
		// Warm, faded memory with letterbox bars.
		DrawRect(FLinearColor(0.32f, 0.2f, 0.08f, 0.82f), 0.f, 0.f, Canvas->ClipX, Canvas->ClipY);
		const float Bar = Canvas->ClipY * 0.11f;
		DrawRect(FLinearColor::Black, 0.f, 0.f, Canvas->ClipX, Bar);
		DrawRect(FLinearColor::Black, 0.f, Canvas->ClipY - Bar, Canvas->ClipX, Bar);
	}

	if (Line.Style == EFGLineStyle::Title)
	{
		const bool bFlash = PC->IsInFlashback();
		float Y = Canvas->ClipY * 0.4f;
		if (bFlash)
		{
			DrawWrapped(TEXT("A MEMORY"), CX, Y - 40.f * S, 900.f * S, Medium, S, FLinearColor(1.f, 0.85f, 0.6f, 0.7f * Fade), true);
		}
		DrawWrapped(Line.Text.ToString(), CX, Y, 1200.f * S, Large, S * 1.6f, FLinearColor(1.f, 1.f, 1.f, Fade), true);
		return;
	}

	const FString Speaker = Line.Speaker.ToString();
	const float W = 1100.f * S;
	const float Y = Canvas->ClipY - (PC->IsInFlashback() ? Canvas->ClipY * 0.11f + 120.f * S : 210.f * S);
	if (!PC->IsInFlashback())
	{
		DrawPanel(CX - W * 0.5f - 16.f * S, Y - 10.f * S, W + 32.f * S, 96.f * S, FLinearColor(0.f, 0.f, 0.f, 0.45f * Fade));
	}
	if (!Speaker.IsEmpty())
	{
		DrawWrapped(Speaker.ToUpper(), CX, Y, W, Medium, S * 1.0f, SpeakerColor(Speaker) * FLinearColor(1.f, 1.f, 1.f, Fade), true);
	}
	DrawWrapped(Line.Text.ToString(), CX, Y + 30.f * S, W, Medium, S * 1.3f, FLinearColor(1.f, 1.f, 1.f, Fade), true);
}

void AFGHUD::DrawPuzzle(AFGPlayerController* PC)
{
	if (!PC->bPuzzleOpen && !PC->bPuzzleWaiting)
	{
		return;
	}
	UFont* Large = GEngine->GetLargeFont();
	UFont* Medium = GEngine->GetMediumFont();
	const float CX = Canvas->ClipX * 0.5f;
	DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.55f), 0.f, 0.f, Canvas->ClipX, Canvas->ClipY);

	if (PC->bPuzzleWaiting)
	{
		DrawWrapped(TEXT("Receiving Neela's drawing..."), CX, Canvas->ClipY * 0.45f, 900.f * S, Medium, S * 1.2f, Warm, true);
		return;
	}

	UTexture2D* Picture = PC->PuzzlePicture;
	const float MaxW = 760.f * S;
	const float Aspect = (Picture && Picture->GetSizeX() > 0) ? float(Picture->GetSizeY()) / Picture->GetSizeX() : 0.55f;
	const float PicW = MaxW;
	const float PicH = MaxW * Aspect;
	const float PicX = CX - PicW * 0.5f;
	const float PicY = Canvas->ClipY * 0.5f - PicH * 0.5f - 40.f * S;

	// A sheet of paper with her drawing on it.
	DrawRect(FLinearColor(0.98f, 0.95f, 0.86f, 1.f), PicX - 24.f * S, PicY - 70.f * S, PicW + 48.f * S, PicH + 190.f * S);
	DrawWrapped(TEXT("\"How many fish did I draw, Mum?\""), CX, PicY - 52.f * S, PicW, Medium, S * 1.15f, FLinearColor(0.25f, 0.18f, 0.1f), true);
	if (Picture)
	{
		// The API pictures have a transparent background: let the paper show through.
		DrawTexture(Picture, PicX, PicY, PicW, PicH, 0.f, 0.f, 1.f, 1.f, FLinearColor::White, BLEND_Translucent);
	}

	// One button-like box per answer.
	const int32 NumOptions = PC->PuzzleOptions.Num();
	const float BoxW = 130.f * S;
	const float BoxGap = 24.f * S;
	float BoxX = CX - (NumOptions * BoxW + (NumOptions - 1) * BoxGap) * 0.5f;
	const float BoxY = PicY + PicH + 18.f * S;
	for (int32 Index = 0; Index < NumOptions; ++Index)
	{
		DrawRect(FLinearColor(0.1f, 0.25f, 0.45f, 0.12f), BoxX, BoxY, BoxW, 52.f * S);
		const FString Label = FString::Printf(TEXT("[%d]   %d"), Index + 1, PC->PuzzleOptions[Index]);
		DrawText(Label, FLinearColor(0.1f, 0.25f, 0.45f), BoxX + (BoxW - TextWidth(Label, Large, S * 1.1f)) * 0.5f, BoxY + 8.f * S, Large, S * 1.1f);
		BoxX += BoxW + BoxGap;
	}
	DrawWrapped(TEXT("Press 1-4"), CX, PicY + PicH + 76.f * S, PicW, Medium, S * 0.9f, FLinearColor(0.4f, 0.35f, 0.3f), true);
}
