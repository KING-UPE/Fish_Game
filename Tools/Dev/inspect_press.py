import unreal

print("--- Inspecting SM_MachineGantry ---")
gantry = unreal.load_object(None, '/Game/Blue/Meshes/SM_MachineGantry.SM_MachineGantry')
if gantry:
    bbox = gantry.get_bounding_box()
    print("Gantry bounds min:", bbox.min, "max:", bbox.max)
    print("Gantry materials:", [m.material_interface.get_name() if m.material_interface else None for m in gantry.static_materials])
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    print("Gantry vertices:", subsystem.get_number_verts(gantry, 0))
else:
    print("Gantry not found")

print("\n--- Inspecting SM_ConsoleTerminal ---")
console = unreal.load_object(None, '/Game/Blue/Meshes/SM_ConsoleTerminal.SM_ConsoleTerminal')
if console:
    bbox = console.get_bounding_box()
    print("Console bounds min:", bbox.min, "max:", bbox.max)
    print("Console materials:", [m.material_interface.get_name() if m.material_interface else None for m in console.static_materials])
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    print("Console vertices:", subsystem.get_number_verts(console, 0))
else:
    print("Console not found")
