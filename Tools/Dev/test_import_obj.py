import os
import unreal

OBJ_PATH = r"D:\Game\FishGame\Saved\DownloadedAssets\test_mesh.obj"

# Create a small multi-group OBJ
obj_content = """# Test OBJ with two material slots
v -10 -10 0
v 10 -10 0
v 10 10 0
v -10 10 0
v -10 -10 20
v 10 -10 20
v 10 10 20
v -10 10 20

vt 0 0
vt 1 0
vt 1 1
vt 0 1

vn 0 0 1
vn 0 0 -1
vn 0 1 0
vn 0 -1 0
vn 1 0 0
vn -1 0 0

g BaseSlot
usemtl M_Base
f 1/1/2 2/2/2 3/3/2
f 1/1/2 3/3/2 4/4/2
f 5/1/1 7/3/1 6/2/1
f 5/1/1 8/4/1 7/3/1

g TopSlot
usemtl M_Top
f 1/1/4 6/2/4 2/3/4
f 1/1/4 5/4/4 6/2/4
f 2/1/5 7/2/5 3/3/5
f 2/1/5 6/4/5 7/2/5
f 3/1/3 8/2/3 4/3/3
f 3/1/3 7/4/3 8/2/3
f 4/1/6 5/2/6 1/3/6
f 4/1/6 8/4/6 5/2/6
"""

with open(OBJ_PATH, "w") as f:
    f.write(obj_content)

task = unreal.AssetImportTask()
task.filename = OBJ_PATH
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestObj"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestObj.SM_TestObj")
if sm:
    print("SUCCESS: Imported SM_TestObj")
    print(f"Num sections: {sm.get_num_sections(0)}, Num mats: {len(sm.static_materials)}")
    for i, m in enumerate(sm.static_materials):
        print(f"  Slot {i}: {m.material_slot_name}")
else:
    print("FAILED to load SM_TestObj")
