import unreal

has_gs = hasattr(unreal, "GeometryScript") or hasattr(unreal, "GeometryScript_AssetManagement")
print("Has GeometryScript?", has_gs)
gs_attrs = [x for x in dir(unreal) if "Geometry" in x or "MeshDescription" in x]
print("Matching UE classes/functions:", len(gs_attrs), gs_attrs[:20])
