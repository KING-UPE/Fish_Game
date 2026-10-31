"""Blue Signal setup 2/4: data tables (run inside the editor).
DT_Items, DT_Recipes, DT_Buildables (row order = hotbar order), DT_Phases (row order = phase order).
Edit the values here and re-run to rebalance; the game reads the tables at runtime."""
import json
import unreal
import warnings

warnings.simplefilter("ignore")

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
PATH = "/Game/Blue/Data"
PROTO = "/Game/LevelPrototyping/Meshes"
CHAMFER = f"{PROTO}/SM_ChamferCube.SM_ChamferCube"
CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"
CUBE = "/Engine/BasicShapes/Cube.Cube"
CONE = "/Engine/BasicShapes/Cone.Cone"
SPHERE = "/Engine/BasicShapes/Sphere.Sphere"

MESHES = "/Game/Blue/Meshes"
SM_CONVEYOR = f"{MESHES}/SM_Conveyor.SM_Conveyor"
SM_CONVEYOR_STRIPE = f"{MESHES}/SM_ConveyorStripe.SM_ConveyorStripe"
SM_SMELTER_CORE = f"{MESHES}/SM_SmelterCore.SM_SmelterCore"
SM_ASSEMBLER_CORE = f"{MESHES}/SM_AssemblerCore.SM_AssemblerCore"
SM_MACHINE_GANTRY = f"{MESHES}/SM_MachineGantry.SM_MachineGantry"
SM_TOWER_SUPPORT = f"{MESHES}/SM_TowerSupport.SM_TowerSupport"
SM_FOUNDATION = f"{MESHES}/SM_FoundationTile.SM_FoundationTile"
SM_HOPPER = f"{MESHES}/SM_Hopper.SM_Hopper"
SM_ROBOT_ARM = f"{MESHES}/SM_RobotArm.SM_RobotArm"
SM_SCANNER = f"{MESHES}/SM_Scanner.SM_Scanner"
SM_CONSOLE = f"{MESHES}/SM_ConsoleTerminal.SM_ConsoleTerminal"
SM_STORAGE = f"{MESHES}/SM_StorageCrate.SM_StorageCrate"
SM_FLUID_TANK = f"{MESHES}/SM_FluidTank.SM_FluidTank"
SM_PIPE_STRAIGHT = f"{MESHES}/SM_PipeStraight.SM_PipeStraight"
SM_PIPE_CORNER = f"{MESHES}/SM_PipeCorner.SM_PipeCorner"
SM_PIPE_STAND = f"{MESHES}/SM_PipeStand.SM_PipeStand"
SM_ANTENNA = f"{MESHES}/SM_SignalAntenna.SM_SignalAntenna"
SM_DISH = f"{MESHES}/SM_SignalDish.SM_SignalDish"


def color(r, g, b, a=1.0):
    return {"R": r, "G": g, "B": b, "A": a}


def stack(item, count):
    return {"Item": item, "Count": count}


def line(speaker, text, duration=0, style="Normal"):
    return {"Speaker": speaker, "Text": text, "Duration": duration, "Style": style}


def table(name, struct, rows):
    full = f"{PATH}/{name}"
    if EAL.does_asset_exist(full):
        dt = EAL.load_asset(full)
    else:
        factory = unreal.DataTableFactory()
        factory.struct = struct
        dt = TOOLS.create_asset(name, PATH, unreal.DataTable, factory)
        print("CREATED:", full)
    ok = unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(dt, json.dumps(rows))
    EAL.save_asset(full)
    print(f"FILLED: {full} rows={len(rows)} ok={ok}")


