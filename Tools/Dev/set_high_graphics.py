"""Restore Unreal Engine to High-Fidelity Epic Cinematic Mode.
Enables full Lumen, Virtual Shadow Maps, Volumetric Fog, and 100% resolution.
"""
import unreal

cmds = [
    "sg.ViewDistanceQuality 3",
    "sg.AntiAliasingQuality 3",
    "sg.ShadowQuality 3",
    "sg.GlobalIlluminationQuality 3",
    "sg.ReflectionQuality 3",
    "sg.PostProcessQuality 3",
    "sg.TextureQuality 3",
    "sg.EffectsQuality 3",
    "sg.FoliageQuality 3",
    "sg.ShadingQuality 3",
    
    "r.Shadow.Virtual.Enable 1",
    "r.VolumetricFog 1",
    "r.Lumen.DiffuseIndirect.Allow 1",
    "r.Lumen.Reflections.Allow 1",
    "r.ScreenPercentage 100",
    "r.DynamicGlobalIlluminationMethod 1",
    "t.MaxFPS 0",
]

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_game_world() or ues.get_editor_world()

for c in cmds:
    unreal.SystemLibrary.execute_console_command(world, c)

print("EPIC CINEMATIC GRAPHICS RESTORED: Full Lumen, Virtual Shadows, Volumetric Fog ON, 100% Native Resolution.")
