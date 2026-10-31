import unreal

try:
    import unreal
    has_gs = hasattr(unreal, "GeometryScriptLibrary_MeshPrimitiveFunctions")
    print(f"Has GeometryScript: {has_gs}")
    if has_gs:
        print("GeometryScript methods:")
        for attr in dir(unreal.GeometryScriptLibrary_MeshPrimitiveFunctions):
            if not attr.startswith("_"):
                print("  ", attr)
except Exception as e:
    print(f"Error checking GeometryScript: {e}")