# ---------------------------------------------------------------- items
ITEMS = [
    ("ScrapMetal", "Scrap Metal", color(0.45, 0.47, 0.5)),
    ("CoralOre", "Coral Ore", color(0.95, 0.38, 0.45)),
    ("SteelBar", "Steel Bar", color(0.78, 0.8, 0.84)),
    ("CoralIngot", "Coral Ingot", color(1.0, 0.48, 0.32)),
    ("SteelPlate", "Steel Plate", color(0.45, 0.58, 0.72)),
    ("CoralSheet", "Coral Sheet", color(1.0, 0.68, 0.52)),
    ("Wire", "Wire", color(0.95, 0.55, 0.15)),
    # Phase 2+
    ("BlackSand", "Black Sand", color(0.12, 0.11, 0.12)),
    ("Glass", "Glass", color(0.6, 0.9, 1.0)),
    ("Brine", "Brine", color(0.2, 0.45, 0.65)),
    ("Glowkelp", "Glowkelp", color(0.2, 1.0, 0.6)),
    ("FreshWater", "Fresh Water", color(0.55, 0.8, 1.0)),
    ("Salt", "Salt", color(0.95, 0.95, 0.92)),
    ("Frame", "Frame", color(0.6, 0.62, 0.66)),
    ("Lens", "Lens", color(0.5, 0.95, 1.0)),
    ("Float", "Float", color(0.95, 0.85, 0.3)),
    ("Biofuel", "Biofuel", color(0.35, 0.55, 0.1)),
    ("GlimmerPearl", "Glimmer Pearl", color(0.85, 0.95, 1.0)),
]
table("DT_Items", unreal.FGItemRow.static_struct(),
      [{"Name": n, "DisplayName": d, "Color": c} for n, d, c in ITEMS])

# ---------------------------------------------------------------- recipes
def recipe(name, machine, inputs, outputs, time):
    return {"Name": name, "Machine": machine, "Inputs": inputs, "Outputs": outputs, "CraftTime": time}


RECIPES = [
    recipe("SteelBar", "Smelter", [stack("ScrapMetal", 2)], [stack("SteelBar", 1)], 2.0),
    recipe("CoralIngot", "Smelter", [stack("CoralOre", 2)], [stack("CoralIngot", 1)], 2.0),
    recipe("SteelPlate", "Press", [stack("SteelBar", 2)], [stack("SteelPlate", 1)], 3.0),
    recipe("CoralSheet", "Press", [stack("CoralIngot", 1)], [stack("CoralSheet", 1)], 2.0),
    recipe("Wire", "WireMill", [stack("CoralIngot", 1)], [stack("Wire", 3)], 2.0),
    recipe("Glass", "Kiln", [stack("BlackSand", 3)], [stack("Glass", 1)], 2.5),
    recipe("FreshWater", "Desalinator", [stack("Brine", 2)], [stack("FreshWater", 1), stack("Salt", 1)], 2.0),
    recipe("Frame", "Assembler", [stack("SteelPlate", 2), stack("Wire", 4)], [stack("Frame", 1)], 4.0),
    recipe("Lens", "Assembler", [stack("Glass", 1), stack("Wire", 2)], [stack("Lens", 1)], 3.0),
    recipe("Float", "Assembler", [stack("Glowkelp", 2), stack("SteelPlate", 1)], [stack("Float", 1)], 3.0),
    recipe("Biofuel", "KelpDryer", [stack("Glowkelp", 3)], [stack("Biofuel", 1)], 2.0),
    recipe("Glowkelp", "KelpFarm", [stack("Brine", 1)], [stack("Glowkelp", 1)], 4.0),
]
table("DT_Recipes", unreal.FGRecipeRow.static_struct(), RECIPES)

# ---------------------------------------------------------------- buildables (row order = hotbar order)
def buildable(name, display, kind, cost, size, height, mesh, col, phase, desc, **extra):
    # Every field is always present: a missing column makes the editor pop up a blocking
    # "import problems" dialog when the table is filled from Python.
    row = {"Name": name, "DisplayName": display, "Kind": kind, "MachineType": "None", "Cost": cost,
           "Size": {"X": size[0], "Y": size[1]}, "Height": height, "Mesh": mesh,
           "TopMesh": "None", "TopScale": {"X": 0.5, "Y": 0.5, "Z": 0.5},
           "Color": col, "AccentColor": color(1.0, 0.55, 0.1), "PowerUse": 0, "PowerOutput": 0,
           "ExtractItem": "None", "ExtractInterval": 2.0, "BufferSize": 10,
           "bNeedsWater": False, "bNoNode": False, "FuelItem": "None", "FuelTime": 4.0, "Pollution": 0.0,
           "Phase": phase, "Description": desc}
    row.update(extra)
    return row


