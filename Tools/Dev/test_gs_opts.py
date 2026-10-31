import unreal

opts = unreal.GeometryScriptCopyMeshToAssetOptions()
print("opts:", opts)
for prop in ["apply_nanite_settings", "defer_mesh_post_edit_change", "enable_recompute_normals", "enable_recompute_tangents", "replace_materials"]:
    print(prop, getattr(opts, prop, None))

lod = unreal.GeometryScriptMeshWriteLOD()
print("lod:", lod)
