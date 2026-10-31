import unreal

task = unreal.AssetImportTask()
task.filename = r"D:\Game\FishGame\Saved\test_tex.png"
task.destination_path = "/Game/Blue/Materials"
task.destination_name = "T_TestImport"
task.replace_existing = True
task.automated = True
task.save = True

TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
TOOLS.import_asset_tasks([task])

tex = unreal.load_object(None, "/Game/Blue/Materials/T_TestImport.T_TestImport")
print("Loaded texture:", tex)
if tex:
    print("Dimensions:", tex.blueprint_get_size_x(), tex.blueprint_get_size_y())
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Materials/T_TestImport")
    print("Deleted successfully.")
