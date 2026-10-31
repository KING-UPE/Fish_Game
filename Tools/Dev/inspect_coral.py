import unreal
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_CoralOreNode")
if sm:
    bb = sm.get_bounding_box()
    sx = bb.max.x - bb.min.x
    sy = bb.max.y - bb.min.y
    sz = bb.max.z - bb.min.z
    nv = subsystem.get_number_verts(sm, 0)
    col = subsystem.get_simple_collision_count(sm)
    print(f"SM_CoralOreNode:")
    print(f"  Bounds: min=({bb.min.x:.1f}, {bb.min.y:.1f}, {bb.min.z:.1f}), max=({bb.max.x:.1f}, {bb.max.y:.1f}, {bb.max.z:.1f})")
    print(f"  Size: ({sx:.1f}, {sy:.1f}, {sz:.1f})")
    print(f"  Num LODs: {sm.get_num_lods()}, Sections: {sm.get_num_sections(0)}, Vertices: {nv}, Collision: {col}")
    for i, mat in enumerate(sm.static_materials):
        mname = mat.material_interface.get_name() if mat.material_interface else "None"
        print(f"  Slot {i} [{mat.material_slot_name}]: {mname}")
else:
    print("SM_CoralOreNode NOT FOUND")

eal = unreal.EditorAssetLibrary
mats = eal.list_assets("/Game/Blue/Materials", recursive=True)
print("\nMaterials in /Game/Blue/Materials:")
for m in sorted(mats):
    print(" ", m)
