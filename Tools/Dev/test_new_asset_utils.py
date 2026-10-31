import unreal

methods = [m for m in dir(unreal.GeometryScript_NewAssetUtils) if not m.startswith("_")]
print("GeometryScript_NewAssetUtils methods:", methods)
for m in methods:
    func = getattr(unreal.GeometryScript_NewAssetUtils, m)
    print(m, func.__doc__)
