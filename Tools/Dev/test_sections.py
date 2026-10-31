import unreal

dm = unreal.DynamicMesh()
unreal.GeometryScript_Materials.enable_material_i_ds(dm)

for i in range(5):
    po = unreal.GeometryScriptPrimitiveOptions()
    po.material_id = i
    unreal.GeometryScript_Primitives.append_box(
        dm, po, unreal.Transform(location=[i * 20, 0, 0]),
        dimension_x=15, dimension_y=15, dimension_z=15
    )

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
copt = unreal.GeometryScriptCopyMeshToAssetOptions()
lod = unreal.GeometryScriptMeshWriteLOD(lod_index=0, write_hi_res_source=False)

unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
    dm, target_asset, copt, lod, use_section_materials=False
)

print("Number of sections in LOD 0:", target_asset.get_num_sections(0))
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for s in range(target_asset.get_num_sections(0)):
    slot_idx = subsystem.get_lod_material_slot(target_asset, 0, s)
    print(f"Section {s} -> Material Slot {slot_idx}")
