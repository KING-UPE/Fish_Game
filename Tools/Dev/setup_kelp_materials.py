import unreal

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
MP = unreal.MaterialProperty

# 1. Ensure /Game/Blue/Textures folder exists and import texture
texture_file = r"D:\Game\FishGame\Saved\T_KelpFarm_Decals.png"
tex_dest_path = "/Game/Blue/Textures"
tex_name = "T_KelpFarm_Decals"
tex_full = f"{tex_dest_path}/{tex_name}"

task = unreal.AssetImportTask()
task.filename = texture_file
task.destination_path = tex_dest_path
task.destination_name = tex_name
task.replace_existing = True
task.automated = True
task.save = True

TOOLS.import_asset_tasks([task])
tex = unreal.load_object(None, f"{tex_full}.{tex_name}")
print("Loaded texture:", tex)

# Helper functions for material building
def get_or_create_mat(name):
    full = f"/Game/Blue/Materials/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        for leftover in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, leftover)
    else:
        mat = TOOLS.create_asset(name, "/Game/Blue/Materials", unreal.Material, unreal.MaterialFactoryNew())
    return mat

def expr(mat, cls, x, y, **props):
    node = MEL.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        node.set_editor_property(k, v)
    return node

def link(a, a_out, b, b_in):
    MEL.connect_material_expressions(a, a_out, b, b_in)

def out(node, node_out, prop):
    MEL.connect_material_property(node, node_out, prop)

def finish(mat):
    MEL.recompile_material(mat)
    EAL.save_asset(mat.get_path_name())
    print("Saved material:", mat.get_path_name())

# Material 1: M_BiocontainmentWhite (FICSIT clean white casing with subtle edge highlight)
m1 = get_or_create_mat("M_BiocontainmentWhite")
c_white = expr(m1, unreal.MaterialExpressionVectorParameter, -800, 0, parameter_name="BaseColor", default_value=unreal.LinearColor(0.88, 0.90, 0.92, 1.0))
edge_col = expr(m1, unreal.MaterialExpressionConstant3Vector, -600, -200, constant=unreal.LinearColor(0.98, 1.0, 1.0, 1.0))
fresnel = expr(m1, unreal.MaterialExpressionFresnel, -600, -50, exponent=4.0, base_reflect_fraction=0.04)
lerp_col = expr(m1, unreal.MaterialExpressionLinearInterpolate, -400, 0)
link(c_white, "", lerp_col, "A")
link(edge_col, "", lerp_col, "B")
link(fresnel, "", lerp_col, "Alpha")
out(lerp_col, "", MP.MP_BASE_COLOR)
out(expr(m1, unreal.MaterialExpressionConstant, -400, 120, r=0.05), "", MP.MP_METALLIC)
out(expr(m1, unreal.MaterialExpressionConstant, -400, 200, r=0.28), "", MP.MP_ROUGHNESS)
finish(m1)

# Material 2: M_NutrientFluid (Deep teal translucent/subsurface nutrient fluid with subtle emissive shimmer)
m2 = get_or_create_mat("M_NutrientFluid")
c_teal = expr(m2, unreal.MaterialExpressionVectorParameter, -600, 0, parameter_name="FluidColor", default_value=unreal.LinearColor(0.015, 0.28, 0.35, 1.0))
c_glow = expr(m2, unreal.MaterialExpressionVectorParameter, -600, 150, parameter_name="FluidGlow", default_value=unreal.LinearColor(0.02, 0.35, 0.42, 1.0))
fresnel_fluid = expr(m2, unreal.MaterialExpressionFresnel, -500, 250, exponent=2.5, base_reflect_fraction=0.1)
mul_glow = expr(m2, unreal.MaterialExpressionMultiply, -300, 180)
link(c_glow, "", mul_glow, "A")
link(fresnel_fluid, "", mul_glow, "B")
out(c_teal, "", MP.MP_BASE_COLOR)
out(mul_glow, "", MP.MP_EMISSIVE_COLOR)
out(expr(m2, unreal.MaterialExpressionConstant, -400, 300, r=0.05), "", MP.MP_METALLIC)
out(expr(m2, unreal.MaterialExpressionConstant, -400, 380, r=0.06), "", MP.MP_ROUGHNESS)
finish(m2)

