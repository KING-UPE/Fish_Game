using UnrealBuildTool;

public class FishGame : ModuleRules
{
	public FishGame(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput"
		});

		// HTTP + Json for the Fish Game API, AssetRegistry for the offline fallback pictures.
		PrivateDependencyModuleNames.AddRange(new string[] {
			"HTTP",
			"Json",
			"JsonUtilities",
			"AssetRegistry"
		});
	}
}
