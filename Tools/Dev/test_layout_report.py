"""Dev tool: during Play, print what every factory actor in the game world is doing."""
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if not world:
    print("Not in Play mode")
else:
    for cls in (unreal.FGBuildable, unreal.FGBelt):
        for actor in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
            if cls == unreal.FGBelt:
                print(f"BELT {actor.get_actor_label()}: start={actor.get_editor_property('start_actor')} "
                      f"src_ok={actor.get_editor_property('source') is not None}")
                continue
            print(f"{actor.get_class().get_name()} {actor.get_actor_label()} row={actor.get_editor_property('row_name')} "
                  f"in={dict(actor.get_editor_property('input_buffer'))} out={dict(actor.get_editor_property('output_buffer'))}")
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    print("PC", pc.get_class().get_name(), "inventory", dict(pc.get_editor_property("inventory")))
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    print("pawn at", pawn.get_actor_location() if pawn else None)
