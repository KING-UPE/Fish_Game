import unreal
gs_classes = [x for x in dir(unreal) if "GeometryScript" in x]
print(f"Total GeometryScript entries: {len(gs_classes)}")
for c in gs_classes:
    print(c)
