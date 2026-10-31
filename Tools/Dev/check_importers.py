import unreal

for factory in unreal.EditorAssetLibrary.list_assets("/Engine", recursive=True):
    pass

factories = [c for c in dir(unreal) if "Factory" in c]
for f in factories:
    if any(k in f.lower() for k in ["fbx", "obj", "mesh", "import"]):
        print(f)
