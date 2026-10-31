import unreal
sm = unreal.load_object(None, '/Game/Blue/Meshes/SM_StorageCrate.SM_StorageCrate')
if sm:
    bbox = sm.get_bounding_box()
    print('Bounds min:', bbox.min, 'max:', bbox.max)
    print('Num LODs:', sm.get_num_lods())
    print('Num sections:', sm.get_num_sections(0))
    print('Materials:', [m.material_interface.get_name() if m.material_interface else None for m in sm.static_materials])
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    print('Vertices:', subsystem.get_number_verts(sm, 0))
    print('Collision count:', subsystem.get_simple_collision_count(sm))
else:
    print('Mesh not found')
