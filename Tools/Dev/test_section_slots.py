import unreal

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

for s in range(5):
    subsystem.set_lod_material_slot(target_asset, 0, s, s)

for s in range(5):
    slot_idx = subsystem.get_lod_material_slot(target_asset, 0, s)
    print(f"Section {s} -> Material Slot {slot_idx}")
