import unreal

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
PATH = "/Game/Blue/Materials"
MP = unreal.MaterialProperty

def create_or_clean_material(name):
    full = f"{PATH}/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        for leftover in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, leftover)
    else:
        mat = TOOLS.create_asset(name, PATH, unreal.Material, unreal.MaterialFactoryNew())
    return mat

def expr(mat, cls, x, y, **props):
    node = MEL.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        node.set_editor_property(k, v)
    return node

def link(a, a_out, b, b_in):
    return MEL.connect_material_expressions(a, a_out, b, b_in)

def out(node, node_out, prop):
    return MEL.connect_material_property(node, node_out, prop)

def const(mat, val, x, y):
    return expr(mat, unreal.MaterialExpressionConstant, x, y, r=val)

def const3(mat, rgb, x, y):
    return expr(mat, unreal.MaterialExpressionConstant3Vector, x, y, constant=unreal.LinearColor(*rgb, 1.0))

def mul(mat, a, a_out, b, b_out, x, y):
    m = expr(mat, unreal.MaterialExpressionMultiply, x, y)
    link(a, a_out, m, "A")
    link(b, b_out, m, "B")
    return m

def add(mat, a, a_out, b, b_out, x, y):
    m = expr(mat, unreal.MaterialExpressionAdd, x, y)
    link(a, a_out, m, "A")
    link(b, b_out, m, "B")
    return m

# ====================================================================
# 1. M_BasaltRock: Dark porous volcanic basalt (0.0 metallic, 0.9 roughness)
# ====================================================================
m_basalt = create_or_clean_material("M_BasaltRock")

# Porous noise variation from World Position
wp = expr(m_basalt, unreal.MaterialExpressionWorldPosition, -1000, 0)
noise = expr(m_basalt, unreal.MaterialExpressionNoise, -700, 0, scale=0.04, levels=3, output_min=0.0, output_max=1.0)
link(wp, "", noise, "World Position")

# Lerp between deep charcoal basalt and dark slate basalt
col_dark = const3(m_basalt, (0.035, 0.035, 0.04), -700, -200)
col_light = const3(m_basalt, (0.075, 0.075, 0.085), -700, -100)
lerp_rock = expr(m_basalt, unreal.MaterialExpressionLinearInterpolate, -450, -150)
link(col_dark, "", lerp_rock, "A")
link(col_light, "", lerp_rock, "B")
link(noise, "", lerp_rock, "Alpha")

# Porous rough surface
rough_rock = const(m_basalt, 0.9, -300, 100)
metal_rock = const(m_basalt, 0.0, -300, 200)

out(lerp_rock, "", MP.MP_BASE_COLOR)
out(rough_rock, "", MP.MP_ROUGHNESS)
out(metal_rock, "", MP.MP_METALLIC)

MEL.recompile_material(m_basalt)
EAL.save_asset(m_basalt.get_path_name())
print("Created M_BasaltRock")

# ====================================================================
# 2. M_CoralCrystal: Glassy translucent crystalline coral (0.1 metallic, 0.05 roughness, strong specular)
# ====================================================================
m_crystal = create_or_clean_material("M_CoralCrystal")

# Prismatic chromatic refraction via Fresnel
fresnel = expr(m_crystal, unreal.MaterialExpressionFresnel, -700, -100)
fresnel.set_editor_property("exponent", 2.2)
fresnel.set_editor_property("base_reflect_fraction", 0.08)

# Core crystal color (vibrant deep magenta/coral) to edge refraction (bright cyan/violet iridescent highlight)
core_col = const3(m_crystal, (0.85, 0.08, 0.38), -700, -300)
edge_col = const3(m_crystal, (0.15, 0.85, 0.95), -700, -200)

lerp_crystal = expr(m_crystal, unreal.MaterialExpressionLinearInterpolate, -400, -200)
link(core_col, "", lerp_crystal, "A")
link(edge_col, "", lerp_crystal, "B")
link(fresnel, "", lerp_crystal, "Alpha")

# Subtle internal crystal glow (0.45 emissive)
emissive_c = mul(m_crystal, lerp_crystal, "", const(m_crystal, 0.45, -500, 50), "", -200, 0)

out(lerp_crystal, "", MP.MP_BASE_COLOR)
out(const(m_crystal, 0.1, -200, 120), "", MP.MP_METALLIC)
out(const(m_crystal, 0.05, -200, 200), "", MP.MP_ROUGHNESS)
out(const(m_crystal, 1.0, -200, 280), "", MP.MP_SPECULAR)
out(emissive_c, "", MP.MP_EMISSIVE_COLOR)

MEL.recompile_material(m_crystal)
EAL.save_asset(m_crystal.get_path_name())
print("Created M_CoralCrystal")

