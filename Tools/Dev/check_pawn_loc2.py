import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if world:
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    print("pc:", pc)
    if pc:
        print("pc pawn:", pc.get_player_pawn(0) if hasattr(pc, "get_player_pawn") else None)
        pawn = pc.get_pawn()
        print("pc.get_pawn():", pawn)
        if pawn:
            print("loc:", pawn.get_actor_location())
