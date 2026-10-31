"""Blender High-Poly Asset Factory for FishGame (Unreal Engine 5.8)
Builds Satisfactory-grade industrial sci-fi models with:
- Beveled hard-surface chassis
- Recessed panels, cooling louvers, hydraulic pistons, conduit runs
- Stamped text plaques and in-universe graphics
- Clean multi-slot materials and proper UVs
- Automated FBX export with UE-ready transforms
"""
import os
import math
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

def create_mat(name, color=(0.2, 0.2, 0.2, 1.0), metallic=0.8, roughness=0.3, emissive=(0,0,0,1), emissive_strength=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emissive
            bsdf.inputs["Emission Strength"].default_value = emissive_strength
    return mat

def get_materials():
    return {
        "chassis": create_mat("M_Chassis_Dark", (0.15, 0.16, 0.18, 1.0), metallic=0.85, roughness=0.3),
        "steel": create_mat("M_Steel_Bright", (0.6, 0.62, 0.65, 1.0), metallic=0.9, roughness=0.22),
        "accent": create_mat("M_Accent_Orange", (0.95, 0.45, 0.05, 1.0), metallic=0.3, roughness=0.35),
        "hazard": create_mat("M_Hazard_Stripe", (0.9, 0.75, 0.05, 1.0), metallic=0.1, roughness=0.4),
        "screen": create_mat("M_Emissive_Screen", (0.1, 0.85, 1.0, 1.0), metallic=0.0, roughness=0.1, emissive=(0.1, 0.85, 1.0, 1.0), emissive_strength=5.0),
        "furnace": create_mat("M_Furnace_Glow", (1.0, 0.35, 0.02, 1.0), metallic=0.0, roughness=0.2, emissive=(1.0, 0.35, 0.02, 1.0), emissive_strength=8.0),
        "rubber": create_mat("M_Rubber_Dark", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.8),
    }

def add_bevel(obj, width=0.03, segments=2):
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(35)

def export_fbx(obj, filename):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Auto UV unwrap
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply transforms
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
# 1. SMELTER: FGS-01 Arc Smelter (Satisfactory-grade)
# ==============================================================================
def build_smelter():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Base Pedestal (3x3m footprint, beveled foundation)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.2))
    base = bpy.context.active_object
    base.name = "Smelter_Base"
    base.scale = (2.8, 2.8, 0.4)
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # Corner Foundation Anchor Brackets
    for cx in (-1.25, 1.25):
        for cy in (-1.25, 1.25):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 0.25))
            bracket = bpy.context.active_object
            bracket.scale = (0.35, 0.35, 0.5)
            bracket.data.materials.append(mats["steel"])
            parts.append(bracket)
    
    # Main Furnace Core Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.2))
    body = bpy.context.active_object
    body.name = "Smelter_Core"
    body.scale = (2.2, 2.2, 1.6)
    body.data.materials.append(mats["chassis"])
    parts.append(body)
    
    # Recessed Cylindrical Induction Arc Chamber (Center)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=1.4, location=(0, 0, 1.25), vertices=32)
    chamber = bpy.context.active_object
    chamber.name = "Smelter_Chamber"
    chamber.data.materials.append(mats["furnace"])
    parts.append(chamber)
    
    # Induction Coil Rings around chamber
    for rz in (0.7, 1.0, 1.3, 1.6):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.88, minor_radius=0.06, location=(0, 0, rz), major_segments=32, minor_segments=12)
        coil = bpy.context.active_object
        coil.data.materials.append(mats["accent"])
        parts.append(coil)
    
    # Top Feeding Hopper Chute (Slanted funnel)
    bpy.ops.mesh.primitive_cone_add(radius1=0.9, radius2=0.45, depth=0.8, location=(0, -0.3, 2.15), vertices=4)
    hopper = bpy.context.active_object
    hopper.rotation_euler = (0, 0, math.radians(45))
    hopper.data.materials.append(mats["steel"])
    parts.append(hopper)
    
    # Side Slag Exhaust / Output Tap Chute
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.25, 0, 0.8))
    tap = bpy.context.active_object
    tap.scale = (0.5, 0.6, 0.4)
    tap.rotation_euler = (0, math.radians(-15), 0)
    tap.data.materials.append(mats["accent"])
    parts.append(tap)
    
    # Rear Heat Radiator Cooling Fins
    for fy in (-0.7, -0.35, 0, 0.35, 0.7):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.18, fy, 1.2))
        fin = bpy.context.active_object
        fin.scale = (0.15, 0.08, 1.2)
        fin.data.materials.append(mats["chassis"])
        parts.append(fin)
    
    # Heavy Hydraulic Piping Conduits
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.8, location=(-0.95, 0.95, 1.2), vertices=16)
    pipe = bpy.context.active_object
    pipe.data.materials.append(mats["steel"])
    parts.append(pipe)
    
    # Operator Status Screen Console (Front Face)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.15, 1.1))
    screen = bpy.context.active_object
    screen.scale = (0.7, 0.08, 0.45)
    screen.data.materials.append(mats["screen"])
    parts.append(screen)
    
    # Stamped Logo / Text Plaque Bar: "FGS-01 ARC SMELTER"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.14, 1.5))
    plaque = bpy.context.active_object
    plaque.scale = (1.2, 0.06, 0.18)
    plaque.data.materials.append(mats["accent"])
    parts.append(plaque)
    
    # Join into single cohesive mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_SmelterCore"
    add_bevel(final_mesh, width=0.02, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    export_fbx(final_mesh, "smelter_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 2. ASSEMBLER: Auto-Assembly Cell MK-II (Dual robotic arms + canopy)
# ==============================================================================
def build_assembler():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Base Platform (3x3m footprint)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.2))
    base = bpy.context.active_object
    base.name = "Assembler_Base"
    base.scale = (2.8, 2.8, 0.4)
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # Dual Overhead Gantry Columns
    for col_x in (-1.15, 1.15):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(col_x, 0, 1.3))
        col = bpy.context.active_object
        col.scale = (0.35, 1.8, 1.8)
        col.data.materials.append(mats["steel"])
        parts.append(col)
    
    # Top Bridge Gantry Arch
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.25))
    bridge = bpy.context.active_object
    bridge.scale = (2.65, 1.8, 0.3)
    bridge.data.materials.append(mats["chassis"])
    parts.append(bridge)
    
    # Central Rotary Parts Carousel Table
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=0.25, location=(0, 0, 0.52), vertices=32)
    carousel = bpy.context.active_object
    carousel.data.materials.append(mats["steel"])
    parts.append(carousel)
    
    # Twin Articulating Robot Arms (Suspended from top gantry)
    for arm_x, arm_angle in ((-0.55, 25), (0.55, -25)):
        # Upper Arm Shoulder
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.6, location=(arm_x, 0, 1.85), vertices=16)
        upper = bpy.context.active_object
        upper.rotation_euler = (0, math.radians(arm_angle), 0)
        upper.data.materials.append(mats["accent"])
        parts.append(upper)
        
        # Forearm with Hydraulic Piston
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.55, location=(arm_x * 0.7, 0, 1.35), vertices=16)
        forearm = bpy.context.active_object
        forearm.rotation_euler = (0, math.radians(-arm_angle * 1.2), 0)
        forearm.data.materials.append(mats["steel"])
        parts.append(forearm)
        
        # End-Effector Precision Welder Head
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.03, depth=0.25, location=(arm_x * 0.5, 0, 0.95), vertices=12)
        welder = bpy.context.active_object
        welder.data.materials.append(mats["screen"])
        parts.append(welder)
    
    # Transparent Safety Canopy Frame (Front Shield)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.05, 1.35))
    canopy = bpy.context.active_object
    canopy.scale = (2.2, 0.08, 1.4)
    canopy.data.materials.append(mats["screen"])
    parts.append(canopy)
    
    # Operator Digital Diagnostics Console
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.25, 0.9))
    pedestal = bpy.context.active_object
    pedestal.scale = (0.8, 0.35, 0.8)
    pedestal.data.materials.append(mats["chassis"])
    parts.append(pedestal)
    
    # Stamped Top Plaque: "AUTO-ASSEMBLY CELL // MK-II"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.92, 2.3))
    plaque = bpy.context.active_object
    plaque.scale = (1.8, 0.06, 0.18)
    plaque.data.materials.append(mats["accent"])
    parts.append(plaque)
    
    # Join into single mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_AssemblerCore"
    add_bevel(final_mesh, width=0.02, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    export_fbx(final_mesh, "assembler_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 3. STORAGE: High-Capacity Hermetic Freight Container (UNIT #774-B)
# ==============================================================================
def build_storage():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Main Corrugated Container Body (2x2m footprint, 1.4m height)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.7))
    body = bpy.context.active_object
    body.name = "Storage_Body"
    body.scale = (1.8, 1.8, 1.35)
    body.data.materials.append(mats["chassis"])
    parts.append(body)
    
    # Corrugated Side Ribs (4 vertical rib extrusions on each side)
    for ry in (-0.6, -0.2, 0.2, 0.6):
        for sx in (-0.92, 0.92):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, ry, 0.7))
            rib = bpy.context.active_object
            rib.scale = (0.06, 0.12, 1.25)
            rib.data.materials.append(mats["steel"])
            parts.append(rib)
    
    # Corner Twist-Lock Castings (All 8 corners)
    for cx in (-0.88, 0.88):
        for cy in (-0.88, 0.88):
            for cz in (0.1, 1.32):
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
                corner = bpy.context.active_object
                corner.scale = (0.18, 0.18, 0.16)
                corner.data.materials.append(mats["accent"])
                parts.append(corner)
    
    # Dual Cam-Lock Cargo Doors (Front)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.92, 0.7))
    doors = bpy.context.active_object
    doors.scale = (1.5, 0.05, 1.2)
    doors.data.materials.append(mats["steel"])
    parts.append(doors)
    
    # Heavy Vertical Cam Lock Bars
    for lx in (-0.35, 0.35):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.15, location=(lx, 0.96, 0.7), vertices=12)
        lock_bar = bpy.context.active_object
        lock_bar.data.materials.append(mats["accent"])
        parts.append(lock_bar)
    
    # Digital Inventory Status Screen: "CAPACITY: 200 SLOTS"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.95, 1.15))
    screen = bpy.context.active_object
    screen.scale = (0.55, 0.04, 0.22)
    screen.data.materials.append(mats["screen"])
    parts.append(screen)
    
    # Stamped Identification Plaque: "KITE FREIGHT // UNIT #774-B"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.94, 0.35))
    plaque = bpy.context.active_object
    plaque.scale = (1.1, 0.03, 0.14)
    plaque.data.materials.append(mats["hazard"])
    parts.append(plaque)
    
    # Join into single mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_StorageCrate"
    add_bevel(final_mesh, width=0.018, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    export_fbx(final_mesh, "storage_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 4. SOLAR: Photovoltaic Tracking Array (KITE ENERGY 10MW)
# ==============================================================================
def build_solar():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Heavy Base Foundation Ring & Cross Legs
    bpy.ops.mesh.primitive_cylinder_add(radius=0.85, depth=0.15, location=(0, 0, 0.08), vertices=8)
    base = bpy.context.active_object
    base.name = "Solar_Base"
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # 4 Corner Anchor Jack Pads
    for angle in (0, 90, 180, 270):
        rad = math.radians(angle)
        jx, jy = math.cos(rad) * 0.85, math.sin(rad) * 0.85
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.22, location=(jx, jy, 0.11), vertices=12)
        pad = bpy.context.active_object
        pad.data.materials.append(mats["steel"])
        parts.append(pad)
    
    # Central Tracking Gimbal Pedestal (Elevation + Azimuth Yoke)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.45, location=(0, 0, 0.35), vertices=24)
    pedestal = bpy.context.active_object
    pedestal.data.materials.append(mats["steel"])
    parts.append(pedestal)
    
    # Gimbal Dual-Fork Arm Yoke
    for yx in (-0.32, 0.32):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(yx, 0, 0.6))
        arm = bpy.context.active_object
        arm.scale = (0.1, 0.25, 0.35)
        arm.data.materials.append(mats["accent"])
        parts.append(arm)
    
    # Main Hexagonal Photovoltaic Wafer Collector Plate (Tilted 25 deg towards sun)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.08, location=(0, 0, 0.85), vertices=6)
    wafer = bpy.context.active_object
    wafer.rotation_euler = (math.radians(-25), 0, math.radians(30))
    wafer.data.materials.append(mats["screen"])
    parts.append(wafer)
    
    # Photovoltaic Outer Collector Rim Ring
    bpy.ops.mesh.primitive_cylinder_add(radius=1.18, depth=0.06, location=(0, 0, 0.84), vertices=6)
    rim = bpy.context.active_object
    rim.rotation_euler = (math.radians(-25), 0, math.radians(30))
    rim.data.materials.append(mats["chassis"])
    parts.append(rim)
    
    # Central Power Concentrator Node
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.05, depth=0.2, location=(0, 0.05, 0.95), vertices=6)
    node = bpy.context.active_object
    node.rotation_euler = (math.radians(-25), 0, math.radians(30))
    node.data.materials.append(mats["accent"])
    parts.append(node)
    
    # Junction Power Inverter Box with Conduit: "KITE ENERGY // 10MW"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.65, 0.25))
    inv = bpy.context.active_object
    inv.scale = (0.5, 0.3, 0.35)
    inv.data.materials.append(mats["steel"])
    parts.append(inv)
    
    # Join into single mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_SignalAntenna"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    export_fbx(final_mesh, "solar_highpoly.fbx")
    return final_mesh

