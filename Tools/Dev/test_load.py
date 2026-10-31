import unreal

m = unreal.load_object(None, "/Game/Blue/Materials/M_Machine.M_Machine")
print("Loaded M_Machine:", m)
sm1 = unreal.load_object(None, "/Game/Blue/Meshes/SM_FoundationTile.SM_FoundationTile")
print("Loaded SM_FoundationTile:", sm1)
sm2 = unreal.load_object(None, "/Game/Blue/Meshes/SM_SignalAntenna.SM_SignalAntenna")
print("Loaded SM_SignalAntenna:", sm2)
