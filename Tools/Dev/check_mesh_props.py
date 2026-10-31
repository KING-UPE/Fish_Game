import unreal

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_SignalDish")
print("Num LODs:", sm.get_num_lods())
print("Num sections LOD0:", sm.get_num_sections(0))
print("StaticMesh properties:")
for p in ["nanite_settings"]:
    print(" ", p, sm.get_editor_property(p).get_editor_property("enabled"))
