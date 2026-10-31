import unreal
import inspect

print("copy_mesh_to_static_mesh help:")
print(unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh.__doc__)

opts = unreal.GeometryScriptCopyMeshToAssetOptions()
print("GeometryScriptCopyMeshToAssetOptions properties:")
for prop in dir(opts):
    if not prop.startswith("_"):
        print(" ", prop)

wlod = unreal.GeometryScriptMeshWriteLOD()
print("GeometryScriptMeshWriteLOD properties:")
for prop in dir(wlod):
    if not prop.startswith("_"):
        print(" ", prop)
