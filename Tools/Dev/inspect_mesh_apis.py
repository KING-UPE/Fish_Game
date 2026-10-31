import unreal

gs = [n for n in dir(unreal) if "Geometry" in n or "Mesh" in n]
print(f"Total matching: {len(gs)}")
classes_with_methods = []
for n in gs:
    cls = getattr(unreal, n)
    if isinstance(cls, type):
        funcs = [f for f in dir(cls) if not f.startswith("_")]
        if funcs:
            classes_with_methods.append((n, len(funcs), funcs[:5]))

classes_with_methods.sort(key=lambda x: -x[1])
for name, count, funcs in classes_with_methods[:30]:
    print(f"{name} ({count} methods): {funcs}")
