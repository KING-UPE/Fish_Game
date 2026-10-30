"""Blue Signal setup 1/4: materials (run inside the editor).
Creates/updates /Game/Blue/Materials: M_Machine, M_Item, M_Ghost, M_Belt, M_Ocean, M_Sand, M_Rock
and a few material instances for the level."""
import unreal
import warnings

warnings.simplefilter("ignore")

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
PATH = "/Game/Blue/Materials"
MP = unreal.MaterialProperty


def material(name):
    full = f"{PATH}/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        # delete_all skips some output nodes (e.g. Single Layer Water output); remove leftovers too.
        for leftover in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, leftover)
        print("UPDATED:", full)
    else:
        mat = TOOLS.create_asset(name, PATH, unreal.Material, unreal.MaterialFactoryNew())
        print("CREATED:", full)
    return mat


def expr(mat, cls, x, y, **props):
    node = MEL.create_material_expression(mat, cls, x, y)
    for key, value in props.items():
        node.set_editor_property(key, value)
    return node


def vparam(mat, name, color, x, y):
    return expr(mat, unreal.MaterialExpressionVectorParameter, x, y, parameter_name=name, default_value=unreal.LinearColor(*color))


def sparam(mat, name, value, x, y):
    return expr(mat, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=name, default_value=value)


def const(mat, value, x, y):
    return expr(mat, unreal.MaterialExpressionConstant, x, y, r=value)


def const3(mat, rgb, x, y):
    return expr(mat, unreal.MaterialExpressionConstant3Vector, x, y, constant=unreal.LinearColor(*rgb, 1.0))


def link(a, a_out, b, b_in):
    if not MEL.connect_material_expressions(a, a_out, b, b_in):
        print(f"  WARN: could not connect {a.get_name()}.{a_out} -> {b.get_name()}.{b_in}")


def out(node, node_out, prop):
    if not MEL.connect_material_property(node, node_out, prop):
        print(f"  WARN: could not connect {node.get_name()}.{node_out} -> {prop}")


def mul(mat, a, a_out, b, b_out, x, y):
    m = expr(mat, unreal.MaterialExpressionMultiply, x, y)
    link(a, a_out, m, "A")
    link(b, b_out, m, "B")
    return m


def finish(mat):
    MEL.recompile_material(mat)
    EAL.save_asset(mat.get_path_name())


# ---------------------------------------------------------------- M_Machine: lit, Color + Glow
m = material("M_Machine")
color = vparam(m, "Color", (0.5, 0.5, 0.5, 1), -600, 0)
glow = sparam(m, "Glow", 0.0, -600, 200)
metal = sparam(m, "Metallic", 0.25, -600, 320)
rough = sparam(m, "Roughness", 0.45, -600, 420)
out(color, "", MP.MP_BASE_COLOR)
out(mul(m, color, "", glow, "", -300, 200), "", MP.MP_EMISSIVE_COLOR)
out(metal, "", MP.MP_METALLIC)
out(rough, "", MP.MP_ROUGHNESS)
finish(m)

# ---------------------------------------------------------------- M_Item: colour from per-instance custom data
m = material("M_Item")
m.set_editor_property("used_with_instanced_static_meshes", True)
r = expr(m, unreal.MaterialExpressionPerInstanceCustomData, -800, 0, data_index=0)
g = expr(m, unreal.MaterialExpressionPerInstanceCustomData, -800, 120, data_index=1)
b = expr(m, unreal.MaterialExpressionPerInstanceCustomData, -800, 240, data_index=2)
rg = expr(m, unreal.MaterialExpressionAppendVector, -600, 60)
link(r, "", rg, "A")
link(g, "", rg, "B")
rgb = expr(m, unreal.MaterialExpressionAppendVector, -400, 120)
link(rg, "", rgb, "A")
link(b, "", rgb, "B")
out(rgb, "", MP.MP_BASE_COLOR)
out(mul(m, rgb, "", const(m, 0.35, -400, 300), "", -200, 260), "", MP.MP_EMISSIVE_COLOR)
out(const(m, 0.35, -200, 400), "", MP.MP_ROUGHNESS)
finish(m)

# ---------------------------------------------------------------- M_Ghost: translucent build preview
m = material("M_Ghost")
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
color = vparam(m, "Color", (0.1, 1.0, 0.35, 0.4), -600, 0)
out(mul(m, color, "", const(m, 2.0, -600, 200), "", -300, 0), "", MP.MP_EMISSIVE_COLOR)
out(const(m, 0.35, -300, 200), "", MP.MP_OPACITY)
finish(m)

# ---------------------------------------------------------------- M_Belt: dark belt with moving stripes
m = material("M_Belt")
color = vparam(m, "Color", (0.12, 0.13, 0.15, 1), -200, -200)
length = sparam(m, "Length", 1.0, -1200, 120)
uv = expr(m, unreal.MaterialExpressionTextureCoordinate, -1200, 0)
mask = expr(m, unreal.MaterialExpressionComponentMask, -1000, 0, r=True, g=False, b=False, a=False)
link(uv, "", mask, "")
stripes = mul(m, mask, "", mul(m, length, "", const(m, 2.5, -1200, 240), "", -1000, 180), "", -800, 60)
time = expr(m, unreal.MaterialExpressionTime, -1000, 320)
speed = mul(m, time, "", const(m, 1.2, -1000, 420), "", -800, 320)
moving = expr(m, unreal.MaterialExpressionSubtract, -600, 120)
link(stripes, "", moving, "A")
link(speed, "", moving, "B")
frac = expr(m, unreal.MaterialExpressionFrac, -450, 120)
link(moving, "", frac, "")
rnd = expr(m, unreal.MaterialExpressionRound, -320, 120)
link(frac, "", rnd, "")
lerp = expr(m, unreal.MaterialExpressionLinearInterpolate, -150, 60)
link(const(m, 0.55, -320, 0), "", lerp, "A")
link(const(m, 1.0, -320, 40), "", lerp, "B")
link(rnd, "", lerp, "Alpha")
out(mul(m, color, "", lerp, "", 50, -100), "", MP.MP_BASE_COLOR)
out(const(m, 0.75, 50, 100), "", MP.MP_ROUGHNESS)
finish(m)

