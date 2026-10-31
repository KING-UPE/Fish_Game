import unreal

for name in ["SM_FoundationTile", "SM_FluidTank"]:
    sm = unreal.load_object(None, f'/Game/Blue/Meshes/{name}.{name}')
    if sm:
        bb = sm.get_bounding_box()
        ext = bb.max - bb.min
        subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        verts = subsystem.get_number_verts(sm, 0)
        mats = [m.material_interface.get_name() if m.material_interface else "None" for m in sm.static_materials]
        print(f"{name}: size=({ext.x:.1f}, {ext.y:.1f}, {ext.z:.1f}), min=({bb.min.x:.1f}, {bb.min.y:.1f}, {bb.min.z:.1f}), max=({bb.max.x:.1f}, {bb.max.y:.1f}, {bb.max.z:.1f}), verts={verts}, mats={mats}")
    else:
        print(f"Could not load {name}")
