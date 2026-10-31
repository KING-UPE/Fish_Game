import unreal

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_ScrapMetalPile.SM_ScrapMetalPile")
if sm:
    bbox = sm.get_bounding_box()
    dx = bbox.max.x - bbox.min.x
    dy = bbox.max.y - bbox.min.y
    dz = bbox.max.z - bbox.min.z
    print(f"SM_ScrapMetalPile exists: min={bbox.min}, max={bbox.max}, size=({dx:.1f}, {dy:.1f}, {dz:.1f})")
    print(f"Num materials: {len(sm.static_materials)}")
    for i, mat in enumerate(sm.static_materials):
        print(f"  Slot {i}: {mat.material_slot_name} -> {mat.material_interface.get_name() if mat.material_interface else 'None'}")
    num_verts = sm.get_num_vertices(0)
    num_tris = sm.get_num_triangles(0)
    print(f"LOD 0 Vertices: {num_verts}, Triangles: {num_tris}")
else:
    print("SM_ScrapMetalPile not found")
