import unreal

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print("is_in_pie:", level_sub.is_in_play_in_editor())

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if world:
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    print("Found PlayerController:", pc)
    
    # Teleport to an elevated meadow vantage point looking across trees, cliffs and factory
    unreal.SystemLibrary.execute_console_command(world, "FGTeleport 1100 900 230", pc)
    unreal.SystemLibrary.execute_console_command(world, "FGLook -10 -140", pc)
    
    path = "D:/Game/FishGame/Saved/Screenshots/WindowsEditor/satisfactory_ground_panoramic.png"
    task = unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, path)
    print("Screenshot triggered:", path)
else:
    print("Game world not available yet")
