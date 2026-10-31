import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "CrashIsland":
        print("CrashIsland transform:", a.get_actor_transform())
    if "Tree" in a.get_actor_label():
        print(a.get_actor_label(), "transform:", a.get_actor_transform())
        break
