import re

# 1. Update 01_materials.py
with open("Tools/Setup/01_materials.py", "r", encoding="utf-8") as f:
    text = f.read()

# Normalize
text = text.replace("\r\n", "\n")

# Replace M_Belt lerp logic
old_belt = """lerp = expr(m, unreal.MaterialExpressionLinearInterpolate, -150, 60)
link(const(m, 0.55, -320, 0), "", lerp, "A")
link(const(m, 1.0, -320, 40), "", lerp, "B")
link(rnd, "", lerp, "Alpha")
out(mul(m, color, "", lerp, "", 50, -100), "", MP.MP_BASE_COLOR)
out(const(m, 0.75, 50, 100), "", MP.MP_ROUGHNESS)"""

new_belt = """lerp = expr(m, unreal.MaterialExpressionLinearInterpolate, -150, 60)
link(const3(m, (0.1, 0.11, 0.13), -320, 0), "", lerp, "A")
link(const3(m, (0.95, 0.65, 0.05), -320, 40), "", lerp, "B")
link(rnd, "", lerp, "Alpha")
out(lerp, "", MP.MP_BASE_COLOR)
out(mul(m, rnd, "", const3(m, (0.4, 0.25, 0.02), -300, 180), "", 50, 150), "", MP.MP_EMISSIVE_COLOR)
out(const(m, 0.45, 50, 100), "", MP.MP_ROUGHNESS)"""

if old_belt in text:
    text = text.replace(old_belt, new_belt)
    print("M_Belt replaced")
else:
    print("M_Belt target not found")

# Replace M_Sand logic
old_sand = """# ---------------------------------------------------------------- M_Sand: warm sand with soft noise variation
m = material("M_Sand")
world = expr(m, unreal.MaterialExpressionWorldPosition, -1000, 0)
noise = expr(m, unreal.MaterialExpressionNoise, -800, 0, scale=0.004, levels=4, output_min=0.0, output_max=1.0)
link(world, "", noise, "World Position")
sand = expr(m, unreal.MaterialExpressionLinearInterpolate, -500, 0)
link(const3(m, (0.62, 0.52, 0.36), -800, -200), "", sand, "A")
link(const3(m, (0.82, 0.72, 0.53), -800, -120), "", sand, "B")
link(noise, "", sand, "Alpha")
out(sand, "", MP.MP_BASE_COLOR)
out(const(m, 0.9, -500, 200), "", MP.MP_ROUGHNESS)
finish(m)"""

new_sand = """# ---------------------------------------------------------------- M_Sand: warm golden sand with wet shoreline gradient & noise
m = material("M_Sand")
world = expr(m, unreal.MaterialExpressionWorldPosition, -1200, 0)
noise = expr(m, unreal.MaterialExpressionNoise, -800, 0, scale=0.003, levels=4, output_min=0.0, output_max=1.0)
link(world, "", noise, "World Position")

dry_sand = expr(m, unreal.MaterialExpressionLinearInterpolate, -550, -100)
link(const3(m, (0.70, 0.58, 0.38), -800, -240), "", dry_sand, "A")
link(const3(m, (0.86, 0.74, 0.52), -800, -160), "", dry_sand, "B")
link(noise, "", dry_sand, "Alpha")

wet_sand = const3(m, (0.28, 0.22, 0.14), -550, -250)

# Shoreline wetness mask from world Z
z_mask = expr(m, unreal.MaterialExpressionComponentMask, -1000, 200, r=False, g=False, b=True, a=False)
link(world, "", z_mask, "")
z_div = expr(m, unreal.MaterialExpressionDivide, -800, 200)
link(z_mask, "", z_div, "A")
link(const(m, 35.0, -1000, 280), "", z_div, "B")
z_clamp = expr(m, unreal.MaterialExpressionClamp, -650, 200, min_default=0.0, max_default=1.0)
link(z_div, "", z_clamp, "")

sand_final = expr(m, unreal.MaterialExpressionLinearInterpolate, -300, -50)
link(wet_sand, "", sand_final, "A")
link(dry_sand, "", sand_final, "B")
link(z_clamp, "", sand_final, "Alpha")

roughness = expr(m, unreal.MaterialExpressionLinearInterpolate, -300, 150)
link(const(m, 0.18, -500, 120), "", roughness, "A")
link(const(m, 0.88, -500, 180), "", roughness, "B")
link(z_clamp, "", roughness, "Alpha")

out(sand_final, "", MP.MP_BASE_COLOR)
out(roughness, "", MP.MP_ROUGHNESS)
out(const(m, 0.05, -100, 250), "", MP.MP_SPECULAR)
finish(m)"""

if old_sand in text:
    text = text.replace(old_sand, new_sand)
    print("M_Sand replaced")
else:
    print("M_Sand target not found")

with open("Tools/Setup/01_materials.py", "w", encoding="utf-8") as f:
    f.write(text)


# 2. Update 03_level.py
with open("Tools/Setup/03_level.py", "r", encoding="utf-8") as f:
    lvl = f.read()

lvl = lvl.replace("\r\n", "\n")

# Upgrade foundations to seamless 6x6 industrial grid
old_foundations = """# ---------------------------------------------------------------- Satisfactory-style Factory Foundation Pads
# Clean 20x20m steel foundations around the player starting construction area
for fx, fy in [(0, 0), (200, 0), (-200, 0), (0, 200), (200, 200), (-200, 200)]:
    fz = ground_z(fx, fy) + 2.0
    static(f"FactoryPad_{fx}_{fy}", f"{MESHES}/SM_FoundationTile", vec(fx, fy, fz),
           scale=(0.1, 0.1, 0.1), material=mat("M_Machine"), folder="FactoryFoundations", tags=["Buildable"])"""

