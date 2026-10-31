# Blue Signal — Tech architecture (the rewrite)

Owner: engine-programmer. Status: **design, 2026-10-31**; no code yet. Implements Plan.md D6, D9-D13 and the
Plan §4 backlog. Units: cm, s, MW, items/min. GT = game-thread ms on the dev laptop (i7-1165G7, Iris Xe, Dev tier).

## 0. Budgets and rules
- Perf scenario `FGStressFactory 200`: 200 machines, ~400 belt segments, full belts (~12k items), poles + cables.
  Dev tier >= 30 fps. Factory GT budget <= 3.0 ms: clock 0.4, belt sim 0.5, belt item writes 1.0, power 0.05
  (topology rebuild <= 2 ms one-off), visuals + significance 0.5, build tool 0.2, UI 0.35.
- Buildables never tick as actors. One clock (`UFGFactorySubsystem`) drives the factory; work runs on change.
- No per-frame heap allocations, no per-frame MIDs: state reaches materials through **CustomPrimitiveData** (§5).
- Balance lives in DTs. Tunables without a row (curve limits, sag, significance distances, autosave interval) live
  in `UFGFactorySettings` (UDeveloperSettings, `DefaultGame.ini`). Each system has a `stat FG` cycle counter.

## 1. Module map (`Source/FishGame`)
| Class | Responsibility | From today |
|---|---|---|
| `FGTypes.h` | Row structs + enums (fields below) | kept, extended |
| `FGGrid.h` | `Foundation=800`, `SubCell=100`, `Half=50`, `WallH=400`; snap helpers | replaces `AFGBuildable::CellSize` |
| `UFGFactorySettings` | DT paths, tunables, MI/NS soft refs | replaces hard-coded paths in `UFGGameData` |
| `UFGGameData` | Static DT and asset access (API kept) | kept; reads paths from the settings |
| `UFGFactorySubsystem` | The one clock: power, then `FactoryTick` of every buildable, then belts, then junctions | new |
| `AFGBuildable` | Row, `FGuid BuildId`, buffers, refunds, ports, `State`, `FactoryTick(dt)` | kept; actor tick off, global power statics removed |
| `AFGMachine` | `SelectedRecipe`, `Clock` 0.5-2.5, `bStandby`, state machine | kept; no more "first recipe it can run" |
| `AFGExtractor` / `AFGGenerator` / `AFGStorage` | Logic as today; generators report output to their circuit | kept |
| `AFGTranslator` / `AFGTradeBuoy` / `AFGTowerSite` | As today; tower takes belts through a ring of input ports | kept |
| `AFGResourceNode` / `AFGGlimmer` / `AFGWeather` | As today; weather calls the power/belt subsystems instead of actor loops | kept |
| `UFGFishApiSubsystem` | Request queue, bundled fallbacks, persisted history (D11, M2) | kept, extended |
| `AFGStructure` | Foundation, wall, ramp, stairs, catwalk, floating platform; one mesh, no logic, no tick | new; absorbs `AFGPlatform` |
| `UFGPortComponent` | Scene comp: `Dir` In/Out, `Kind` Solid/Fluid, `Index`, `Linked`, `ChainId` | new; replaces fixed -X/+X ports |
| `UFGBeltSubsystem` | Segments to chains, item sim, ISM writes, port spatial hash | new; replaces `AFGBelt` logic |
| `AFGBeltSegment` | One placed belt: spline, spline meshes, frame LUT, `bBroken` | new; replaces `AFGBelt` |
| `AFGBeltItemRenderer` | One actor, one ISM per item type world-wide, instance block allocator | new |
| `AFGBeltLift` / `AFGSplitter` / `AFGMerger` | Lift = vertical segment; splitter 1-to-3, merger 3-to-1, 1-item buffer, round robin | new (M2) |
| `UFGPowerSubsystem` | Circuits, union-find rebuild on change, batteries, fuse, surges, history ring | new; replaces global pool |
| `UFGPowerConnectionComponent` | Connector on poles and powered buildables: `MaxCables`, cables, `CircuitId` | new |
| `AFGPowerPole` / `AFGPowerCable` / `AFGBattery` | Pole buildable; cable actor (catenary spline meshes); battery buildable | new |
| `UFGBuildableVisual` | Data asset per buildable: parts, roles, ports, snaps, state FX (§5) | new |
| `UFGBuildableVisualComponent` | Builds part comps from the DA (legacy stretched mesh if none), applies state, materialise | new; absorbs `ApplyVisuals` |
| `UFGVisualSubsystem` | Significance buckets, part animation, VFX/audio caps | new |
| `AFGHologram` | Preview actor from the same DA with `MI_Hologram`; zoop pool of 10 | new; replaces ghost `AFGBuildable` |
| `UFGPlacementSolver` | Pure functions: grid, snap points, validation (`EFGPlaceError`) | new; from the controller |
| `AFGPlayerController` | Owns components, IMC switching, restore on load (~250 lines) | rewritten (§6) |
| `UFGInventoryComponent` / `UFGBuildToolComponent` / `UFGInteractionComponent` / `UFGStoryComponent` | §6 | new; split from the controller |
| `UFGCheatManager` / `UFGTestLibrary` | Every `FG*` exec; static BlueprintCallable JSON dumps for Python | new; exec moved from the controller |
| `UFGSaveSubsystem` + `UFGSaveGame` | Versioned complete save, autosave rotation | new; schema v2 |
| `UFGUIManager` + `UFGWidget_*` | CommonUI layer stacks; C++ bases of every WBP | new; Canvas `AFGHUD` becomes a debug overlay |

