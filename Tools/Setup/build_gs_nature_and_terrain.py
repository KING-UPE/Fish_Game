"""GeometryScript Satisfactory Nature & Landscape Generator for FishGame (UE 5.8)
Builds 100% native Unreal static meshes with collision and materials:
1. SM_Island_Terrain (submerged base to Z = -600, rolling hills, factory plateau, slope material)
2. SM_RockCliff_Large (stratified geological cliff face with horizontal ledges & vertical fissures)
3. SM_RockBoulder_A & B (organic weathered granite boulders)
4. SM_SeaStack (dramatic coastal monolith with wave-cut notch and overhanging crown)
5. SM_AlienTree_Canopy (10m sprawling umbrella tree with buttress roots and hanging vines)
6. SM_Foliage_Bush (dense multi-lobe leafy shrub)
7. SM_Fern_Cluster (ground fern rosette)
"""
import math
import random
import unreal

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MESH_DIR = "/Game/Blue/Meshes"
MAT_DIR = "/Game/Blue/Materials"

def get_or_create_mesh(name):
    path = f"{MESH_DIR}/{name}"
    if not EAL.does_asset_exist(path):
        EAL.duplicate_asset("/Engine/BasicShapes/Cylinder", path)
    return EAL.load_asset(path), path

def get_mat(name):
    return EAL.load_asset(f"{MAT_DIR}/{name}")

def commit_mesh(sm, dm, path, collision_complex=False, material=None):
    norm_opts = unreal.GeometryScriptCalculateNormalsOptions()
    unreal.GeometryScript_Normals.recompute_normals(dm, norm_opts)
    
    copy_opts = unreal.GeometryScriptCopyMeshToAssetOptions()
    lod = unreal.GeometryScriptMeshWriteLOD()
    res, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, copy_opts, lod)
    
    if material:
        sm.set_material(0, material)
        
    body = sm.get_editor_property("body_setup")
    if body:
        if collision_complex:
            body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        else:
            subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
            if subsystem and subsystem.get_simple_collision_count(sm) == 0:
                subsystem.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
                
    EAL.save_asset(path)
    bbox = sm.get_bounding_box()
    dx = bbox.max.x - bbox.min.x
    dy = bbox.max.y - bbox.min.y
    dz = bbox.max.z - bbox.min.z
    print(f"  OK: {sm.get_name()} Outcome={outcome} Size=({dx:.0f}x{dy:.0f}x{dz:.0f})")

# ==============================================================================
# 1. SM_Island_Terrain: Real Island with Submerged Foundation & Plateau
# ==============================================================================
def build_island_terrain():
    sm, path = get_or_create_mesh("SM_Island_Terrain")
    dm = unreal.DynamicMesh()
    opts = unreal.GeometryScriptPrimitiveOptions()
    
    # 1. Submerged seabed anchor foundation from Z = -600 to Z = 0
    tf_base = unreal.Transform(location=[0, 0, -600])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_base, radius=2550.0, height=600.0, radial_steps=48, height_steps=4)
    
    # 2. Main island above waterline: Z = 0 to Z = 150
    tf_land = unreal.Transform(location=[0, 0, 0])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_land, radius=2450.0, height=140.0, radial_steps=48, height_steps=4)
    
    # 3. Flat factory construction plateau in center (Radius 850 cm, flat at Z = 145)
    tf_plat = unreal.Transform(location=[0, 0, 140])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_plat, radius=850.0, height=10.0, radial_steps=32)
    
    # 4. Elevated rolling hill ridge on East flank (Reaching Z = 210)
    tf_hill = unreal.Transform(location=[950, 450, 120], rotation=[0, 0, 25], scale=[1.5, 0.9, 0.45])
    unreal.GeometryScript_Primitives.append_sphere_lat_long(dm, opts, tf_hill, radius=520.0, steps_phi=32, steps_theta=20)
    
    # 5. Secondary hill knoll on Northwest flank
    tf_knoll = unreal.Transform(location=[-1100, 750, 110], scale=[1.2, 1.2, 0.4])
    unreal.GeometryScript_Primitives.append_sphere_lat_long(dm, opts, tf_knoll, radius=420.0, steps_phi=24, steps_theta=16)
    
    # Natural Perlin noise displacement on land
    noise_opts = unreal.GeometryScriptPerlinNoiseOptions()
    noise_opts.apply_along_normal = True
    noise_opts.base_layer.magnitude = 15.0
    noise_opts.base_layer.frequency = 0.005
    sel = unreal.GeometryScriptMeshSelection()
    unreal.GeometryScript_MeshDeformers.apply_perlin_noise_to_mesh2(dm, sel, noise_opts)
    
    commit_mesh(sm, dm, path, collision_complex=True, material=get_mat("M_Terrain_Satisfactory"))

