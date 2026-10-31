import unreal
import time

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

if not level_sub.is_in_play_in_editor():
    print("Starting PIE...")
    level_sub.editor_request_begin_play()
    print("PIE start requested.")
else:
    print("PIE already active.")
