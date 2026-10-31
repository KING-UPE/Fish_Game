import unreal
ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous(["/Game"])
eal = unreal.EditorAssetLibrary
print("SM_TowerSupport exists?", eal.does_asset_exist("/Game/Blue/Meshes/SM_TowerSupport"))
sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TowerSupport.SM_TowerSupport")
print("Loaded:", sm)
if sm:
    bbox = sm.get_bounding_box()
    print("BBox:", bbox.min, "to", bbox.max)
    print("Num materials:", len(sm.static_materials))
    print("Num LODs:", sm.get_num_lods())
    # count vertices
    mesh_desc = unreal.StaticMeshDescription()
