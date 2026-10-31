import unreal

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
print("UES methods:", [m for m in dir(ues) if "play" in m.lower() or "pie" in m.lower()])
print("LevelEditorSubsystem methods:", [m for m in dir(unreal.LevelEditorSubsystem) if "play" in m.lower() or "pie" in m.lower()])
