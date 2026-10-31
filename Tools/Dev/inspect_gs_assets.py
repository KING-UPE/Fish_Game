import unreal

for name in ["GeometryScript_AssetManagement", "GeometryScript_AssetUtils", "GeometryScript_MeshBasicEdit"]:
    cls = getattr(unreal, name, None)
    if cls:
        funcs = [m for m in dir(cls) if not m.startswith("_") and not m in ['cast', 'call_method', 'acquire_editor_element_handle', 'get_class', 'get_default_object']]
        print(f"=== {name} ===")
        for f in sorted(funcs):
            print(" ", f)