# ==============================================================================
# 2. SM_RockCliff_Large: Massive Stratified Geological Cliff (8m x 6m)
# ==============================================================================
def build_rock_cliff():
    sm, path = get_or_create_mesh("SM_RockCliff_Large")
    dm = unreal.DynamicMesh()
    opts = unreal.GeometryScriptPrimitiveOptions()
    
    # Main sheer cliff block (800 x 300 x 600 cm)
    tf_main = unreal.Transform(location=[0, 0, 0])
    unreal.GeometryScript_Primitives.append_box(dm, opts, tf_main, 800.0, 300.0, 600.0)
    
    # 3 Stratified horizontal rock layer shelves
    for sz in (140.0, 320.0, 480.0):
        tf_shelf = unreal.Transform(location=[0, -40.0, sz])
        unreal.GeometryScript_Primitives.append_box(dm, opts, tf_shelf, 840.0, 180.0, 45.0)
        
    # Vertical fissure buttresses
    for bx in (-260.0, 30.0, 250.0):
        tf_butt = unreal.Transform(location=[bx, -30.0, 0], rotation=[0, random.uniform(-6, 6), random.uniform(0, 360)])
        unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_butt, radius=90.0, height=620.0, radial_steps=8)
        
    # Perlin noise for weathered rock fractures
    noise_opts = unreal.GeometryScriptPerlinNoiseOptions()
    noise_opts.apply_along_normal = True
    noise_opts.base_layer.magnitude = 25.0
    noise_opts.base_layer.frequency = 0.015
    sel = unreal.GeometryScriptMeshSelection()
    unreal.GeometryScript_MeshDeformers.apply_perlin_noise_to_mesh2(dm, sel, noise_opts)
    
    commit_mesh(sm, dm, path, collision_complex=True, material=get_mat("MI_Rock"))

# ==============================================================================
# 3. SM_RockBoulder_A & B: Weathered Granite Boulders
# ==============================================================================
def build_boulders():
    for name, rad, scale in [("SM_RockBoulder_A", 160.0, [1.3, 1.05, 0.85]), ("SM_RockBoulder_B", 120.0, [1.1, 1.4, 0.9])]:
        sm, path = get_or_create_mesh(name)
        dm = unreal.DynamicMesh()
        opts = unreal.GeometryScriptPrimitiveOptions()
        
        tf = unreal.Transform(location=[0, 0, rad * 0.7], scale=scale)
        unreal.GeometryScript_Primitives.append_sphere_lat_long(dm, opts, tf, radius=rad, steps_phi=24, steps_theta=16)
        
        noise_opts = unreal.GeometryScriptPerlinNoiseOptions()
        noise_opts.apply_along_normal = True
        noise_opts.base_layer.magnitude = 28.0
        noise_opts.base_layer.frequency = 0.025
        sel = unreal.GeometryScriptMeshSelection()
        unreal.GeometryScript_MeshDeformers.apply_perlin_noise_to_mesh2(dm, sel, noise_opts)
        
        commit_mesh(sm, dm, path, collision_complex=False, material=get_mat("MI_Rock"))

