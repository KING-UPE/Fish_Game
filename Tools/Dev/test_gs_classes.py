import unreal

for n in dir(unreal):
    if "GeometryScript_" in n or ("GeometryScript" in n and not n.startswith("GeometryScript")):
        print(n)
