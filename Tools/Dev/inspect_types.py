import unreal

po = unreal.GeometryScriptPrimitiveOptions()
print("PrimitiveOptions:", dir(po))
print("Origin modes:", dir(unreal.GeometryScriptPrimitiveOriginMode))
print("WriteLOD:", dir(unreal.GeometryScriptMeshWriteLOD))
lod = unreal.GeometryScriptMeshWriteLOD()
print("WriteLOD default:", lod.write_lod_type, lod.lod_index)

copt = unreal.GeometryScriptCopyMeshToAssetOptions()
print("CopyOptions:", dir(copt))

# Also check Materials and PolyGroups in GeometryScript
print("Materials:", dir(unreal.GeometryScript_Materials))
print("PolyGroups:", dir(unreal.GeometryScript_PolyGroups))
print("Normals:", dir(unreal.GeometryScript_Normals))
print("UVs:", dir(unreal.GeometryScript_UVs))
print("Collision:", dir(unreal.GeometryScript_Collision))