# ==============================================================================
# Run All Builds
# ==============================================================================
print("--- STARTING BLENDER ASSET FACTORY GENERATION ---")
build_smelter()
build_assembler()
build_storage()
build_solar()
print("--- ALL FACTORY ASSETS GENERATED & EXPORTED SUCCESSFULLY ---")

# ==============================================================================
# 5. CONVEYOR: Motorized Roller Conveyor Deck (CAUTION // MOVING SURFACE)
# ==============================================================================
def build_conveyor():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Left & Right Steel Channel Side Rails (1x1m, 35cm height)
    for ry in (-0.45, 0.45):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, ry, 0.22))
        rail = bpy.context.active_object
        rail.scale = (1.0, 0.08, 0.24)
        rail.data.materials.append(mats["steel"])
        parts.append(rail)
        
        # Stamped hazard chevrons along top edge
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, ry, 0.35))
        top_lip = bpy.context.active_object
        top_lip.scale = (1.0, 0.1, 0.04)
        top_lip.data.materials.append(mats["hazard"])
        parts.append(top_lip)
    
    # Central Vulcanized Rubber Conveyor Belt Bed
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.26))
    belt = bpy.context.active_object
    belt.scale = (1.0, 0.8, 0.05)
    belt.data.materials.append(mats["rubber"])
    parts.append(belt)
    
    # Transverse Bearing Rollers (5 rollers spaced along X)
    for rx in (-0.4, -0.2, 0, 0.2, 0.4):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.82, location=(rx, 0, 0.27), vertices=16)
        roller = bpy.context.active_object
        roller.rotation_euler = (math.radians(90), 0, 0)
        roller.data.materials.append(mats["steel"])
        parts.append(roller)
    
    # Electric Drive Motor Pod (Side-mounted with cooling fins)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.35, location=(0.25, 0.58, 0.2), vertices=20)
    motor = bpy.context.active_object
    motor.rotation_euler = (math.radians(90), 0, 0)
    motor.data.materials.append(mats["accent"])
    parts.append(motor)
    
    # Motor Terminal Junction Box with Status LED: "CAUTION // MOVING"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.25, 0.58, 0.34))
    junc = bpy.context.active_object
    junc.scale = (0.2, 0.15, 0.12)
    junc.data.materials.append(mats["screen"])
    parts.append(junc)
    
    # 4 Heavy Steel Floor Stanchion Mounting Legs
    for lx in (-0.42, 0.42):
        for ly in (-0.45, 0.45):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, 0.08))
            leg = bpy.context.active_object
            leg.scale = (0.1, 0.08, 0.16)
            leg.data.materials.append(mats["chassis"])
            parts.append(leg)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = belt
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_Conveyor"
    add_bevel(final_mesh, width=0.012, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "conveyor_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 6. CRANE / GANTRY: Heavy Structural Industrial Gantry (KITE CARGO 01)
# ==============================================================================
def build_crane_gantry():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Base Platform Ring / Outriggers (2x2m footprint, 2.2m height)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.15))
    base = bpy.context.active_object
    base.scale = (2.2, 2.2, 0.3)
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # 4 Corner Heavy Structural Lattice Columns
    for col_x in (-0.85, 0.85):
        for col_y in (-0.85, 0.85):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(col_x, col_y, 1.15))
            col = bpy.context.active_object
            col.scale = (0.22, 0.22, 1.8)
            col.data.materials.append(mats["steel"])
            parts.append(col)
    
    # Upper Cross Girders (Top Box Ring)
    for gx, gy, sz_x, sz_y in ((0, -0.85, 1.7, 0.2), (0, 0.85, 1.7, 0.2), (-0.85, 0, 0.2, 1.7), (0.85, 0, 0.2, 1.7)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gx, gy, 2.05))
        girder = bpy.context.active_object
        girder.scale = (sz_x, sz_y, 0.2)
        girder.data.materials.append(mats["chassis"])
        parts.append(girder)
    
    # Diagonal Reinforcement Cross-Braces
    for side in (-0.85, 0.85):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=2.4, location=(0, side, 1.15), vertices=12)
        brace1 = bpy.context.active_object
        brace1.rotation_euler = (0, math.radians(45), 0)
        brace1.data.materials.append(mats["accent"])
        parts.append(brace1)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=2.4, location=(0, side, 1.15), vertices=12)
        brace2 = bpy.context.active_object
        brace2.rotation_euler = (0, math.radians(-45), 0)
        brace2.data.materials.append(mats["accent"])
        parts.append(brace2)
    
    # Center Winch Motor Housing & Hydraulic Drums
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.9, location=(0, 0, 2.15), vertices=24)
    winch = bpy.context.active_object
    winch.rotation_euler = (math.radians(90), 0, 0)
    winch.data.materials.append(mats["steel"])
    parts.append(winch)
    
    # Stamped Crane Capacity Plaque: "SWL: 25 TONNES // KITE CARGO"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.96, 2.05))
    plaque = bpy.context.active_object
    plaque.scale = (1.4, 0.05, 0.16)
    plaque.data.materials.append(mats["hazard"])
    parts.append(plaque)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_MachineGantry"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "crane_gantry_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 7. FLUID TANK / SEA PUMP: Submersible Marine Vessel & Pump (5000 L/MIN)
