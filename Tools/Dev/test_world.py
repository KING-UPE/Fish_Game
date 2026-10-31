import unreal

sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = sub.get_editor_world()
print("Editor world:", world.get_path_name() if world else "None")