# ==============================================================================
# 4. SM_SeaStack: Coastal Rock Pinnacle Monolith (14m)
# ==============================================================================
def build_sea_stack():
    sm, path = get_or_create_mesh("SM_SeaStack")
    dm = unreal.DynamicMesh()
    opts = unreal.GeometryScriptPrimitiveOptions()
    
    # Rising column from Z = -500 to Z = 700 (Height 1200 cm)
    tf_col = unreal.Transform(location=[0, 0, -500])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_col, radius=180.0, height=1200.0, radial_steps=12, height_steps=6)
    
    # Overhanging craggy crown at top (Z = 700 to Z = 950)
    tf_crown = unreal.Transform(location=[0, 0, 700])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_crown, radius=260.0, height=250.0, radial_steps=10)
    
    # Wave-cut base notch at water line (Z = 0)
    tf_notch = unreal.Transform(location=[0, 0, -40.0])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts, tf_notch, radius=150.0, height=80.0, radial_steps=12)
    
    noise_opts = unreal.GeometryScriptPerlinNoiseOptions()
    noise_opts.apply_along_normal = True
    noise_opts.base_layer.magnitude = 30.0
    noise_opts.base_layer.frequency = 0.012
    sel = unreal.GeometryScriptMeshSelection()
    unreal.GeometryScript_MeshDeformers.apply_perlin_noise_to_mesh2(dm, sel, noise_opts)
    
    commit_mesh(sm, dm, path, collision_complex=True, material=get_mat("MI_Rock"))

# ==============================================================================
# 5. SM_AlienTree_Canopy: Sprawling Umbrella Tree with Buttress Roots & Vines
# ==============================================================================
def build_alien_tree():
    sm, path = get_or_create_mesh("SM_AlienTree_Canopy")
    dm = unreal.DynamicMesh()
    unreal.GeometryScript_Materials.enable_material_i_ds(dm)
    
    opts_trunk = unreal.GeometryScriptPrimitiveOptions()
    opts_trunk.material_id = 0
    
    opts_leaf = unreal.GeometryScriptPrimitiveOptions()
    opts_leaf.material_id = 1
    
    # Gnarled trunk (Height 550 cm, radius 60 cm)
    tf_trunk = unreal.Transform(location=[0, 0, 0])
    unreal.GeometryScript_Primitives.append_cylinder(dm, opts_trunk, tf_trunk, radius=60.0, height=550.0, radial_steps=12, height_steps=4)
    
    # 5 Flaring buttress roots around trunk base
    for angle in (0, 72, 144, 216, 288):
        rad = math.radians(angle)
        rx, ry = math.cos(rad) * 90.0, math.sin(rad) * 90.0
        tf_root = unreal.Transform(location=[rx, ry, 0], rotation=[15 * math.sin(rad), -15 * math.cos(rad), angle])
        unreal.GeometryScript_Primitives.append_box(dm, opts_trunk, tf_root, 35.0, 25.0, 120.0)
        
    # 3 Major spreading boughs branching outward
    boughs = [
        (-220.0, 80.0, 520.0, 25, 30),
        (200.0, -120.0, 540.0, -25, -20),
        (50.0, 240.0, 560.0, 15, 35),
    ]
    for bx, by, bz, rx, ry in boughs:
        # Branch limb
        tf_bough = unreal.Transform(location=[bx * 0.5, by * 0.5, 450.0], rotation=[rx, ry, 0])
        unreal.GeometryScript_Primitives.append_cylinder(dm, opts_trunk, tf_bough, radius=32.0, height=260.0, radial_steps=8)
        
        # Sprawling umbrella foliage canopy on each branch
        tf_canopy = unreal.Transform(location=[bx, by, bz + 80.0], scale=[1.4, 1.4, 0.45])
        unreal.GeometryScript_Primitives.append_sphere_lat_long(dm, opts_leaf, tf_canopy, radius=240.0, steps_phi=20, steps_theta=12)
        
        # Drooping vine tendrils hanging from canopy
        for vx, vy in ((-70, 30), (60, -50), (10, 80)):
            tf_vine = unreal.Transform(location=[bx + vx, by + vy, bz - 120.0])
            unreal.GeometryScript_Primitives.append_cylinder(dm, opts_leaf, tf_vine, radius=4.0, height=200.0, radial_steps=6)
            
    # Central top canopy crown
    tf_crown = unreal.Transform(location=[0, 0, 680.0], scale=[1.5, 1.5, 0.5])
    unreal.GeometryScript_Primitives.append_sphere_lat_long(dm, opts_leaf, tf_crown, radius=320.0, steps_phi=24, steps_theta=14)
    
    norm_opts = unreal.GeometryScriptCalculateNormalsOptions()
    unreal.GeometryScript_Normals.recompute_normals(dm, norm_opts)
    copy_opts = unreal.GeometryScriptCopyMeshToAssetOptions()
    lod = unreal.GeometryScriptMeshWriteLOD()
    unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, copy_opts, lod, use_section_materials=True)
    sm.set_material(0, get_mat("MI_Trunk"))
    sm.set_material(1, get_mat("MI_Palm"))
    
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if subsystem and subsystem.get_simple_collision_count(sm) == 0:
        subsystem.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
        
    EAL.save_asset(path)
    print("  OK: SM_AlienTree_Canopy updated with Trunk (MI_Trunk) & Canopy (MI_Palm) materials!")

