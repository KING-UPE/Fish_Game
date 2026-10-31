import unreal

def inspect_mat(path):
    mat = unreal.load_object(None, path)
    if not mat:
        print(f"Material {path} not found")
        return
    print(f"=== {path} ({mat.get_class().get_name()}) ===")
    if isinstance(mat, unreal.MaterialInstance):
        for sp in mat.scalar_parameter_values:
            print(f"  Scalar: {sp.parameter_info.name} = {sp.parameter_value}")
        for vp in mat.vector_parameter_values:
            print(f"  Vector: {vp.parameter_info.name} = {vp.parameter_value}")
    elif isinstance(mat, unreal.Material):
        print("  Base material")

inspect_mat("/Game/Blue/Materials/M_Machine.M_Machine")
inspect_mat("/Game/Blue/Materials/M_Belt.M_Belt")
inspect_mat("/Game/Blue/Materials/M_Item.M_Item")
