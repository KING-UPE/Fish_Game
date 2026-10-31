import unreal

has_geom = hasattr(unreal, "GeometryScriptLibrary_MeshPrimitiveFunctions")
print("Has GeometryScript:", has_geom)
if has_geom:
    print("GeometryScript methods:", [m for m in dir(unreal.GeometryScriptLibrary_MeshPrimitiveFunctions) if not m.startswith("_")][:10])
