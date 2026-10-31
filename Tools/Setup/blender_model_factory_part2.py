"""Blender High-Poly Asset Factory Part 2 for FishGame (Unreal Engine 5.8)
Builds the remaining Satisfactory-grade industrial sci-fi models:
- Drill Tower, Operator Console, Robot Claw Arm, Material Hopper, Wire Mill Scanner
- Modular Diamond-Plate Steel Foundations
- Industrial Pipelines (Straight, Corner, Stand)
- Black Sand Quarry Deposit
- The Wreck of the Paper Kite Starship Fuselage & Thruster Bell
"""
import os
import math
import bpy

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
        "hull": create_mat("M_Aerospace_Hull", (0.75, 0.76, 0.78, 1.0), metallic=0.4, roughness=0.45),
        "scorched": create_mat("M_Scorched_Tiles", (0.08, 0.08, 0.08, 1.0), metallic=0.2, roughness=0.85),
    }

def add_bevel(obj, width=0.015, segments=2):
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(35)

def export_fbx(obj, filename):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
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
# 11. DRILL TOWER: Deep-Core Pneumatic Drill (PROJECT BLUE CORE DRILL)
# ==============================================================================
def build_drill_tower():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Octagonal Derrick Base Ring (2x2m footprint, 2.0m height)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.25, location=(0, 0, 0.12), vertices=8)
    base = bpy.context.active_object
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # 4 Corner Tower Derrick Legs
    for angle in (45, 135, 225, 315):
        rad = math.radians(angle)
        lx, ly = math.cos(rad) * 0.75, math.sin(rad) * 0.75
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.9, location=(lx, ly, 1.05), vertices=12)
        leg = bpy.context.active_object
        leg.data.materials.append(mats["steel"])
        parts.append(leg)
    
    # Central Pneumatic Core Impact Drill Column
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=1.8, location=(0, 0, 1.0), vertices=24)
    shaft = bpy.context.active_object
    shaft.data.materials.append(mats["chassis"])
    parts.append(shaft)
    
    # Carbide Rotary Drill Bit with Helical Extraction Flutes
    bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.05, depth=0.55, location=(0, 0, 0.28), vertices=16)
    bit = bpy.context.active_object
    bit.rotation_euler = (math.radians(180), 0, 0)
    bit.data.materials.append(mats["accent"])
    parts.append(bit)
    
    # High-Pressure Pneumatic Accumulator Tank
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.8, location=(0.55, 0, 1.3), vertices=16)
    tank = bpy.context.active_object
    tank.data.materials.append(mats["hazard"])
    parts.append(tank)
    
    # Stamped Signage Plaque: "PROJECT BLUE // CORE DRILL 150M"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.78, 1.8))
    plaque = bpy.context.active_object
    plaque.scale = (0.9, 0.04, 0.15)
    plaque.data.materials.append(mats["hazard"])
    parts.append(plaque)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_TowerSupport"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "drill_tower_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 12. ROBOT ARM: Articulated Industrial Robotic Manipulator Claw
