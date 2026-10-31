import unreal

libs = [n for n in dir(unreal) if n.startswith("GeometryScriptLibrary_")]
print(f"GeometryScript Libraries ({len(libs)}):")
for lib in sorted(libs):
    methods = [m for m in dir(getattr(unreal, lib)) if not m.startswith("_")]
    print(f"\n{lib} ({len(methods)} methods):")
    for m in sorted(methods)[:12]:
        print(f"  {m}")
    if len(methods) > 12:
        print(f"  ... and {len(methods) - 12} more")
