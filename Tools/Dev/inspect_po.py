import unreal

po = unreal.GeometryScriptPrimitiveOptions()
print("GeometryScriptPrimitiveOptions fields:")
for f in dir(po):
    if not f.startswith("_"):
        print(f, getattr(po, f))
