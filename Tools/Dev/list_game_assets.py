import unreal
eal = unreal.EditorAssetLibrary
assets = eal.list_assets("/Game", recursive=True)
print(f"Total assets in /Game: {len(assets)}")
for a in assets[:50]:
    print(" ", a)
