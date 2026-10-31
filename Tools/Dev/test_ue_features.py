import unreal

has_gs = hasattr(unreal, "GeometryScriptLibrary_MeshPrimitiveFunctions")
print(f"GeometryScript available: {has_gs}")

if has_gs:
    print("GeometryScript methods:", dir(unreal.GeometryScriptLibrary_MeshPrimitiveFunctions)[:5])

# Also check FBX / OBJ import factory
obj_factory = unreal.ReimportTextureFactory()
print("AssetTools exists:", hasattr(unreal, "AssetToolsHelpers"))
