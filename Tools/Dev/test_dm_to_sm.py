import unreal

dm = unreal.DynamicMesh()
print("Created dm:", dm)
box_opts = unreal.GeometryScriptPrimitiveOptions()
transform = unreal.Transform()
unreal.GeometryScript_Primitives.append_box(dm, box_opts, transform, dimension_x=100.0, dimension_y=100.0, dimension_z=50.0)
print("DM triangle count:", dm.get_triangle_count())

# Test creating a static mesh or copying
temp_path = "/Game/Blue/Meshes/SM_TestTemp"
if unreal.EditorAssetLibrary.does_asset_exist(temp_path):
    unreal.EditorAssetLibrary.delete_asset(temp_path)

tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.StaticMeshFactoryNew()
sm = tools.create_asset("SM_TestTemp", "/Game/Blue/Meshes", unreal.StaticMesh, factory)

copy_opts = unreal.GeometryScriptCopyMeshToAssetOptions()
target_lod = unreal.GeometryScriptMeshWriteLOD()
res, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, copy_opts, target_lod)
print("Copy outcome:", outcome)

bb = sm.get_bounding_box()
print("SM bounding box:", bb.max - bb.min)

unreal.EditorAssetLibrary.delete_asset(temp_path)
print("Cleaned up temp mesh.")
