import unreal

smelter = unreal.load_object(None, "/Game/Blue/Meshes/SM_SmelterCore.SM_SmelterCore")
pipe = unreal.load_object(None, "/Game/Blue/Meshes/SM_PipeCorner.SM_PipeCorner")

for name, mesh in [("SM_SmelterCore", smelter), ("SM_PipeCorner", pipe)]:
    if mesh:
        bbox = mesh.get_bounding_box()
        size = bbox.max - bbox.min
        num_mats = len(mesh.static_materials)
        # Check num vertices / triangles
        num_lods = mesh.get_num_lods()
        print(f"Mesh: {name}")
        print(f"  Bounds: min={bbox.min}, max={bbox.max}, size={size}")
        print(f"  Materials ({num_mats}): {[m.material_slot_name for m in mesh.static_materials]}")
        print(f"  Num LODs: {num_lods}")
    else:
        print(f"Mesh {name} is None!")
