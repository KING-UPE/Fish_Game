import unreal

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
m_machine = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")
m_belt = unreal.load_object(None, "/Game/Blue/Materials/M_Belt.M_Belt")

# Let's see how many static materials there are, or how to add static material slots
print("Current static materials:", len(target_asset.static_materials))

# In UE, StaticMesh.set_material(index, material)
target_asset.set_material(0, m_machine)
# If index 1 does not exist, can we add a slot or does static_materials list need updating?
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print("Subsystem methods:", [m for m in dir(subsystem) if "material" in m.lower()])

try:
    target_asset.set_material(1, m_belt)
    print("set_material(1) succeeded!")
except Exception as e:
    print("set_material(1) failed:", e)

print("Static materials after set_material:", len(target_asset.static_materials))
for i, m in enumerate(target_asset.static_materials):
    print(f"Slot {i}: {m.material_slot_name} = {m.material_interface.get_name() if m.material_interface else None}")
