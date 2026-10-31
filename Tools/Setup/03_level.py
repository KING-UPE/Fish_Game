"""Blue Signal setup 3/4: the Phase 1 map /Game/Blue/Maps/L_Blue (run inside the editor).
Rebuilds the level with Satisfactory-grade visual fidelity:
Lumen GI, contact shadows, atmospheric volumetric lighting, PBR foundation pads,
and real 3D sci-fi models for all resources and structures."""
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

ISLAND_R = 2250.0   # main island radius at the waterline (cm)
ISLAND_H = 150.0    # dome height at the centre


def mat(name):
    return EAL.load_asset(f"{MATS}/{name}")


def mesh(path):
    return EAL.load_asset(path)


def rot(pitch=0.0, yaw=0.0, roll=0.0):
    return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)


def vec(x, y, z):
    return unreal.Vector(x, y, z)


def ground_z(x, y, r_island=ISLAND_R, h=ISLAND_H, cx=0.0, cy=0.0):
    r = math.hypot(x - cx, y - cy)
    return h * math.sqrt(max(0.0, 1.0 - (r / r_island) ** 2))


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


# ---------------------------------------------------------------- island mesh with real collision
DOME = f"{MESHES}/SM_IslandDome"
if not EAL.does_asset_exist(DOME):
    EAL.duplicate_asset("/Engine/BasicShapes/Sphere", DOME)
dome = EAL.load_asset(DOME) or unreal.load_object(None, f"{DOME}.SM_IslandDome")
body = dome.get_editor_property("body_setup")
body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
SMES = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
SMES.set_convex_decomposition_collisions(dome, 1, 128, 400000)
EAL.save_asset(DOME)

