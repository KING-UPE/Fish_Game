import unreal

for name in ["SM_Scanner", "SM_ConsoleTerminal"]:
    path = f"/Game/Blue/Meshes/{name}.{name}"
    mesh = unreal.load_object(None, path)
    if mesh:
        bbox = mesh.get_bounding_box()
        ext = bbox.max - bbox.min
        min_p = bbox.min
        max_p = bbox.max
        num_lods = mesh.get_num_lods()
        num_verts = mesh.get_num_vertices(0) if num_lods > 0 else 0
        num_tris = mesh.get_num_triangles(0) if num_lods > 0 else 0
        print(f"{name}: verts={num_verts}, tris={num_tris}, size=({ext.x:.1f}, {ext.y:.1f}, {ext.z:.1f}), min=({min_p.x:.1f}, {min_p.y:.1f}, {min_p.z:.1f}), max=({max_p.x:.1f}, {max_p.y:.1f}, {max_p.z:.1f}), mats={len(mesh.static_materials)}")
        for i, sm in enumerate(mesh.static_materials):
            mat_name = sm.material_interface.get_name() if sm.material_interface else "None"
            print(f"  Slot {i}: {sm.material_slot_name} -> {mat_name}")
    else:
        print(f"Could not load {path}")
