import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()

sky_comp = None
for a in actors:
    if a.get_actor_label() == "SkyLight":
        sky_comp = a.get_component_by_class(unreal.SkyLightComponent)
        break

if sky_comp:
    sky_comp.set_intensity(3.5)
    sky_comp.set_editor_property("lower_hemisphere_is_black", False)
    sky_comp.set_lower_hemisphere_color(unreal.LinearColor(0.25, 0.32, 0.2, 1.0))
    sky_comp.recapture_sky()
    print("Updated SkyLight: intensity=3.5, lower_hemisphere_is_black=False, warm ambient bounce set!")

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_game_world() or ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "r.Lumen.DiffuseIndirect.Allow 1")
unreal.SystemLibrary.execute_console_command(world, "r.DynamicGlobalIlluminationMethod 1")
print("Lumen Diffuse Indirect re-enabled")
