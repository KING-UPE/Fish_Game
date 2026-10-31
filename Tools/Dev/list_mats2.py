import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous(["/Game/Blue"])
assets = ar.get_assets_by_path("/Game/Blue/Materials", recursive=True)
print(f"Found {len(assets)} assets in /Game/Blue/Materials:")
for a in assets:
    print(" ", a.package_name, a.asset_class_path.asset_name)
