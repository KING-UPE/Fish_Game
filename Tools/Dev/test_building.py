"""Dev tool: drive the real build/interact code during Play through the FG* console commands.
Usage (Play mode running): python ue.py with STEP set, e.g. exec(open(...).read()) after defining STEP.
Each step must run in its own call so the game ticks in between (camera, ghost, timers)."""
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
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    cmd(f"FGLook {pitch:.2f} {yaw:.2f}")


def count(cls):
    return len(unreal.GameplayStatics.get_all_actors_of_class(world, cls))


def report(tag):
    print(f"[{tag}] generators={count(unreal.FGGenerator)} machines={count(unreal.FGMachine)} "
          f"extractors={count(unreal.FGExtractor)} belts={count(unreal.FGBelt)} "
          f"inventory={dict(pc.get_editor_property('inventory'))} slot={pc.get_editor_property('selected_slot')}")


def node(label_prefix):
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FGResourceNode):
        if actor.get_actor_label().startswith(label_prefix):
            return actor


STEP = globals().get("STEP", "report")

if STEP == "gather_setup":
    pile = node("ScrapPile1").get_actor_location()
    cmd(f"FGTeleport {pile.x + 250:.0f} {pile.y:.0f} {pile.z + 20:.0f}")
elif STEP == "gather_look":
    pile = node("ScrapPile1").get_actor_location()
    look_at(pile.x, pile.y, pile.z)
elif STEP == "gather":
    cmd("FGSkipStory")
    cmd("FGInteract")
    report("after gather")
elif STEP == "give":
    for item, n in (("ScrapMetal", 200), ("SteelBar", 60), ("CoralIngot", 30), ("SteelPlate", 30)):
        cmd(f"FGGive {item} {n}")
    cmd("FGTeleport 0 500 140")
elif STEP == "solar_aim":
    cmd("FGLook -35 0")
    cmd("FGSelect 1")
elif STEP == "solar_place":
    cmd("FGClick")
    report("after solar")
elif STEP == "smelter_aim":
    cmd("FGLook -35 90")
    cmd("FGSelect 4")
elif STEP == "smelter_place":
    cmd("FGClick")
    report("after smelter")
elif STEP == "crane_setup":
    pile = node("ScrapPile3").get_actor_location()
    cmd(f"FGTeleport {pile.x - 350:.0f} {pile.y:.0f} {pile.z:.0f}")
elif STEP == "crane_aim":
    pile = node("ScrapPile3").get_actor_location()
    look_at(pile.x, pile.y, pile.z - 30)
    cmd("FGSelect 2")
elif STEP == "crane_place":
    cmd("FGClick")
    report("after crane")
elif STEP == "belt_start":
    crane = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FGExtractor)[0]
    loc = crane.get_actor_location()
    look_at(loc.x, loc.y, loc.z + 100)
    cmd("FGSelect 8")
elif STEP == "belt_click1":
    cmd("FGClick")
elif STEP == "belt_end":
    smelter = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FGMachine)[0]
    loc = smelter.get_actor_location()
    look_at(loc.x, loc.y, loc.z + 100)
elif STEP == "belt_click2":
    cmd("FGClick")
    report("after belt")
else:
    report("report")
