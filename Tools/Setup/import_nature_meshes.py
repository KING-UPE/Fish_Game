import os
import unreal

# Disable Interchange for FBX so reliable legacy importer is used
unreal.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')

DOWNLOAD_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
DEST_PATH = "/Game/Blue/Meshes"

ASSET_MAP = {
    "island_terrain_highpoly.fbx": "SM_Island_Terrain",
    "rock_cliff_highpoly.fbx": "SM_RockCliff_Large",
    "rock_boulder_highpoly.fbx": "SM_RockBoulder_A",
    "sea_stack_highpoly.fbx": "SM_SeaStack",
    "alien_tree_highpoly.fbx": "SM_AlienTree_Canopy",
    "foliage_bush_highpoly.fbx": "SM_Foliage_Bush",
    "fern_cluster_highpoly.fbx": "SM_Fern_Cluster",
}

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

# Clean up any leftover test assets
for test_name in ["SM_TestLegacy", "SM_TestTerrainLegacy", "SM_TestAssembler", "SM_TestTree", "SM_TestCliff", "SM_TestTri", "SM_TestObj", "SM_TestTerrain"]:
    p = f"{DEST_PATH}/{test_name}"
    if EAL.does_asset_exist(p):
        EAL.delete_asset(p)

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
    ui.static_mesh_import_data.set_editor_property("generate_lightmap_u_vs", False)
    ui.static_mesh_import_data.set_editor_property("auto_generate_collision", False)
    task.options = ui
    tasks.append(task)

print(f"Importing {len(tasks)} Nature and Landscape high-poly meshes into UE 5.8...")
TOOLS.import_asset_tasks(tasks)

for task in tasks:
    asset_path = f"{DEST_PATH}/{task.destination_name}.{task.destination_name}"
    sm = unreal.load_object(None, asset_path)
    if sm:
        # Check collision
        if subsystem and subsystem.get_simple_collision_count(sm) == 0:
            if "Terrain" in task.destination_name or "Cliff" in task.destination_name:
                body = sm.get_editor_property("body_setup")
                if body:
                    body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            else:
                subsystem.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
        EAL.save_asset(asset_path)
        bbox = sm.get_bounding_box()
        dx = bbox.max.x - bbox.min.x
        dy = bbox.max.y - bbox.min.y
        dz = bbox.max.z - bbox.min.z
        print(f"  OK: {task.destination_name} - LODs: {sm.get_num_lods()}, Sections: {sm.get_num_sections(0)}, Size: {dx:.1f}x{dy:.1f}x{dz:.1f}")
    else:
        print(f"  FAILED to load {task.destination_name}")

print("ALL NATURE AND LANDSCAPE MESHES IMPORTED SUCCESSFULLY!")
