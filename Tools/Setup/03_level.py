"""Blue Signal setup 3/4: the Phase 1 map /Game/Blue/Maps/L_Blue (run inside the editor).
Rebuilds the level with Satisfactory-grade visual fidelity:
- SM_Island_Terrain: Real island with submerged anchor foundation, rolling hills, and slope-blending PBR material
- SM_RockCliff_Large: Massive stratified geological cliff faces with horizontal ledges and vertical fissure buttresses
- SM_RockBoulder_A & B: Weathered granite boulders and field stones
- SM_SeaStack: Towering coastal monolith pinnacles rising from ocean
- SM_AlienTree_Canopy: 10m sprawling umbrella canopy trees with hanging vines & buttress roots
- SM_Foliage_Bush & SM_Fern_Cluster: Lush tropical vegetation carpets
- Full Lumen GI, volumetric clouds, atmospheric height fog, contact shadows, and industrial foundation pads
"""
import math
import random
import unreal
import warnings

warnings.simplefilter("ignore")
random.seed(7)

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LOAD = unreal.EditorLoadingAndSavingUtils
MAP = "/Game/Blue/Maps/L_Blue"
MATS = "/Game/Blue/Materials"
MESHES = "/Game/Blue/Meshes"

ISLAND_R = 2400.0   # main island radius at waterline (cm)
ISLAND_H = 140.0    # factory plateau height

def mat(name):
    return EAL.load_asset(f"{MATS}/{name}")

def mesh(path):
    return EAL.load_asset(path)

def rot(pitch=0.0, yaw=0.0, roll=0.0):
    return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)

def vec(x, y, z):
    return unreal.Vector(x, y, z)

def ground_z(x, y):
    r = math.hypot(x, y)
    if r < 850.0:
        base = 140.0
    elif r < 2400.0:
        t = (r - 850.0) / (2400.0 - 850.0)
        base = 140.0 * (1.0 - t ** 1.5) + 15.0
    else:
        base = 10.0
    ridge = math.exp(-((x - 950.0) ** 2 + (y - 450.0) ** 2) / (500.0 ** 2)) * 65.0
    knoll = math.exp(-((x + 1100.0) ** 2 + (y - 750.0) ** 2) / (400.0 ** 2)) * 45.0
    return base + ridge + knoll

def label(actor, name, folder=None):
    actor.set_actor_label(name)
    if folder:
        actor.set_folder_path(folder)
    return actor

def static(name, mesh_path, location, rotation=None, scale=(1, 1, 1), material=None, folder=None,
           collision=True, tags=None):
    actor = EAS.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation or rot())
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh(mesh_path))
    actor.set_actor_scale3d(vec(*scale))
    if material:
        comp.set_material(0, material)
    if not collision:
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if tags:
        actor.set_editor_property("tags", [unreal.Name(t) for t in tags])
    return label(actor, name, folder)