# ---------------------------------------------------------------- M_Ocean: single layer water with two panning normal maps
m = material("M_Ocean")
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
water_n = unreal.load_asset("/Engine/Functions/Engine_MaterialFunctions02/ExampleContent/Textures/water_n.water_n")
world = expr(m, unreal.MaterialExpressionWorldPosition, -1600, 0)
xy = expr(m, unreal.MaterialExpressionComponentMask, -1400, 0, r=True, g=True, b=False, a=False)
link(world, "", xy, "")


def panning_normal(scale, sx, sy, y):
    uv = expr(m, unreal.MaterialExpressionDivide, -1200, y)
    link(xy, "", uv, "A")
    link(const(m, scale, -1400, y + 80), "", uv, "B")
    pan = expr(m, unreal.MaterialExpressionPanner, -1000, y, speed_x=sx, speed_y=sy)
    link(uv, "", pan, "Coordinate")
    tex = expr(m, unreal.MaterialExpressionTextureSample, -800, y, texture=water_n,
               sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    link(pan, "", tex, "UVs")
    return tex


n1 = panning_normal(900.0, 0.02, 0.012, 0)
n2 = panning_normal(2300.0, -0.01, 0.015, 300)
blend = expr(m, unreal.MaterialExpressionAdd, -550, 150)
link(n1, "RGB", blend, "A")
link(n2, "RGB", blend, "B")
calm = expr(m, unreal.MaterialExpressionLinearInterpolate, -350, 150)
link(blend, "", calm, "A")
link(const3(m, (0, 0, 1), -550, 320), "", calm, "B")
link(const(m, 0.35, -550, 420), "", calm, "Alpha")
out(calm, "", MP.MP_NORMAL)
out(const3(m, (0.02, 0.09, 0.12), -350, -150), "", MP.MP_BASE_COLOR)
out(const(m, 0.03, -350, -50), "", MP.MP_ROUGHNESS)
out(const(m, 0.6, -350, 20), "", MP.MP_SPECULAR)
slw = expr(m, unreal.MaterialExpressionSingleLayerWaterMaterialOutput, -100, 400)
link(const3(m, (0.012, 0.055, 0.06), -350, 480), "", slw, "ScatteringCoefficients")
link(const3(m, (0.38, 0.06, 0.035), -350, 560), "", slw, "AbsorptionCoefficients")
finish(m)

# ---------------------------------------------------------------- M_Sand: warm sand with soft noise variation
m = material("M_Sand")
world = expr(m, unreal.MaterialExpressionWorldPosition, -1000, 0)
noise = expr(m, unreal.MaterialExpressionNoise, -800, 0, scale=0.004, levels=4, output_min=0.0, output_max=1.0)
link(world, "", noise, "World Position")
sand = expr(m, unreal.MaterialExpressionLinearInterpolate, -500, 0)
link(const3(m, (0.62, 0.52, 0.36), -800, -200), "", sand, "A")
link(const3(m, (0.82, 0.72, 0.53), -800, -120), "", sand, "B")
link(noise, "", sand, "Alpha")
out(sand, "", MP.MP_BASE_COLOR)
out(const(m, 0.9, -500, 200), "", MP.MP_ROUGHNESS)
finish(m)

# ---------------------------------------------------------------- material instances for the level
def instance(name, parent, params):
    full = f"{PATH}/{name}"
    if EAL.does_asset_exist(full):
        mi = EAL.load_asset(full)
    else:
        mi = TOOLS.create_asset(name, PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        print("CREATED:", full)
    MEL.set_material_instance_parent(mi, parent)
    for key, value in params.items():
        if isinstance(value, tuple):
            MEL.set_material_instance_vector_parameter_value(mi, key, unreal.LinearColor(*value))
        else:
            MEL.set_material_instance_scalar_parameter_value(mi, key, value)
    EAL.save_asset(full)
    return mi


machine = EAL.load_asset(f"{PATH}/M_Machine")
instance("MI_WreckHull", machine, {"Color": (0.32, 0.34, 0.37, 1), "Metallic": 0.6, "Roughness": 0.55})
instance("MI_WreckStripe", machine, {"Color": (0.95, 0.42, 0.08, 1), "Metallic": 0.2, "Roughness": 0.5})
instance("MI_WreckBurnt", machine, {"Color": (0.06, 0.06, 0.06, 1), "Metallic": 0.3, "Roughness": 0.8})
instance("MI_EngineGlow", machine, {"Color": (0.2, 0.7, 1.0, 1), "Glow": 4.0})
instance("MI_Rock", machine, {"Color": (0.28, 0.27, 0.25, 1), "Metallic": 0.0, "Roughness": 0.9})
instance("MI_Palm", machine, {"Color": (0.12, 0.38, 0.12, 1), "Metallic": 0.0, "Roughness": 0.8})
instance("MI_Trunk", machine, {"Color": (0.35, 0.24, 0.14, 1), "Metallic": 0.0, "Roughness": 0.9})
print("MATERIALS DONE")
