"""Test placing a complete production line: Smelter -> Conveyor Belt -> Storage Crate"""
import math
import sys
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if not world:
    print("NO GAME WORLD")
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

step = globals().get("STEP", "report")
print(f"FactoryLine Step: {step}")

if step == "give":
    cmd("FGSkipStory")
    for item, n in [("ScrapMetal", 500), ("SteelBar", 200), ("CoralIngot", 100), ("SteelPlate", 200), ("Wire", 200)]:
        cmd(f"FGGive {item} {n}")

elif step == "prep_smelter":
    # Stand 3m south of smelter site
    cmd("FGTeleport -150 -250 145")
    cmd("FGLook -30 90")
    cmd("FGSelect 4")

elif step == "place_smelter":
    cmd("FGClick")

elif step == "prep_storage":
    # Stand 3m south of storage site
    cmd("FGTeleport 150 -250 145")
    cmd("FGLook -30 90")
    cmd("FGSelect 7")

elif step == "place_storage":
    cmd("FGClick")

elif step == "view_line":
    # Elevated overview of the machines
    cmd("FGTeleport 0 -600 280")
    cmd("FGLook -15 90")

print("Done step:", step)