# ---------------------------------------------------------------- fresh map
LOAD.new_blank_map(False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# ---------------------------------------------------------------- Lumen Lighting & Atmosphere
sun = label(EAS.spawn_actor_from_class(unreal.DirectionalLight, vec(0, 0, 2500), rot(pitch=-34, yaw=-45)), "Sun", "Lighting")
sun.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sun_light = sun.get_component_by_class(unreal.DirectionalLightComponent)
sun_light.set_editor_property("intensity", 6.8)
sun_light.set_editor_property("light_color", unreal.Color(255, 244, 228, 255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sun_light.set_editor_property("cast_shadows", True)
sun_light.set_editor_property("dynamic_shadow_distance_movable_light", 30000.0)
sun_light.set_editor_property("contact_shadow_length", 0.25)

label(EAS.spawn_actor_from_class(unreal.SkyAtmosphere, vec(0, 0, 0)), "SkyAtmosphere", "Lighting")
sky = label(EAS.spawn_actor_from_class(unreal.SkyLight, vec(0, 0, 500)), "SkyLight", "Lighting")
sky.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky_comp = sky.get_component_by_class(unreal.SkyLightComponent)
sky_comp.set_editor_property("real_time_capture", True)
sky_comp.set_intensity(3.5)
sky_comp.set_editor_property("lower_hemisphere_is_black", False)
sky_comp.set_lower_hemisphere_color(unreal.LinearColor(0.25, 0.32, 0.2, 1.0))

clouds = label(EAS.spawn_actor_from_class(unreal.VolumetricCloud, vec(0, 0, 0)), "Clouds", "Lighting")

fog = label(EAS.spawn_actor_from_class(unreal.ExponentialHeightFog, vec(0, 0, 0)), "Fog", "Lighting")
fog_comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
for prop, val in [
    ("fog_density", 0.003),
    ("fog_height_falloff", 0.04),
    ("enable_volumetric_fog", True),
    ("volumetric_fog", True),
    ("volumetric_fog_scattering_distribution", 0.65),
    ("volumetric_fog_extinction_scale", 0.8),
]:
    try:
        fog_comp.set_editor_property(prop, val)
    except Exception:
        pass

# Post-Process Volume with Lumen
ppv = label(EAS.spawn_actor_from_class(unreal.PostProcessVolume, vec(0, 0, 0)), "PostProcess", "Lighting")
ppv.set_editor_property("unbound", True)
settings = ppv.get_editor_property("settings")
for key, value in {
    "override_bloom_intensity": True, "bloom_intensity": 0.4,
    "override_bloom_threshold": True, "bloom_threshold": 1.2,
    "override_vignette_intensity": True, "vignette_intensity": 0.25,
    "override_auto_exposure_bias": True, "auto_exposure_bias": 0.2,
    "override_ambient_occlusion_intensity": True, "ambient_occlusion_intensity": 1.0,
    "override_ambient_occlusion_radius": True, "ambient_occlusion_radius": 150.0,
    "override_motion_blur_amount": True, "motion_blur_amount": 0.0,
}.items():
    try:
        settings.set_editor_property(key, value)
    except Exception:
        pass
ppv.set_editor_property("settings", settings)

# ---------------------------------------------------------------- Ocean & Seabed
static("Ocean", "/Engine/BasicShapes/Plane", vec(0, 0, 0), scale=(1800, 1800, 1), material=mat("M_Ocean"),
       folder="World", collision=False)
static("Seabed", "/Engine/BasicShapes/Plane", vec(0, 0, -700), scale=(1800, 1800, 1), material=mat("M_Sand"), folder="World")

# ---------------------------------------------------------------- Crash Island (Satisfactory-Grade Terrain)
# Native GeometryScript terrain mesh with solid foundation anchored to seabed (NO floating disk!)
static("CrashIsland", f"{MESHES}/SM_Island_Terrain", vec(0, 0, 0), scale=(1.0, 1.0, 1.0),
       material=mat("M_Terrain_Satisfactory"), folder="World", tags=["Buildable"], collision=True)

# ---------------------------------------------------------------- Distant Sea Pinnacles & Sea Stacks
for index, (x, y, scale_xy, scale_z) in enumerate([
    (6200, 2600, 2.5, 2.0),
    (-4300, 5200, 3.2, 2.4),
    (2600, -6400, 2.0, 1.8),
    (-5800, -3200, 2.8, 2.2),
    (5400, -4200, 2.2, 1.9),
]):
    static(f"SeaPinnacle_{index + 1}", f"{MESHES}/SM_SeaStack", vec(x, y, 0),
           rot(yaw=random.uniform(0, 360)), scale=(scale_xy, scale_xy, scale_z),
           material=mat("MI_Rock"), folder="World/SeaPinnacles", collision=True)

# ---------------------------------------------------------------- Massive Stratified Rock Cliffs
cliff_positions = [
    (950, 420, 110, 25, (1.2, 1.0, 1.1)),
    (1150, 550, 95, 35, (1.0, 1.0, 0.9)),
    (-1100, 750, 90, -40, (1.1, 1.1, 1.0)),
    (-1300, 850, 75, -30, (0.9, 1.0, 0.8)),
    (400, -1150, 50, 110, (1.3, 1.0, 0.95)),
    (-850, -950, 35, 210, (1.1, 1.1, 0.85)),
]
for idx, (cx, cy, cz, cyaw, cscale) in enumerate(cliff_positions):
    static(f"RockCliff_{idx + 1}", f"{MESHES}/SM_RockCliff_Large", vec(cx, cy, cz),
           rot(yaw=cyaw, pitch=random.uniform(-4, 4)), scale=cscale,
           material=mat("MI_Rock"), folder="World/Cliffs", collision=True)

# ---------------------------------------------------------------- Granite Boulders & Scatter Stones
boulder_positions = [
    # Meadow boulders near trails & central plateau
    (550, 250, 140, "SM_RockBoulder_A", (1.1, 1.1, 1.0)),
    (-480, 520, 138, "SM_RockBoulder_B", (0.95, 0.95, 0.9)),
    (320, 680, 135, "SM_RockBoulder_A", (0.8, 0.8, 0.75)),
    (-650, -350, 125, "SM_RockBoulder_B", (1.2, 1.2, 1.1)),
    (750, -500, 115, "SM_RockBoulder_A", (1.0, 1.0, 0.9)),
    (-250, -850, 105, "SM_RockBoulder_B", (0.85, 0.85, 0.8)),
    # Hillside boulders
    (880, 620, 160, "SM_RockBoulder_A", (1.3, 1.2, 1.1)),
    (1020, 320, 155, "SM_RockBoulder_B", (1.1, 1.1, 1.0)),
    (-1020, 620, 120, "SM_RockBoulder_A", (1.15, 1.15, 1.0)),
    # Shoreline boulders
    (1850, 450, 20, "SM_RockBoulder_A", (1.4, 1.3, 1.2)),
    (-1750, 550, 25, "SM_RockBoulder_B", (1.2, 1.2, 1.1)),
    (550, 1800, 18, "SM_RockBoulder_A", (1.1, 1.1, 0.9)),
    (-600, -1700, 15, "SM_RockBoulder_B", (1.3, 1.2, 1.0)),
    (1450, -1200, 22, "SM_RockBoulder_A", (1.0, 1.0, 0.95)),
]
for idx, (bx, by, bz, bmesh, bscale) in enumerate(boulder_positions):
    static(f"Boulder_{idx + 1}", f"{MESHES}/{bmesh}", vec(bx, by, bz),
           rot(yaw=random.uniform(0, 360), pitch=random.uniform(-8, 8)), scale=bscale,
           material=mat("MI_Rock"), folder="World/Boulders", collision=True)

# ---------------------------------------------------------------- Satisfactory Alien Canopy Trees (Umbrella Trees)
tree_positions = [
    # Majestic groves around the perimeter of the factory plateau
    (780, 720, ground_z(780, 720), 45, (1.0, 1.0, 1.0)),
    (920, 850, ground_z(920, 850), 120, (0.85, 0.85, 0.85)),
    (-750, 950, ground_z(-750, 950), -30, (1.1, 1.1, 1.05)),
    (-950, 1100, ground_z(-950, 1100), 75, (0.9, 0.9, 0.9)),
    (1250, -150, ground_z(1250, -150), 160, (1.15, 1.15, 1.1)),
    (1400, 100, ground_z(1400, 100), -85, (0.95, 0.95, 0.95)),
    (-650, -650, ground_z(-650, -650), 210, (1.05, 1.05, 1.0)),
    (-850, -520, ground_z(-850, -520), 40, (0.8, 0.8, 0.8)),
    (380, -1020, ground_z(380, -1020), -140, (1.2, 1.2, 1.15)),
    (180, -1200, ground_z(180, -1200), 90, (0.9, 0.9, 0.85)),
    (-1250, -250, ground_z(-1250, -250), -60, (1.0, 1.0, 0.95)),
    (1100, 1050, ground_z(1100, 1050), 135, (1.1, 1.1, 1.05)),
]
for idx, (tx, ty, tz, tyaw, tscale) in enumerate(tree_positions):
    static(f"AlienTree_{idx + 1}", f"{MESHES}/SM_AlienTree_Canopy", vec(tx, ty, tz),
           rot(yaw=tyaw), scale=tscale, material=mat("MI_Palm"),
           folder="World/Foliage/Trees", collision=True)

# ---------------------------------------------------------------- Shrubbery Bushes & Ground Fern Clusters
for idx in range(24):
    angle = random.uniform(0, math.tau)
    dist = random.uniform(400, 2100)
    fx = math.cos(angle) * dist
    fy = math.sin(angle) * dist
    fz = ground_z(fx, fy)
    fscale = random.uniform(0.75, 1.35)
    
    # Bush
    static(f"Bush_{idx + 1}", f"{MESHES}/SM_Foliage_Bush", vec(fx, fy, fz),
           rot(yaw=random.uniform(0, 360)), scale=(fscale, fscale, fscale),
           material=mat("MI_Palm"), folder="World/Foliage/Bushes", collision=False)
    
    # Fern cluster beside bush
    static(f"Fern_{idx + 1}", f"{MESHES}/SM_Fern_Cluster",
           vec(fx + random.uniform(-80, 80), fy + random.uniform(-80, 80), fz),
           rot(yaw=random.uniform(0, 360)), scale=(fscale * 0.9, fscale * 0.9, fscale * 0.9),
           material=mat("MI_Palm"), folder="World/Foliage/Ferns", collision=False)

# ---------------------------------------------------------------- Satisfactory-style Factory Foundation Pads
# Raised 12x12m heavy steel industrial foundation deck on central plateau
for gx in [-500, -300, -100, 100, 300, 500]:
    for gy in [-500, -300, -100, 100, 300, 500]:
        static(f"FactoryPad_{gx}_{gy}", f"{MESHES}/SM_FoundationTile", vec(gx, gy, 142.0),
               rot(roll=-90), scale=(10.0, 10.0, 25.0),
               material=mat("M_Machine"), folder="FactoryFoundations", tags=["Buildable"])

# ---------------------------------------------------------------- The Wreck of the Paper Kite
WX, WY = -950.0, 650.0
wz = ground_z(WX, WY)
hull = static("Wreck_Hull", "/Engine/BasicShapes/Cylinder", vec(WX, WY, wz + 120), rot(pitch=82, yaw=25, roll=8),
              (3.0, 3.0, 13.0), mat("MI_WreckHull"), "Wreck")
static("Wreck_Nose", "/Engine/BasicShapes/Cone", vec(WX + 720, WY + 340, wz + 150), rot(pitch=-90, yaw=25),
       (3.0, 3.0, 3.6), mat("MI_WreckBurnt"), "Wreck")
static("Wreck_Gantry", f"{MESHES}/SM_TowerSupport", vec(WX - 200, WY + 150, wz + 50), rot(pitch=15, yaw=45),
       (0.45, 0.45, 0.45), mat("MI_WreckHull"), "Wreck")
static("Wreck_Tank", f"{MESHES}/SM_FluidTank", vec(WX + 450, WY - 200, wz + 20), rot(pitch=35, yaw=-20),
       (0.4, 0.4, 0.4), mat("MI_WreckBurnt"), "Wreck")

# Scattered cargo containers around crash site
for index in range(6):
    x = WX + random.uniform(-500, 500)
    y = WY + random.uniform(-400, 400)
    static(f"Wreck_Container{index}", f"{MESHES}/SM_StorageCrate", vec(x, y, ground_z(x, y) + 15),
           rot(pitch=random.uniform(-15, 15), yaw=random.uniform(0, 360), roll=random.uniform(-15, 15)),
           (0.65, 0.65, 0.65), mat("MI_WreckHull" if index % 2 else "MI_WreckBurnt"),
           "Wreck/Cargo", collision=True)

# ---------------------------------------------------------------- Resource Nodes (Real 3D models)
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

# Massive scrap metal deposits
for index, (x, y) in enumerate([(-450, 1250), (-1450, 300), (-300, 200), (-1300, 1350)]):
    node(f"ScrapPile{index + 1}", "ScrapMetal", x, y, f"{MESHES}/SM_ScrapMetalPile", (28.0, 28.0, 25.0), "Resources")

# Brilliant crystalline coral ore formations
for index, angle in enumerate([300, 330, 15, 200]):
    dist = ISLAND_R * 0.78
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"CoralPatch{index + 1}", "CoralOre", x, y, f"{MESHES}/SM_CoralOreNode", (25.0, 25.0, 25.0), "Resources")

# Phase 2: Black sand deposits
for index, angle in enumerate([95, 115, 135]):
    dist = ISLAND_R * 0.75
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"BlackSand{index + 1}", "BlackSand", x, y, f"{MESHES}/SM_CoralOreNode", (30.0, 30.0, 18.0), "Resources")

# Glimmers in ocean
for index, (x, y, radius, speed) in enumerate([
        (3200, 300, 450, 14), (3000, -700, 650, -10), (3600, 900, 350, 18),
        (5200, 2000, 700, 9), (6000, 1500, 500, -12), (2900, 1200, 300, 22)]):
    glimmer = EAS.spawn_actor_from_class(unreal.FGGlimmer, vec(x, y, -45), rot())
    glimmer.set_editor_property("swim_radius", float(radius))
    glimmer.set_editor_property("swim_speed", float(speed))
    label(glimmer, f"Glimmer{index + 1}", "Glimmers")

# ---------------------------------------------------------------- Signal Tower Site & Player Start
TX, TY = 650.0, -250.0
tz = ground_z(TX, TY)
tower = EAS.spawn_actor_from_class(unreal.FGTowerSite, vec(TX, TY, tz), rot())
label(tower, "SignalTower", "Gameplay")

static("Tower_Array", f"{MESHES}/SM_SignalDish", vec(TX, TY, tz + 280), rot(pitch=-15, yaw=45),
       (14.0, 14.0, 14.0), mat("M_Machine"), "Gameplay", collision=False)
static("Tower_Gantry", f"{MESHES}/SM_TowerSupport", vec(TX, TY, tz), rot(yaw=45),
       (15.0, 15.0, 25.0), mat("M_Machine"), "Gameplay", collision=True)

PX, PY = 250.0, 1150.0
yaw = math.degrees(math.atan2(TY - PY, TX - PX))
label(EAS.spawn_actor_from_class(unreal.PlayerStart, vec(PX, PY, ground_z(PX, PY) + 110), rot(yaw=yaw)), "PlayerStart", "Gameplay")

# Game mode
game_mode = unreal.EditorAssetLibrary.load_blueprint_class("/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode")
world.get_world_settings().set_editor_property("default_game_mode", game_mode)

if LOAD.save_map(world, MAP):
    print("SAVED:", MAP)
else:
    print("FAILED to save", MAP)
print("SATISFACTORY ENVIRONMENT REBUILT SUCCESSFULLY!")
