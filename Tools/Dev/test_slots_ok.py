import unreal

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
m_machine = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")

slots = [
    unreal.StaticMaterial(material_interface=m_machine, material_slot_name=f"Slot_{i}")
    for i in range(5)
]
target_asset.set_editor_property("static_materials", slots)

dm = unreal.DynamicMesh()
unreal.GeometryScript_Materials.enable_material_i_ds(dm)
for i in range(5):
    po = unreal.GeometryScriptPrimitiveOptions()
    po.material_id = i
    unreal.GeometryScript_Primitives.append_box(
        dm, po, unreal.Transform(location=[i * 20, 0, 0]),
        dimension_x=15, dimension_y=15, dimension_z=15
    )

copt = unreal.GeometryScriptCopyMeshToAssetOptions()
lod = unreal.GeometryScriptMeshWriteLOD(lod_index=0, write_hi_res_source=False)
unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
    dm, target_asset, copt, lod, use_section_materials=True
)
unreal.EditorAssetLibrary.save_loaded_asset(target_asset)

subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print("Sections count:", target_asset.get_num_sections(0))
for s in range(target_asset.get_num_sections(0)):
    slot_idx = subsystem.get_lod_material_slot(target_asset, 0, s)
    mat = target_asset.get_material(slot_idx) if slot_idx >= 0 else None
    print(f"Section {s} -> Slot {slot_idx} ({slots[s].material_slot_name}) = {mat.get_name() if mat else None}")
