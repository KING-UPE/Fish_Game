import unreal
import inspect

print("--- GeometryScript_Primitives ---")
for m in dir(unreal.GeometryScript_Primitives):
    if not m.startswith("_"):
        print(m)

print("--- GeometryScript_AssetUtils ---")
for m in dir(unreal.GeometryScript_AssetUtils):
    if not m.startswith("_"):
        print(m)
