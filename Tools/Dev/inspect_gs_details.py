import unreal

for name in [
    "GeometryScript_AssetManagement",
    "GeometryScript_Primitives",
    "GeometryScript_Materials",
    "GeometryScript_MeshBasicEdit",
    "GeometryScript_UVs",
    "GeometryScript_Normals",
    "GeometryScript_Booleans",
    "GeometryScript_VertexColors"
]:
    cls = getattr(unreal, name, None)
    if cls:
        funcs = [m for m in dir(cls) if not m.startswith("_") and not m in ['cast', 'call_method', 'acquire_editor_element_handle', 'get_class', 'get_default_object']]
        print(f"=== {name} ({len(funcs)}) ===")
        for f in sorted(funcs):
            print(" ", f)
