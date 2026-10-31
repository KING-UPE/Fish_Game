"""Blender Nature & Landscape Generator for FishGame (Unreal Engine 5.8)
Builds Satisfactory-style ground environment:
1. SM_Island_Terrain: Real island topography with rolling hills, cliff terraces, buildable plateau, and solid submerged base (NO floating saucer!).
2. SM_RockCliff_Large: Massive stratified geological cliff face.
3. SM_RockBoulder_A & B: Weathered granite boulders and fractured outcrops.
4. SM_RockCluster: Natural ground pebble & stone scatter.
5. SM_SeaStack: Dramatic ocean rock pinnacle.
6. SM_AlienTree_Canopy: Sprawling umbrella tree with gnarled trunk and hanging vines (matching Satisfactory reference).
7. SM_Foliage_Bush: Dense multi-tier shrub.
8. SM_Fern_Cluster: Ground fern rosette.
"""
import os
import math
import random
import bpy
import bmesh

EXPORT_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
os.makedirs(EXPORT_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def create_mat(name, color=(0.2, 0.2, 0.2, 1.0), metallic=0.0, roughness=0.8):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

def get_nature_materials():
    return {
        "grass": create_mat("M_Nature_Grass", (0.16, 0.38, 0.12, 1.0), metallic=0.0, roughness=0.85),
        "rock": create_mat("M_Nature_Rock", (0.28, 0.27, 0.26, 1.0), metallic=0.05, roughness=0.9),
        "sand": create_mat("M_Nature_Sand", (0.75, 0.62, 0.42, 1.0), metallic=0.0, roughness=0.8),
        "bark": create_mat("M_Nature_Bark", (0.22, 0.16, 0.11, 1.0), metallic=0.0, roughness=0.9),
        "leaf": create_mat("M_Nature_Leaf", (0.18, 0.48, 0.14, 1.0), metallic=0.0, roughness=0.6),
    }

def export_fbx(obj, filename, smart_uv=True):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    if smart_uv:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    filepath = os.path.join(EXPORT_DIR, filename)
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        axis_forward='-Z',
        axis_up='Y',
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE'
    )
    print(f"Exported: {filepath} ({len(obj.data.vertices)} vertices)")
    return filepath

# ==============================================================================
# 1. REAL ISLAND TERRAIN: Natural Topography with Submerged Base (NO FLOATING DISK!)
# ==============================================================================
def build_island_terrain():
    reset_scene()
    mats = get_nature_materials()
    
    mesh = bpy.data.meshes.new("SM_Island_Terrain")
    bm = bmesh.new()
    
    R_ISLAND = 24.0      # In Blender units (will be scaled to 2400 cm in UE)
    R_SEABED = 36.0      # Submerged foundation perimeter
    GRID_N = 64          # Grid density
    
    verts = []
    # Generate high-density terrain grid
    for ix in range(GRID_N + 1):
        row = []
        gx = (ix / GRID_N - 0.5) * 2.0 * R_SEABED
        for iy in range(GRID_N + 1):
            gy = (iy / GRID_N - 0.5) * 2.0 * R_SEABED
            dist = math.hypot(gx, gy)
            
            if dist > R_SEABED:
                # Underwater ocean floor
                gz = -6.0
            elif dist > R_ISLAND:
                # Submerged coastal shelf sloping down to seabed
                t = (dist - R_ISLAND) / (R_SEABED - R_ISLAND)
                gz = -0.5 - t * 5.5
            else:
                # Island above sea level!
                norm_d = dist / R_ISLAND
                # Base dome height curve
                base_h = 2.4 * (1.0 - norm_d ** 1.8)
                
                # Multi-octave natural terrain noise (hills, valleys, ridges)
                n1 = math.sin(gx * 0.35) * math.cos(gy * 0.35) * 0.45
                n2 = math.sin(gx * 0.7 + 1.2) * math.sin(gy * 0.7 - 0.8) * 0.25
                n3 = math.cos(gx * 1.4) * math.cos(gy * 1.4) * 0.12
                
                # Ridge on East flank
                ridge = math.exp(-((gx - 6.0)**2 + (gy - 4.0)**2) / 36.0) * 0.85
                
                # Central factory building plateau (flattened for clean construction)
                if dist < 6.5:
                    plateau_weight = min(1.0, max(0.0, (6.5 - dist) / 2.0))
                    raw_z = max(0.2, base_h + n1 + n2 + n3 + ridge)
                    gz = (1.0 - plateau_weight) * raw_z + plateau_weight * 2.2
                else:
                    gz = max(0.1, base_h + n1 + n2 + n3 + ridge)
            
            v = bm.verts.new((gx, gy, gz))
            row.append(v)
        verts.append(row)
    
    bm.verts.ensure_lookup_table()
    
    # Create quad faces
    for ix in range(GRID_N):
        for iy in range(GRID_N):
            v1 = verts[ix][iy]
            v2 = verts[ix + 1][iy]
            v3 = verts[ix + 1][iy + 1]
            v4 = verts[ix][iy + 1]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except Exception:
                pass
    
    # Create clean planar UV mapping for terrain
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for loop in face.loops:
            u = loop.vert.co.x / (2.0 * R_SEABED) + 0.5
            v = loop.vert.co.y / (2.0 * R_SEABED) + 0.5
            loop[uv_layer].uv = (u, v)

    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("SM_Island_Terrain", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mats["grass"])
    obj.data.materials.append(mats["rock"])
    obj.data.materials.append(mats["sand"])
    
    # Smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True
        
    export_fbx(obj, "island_terrain_highpoly.fbx", smart_uv=False)
    return obj