BUILDABLES = [
    buildable("Solar", "Solar Panel", "Generator", [stack("ScrapMetal", 8)], (2, 2), 70, SM_FOUNDATION,
              color(0.85, 0.88, 0.92), 1, "Salvaged panel array. Generates 10 power from the sun.",
              PowerOutput=10, TopMesh=SM_ANTENNA, TopScale={"X": 0.85, "Y": 0.85, "Z": 0.6},
              AccentColor=color(0.1, 0.45, 0.95)),
    buildable("SalvageCrane", "Salvage Crane", "Extractor", [stack("ScrapMetal", 12)], (2, 2), 220, SM_MACHINE_GANTRY,
              color(0.92, 0.65, 0.1), 1, "Heavy automated crane. Pulls scrap metal from wreckage.",
              ExtractItem="ScrapMetal", ExtractInterval=2.0, PowerUse=4, BufferSize=20,
              TopMesh=SM_ROBOT_ARM, TopScale={"X": 0.75, "Y": 0.75, "Z": 0.6}, AccentColor=color(1.0, 0.8, 0.2)),
    buildable("SeabedDrill", "Seabed Drill", "Extractor", [stack("SteelBar", 10)], (2, 2), 200, SM_TOWER_SUPPORT,
              color(0.25, 0.35, 0.42), 1, "Deep core pneumatic drill. Extracts coral ore.",
              ExtractItem="CoralOre", ExtractInterval=2.0, PowerUse=4, BufferSize=20,
              TopMesh=SM_HOPPER, TopScale={"X": 0.8, "Y": 0.8, "Z": 0.5}, AccentColor=color(1.0, 0.4, 0.45)),
    buildable("Smelter", "Smelter", "Machine", [stack("ScrapMetal", 15)], (3, 3), 240, SM_SMELTER_CORE,
              color(0.35, 0.38, 0.42), 1, "High-temp arc smelter: Scrap -> Steel Bar, Coral -> Ingot.",
              MachineType="Smelter", PowerUse=6, BufferSize=20,
              TopMesh=SM_HOPPER, TopScale={"X": 0.6, "Y": 0.6, "Z": 0.35}, AccentColor=color(1.0, 0.45, 0.05)),
    buildable("Press", "Press", "Machine", [stack("SteelBar", 10), stack("CoralIngot", 4)], (3, 2), 210, SM_MACHINE_GANTRY,
              color(0.28, 0.36, 0.46), 1, "Hydraulic stamper: Bars -> Steel Plates, Ingots -> Sheets.",
              MachineType="Press", PowerUse=5, BufferSize=20,
              TopMesh=SM_CONSOLE, TopScale={"X": 0.6, "Y": 0.6, "Z": 0.35}, AccentColor=color(0.3, 0.75, 1.0)),
    buildable("WireMill", "Wire Mill", "Machine", [stack("SteelPlate", 6), stack("CoralIngot", 4)], (3, 2), 180, SM_SCANNER,
              color(0.42, 0.28, 0.18), 1, "Precision wire extrusion: Coral Ingot -> 3 High-conductivity Wire.",
              MachineType="WireMill", PowerUse=5, BufferSize=30,
              TopMesh=SM_CONSOLE, TopScale={"X": 0.5, "Y": 0.5, "Z": 0.4}, AccentColor=color(0.95, 0.55, 0.15)),
    buildable("Storage", "Storage Crate", "Storage", [stack("SteelPlate", 8)], (2, 2), 140, SM_STORAGE,
              color(0.82, 0.85, 0.88), 1, "Heavy pressurized cargo container. Stores 200 items.",
              BufferSize=200, AccentColor=color(0.95, 0.55, 0.1)),
    buildable("Belt", "Belt", "Belt", [stack("SteelBar", 1)], (1, 1), 35, SM_CONVEYOR,
              color(0.2, 0.22, 0.25), 1, "Motorized roller conveyor belt."),
    # ---- Phase 2: Strangers
    buildable("SandDredger", "Sand Dredger", "Extractor", [stack("SteelPlate", 6), stack("Wire", 10)], (2, 2), 180, SM_TOWER_SUPPORT,
              color(0.22, 0.24, 0.28), 2, "Heavy bucket-wheel dredge: Gathers black mineral sand.",
              ExtractItem="BlackSand", ExtractInterval=2.0, PowerUse=4, BufferSize=20,
              TopMesh=SM_HOPPER, TopScale={"X": 0.7, "Y": 0.7, "Z": 0.4}, AccentColor=color(0.6, 0.6, 0.65)),
    buildable("SeaPump", "Sea Pump", "Extractor", [stack("SteelPlate", 4), stack("Wire", 6)], (2, 2), 160, SM_FLUID_TANK,
              color(0.15, 0.35, 0.65), 2, "High-volume submersible sea intake pump for Brine.",
              ExtractItem="Brine", ExtractInterval=2.0, PowerUse=3, BufferSize=20, bNeedsWater=True,
              TopMesh=SM_PIPE_STRAIGHT, TopScale={"X": 0.5, "Y": 0.5, "Z": 0.5}, AccentColor=color(0.2, 0.75, 1.0)),
    buildable("Kiln", "Kiln", "Machine", [stack("SteelBar", 10), stack("CoralSheet", 6)], (2, 2), 190, SM_SMELTER_CORE,
              color(0.6, 0.35, 0.22), 2, "Thermal sintering kiln: Black Sand -> Optical Glass.",
              MachineType="Kiln", PowerUse=5, BufferSize=30,
              TopMesh=SM_PIPE_CORNER, TopScale={"X": 0.5, "Y": 0.5, "Z": 0.4}, AccentColor=color(1.0, 0.55, 0.1)),
    buildable("Assembler", "Assembler", "Machine", [stack("SteelPlate", 10), stack("Wire", 20)], (3, 3), 240, SM_ASSEMBLER_CORE,
              color(0.85, 0.88, 0.92), 2, "Dual-stage robotic assembly cell (Frames, Lenses, Floats).",
              MachineType="Assembler", PowerUse=8, BufferSize=30,
              TopMesh=SM_ROBOT_ARM, TopScale={"X": 0.7, "Y": 0.7, "Z": 0.35}, AccentColor=color(0.3, 0.95, 0.6)),
    buildable("KelpFarm", "Kelp Farm", "Machine", [stack("SteelPlate", 6), stack("CoralSheet", 6)], (3, 3), 90, SM_FOUNDATION,
              color(0.12, 0.3, 0.25), 2, "Hydroponic growth bed for bioluminescent Glowkelp.",
              MachineType="KelpFarm", PowerUse=3, BufferSize=30,
              TopMesh=SM_FLUID_TANK, TopScale={"X": 0.65, "Y": 0.65, "Z": 0.35}, AccentColor=color(0.2, 1.0, 0.6)),
    buildable("Desalinator", "Desalinator", "Machine", [stack("SteelPlate", 8), stack("Wire", 10)], (2, 2), 190, SM_FLUID_TANK,
              color(0.75, 0.8, 0.85), 2, "Multi-stage flash evaporator: Brine -> Fresh Water + Salt.",
              MachineType="Desalinator", PowerUse=4, BufferSize=30,
              TopMesh=SM_PIPE_STAND, TopScale={"X": 0.5, "Y": 0.5, "Z": 0.5}, AccentColor=color(0.4, 0.85, 1.0)),
    buildable("KelpDryer", "Kelp Dryer", "Machine", [stack("SteelPlate", 6)], (2, 2), 170, SM_SMELTER_CORE,
              color(0.32, 0.36, 0.2), 2, "Thermal dehydrator: Glowkelp -> Biofuel briquettes.",
              MachineType="KelpDryer", PowerUse=3, BufferSize=30,
              TopMesh=SM_CONSOLE, TopScale={"X": 0.6, "Y": 0.6, "Z": 0.3}, AccentColor=color(0.7, 0.9, 0.2)),
    buildable("KelpBurner", "Kelp Burner", "Generator", [stack("SteelPlate", 10), stack("CoralSheet", 4)], (2, 2), 200, SM_SMELTER_CORE,
              color(0.22, 0.2, 0.18), 2, "Industrial thermal power generator (burns Biofuel for 30 MW).",
              PowerOutput=30, FuelItem="Biofuel", FuelTime=6.0, Pollution=1.0, BufferSize=20,
              TopMesh=SM_PIPE_STRAIGHT, TopScale={"X": 0.45, "Y": 0.45, "Z": 0.6}, AccentColor=color(1.0, 0.35, 0.05)),
    buildable("Platform", "Floating Platform", "Platform", [stack("Float", 2), stack("SteelPlate", 1)], (4, 4), 40, SM_FOUNDATION,
              color(0.45, 0.48, 0.52), 2, "Modular floating steel foundation for factory expansion on water."),
    buildable("Translator", "Translator", "Translator", [stack("Frame", 4), stack("Lens", 4), stack("Wire", 12)], (2, 2), 240, SM_TOWER_SUPPORT,
              color(0.18, 0.22, 0.32), 2, "Optical bio-acoustic translation terminal for Glimmer communication.",
              PowerUse=6, TopMesh=SM_DISH, TopScale={"X": 0.85, "Y": 0.85, "Z": 0.45}, AccentColor=color(0.3, 0.9, 1.0)),
    buildable("TradeBuoy", "Trade Buoy", "TradeBuoy", [stack("Float", 4), stack("Wire", 10), stack("Lens", 1)], (2, 2), 130, CYLINDER,
              color(1.0, 0.45, 0.1), 2, "Where Glimmers come to trade. Place it at the water's edge or on a platform.",
              bNeedsWater=True, BufferSize=999, TopMesh=SPHERE, TopScale={"X": 0.5, "Y": 0.5, "Z": 0.35},
              AccentColor=color(0.3, 0.9, 1.0)),
]
table("DT_Buildables", unreal.FGBuildableRow.static_struct(), BUILDABLES)

