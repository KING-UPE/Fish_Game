import unreal

eal = unreal.EditorAssetLibrary
mats = eal.list_assets("/Game/Blue/Materials", recursive=True)
print(f"Materials in /Game/Blue/Materials: {len(mats)}")
for m in sorted(mats):
    obj = eal.load_asset(m)
    print(f"  {m} ({obj.get_class().get_name() if obj else 'None'})")
