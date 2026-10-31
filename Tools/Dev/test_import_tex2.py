import unreal

task = unreal.AssetImportTask()
task.filename = r"D:\Game\FishGame\Saved\test_tex.png"
task.destination_path = "/Game/Blue/Materials"
task.destination_name = "T_TestTex"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

tex = unreal.load_object(None, "/Game/Blue/Materials/T_TestTex.T_TestTex")
if tex:
    print("Texture imported successfully!", tex.get_name(), tex.blueprint_get_size_x(), tex.blueprint_get_size_y())
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Materials/T_TestTex")
else:
    print("Failed to import texture")
