import unreal

def inspect(name):
    path = f"/Game/Blue/Meshes/{name}.{name}"
    mesh = unreal.load_object(None, path)
    print(f"\n=== Inspecting {name} ({path}) ===")
    if not mesh:
        print("  Asset NOT FOUND!")
        return
    bb = mesh.get_bounding_box()
    size = bb.max - bb.min
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    num_verts = subsystem.get_number_verts(mesh, 0)
    print(f"  Bounds Min: ({bb.min.x:.2f}, {bb.min.y:.2f}, {bb.min.z:.2f})")
    print(f"  Bounds Max: ({bb.max.x:.2f}, {bb.max.y:.2f}, {bb.max.z:.2f})")
    print(f"  Bounds Size: ({size.x:.2f}, {size.y:.2f}, {size.z:.2f})")
    print(f"  Num Vertices (LOD0): {num_verts}")
    print(f"  Material slots: {len(mesh.static_materials)}")
    for i, m in enumerate(mesh.static_materials):
        mat_name = m.material_interface.get_path_name() if m.material_interface else "None"
        print(f"    Slot {i} [{m.material_slot_name}]: {mat_name}")
    col_count = subsystem.get_simple_collision_count(mesh)
    print(f"  Simple collision count: {col_count}")

inspect("SM_FluidTank")
inspect("SM_PipeStraight")
