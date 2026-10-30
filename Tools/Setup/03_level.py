"""Blue Signal setup 3/4: the Phase 1 map /Game/Blue/Maps/L_Blue (run inside the editor).
Rebuilds the level from scratch: sky + lighting, ocean, crash-site island, wreck, resource nodes,
Signal Tower site, player start, a few distant islands."""
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


# ---------------------------------------------------------------- island mesh with real (complex) collision
DOME = "/Game/Blue/Meshes/SM_IslandDome"
if not EAL.does_asset_exist(DOME):
    EAL.duplicate_asset("/Engine/BasicShapes/Sphere", DOME)
    print("CREATED:", DOME)
dome = EAL.load_asset(DOME)
# The dome is convex, so one convex hull scales correctly with the squashed island
# (the sphere's own simple collision can't scale non-uniformly, players fell through).
body = dome.get_editor_property("body_setup")
body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
SMES = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
SMES.set_convex_decomposition_collisions(dome, 1, 128, 400000)
print("DOME collision hulls:", SMES.get_convex_collision_count(dome))
EAL.save_asset(DOME)

# ---------------------------------------------------------------- fresh map
LOAD.new_blank_map(False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# ---------------------------------------------------------------- sky and light
sun = label(EAS.spawn_actor_from_class(unreal.DirectionalLight, vec(0, 0, 2000), rot(pitch=-28, yaw=-35)), "Sun", "Lighting")
sun.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sun_light = sun.get_component_by_class(unreal.DirectionalLightComponent)
sun_light.set_editor_property("intensity", 9.0)
sun_light.set_editor_property("light_color", unreal.Color(255, 236, 210, 255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sun_light.set_editor_property("cast_shadows", True)

label(EAS.spawn_actor_from_class(unreal.SkyAtmosphere, vec(0, 0, 0)), "SkyAtmosphere", "Lighting")
sky = label(EAS.spawn_actor_from_class(unreal.SkyLight, vec(0, 0, 500)), "SkyLight", "Lighting")
sky.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky_comp = sky.get_component_by_class(unreal.SkyLightComponent)
sky_comp.set_editor_property("real_time_capture", True)
label(EAS.spawn_actor_from_class(unreal.VolumetricCloud, vec(0, 0, 0)), "Clouds", "Lighting")
fog = label(EAS.spawn_actor_from_class(unreal.ExponentialHeightFog, vec(0, 0, 0)), "Fog", "Lighting")
fog_comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
fog_comp.set_editor_property("fog_density", 0.006)
fog_comp.set_editor_property("fog_height_falloff", 0.08)

ppv = label(EAS.spawn_actor_from_class(unreal.PostProcessVolume, vec(0, 0, 0)), "PostProcess", "Lighting")
ppv.set_editor_property("unbound", True)
settings = ppv.get_editor_property("settings")
for key, value in {
    "override_bloom_intensity": True, "bloom_intensity": 0.55,
    "override_vignette_intensity": True, "vignette_intensity": 0.35,
    "override_auto_exposure_bias": True, "auto_exposure_bias": 0.4,
}.items():
    try:
        settings.set_editor_property(key, value)
    except Exception as exc:
        print("  WARN post process", key, exc)
ppv.set_editor_property("settings", settings)

# ---------------------------------------------------------------- ocean
static("Ocean", "/Engine/BasicShapes/Plane", vec(0, 0, 0), scale=(1500, 1500, 1), material=mat("M_Ocean"),
       folder="World", collision=False)
# Visible sandy seabed: gives the shallows their colour and catches anyone who falls in.
static("Seabed", "/Engine/BasicShapes/Plane", vec(0, 0, -700), scale=(1500, 1500, 1), material=mat("M_Sand"), folder="World")

# ---------------------------------------------------------------- islands
static("CrashIsland", DOME, vec(0, 0, 0), scale=(ISLAND_R / 50, ISLAND_R / 50, ISLAND_H / 50),
       material=mat("M_Sand"), folder="World", tags=["Buildable"])
for index, (x, y, r, h) in enumerate([(6200, 2600, 1300, 110), (-4300, 5200, 1700, 130), (2600, -6400, 1000, 90)]):
    static(f"FarIsland{index + 1}", DOME, vec(x, y, 0), scale=(r / 50, r / 50, h / 50),
           material=mat("M_Sand"), folder="World", tags=["Buildable"])

# Rocks around the shore (decor, no collision).
for index in range(14):
    angle = random.uniform(0, math.tau)
    dist = random.uniform(ISLAND_R * 0.92, ISLAND_R * 1.12)
    size = random.uniform(90, 260)
    x, y = math.cos(angle) * dist, math.sin(angle) * dist
    static(f"Rock{index}", "/Engine/BasicShapes/Sphere", vec(x, y, -size * 0.2),
           rot(pitch=random.uniform(-20, 20), yaw=random.uniform(0, 360)),
           (size / 50 * random.uniform(0.8, 1.4), size / 50, size / 50 * random.uniform(0.5, 0.9)),
           mat("MI_Rock"), "World/Rocks", collision=False)

# Palm trees (trunk + three leaf blades).
for index, (x, y) in enumerate([(1500, 1300), (-1700, -900), (300, -1850), (1750, -500), (-600, 1850)]):
    z = ground_z(x, y)
    lean = random.uniform(6, 14)
    yaw = random.uniform(0, 360)
    static(f"PalmTrunk{index}", "/Engine/BasicShapes/Cylinder", vec(x, y, z + 220), rot(pitch=lean, yaw=yaw),
           (0.22, 0.22, 4.6), mat("MI_Trunk"), "World/Palms")
    top = vec(x + math.cos(math.radians(yaw)) * lean * 8, y + math.sin(math.radians(yaw)) * lean * 8, z + 450)
    for leaf in range(5):
        static(f"PalmLeaf{index}_{leaf}", "/Engine/BasicShapes/Cube", top,
               rot(pitch=-25, yaw=leaf * 72 + yaw), (2.6, 0.55, 0.05), mat("MI_Palm"), "World/Palms", collision=False)

# ---------------------------------------------------------------- the wreck of the Paper Kite
WX, WY = -950.0, 650.0
wz = ground_z(WX, WY)
hull = static("Wreck_Hull", "/Engine/BasicShapes/Cylinder", vec(WX, WY, wz + 120), rot(pitch=82, yaw=25, roll=8),
              (3.0, 3.0, 13.0), mat("MI_WreckHull"), "Wreck")
static("Wreck_Nose", "/Engine/BasicShapes/Cone", vec(WX + 720, WY + 340, wz + 150), rot(pitch=-90, yaw=25),
       (3.0, 3.0, 3.6), mat("MI_WreckBurnt"), "Wreck")
static("Wreck_Stripe", "/Engine/BasicShapes/Cylinder", vec(WX + 150, WY + 70, wz + 130), rot(pitch=82, yaw=25, roll=8),
       (3.08, 3.08, 0.8), mat("MI_WreckStripe"), "Wreck")
static("Wreck_WingL", "/Engine/BasicShapes/Cube", vec(WX - 80, WY + 380, wz + 40), rot(pitch=4, yaw=25, roll=-18),
       (3.2, 6.5, 0.18), mat("MI_WreckHull"), "Wreck")
static("Wreck_WingR", "/Engine/BasicShapes/Cube", vec(WX + 260, WY - 420, wz + 15), rot(pitch=-6, yaw=40, roll=24),
       (2.6, 4.0, 0.18), mat("MI_WreckBurnt"), "Wreck")
static("Wreck_Engine", "/Engine/BasicShapes/Cylinder", vec(WX - 640, WY - 290, wz + 110), rot(pitch=86, yaw=25),
       (1.7, 1.7, 2.8), mat("MI_WreckHull"), "Wreck")
static("Wreck_EngineGlow", "/Engine/BasicShapes/Cylinder", vec(WX - 770, WY - 350, wz + 112), rot(pitch=86, yaw=25),
       (1.35, 1.35, 0.4), mat("MI_EngineGlow"), "Wreck", collision=False)
for index in range(9):
    x = WX + random.uniform(-900, 700)
    y = WY + random.uniform(-700, 700)
    static(f"Wreck_Panel{index}", "/Engine/BasicShapes/Cube", vec(x, y, ground_z(x, y) + 10),
           rot(pitch=random.uniform(-25, 25), yaw=random.uniform(0, 360), roll=random.uniform(-25, 25)),
           (random.uniform(0.6, 1.6), random.uniform(0.4, 1.2), 0.08), mat("MI_WreckBurnt" if index % 2 else "MI_WreckHull"),
           "Wreck/Debris", collision=False)

# ---------------------------------------------------------------- resource nodes
def node(name, item, x, y, mesh_path, scale, folder):
    z = ground_z(x, y)
    actor = EAS.spawn_actor_from_class(unreal.FGResourceNode, vec(x, y, z + scale[2] * 40),
                                       rot(yaw=random.uniform(0, 360), roll=random.uniform(-8, 8)))
    actor.set_editor_property("item", unreal.Name(item))
    comp = actor.get_editor_property("mesh")
    comp.set_static_mesh(mesh(mesh_path))
    comp.set_collision_profile_name("BlockAllDynamic")
    actor.set_actor_scale3d(vec(*scale))
    return label(actor, name, folder)


for index, (x, y) in enumerate([(-450, 1250), (-1500, 300), (-300, 200), (-1300, 1350)]):
    node(f"ScrapPile{index + 1}", "ScrapMetal", x, y, "/Game/LevelPrototyping/Meshes/SM_ChamferCube", (0.9, 0.75, 0.55), "Resources")
for index, angle in enumerate([300, 330, 15, 200]):
    dist = ISLAND_R * 0.82
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"CoralPatch{index + 1}", "CoralOre", x, y, "/Engine/BasicShapes/Cone", (0.9, 0.9, 0.9), "Resources")

# Phase 2: black sand on the north beach.
for index, angle in enumerate([95, 115, 135]):
    dist = ISLAND_R * 0.8
    x, y = math.cos(math.radians(angle)) * dist, math.sin(math.radians(angle)) * dist
    node(f"BlackSand{index + 1}", "BlackSand", x, y, "/Engine/BasicShapes/Sphere", (1.6, 1.6, 0.35), "Resources")

# Phase 2: the Glimmers, circling just under the surface east of the island and near the far island.
for index, (x, y, radius, speed) in enumerate([
        (3200, 300, 450, 14), (3000, -700, 650, -10), (3600, 900, 350, 18),
        (5200, 2000, 700, 9), (6000, 1500, 500, -12), (2900, 1200, 300, 22)]):
    glimmer = EAS.spawn_actor_from_class(unreal.FGGlimmer, vec(x, y, -45), rot())
    glimmer.set_editor_property("swim_radius", float(radius))
    glimmer.set_editor_property("swim_speed", float(speed))
    label(glimmer, f"Glimmer{index + 1}", "Glimmers")

# ---------------------------------------------------------------- Signal Tower site and player start
TX, TY = 650.0, -250.0
tower = EAS.spawn_actor_from_class(unreal.FGTowerSite, vec(TX, TY, ground_z(TX, TY)), rot())
label(tower, "SignalTower", "Gameplay")

PX, PY = 250.0, 1150.0   # open sand between the wreck and the tower
yaw = math.degrees(math.atan2(TY - PY, TX - PX))
label(EAS.spawn_actor_from_class(unreal.PlayerStart, vec(PX, PY, ground_z(PX, PY) + 110), rot(yaw=yaw)), "PlayerStart", "Gameplay")

# ---------------------------------------------------------------- game mode + save
game_mode = unreal.EditorAssetLibrary.load_blueprint_class("/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode")
world.get_world_settings().set_editor_property("default_game_mode", game_mode)

if LOAD.save_map(world, MAP):
    print("SAVED:", MAP)
else:
    print("FAILED to save", MAP)
print("LEVEL DONE")