# ---------------------------------------------------------------- fresh map
LOAD.new_blank_map(False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# ---------------------------------------------------------------- Lumen Lighting & Atmosphere
sun = label(EAS.spawn_actor_from_class(unreal.DirectionalLight, vec(0, 0, 2500), rot(pitch=-32, yaw=-42)), "Sun", "Lighting")
sun.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sun_light = sun.get_component_by_class(unreal.DirectionalLightComponent)
sun_light.set_editor_property("intensity", 6.5)
sun_light.set_editor_property("light_color", unreal.Color(255, 242, 225, 255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sun_light.set_editor_property("cast_shadows", True)
sun_light.set_editor_property("dynamic_shadow_distance_movable_light", 25000.0)
sun_light.set_editor_property("contact_shadow_length", 0.2)

label(EAS.spawn_actor_from_class(unreal.SkyAtmosphere, vec(0, 0, 0)), "SkyAtmosphere", "Lighting")
sky = label(EAS.spawn_actor_from_class(unreal.SkyLight, vec(0, 0, 500)), "SkyLight", "Lighting")
sky.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky_comp = sky.get_component_by_class(unreal.SkyLightComponent)
sky_comp.set_editor_property("real_time_capture", True)

clouds = label(EAS.spawn_actor_from_class(unreal.VolumetricCloud, vec(0, 0, 0)), "Clouds", "Lighting")

fog = label(EAS.spawn_actor_from_class(unreal.ExponentialHeightFog, vec(0, 0, 0)), "Fog", "Lighting")
fog_comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
for prop, val in [
    ("fog_density", 0.0035),
    ("fog_height_falloff", 0.05),
    ("enable_volumetric_fog", True),
    ("volumetric_fog", True),
    ("volumetric_fog_scattering_distribution", 0.65),
    ("volumetric_fog_extinction_scale", 0.8),
]:
    try:
        fog_comp.set_editor_property(prop, val)
    except Exception as exc:
        pass

# Post-Process with Lumen & Tone Mapping
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
    except Exception as exc:
        print("  WARN post process", key, exc)
ppv.set_editor_property("settings", settings)

# ---------------------------------------------------------------- Ocean & Seabed
static("Ocean", "/Engine/BasicShapes/Plane", vec(0, 0, 0), scale=(1800, 1800, 1), material=mat("M_Ocean"),
       folder="World", collision=False)
static("Seabed", "/Engine/BasicShapes/Plane", vec(0, 0, -700), scale=(1800, 1800, 1), material=mat("M_Sand"), folder="World")

# ---------------------------------------------------------------- Islands
static("CrashIsland", DOME, vec(0, 0, 0), scale=(ISLAND_R / 50, ISLAND_R / 50, ISLAND_H / 50),
       material=mat("M_Sand"), folder="World", tags=["Buildable"])
for index, (x, y, r, h) in enumerate([(6200, 2600, 1300, 110), (-4300, 5200, 1700, 130), (2600, -6400, 1000, 90)]):
    static(f"FarIsland{index + 1}", DOME, vec(x, y, 0), scale=(r / 50, r / 50, h / 50),
           material=mat("M_Sand"), folder="World", tags=["Buildable"])

# ---------------------------------------------------------------- Satisfactory-style Factory Foundation Pads
# Raised 12x12m heavy steel industrial foundation deck with sub-floor supports
for gx in [-500, -300, -100, 100, 300, 500]:
    for gy in [-500, -300, -100, 100, 300, 500]:
        static(f"FactoryPad_{gx}_{gy}", f"{MESHES}/SM_FoundationTile", vec(gx, gy, 140.0),
               rot(roll=-90), scale=(10.0, 10.0, 25.0),
               material=mat("M_Machine"), folder="FactoryFoundations", tags=["Buildable"])

# Shoreline rock detail using real 3D crystal ore meshes
for index in range(12):
    angle = random.uniform(0, math.tau)
    dist = random.uniform(ISLAND_R * 0.95, ISLAND_R * 1.08)
    size = random.uniform(0.35, 0.75)
    x, y = math.cos(angle) * dist, math.sin(angle) * dist
    static(f"ShoreRock{index}", f"{MESHES}/SM_CoralOreNode", vec(x, y, -20),
           rot(pitch=random.uniform(-10, 10), yaw=random.uniform(0, 360)),
           (size, size, size * 0.8), mat("MI_Rock"), "World/Rocks", collision=True)

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

# Scattered cargo containers & debris around the crash site
for index in range(6):
    x = WX + random.uniform(-600, 600)
    y = WY + random.uniform(-500, 500)
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
    node(f"BlackSand{index + 1}", "BlackSand", x, y, f"{MESHES}/SM_CoralOreNode", (30.0, 30.0, 18.0), "Resources")

# Glimmers
for index, (x, y, radius, speed) in enumerate([
        (3200, 300, 450, 14), (3000, -700, 650, -10), (3600, 900, 350, 18),
        (5200, 2000, 700, 9), (6000, 1500, 500, -12), (2900, 1200, 300, 22)]):
    glimmer = EAS.spawn_actor_from_class(unreal.FGGlimmer, vec(x, y, -45), rot())
    glimmer.set_editor_property("swim_radius", float(radius))
    glimmer.set_editor_property("swim_speed", float(speed))
    label(glimmer, f"Glimmer{index + 1}", "Glimmers")

# ---------------------------------------------------------------- Signal Tower Site & Player Start
TX, TY = 650.0, -250.0
tower = EAS.spawn_actor_from_class(unreal.FGTowerSite, vec(TX, TY, ground_z(TX, TY)), rot())
label(tower, "SignalTower", "Gameplay")

# Decorative tower base gantry & massive communication array
static("Tower_Array", f"{MESHES}/SM_SignalDish", vec(TX, TY, ground_z(TX, TY) + 280), rot(pitch=-15, yaw=45),
       (14.0, 14.0, 14.0), mat("M_Machine"), "Gameplay", collision=False)
static("Tower_Gantry", f"{MESHES}/SM_TowerSupport", vec(TX, TY, ground_z(TX, TY)), rot(yaw=45),
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
print("LEVEL REBUILT WITH SATISFACTORY GRAPHICS!")