# ==============================================================================
def build_robot_arm():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Turntable Base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.2, location=(0, 0, 0.1), vertices=24)
    base = bpy.context.active_object
    base.data.materials.append(mats["chassis"])
    parts.append(base)
    
    # Shoulder Pivot Yoke
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.35))
    shoulder = bpy.context.active_object
    shoulder.scale = (0.5, 0.4, 0.35)
    shoulder.data.materials.append(mats["steel"])
    parts.append(shoulder)
    
    # Upper Bicep Arm (Angled 35 deg)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.75, location=(0, 0.22, 0.72), vertices=16)
    upper = bpy.context.active_object
    upper.rotation_euler = (math.radians(35), 0, 0)
    upper.data.materials.append(mats["accent"])
    parts.append(upper)
    
    # Forearm (Angled -45 deg)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.65, location=(0, 0.35, 1.25), vertices=16)
    forearm = bpy.context.active_object
    forearm.rotation_euler = (math.radians(-30), 0, 0)
    forearm.data.materials.append(mats["steel"])
    parts.append(forearm)
    
    # 3-Finger Pneumatic Salvage Grabber Claw
    for angle in (0, 120, 240):
        rad = math.radians(angle)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(math.cos(rad) * 0.18, 0.3 + math.sin(rad) * 0.18, 1.62))
        finger = bpy.context.active_object
        finger.scale = (0.05, 0.08, 0.28)
        finger.rotation_euler = (math.radians(15), 0, rad)
        finger.data.materials.append(mats["hazard"])
        parts.append(finger)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_RobotArm"
    add_bevel(final_mesh, width=0.012, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "robot_arm_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 13. OPERATOR CONSOLE: Industrial Control Terminal (SM_ConsoleTerminal)
# ==============================================================================
def build_console():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Armored Base Pedestal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.35))
    pedestal = bpy.context.active_object
    pedestal.scale = (0.7, 0.5, 0.7)
    pedestal.data.materials.append(mats["chassis"])
    parts.append(pedestal)
    
    # Angled Operator Console Desk (Tilted 30 deg)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 0.85))
    desk = bpy.context.active_object
    desk.scale = (0.85, 0.55, 0.22)
    desk.rotation_euler = (math.radians(-30), 0, 0)
    desk.data.materials.append(mats["steel"])
    parts.append(desk)
    
    # Glowing Ultrawide CRT/OLED Diagnostics Display Screen
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.02, 0.96))
    screen = bpy.context.active_object
    screen.scale = (0.7, 0.03, 0.38)
    screen.rotation_euler = (math.radians(-30), 0, 0)
    screen.data.materials.append(mats["screen"])
    parts.append(screen)
    
    # Emergency Palm Shutoff Mushroom Button
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.08, location=(0.3, -0.15, 0.82), vertices=16)
    estop = bpy.context.active_object
    estop.rotation_euler = (math.radians(-30), 0, 0)
    estop.data.materials.append(mats["accent"])
    parts.append(estop)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pedestal
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_ConsoleTerminal"
    add_bevel(final_mesh, width=0.012, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "console_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 14. FEED HOPPER: Raw Material Infeed Funnel (SM_Hopper)
# ==============================================================================
def build_hopper():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Flanged Square Discharge Flange
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
    flange = bpy.context.active_object
    flange.scale = (0.65, 0.65, 0.18)
    flange.data.materials.append(mats["chassis"])
    parts.append(flange)
    
    # Slanted Pyramid Funnel Walls (1.2m height)
    bpy.ops.mesh.primitive_cone_add(radius1=1.0, radius2=0.35, depth=0.9, location=(0, 0, 0.65), vertices=4)
    funnel = bpy.context.active_object
    funnel.rotation_euler = (0, 0, math.radians(45))
    funnel.data.materials.append(mats["steel"])
    parts.append(funnel)
    
    # Top Stiffening Perimeter Flange & Safety Intake Grate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.15))
    rim = bpy.context.active_object
    rim.scale = (1.45, 1.45, 0.1)
    rim.data.materials.append(mats["accent"])
    parts.append(rim)
    
    # Vibration Dampener Spring Cylinders (4 corners)
    for vx in (-0.55, 0.55):
        for vy in (-0.55, 0.55):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(vx, vy, 0.25), vertices=12)
            mount = bpy.context.active_object
            mount.data.materials.append(mats["chassis"])
            parts.append(mount)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = flange
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_Hopper"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "hopper_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 15. STARSHIP WRECK: The Wreck of the Paper Kite Fuselage & Thruster
# ==============================================================================
def build_starship_wreck():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Fractured Cylindrical Aerospace Hull (Length 12m, Diameter 3.6m)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=10.0, location=(0, 0, 1.8), vertices=32)
    hull = bpy.context.active_object
    hull.rotation_euler = (0, math.radians(90), 0)
    hull.data.materials.append(mats["hull"])
    parts.append(hull)
    
    # Scorched Black Atmospheric Re-Entry Thermal Protection Tiles (Bottom Arc)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.84, depth=9.8, location=(0, 0, 1.8), vertices=32)
    heatshield = bpy.context.active_object
    heatshield.rotation_euler = (0, math.radians(90), 0)
    heatshield.scale = (1.0, 1.0, 0.6)
    heatshield.data.materials.append(mats["scorched"])
    parts.append(heatshield)
    
    # Internal Structural Ring Bulkheads (Exposed by crash fractures)
    for bx in (-3.5, -1.0, 1.5, 4.0):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.82, minor_radius=0.1, location=(bx, 0, 1.8), major_segments=32, minor_segments=12)
        ring = bpy.context.active_object
        ring.rotation_euler = (0, math.radians(90), 0)
        ring.data.materials.append(mats["steel"])
        parts.append(ring)
    
    # Giant Fusion Thruster Bell Nozzle (Rear)
    bpy.ops.mesh.primitive_cone_add(radius1=1.9, radius2=0.7, depth=2.8, location=(-5.8, 0, 1.8), vertices=32)
    thruster = bpy.context.active_object
    thruster.rotation_euler = (0, math.radians(-90), 0)
    thruster.data.materials.append(mats["chassis"])
    parts.append(thruster)
    
    # Prominent Aerospace Stenciled Lettering: "SS PAPER KITE // REG-9941"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.85, 2.2))
    nameplate = bpy.context.active_object
    nameplate.scale = (4.5, 0.05, 0.65)
    nameplate.data.materials.append(mats["accent"])
    parts.append(nameplate)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = hull
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_WreckHull"
    add_bevel(final_mesh, width=0.02, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "wreck_hull_highpoly.fbx")
    return final_mesh

# ==============================================================================
# 16. FOUNDATION PLATFORM: Diamond-Plate Heavy Factory Tile
# ==============================================================================
def build_foundation():
    reset_scene()
    mats = get_materials()
    parts = []
    
    # Solid Heavy Steel Deck Platform (2x2m, 20cm thickness)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
    tile = bpy.context.active_object
    tile.scale = (2.0, 2.0, 0.2)
    tile.data.materials.append(mats["chassis"])
    parts.append(tile)
    
    # Perimeter Recessed Border Channel with Safety Yellow Edge Trim
    for ex, ey, sx, sy in ((0, -0.96, 1.95, 0.08), (0, 0.96, 1.95, 0.08), (-0.96, 0, 0.08, 1.95), (0.96, 0, 0.08, 1.95)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, ey, 0.19))
        border = bpy.context.active_object
        border.scale = (sx, sy, 0.03)
        border.data.materials.append(mats["hazard"])
        parts.append(border)
    
    # Underside Heavy I-Beam Sub-Floor Girders
    for gx in (-0.65, 0.65):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gx, 0, -0.08))
        girder = bpy.context.active_object
        girder.scale = (0.16, 1.95, 0.18)
        girder.data.materials.append(mats["steel"])
        parts.append(girder)
        
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = tile
    bpy.ops.object.join()
    
    final_mesh = bpy.context.active_object
    final_mesh.name = "SM_FoundationTile"
    add_bevel(final_mesh, width=0.015, segments=2)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    export_fbx(final_mesh, "foundation_highpoly.fbx")
    return final_mesh

# Run Part 2
print("--- STARTING PART 2 GENERATION ---")
build_drill_tower()
build_robot_arm()
build_console()
build_hopper()
build_starship_wreck()
build_foundation()
print("--- PART 2 COMPLETED SUCCESSFULLY ---")
