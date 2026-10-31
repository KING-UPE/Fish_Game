# M0 Audit — what exists (2026-10-31)

Explore-agent summary of `Source/FishGame`, `Content/Blue/Data` and `Tools/` at commit `f3998e9`, plus the
producer's hardware check. Use it to decide what to keep and what to rewrite.

## Hardware (measured)
| Thing | Value | Consequence |
|---|---|---|
| GPU | **Intel Iris Xe** (integrated, ~2 GB shared, driver 32.0.101.7088) | Software Lumen only; no HW RT; MegaLights/Epic can't be measured here |
| CPU | i7-1165G7, 4 cores / 8 threads | Slow C++ builds and shader compiles |
| RAM | 15.7 GB, **0.4 GB free** with editor + browser + Spotify + IDE open | One Blender at a time; UBT drops to 1 action |
| Disk | C: 51 GB free, **D: 16 GB free** (project drive) | Tight texture/DDC budget |
| Tools | uv, winget, Python 3.14, git-lfs, gh present; **Blender missing** (installing via winget) | |
| LFS | 136 MB local store | GitHub free LFS = 1 GB storage + 1 GB/month bandwidth |

## C++ (`Source/FishGame`, ~4.8k lines)
- `FGTypes.h`: row structs (ItemStack, ItemRow, RecipeRow, BuildableRow, StoryLine, PhaseRow), enums (BuildableKind x9, LineStyle). Solid.
- `AFGBuildable` (690 lines): grid footprint, one input port at -X and one output at +X, In/Out buffer TMaps, refunds, global power statics. Visual = Row.Mesh stretched non-uniformly to the footprint with a flat-colour MID on slot 0, plus a TopMesh. Solid logic, placeholder visuals.
- Subclasses: `AFGMachine` (runs the first recipe whose inputs it has — **no recipe picker**), `AFGExtractor`, `AFGGenerator` (fuel burn), `AFGStorage`, `AFGPlatform`: solid. `AFGTranslator`, `AFGTradeBuoy`: prototype but complete.
- `AFGTowerSite`: phase index, Delivered, GlimmerTrust, OceanHealth, OnPhaseStarted/Completed delegates, section meshes. Solid.
- `AFGResourceNode` (hand-gather) solid. `AFGGlimmer` cosmetic swim loop. `UFGGameData` function library with hard-coded DT and mesh paths.
- `AFGPlayerController` (**1398 lines**): inventory, build, belts, interact, dismantle, story queue, puzzles, hints, save/load, cheats. Works, but monolithic. **Legacy BindKey input**, not Enhanced Input.
- `AFGHUD`: **everything drawn on Canvas** (DrawRect/DrawText). **No UMG anywhere.**
- `UFGSaveGame`, `AFGWeather`: WIP, untested (commit d4423cd; not on `main`).

### Building and belts
- Grid **CellSize = 100 cm** (must migrate to 800), world-aligned, footprint from Row.Size, R rotates 90°.
- Ghost = a real AFGBuildable with bGhost (no tick/collision, M_Ghost green/red). Valid when the ground is tagged
  "Buildable", slope normal Z >= 0.8, no 2D overlap within 400 cm height, affordable. Extractors snap to nodes
  within 350 cm. Water buildings need Z <= 70 or a platform. Platforms at Z = -20.
- **No foundations, no vertical stacking, no port-to-port snapping.**
- Belts: one AFGBelt per **straight** line output->input, max 30 m, 180 cm/s, 45 cm spacing. **No splines,
  splitters, mergers, lifts or tiers.** Body = stretched engine cube.
- Belt items: one ISM per belt (good), but every tick rewrites all instance transforms + MarkRenderStateDirty.
  Items back up visibly when blocked.

### Power, save, weather, story, Fish API
- Power: **one global pool**, summed every frame over all buildables; ratio slows crafting. No poles, cables,
  circuits, fuses, batteries.
- Save: USaveGame slot "BlueSignal", v1. Saves buildables, belts (index pairs), inventory, hints, phase,
  delivered, trust, ocean health, player transform. **Not saved:** items on belts, machine progress, fuel,
  extractor timers, trade state, broken belts, PuzzlesSolved, Fish API history, story queue, weather. Autosave
  every 60 s + on quit + **on PIE end, so every PIE run resumes the last run** (`FGNewGame` wipes it).
