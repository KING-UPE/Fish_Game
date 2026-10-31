import unreal

task = unreal.AssetImportTask()
task.filename = r"D:\Game\FishGame\Saved\test_cube.fbx"
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestCube"
task.replace_existing = True
task.automated = True
task.save = True

ui = unreal.FbxImportUI()
ui.import_mesh = True
ui.import_as_skeletal = False
ui.import_materials = False
ui.import_textures = False
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
ui.static_mesh_import_data.set_editor_property("combine_meshes", True)
ui.static_mesh_import_data.set_editor_property("transform_vertex_to_absolute", False)
task.options = ui

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestCube.SM_TestCube")
if sm:
    bbox = sm.get_bounding_box()
    dx = bbox.max.x - bbox.min.x
    dy = bbox.max.y - bbox.min.y
    dz = bbox.max.z - bbox.min.z
    print(f"TEST CUBE BBOX: min={bbox.min.x:.1f},{bbox.min.y:.1f},{bbox.min.z:.1f} max={bbox.max.x:.1f},{bbox.max.y:.1f},{bbox.max.z:.1f} size=({dx:.1f}, {dy:.1f}, {dz:.1f})")
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Meshes/SM_TestCube")
else:
    print("FAILED TO LOAD SM_TestCube")
