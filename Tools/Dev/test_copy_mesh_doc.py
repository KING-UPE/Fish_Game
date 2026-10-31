import inspect
import unreal

fn = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh
print("copy_mesh_to_static_mesh doc:", fn.__doc__)
