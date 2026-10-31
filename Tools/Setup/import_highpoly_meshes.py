import os
import unreal
import warnings

warnings.simplefilter("ignore")

DOWNLOAD_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
DEST_PATH = "/Game/Blue/Meshes"

# Mapping: filename -> Asset Name
ASSET_MAP = {
    "conveyor.fbx": "SM_Conveyor",
    "conveyor-sides.fbx": "SM_ConveyorSides",
    "conveyor-stripe.fbx": "SM_ConveyorStripe",
    "cover-hopper.fbx": "SM_Hopper",
    "robot-arm-a.fbx": "SM_RobotArm",
    "scanner-high.fbx": "SM_Scanner",
    "box-large.fbx": "SM_StorageCrate",
    "station.fbx": "SM_SmelterCore",
    "stationLarge.fbx": "SM_AssemblerCore",
    "metalStructure.fbx": "SM_MachineGantry",
    "metalStructureCross.fbx": "SM_TowerSupport",
    "metalTileLarge.fbx": "SM_FoundationTile",
    "consoleScreen.fbx": "SM_ConsoleTerminal",
    "pipeStraight.fbx": "SM_PipeStraight",
    "pipeCorner.fbx": "SM_PipeCorner",
    "pipeStand.fbx": "SM_PipeStand",
    "barrelLarge.fbx": "SM_FluidTank",
    "satelliteDishLarge.fbx": "SM_SignalDish",
    "satelliteDishAntenna.fbx": "SM_SignalAntenna",
    "rocksOre.fbx": "SM_CoralOreNode",
    "rocksTallOre.fbx": "SM_ScrapMetalPile",
}

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()

tasks = []
for filename, asset_name in ASSET_MAP.items():
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename}, file not found")
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

print(f"Starting batch import of {len(tasks)} assets...")
TOOLS.import_asset_tasks(tasks)

# Set collision & materials on imported meshes
default_mat = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")
belt_mat = unreal.load_object(None, "/Game/Blue/Materials/M_Belt.M_Belt")
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

imported_count = 0
for task in tasks:
    asset_path = f"{DEST_PATH}/{task.destination_name}.{task.destination_name}"
    sm = unreal.load_object(None, asset_path)
    if sm:
        # Assign base material
        mat = belt_mat if "Conveyor" in task.destination_name else default_mat
        for idx in range(max(1, len(sm.static_materials))):
            sm.set_material(idx, mat)
        
        # Add simple box collision if missing
        if subsystem and subsystem.get_simple_collision_count(sm) == 0:
            subsystem.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
            
        EAL.save_loaded_asset(sm)
        bbox = sm.get_bounding_box()
        dx = bbox.max.x - bbox.min.x
        dy = bbox.max.y - bbox.min.y
        dz = bbox.max.z - bbox.min.z
        print(f"  OK: {task.destination_name} ({dx:.0f}x{dy:.0f}x{dz:.0f})")
        imported_count += 1
    else:
        print(f"  FAIL: Could not load {asset_path}")

print(f"Import complete! {imported_count}/{len(tasks)} meshes imported and saved.")
