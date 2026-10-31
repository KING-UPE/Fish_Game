import unreal

sm = unreal.EditorAssetLibrary.load_asset('/Game/Blue/Meshes/SM_AlienTree_Canopy')
print("SM_AlienTree_Canopy materials:")
for i, m in enumerate(sm.static_materials):
    print(f"  Slot {i}: {m.material_slot_name} -> {m.material_interface.get_name() if m.material_interface else 'None'}")

# Also check lighting actors in the level
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
for a in actors:
    if "Light" in a.get_class().get_name() or "Sky" in a.get_class().get_name() or "PostProcess" in a.get_class().get_name():
        print(f"Light actor: {a.get_name()} ({a.get_class().get_name()})")
