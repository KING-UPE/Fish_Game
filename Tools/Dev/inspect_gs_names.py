import unreal

names = [n for n in dir(unreal) if "GeometryScript" in n]
for n in names:
    cls = getattr(unreal, n)
    # Check if it has callable methods other than standard object methods
    methods = [m for m in dir(cls) if not m.startswith("_")]
    if len(methods) > 0:
        print(f"{n}: {methods[:5]} (total {len(methods)})")
