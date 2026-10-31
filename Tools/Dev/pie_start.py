import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_game_world()
if world is None:
    print("Requesting begin play...")
    les.editor_request_begin_play()
    print("Requested begin play.")
else:
    print("Already in play mode:", world.get_name())