**Data side (generic).** `Design/Data/<Name>.json` becomes `DT_<Name>` through one importer
(`Tools/Setup/import_data.py`, replaces `02_data.py`): map file name to struct (`Items`, `Recipes`, `Buildables`,
`Phases`, `Milestones`, `Research`...), check every key against the struct's UPROPERTYs (an unknown key is an
error), fill missing keys from the struct default before `fill_data_table_from_json_string` (avoids the blocking
dialog, CLAUDE.md §1.17), row order kept. New row fields (PascalCase = JSON key):
- `FFGItemRow`: `+StackSize`, `Form` (Solid/Fluid), `BeltMesh`, `Icon`, `Category`.
- `FFGRecipeRow`: `+DisplayName`, `bAlternate`, `UnlockedBy`, `bHandcraft`, `HandcraftTime`.
- `FFGBuildableRow`: `+Category`, `Visual` (soft `UFGBuildableVisual`; `Mesh/TopMesh/Color` stay as fallback),
  `Placement` (Grid/Structure/Node/Water/Wall/Free), `StructureType`, `InputPorts`, `OutputPorts` (fallback
  ports when no DA), `BeltSpeed` cm/s, `BeltRate` items/min, `MaxCables`, `CableMaxLength`, `BatteryCapacity`
  MW-min, `BatteryRate` MW, `ProtectRadius`, `WeatherFactor`, `MaxClock`, `ClockItem`. `Size` stays in 100 cm cells.
- New `FFGMilestoneRow`, `FFGResearchRow` follow the game designer's JSON; the struct mirrors it 1:1.

## 2. Belts
- **Segment.** `AFGBeltSegment`: 2-point Hermite spline (start/end location + tangent; tangent length 0.5 x chord,
  clamped 100-1200). Modes: Curved (default) or Straight. Limits: length 50-5600 cm, bend radius >= 200 cm,
  slope <= 35 deg, sampled every 25 cm; sample boxes overlap-tested against WorldStatic + buildables minus the end ports.
