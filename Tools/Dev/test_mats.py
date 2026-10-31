import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
assets = ar.get_assets_by_path("/Game/Blue/Materials", recursive=True)
for a in assets:
    print(f"{a.asset_name} ({a.asset_class_path.asset_name})")