new_foundations = """# ---------------------------------------------------------------- Satisfactory-style Factory Foundation Pads
# Raised 12x12m heavy steel industrial foundation deck with sub-floor supports
for gx in [-500, -300, -100, 100, 300, 500]:
    for gy in [-500, -300, -100, 100, 300, 500]:
        static(f"FactoryPad_{gx}_{gy}", f"{MESHES}/SM_FoundationTile", vec(gx, gy, 140.0),
               rot(pitch=-90, yaw=0, roll=0), scale=(10.0, 10.0, 25.0),
               material=mat("M_Machine"), folder="FactoryFoundations", tags=["Buildable"])"""

if old_foundations in lvl:
    lvl = lvl.replace(old_foundations, new_foundations)
    print("Foundations replaced")
else:
    print("Foundations target not found")

# Upgrade resource node scaling and Wreck details
old_node = """# ---------------------------------------------------------------- Resource Nodes (Real 3D models)
def node(name, item, x, y, mesh_path, scale, folder):
    z = ground_z(x, y)
    actor = EAS.spawn_actor_from_class(unreal.FGResourceNode, vec(x, y, z + scale[2] * 20),
                                       rot(yaw=random.uniform(0, 360)))
    actor.set_editor_property("item", unreal.Name(item))
    comp = actor.get_editor_property("mesh")
    comp.set_static_mesh(mesh(mesh_path))
    comp.set_collision_profile_name("BlockAllDynamic")
    actor.set_actor_scale3d(vec(*scale))
    return label(actor, name, folder)


# Scrap metal resource deposits
for index, (x, y) in enumerate([(-450, 1250), (-1500, 300), (-300, 200), (-1300, 1350)]):
    node(f"ScrapPile{index + 1}", "ScrapMetal", x, y, f"{MESHES}/SM_ScrapMetalPile", (0.55, 0.55, 0.55), "Resources")

# Coral ore crystalline nodes
for index, angle in enumerate([300, 330, 15, 200]):
    dist = ISLAND_R * 0.82
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"CoralPatch{index + 1}", "CoralOre", x, y, f"{MESHES}/SM_CoralOreNode", (0.55, 0.55, 0.55), "Resources")

# Phase 2: Black sand deposits
for index, angle in enumerate([95, 115, 135]):
    dist = ISLAND_R * 0.8
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"BlackSand{index + 1}", "BlackSand", x, y, f"{MESHES}/SM_CoralOreNode", (0.7, 0.7, 0.35), "Resources")"""

new_node = """# ---------------------------------------------------------------- Resource Nodes (Real 3D models)
def node(name, item, x, y, mesh_path, scale, folder):
    z = ground_z(x, y)
    actor = EAS.spawn_actor_from_class(unreal.FGResourceNode, vec(x, y, z + 5.0),
                                       rot(yaw=random.uniform(0, 360)))
    actor.set_editor_property("item", unreal.Name(item))
    comp = actor.get_editor_property("mesh")
    comp.set_static_mesh(mesh(mesh_path))
    comp.set_collision_profile_name("BlockAllDynamic")
    actor.set_actor_scale3d(vec(*scale))
    return label(actor, name, folder)


# Massive 2.5m scrap metal deposits with industrial debris
for index, (x, y) in enumerate([(-450, 1250), (-1500, 300), (-300, 200), (-1300, 1350)]):
    node(f"ScrapPile{index + 1}", "ScrapMetal", x, y, f"{MESHES}/SM_ScrapMetalPile", (28.0, 28.0, 25.0), "Resources")

# Brilliant 2.5m crystalline coral ore formations
for index, angle in enumerate([300, 330, 15, 200]):
    dist = ISLAND_R * 0.82
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"CoralPatch{index + 1}", "CoralOre", x, y, f"{MESHES}/SM_CoralOreNode", (25.0, 25.0, 25.0), "Resources")

# Phase 2: Black sand deposits
for index, angle in enumerate([95, 115, 135]):
    dist = ISLAND_R * 0.8
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"BlackSand{index + 1}", "BlackSand", x, y, f"{MESHES}/SM_CoralOreNode", (30.0, 30.0, 18.0), "Resources")"""

if old_node in lvl:
    lvl = lvl.replace(old_node, new_node)
    print("Resource nodes replaced")
else:
    print("Resource nodes target not found")

# Upgrade Signal Tower array and Wreck models
old_tower = """# Decorative tower base gantry & communication array
static("Tower_Array", f"{MESHES}/SM_SignalDish", vec(TX, TY, ground_z(TX, TY) + 280), rot(pitch=-15, yaw=45),
       (0.5, 0.5, 0.5), mat("M_Machine"), "Gameplay", collision=False)"""

new_tower = """# Decorative tower base gantry & massive communication array
static("Tower_Array", f"{MESHES}/SM_SignalDish", vec(TX, TY, ground_z(TX, TY) + 280), rot(pitch=-15, yaw=45),
       (14.0, 14.0, 14.0), mat("M_Machine"), "Gameplay", collision=False)
static("Tower_Gantry", f"{MESHES}/SM_TowerSupport", vec(TX, TY, ground_z(TX, TY)), rot(yaw=45),
       (15.0, 15.0, 25.0), mat("M_Machine"), "Gameplay", collision=True)"""

if old_tower in lvl:
    lvl = lvl.replace(old_tower, new_tower)
    print("Tower replaced")
else:
    print("Tower target not found")

with open("Tools/Setup/03_level.py", "w", encoding="utf-8") as f:
    f.write(lvl)

print("Update script completed successfully!")
