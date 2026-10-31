import unreal

# Generate the FBX first
import subprocess
subprocess.run(["python", "Tools/Dev/gen_test_fbx.py"], check=True)

fbx_path = r"D:\Game\FishGame\Saved\DownloadedAssets\test_generated.fbx"

task = unreal.AssetImportTask()
task.filename = fbx_path
task.destination_path = "/Game/Blue/Meshes"
task.destination_name = "SM_TestGen"
task.replace_existing = True
task.automated = True
task.save = True

ui = unreal.FbxImportUI()
ui.import_mesh = True
ui.import_as_skeletal = False
ui.import_materials = False
ui.import_textures = False
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
ui.static_mesh_import_data.set_editor_property("combine_meshes", True)
ui.static_mesh_import_data.set_editor_property("transform_vertex_to_absolute", False)
task.options = ui

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestGen.SM_TestGen")
if sm:
    print("SUCCESS importing SM_TestGen!")
    bb = sm.get_bounding_box()
    dx = bb.max.x - bb.min.x
    dy = bb.max.y - bb.min.y
    dz = bb.max.z - bb.min.z
    print(f"Bounds: min=({bb.min.x:.1f},{bb.min.y:.1f},{bb.min.z:.1f}) size=({dx:.1f}x{dy:.1f}x{dz:.1f})")
    print(f"LODs: {sm.get_num_lods()}, Sections: {sm.get_num_sections(0)}, Materials: {len(sm.static_materials)}")
    for i, m in enumerate(sm.static_materials):
        print(f"  Slot {i}: {m.material_slot_name}")
else:
    print("FAILED to load SM_TestGen")