# ==============================================================================
# 6. SM_Foliage_Bush: Dense Multi-Lobe Shrub
# ==============================================================================
def build_bush():
    sm, path = get_or_create_mesh("SM_Foliage_Bush")
    dm = unreal.DynamicMesh()
    opts = unreal.GeometryScriptPrimitiveOptions()
    
    lobes = [
        (0, 0, 70, 95.0),
        (55, 30, 60, 75.0),
        (-45, 35, 55, 70.0),
        (25, -50, 65, 80.0),
        (-35, -40, 50, 65.0),
    ]
    for lx, ly, lz, rad in lobes:
        tf = unreal.Transform(location=[lx, ly, lz], scale=[1.0, 1.0, 0.75])
        unreal.GeometryScript_Primitives.append_sphere_lat_long(dm, opts, tf, radius=rad, steps_phi=16, steps_theta=10)
        
    noise_opts = unreal.GeometryScriptPerlinNoiseOptions()
    noise_opts.apply_along_normal = True
    noise_opts.base_layer.magnitude = 12.0
    noise_opts.base_layer.frequency = 0.03
    sel = unreal.GeometryScriptMeshSelection()
    unreal.GeometryScript_MeshDeformers.apply_perlin_noise_to_mesh2(dm, sel, noise_opts)
    
    commit_mesh(sm, dm, path, collision_complex=False, material=get_mat("MI_Palm"))

# ==============================================================================
# 7. SM_Fern_Cluster: Ground Fern Rosette
# ==============================================================================
def build_fern():
    sm, path = get_or_create_mesh("SM_Fern_Cluster")
    dm = unreal.DynamicMesh()
    opts = unreal.GeometryScriptPrimitiveOptions()
    
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        fx, fy = math.cos(rad) * 45.0, math.sin(rad) * 45.0
        tf = unreal.Transform(location=[fx, fy, 25.0], rotation=[-20 * math.sin(rad), 20 * math.cos(rad), angle])
        unreal.GeometryScript_Primitives.append_box(dm, opts, tf, 22.0, 90.0, 4.0)
        
    commit_mesh(sm, dm, path, collision_complex=False, material=get_mat("MI_Palm"))

# ==============================================================================
# Execute All Nature & Landscape Builds
# ==============================================================================
print("--- BUILDING FULL SATISFACTORY NATURE & TERRAIN SUITE VIA GEOMETRYSCRIPT ---")
build_island_terrain()
build_rock_cliff()
build_boulders()
build_sea_stack()
build_alien_tree()
build_bush()
build_fern()
print("--- SATISFACTORY NATURE & TERRAIN SUITE COMPLETED SUCCESSFULLY! ---")
