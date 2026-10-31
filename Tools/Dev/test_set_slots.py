import unreal

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
m_machine = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")
m_belt = unreal.load_object(None, "/Game/Blue/Materials/M_Belt.M_Belt")

sm0 = unreal.StaticMaterial(material_interface=m_machine, material_slot_name="MainBody")
sm1 = unreal.StaticMaterial(material_interface=m_belt, material_slot_name="Trim")

target_asset.set_editor_property("static_materials", [sm0, sm1])
unreal.EditorAssetLibrary.save_loaded_asset(target_asset)

print("Updated static materials count:", len(target_asset.static_materials))
for i, m in enumerate(target_asset.static_materials):
    print(f"Slot {i}: {m.material_slot_name} = {m.material_interface.get_name() if m.material_interface else None}")
