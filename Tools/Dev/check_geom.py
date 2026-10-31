import unreal
print("Checking for GeometryScript:")
for attr in dir(unreal):
    if "geometry" in attr.lower() or "dynamicmesh" in attr.lower():
        print(" ", attr)