# ====================================================================
# 3. M_CoralEnergyVeins: Bioluminescent resonant energy veins pulsating along crystal axes (emissive x5.0 pink/cyan glow)
# ====================================================================
m_veins = create_or_clean_material("M_CoralEnergyVeins")

time = expr(m_veins, unreal.MaterialExpressionTime, -1000, 0)
# 440 THz harmonic simulation (frequency wave around 2.5 rad/sec)
freq = mul(m_veins, time, "", const(m_veins, 2.5, -1000, 100), "", -800, 50)
sine = expr(m_veins, unreal.MaterialExpressionSine, -650, 50)
link(freq, "", sine, "")

# Map sine from [-1, 1] to [0, 1]
sine_norm = expr(m_veins, unreal.MaterialExpressionLinearInterpolate, -450, 50)
link(const(m_veins, 0.0, -650, 150), "", sine_norm, "A")
link(const(m_veins, 1.0, -650, 200), "", sine_norm, "B")
# Rescale sine to [0, 1] via add and mul: (sine * 0.5) + 0.5
half = const(m_veins, 0.5, -600, -50)
s_mul = mul(m_veins, sine, "", half, "", -450, -50)
s_bias = add(m_veins, s_mul, "", half, "", -300, -50)

# Resonant colors: Hot Pink/Magenta and Electric Cyan
col_pink = const3(m_veins, (1.0, 0.05, 0.45), -500, -300)
col_cyan = const3(m_veins, (0.05, 0.90, 1.0), -500, -200)

vein_color = expr(m_veins, unreal.MaterialExpressionLinearInterpolate, -200, -200)
link(col_pink, "", vein_color, "A")
link(col_cyan, "", vein_color, "B")
link(s_bias, "", vein_color, "Alpha")

# Base glow intensity x5.0, pulsing up to x8.0
pulse_intensity = expr(m_veins, unreal.MaterialExpressionLinearInterpolate, -200, 0)
link(const(m_veins, 5.0, -400, 80), "", pulse_intensity, "A")
link(const(m_veins, 8.5, -400, 140), "", pulse_intensity, "B")
link(s_bias, "", pulse_intensity, "Alpha")

emissive_vein = mul(m_veins, vein_color, "", pulse_intensity, "", 0, -100)

out(vein_color, "", MP.MP_BASE_COLOR)
out(emissive_vein, "", MP.MP_EMISSIVE_COLOR)
out(const(m_veins, 0.0, 0, 100), "", MP.MP_METALLIC)
out(const(m_veins, 0.1, 0, 180), "", MP.MP_ROUGHNESS)

MEL.recompile_material(m_veins)
EAL.save_asset(m_veins.get_path_name())
print("Created M_CoralEnergyVeins")

# ====================================================================
# 4. M_SurveyPlaque: Industrial stamped survey plaque with decals and emissive readouts
# ====================================================================
m_plaque = create_or_clean_material("M_SurveyPlaque")
tex_survey = unreal.load_asset("/Game/Blue/Textures/T_CoralOre_SurveyPlaque.T_CoralOre_SurveyPlaque")

ts = expr(m_plaque, unreal.MaterialExpressionTextureSample, -600, -100, texture=tex_survey)

# Roughness: 0.35 satin anodized plate
# Metallic: 0.8
out(ts, "RGB", MP.MP_BASE_COLOR)
out(const(m_plaque, 0.8, -300, 100), "", MP.MP_METALLIC)
out(const(m_plaque, 0.35, -300, 200), "", MP.MP_ROUGHNESS)

# Emissive readout boost for bright text/readouts:
# High luminance parts (text/LEDs/waveforms) emit light
lum = expr(m_plaque, unreal.MaterialExpressionComponentMask, -400, -300, r=True, g=True, b=True, a=False)
link(ts, "RGB", lum, "")
# Multiply color by 1.8 for glowing screens and text
emissive_p = mul(m_plaque, ts, "RGB", const(m_plaque, 1.8, -400, -50), "", -150, -150)
out(emissive_p, "", MP.MP_EMISSIVE_COLOR)

MEL.recompile_material(m_plaque)
EAL.save_asset(m_plaque.get_path_name())
print("Created M_SurveyPlaque")

# ====================================================================
# 5. M_AnchorHardware: Galvanized steel extraction hardware & drill bolts
# ====================================================================
m_hw = create_or_clean_material("M_AnchorHardware")
out(const3(m_hw, (0.28, 0.29, 0.32), -400, -100), "", MP.MP_BASE_COLOR)
out(const(m_hw, 0.88, -400, 50), "", MP.MP_METALLIC)
out(const(m_hw, 0.28, -400, 150), "", MP.MP_ROUGHNESS)

MEL.recompile_material(m_hw)
EAL.save_asset(m_hw.get_path_name())
print("Created M_AnchorHardware")

print("ALL 5 MATERIALS READY!")
