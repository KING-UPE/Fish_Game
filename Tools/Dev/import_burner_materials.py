import os
import unreal

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
MP = unreal.MaterialProperty

TEXTURE_DIR = r"D:\Game\FishGame\Saved\BurnerTextures"
TEX_PATH = "/Game/Blue/Textures"
MAT_PATH = "/Game/Blue/Materials"

# 1. Import Textures
texture_files = [
    "T_BurnerDecals_D.png",
    "T_BurnerDecals_E.png",
    "T_BurnerDecals_ORM.png",
    "T_CombustionSight_D.png",
    "T_CombustionSight_E.png",
    "T_SparkArrestor_D.png"
]

tasks = []
for tf in texture_files:
    task = unreal.AssetImportTask()
    task.filename = os.path.join(TEXTURE_DIR, tf)
    task.destination_path = TEX_PATH
    task.destination_name = os.path.splitext(tf)[0]
    task.replace_existing = True
    task.automated = True
    task.save = True
    tasks.append(task)

TOOLS.import_asset_tasks(tasks)
print(f"Imported {len(tasks)} textures to {TEX_PATH}")

# Helper functions for materials
def get_or_create_material(name):
    full = f"{MAT_PATH}/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        for leftover in list(MEL.get_material_expressions(mat)):
            try:
                MEL.delete_material_expression(mat, leftover)
            except Exception:
                pass
    else:
        mat = TOOLS.create_asset(name, MAT_PATH, unreal.Material, unreal.MaterialFactoryNew())
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
    print(f"Compiled & saved material: {mat.get_name()}")

# -------------------------------------------------------------
# Material 1: M_CastIronScorched (Heat-scorched black cast iron body)
# Metallic 0.4, Roughness 0.7, dark charcoal Base Color
# -------------------------------------------------------------
m_cast = get_or_create_material("M_CastIronScorched")
col_cast = expr(m_cast, unreal.MaterialExpressionVectorParameter, -400, 0,
                parameter_name="Color", default_value=unreal.LinearColor(0.12, 0.12, 0.13, 1.0))
met_cast = expr(m_cast, unreal.MaterialExpressionScalarParameter, -400, 150,
                parameter_name="Metallic", default_value=0.4)
rough_cast = expr(m_cast, unreal.MaterialExpressionScalarParameter, -400, 250,
                  parameter_name="Roughness", default_value=0.7)
out(col_cast, "", MP.MP_BASE_COLOR)
out(met_cast, "", MP.MP_METALLIC)
out(rough_cast, "", MP.MP_ROUGHNESS)
finish(m_cast)

# -------------------------------------------------------------
# Material 2: M_CombustionGlow (Glowing combustion core, 5.0x orange bloom)
# -------------------------------------------------------------
m_fire = get_or_create_material("M_CombustionGlow")
tex_fire_d = unreal.load_object(None, f"{TEX_PATH}/T_CombustionSight_D.T_CombustionSight_D")
tex_fire_e = unreal.load_object(None, f"{TEX_PATH}/T_CombustionSight_E.T_CombustionSight_E")

node_fire_d = expr(m_fire, unreal.MaterialExpressionTextureSample, -500, -100, texture=tex_fire_d)
node_fire_e = expr(m_fire, unreal.MaterialExpressionTextureSample, -500, 200, texture=tex_fire_e)
glow_mult = expr(m_fire, unreal.MaterialExpressionScalarParameter, -500, 400,
                 parameter_name="GlowIntensity", default_value=5.0)

mul_em = expr(m_fire, unreal.MaterialExpressionMultiply, -250, 250)
link(node_fire_e, "RGB", mul_em, "A")
link(glow_mult, "", mul_em, "B")

out(node_fire_d, "RGB", MP.MP_BASE_COLOR)
out(mul_em, "", MP.MP_EMISSIVE_COLOR)
out(expr(m_fire, unreal.MaterialExpressionConstant, -200, 450, r=0.1), "", MP.MP_ROUGHNESS)
finish(m_fire)

# -------------------------------------------------------------
# Material 3: M_BurnerDecals (Factory signage, decals, screen)
# -------------------------------------------------------------
m_decal = get_or_create_material("M_BurnerDecals")
tex_dec_d = unreal.load_object(None, f"{TEX_PATH}/T_BurnerDecals_D.T_BurnerDecals_D")
tex_dec_e = unreal.load_object(None, f"{TEX_PATH}/T_BurnerDecals_E.T_BurnerDecals_E")
tex_dec_orm = unreal.load_object(None, f"{TEX_PATH}/T_BurnerDecals_ORM.T_BurnerDecals_ORM")

node_dec_d = expr(m_decal, unreal.MaterialExpressionTextureSample, -500, -150, texture=tex_dec_d)
node_dec_orm = expr(m_decal, unreal.MaterialExpressionTextureSample, -500, 100, texture=tex_dec_orm)
node_dec_e = expr(m_decal, unreal.MaterialExpressionTextureSample, -500, 350, texture=tex_dec_e)

