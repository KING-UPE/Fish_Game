import unreal

print("GeometryScript_AssetUtils methods:")
for m in dir(unreal.GeometryScript_AssetUtils):
    if not m.startswith("_"):
        print(" ", m)

print("GeometryScript_NewAssetUtils methods:")
for m in dir(unreal.GeometryScript_NewAssetUtils):
    if not m.startswith("_"):
        print(" ", m)
