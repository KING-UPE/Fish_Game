import unreal

dyn = unreal.DynamicMesh()
opts = unreal.GeometryScriptPrimitiveOptions()
xform = unreal.Transform()
xform.translation = unreal.Vector(0, 0, 50)
unreal.GeometryScript_Primitives.append_box(dyn, opts, xform, 100, 100, 100)

new_opts = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
new_opts.enable_nanite = True

asset_path = "/Game/Blue/Meshes/SM_TestDynMesh"
sm, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(
    dyn, asset_path, new_opts
)
print("Outcome:", outcome)
print("Created StaticMesh:", sm)
if sm:
    print("BBox:", sm.get_bounding_box())
    print("Num LODs:", sm.get_num_lods())
    print("Num Verts:", sm.get_num_vertices(0))
    unreal.EditorAssetLibrary.delete_asset(asset_path)
    print("Cleaned up successfully!")