- **Mesh.** `SM_Belt_MkN_Seg` is authored 200 cm along +X; N = ceil(L/200) `USplineMeshComponent`s, each scaled
  to L/N. End caps `SM_Belt_MkN_End` at ports. Spline meshes stay Nanite if `r.Nanite.AllowSplineMeshes` holds on
  5.8, else LOD0 <= 3k tris + 2 LODs. Query-only collision on channel `FGBuildable` (dismantle and look traces).
  Scroll: material panner x CPD[4] speed (0 when the chain is stopped).
- **Frame LUT.** At build: position + quat every 25 cm (<= 225 samples, ~6 KB). Item placement lerps the LUT,
  never `GetLocationAtDistanceAlongSpline` at runtime.
- **Chains.** The subsystem merges segments linked end-to-start into `FFGBeltChain {Segments, Length,
  Speed, Spacing, Items, Head port, Tail port, Blocks, Bounds}`, rebuilt on topology change only.
  Items are a gap list `FFGBeltItem {uint16 Type; uint16 Flags; float Gap}` (gap to the item ahead / chain end) =
  8 B per item. Move: if `Gap[0] > 0` shrink it (everything moves, O(1)); else shrink the first gap > `Spacing`
  (`FirstSlack` cached), so items behind a block queue at `Spacing`. Head: item at the end goes to
  `Target->TryInsert(Item, PortIndex)`. Tail: when the last gap >= `Spacing`, pull `Source->TakeOutputFor(Port)`.
- **Tick.** In the clock: chains move (ParallelFor above 128 chains), then serial handoffs, then junctions
  (splitter/merger round robin over ports that accept). dt clamped to 0.1 s.
- **Tiers.** Row `BeltSpeed` + `BeltRate`; `Spacing = BeltSpeed * 60 / BeltRate`, >= 40 cm. Suggested
  (designer owns): Mk1 120 cm/s @ 60/min, Mk2 240 @ 120, Mk3 405 @ 270.
