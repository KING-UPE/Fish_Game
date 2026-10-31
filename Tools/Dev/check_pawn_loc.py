import unreal

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print("in pie:", level_sub.is_in_play_in_editor())
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if world:
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    print("pawn location:", pawn.get_actor_location() if pawn else None)
