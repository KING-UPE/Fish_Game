import os
import unreal

OBJ_CONTENT = """# Test multi-material obj
mtllib test.mtl
v 0 0 0
v 100 0 0
v 100 100 0
v 0 100 0
v 0 0 50
v 100 0 50
v 100 100 50
v 0 100 50

usemtl MatA
f 1 2 6 5
f 2 3 7 6

usemtl MatB
f 3 4 8 7
f 4 1 5 8
f 5 6 7 8
f 4 3 2 1
"""

test_obj_path = r"D:\Game\FishGame\Saved\test_mesh.obj"
with open(test_obj_path, "w") as f:
    f.write(OBJ_CONTENT)

task = unreal.AssetImportTask()
task.filename = test_obj_path
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestMesh"
task.replace_existing = True
task.automated = True
task.save = True

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestMesh.SM_TestMesh")
if sm:
    print(f"Successfully imported SM_TestMesh! Materials: {len(sm.static_materials)}")
    for i, m in enumerate(sm.static_materials):
        print(f"  Slot {i}: {m.material_slot_name}")
else:
    print("Failed to load SM_TestMesh")
