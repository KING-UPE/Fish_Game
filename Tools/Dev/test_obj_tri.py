import os
import unreal

obj_path = r"D:\Game\FishGame\Saved\DownloadedAssets\test_box2.obj"
with open(obj_path, "w") as f:
    f.write("""# Test OBJ triangulated
v -50.0 -50.0 0.0
v 50.0 -50.0 0.0
v 50.0 50.0 0.0
v -50.0 50.0 0.0
v -50.0 -50.0 100.0
v 50.0 -50.0 100.0
v 50.0 50.0 100.0
v -50.0 50.0 100.0

vn 0.0 0.0 -1.0
vn 0.0 0.0 1.0
vn 0.0 -1.0 0.0
vn 1.0 0.0 0.0
vn 0.0 1.0 0.0
vn -1.0 0.0 0.0

vt 0.0 0.0
vt 1.0 0.0
vt 1.0 1.0
vt 0.0 1.0

g Box
usemtl M_Machine
f 1/1/1 2/2/1 3/3/1
f 1/1/1 3/3/1 4/4/1
f 5/1/2 7/3/2 6/2/2
f 5/1/2 8/4/2 7/3/2
f 1/1/3 6/3/3 2/2/3
f 1/1/3 5/4/3 6/3/3
f 2/1/4 7/3/4 3/2/4
f 2/1/4 6/4/4 7/3/4
f 3/1/5 8/3/5 4/2/5
f 3/1/5 7/4/5 8/3/5
f 4/1/6 5/3/6 1/2/6
f 4/1/6 8/4/6 5/3/6
""")

tools = unreal.AssetToolsHelpers.get_asset_tools()
task = unreal.AssetImportTask()
task.filename = obj_path
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestBox2"
task.replace_existing = True
task.automated = True
task.save = True

tools.import_asset_tasks([task])
sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestBox2.SM_TestBox2")
print("Imported test box 2:", sm)
if sm:
    print("Num LODs:", sm.get_num_lods())
    if sm.get_num_lods() > 0:
        print("Num sections:", sm.get_num_sections(0))
        print("Num vertices:", sm.get_num_vertices(0))
    print("Bounding box:", sm.get_bounding_box())
    unreal.EditorAssetLibrary.delete_asset("/Game/Blue/Meshes/SM_TestBox2")
