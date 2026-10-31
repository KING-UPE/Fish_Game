import math
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)
pawn = unreal.GameplayStatics.get_player_pawn(world, 0)

def cmd(text):
    unreal.SystemLibrary.execute_console_command(world, text, pc)

# Give ample resources
cmd("FGSkipStory")
for item, n in [
    ("ScrapMetal", 1000), ("SteelBar", 500), ("CoralIngot", 300),
    ("SteelPlate", 500), ("Wire", 500), ("Glass", 300), ("CoralSheet", 300)
]:
    cmd(f"FGGive {item} {n}")

# Stand on factory platform
cmd("FGTeleport 0 0 150")
cmd("FGLook -25 90")
print("Player stationed on factory platform")
