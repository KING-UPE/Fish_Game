import unreal
import time

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
key = level_sub.get_active_viewport_config_key()

# Position looking across the landscape at ground level / slight elevation
# (X=1400, Y=1400, Z=300) looking towards the center and east ridge
level_sub.set_level_viewport_camera_info(unreal.Vector(1400, 1400, 320), unreal.Rotator(roll=0, pitch=-10, yaw=-135), key)

path = 'D:/Game/FishGame/Saved/Screenshots/WindowsEditor/satisfactory_final_scenic.png'
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, path)
print('Screenshot requested:', path)
