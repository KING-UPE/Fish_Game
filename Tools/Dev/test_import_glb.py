import unreal

task = unreal.AssetImportTask()
task.filename = r"D:\Game\FishGame\Saved\DownloadedAssets\conveyor.glb"
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestGlb"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestGlb.SM_TestGlb")
print("GLB load:", sm)
if sm:
    print("Num sections:", sm.get_num_sections(0))
    print("Num mats:", len(sm.static_materials))
    bb = sm.get_bounding_box()
    print("Bounds:", bb.min, bb.max)
