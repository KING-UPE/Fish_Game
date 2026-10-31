import unreal

# Test creating DynamicMesh
dyn_mesh = unreal.DynamicMesh()
prim_opts = unreal.GeometryScriptPrimitiveOptions()
prim_opts.polygroup_mode = unreal.GeometryScriptPrimitivePolygroupMode.PER_FACE

# Add a box
box_transform = unreal.Transform()
unreal.GeometryScript_Primitives.append_box(
    dyn_mesh,
    prim_opts,
    box_transform,
    dimension_x=100.0,
    dimension_y=100.0,
    dimension_z=100.0
)

tri_count = dyn_mesh.get_triangle_count()
print(f"Test box created with {tri_count} triangles.")