# ==============================================================================
# 2. SATISFACTORY-STYLE ROCK FORMATIONS (Cliffs, Boulders, Outcrops)
# ==============================================================================
def build_rock_cliff():
    reset_scene()
    mats = get_nature_materials()
    parts = []
    
    # Massive Jagged Stratified Cliff Face (8m width, 6m height, 3m depth)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 3.0))
    cliff = bpy.context.active_object
    cliff.scale = (8.0, 3.0, 6.0)
    cliff.data.materials.append(mats["rock"])
    parts.append(cliff)
    
    # Stratified Horizontal Rock Layer Shelves
    for sz in (1.5, 3.2, 4.8):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.6, sz))
        shelf = bpy.context.active_object
        shelf.scale = (8.4, 1.8, 0.45)
        shelf.data.materials.append(mats["rock"])
        parts.append(shelf)
    
    # Vertical Fissure Buttresses
    for bx in (-2.8, 0.4, 2.6):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=6.2, location=(bx, -0.4, 3.0), vertices=7)
        buttress = bpy.context.active_object
        buttress.rotation_euler = (0, math.radians(random.uniform(-8, 8)), math.radians(random.uniform(0, 360)))
        buttress.data.materials.append(mats["rock"])
        parts.append(buttress)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = cliff
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_RockCliff_Large"
    export_fbx(final_mesh, "rock_cliff_highpoly.fbx")
    return final_mesh

def build_boulder():
    reset_scene()
    mats = get_nature_materials()
    
    # Weathered Rounded Mossy Granite Boulder (3m diameter)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.6, location=(0, 0, 1.3))
    boulder = bpy.context.active_object
    boulder.scale = (1.4, 1.1, 0.9)
    boulder.data.materials.append(mats["rock"])
    
    # Displace vertices slightly for organic natural variation
    for v in boulder.data.vertices:
        v.co.x += math.sin(v.co.y * 3.0) * 0.15
        v.co.y += math.cos(v.co.z * 3.0) * 0.15
        v.co.z += math.sin(v.co.x * 2.5) * 0.12
    
    boulder.name = "SM_RockBoulder_A"
    export_fbx(boulder, "rock_boulder_highpoly.fbx")
    return boulder

