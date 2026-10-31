"""Create and bind high-fidelity Satisfactory-grade multi-materials
to all custom crafted 3D models in FishGame (Unreal Engine 5.8).
"""
import unreal

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MAT_PATH = "/Game/Blue/Materials"
MESH_PATH = "/Game/Blue/Meshes"

# 1. Base Machine Material
base_mat = unreal.load_object(None, f"{MAT_PATH}/M_Machine.M_Machine")
if not base_mat:
    raise RuntimeError("Base material M_Machine not found!")

def create_instance(name, params):
    full = f"{MAT_PATH}/{name}"
    if EAL.does_asset_exist(full):
        mi = unreal.load_object(None, f"{full}.{name}")
    else:
        mi = TOOLS.create_asset(name, MAT_PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    
    MEL.set_material_instance_parent(mi, base_mat)
    for key, value in params.items():
        if isinstance(value, tuple):
            MEL.set_material_instance_vector_parameter_value(mi, key, unreal.LinearColor(*value))
        else:
            MEL.set_material_instance_scalar_parameter_value(mi, key, float(value))
    EAL.save_loaded_asset(mi)
    return mi

# 2. Satisfactory Industrial Material Suite
INSTANCES = {
    # Dark Gunmetal Industrial Chassis
    "M_Chassis_Dark": create_instance("MI_Chassis_Dark", {
        "Color": (0.13, 0.14, 0.16, 1.0), "Metallic": 0.85, "Roughness": 0.32, "Glow": 0.0
    }),
    # Polished Machined Steel
    "M_Steel_Bright": create_instance("MI_Steel_Bright", {
        "Color": (0.75, 0.77, 0.82, 1.0), "Metallic": 0.95, "Roughness": 0.16, "Glow": 0.0
    }),
    # FICSIT-style Safety Orange Trim
    "M_Accent_Orange": create_instance("MI_Accent_Orange", {
        "Color": (0.95, 0.42, 0.04, 1.0), "Metallic": 0.25, "Roughness": 0.35, "Glow": 0.2
    }),
    # High-Visibility Warning Yellow / Hazard
    "M_Hazard_Stripe": create_instance("MI_Hazard_Stripe", {
        "Color": (0.95, 0.75, 0.05, 1.0), "Metallic": 0.1, "Roughness": 0.38, "Glow": 0.5
    }),
    # Glowing Cyan/Teal Diagnostics Display Screen
    "M_Emissive_Screen": create_instance("MI_Emissive_Screen", {
        "Color": (0.05, 0.85, 1.0, 1.0), "Metallic": 0.0, "Roughness": 0.1, "Glow": 6.0
    }),
    # Intensely Blooming Molten Arc Chamber (2800°C)
    "M_Furnace_Glow": create_instance("MI_Furnace_Glow", {
        "Color": (1.0, 0.32, 0.02, 1.0), "Metallic": 0.0, "Roughness": 0.2, "Glow": 12.0
    }),
    # Vulcanized Dark Conveyor Rubber
    "M_Rubber_Dark": create_instance("MI_Rubber_Dark", {
        "Color": (0.07, 0.07, 0.08, 1.0), "Metallic": 0.05, "Roughness": 0.85, "Glow": 0.0
    }),
    # Off-White Aerospace Starship Hull
    "M_Aerospace_Hull": create_instance("MI_Aerospace_Hull", {
        "Color": (0.78, 0.80, 0.82, 1.0), "Metallic": 0.4, "Roughness": 0.45, "Glow": 0.0
    }),
    # Scorched Re-entry Carbon Tiles
    "M_Scorched_Tiles": create_instance("MI_Scorched_Tiles", {
        "Color": (0.06, 0.06, 0.06, 1.0), "Metallic": 0.2, "Roughness": 0.9, "Glow": 0.0
    }),
}

print(f"Created/updated {len(INSTANCES)} high-fidelity PBR material instances.")

# 3. Bind Material Instances to every Mesh Slot
MESHES = [
    "SM_SmelterCore", "SM_AssemblerCore", "SM_StorageCrate", "SM_SignalAntenna",
    "SM_Conveyor", "SM_MachineGantry", "SM_FluidTank", "SM_SignalDish",
    "SM_CoralOreNode", "SM_ScrapMetalPile", "SM_TowerSupport", "SM_RobotArm",
    "SM_ConsoleTerminal", "SM_Hopper", "SM_WreckHull", "SM_FoundationTile"
]

bound_count = 0
for name in MESHES:
    sm = unreal.load_object(None, f"{MESH_PATH}/{name}.{name}")
    if not sm:
        continue
    
    modified = False
    for idx, mat_slot in enumerate(sm.static_materials):
        slot_name = str(mat_slot.material_slot_name)
        # Find matching material instance
        target_mi = None
        for key, mi in INSTANCES.items():
            if key.lower() in slot_name.lower() or slot_name.lower() in key.lower():
                target_mi = mi
                break
        
        # Fallbacks for specific meshes
        if not target_mi:
            if "Screen" in slot_name or "Console" in slot_name:
                target_mi = INSTANCES["M_Emissive_Screen"]
            elif "Glow" in slot_name or "Furnace" in slot_name:
                target_mi = INSTANCES["M_Furnace_Glow"]
            elif "Orange" in slot_name or "Accent" in slot_name:
                target_mi = INSTANCES["M_Accent_Orange"]
            elif "Hazard" in slot_name or "Stripe" in slot_name:
                target_mi = INSTANCES["M_Hazard_Stripe"]
            elif "Steel" in slot_name:
                target_mi = INSTANCES["M_Steel_Bright"]
            elif "Rubber" in slot_name:
                target_mi = INSTANCES["M_Rubber_Dark"]
            else:
                target_mi = INSTANCES["M_Chassis_Dark"]
        
        sm.set_material(idx, target_mi)
        modified = True
        print(f"  {name} Slot {idx} [{slot_name}] -> {target_mi.get_name()}")
        bound_count += 1
    
    if modified:
        EAL.save_loaded_asset(sm)

print(f"SUCCESS: Bound {bound_count} multi-material slots across all high-poly models!")
