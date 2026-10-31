import unreal

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if level_sub.is_in_play_in_editor():
    level_sub.editor_request_end_play()
    print("PIE end requested.")
else:
    print("PIE was not running.")
