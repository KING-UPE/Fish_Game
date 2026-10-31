import unreal
import inspect

dm = unreal.DynamicMesh()
opts = unreal.GeometryScriptPrimitiveOptions()
transform = unreal.Transform(location=[0, 0, 50], rotation=[0, 0, 0], scale=[1, 1, 1])
unreal.GeometryScript_Primitives.append_box(dm, opts, transform, 100, 100, 100)
print("Vertex count:", unreal.GeometryScript_MeshQueries.get_vertex_count(dm))
print("Triangle count:", unreal.GeometryScript_MeshQueries.get_num_triangle_i_ds(dm))

# Check copy_mesh_to_static_mesh signature / help
help_str = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh.__doc__
print("copy_mesh_to_static_mesh doc:\n", help_str)
