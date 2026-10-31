import unreal
import os

obj_content = """# Test Multi-material OBJ
v -10 -10 0
v 10 -10 0
v 10 10 0
v -10 10 0
v 0 0 20
v 0 0 -10
vt 0 0
vt 1 0
vt 1 1
vt 0 1
vn 0 0 1

usemtl Slot_Basalt
f 1/1/1 2/2/1 3/3/1
f 1/1/1 3/3/1 4/4/1

usemtl Slot_Crystal
f 1/1/1 2/2/1 5/1/1
f 2/2/1 3/3/1 5/2/1

usemtl Slot_Veins
f 3/3/1 4/4/1 5/3/1
f 4/4/1 1/1/1 5/4/1
"""

test_obj_path = r"D:\Game\FishGame\Saved\test_multimat.obj"
with open(test_obj_path, "w") as f:
    f.write(obj_content)

task = unreal.AssetImportTask()
task.filename = test_obj_path
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestMultiMat"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestMultiMat")
if sm:
    print(f"Num material slots: {len(sm.static_materials)}")
    for i, m in enumerate(sm.static_materials):
        print(f"  Slot {i}: {m.material_slot_name}")
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Meshes/SM_TestMultiMat")
else:
    print("FAILED")
