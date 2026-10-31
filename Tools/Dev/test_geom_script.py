import unreal

for c in dir(unreal):
    if "GeometryScript" in c:
        print("GeometryScript:", c)
