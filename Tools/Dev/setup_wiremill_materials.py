import os
import unreal

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
MP = unreal.MaterialProperty

TEXTURE_DIR = r"D:\Game\FishGame\Saved\Textures"
TEX_PATH = "/Game/Blue/Textures"
MAT_PATH = "/Game/Blue/Materials"

# 1. Import Textures
tex_tasks = []
for name in ["T_Decal_WireMill.png", "T_Screen_Terminal.png"]:
    filepath = os.path.join(TEXTURE_DIR, name)
    asset_name = os.path.splitext(name)[0]
    task = unreal.AssetImportTask()
    task.filename = filepath
    task.destination_path = TEX_PATH
    task.destination_name = asset_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    tex_tasks.append(task)

TOOLS.import_asset_tasks(tex_tasks)
print(f"Imported {len(tex_tasks)} textures.")

# Helper to create/update material
def get_or_create_mat(name):
    full = f"{MAT_PATH}/{name}"
    if EAL.does_asset_exist(full):
        mat = EAL.load_asset(full)
        MEL.delete_all_material_expressions(mat)
        for leftover in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, leftover)
        print("Updated material:", full)
    else:
        mat = TOOLS.create_asset(name, MAT_PATH, unreal.Material, unreal.MaterialFactoryNew())
        print("Created material:", full)
    return mat

def expr(mat, cls, x, y, **props):
    node = MEL.create_material_expression(mat, cls, x, y)
    for key, value in props.items():
        node.set_editor_property(key, value)
    return node

def link(a, a_out, b, b_in):
    MEL.connect_material_expressions(a, a_out, b, b_in)

def out(node, node_out, prop):
    MEL.connect_material_property(node, node_out, prop)

def finish(mat):
    MEL.recompile_material(mat)
    EAL.save_asset(mat.get_path_name())

# Helper for material instances
def create_or_update_mi(name, parent_asset, params):
    full = f"{MAT_PATH}/{name}"
    if EAL.does_asset_exist(full):
        mi = EAL.load_asset(full)
    else:
        mi = TOOLS.create_asset(name, MAT_PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent_asset)
    for k, v in params.items():
        if isinstance(v, (tuple, list)):
            MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
        else:
            MEL.set_material_instance_scalar_parameter_value(mi, k, float(v))
    EAL.save_asset(full)
    print(f"Configured MI: {full}")
    return mi

# Load base M_Machine
m_machine = EAL.load_asset(f"{MAT_PATH}/M_Machine")

# 1. MI_BurnishedSteel: 0.85 metallic, 0.2 roughness
create_or_update_mi("MI_BurnishedSteel", m_machine, {
    "Color": (0.80, 0.82, 0.85, 1.0),
    "Metallic": 0.85,
    "Roughness": 0.20,
    "Glow": 0.0
})

# 2. MI_CopperTrim: 0.9 metallic, 0.25 roughness
create_or_update_mi("MI_CopperTrim", m_machine, {
    "Color": (0.94, 0.54, 0.26, 1.0),
    "Metallic": 0.90,
    "Roughness": 0.25,
    "Glow": 0.0
})

# 3. MI_LaserCyan: Bright cyan laser scanner aperture glow
create_or_update_mi("MI_LaserCyan", m_machine, {
    "Color": (0.05, 0.95, 1.0, 1.0),
    "Metallic": 0.0,
    "Roughness": 0.1,
    "Glow": 15.0
})

# 4. MI_DarkMechanical: Dark cast iron / chassis sub-components
create_or_update_mi("MI_DarkMechanical", m_machine, {
    "Color": (0.12, 0.13, 0.15, 1.0),
    "Metallic": 0.70,
    "Roughness": 0.45,
    "Glow": 0.0
})

# 5. MI_BeaconLights: Green running indicator
create_or_update_mi("MI_BeaconLights", m_machine, {
    "Color": (0.15, 0.95, 0.35, 1.0),
    "Metallic": 0.1,
    "Roughness": 0.2,
    "Glow": 8.0
})

# 6. M_WireMillDecal: Stamped factory decals material with diffuse texture and metallic/roughness
t_decal = EAL.load_asset(f"{TEX_PATH}/T_Decal_WireMill")
m_decal = get_or_create_mat("M_WireMillDecal")
ts_decal = expr(m_decal, unreal.MaterialExpressionTextureSample, -400, 0, texture=t_decal)
out(ts_decal, "RGB", MP.MP_BASE_COLOR)
const_met = expr(m_decal, unreal.MaterialExpressionConstant, -200, 100, r=0.4)
out(const_met, "", MP.MP_METALLIC)
const_rou = expr(m_decal, unreal.MaterialExpressionConstant, -200, 200, r=0.35)
out(const_rou, "", MP.MP_ROUGHNESS)
finish(m_decal)

# 7. M_ConsoleScreen: Telemetry LCD display with emissive glow
t_screen = EAL.load_asset(f"{TEX_PATH}/T_Screen_Terminal")
m_screen = get_or_create_mat("M_ConsoleScreen")
ts_screen = expr(m_screen, unreal.MaterialExpressionTextureSample, -600, 0, texture=t_screen)
out(ts_screen, "RGB", MP.MP_BASE_COLOR)
const_met2 = expr(m_screen, unreal.MaterialExpressionConstant, -300, 100, r=0.1)
out(const_met2, "", MP.MP_METALLIC)
const_rou2 = expr(m_screen, unreal.MaterialExpressionConstant, -300, 200, r=0.15)
out(const_rou2, "", MP.MP_ROUGHNESS)
mul_emiss = expr(m_screen, unreal.MaterialExpressionMultiply, -300, -100)
link(ts_screen, "RGB", mul_emiss, "A")
const_glow = expr(m_screen, unreal.MaterialExpressionConstant, -450, -50, r=2.8)
link(const_glow, "", mul_emiss, "B")
out(mul_emiss, "", MP.MP_EMISSIVE_COLOR)
finish(m_screen)

print("All Wire Mill materials successfully created and compiled!")
