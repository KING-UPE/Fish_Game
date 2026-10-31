import unreal
has_gs = hasattr(unreal, "GeometryScriptLibrary_MeshPrimitiveFunctions")
print("Has GeometryScript:", has_gs)
if has_gs:
    print("GeometryScript functions:", [f for f in dir(unreal) if "GeometryScript" in f][:10])