# Material 3: M_Glowkelp (Vibrant bioluminescent emerald/cyan kelp foliage with 4.0x emissive intensity!)
m3 = get_or_create_mat("M_Glowkelp")
kelp_base = expr(m3, unreal.MaterialExpressionVectorParameter, -700, 0, parameter_name="KelpColor", default_value=unreal.LinearColor(0.12, 0.88, 0.45, 1.0))
kelp_glow_col = expr(m3, unreal.MaterialExpressionVectorParameter, -700, 180, parameter_name="GlowColor", default_value=unreal.LinearColor(0.25, 1.0, 0.65, 1.0))
kelp_mult = expr(m3, unreal.MaterialExpressionScalarParameter, -700, 320, parameter_name="EmissiveIntensity", default_value=4.0)
fresnel_kelp = expr(m3, unreal.MaterialExpressionFresnel, -600, 420, exponent=2.0, base_reflect_fraction=0.2)
add_glow = expr(m3, unreal.MaterialExpressionAdd, -450, 280)
link(kelp_mult, "", add_glow, "A")
link(fresnel_kelp, "", add_glow, "B")
emissive_kelp = expr(m3, unreal.MaterialExpressionMultiply, -250, 200)
link(kelp_glow_col, "", emissive_kelp, "A")
link(add_glow, "", emissive_kelp, "B")
out(kelp_base, "", MP.MP_BASE_COLOR)
out(emissive_kelp, "", MP.MP_EMISSIVE_COLOR)
out(expr(m3, unreal.MaterialExpressionConstant, -400, 480, r=0.0), "", MP.MP_METALLIC)
out(expr(m3, unreal.MaterialExpressionConstant, -400, 540, r=0.32), "", MP.MP_ROUGHNESS)
finish(m3)

# Material 4: M_IndustrialDark (Carbon steel / gunmetal frames, pump manifolds, brackets, bolts)
m4 = get_or_create_mat("M_IndustrialDark")
c_dark = expr(m4, unreal.MaterialExpressionVectorParameter, -600, 0, parameter_name="BaseColor", default_value=unreal.LinearColor(0.12, 0.13, 0.15, 1.0))
out(c_dark, "", MP.MP_BASE_COLOR)
out(expr(m4, unreal.MaterialExpressionConstant, -400, 100, r=0.88), "", MP.MP_METALLIC)
out(expr(m4, unreal.MaterialExpressionConstant, -400, 180, r=0.36), "", MP.MP_ROUGHNESS)
finish(m4)

# Material 5: M_ScreenDecal (Decals and climate monitoring screen with emissive readout)
m5 = get_or_create_mat("M_ScreenDecal")
tex_node = expr(m5, unreal.MaterialExpressionTextureSample, -600, 0, texture=tex)
glow_scale = expr(m5, unreal.MaterialExpressionScalarParameter, -600, 250, parameter_name="ScreenGlow", default_value=2.5)
mul_screen_glow = expr(m5, unreal.MaterialExpressionMultiply, -300, 150)
link(tex_node, "RGB", mul_screen_glow, "A")
link(glow_scale, "", mul_screen_glow, "B")
out(tex_node, "RGB", MP.MP_BASE_COLOR)
out(mul_screen_glow, "", MP.MP_EMISSIVE_COLOR)
out(expr(m5, unreal.MaterialExpressionConstant, -300, 320, r=0.1), "", MP.MP_METALLIC)
out(expr(m5, unreal.MaterialExpressionConstant, -300, 400, r=0.25), "", MP.MP_ROUGHNESS)
finish(m5)

print("ALL 5 KELP FARM MATERIALS CREATED SUCCESSFULLY!")
