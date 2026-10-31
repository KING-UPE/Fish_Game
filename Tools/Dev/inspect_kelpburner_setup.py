import unreal

def check_asset(path):
    obj = unreal.load_object(None, path)
    if not obj:
        print(f"NOT FOUND: {path}")
        return
    print(f"\nAsset: {path} ({obj.get_class().get_name()})")
    if isinstance(obj, unreal.StaticMesh):
        bb = obj.get_bounding_box()
        size = bb.max - bb.min
        sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        verts = sub.get_number_verts(obj, 0)
        # tris
        cols = sub.get_simple_collision_count(obj)
        print(f"  Bounds: Min=({bb.min.x:.1f}, {bb.min.y:.1f}, {bb.min.z:.1f}) Max=({bb.max.x:.1f}, {bb.max.y:.1f}, {bb.max.z:.1f}) Size=({size.x:.1f}, {size.y:.1f}, {size.z:.1f})")
        print(f"  Verts: {verts}, Collision Prims: {cols}")
        print(f"  Materials ({len(obj.static_materials)}):")
        for i, sm in enumerate(obj.static_materials):
            mname = sm.material_interface.get_name() if sm.material_interface else "None"
            print(f"    Slot {i}: {sm.material_slot_name} -> {mname}")

check_asset("/Game/Blue/Meshes/SM_SmelterCore.SM_SmelterCore")
check_asset("/Game/Blue/Meshes/SM_PipeStraight.SM_PipeStraight")

ar = unreal.AssetRegistryHelpers.get_asset_registry()
mats = ar.get_assets_by_path("/Game/Blue/Materials", recursive=True)
print("\nMaterials in /Game/Blue/Materials:")
for m in mats:
    print(f"  {m.asset_name} ({m.asset_class_path.asset_name})")

# Check referencers of SM_SmelterCore and SM_PipeStraight
for name in ["SM_SmelterCore", "SM_PipeStraight"]:
    refs = ar.get_referencers(f"/Game/Blue/Meshes/{name}", unreal.AssetRegistryDependencyOptions())
    print(f"\nReferencers of {name}:")
    for r in refs:
        print(f"  {r}")
