import os
import unreal

DOWNLOAD_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
DEST_PATH = "/Game/Blue/Meshes"

ASSET_MAP = {
    "drill_tower_highpoly.fbx": "SM_TowerSupport",
    "robot_arm_highpoly.fbx": "SM_RobotArm",
    "console_highpoly.fbx": "SM_ConsoleTerminal",
    "hopper_highpoly.fbx": "SM_Hopper",
    "wreck_hull_highpoly.fbx": "SM_WreckHull",
    "foundation_highpoly.fbx": "SM_FoundationTile",
}

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

tasks = []
for filename, asset_name in ASSET_MAP.items():
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename}, not found")
        continue

    task = unreal.AssetImportTask()
    task.filename = filepath
    task.destination_path = DEST_PATH
    task.destination_name = asset_name
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
    tasks.append(task)

print(f"Importing {len(tasks)} Part 2 high-poly meshes into UE 5.8...")
TOOLS.import_asset_tasks(tasks)

# Assign PBR materials & collision
default_mat = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")

for task in tasks:
    asset_path = f"{DEST_PATH}/{task.destination_name}.{task.destination_name}"
    sm = unreal.load_object(None, asset_path)
    if sm:
        for idx in range(max(1, len(sm.static_materials))):
            sm.set_material(idx, default_mat)
        
        if subsystem and subsystem.get_simple_collision_count(sm) == 0:
            subsystem.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
            
        EAL.save_loaded_asset(sm)
        b = sm.get_bounds()
        print(f"  OK: {task.destination_name} Extent={b.box_extent} Origin={b.origin}")

print("Part 2 import complete!")
