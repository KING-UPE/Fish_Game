import unreal

eal = unreal.EditorAssetLibrary
smes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

sm = unreal.load_object(None, "/Game/Blue/Meshes/SM_TestImport")
if sm:
    smes.set_convex_decomposition_collisions(sm, 4, 32, 100000)
    col_count = smes.get_simple_collision_count(sm)
    print("Collision count:", col_count)
    eal.delete_asset("/Game/Blue/Meshes/SM_TestImport")
    print("Cleaned up test asset")
