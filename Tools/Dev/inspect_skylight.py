import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "SkyLight":
        c = a.get_component_by_class(unreal.SkyLightComponent)
        for p in dir(c):
            if "lower" in p.lower() or "hemi" in p.lower() or "color" in p.lower() or "intensity" in p.lower():
                print("  ", p)
