import unreal

world = unreal.EditorLevelLibrary.get_editor_world()
print("Current world:", world.get_path_name() if world else "None")
actors = unreal.EditorLevelLibrary.get_all_level_actors()
print("Total actors in world:", len(actors))
solars = [a for a in actors if "Solar" in a.get_name() or "Buildable" in a.get_name()]
print("Solar/Buildable actors in level:", len(solars))
for a in solars[:10]:
    print(" ", a.get_name(), a.get_class().get_name())
