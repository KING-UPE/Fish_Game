import unreal

print("GeometryScript_Primitives methods:")
for m in dir(unreal.GeometryScript_Primitives):
    if not m.startswith("_"):
        print(" ", m)

print("GeometryScript_Materials methods:")
for m in dir(unreal.GeometryScript_Materials):
    if not m.startswith("_"):
        print(" ", m)

print("GeometryScript_Normals methods:")
for m in dir(unreal.GeometryScript_Normals):
    if not m.startswith("_"):
        print(" ", m)

print("GeometryScript_UVs methods:")
for m in dir(unreal.GeometryScript_UVs):
    if not m.startswith("_"):
        print(" ", m)
