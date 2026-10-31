import unreal

for name in ["SM_FoundationTile", "SM_SignalAntenna"]:
    p = f"/Game/Blue/Meshes/{name}.{name}"
    mesh = unreal.load_object(None, p)
    if mesh:
        bb = mesh.get_bounding_box()
        size = bb.max - bb.min
        print(f"Asset {name}: bounds=({size.x:.1f}, {size.y:.1f}, {size.z:.1f}), min=({bb.min.x:.1f}, {bb.min.y:.1f}, {bb.min.z:.1f}), max=({bb.max.x:.1f}, {bb.max.y:.1f}, {bb.max.z:.1f}), mats={len(mesh.static_materials)}")
        for i, m in enumerate(mesh.static_materials):
            mat_name = m.material_interface.get_name() if m.material_interface else "None"
            print(f"  Slot {i}: {m.material_slot_name} -> {mat_name}")
    else:
        print(f"Asset {name} NOT FOUND!")
