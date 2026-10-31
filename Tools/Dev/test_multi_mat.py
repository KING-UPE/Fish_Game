import unreal

dm = unreal.DynamicMesh()
unreal.GeometryScript_Materials.enable_material_i_ds(dm)

po0 = unreal.GeometryScriptPrimitiveOptions()
po0.material_id = 0
unreal.GeometryScript_Primitives.append_box(
    dm, po0, unreal.Transform(location=[0, 0, 0]),
    dimension_x=50, dimension_y=50, dimension_z=50
)

po1 = unreal.GeometryScriptPrimitiveOptions()
po1.material_id = 1
unreal.GeometryScript_Primitives.append_box(
    dm, po1, unreal.Transform(location=[60, 0, 0]),
    dimension_x=50, dimension_y=50, dimension_z=50
)

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
copt = unreal.GeometryScriptCopyMeshToAssetOptions()
lod = unreal.GeometryScriptMeshWriteLOD(lod_index=0, write_hi_res_source=False)

res = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
    dm, target_asset, copt, lod, use_section_materials=False
)
print("Sections count:", target_asset.get_num_sections(0))
print("Static materials count:", len(target_asset.static_materials))
for i, m in enumerate(target_asset.static_materials):
    print(f"Slot {i}: {m.material_slot_name} = {m.material_interface.get_name() if m.material_interface else None}")
