"""Dev tool: drive Phase 2 (platform, Translator, Trade Buoy, a full Glimmer trade) during Play.
Run each STEP in its own call so the game ticks in between."""
import math
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)
pawn = unreal.GameplayStatics.get_player_pawn(world, 0)


def cmd(text):
    unreal.SystemLibrary.execute_console_command(world, text, pc)


def look_at(x, y, z):
    eye = pawn.get_actor_location() + unreal.Vector(0, 0, 60)
    dx, dy, dz = x - eye.x, y - eye.y, z - eye.z
    cmd(f"FGLook {math.degrees(math.atan2(dz, math.hypot(dx, dy))):.2f} {math.degrees(math.atan2(dy, dx)):.2f}")


def actors(cls):
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls) if not a.get_editor_property("ghost")]


def ground_z(x, y):
    return 150 * math.sqrt(max(0, 1 - (math.hypot(x, y) / 2250) ** 2))


def report(tag):
    tower = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FGTowerSite)[0]
    buoys = actors(unreal.FGTradeBuoy)
    buoy = ""
    if buoys:
        b = buoys[0]
        buoy = (f" buoy[state={b.get_editor_property('state')} want={b.get_editor_property('want_count')} "
                f"{b.get_editor_property('want_item')} delivered={b.get_editor_property('delivered')} "
                f"reward={b.get_editor_property('reward_pearls')} out={dict(b.get_editor_property('output_buffer'))}]")
    print(f"[{tag}] phase={tower.get_editor_property('current_phase')} trust={tower.get_editor_property('glimmer_trust')} "
          f"solar={len(actors(unreal.FGGenerator))} translators={len(actors(unreal.FGTranslator))} "
          f"platforms={len(actors(unreal.FGPlatform))} buoys={len(buoys)}{buoy} "
          f"pearls={ {str(k): v for k, v in pc.get_editor_property('inventory').items()}.get('GlimmerPearl', 0)}")


STEP = globals().get("STEP", "report")

if STEP == "phase2":
    cmd("FGCompletePhase")
    cmd("FGSkipStory")
    for item, n in (("Float", 40), ("SteelPlate", 80), ("Wire", 120), ("Frame", 12), ("Lens", 12),
                    ("CoralSheet", 40), ("SteelBar", 60), ("ScrapMetal", 60), ("Glass", 40)):
        cmd(f"FGGive {item} {n}")
    cmd("FGTeleport 0 500 140")
elif STEP == "solar1":
    cmd("FGLook -35 0"); cmd("FGSelect 1")
elif STEP == "solar2":
    cmd("FGClick"); cmd("FGLook -35 40")
elif STEP == "translator":
    cmd("FGClick"); cmd("FGLook -35 100"); cmd("FGSelect 18")
elif STEP == "translator_place":
    cmd("FGClick")
    report("after translator")
elif STEP == "to_shore":
    cmd(f"FGTeleport 2050 0 {ground_z(2050, 0):.0f}")
elif STEP == "platform_aim":
    cmd("FGLook -35 0"); cmd("FGSelect 17")
elif STEP == "platform_place":
    cmd("FGClick")
    report("after platform")
elif STEP == "buoy_aim":
    platform = actors(unreal.FGPlatform)[0].get_actor_location()
    look_at(platform.x, platform.y, platform.z + 20)
    cmd("FGSelect 19")
elif STEP == "buoy_place":
    cmd("FGClick")
    report("after buoy")
elif STEP == "talk_aim":
    cmd("FGSelect 19")  # put the buoy tool away (select again = deselect)
    buoy = actors(unreal.FGTradeBuoy)[0].get_actor_location()
    look_at(buoy.x, buoy.y, buoy.z + 60)
elif STEP == "talk":
    cmd("FGInteract")
elif STEP == "answer_fish":
    api = unreal.find_object(unreal.GameplayStatics.get_game_instance(world), "FGFishApiSubsystem_0")
    last = api.get_editor_property("history")[-1]
    print("picture: fish", last.fish, "chests", last.chests)
    cmd(f"FGSelect {100 + last.fish}")
elif STEP == "answer_chests":
    api = unreal.find_object(unreal.GameplayStatics.get_game_instance(world), "FGFishApiSubsystem_0")
    cmd(f"FGSelect {100 + api.get_editor_property('history')[-1].chests}")
    report("after answers")
elif STEP == "deliver":
    buoy = actors(unreal.FGTradeBuoy)[0]
    cmd(f"FGGive {buoy.get_editor_property('want_item')} {buoy.get_editor_property('want_count')}")
    cmd("FGInteract")
    report("after delivery")
elif STEP == "collect":
    cmd("FGInteract")
    report("after collect")
else:
    report("report")
