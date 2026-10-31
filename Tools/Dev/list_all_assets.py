import unreal

eal = unreal.EditorAssetLibrary
print("Assets recursive:")
for a in eal.list_assets("/Game/Blue", recursive=True):
    print(" ", a)
