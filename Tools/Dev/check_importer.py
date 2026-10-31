import unreal

tools = unreal.AssetToolsHelpers.get_asset_tools()
print("AssetTools available")

# Check if OBJ or GLTF or FBX are supported
factories = [
    f for f in dir(unreal) if "Factory" in f and ("Mesh" in f or "Fbx" in f or "Obj" in f or "Interchange" in f)
]
print("Factories:", factories)
