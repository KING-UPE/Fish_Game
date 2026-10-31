import unreal

# Test how material IDs are set on DynamicMesh
dyn = unreal.DynamicMesh()
unreal.GeometryScript_Materials.enable_material_i_ds(dyn)

prim_opts = unreal.GeometryScriptPrimitiveOptions()

# Box 1
t1 = unreal.Transform(location=unreal.Vector(0, 0, 0))
dyn1 = unreal.DynamicMesh()
unreal.GeometryScript_Materials.enable_material_i_ds(dyn1)
unreal.GeometryScript_Primitives.append_box(dyn1, prim_opts, t1, 100, 100, 100)
# Set material ID 0
unreal.GeometryScript_Materials.set_all_triangle_material_i_ds(dyn1, 0)

# Box 2
dyn2 = unreal.DynamicMesh()
unreal.GeometryScript_Materials.enable_material_i_ds(dyn2)
t2 = unreal.Transform(location=unreal.Vector(0, 0, 100))
unreal.GeometryScript_Primitives.append_box(dyn2, prim_opts, t2, 50, 50, 50)
unreal.GeometryScript_Materials.set_all_triangle_material_i_ds(dyn2, 1)

# Combine dyn1 and dyn2
append_opts = unreal.GeometryScriptAppendMeshOptions()
unreal.GeometryScript_MeshEdits.append_mesh(dyn1, dyn2, unreal.Transform(), append_opts)

mids = unreal.GeometryScript_Materials.get_all_triangle_material_i_ds(dyn1)
print(f"Combined mesh has {dyn1.get_triangle_count()} triangles.")
print(f"Material IDs count: {len(mids.list)}")
distinct_mids = set(mids.list)
print(f"Distinct Material IDs: {distinct_mids}")
