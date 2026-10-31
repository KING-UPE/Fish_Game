import unreal

tex_file = r"D:\Game\FishGame\Saved\T_CoralOre_SurveyPlaque.png"
task = unreal.AssetImportTask()
task.filename = tex_file
task.destination_path = "/Game/Blue/Textures"
task.destination_name = "T_CoralOre_SurveyPlaque"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

tex = unreal.load_object(None, "/Game/Blue/Textures/T_CoralOre_SurveyPlaque")
if tex:
    print(f"Successfully imported texture: {tex.get_name()}, size={tex.blueprint_get_size_x()}x{tex.blueprint_get_size_y()}")
else:
    print("Failed to import texture")
