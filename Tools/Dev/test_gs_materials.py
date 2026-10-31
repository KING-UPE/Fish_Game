import unreal

methods = [m for m in dir(unreal.GeometryScript_Materials) if not m.startswith("_")]
print("GeometryScript_Materials methods:", methods)
for m in methods:
    func = getattr(unreal.GeometryScript_Materials, m)
    print(m, func.__doc__)