- Weather (P3): storm scheduler, sun/fog dimming, MPC_Ocean Storm/Murk, belts snap unless near a Breakwater,
  lightning rods, Row.Pollution lowers OceanHealth. **Not wired:** no AFGWeather in L_Blue, no P3 row, no
  MPC_Ocean asset, no Breakwater/LightningRod/ReefFilter rows, no rain/lightning on the HUD.
- Story: PhaseRow carries Intro, MessageHome, FlashbackTitle + Flashback (letterboxed text), Reply, drawing
  puzzle (4 options); title cards; one-shot Echo hints; "relay broken" hook from phase index 4. **Missing:**
  choices, endings, voice/audio, Sequencer cinematics; only 2 of 5 phases written; trust never read.
- `UFGFishApi` (GameInstance subsystem): JSON (6 s timeout) then image (8 s) -> texture. Fallback looks for
  `/Game/Blue/FishApi/T_Fish_F#_C#` — **that folder doesn't exist, so offline the drawing is skipped and trades
  fail.** History in memory only. **A second request while busy is dropped silently** (caller never answered).
- Exec: FGCompletePhase, FGGive Item N, FGSkipStory, FGSelect slot, FGClick, FGInteract, FGLook p y,
  FGTeleport x y z, FGSave, FGNewGame.

## Data tables (`Tools/Setup/02_data.py`)
- DT_Items (DisplayName, Color): 18. DT_Recipes (Machine, Inputs[], Outputs[], CraftTime): 12.
- DT_Buildables: 19 (8 P1, 11 P2), row order = hotbar order. Fields: DisplayName, Kind, MachineType, Cost[], Size,
  Height, Mesh, TopMesh, TopScale, Color, AccentColor, PowerUse, PowerOutput, ExtractItem, ExtractInterval,
  bNeedsWater, bNoNode, FuelItem, FuelTime, Pollution, BufferSize, Phase, Description.
- DT_Phases: 2. Fields: Title, TowerPart, Requirements[], Intro[], MessageHome[], FlashbackTitle, Flashback[],
  Reply[], bReplyHasDrawing (StoryLine = Speaker, Text, Duration, Style).

## Tools
- `Tools/ue.py`: reusable MCP client (JSON-RPC -> execute_python_code on :18765).
- Reusable: `Setup/01..04`, Dev `start_pie/end_pie`, `test_building`, `test_phase2`, `test_factory_line`,
  `test_layout_report`, `place_batch`, `take_scenic_shot`, `take_panoramic`, `set_low/high_graphics`, `ping`.
- Dead here (need Blender): `Setup/blender_model_factory*.py`, `build_landscape_and_nature.py`, `Dev/test_export_cube.py`.
- **Not reproducible from a clone:** `Setup/import_highpoly`, `import_custom_crafted`, `import_part2`,
  `import_nature_meshes` read 61 files from git-ignored `Saved/DownloadedAssets`.
- Risky: `update_materials_and_level.py` rewrites the text of other scripts.
- ~110 Dev junk probes (`check_*`, `inspect_*`, `list_*`, `test_gs*`, `test_import*`, `test_tex*`, `test_mat*`).

## Placeholder inventory (Content/Blue)
- Test junk: SM_TestBox/Box2/Cube/Import/Mesh/MultiMat/Pyramid, T_TestTex/T_TestTexture, T_TestDecal.
- Likely orphans: SM_IslandDome, SM_WreckHull + MI_WreckHull/Burnt/Stripe, SM_Conveyor/Sides/Stripe.
- ~10 kit meshes stretched/tinted to stand in for 19 machines; Trade Buoy = cylinder + sphere; belt items and
  ports = engine cubes. **Everything visual is placeholder.**

## Top risks
1. **Logistics won't scale**: straight point-to-point belts, 1 in / 1 out port, per-belt ISM re-dirtied every
   tick, actor loops for power/pollution/placement/save. Needs a central belt subsystem with spline belts and
   shared per-item ISMs.
2. **UI + controller need replacing**: 1400-line controller, Canvas HUD, legacy input => UMG (CommonUI),
   Enhanced Input, controller split into components.
3. **Persistence, power, pipeline**: save untested and lossy, no versioning; global power pool; P3-5 and endings
   missing; art not reproducible from the repo.
4. **Hardware**: the dev machine can't run or measure the Satisfactory-1.0 Target tier (see Plan.md).
