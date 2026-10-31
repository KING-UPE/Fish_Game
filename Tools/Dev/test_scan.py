import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous(["/Game/Blue"])
eal = unreal.EditorAssetLibrary
print("Assets after scan:")
for a in eal.list_assets("/Game/Blue", recursive=True):
    print(" ", a)