em_scale = expr(m_decal, unreal.MaterialExpressionScalarParameter, -500, 500,
                 parameter_name="ScreenGlow", default_value=3.5)
mul_dec_e = expr(m_decal, unreal.MaterialExpressionMultiply, -250, 380)
link(node_dec_e, "RGB", mul_dec_e, "A")
link(em_scale, "", mul_dec_e, "B")

out(node_dec_d, "RGB", MP.MP_BASE_COLOR)
out(node_dec_orm, "B", MP.MP_METALLIC)
out(node_dec_orm, "G", MP.MP_ROUGHNESS)
out(mul_dec_e, "", MP.MP_EMISSIVE_COLOR)
finish(m_decal)

# -------------------------------------------------------------
# Material 4: M_Copper (Copper generator windings & busbars)
# Metallic 0.95, Roughness 0.25, Copper Color (0.95, 0.64, 0.54)
# -------------------------------------------------------------
m_copper = get_or_create_material("M_Copper")
col_copper = expr(m_copper, unreal.MaterialExpressionVectorParameter, -400, 0,
                  parameter_name="Color", default_value=unreal.LinearColor(0.955, 0.638, 0.538, 1.0))
met_copper = expr(m_copper, unreal.MaterialExpressionScalarParameter, -400, 150,
                  parameter_name="Metallic", default_value=0.95)
rough_copper = expr(m_copper, unreal.MaterialExpressionScalarParameter, -400, 250,
                    parameter_name="Roughness", default_value=0.25)
out(col_copper, "", MP.MP_BASE_COLOR)
out(met_copper, "", MP.MP_METALLIC)
out(rough_copper, "", MP.MP_ROUGHNESS)
finish(m_copper)

# -------------------------------------------------------------
# Material 5: M_Ceramic (High-voltage porcelain bushings)
# Metallic 0.05, Roughness 0.12, Glazed Dark Amber/Brown
# -------------------------------------------------------------
m_ceramic = get_or_create_material("M_Ceramic")
col_ceramic = expr(m_ceramic, unreal.MaterialExpressionVectorParameter, -400, 0,
                   parameter_name="Color", default_value=unreal.LinearColor(0.18, 0.09, 0.04, 1.0))
met_ceramic = expr(m_ceramic, unreal.MaterialExpressionScalarParameter, -400, 150,
                   parameter_name="Metallic", default_value=0.05)
rough_ceramic = expr(m_ceramic, unreal.MaterialExpressionScalarParameter, -400, 250,
                     parameter_name="Roughness", default_value=0.12)
out(col_ceramic, "", MP.MP_BASE_COLOR)
out(met_ceramic, "", MP.MP_METALLIC)
out(rough_ceramic, "", MP.MP_ROUGHNESS)
finish(m_ceramic)

# -------------------------------------------------------------
# Material 6: M_SparkArrestor (Spark arrestor mesh cage)
# -------------------------------------------------------------
m_mesh = get_or_create_material("M_SparkArrestor")
tex_mesh_d = unreal.load_object(None, f"{TEX_PATH}/T_SparkArrestor_D.T_SparkArrestor_D")
node_mesh_d = expr(m_mesh, unreal.MaterialExpressionTextureSample, -500, -100, texture=tex_mesh_d)
out(node_mesh_d, "RGB", MP.MP_BASE_COLOR)
out(expr(m_mesh, unreal.MaterialExpressionConstant, -300, 100, r=0.75), "", MP.MP_METALLIC)
out(expr(m_mesh, unreal.MaterialExpressionConstant, -300, 200, r=0.65), "", MP.MP_ROUGHNESS)
finish(m_mesh)

# -------------------------------------------------------------
# Material 7: M_SteelTrim (Galvanized structural steel trim & bolts)
# -------------------------------------------------------------
m_steel = get_or_create_material("M_SteelTrim")
col_steel = expr(m_steel, unreal.MaterialExpressionVectorParameter, -400, 0,
                 parameter_name="Color", default_value=unreal.LinearColor(0.62, 0.65, 0.7, 1.0))
met_steel = expr(m_steel, unreal.MaterialExpressionScalarParameter, -400, 150,
                 parameter_name="Metallic", default_value=0.85)
rough_steel = expr(m_steel, unreal.MaterialExpressionScalarParameter, -400, 250,
                   parameter_name="Roughness", default_value=0.35)
out(col_steel, "", MP.MP_BASE_COLOR)
out(met_steel, "", MP.MP_METALLIC)
out(rough_steel, "", MP.MP_ROUGHNESS)
finish(m_steel)

print("ALL BURNER MATERIALS SUCCESSFULLY CONFIGURED AND SAVED!")
