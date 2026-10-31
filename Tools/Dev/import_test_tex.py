import unreal
import os

tex_path = r"D:\Game\FishGame\Saved\test_tex.png"
task = unreal.AssetImportTask()
task.filename = tex_path
task.destination_path = "/Game/Blue/Textures"
task.destination_name = "T_TestTex"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

tex = unreal.load_object(None, "/Game/Blue/Textures/T_TestTex")
if tex:
    print("SUCCESS importing Texture!", tex.get_name())
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Textures/T_TestTex")
else:
    print("FAILED importing Texture")
if os.path.exists(tex_path):
    os.remove(tex_path)
