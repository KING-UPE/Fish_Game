import unreal

tools = unreal.AssetToolsHelpers.get_asset_tools()
print("Asset tools found:", tools)
for c in dir(unreal):
    if "Factory" in c and ("Mesh" in c or "Fbx" in c or "OBJ" in c or "GLTF" in c or "Static" in c):
        print("Factory class:", c)
