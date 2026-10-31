import unreal

subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

for path in ['/Game/Blue/Meshes/SM_FluidTank.SM_FluidTank', '/Game/Blue/Meshes/SM_PipeStand.SM_PipeStand']:
    mesh = unreal.load_object(None, path)
    if mesh:
        bbox = mesh.get_bounding_box()
        dx = bbox.max.x - bbox.min.x
        dy = bbox.max.y - bbox.min.y
        dz = bbox.max.z - bbox.min.z
        print(f"\n--- {path} ---")
        print(f"Bounds min: ({bbox.min.x:.1f}, {bbox.min.y:.1f}, {bbox.min.z:.1f})")
        print(f"Bounds max: ({bbox.max.x:.1f}, {bbox.max.y:.1f}, {bbox.max.z:.1f})")
        print(f"Size: ({dx:.1f}, {dy:.1f}, {dz:.1f})")
        print(f"LODs: {mesh.get_num_lods()}, Sections LOD0: {mesh.get_num_sections(0)}")
        print(f"Vertices: {subsystem.get_number_verts(mesh, 0)}")
        print(f"Collision count: {subsystem.get_simple_collision_count(mesh)}")
        print(f"Materials: {[m.material_interface.get_name() if m.material_interface else None for m in mesh.static_materials]}")
    else:
        print(f"\n--- {path} NOT FOUND ---")
