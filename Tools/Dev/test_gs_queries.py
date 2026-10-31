import unreal

print("GeometryScript_MeshQueries methods:")
for m in dir(unreal.GeometryScript_MeshQueries):
    if not m.startswith("_"):
        print(" ", m)
