import unreal

try:
    eal = unreal.EditorAssetLibrary
    p = "/Game/Blue/Meshes/SM_TestObj"
    print("Does exist:", eal.does_asset_exist(p))
    sm = eal.load_asset(p)
    print("sm loaded:", sm)
except Exception as e:
    print("Exception:", e)
