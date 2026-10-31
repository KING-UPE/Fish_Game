import unreal

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
print("static_materials length:", len(target_asset.static_materials))
for i, m in enumerate(target_asset.static_materials):
    print(i, m.material_slot_name, m.material_interface)

for s in range(target_asset.get_num_sections(0)):
    print(f"target_asset.get_material({s}):", target_asset.get_material(s))
