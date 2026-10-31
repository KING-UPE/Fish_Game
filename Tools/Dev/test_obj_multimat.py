import unreal

task = unreal.AssetImportTask()
task.filename = r"D:\Game\FishGame\Saved\test_multimat.obj"
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestMultiMat"
task.replace_existing = True
task.automated = True
task.save = True

ui = unreal.FbxImportUI()
ui.import_mesh = True
ui.import_as_skeletal = False
ui.import_materials = False
ui.import_textures = False
task.options = ui

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestMultiMat.SM_TestMultiMat")
if sm:
    print(f"Success! Imported {sm.get_name()}:")
    print(f"  Materials: {len(sm.static_materials)}")
    for i, m in enumerate(sm.static_materials):
        print(f"    Slot {i}: {m.material_slot_name}")
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Meshes/SM_TestMultiMat")
else:
    print("Failed to import SM_TestMultiMat")
