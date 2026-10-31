import unreal

task = unreal.AssetImportTask()
task.filename = r"D:\Game\FishGame\Saved\DownloadedAssets\test_tex.png"
task.destination_path = "/Game/Blue/Materials"
task.destination_name = "T_TestTex"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

tex = unreal.load_object(None, "/Game/Blue/Materials/T_TestTex")
if tex:
    print("SUCCESS: Loaded T_TestTex, size:", tex.blueprint_get_size_x(), tex.blueprint_get_size_y())
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Materials/T_TestTex")
    print("Cleaned up T_TestTex")
else:
    print("FAILED to load T_TestTex")