# ---------------------------------------------------------------- phases
ECHO, ISLA, SKYE = "Echo", "Isla", "Skye"
PHASES = [
    {
        "Name": "Phase1",
        "Title": "I'm alive",
        "TowerPart": "Tower Base",
        "Requirements": [stack("SteelPlate", 40), stack("CoralSheet", 30), stack("Wire", 60)],
        "Intro": [
            line(ECHO, "The Paper Kite is in pieces. Pieces are useful. Look at the scrap by the wreck and press E. Hold E to keep gathering."),
            line(ECHO, "That ring on the sand is the Signal Tower site. Feed it what it needs and we can talk to Earth."),
            line(ECHO, "Top left: what the tower needs. Top right: power and inventory. Pink rocks by the water are coral ore."),
        ],
        "MessageHome": [
            line(ISLA, "Skye, it's Mum. I'm alive."),
            line(ISLA, "I'm coming home. I promise."),
        ],
        "FlashbackTitle": "Count My Fish",
        "Flashback": [
            line("", "Seven years ago. A kitchen. Rain on the window."),
            line(SKYE, "How many fish did I draw, Mum?"),
            line(ISLA, "...Five?"),
            line(SKYE, "Wrong! Six! You're not even looking!"),
            line(ISLA, "Okay. Laptop closed. Show me. One... two..."),
            line(SKYE, "...six! See? You have to really look."),
        ],
        "Reply": [
            line(SKYE, "Mum! Mum, you're alive! Everyone kept saying... I didn't believe them."),
            line(SKYE, "When are you coming home? I drew you something. Count them properly this time!"),
        ],
        "bReplyHasDrawing": True,
    },
    {
        "Name": "Phase2",
        "Title": "Strangers",
        "TowerPart": "Receiver Dish",
        "Requirements": [stack("Frame", 30), stack("Lens", 20), stack("GlimmerPearl", 3)],
        "Intro": [
            line(ECHO, "The dish needs Frames and Lenses. Lenses need glass, glass needs black sand. There's a dark patch on the north beach."),
            line(ECHO, "New machines are on your hotbar. Press Tab for the second page: Sea Pump, Kelp Farm, Platforms and more."),
            line(ECHO, "And... something is moving under the water to the east. Something that glows."),
            line(ECHO, "If those lights are what I think they are, we'll need a Translator. And something they'd want to trade for."),
        ],
        "MessageHome": [
            line(ISLA, "There are people here, Skye. They glow."),
            line(ISLA, "They talk in pictures. Like your drawings."),
        ],
        "FlashbackTitle": "You Always Leave",
        "Flashback": [
            line("", "Skye is nine. The night Isla tells her about the mission."),
            line(SKYE, "Two years? You always choose work!"),
            line(SKYE, "Dad would never have left!"),
            line("", "A door slams."),
            line(ISLA, "...I'm sorry, sweetheart."),
        ],
        "Reply": [
            line(SKYE, "Glowing people?! Are they nice? I drew them. Count them!"),
        ],
        "bReplyHasDrawing": True,
    },
]
table("DT_Phases", unreal.FGPhaseRow.static_struct(), PHASES)
print("DATA DONE")
