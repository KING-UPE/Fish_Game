import unreal

eal = unreal.EditorAssetLibrary
assets = eal.list_assets("/Game/Blue/Materials")
for a in sorted(assets):
    print(a)
