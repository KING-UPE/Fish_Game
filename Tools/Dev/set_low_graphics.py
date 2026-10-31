"""Set Unreal Engine to Fast Performance / Low-Spec Testing Mode.
Drastically reduces GPU load:
- Disables Virtual Shadow Maps (VSM) -> standard CSM (huge FPS boost)
- Disables Volumetric Height Fog
- Lowers Post-Processing, Shadows, Anti-Aliasing, and Effects to Low/Medium
- Enables Temporal Super Resolution (TSR) with 70% screen resolution scale
- Caps FPS to smooth 60
"""
import unreal

cmds = [
    # Global scalability levels (0 = Low, 1 = Medium, 2 = High, 3 = Epic)
    "sg.ViewDistanceQuality 1",
    "sg.AntiAliasingQuality 1",
    "sg.ShadowQuality 1",
    "sg.GlobalIlluminationQuality 1",
    "sg.ReflectionQuality 1",
    "sg.PostProcessQuality 1",
    "sg.TextureQuality 2",
    "sg.EffectsQuality 1",
    "sg.FoliageQuality 1",
    "sg.ShadingQuality 1",
    
    # Specific heavy UE5 features
    "r.Shadow.Virtual.Enable 0",            # Disable expensive Virtual Shadow Maps
    "r.Shadow.CSM.MaxCascades 2",           # Fast 2-cascade standard shadows
    "r.VolumetricFog 0",                     # Disable volumetric fog raymarching
    "r.Lumen.DiffuseIndirect.Allow 0",      # Disable heavy Lumen indirect GI compute
    "r.Lumen.Reflections.Allow 0",          # Disable Lumen reflection tracing
    "r.ScreenPercentage 70",                 # Render at 70% with TSR upscaling (doubles frame rate)
    "r.DynamicGlobalIlluminationMethod 0",  # Disable heavy real-time GI in test mode
    "t.MaxFPS 60",                           # Stable 60 FPS cap
]

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = ues.get_game_world() or ues.get_editor_world()

for c in cmds:
    unreal.SystemLibrary.execute_console_command(world, c)

print("FAST PERFORMANCE MODE ACTIVATED: Virtual Shadows OFF, Volumetric Fog OFF, 70% Resolution Scale, 60 FPS Cap.")
