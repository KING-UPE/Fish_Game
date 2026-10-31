"""Import Seabed Drill textures and create PBR materials:
  /Game/Blue/Materials/M_HardenedTungsten
  /Game/Blue/Materials/M_DarkSteel
  /Game/Blue/Materials/M_AmberBeacon
  /Game/Blue/Materials/M_FactoryDecals
"""
import unreal
import os

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MP = unreal.MaterialProperty

SAVED_DIR = r"D:\Game\FishGame\Saved"
TEX_PATH = "/Game/Blue/Textures"
MAT_PATH = "/Game/Blue/Materials"

# 1. Import Textures
tex_tasks = []
for name in ["T_SeabedDrill_Decals_D", "T_SeabedDrill_Decals_E"]:
    file_path = os.path.join(SAVED_DIR, f"{name}.png")
    task = unreal.AssetImportTask()
    task.filename = file_path
    task.destination_path = TEX_PATH
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = True
    tex_tasks.append(task)

TOOLS.import_asset_tasks(tex_tasks)
print("Textures imported successfully.")

tex_d = unreal.load_object(None, f"{TEX_PATH}/T_SeabedDrill_Decals_D")
tex_e = unreal.load_object(None, f"{TEX_PATH}/T_SeabedDrill_Decals_E")
print(f"Loaded tex_d: {tex_d is not None}, tex_e: {tex_e is not None}")

# Helper functions for material building
def get_or_create_material(name):
    full = f"{MAT_PATH}/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        for leftover in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, leftover)
    else:
        mat = TOOLS.create_asset(name, MAT_PATH, unreal.Material, unreal.MaterialFactoryNew())
    return mat

def expr(mat, cls, x, y, **props):
    node = MEL.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        node.set_editor_property(k, v)
    return node

def const(mat, val, x, y):
    return expr(mat, unreal.MaterialExpressionConstant, x, y, r=val)

def const3(mat, rgb, x, y):
    return expr(mat, unreal.MaterialExpressionConstant3Vector, x, y, constant=unreal.LinearColor(*rgb, 1.0))

def vparam(mat, name, color, x, y):
    return expr(mat, unreal.MaterialExpressionVectorParameter, x, y, parameter_name=name, default_value=unreal.LinearColor(*color))

def sparam(mat, name, val, x, y):
    return expr(mat, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=name, default_value=val)

def link(a, a_out, b, b_in):
    MEL.connect_material_expressions(a, a_out, b, b_in)

def out(node, node_out, prop):
    MEL.connect_material_property(node, node_out, prop)

def finish(mat):
    MEL.recompile_material(mat)
    EAL.save_asset(mat.get_path_name())
    print(f"Material {mat.get_name()} compiled and saved.")

# -----------------------------------------------------------------------------
# 1. M_HardenedTungsten: 0.95 metallic, 0.18 roughness, dark carbide sheen
# -----------------------------------------------------------------------------
m_tungsten = get_or_create_material("M_HardenedTungsten")
col_tung = vparam(m_tungsten, "BaseColor", (0.55, 0.58, 0.62, 1.0), -600, 0)
fresnel_t = expr(m_tungsten, unreal.MaterialExpressionFresnel, -400, -150)
fresnel_t.set_editor_property("exponent", 4.0)
fresnel_t.set_editor_property("base_reflect_fraction", 0.1)

edge_t = const3(m_tungsten, (0.85, 0.88, 0.92), -400, -250)
lerp_t = expr(m_tungsten, unreal.MaterialExpressionLinearInterpolate, -200, -50)
link(col_tung, "", lerp_t, "A")
link(edge_t, "", lerp_t, "B")
link(fresnel_t, "", lerp_t, "Alpha")

out(lerp_t, "", MP.MP_BASE_COLOR)
out(sparam(m_tungsten, "Metallic", 0.95, -400, 100), "", MP.MP_METALLIC)
out(sparam(m_tungsten, "Roughness", 0.18, -400, 200), "", MP.MP_ROUGHNESS)
finish(m_tungsten)

# -----------------------------------------------------------------------------
# 2. M_DarkSteel: structural iron, trusses, heavy conduits, accumulator brackets
# -----------------------------------------------------------------------------
m_steel = get_or_create_material("M_DarkSteel")
col_steel = vparam(m_steel, "BaseColor", (0.12, 0.13, 0.15, 1.0), -400, 0)
out(col_steel, "", MP.MP_BASE_COLOR)
out(sparam(m_steel, "Metallic", 0.85, -400, 100), "", MP.MP_METALLIC)
out(sparam(m_steel, "Roughness", 0.42, -400, 200), "", MP.MP_ROUGHNESS)
finish(m_steel)

# -----------------------------------------------------------------------------
# 3. M_AmberBeacon: High-intensity amber strobe beacon with bloom
# -----------------------------------------------------------------------------
m_beacon = get_or_create_material("M_AmberBeacon")
col_amber = vparam(m_beacon, "BaseColor", (1.0, 0.55, 0.05, 1.0), -600, 0)
emiss_mult = sparam(m_beacon, "EmissiveIntensity", 12.0, -600, 200)

mult_node = expr(m_beacon, unreal.MaterialExpressionMultiply, -300, 100)
link(col_amber, "", mult_node, "A")
link(emiss_mult, "", mult_node, "B")

out(col_amber, "", MP.MP_BASE_COLOR)
out(mult_node, "", MP.MP_EMISSIVE_COLOR)
out(const(m_beacon, 0.1, -400, 300), "", MP.MP_METALLIC)
out(const(m_beacon, 0.15, -400, 400), "", MP.MP_ROUGHNESS)
finish(m_beacon)

# -----------------------------------------------------------------------------
# 4. M_FactoryDecals: Stamped factory decals, hazard stripes & digital screens
# -----------------------------------------------------------------------------
m_decals = get_or_create_material("M_FactoryDecals")
tex_node_d = expr(m_decals, unreal.MaterialExpressionTextureSample, -600, -100)
if tex_d:
    tex_node_d.set_editor_property("texture", tex_d)

tex_node_e = expr(m_decals, unreal.MaterialExpressionTextureSample, -600, 200)
if tex_e:
    tex_node_e.set_editor_property("texture", tex_e)

glow_factor = sparam(m_decals, "GlowBoost", 3.5, -600, 450)
mult_emiss = expr(m_decals, unreal.MaterialExpressionMultiply, -300, 250)
link(tex_node_e, "RGB", mult_emiss, "A")
link(glow_factor, "", mult_emiss, "B")

out(tex_node_d, "RGB", MP.MP_BASE_COLOR)
out(mult_emiss, "", MP.MP_EMISSIVE_COLOR)
out(const(m_decals, 0.40, -400, 500), "", MP.MP_METALLIC)
out(const(m_decals, 0.32, -400, 600), "", MP.MP_ROUGHNESS)
finish(m_decals)

print("All Seabed Drill materials created and configured!")
