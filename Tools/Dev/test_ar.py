import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
assets = ar.get_assets_by_path("/Game/Blue", recursive=True)
print(f"Total assets via AR: {len(assets)}")
for a in assets[:20]:
    print(" ", a.package_name, a.asset_name, a.asset_class_path.asset_name)
