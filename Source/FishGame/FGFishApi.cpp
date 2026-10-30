#include "FGFishApi.h"

#include "FishGame.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Dom/JsonObject.h"
#include "Engine/Texture2D.h"
#include "HttpModule.h"
#include "ImageUtils.h"
#include "Interfaces/IHttpResponse.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

void UFGFishApiSubsystem::RequestPuzzle()
{
	if (bBusy)
	{
		return;
	}
	bBusy = true;

	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
	Request->SetURL(ApiUrl);
	Request->SetVerb(TEXT("GET"));
	Request->SetTimeout(6.f);
	Request->OnProcessRequestComplete().BindUObject(this, &UFGFishApiSubsystem::OnJsonReceived);
	if (!Request->ProcessRequest())
	{
		UseFallback(TEXT("request could not start"));
	}
}

void UFGFishApiSubsystem::RequestRepeatPuzzle()
{
	if (History.Num() == 0)
	{
		RequestPuzzle();
		return;
	}
	const FFGPuzzle& Old = History[FMath::RandRange(0, History.Num() - 1)];
	OnPuzzleReady.Broadcast(Old.Picture, Old.Fish, Old.Chests);
}

void UFGFishApiSubsystem::OnJsonReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnected)
{
	if (!bConnected || !Response.IsValid() || Response->GetResponseCode() != 200)
	{
		UseFallback(TEXT("no answer from the API"));
		return;
	}

	// { "question" : "https://.../ch_xxx.png" , "fish" : 4, "chest" : 3 }
	TSharedPtr<FJsonObject> Json;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());
	FString PictureUrl;
	int32 Fish = 0;
	int32 Chests = 0;
	if (!FJsonSerializer::Deserialize(Reader, Json) || !Json.IsValid()
		|| !Json->TryGetStringField(TEXT("question"), PictureUrl)
		|| !Json->TryGetNumberField(TEXT("fish"), Fish)
		|| !Json->TryGetNumberField(TEXT("chest"), Chests))
	{
		UseFallback(TEXT("unexpected JSON"));
		return;
	}

	PendingFish = Fish;
	PendingChests = Chests;

	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> ImageRequest = FHttpModule::Get().CreateRequest();
	ImageRequest->SetURL(PictureUrl);
	ImageRequest->SetVerb(TEXT("GET"));
	ImageRequest->SetTimeout(8.f);
	ImageRequest->OnProcessRequestComplete().BindUObject(this, &UFGFishApiSubsystem::OnImageReceived);
	if (!ImageRequest->ProcessRequest())
	{
		UseFallback(TEXT("picture request could not start"));
	}
}

void UFGFishApiSubsystem::OnImageReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnected)
{
	if (!bConnected || !Response.IsValid() || Response->GetResponseCode() != 200)
	{
		UseFallback(TEXT("picture download failed"));
		return;
	}
	const TArray<uint8>& Bytes = Response->GetContent();
	UTexture2D* Picture = FImageUtils::ImportBufferAsTexture2D(TArrayView64<const uint8>(Bytes.GetData(), Bytes.Num()));
	if (!Picture)
	{
		UseFallback(TEXT("picture could not be decoded"));
		return;
	}
	Finish(Picture, PendingFish, PendingChests, true);
}

void UFGFishApiSubsystem::UseFallback(const TCHAR* Reason)
{
	UE_LOG(LogFishGame, Warning, TEXT("Fish API: %s, using a bundled picture."), Reason);

	// Bundled pictures: /Game/Blue/FishApi/T_Fish_F<fish>_C<chests>
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
	TArray<FAssetData> Assets;
	Registry.GetAssetsByPath(FName(TEXT("/Game/Blue/FishApi")), Assets, true);
	TArray<FAssetData> Usable;
	for (const FAssetData& Asset : Assets)
	{
		if (Asset.AssetName.ToString().StartsWith(TEXT("T_Fish_F")))
		{
			Usable.Add(Asset);
		}
	}
	if (Usable.Num() == 0)
	{
		Finish(nullptr, 0, 0, false);
		return;
	}

	const FAssetData& Pick = Usable[FMath::RandRange(0, Usable.Num() - 1)];
	TArray<FString> Parts;
	Pick.AssetName.ToString().ParseIntoArray(Parts, TEXT("_"));
	int32 Fish = 0;
	int32 Chests = 0;
	for (const FString& Part : Parts)
	{
		if (Part.StartsWith(TEXT("F")) && Part.Len() > 1 && FChar::IsDigit(Part[1]))
		{
			Fish = FCString::Atoi(*Part.Mid(1));
		}
		else if (Part.StartsWith(TEXT("C")) && Part.Len() > 1 && FChar::IsDigit(Part[1]))
		{
			Chests = FCString::Atoi(*Part.Mid(1));
		}
	}
	Finish(Cast<UTexture2D>(Pick.GetAsset()), Fish, Chests, false);
}

void UFGFishApiSubsystem::Finish(UTexture2D* Picture, int32 Fish, int32 Chests, bool bLive)
{
	bBusy = false;
	if (Picture)
	{
		FFGPuzzle Puzzle;
		Puzzle.Picture = Picture;
		Puzzle.Fish = Fish;
		Puzzle.Chests = Chests;
		Puzzle.bLive = bLive;
		History.Add(Puzzle);
		UE_LOG(LogFishGame, Log, TEXT("Fish API puzzle ready: %d fish, %d chests (%s)."), Fish, Chests, bLive ? TEXT("live") : TEXT("offline"));
	}
	OnPuzzleReady.Broadcast(Picture, Fish, Chests);
}
