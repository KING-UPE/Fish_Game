import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
assets = ar.get_assets_by_path("/Game/Blue", recursive=True)
print(f"Found {len(assets)} assets in /Game/Blue:")
for a in assets:
    print(f"  {a.asset_name} ({a.asset_class_path.asset_name}) at {a.package_name}")

meshes = ar.get_assets_by_path("/Game/Blue/Meshes", recursive=True)
print(f"\nMeshes in /Game/Blue/Meshes: {len(meshes)}")
for m in meshes:
    print(f"  {m.asset_name} at {m.package_name}")

mats = ar.get_assets_by_path("/Game/Blue/Materials", recursive=True)
print(f"\nMaterials in /Game/Blue/Materials: {len(mats)}")
for m in mats:
    print(f"  {m.asset_name} at {m.package_name}")
