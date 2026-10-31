"""Import crane textures and build crane PBR materials in /Game/Blue/Materials."""
import unreal

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
PATH = "/Game/Blue/Materials"
MP = unreal.MaterialProperty

# 1. Import textures
tasks = []
for name, filename in [("T_HazardStripes", r"D:\Game\FishGame\Saved\Textures\T_HazardStripes.png"),
                       ("T_CraneDecals", r"D:\Game\FishGame\Saved\Textures\T_CraneDecals.png")]:
    task = unreal.AssetImportTask()
    task.filename = filename
    task.destination_path = PATH
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = True
    tasks.append(task)

TOOLS.import_asset_tasks(tasks)
print("Textures imported.")

tex_hazard = EAL.load_asset(f"{PATH}/T_HazardStripes")
tex_decals = EAL.load_asset(f"{PATH}/T_CraneDecals")

def clean_material(name):
    full = f"{PATH}/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        for leftover in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, leftover)
    else:
        mat = TOOLS.create_asset(name, PATH, unreal.Material, unreal.MaterialFactoryNew())
    return mat, full

# -------------------------------------------------------------
# M_CranePrimary: FICSIT High-Vis Yellow/Orange Frame Paint
# -------------------------------------------------------------
m, full = clean_material("M_CranePrimary")
col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -800, -100)
col.set_editor_property("parameter_name", "Color")
col.set_editor_property("default_value", unreal.LinearColor(0.92, 0.58, 0.08, 1.0))

met = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -800, 100)
met.set_editor_property("parameter_name", "Metallic")
met.set_editor_property("default_value", 0.60)

rou = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -800, 250)
rou.set_editor_property("parameter_name", "Roughness")
rou.set_editor_property("default_value", 0.35)

# Fresnel subtle edge sheen
fresnel = MEL.create_material_expression(m, unreal.MaterialExpressionFresnel, -600, -250)
fresnel.set_editor_property("exponent", 4.0)
fresnel.set_editor_property("base_reflect_fraction", 0.04)

edge_col = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -600, -380)
edge_col.set_editor_property("constant", unreal.LinearColor(1.0, 0.85, 0.5, 1.0))

lerp_col = MEL.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -350, -150)
MEL.connect_material_expressions(col, "", lerp_col, "A")
MEL.connect_material_expressions(edge_col, "", lerp_col, "B")
MEL.connect_material_expressions(fresnel, "", lerp_col, "Alpha")

# Glow / emissive support for FGBuildable
glow = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 420)
glow.set_editor_property("parameter_name", "Glow")
glow.set_editor_property("default_value", 0.0)

glow_mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 380)
MEL.connect_material_expressions(col, "", glow_mul, "A")
MEL.connect_material_expressions(glow, "", glow_mul, "B")

MEL.connect_material_property(lerp_col, "", MP.MP_BASE_COLOR)
MEL.connect_material_property(met, "", MP.MP_METALLIC)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.connect_material_property(glow_mul, "", MP.MP_EMISSIVE_COLOR)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CranePrimary")

# -------------------------------------------------------------
# M_CraneSteelDark: Cast weathered joint steel
# -------------------------------------------------------------
m, full = clean_material("M_CraneSteelDark")
col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -600, -100)
col.set_editor_property("parameter_name", "Color")
col.set_editor_property("default_value", unreal.LinearColor(0.12, 0.13, 0.16, 1.0))

met = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 100)
met.set_editor_property("parameter_name", "Metallic")
met.set_editor_property("default_value", 0.85)

rou = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 250)
rou.set_editor_property("parameter_name", "Roughness")
rou.set_editor_property("default_value", 0.45)

MEL.connect_material_property(col, "", MP.MP_BASE_COLOR)
MEL.connect_material_property(met, "", MP.MP_METALLIC)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CraneSteelDark")

# -------------------------------------------------------------
# M_CraneChrome: Polished hydraulic piston steel
# -------------------------------------------------------------
m, full = clean_material("M_CraneChrome")
col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -600, -100)
col.set_editor_property("parameter_name", "Color")
col.set_editor_property("default_value", unreal.LinearColor(0.88, 0.90, 0.92, 1.0))

met = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 100)
met.set_editor_property("parameter_name", "Metallic")
met.set_editor_property("default_value", 0.95)

rou = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 250)
rou.set_editor_property("parameter_name", "Roughness")
rou.set_editor_property("default_value", 0.12)

MEL.connect_material_property(col, "", MP.MP_BASE_COLOR)
MEL.connect_material_property(met, "", MP.MP_METALLIC)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CraneChrome")

# -------------------------------------------------------------
# M_CraneHazard: Hazard Chevrons using T_HazardStripes
# -------------------------------------------------------------
m, full = clean_material("M_CraneHazard")
tex_node = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, -100)
tex_node.set_editor_property("texture", tex_hazard)

met = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -500, 120)
met.set_editor_property("r", 0.25)

rou = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -500, 240)
rou.set_editor_property("r", 0.38)

MEL.connect_material_property(tex_node, "RGB", MP.MP_BASE_COLOR)
MEL.connect_material_property(met, "", MP.MP_METALLIC)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CraneHazard")

# -------------------------------------------------------------
# M_CraneDecal: Stamped Lore Decals using T_CraneDecals
# -------------------------------------------------------------
m, full = clean_material("M_CraneDecal")
tex_node = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -600, -100)
tex_node.set_editor_property("texture", tex_decals)

met = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -600, 120)
met.set_editor_property("r", 0.40)

rou = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -600, 240)
rou.set_editor_property("r", 0.45)

# Subtle emissive on decals so signs and readouts pop in shadows
emi_mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, 360)
MEL.connect_material_expressions(tex_node, "RGB", emi_mul, "A")
c_boost = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -550, 420)
c_boost.set_editor_property("r", 0.35)
MEL.connect_material_expressions(c_boost, "", emi_mul, "B")

MEL.connect_material_property(tex_node, "RGB", MP.MP_BASE_COLOR)
MEL.connect_material_property(met, "", MP.MP_METALLIC)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.connect_material_property(emi_mul, "", MP.MP_EMISSIVE_COLOR)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CraneDecal")

# -------------------------------------------------------------
# M_CraneEmissive: Digital Screen & LED Bloom Glow
# -------------------------------------------------------------
m, full = clean_material("M_CraneEmissive")
col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -600, -100)
col.set_editor_property("parameter_name", "Color")
col.set_editor_property("default_value", unreal.LinearColor(0.1, 0.85, 1.0, 1.0))

glow_val = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 100)
glow_val.set_editor_property("parameter_name", "Glow")
glow_val.set_editor_property("default_value", 5.0)

mul_emi = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, 0)
MEL.connect_material_expressions(col, "", mul_emi, "A")
MEL.connect_material_expressions(glow_val, "", mul_emi, "B")

rou = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -600, 240)
rou.set_editor_property("r", 0.20)

MEL.connect_material_property(col, "", MP.MP_BASE_COLOR)
MEL.connect_material_property(mul_emi, "", MP.MP_EMISSIVE_COLOR)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CraneEmissive")

# -------------------------------------------------------------
# M_CraneRubber: Carbon black vulcanized rubber
# -------------------------------------------------------------
m, full = clean_material("M_CraneRubber")
col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -600, -100)
col.set_editor_property("parameter_name", "Color")
col.set_editor_property("default_value", unreal.LinearColor(0.04, 0.04, 0.04, 1.0))

met = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -600, 100)
met.set_editor_property("r", 0.05)

rou = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -600, 240)
rou.set_editor_property("r", 0.82)

MEL.connect_material_property(col, "", MP.MP_BASE_COLOR)
MEL.connect_material_property(met, "", MP.MP_METALLIC)
MEL.connect_material_property(rou, "", MP.MP_ROUGHNESS)
MEL.recompile_material(m)
EAL.save_asset(full)
print("Configured M_CraneRubber")

print("All crane materials successfully configured!")
