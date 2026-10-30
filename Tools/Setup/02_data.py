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
           "Phase": phase, "Description": desc}
    row.update(extra)
    return row


BUILDABLES = [
    buildable("Solar", "Solar Panel", "Generator", [stack("ScrapMetal", 8)], (2, 2), 45, CHAMFER,
              color(0.04, 0.09, 0.25), 1, "Salvaged panel. Makes 10 power from the sun.",
              PowerOutput=10, TopMesh=CUBE, TopScale={"X": 0.9, "Y": 0.9, "Z": 0.15},
              AccentColor=color(0.1, 0.3, 0.8)),
    buildable("SalvageCrane", "Salvage Crane", "Extractor", [stack("ScrapMetal", 12)], (2, 2), 220, CYLINDER,
              color(0.9, 0.62, 0.08), 1, "Sits on a Scrap Metal pile and pulls out scrap.",
              ExtractItem="ScrapMetal", ExtractInterval=2.0, PowerUse=4, BufferSize=20,
              TopMesh=CUBE, TopScale={"X": 1.2, "Y": 0.18, "Z": 0.12}, AccentColor=color(1.0, 0.75, 0.15)),
    buildable("SeabedDrill", "Seabed Drill", "Extractor", [stack("SteelBar", 10)], (2, 2), 170, CYLINDER,
              color(0.22, 0.32, 0.38), 1, "Sits on a Coral Ore patch and drills out coral.",
              ExtractItem="CoralOre", ExtractInterval=2.0, PowerUse=4, BufferSize=20,
              TopMesh=CONE, TopScale={"X": 0.55, "Y": 0.55, "Z": 0.45}, AccentColor=color(1.0, 0.4, 0.45)),
    buildable("Smelter", "Smelter", "Machine", [stack("ScrapMetal", 15)], (3, 3), 220, CHAMFER,
              color(0.42, 0.22, 0.15), 1, "Scrap Metal -> Steel Bar.  Coral Ore -> Coral Ingot.",
              MachineType="Smelter", PowerUse=6, BufferSize=20,
              TopMesh=CYLINDER, TopScale={"X": 0.25, "Y": 0.25, "Z": 0.6}, AccentColor=color(1.0, 0.45, 0.1)),
    buildable("Press", "Press", "Machine", [stack("SteelBar", 10), stack("CoralIngot", 4)], (3, 2), 190, CHAMFER,
              color(0.28, 0.36, 0.46), 1, "Steel Bars -> Steel Plate.  Coral Ingot -> Coral Sheet.",
              MachineType="Press", PowerUse=5, BufferSize=20,
              TopMesh=CUBE, TopScale={"X": 0.6, "Y": 0.85, "Z": 0.25}, AccentColor=color(0.4, 0.75, 1.0)),
    buildable("WireMill", "Wire Mill", "Machine", [stack("SteelPlate", 6), stack("CoralIngot", 4)], (3, 2), 160, CHAMFER,
              color(0.33, 0.2, 0.11), 1, "Coral Ingot -> 3 Wire.",
              MachineType="WireMill", PowerUse=5, BufferSize=30,
              TopMesh=CYLINDER, TopScale={"X": 0.5, "Y": 0.5, "Z": 0.35}, AccentColor=color(0.95, 0.55, 0.15)),
    buildable("Storage", "Storage Crate", "Storage", [stack("SteelPlate", 8)], (2, 2), 140, CHAMFER,
              color(0.3, 0.32, 0.27), 1, "Holds 200 of anything. Belts can feed it and pull from it.",
              BufferSize=200, AccentColor=color(0.8, 0.8, 0.7)),
    buildable("Belt", "Belt", "Belt", [stack("SteelBar", 1)], (1, 1), 10, CUBE,
              color(0.12, 0.13, 0.15), 1, "Floating belt from an orange output to a blue input."),
]
table("DT_Buildables", unreal.FGBuildableRow.static_struct(), BUILDABLES)

# ---------------------------------------------------------------- phases
ECHO, ISHANI, NEELA = "Echo", "Ishani", "Neela"
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
            line(ISHANI, "Neela, it's Mum. I'm alive."),
            line(ISHANI, "I'm coming home. I promise."),
        ],
        "FlashbackTitle": "Count My Fish",
        "Flashback": [
            line("", "Seven years ago. A kitchen. Rain on the window."),
            line(NEELA, "How many fish did I draw, Mum?"),
            line(ISHANI, "...Five?"),
            line(NEELA, "Wrong! Six! You're not even looking!"),
            line(ISHANI, "Okay. Laptop closed. Show me. One... two..."),
            line(NEELA, "...six! See? You have to really look."),
        ],
        "Reply": [
            line(NEELA, "Mum! Mum, you're alive! Everyone kept saying... I didn't believe them."),
            line(NEELA, "When are you coming home? I drew you something. Count them properly this time!"),
        ],
        "bReplyHasDrawing": True,
    },
    {
        "Name": "Phase2",
        "Title": "Strangers",
        "TowerPart": "Receiver Dish",
        "Requirements": [stack("Frame", 30), stack("Lens", 20)],
        "Intro": [
            line(ECHO, "New parts unlocked. The dish needs Frames and Lenses: glass from black sand, and an Assembler to put it together."),
            line(ECHO, "Also... something is moving under the water. Something that glows."),
        ],
        "MessageHome": [
            line(ISHANI, "There are people here, Neela. They glow."),
            line(ISHANI, "They talk in pictures. Like your drawings."),
        ],
        "FlashbackTitle": "You Always Leave",
        "Flashback": [
            line("", "Neela is nine. The night Ishani tells her about the mission."),
            line(NEELA, "Two years? You always choose work!"),
            line(NEELA, "Appa would never have left!"),
            line("", "A door slams."),
            line(ISHANI, "...I'm sorry, Duwa."),
        ],
        "Reply": [
            line(NEELA, "Glowing people?! Are they nice? I drew them. Count them!"),
        ],
        "bReplyHasDrawing": True,
    },
]
table("DT_Phases", unreal.FGPhaseRow.static_struct(), PHASES)
print("DATA DONE")
