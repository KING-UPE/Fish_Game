import os
import unreal

DOWNLOAD_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
DEST_PATH = "/Game/Blue/Meshes"

# Map high-poly FBX to Unreal static mesh asset names
NEW_ASSET_MAP = {
    "smelter_highpoly.fbx": "SM_SmelterCore",
    "assembler_highpoly.fbx": "SM_AssemblerCore",
    "storage_highpoly.fbx": "SM_StorageCrate",
    "solar_highpoly.fbx": "SM_SignalAntenna",
    "conveyor_highpoly.fbx": "SM_Conveyor",
    "crane_gantry_highpoly.fbx": "SM_MachineGantry",
    "fluid_tank_highpoly.fbx": "SM_FluidTank",
    "signal_dish_highpoly.fbx": "SM_SignalDish",
    "coral_ore_highpoly.fbx": "SM_CoralOreNode",
    "scrap_pile_highpoly.fbx": "SM_ScrapMetalPile",
}

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

tasks = []
for filename, asset_name in NEW_ASSET_MAP.items():
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

print(f"Importing {len(tasks)} custom high-poly meshes into UE 5.8...")
TOOLS.import_asset_tasks(tasks)

# Setup materials & collision
default_mat = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")
belt_mat = unreal.load_object(None, "/Game/Blue/Materials/M_Belt.M_Belt")

for task in tasks:
    asset_path = f"{DEST_PATH}/{task.destination_name}.{task.destination_name}"
    sm = unreal.load_object(None, asset_path)
    if sm:
        mat = belt_mat if "Conveyor" in task.destination_name else default_mat
        for idx in range(max(1, len(sm.static_materials))):
            sm.set_material(idx, mat)
        
        # Add simple box collision if needed
        if subsystem and subsystem.get_simple_collision_count(sm) == 0:
            subsystem.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
            
        EAL.save_loaded_asset(sm)
        b = sm.get_bounds()
        print(f"  OK: {task.destination_name} Extent={b.box_extent} Origin={b.origin}")

print("Import and configuration complete!")
