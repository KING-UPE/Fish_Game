#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "FGHUD.generated.h"

class AFGPlayerController;
class UFont;

/** Canvas HUD: phase goals, power, inventory, hotbar, look-at info, subtitles, flashbacks, Neela's drawing. */
UCLASS()
class FISHGAME_API AFGHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;

private:
	float S = 1.f; // UI scale (1 at 1080p)

	void DrawPanel(float X, float Y, float W, float H, const FLinearColor& Color = FLinearColor(0.f, 0.02f, 0.04f, 0.6f));
	float DrawWrapped(const FString& Text, float X, float Y, float MaxWidth, UFont* Font, float Scale, const FLinearColor& Color, bool bCentered = false);
	float TextWidth(const FString& Text, UFont* Font, float Scale);

	void DrawCrosshair();
	void DrawPhasePanel(AFGPlayerController* PC);
	void DrawPowerAndInventory(AFGPlayerController* PC);
	void DrawHotbar(AFGPlayerController* PC);
	void DrawLookInfo(AFGPlayerController* PC);
	void DrawStory(AFGPlayerController* PC);
	void DrawPuzzle(AFGPlayerController* PC);
	void DrawToast(AFGPlayerController* PC);
};
