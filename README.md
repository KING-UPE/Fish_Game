# Blue Signal

A story-driven factory-building game made in **Unreal Engine 5.8**.

Isla, an engineer, crash-lands on an ocean planet she calls **Blue**. To reach her 10-year-old daughter
**Skye** on Earth, she builds a giant **Signal Tower** from the wreck and the planet's materials. Every finished
tower phase sends a message home, plays a memory (flashback) and brings back a reply from Skye. Each reply
includes one of her drawings, and the drawings come live from the **Fish Game API**.

Full story, phases, machines and recipes: [`Design/Blue_Signal.md`](Design/Blue_Signal.md).

## Status

| Phase | State |
|---|---|
| 1. "I'm alive": salvage, smelting, pressing, wire, belts, power, Tower Base | **Playable** |
| 2. "Strangers": black sand + glass, sea pump, kelp, assembler, fuel burners, floating platforms, Glimmers, Translator, Trade Buoy trades | **Playable** |
| 3-5 + endings | Planned |

## Requirements

- **Unreal Engine 5.8** (an installed/source build; the project expects it at `D:\UE_5.8`, see below).
- **Visual Studio 2022 or Build Tools** with the *Game development with C++* workload and MSVC.
- **.NET Framework 4.8 SDK** (Unreal's build tools need it).
- **Git LFS** (`git lfs install`): all `.uasset` / `.umap` files are stored with LFS.
- Internet access for the Fish Game API (the game falls back to bundled pictures when offline).

## Setup

```bat
git lfs install
git clone https://github.com/KING-UPE/Fish_Game.git
cd Fish_Game
```

1. If your engine is not at `D:\UE_5.8`, set it once: `setx UE_ROOT "C:\Path\To\UE_5.8"` (new terminal after).
2. Compile the game module: double-click **`BuildGame.bat`** (takes a few minutes the first time).
3. Start the editor: double-click **`LaunchEditor.bat`**. The map `L_Blue` opens.
4. Press **Play**.

> The `.uproject` has no engine association because this engine isn't registered with the Epic launcher.
> If you use a launcher-installed UE 5.8 instead, right-click `FishGame.uproject` → *Switch Unreal Engine
> version*.

## Controls

| Key | Action |
|---|---|
| WASD / mouse / Space | Move, look, jump |
| **E** | Gather from a resource (hold to keep gathering) · take a machine's output and hand it inputs · hand items to the tower |
| **1-9** | Choose a building (again to put it away) |
| **Left click** | Place the building (belts: click an orange output, then a blue input) |
| **R** | Rotate |
| **Right click / Q** | Cancel |
| **X** | Dismantle (refunds the cost) |
| **Tab** | Next page of buildings |
| **1-4** | Answer a picture: Skye's drawing ("How many fish did I draw?") or a Glimmer's trade (fish = crates they want, chests = pearls they give) |

## How it is built

- **C++ game module** (`Source/FishGame`): the factory core and the story.
  - `FGBuildable` (machines, extractors, generators, storage) with item buffers and ports.
  - `FGBelt` (floating belts that carry items), `FGResourceNode`, `FGTowerSite` (phases + tower sections).
  - `FGPlayerController`: inventory, grid build mode with ghost preview, belts, interaction, story queue.
  - `FGHUD`: phase goals, power, inventory, hotbar, subtitles, flashback overlay, Skye's drawing.
  - `FGFishApi`: the Fish Game API client (live picture + counts, offline fallback, history).
- **Data tables** (`Content/Blue/Data`): items, recipes, buildings (hotbar order) and story phases. The game
  reads them at runtime; balance changes don't need C++.
- **Blueprints**: the first-person character and controller come from the UE template; the controller is
  re-parented to `FGPlayerController`.

### Fish Game API

`GET https://marcconrad.com/uob/fish/api.php?out=json&base64=no` →
`{ "question": "<picture url>", "fish": 4, "chest": 3 }`. The game downloads the picture, shows it as Skye's
drawing and asks how many fish it shows. Every picture is kept so the story's twist can re-show old drawings.

## Tools

- `Tools/Setup/*.py`: rebuild the game content from scratch inside the editor (materials, data tables, map,
  player hookup). Run in order with the editor open, e.g. `python Tools/ue.py Tools/Setup/02_data.py`.
- `Tools/Dev/*.py`: test helpers (drop a test factory into the map, drive building from scripts).
- Console commands in Play mode: `FGGive <Item> <Count>`, `FGCompletePhase`, `FGSkipStory`, `FGSelect <slot>`,
  `FGClick`, `FGInteract`, `FGLook <pitch> <yaw>`, `FGTeleport <x> <y> <z>`.
