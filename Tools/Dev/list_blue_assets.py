import unreal

eal = unreal.EditorAssetLibrary
assets = eal.list_assets("/Game/Blue", recursive=True)
print(f"Total assets in /Game/Blue: {len(assets)}")
for a in sorted(assets):
    if "Texture" in a or "T_" in a or "M_" in a:
        print(" ", a)
