import unreal

for n in dir(unreal):
    if any(k in n for k in ["DynamicMesh", "MeshDescription", "StaticMeshEditor"]):
        print(n)
