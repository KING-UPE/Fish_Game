import unreal

dyn_mesh = unreal.DynamicMesh()
prim_opts = unreal.GeometryScriptPrimitiveOptions()

xform = unreal.Transform()
xform.translation = unreal.Vector(0, 0, 50)
unreal.GeometryScript_Primitives.append_box(dyn_mesh, prim_opts, xform, 100, 100, 100)

print("Dynamic mesh poly count:", dyn_mesh.get_triangle_count())

# Test saving to static mesh
copy_opts = unreal.GeometryScriptCopyMeshToAssetOptions()
lod = unreal.GeometryScriptMeshWriteLOD()

sm_path = "/Game/Blue/Meshes/SM_TestDyn"
eal = unreal.EditorAssetLibrary
if not eal.does_asset_exist(sm_path):
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.StaticMeshFactoryNew()
    sm = tools.create_asset("SM_TestDyn", "/Game/Blue/Meshes", unreal.StaticMesh, factory)
else:
    sm = eal.load_asset(sm_path)

res = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dyn_mesh, sm, copy_opts, lod)
print("Copy result:", res)
sm = eal.load_asset(sm_path)
print("LODs:", sm.get_num_lods())
print("Vertices:", sm.get_num_vertices(0))
print("BBox:", sm.get_bounding_box())
eal.delete_asset(sm_path)
