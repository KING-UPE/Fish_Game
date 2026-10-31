import unreal

print("GeometryScript_AssetUtils methods:")
for m in dir(unreal.GeometryScript_AssetUtils):
    if not m.startswith("_"):
        print(" ", m)

print("GeometryScript_Materials methods:")
for m in dir(unreal.GeometryScript_Materials):
    if not m.startswith("_"):
        print(" ", m)

print("GeometryScript_Collision methods:")
for m in dir(unreal.GeometryScript_Collision):
    if not m.startswith("_"):
        print(" ", m)