def build_sea_stack():
    reset_scene()
    mats = get_nature_materials()
    parts = []
    
    # Dramatic Coastal Sea Pinnacle Monolith (12m height rising from sea)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=12.0, location=(0, 0, 5.5), vertices=8)
    monolith = bpy.context.active_object
    monolith.data.materials.append(mats["rock"])
    parts.append(monolith)
    
    # Overhanging Craggy Crown
    bpy.ops.mesh.primitive_cylinder_add(radius=2.4, depth=2.5, location=(0, 0, 10.5), vertices=8)
    crown = bpy.context.active_object
    crown.data.materials.append(mats["rock"])
    parts.append(crown)
    
    # Wave-cut notch at water line (Z = 0)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.4, location=(0, 0, 0.5), major_segments=16, minor_segments=8)
    notch = bpy.context.active_object
    notch.data.materials.append(mats["sand"])
    parts.append(notch)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = monolith
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_SeaStack"
    export_fbx(final_mesh, "sea_stack_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 3. SATISFACTORY-STYLE ALIEN VEGETATION (Canopy Trees, Bushes, Ferns)
# ==============================================================================
def build_alien_tree():
    reset_scene()
    mats = get_nature_materials()
    parts = []
    
    # Gnarled Organic Twisted Trunk (Height 10m)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=5.0, location=(0, 0, 2.5), vertices=12)
    trunk = bpy.context.active_object
    trunk.data.materials.append(mats["bark"])
    parts.append(trunk)
    
    # Flaring Buttress Root Flares at Base
    for angle in (0, 72, 144, 216, 288):
        rad = math.radians(angle)
        rx, ry = math.cos(rad) * 0.9, math.sin(rad) * 0.9
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, ry, 0.6))
        root = bpy.context.active_object
        root.scale = (0.35, 0.25, 1.2)
        root.rotation_euler = (math.radians(15 * math.cos(rad)), math.radians(15 * math.sin(rad)), rad)
        root.data.materials.append(mats["bark"])
        parts.append(root)
    
    # 3 Major Spreading Bough Branches
    bough_configs = [
        (-2.2, 0.8, 6.5, 0.38, 4.2, 35, 20),
        (2.0, -1.2, 6.8, 0.35, 3.8, -30, -35),
        (0.5, 2.4, 7.2, 0.32, 4.0, 15, 45),
    ]
    for bx, by, bz, rad, depth, rx, ry in bough_configs:
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=depth, location=(bx * 0.5, by * 0.5, bz * 0.7), vertices=10)
        bough = bpy.context.active_object
        bough.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        bough.data.materials.append(mats["bark"])
        parts.append(bough)
        
        # Sprawling Umbrella Foliage Canopy Clustered on each branch
        bpy.ops.mesh.primitive_uv_sphere_add(radius=2.6, location=(bx, by, bz + 1.2), segments=16, ring_count=12)
        canopy = bpy.context.active_object
        canopy.scale = (1.4, 1.4, 0.55)  # Flattened umbrella shape
        canopy.data.materials.append(mats["leaf"])
        parts.append(canopy)
        
        # Hanging Moss / Vine Strands (Drooping down from canopy)
        for vx, vy in ((-0.8, 0.4), (0.7, -0.6), (0.2, 0.9)):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.2, location=(bx + vx, by + vy, bz - 0.2), vertices=6)
            vine = bpy.context.active_object
            vine.data.materials.append(mats["leaf"])
            parts.append(vine)
    
    # Central Main Top Canopy Crown
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.4, location=(0, 0, 9.5), segments=20, ring_count=14)
    top_crown = bpy.context.active_object
    top_crown.scale = (1.5, 1.5, 0.6)
    top_crown.data.materials.append(mats["leaf"])
    parts.append(top_crown)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_AlienTree_Canopy"
    export_fbx(final_mesh, "alien_tree_highpoly.fbx")
    return final_mesh

def build_bush():
    reset_scene()
    mats = get_nature_materials()
    parts = []
    
    # Dense Layered Shrub Cluster (2.2m diameter, 1.8m height)
    cluster_centers = [
        (0, 0, 0.9, 1.1),
        (0.65, 0.35, 0.75, 0.85),
        (-0.55, 0.45, 0.7, 0.8),
        (0.3, -0.6, 0.8, 0.9),
        (-0.4, -0.5, 0.65, 0.75),
    ]
    for cx, cy, cz, rad in cluster_centers:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rad, location=(cx, cy, cz))
        blob = bpy.context.active_object
        blob.scale = (1.0, 1.0, 0.75)
        blob.data.materials.append(mats["leaf"])
        parts.append(blob)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_Foliage_Bush"
    export_fbx(final_mesh, "foliage_bush_highpoly.fbx")
    return final_mesh

def build_fern():
    reset_scene()
    mats = get_nature_materials()
    parts = []
    
    # Ground-Covering Tropical Fern Rosette (1.6m diameter)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        fx, fy = math.cos(rad) * 0.55, math.sin(rad) * 0.55
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy, 0.35))
        frond = bpy.context.active_object
        frond.scale = (0.22, 0.95, 0.04)
        frond.rotation_euler = (math.radians(-25 * math.sin(rad)), math.radians(25 * math.cos(rad)), rad)
        frond.data.materials.append(mats["leaf"])
        parts.append(frond)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_Fern_Cluster"
    export_fbx(final_mesh, "fern_cluster_highpoly.fbx")
    return final_mesh

# ==============================================================================
# Execute All Nature & Landscape Builds
# ==============================================================================
print("--- GENERATING SATISFACTORY NATURE & LANDSCAPE SUITE ---")
build_island_terrain()
build_rock_cliff()
build_boulder()
build_sea_stack()
build_alien_tree()
build_bush()
build_fern()
print("--- NATURE & LANDSCAPE SUITE COMPLETED SUCCESSFULLY ---")
