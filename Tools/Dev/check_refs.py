import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
for name in ["SM_FluidTank", "SM_PipeStraight"]:
    p = f"/Game/Blue/Meshes/{name}"
    refs = ar.get_referencers(p, unreal.AssetRegistryDependencyOptions())
    print(f"Referencers of {name}:", refs)
