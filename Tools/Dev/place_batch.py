import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)

def cmd(text):
    unreal.SystemLibrary.execute_console_command(world, text, pc)

# 1. Place Smelter
cmd("FGTeleport -200 -250 145")
cmd("FGLook -25 90")
cmd("FGSelect 4")
cmd("FGClick")

# 2. Place Storage Crate
cmd("FGTeleport 200 -250 145")
cmd("FGLook -25 90")
cmd("FGSelect 7")
cmd("FGClick")

# 3. Place Solar Array
cmd("FGTeleport 0 250 145")
cmd("FGLook -25 -90")
cmd("FGSelect 1")
cmd("FGClick")

print("Machines placed on platform")
