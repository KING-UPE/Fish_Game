import unreal

gs = [n for n in dir(unreal) if "GeometryScript" in n]
print(f"Total {len(gs)} GeometryScript classes:")
for n in gs[:30]:
    print(" ", n)
