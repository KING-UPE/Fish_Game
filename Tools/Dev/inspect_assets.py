import unreal

eal = unreal.EditorAssetLibrary
print("Assets in /Game (recursive):")
assets = eal.list_assets("/Game", recursive=True)
print(f"Total: {len(assets)}")
for a in sorted(assets)[:50]:
    print(" ", a)

print("\nAsset classes:")
classes = {}
for a in assets:
    data = eal.find_asset_data(a)
    cls = str(data.asset_class_path.asset_name)
    classes[cls] = classes.get(cls, 0) + 1
for c, cnt in sorted(classes.items(), key=lambda x: -x[1]):
    print(f"  {c}: {cnt}")
