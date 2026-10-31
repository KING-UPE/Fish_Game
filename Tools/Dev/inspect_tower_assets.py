import unreal

subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

for name in ["SM_SignalDish", "SM_TowerSupport", "SM_SignalAntenna"]:
    p = f"/Game/Blue/Meshes/{name}"
    sm = unreal.load_object(None, p)
    if sm:
        bb = sm.get_bounding_box()
        sx = bb.max.x - bb.min.x
        sy = bb.max.y - bb.min.y
        sz = bb.max.z - bb.min.z
        nv = subsystem.get_number_verts(sm, 0)
        col = subsystem.get_simple_collision_count(sm)
        print(f"=== {name} ===")
        print(f"Bounds min: ({bb.min.x:.2f}, {bb.min.y:.2f}, {bb.min.z:.2f})")
        print(f"Bounds max: ({bb.max.x:.2f}, {bb.max.y:.2f}, {bb.max.z:.2f})")
        print(f"Bounds size: ({sx:.2f}, {sy:.2f}, {sz:.2f})")
        print(f"LODs: {sm.get_num_lods()}, Sections: {sm.get_num_sections(0)}, Vertices: {nv}, Collision shapes: {col}")
        for i, mat in enumerate(sm.static_materials):
            mname = mat.material_interface.get_name() if mat.material_interface else "None"
            print(f"  Slot {i} [{mat.material_slot_name}]: {mname}")
    else:
        print(f"{name}: NOT FOUND")