- **Rendering.** `AFGBeltItemRenderer`: one plain ISM per item type (not HISM; Nanite; no collision, no nav,
  `InstanceEndCullDistance` 12000). Each (chain, type) owns a **contiguous block** in that type's ISM, capacity
  ceil(L/Spacing) rounded to 16, first-fit free list; unused slots parked at scale 0. A chain that moved this
  tick rewrites its blocks with one `BatchUpdateInstancesTransforms(start, span, ..., bMarkRenderStateDirty=false)`
  each (incremental instance-data path; never `MarkRenderStateDirty` per frame, the audit's hot spot). Stopped
  or empty chains write nothing. Significance by chain bounds: < 50 m every frame; 50-120 m every 4th frame,
  staggered by chain id; > 120 m none (culled). A chain coming back into range rewrites in full.
- **Lifts** (M2): a vertical segment, 200-2000 cm in 100 steps, same sim, items upright. **Splitter/merger** (M2):
  `AFGBuildable`s with 4 ports, 50 cm half-cell placement, can be placed onto a belt (splits the segment in two).
- **Snapping.** Ports sit in a spatial hash (800 cm cells). The belt tool starts and ends on the nearest
  compatible free port within 150 cm of the aim (tangent = port forward) or on a free end (chain with no head:
  items queue at the end). A machine placed with a port within 50 cm of a free belt end, facing it, auto-links.
  Placing a belt from a free end continues that chain.
- **Storms.** `bBroken` on a segment stops its chain (items stay); repair with E as today.
- **Save.** Per segment: `Id, Row, P0, T0, P1, T1, Source{BuildId, Port}, Target{BuildId, Port}, bBroken,
  ItemIdx[] (uint16 into the save's item name table), ItemPos[] (cm from segment start)`.

## 3. Placement
- **Grid** (D10). World-aligned, yaw 0. Terrain: foundations snap XY to the 800 grid, top Z = round(hit Z, 50) +
  height (100/200/400 variants); machines on terrain snap to the 800 grid. On a foundation or platform top: XY
  on the 100 sub-grid, Z = top. Splitter/merger/pole/lift may use 50 cm. Extractors snap to nodes (350 cm),
  water buildings keep the waterline rule. Rotation: R / wheel, 90 deg steps; belts and cables are free.
- **Structures** (`AFGStructure`, Nanite, simple hand-made collision, no tick): Foundation 800x800 x
  100/200/400, Ramp 800x800 rise 200/400, Stairs, Wall 800x400 (+ window/door variants later), Catwalk 400x200
  (straight/corner/T/stairs), Floating platform 800x800 at Z = -20. Actors in M1; if structures exceed ~1500 or
  their primitives cost > 1 ms, move them to ISM batching in M7 (same API).
- **Snap points.** The DA lists `FFGSnapPoint {Name, Type, LocCm, YawDeg}`; Types: FoundationEdge, WallBase,
  WallTop, RampLow, RampHigh, StairBottom, StairTop, CatwalkEnd. Compatible: FoundationEdge with FoundationEdge,
  RampLow/High, StairBottom, CatwalkEnd, WallBase; WallTop with WallBase. Solver: hit structure, compatible snaps
  of it within 400 cm of the hit, nearest wins; hologram = target x yaw180 x inverse(own snap). A foundation hit on
  its top more than 200 cm from every edge stacks on top instead.
- **Nudge.** H locks the hologram; arrows move +-100 cm view-relative, PgUp/PgDn +-100 cm Z (Alt: 50); max 800 cm.
- **Zoop.** Hold Place 0.25 s on a structure: axis = dominant axis of (aim - start), count = round(|d|/size)+1, max
  10, pooled holograms; release places all only if all are valid and affordable (else one reason shown).
- **Hologram.** `AFGHologram` with `MI_Hologram`; CPD[0] = 0 valid (teal), 1 invalid (red). `EFGPlaceError`: None,
  OutOfRange, NotAffordable, Overlap, BadGround, TooSteep, NeedsNode, NeedsWater, Unsupported, Locked. Overlap =
  one `OverlapAnyTestByChannel` box shrunk 2 cm (replaces the 2D actor loop). Ground = tag "Buildable" or a
  structure top; terrain normal Z >= 0.8.
- **Materialise.** Parts swap to `MI_Materialise` (masked scan line) for the effect only, then back to their slot
  MIs (masked Nanite costs only while it plays). CPD[5] progress, CPD[6] bounds min Z, CPD[7] height; `NS_Materialise`
  + sound. 0.8 s machines, 0.4 s structures, zoop staggered 0.05 s. A buildable starts working only when done.
  Dematerialise = reverse 0.5 s, then refund + destroy.
- **Dismantle.** Look highlight = CustomDepth stencil 1 (teal), dismantle = stencil 2 (orange-red) through
  `M_PP_Outline` (Nanite-safe). Ctrl+click adds up to 64 targets; hold Place 0.6 s confirms. Refund = build cost +
  contents; overflow goes into an `AFGRefundCrate` (storage, saved, gone when empty). A structure with something
  resting on it (box 20 cm above its top) is refused unless that is selected too. Belts on a dismantled machine
  keep free ends and items; its cables are refunded with it.
- **Migration.** Footprints are already in 100 cm cells, so `Size` values stay. Level-placed and v1-saved buildables
  keep their exact transforms (`bLegacyPlaced`, never re-snapped). `AFGPlatform` rows map to `FloatingPlatform`.
  Tests move from FGLook + FGClick to `FGBuild` with explicit coordinates.

## 4. Power
- **Graph.** Nodes = `UFGPowerConnectionComponent` (DA socket `Power`); edges = `AFGPowerCable` (A, B). Pole Mk1:
  4 cables, cable max 5000 cm (row `CableMaxLength`). Powered buildables take 1 cable (wall outlets later).
- **Rebuild on change only.** Adding or removing a cable, pole or powered buildable sets `bTopologyDirty`; next
  clock: union-find over nodes, assign `CircuitId`, rebuild producer/consumer/battery lists (<= 2 ms for 1k nodes).
- **Totals are incremental.** A buildable calls `SetDemand(MW)` / `SetSupply(MW)` only when its value changes
  (state change, fuel out, weather step); the circuit adds the delta. Demand = `PowerUse x Clock^Exp` while
  Working (Exp in settings, default 1.32), else 0. Per tick: O(circuits).
- **Circuit** `{Id, Supply, Demand, BatteryStored, BatteryCap, BatteryRate, bTripped, History[60] at 1 Hz}`.
  Surplus charges batteries (<= rate); a deficit draws them; if Demand > Supply + available discharge, the
  **fuse trips**: every consumer is Unpowered, generators stop burning fuel, HUD alert. Reset: E on any pole or
  generator, the power panel, or `FGFuseReset`; re-trips after 1 s if still overloaded. No partial-speed power.
- **Cable mesh.** Parabola close to a catenary: z(t) = lerp(zA, zB, t) - 4 s t (1-t), sag s = 0.02 L + 15 cm, max
  200; N = clamp(ceil(L/400), 4, 16) spline meshes of `SM_Cable` (100 cm, 4 cm wide). No collision: dismantle picks
  the cable nearest the view ray within 30 cm (subsystem list). Rebuilt when an end moves.
- **Storms** (P3+, M4/M5). `AFGWeather` schedules strikes every 4-10 s near the player, weighted to the tallest
  powered things. A lightning rod (row `ProtectRadius`, default 3000) in range takes the strike: +1 Storm Crystal
  (today's behaviour) and `Surge(Circuit, Energy)` fills its batteries. Unprotected: the struck circuit trips +
  spark VFX on the hit pole/cable. Solar-type rows scale output by `1 - (1 - WeatherFactor) x Intensity`, pushed at 1 Hz.

## 5. Art contract (assembly.json to the engine)
- **Inputs.** `ArtSource/<id>/export/assembly.json` (part, mesh, offset_cm, slots) + `card.json` `"rig"` block:
  `{"parts": {"Drum": {"role": "Rotator", "axis": [0,1,0], "rate": 90}}, "ports": [{"name": "In0", "dir": "In",
  "kind": "Solid", "loc_cm": [-300,0,100], "yaw": 180}], "power": [0,0,350], "snaps": [...], "bounds_cm": [...]}`.
  A step after `ue_import.py` (`ue_visual.py`, owned by the pipeline) writes `DA_<Asset>_Visual` next to the meshes.
- **`UFGBuildableVisual`** (UPrimaryDataAsset): `Parts[] FFGVisualPart {Part, Mesh, OffsetCm, Rot, Role, Axis,
  Rate (deg/s or Hz at 100%), Amplitude (cm/deg), Phase, bCollision (Body only), AttachTo}`, `Ports[]
  FFGPortSpec {Name, Dir, Kind, Index, LocCm, YawDeg}`, `SnapPoints[]`, `PowerSocket`, `Bounds`, `WorkVFX`
  (NS + part + offset), `LoopWorking`, `LoopIdle`, `SfxStart`, `SfxStop`, `RampSeconds` = 0.6.
- **Roles.** Static, Rotator (spin about Axis), Piston (sine along Axis), Oscillator (sine rotation), StatusLight,
  PortFrame. Missing rig: name prefix decides (Body/Frame = Static, Light/Status = StatusLight, PortIn/PortOut =
  PortFrame); moving prefixes (Drum, Fan, Piston) need an explicit axis, else Static + an import warning.
- **CPD layout** (material-artist implements in `M_Factory_Master` / `MI_Hologram` / `MI_Materialise`): [0-2] status
  RGB, [3] status intensity, [4] work speed (scroll, pulse), [5] materialise progress, [6] bounds min Z,
  [7] height. Hologram: [0] valid/invalid/dismantle. Set once per state change, never per frame.
- **State to visuals** (`EFGMachineState`, set by logic only on change):

| State | Status light | Part speed | VFX | Audio |
|---|---|---|---|---|
| Constructing | off | 0 | NS_Materialise | build sfx |
| Working | green x20 | Clock (ramp 0.6 s) | WorkVFX on | LoopWorking |
| NoRecipe / Starved | amber x8, 0.5 Hz blink | 0 (ramp) | off | LoopIdle |
| Blocked (output full) | orange x8, 2 Hz blink | 0 | off | LoopIdle |
| Unpowered / tripped | red x6 | 0 | spark burst once | SfxStop |
| Standby (player) | dim white x2 | 0 | off | none |

- **Significance** (`UFGVisualSubsystem`, round robin 64 components per frame; distance + `WasRecentlyRendered(0.5)`):
  S0 < 25 m: parts at frame rate, VFX, audio. S1 25-60 m: parts at 20 Hz, VFX at Niagara low scalability, audio if
  within attenuation (30 m). S2 60-120 m: parts frozen, no VFX/audio, light static. S3 > 120 m or unseen 1 s: all
  off. Caps: 64 animated machines, 40 working NS, 24 machine loops (+ concurrency `SC_MachineLoop` max 16 per
  sound); nearest win. Moving parts have no collision and no children, so a transform update is cheap.

## 6. Input and UI
- **Enhanced Input** (`UFGInputConfig` DA lists them; template `IA_Move/IA_Look/IA_Jump` reused):
  - `IMC_Player` (0): Move, Look, Jump, Sprint (Shift), Crouch (C), Interact (E press; hold = gather / hold-to-craft),
    Primary (LMB), Secondary (RMB), BuildMenu (Q), Inventory (Tab), Dismantle (F), Hotbar (1-0, one action, Scalar
    modifier = slot), HotbarPage (wheel when no tool), Flashlight (V), Pause (Esc).
  - `IMC_Build` (1, while a hologram is up): Place (LMB press/hold = zoop), Cancel (RMB), Rotate (R / wheel), NudgeLock
    (H), Nudge (arrows, Axis2D), NudgeZ (PgUp/PgDn), BeltMode (Ctrl+R), Sample (MMB).
  - `IMC_Dismantle` (1): Dismantle (LMB), MultiSelect (Ctrl+LMB), ConfirmHold (hold LMB), Cancel (RMB).
  - `IMC_Story` (3, during cards/puzzles): SkipLine (Space/Enter), Answer (1-4 Scalar).
  Menus take input through CommonUI; legacy `BindKey` goes away.
- **Screens.** `UFGUIManager` (LocalPlayer subsystem) pushes onto 5 CommonUI stacks in `WBP_Root`:
  L0 Game (no focus): `WBP_HUD` (crosshair, hotbar, goals/to-do, power alert, toasts, look tooltip, build hints,
  subtitles). L1 GameMenu (cursor, game keeps running): `WBP_BuildMenu`, `WBP_Inventory`, `WBP_Machine` (recipe
  picker, buffers, rate/min, clock, standby), `WBP_Storage`, `WBP_Workbench`, `WBP_PowerPanel` (graph, fuse reset),
  `WBP_Hub`, `WBP_TideLab`, `WBP_TradeBuoy`, `WBP_Tower`. L2 Menu (pauses): `WBP_Pause`, `WBP_Settings` (Dev/Target
  tier, keys, audio), `WBP_SaveLoad`. L3 Modal: `WBP_Puzzle`, `WBP_Choice`, `WBP_Confirm`, `WBP_Message`.
  L4 Cinematic: `WBP_Letterbox`, `WBP_TitleCard`, `WBP_Fade`. Only the top stack takes input.
- **Every WBP derives from a C++ `UFGWidget_<Name>`** with `meta=(BindWidget)` members; buttons are bound in
  `NativeOnInitialized`. WBPs are layout only (sidesteps CLAUDE.md §1.14, `bind_event` is a no-op).
  Needs CommonUI + `CommonGameViewportClient` in `DefaultEngine.ini`; Build.cs adds UMG, Slate, SlateCore,
  CommonUI, CommonInput, Niagara, DeveloperSettings.
- **Controller split** (1398 lines): `UFGInventoryComponent` (slot stacks, StackSize, `OnChanged`);
  `UFGBuildToolComponent` (hotbar, hologram, belt/cable/zoop/dismantle modes, uses `UFGPlacementSolver`);
  `UFGInteractionComponent` (one look trace per frame shared by all, E, gather, exchange, buoy, machine UI, sea
  fall-back); `UFGStoryComponent` (line queue, puzzles, hints, toasts, choices, tower events); save to
  `UFGSaveSubsystem`; cheats to `UFGCheatManager`. Each piece gets the existing code moved first, then rewritten.

## 7. Save
- `UFGSaveSubsystem` (GameInstance). Tagged-property `USaveGame` (new fields read as defaults) + explicit
  `Migrate(v)` steps; current `Version = 2`. Slots `BlueSignal` (manual/quit) and `BlueSignal_Auto0..2` rotating.
  Autosave every 300 s (`UFGFactorySettings`), `AsyncSaveGameToSlot`; no save on PIE end (D12, backlog 8).
  References use `BuildId` guids, never array indices. Budget: < 5 MB and < 200 ms GT for the stress factory.
- **Persisted:** header (version, save time, playtime, level); player (transform, view, inventory slots,
  equipment, hotbar, unlocked buildables/recipes/alternates); buildables (Id, row, transform, buffers,
  SelectedRecipe, Progress, Clock, bStandby, BurnLeft, extractor Timer, battery charge, junction buffer + round
  robin, bLegacyPlaced); trade buoy (State, WantItem, WantCount, Delivered, RewardPearls, Cooldown); structures
  (Id, row, transform); belts + items (§2) and lifts; cables (Id, row, A/B BuildId); tripped circuits (BuildId of
  one node each); refund crates; tower (phase, Delivered, trust, OceanHealth); progression (milestones, research,
  data cores, shop purchases, to-do); story (hints, PuzzlesSolved, pending lines as (row, field, index), choices,
  flags such as RelayBroken, pending puzzle); Fish API history (url or fallback id, fish, chests, live, time; live
  images cached in `Saved/FishApi/<hash>.png` for the twist) + pending requests; weather (bStorm, StormLeft, Timer,
  StormCount); picked-up level actors by name; skiff transform. Items missing today: belt items, machine progress,
  fuel, timers, trades, broken belts, PuzzlesSolved, Fish API history, story queue, weather.
- **Load order:** structures, buildables (`InitFromRow` + `RestoreState`, materialise skipped), belts (ports by
  guid, chains), cables (circuits), player, story, weather. v1 to v2: buildables keep transforms, belt index pairs
  become straight segments (empty), platforms become structures; on failure start a new game and log it.

## 8. Test hooks (`UFGCheatManager`, added by `AddCheats(true)` outside Shipping)
Kept names: FGCompletePhase, FGGive, FGSkipStory, FGSelect, FGClick, FGInteract, FGLook, FGTeleport, FGSave, FGNewGame.

| Command | Does |
|---|---|
| `FGBuild Row X Y Z Yaw` / `FGBuildForce ...` | Place through the solver (prints BuildId + `EFGPlaceError`) / skip checks and cost |
| `FGBelt IdA PortA IdB PortB [Row]`, `FGBeltFree x y z x y z [Row]` | Port-to-port or free belt |
| `FGCable IdA IdB`, `FGFuseReset [Circuit]`, `FGStorm 1/0 [s]`, `FGStrike x y z` | Power and weather |
| `FGDismantle Id`, `FGMassDismantle Id,Id,...` | Dismantle with refund |
| `FGRecipe Id Recipe`, `FGClock Id 1.5`, `FGStandby Id 0/1`, `FGState Id` | Machines |
| `FGFillBelts Item`, `FGStressFactory N` | Perf scenario (N machines, belts, poles) |
| `FGLoad [slot]`, `FGAutosaveNow`, `FGHideHUD 0/1`, `FGDebugHUD 0/1` | Save, QA stills |
| `FGDump belts/power/machines/save/visual` | JSON to `Saved/FGDump/<what>.json` + one summary log line |
| `FGPerf` | Logs ms per subsystem, moving/visible items, significance buckets |

Python: `unreal.FGTestLibrary.dump(world, "belts")` returns the same JSON; `get_build(world, id)`,
`get_circuit(world, id)`. Scripts: `test_building` (moved to FGBuild), `test_phase2`, new `test_belts`,
`test_power`, `test_save_roundtrip`, `test_perf`; all start with `FGNewGame` (D12).

## 9. M1 implementation order
| # | Step | Size | Keeps P1-2 playable by | Done when |
|---|---|---|---|---|
| 1 | `UFGCheatManager` (exec moved, names kept), `UFGTestLibrary` + `FGDump`, `BuildId`, `UFGFactorySettings`, `stat FG` | S | pure moves | test_building + test_phase2 pass |
| 2 | `UFGFactorySubsystem` clock; actor tick off; same logic | M | identical behaviour | same tests, `FGPerf` baseline |
| 3 | Extract `UFGBuildToolComponent` + `UFGPlacementSolver` + `AFGHologram`; `IMC_Player`/`IMC_Build` | L | old 100 cm placement still runs inside the new component | tests pass via FGBuild |
| 4 | Grid (D10), `AFGStructure` foundation/wall/ramp, snap points, nudge, rotate, overlap test | M | old buildables keep transforms | test_building places a pad + wall + ramp |
| 5 | `UFGBuildableVisual` + visual component + `UFGVisualSubsystem` + state machine + CPD; `ue_visual.py` spec handed over | M | no DA = legacy stretched mesh | smoke asset spins its Drum; state lights switch |
| 6 | Materialise/dematerialise + outline highlight + mass dismantle | S | effect only, logic unchanged | capture mid-effect; refund test |
| 7 | Belts: ports, segments, chains, gap sim, item ISMs + dirty blocks, belt tool + port snapping; `AFGBelt` deleted | L | test_factory_line moves to new belts in the same change | items flow ore to ingot; stress 200 at Dev tier meets §0 |
| 8 | Power: subsystem, pole, cable catenary, circuits, fuse; global pool removed | M | level gets a pole pair pre-placed; solar wired | test_power: trip and reset |
| 9 | Save v2 for 1-8 (guids, structures, belts + items, cables, machine progress) + 5 min autosave + v1 migration | M | v1 load path | test_save_roundtrip byte-compares dumps |

Deferred to M2: zoop, lifts, splitters/mergers, batteries, UMG screens (M1 hides the Canvas HUD for QA stills),
inventory/story/interaction extraction, Fish API queue. Storm strikes: M4/M5.
Builds: land all new headers of a step in one full build (Live Coding can't add UPROPERTYs), editor closed under
`EDITOR.lock`; expect 2-3 full builds per step.

**Risks**
- Nanite spline meshes on 5.8 (belts, cables): check in step 7 day 1; fallback non-Nanite LODs.
- ISM incremental updates on Iris Xe: build `FGStressFactory` in step 7 before polish; fallback: 15 Hz updates for
  50-120 m chains and 90 m cull.
- Controller extraction regressions: move code verbatim first, tests green, then rewrite.
- RAM < 1.5 GB makes UBT single-action (~10 min builds); ask the user to close apps before build days.
- Art-contract drift: the CPD layout and the `rig` block need sign-off from material-artist and the pipeline owner.
- CommonUI config (viewport client, input data) is new to this project: one-step spike before M2 UI work.