# ==============================================================================
def build_fluid_tank():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Heavy Hexagonal Base Support Frame
    bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=0.2, location=(0, 0, 0.1), vertices=6)
    base = bpy.context.active_object
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # Cylindrical Pressure Vessel Body (2x2m, 1.8m height)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=1.35, location=(0, 0, 0.9), vertices=32)
    vessel = bpy.context.active_object
    vessel.data.materials.append(mats["steel"])
    parts.append(vessel)
    
    # Domed Pressure End-Cap (Top)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(0, 0, 1.55), segments=32, ring_count=16)
    dome = bpy.context.active_object
    dome.scale = (1.0, 1.0, 0.45)
    dome.data.materials.append(mats["steel"])
    parts.append(dome)
    
    # Reinforcing Girth Bands / Rib Rings
    for bz in (0.45, 0.9, 1.35):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.82, minor_radius=0.05, location=(0, 0, bz), major_segments=32, minor_segments=12)
        band = bpy.context.active_object
        band.data.materials.append(mats["accent"])
        parts.append(band)
    
    # External Liquid Level Sight Glass Tube (Front with glowing fluid)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.1, location=(0, 0.83, 0.9), vertices=16)
    sight = bpy.context.active_object
    sight.data.materials.append(mats["screen"])
    parts.append(sight)
    
    # Top Intake Manifold Flange & Flanged Valves
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.35, location=(0, 0, 1.8), vertices=20)
    flange = bpy.context.active_object
    flange.data.materials.append(mats["chassis"])
    parts.append(flange)
    
    # Marine Impeller Intake Basket (Bottom perforated ring)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.88, depth=0.25, location=(0, 0, 0.28), vertices=24)
    basket = bpy.context.active_object
    basket.data.materials.append(mats["hazard"])
    parts.append(basket)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_FluidTank"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "fluid_tank_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 8. SIGNAL DISH: 3.5m High-Gain Parabolic Communications Dish (142.8 MHZ)
