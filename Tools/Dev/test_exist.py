import unreal

eal = unreal.EditorAssetLibrary
print("M_Machine exists?", eal.does_asset_exist("/Game/Blue/Materials/M_Machine"))
print("SM_FoundationTile exists?", eal.does_asset_exist("/Game/Blue/Meshes/SM_FoundationTile"))
