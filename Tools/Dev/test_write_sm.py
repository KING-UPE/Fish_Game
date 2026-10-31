import unreal

dm = unreal.DynamicMesh()
po = unreal.GeometryScriptPrimitiveOptions()
unreal.GeometryScript_Primitives.append_box(
    dm, po, unreal.Transform(),
    dimension_x=200.0, dimension_y=200.0, dimension_z=140.0,
    origin=unreal.GeometryScriptPrimitiveOriginMode.BASE
)

print("Triangles:", dm.get_triangle_count())

target_asset = unreal.load_object(None, "/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate")
copt = unreal.GeometryScriptCopyMeshToAssetOptions()
lod = unreal.GeometryScriptMeshWriteLOD(lod_index=0, write_hi_res_source=False)

res = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
    dm, target_asset, copt, lod, use_section_materials=False
)
print("Copy result:", res)
unreal.EditorAssetLibrary.save_loaded_asset(target_asset)
bbox = target_asset.get_bounding_box()
print("New bounds min:", bbox.min, "max:", bbox.max)