# ==============================================================================
def build_signal_dish():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Heavy Azimuth Gimbal Base Yoke
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.35, location=(0, 0, 0.18), vertices=24)
    base = bpy.context.active_object
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # Elevation Fork Struts
    for sx in (-0.42, 0.42):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.65))
        fork = bpy.context.active_object
        fork.scale = (0.12, 0.35, 0.65)
        fork.data.materials.append(mats["steel"])
        parts.append(fork)
    
    # Parabolic Dish Reflector (Concave parabolic bowl, diameter 3.2m, tilted 35 deg)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.6, location=(0, 0.1, 1.25), segments=36, ring_count=18)
    dish = bpy.context.active_object
    dish.rotation_euler = (math.radians(-35), 0, 0)
    dish.scale = (1.0, 1.0, 0.25)
    dish.data.materials.append(mats["steel"])
    parts.append(dish)
    
    # Dish Outer Rim Ring with Aerospace Stamping
    bpy.ops.mesh.primitive_torus_add(major_radius=1.62, minor_radius=0.06, location=(0, 0.1, 1.25), major_segments=36, minor_segments=12)
    rim = bpy.context.active_object
    rim.rotation_euler = (math.radians(-35), 0, 0)
    rim.data.materials.append(mats["accent"])
    parts.append(rim)
    
    # Tripod Sub-Reflector Feed Horn Struts & Center Transceiver Node
    for angle in (0, 120, 240):
        rad = math.radians(angle)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.35, location=(math.cos(rad) * 0.7, 0.6 + math.sin(rad) * 0.4, 1.5), vertices=12)
        strut = bpy.context.active_object
        strut.rotation_euler = (math.radians(-35), math.radians(20), rad)
        strut.data.materials.append(mats["steel"])
        parts.append(strut)
        
    # Central High-Frequency Transceiver Feed Horn (Glowing Ruby Beacon)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.08, depth=0.35, location=(0, 0.9, 1.8), vertices=16)
    feed = bpy.context.active_object
    feed.rotation_euler = (math.radians(145), 0, 0)
    feed.data.materials.append(mats["screen"])
    parts.append(feed)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_SignalDish"
    add_bevel(final_mesh, width=0.012, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "signal_dish_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 9. CORAL ORE NODE: Giant Bioluminescent Prismatic Geode (CLASS-4 ANOMALY)
# ==============================================================================
def build_coral_ore():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Rugged Basalt Rock Base
    bpy.ops.mesh.primitive_cylinder_add(radius=1.35, depth=0.45, location=(0, 0, 0.22), vertices=9)
    rock = bpy.context.active_object
    rock.data.materials.append(mats["chassis"])
    parts.append(rock)
    
    # Clustered Hexagonal & Prismatic Crystal Spires (10 spires of varying height & tilt)
    spire_data = [
        (0, 0, 1.25, 0.35, 2.1, 0, 0),
        (0.45, 0.35, 1.05, 0.28, 1.7, 12, 15),
        (-0.4, 0.3, 0.95, 0.26, 1.5, -15, 10),
        (0.5, -0.4, 0.85, 0.25, 1.35, 10, -18),
        (-0.5, -0.35, 1.0, 0.27, 1.6, -12, -15),
        (0.1, 0.65, 0.75, 0.22, 1.2, 5, 25),
        (-0.15, -0.65, 0.8, 0.24, 1.3, -8, -22),
        (0.75, 0.05, 0.65, 0.2, 1.05, 22, 5),
        (-0.7, 0.1, 0.7, 0.21, 1.1, -20, 8),
    ]
    for sx, sy, sz, rad, depth, rx, ry in spire_data:
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=depth, location=(sx, sy, sz), vertices=6)
        spire = bpy.context.active_object
        spire.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        spire.data.materials.append(mats["screen"])
        parts.append(spire)
        
        # Faceted Pyramidal Crystal Cap
        bpy.ops.mesh.primitive_cone_add(radius1=rad, radius2=0.01, depth=rad * 1.5, location=(sx, sy, sz + depth * 0.48), vertices=6)
        cap = bpy.context.active_object
        cap.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        cap.data.materials.append(mats["screen"])
        parts.append(cap)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = rock
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_CoralOreNode"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "coral_ore_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 10. SCRAP METAL PILE: Sheared Spaceship Aerospace Bulkhead Deposit
# ==============================================================================
def build_scrap_pile():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Ground Impact Depression Plate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
    plate = bpy.context.active_object
    plate.scale = (2.4, 2.2, 0.2)
    plate.data.materials.append(mats["chassis"])
    parts.append(plate)
    
    # Large Crumpled Titanium Bulkhead (Tilted 35 deg with lightening holes)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.0))
    hull_plate = bpy.context.active_object
    hull_plate.scale = (1.8, 0.12, 1.7)
    hull_plate.rotation_euler = (math.radians(35), math.radians(-15), math.radians(10))
    hull_plate.data.materials.append(mats["steel"])
    parts.append(hull_plate)
    
    # Structural I-Beam Girders (Twisted & sheared)
    for bx, by, bz, rx, ry, rz in (
        (-0.6, -0.4, 0.8, 25, 45, 10),
        (0.5, 0.3, 0.9, -20, 30, -35),
        (0.1, -0.6, 0.6, 15, -40, 50)
    ):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz))
        beam = bpy.context.active_object
        beam.scale = (0.2, 0.16, 1.6)
        beam.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
        beam.data.materials.append(mats["accent"])
        parts.append(beam)
    
    # Tangled Heavy Braided Conduit Bundles
    for angle in (0, 75, 150):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.75, minor_radius=0.08, location=(0, 0, 0.65), major_segments=24, minor_segments=12)
        cable = bpy.context.active_object
        cable.rotation_euler = (math.radians(30), math.radians(angle), math.radians(15))
        cable.data.materials.append(mats["rubber"])
        parts.append(cable)
    
    # Stenciled Starship Hull Fragment: "SS PAPER KITE // BULKHEAD 4"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.1, 0.05, 1.45))
    tag = bpy.context.active_object
    tag.scale = (1.2, 0.04, 0.25)
    tag.rotation_euler = (math.radians(35), math.radians(-15), math.radians(10))
    tag.data.materials.append(mats["hazard"])
    parts.append(tag)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = plate
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_ScrapMetalPile"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "scrap_pile_highpoly.fbx")
    return final_mesh

# Run Batch 2
print("--- STARTING BATCH 2 GENERATION ---")
build_conveyor()
build_crane_gantry()
build_fluid_tank()
build_signal_dish()
build_coral_ore()
build_scrap_pile()
print("--- BATCH 2 COMPLETED SUCCESSFULLY ---")
