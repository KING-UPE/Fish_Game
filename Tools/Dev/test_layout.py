"""Dev tool: drop a small working factory into the open level (NOT saved) to test the chain.
Salvage Crane (on ScrapPile3) -> Smelter -> Press -> Storage, powered by two Solar Panels.
Run, start Play, wait ~40 s, then run test_layout_report.py."""
import math
import unreal
import warnings

warnings.simplefilter("ignore")
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def ground_z(x, y, r=2250.0, h=150.0):
    return h * math.sqrt(max(0.0, 1.0 - (math.hypot(x, y) / r) ** 2))


def place(cls, row, x, y, label):
    actor = EAS.spawn_actor_from_class(cls, unreal.Vector(x, y, ground_z(x, y)), unreal.Rotator())
    actor.set_editor_property("row_name", unreal.Name(row))
    actor.set_actor_label(label)
    actor.set_folder_path("TestLayout")
    return actor


def belt(a, b, label):
    actor = EAS.spawn_actor_from_class(unreal.FGBelt, unreal.Vector(0, 0, 0), unreal.Rotator())
    actor.set_editor_property("start_actor", a)
    actor.set_editor_property("end_actor", b)
    actor.set_actor_label(label)
    actor.set_folder_path("TestLayout")
    return actor


crane = place(unreal.FGExtractor, "SalvageCrane", -300, 200, "T_Crane")
smelter = place(unreal.FGMachine, "Smelter", 50, 250, "T_Smelter")
press = place(unreal.FGMachine, "Press", 450, 250, "T_Press")
storage = place(unreal.FGStorage, "Storage", 800, 250, "T_Storage")
place(unreal.FGGenerator, "Solar", -300, -300, "T_Solar1")
place(unreal.FGGenerator, "Solar", -100, -300, "T_Solar2")
belt(crane, smelter, "T_Belt1")
belt(smelter, press, "T_Belt2")
belt(press, storage, "T_Belt3")
print("TEST LAYOUT PLACED")
