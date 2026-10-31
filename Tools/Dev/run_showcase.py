"""Execute showcase step in PIE"""
import sys
import math
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if not world:
    print("NO GAME WORLD - PIE is not running!")
    sys.exit(1)

pc = unreal.GameplayStatics.get_player_controller(world, 0)
pawn = unreal.GameplayStatics.get_player_pawn(world, 0)

def cmd(text):
    unreal.SystemLibrary.execute_console_command(world, text, pc)

def look_at(x, y, z):
    eye = pawn.get_actor_location() + unreal.Vector(0, 0, 60)
    dx, dy, dz = x - eye.x, y - eye.y, z - eye.z
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    cmd(f"FGLook {pitch:.2f} {yaw:.2f}")

def count(cls):
    return len(unreal.GameplayStatics.get_all_actors_of_class(world, cls))

def report(tag):
    print(f"[{tag}] generators={count(unreal.FGGenerator)} machines={count(unreal.FGMachine)} "
          f"extractors={count(unreal.FGExtractor)} belts={count(unreal.FGBelt)} "
          f"storage={count(unreal.FGStorage)} loc={pawn.get_actor_location()}")

step = globals().get("STEP", "report")
if len(sys.argv) > 2:
    step = sys.argv[2]
print(f"Executing step: {step}")

if step == "init":
    cmd("FGSkipStory")
    for item, n in [
        ("ScrapMetal", 500), ("SteelBar", 200), ("CoralIngot", 100),
        ("SteelPlate", 200), ("Wire", 200), ("Glass", 100), ("CoralSheet", 100)
    ]:
        cmd(f"FGGive {item} {n}")
    # Teleport to foundation pad area
    cmd("FGTeleport 0 0 145")
    report("init")

elif step == "aim_solar":
    cmd("FGLook -25 0")
    cmd("FGSelect 1")

elif step == "place_solar":
    cmd("FGClick")
    report("after_solar")

elif step == "aim_smelter":
    cmd("FGLook -25 90")
    cmd("FGSelect 4")

elif step == "place_smelter":
    cmd("FGClick")
    report("after_smelter")

elif step == "aim_assembler":
    cmd("FGLook -25 180")
    cmd("FGSelect 12")

elif step == "place_assembler":
    cmd("FGClick")
    report("after_assembler")

elif step == "aim_storage":
    cmd("FGLook -25 270")
    cmd("FGSelect 7")

elif step == "place_storage":
    cmd("FGClick")
    report("after_storage")

elif step == "crane_setup":
    nodes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FGResourceNode)
    target = None
    for n in nodes:
        if "ScrapPile" in n.get_actor_label():
            target = n
            break
    if target:
        loc = target.get_actor_location()
        cmd(f"FGTeleport {loc.x - 300:.0f} {loc.y:.0f} {loc.z:.0f}")
        look_at(loc.x, loc.y, loc.z - 30)
        cmd("FGSelect 2")
        print(f"Teleported near node {target.get_actor_label()} at {loc}")

elif step == "crane_place":
    cmd("FGClick")
    report("after_crane")

elif step == "view_pan":
    # Teleport to an elevated scenic overlook
    cmd("FGTeleport 0 -500 300")
    cmd("FGLook -20 90")
    report("view_pan")

else:
    report("status")
