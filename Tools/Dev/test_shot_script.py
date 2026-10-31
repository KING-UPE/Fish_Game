import unreal

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
key = level_sub.get_active_viewport_config_key()
print("active key:", key)
cam_info = level_sub.get_level_viewport_camera_info(key)
print("cam info:", cam_info)

level_sub.set_level_viewport_camera_info(unreal.Vector(1500, 1600, 380), unreal.Rotator(roll=0, pitch=-8, yaw=-138), key)
task = unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "D:/Game/FishGame/Saved/Screenshots/WindowsEditor/test_shot.png")
print("task:", task, "is_task_done:", task.is_task_done() if task else None)
