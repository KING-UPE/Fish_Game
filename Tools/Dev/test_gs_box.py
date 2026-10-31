import unreal

# Test creating a DynamicMesh
dynamic_mesh = unreal.DynamicMesh()
print("DynamicMesh created:", dynamic_mesh)

# Enable material IDs
unreal.GeometryScript_Materials.enable_material_i_ds(dynamic_mesh)

# Append a box
box_opts = unreal.GeometryScriptPrimitiveOptions()
transform = unreal.Transform(location=[0, 0, 50], rotation=[0, 0, 0], scale=[1, 1, 1])
unreal.GeometryScript_Primitives.append_box(dynamic_mesh, box_opts, transform, 100, 100, 100)

num_triangles = unreal.GeometryScript_MeshQueries.get_num_triangles(dynamic_mesh)
print("Num triangles after append_box:", num_triangles)
