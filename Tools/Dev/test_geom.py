import unreal

print("GeometryScript classes:")
for attr in dir(unreal):
    if "GeometryScript" in attr:
        print("  ", attr)

print("DynamicMesh classes:")
for attr in dir(unreal):
    if "DynamicMesh" in attr:
        print("  ", attr)
