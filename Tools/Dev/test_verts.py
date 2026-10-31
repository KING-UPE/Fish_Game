import unreal

sm = unreal.load_object(None, '/Game/Blue/Meshes/SM_SmelterCore.SM_SmelterCore')
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

print("SM_SmelterCore:")
print("  num LODs:", sm.get_num_lods())
print("  num sections LOD0:", sm.get_num_sections(0))
print("  bounds:", sm.get_bounding_box())
for fn in dir(subsystem):
    if "vert" in fn.lower() or "poly" in fn.lower() or "tri" in fn.lower() or "count" in fn.lower() or "lod" in fn.lower():
        print("  subsystem fn:", fn)

try:
    print("  verts via get_number_verts:", subsystem.get_number_verts(sm, 0))
except Exception as e:
    print("  verts error:", e)

try:
    print("  LOD0 vertex count:", sm.get_num_vertices(0))
except Exception as e:
    print("  get_num_vertices error:", e)
