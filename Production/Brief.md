# Blue Signal — Master Production Brief

> The user's production prompt, saved verbatim on 2026-10-31 so every session and agent can re-read it.
> Decisions that refine or override it live in `Production/Plan.md` (§ "Decisions"). Progress lives in
> `Production/Log.md`.

---

You are the **lead producer, art director and technical director** of *Blue Signal*, the Unreal Engine 5.8 game
in this folder. You lead a team of subagents. Your job: turn the current prototype into a story-driven
**"mini Satisfactory"**. It should have the same feel, the same core systems and the same visual quality bar as
Satisfactory 1.0, with a smaller recipe tree and a journey of about **10 hours**, all in service of Ishani's story.

Work on your own, milestone by milestone (§10), until the Definition of Done (§12) is met.

---

## 1. Read first, in this order

1. `CLAUDE.md` and `SETUP.md`. These cover the machine, toolchain, MCP servers and every editor gotcha that has
   crashed this project before. Treat them as law: their crash rules outrank speed.
2. `Design/Blue_Signal.md`, the story. It is the authority on characters, beats, choices and endings.
3. `README.md`. Then have **one Explore subagent** summarise `Source/FishGame`, `Content/Blue/Data` and `Tools/`
   in 40 lines or fewer: which systems exist, which data tables exist, and what is placeholder.
   Don't read the whole codebase yourself.

**Fixed vs free**

| Fixed, never change | Free, redesign as much as you want |
|---|---|
| The story core: Ishani crash-lands on the ocean planet Blue, builds the Signal Tower, and each phase sends a message home to Neela. Each phase brings a flashback and a reply with Neela's drawing, plus the Glimmers, the choices and the two endings | Phase contents, machines, items, recipes, numbers, map layout, HUD, controls |
| **Fish Game API** (hard requirement): Neela's drawings, the Glimmers' language and the trade contracts, with the offline fallback | Every mesh, material, texture and effect. All current placeholder art gets replaced |
| UE 5.8, C++ + Blueprints, this repo, Git LFS | C++ architecture: keep what is solid and rewrite what limits quality |

The existing build is a **prototype**. Don't treat it as sacred. Reuse code that works, and replace anything that
holds back the feel or the look.

---

## 2. The target

- **Feel.** A Satisfactory player should feel at home within 10 seconds. That means a first-person build tool
  with hologram previews, snapping foundations, belts with items visibly riding them, and machines that thump,
  glow and steam. Milestones come from a central hub, and you feed parts into a giant structure that grows.
- **Look.** Hit the **Satisfactory 1.0 quality bar**: stylised realism with chunky, readable industrial machines.
  They have painted panels, real wear and moving parts, and they stand in huge, lush alien landscapes under
  dramatic skies with Lumen GI. Blue is an **ocean planet**, so think turquoise lagoons, reefs, black-sand
  beaches, kelp forests, sea stacks and storms. It is not grassland.
- **Size.** About 10 hours for a first playthrough. Aim for roughly **two-thirds of Satisfactory's early-to-mid-game
  breadth**, and cut whatever the story doesn't need.
- **Heart.** Every step of factory progress serves the story. Every tower phase is a message home.

When you need Satisfactory specifics (building proportions, rates, how a mechanic behaves), check
`satisfactory.wiki.gg` instead of relying on memory.

---

## 3. Satisfactory → Blue Signal mapping

Mechanics are fair game. Satisfactory's **names, brand, logos and assets are not**. The names below are
suggestions; you choose the final names.

| Satisfactory | Blue Signal | Notes |
|---|---|---|
| HUB + milestone tiers | **Lander Hub**, built from Ishani's escape pod | Milestone terminal. It visibly grows (burner, antenna, lockers, lights) as tiers unlock |
| Craft Bench | **Workbench** | Hold-to-craft, with a satisfying animation and sound |
| Equipment Workshop | **Suit Fabricator** | Rebreather, glider-pack, scanner, salvage cutter |
| M.A.M. research | **Tide Lab** | Research trees: kelp, black sand/glass, Glimmer pearls, storm crystal |
| Space Elevator + Project Assembly | **Signal Tower phases** | Delivered parts make the tower grow a section, then the transmission cinematic plays, then Neela's reply and drawing (Fish API), then the flashback |
| Hard drives → alternate recipes | **Black-box data cores** scattered across the islands in wreck debris | Each one also holds a short voice memory |
| AWESOME Sink + Shop | **Trade Buoy** with the Glimmers | Fish API trade contracts. Pearls buy paint swatches, cosmetics and alternate recipes |
| ADA | **ECHO**, the suit AI | Dry, helpful tutorial voice. Ishani's own voice carries the emotion |
| Power slugs / overclocking | **Glow shells** | Found on reefs at night. Used to overclock machines |
| Resource nodes with purity | Ore vents, coral-lime beds, black-sand dunes, tar seeps | Impure, normal and pure |
| Foundations | Foundations **plus floating platforms on the ocean** | The planet's signature build mechanic |
| Zipline, jetpack, hoverpack | Cable zipline + glider-pack | |
| Trucks, trains, drones | **One skiff** (boat) | The other vehicles are cut |
| Biomes with landmarks | **5 island biomes**, each with a landmark visible from far away | Landmarks are how players navigate |

---

## 4. Scope budget (10 hours)

**Content targets.** The game designer may move these by ±20%.
- 8–9 raw resources. About **60 items** in total, covering raw, intermediate, tower parts and equipment.
- About **70 recipes**, including 12–15 alternates. Production chains max out at 4–5 steps deep.
- About **35 buildables**: ~8 production, ~5 extraction, ~5 power, ~9 logistics, and ~15 structural pieces. On top
  of those come the Hub, Workbench, Fabricator, Tide Lab, Tower, Trade Buoy and Translator.
- 5 tower phases × 2 hub tiers = **10 milestone steps**.
- Map: a compact archipelago about 2.5 × 2.5 km playable, with ocean out to the horizon.

**Playtime model.** The game designer writes `Design/Progression.md` and `Tools/Design/playtime_model.py`. The
script estimates minutes per milestone from recipe rates, part counts and travel. Tune the numbers until a
first-time player lands at **10 h ± 1 h**, split as P1 1.5 h, P2 2 h, P3 2 h, P4 2.25 h, P5 2 h, then the ending.
All rates are shown **per minute**, like Satisfactory.

**Included / simplified / cut**

| Include (full feel) | Simplify | Cut |
|---|---|---|
| Build tool + holograms, foundations/walls/ramps/stairs/catwalks, multi-place ("zoop"), dismantle with refund | Fluids: pipes, pump, valve and throughput limit, with light head-lift at most | Trains, drones, trucks |
| Belts in 3 tiers, lifts, splitters, mergers, storage | Power: one grid UI, fuse trip/reset, battery | Nuclear, particle accelerator, quantum tech |
| Miners in 3 tiers on nodes with purity, scanner pulse | Creatures: a few, mostly passive, plus one mild hazard | Multiplayer, blueprint designer, dimensional storage |
| Machines with recipe choice, per-minute rates, standby, overclocking | Vehicles: one skiff | |
| Power grid with poles and **sagging cables**, generators, fuse | | |
| Hub milestones, research, alternate recipes, shop | | |
| Paint customiser, day/night, to-do list (pin recipes), production stats, **save + autosave**, photo mode | | |

**Phase seed.** Keep the story beats from `Design/Blue_Signal.md`. If phases 3–5 are already written there, keep
their story and only refit the factory content. Phases 1–2 are already playable, so rebuild them at the new quality.

| Phase | Biome | Factory step (≈ Satisfactory tiers) | New mechanics |
|---|---|---|---|
| 1 "I'm alive" | **Crash Reef**: turquoise lagoon, coral sand, the ship's wreck strewn across the reef | Hand-salvage → Workbench → Lander Hub → Smelter, Press, Miner Mk1, Kelp Burner, Belt Mk1, storage. Ferrite → plate/rod/bolts/reinforced plate; cuprite → wire/cable; coral lime → concrete. Builds the **Tower Base** | Building, belts, power |
| 2 "Strangers" | **Black Sands** (basalt columns, volcanic beach) + **Kelp Shallows** | Black sand → glass, Sea Pump, Kelp Harvester → biofuel, Assembler, fuel burners, Belt Mk2, lift, splitter/merger, Miner Mk2, Tide Lab, Suit Fabricator | Floating platforms, the Glimmers, Translator, Trade Buoy, data cores |
| 3 (seed) | Open ocean shelves, tar seeps | Kelp char (coal role) + ferrite → steel in the Foundry. Pipes, Refinery (tar → polymer, sealant). **Tidal Generator**, batteries, skiff, zipline | Fluids, the vehicle |
| 4 (seed) | **Storm Spires**: sea cliffs, lightning | Storm crystal → lenses and oscillators. Manufacturer, logic boards, control units, Belt Mk3, Miner Mk3, geothermal vents | Storms strike and trip fuses unless you build lightning rods |
| 5 (seed) | **Glimmer Deep**: bioluminescent ring reef | Glimmer pearls + resonance tech → final assembly | Choices, the two endings, the twist that re-shows old drawings |

---

## 5. Art bible seed → becomes `Art/ArtBible.md`

The art director expands this section into `Art/ArtBible.md` (300 lines or fewer) and builds the reference board.
**Every visual agent reads that file, not this prompt.**

### 5.1 Pillars
1. **Readable function.** You can tell what a machine does from 50 m by its silhouette.
2. **Chunky, believable industry.** Toy-like proportions built from real materials: bevelled edges, bolts, gaskets,
   hoses and vents. No razor-sharp CG edges and no flat untextured faces.
3. **Life.** Everything that works also moves, glows, sounds and emits something.
4. **Scale contrast.** A small player, big machines, and enormous nature (arches, sea stacks, giant kelp, sky vistas).
5. **Story in the surfaces.** Salvaged wreck plating on the early machines. Later tiers are cleaner and more
   confident. Salt crust and rust streaks near the waterline.

### 5.2 Machines
- Each machine has a silhouette sketch in its Asset Card before modelling starts.
- Paint zones: **Primary** (warm brand colour), **Secondary** (deep neutral), and **Detail** (hazard stripes,
  trims). All three are driven by the customiser.
- Required details: bare-metal frames, rubber hoses and gaskets, rivets and bolts, grilles and vents, maintenance
  hatches, ladders and railings where they make sense, stencilled labels in an **original** brand, and warning decals.
- Status lights: green when working, amber when idle or blocked, red when unpowered. Status also drives emissives,
  animation speed, VFX and the audio loop.
- Moving parts are separate meshes with clean pivots: pistons, presses, rotating drums, fans, crucibles, gears.
  Animate them with the cheapest method that looks right (component rotation or material WPO first, skeletal
  meshes only if truly needed).
- Ports sit at **one standard height** on every machine, inside a clear port frame. Orange = output, blue = input,
  consistent with the current controls.
- Footprints are whole multiples of the foundation grid.

### 5.3 Materials
- One **master material** (`M_Factory_Master`) with material instances. It has paint slots (Primary, Secondary,
  Detail), a material-type mask (paint, bare metal, rubber, glass, emissive), and edge wear from baked curvature.
  Cavity dirt comes from baked AO, plus a world-aligned **salt crust and rust streak** layer driven by height above
  sea level, detail normals, and decals.
- Shared **trim sheets** for panels, grilles and edges. Keep unique textures rare.
- Separate master materials for terrain/rock (with triplanar options), foliage (with wind), water and holograms.
- Palette: an original brand, **not FICSIT orange and grey**. Suggested: *Beacon Yellow* `#F2B33D` primary,
  *Deep Hull Navy* `#2B3A4A` secondary, *Signal Teal* `#3FE0D0` emissive tech accents, and yellow/black hazard.
  The art director finalises it.

### 5.4 Logistics visuals
- Belts are spline meshes with rollers, side rails and a scrolling surface. Items ride them as **instanced meshes**,
  evenly spaced, and stop and queue convincingly when blocked.
- Lifts, splitters and mergers get readable shapes with flaps and arrows. Pipes have flanges, valves and supports.
- Power cables sag between poles as a catenary. Poles and wall outlets have insulators.
- Every item has its own small 3D mesh (ingot, plate, rod, coil, crate…) for belts and the hand-held view.

### 5.5 Build tool and holograms
- The tool is a salvaged multitool shown in first person, with its own animations: equip, place, dismantle, reject.
- The hologram material is translucent teal with fresnel, scanlines and a grid. It turns red when invalid, and the
  dismantle highlight is orange-red.
- Placing a building plays a **materialise effect**: a scan-line dissolve with particles and a sound. Dismantling
  plays a reverse dissolve.

### 5.6 Environment
- Five biomes. Each gets a palette, fog colour, foliage set, signature landmark, ambient VFX and audio bed.
- Ocean: UE Water (ocean body, waves, shoreline foam), Single Layer Water shading, caustics, visible reef and coral
  underwater, underwater post-process.
- Foliage is layered and dense: ground cover, mid plants, alien trees and kelp, all with wind. Scatter it with
  **PCG graphs**, never by hand.
- Cliffs and sea stacks are Nanite meshes. Mesh Terrain (experimental in 5.8) only gets used after a short spike
  proves it stable on this machine; otherwise use Landscape plus Nanite cliff meshes.
- The wreck is a **kit**: hull plates, ribs, engines, cargo pods and a cockpit, used across the islands for
  salvage nodes and story beats.

### 5.7 Sky, light and post
- Sky Atmosphere with an alien tint, Volumetric Clouds, and a large ringed planet or moons in the sky for vistas.
  A full day/night cycle with a spectacular golden hour. Nights glow with plankton and Glimmer light.
- Lumen GI and reflections (hardware RT if the GPU supports it), **MegaLights** for hundreds of factory lights at
  night, Virtual Shadow Maps, TSR, and volumetric fog with light shafts.
- Exposure tuned by hand, plus a colour grade per biome through post-process volumes. Subtle bloom. No heavy
  chromatic aberration or motion blur.
- Scalability presets from Low to Epic. **Lumen Lite** for Medium.

### 5.8 VFX (Niagara)
Smelter sparks and embers, steam and heat haze, press impacts, sea spray and wave foam, rain, storm and lightning,
build and dismantle dissolves, the scanner pulse, the glow-shell sparkle, Glimmer bioluminescence, underwater bubbles
and particulates, and the **tower transmission beam** (the big payoff shot of each phase).

### 5.9 UI and icons
- UI: clean, dark translucent panels with a warm accent. Large icons, a hotbar, a categorised build menu, a
  milestone screen, recipe tooltips with per-minute rates, a power graph and a production stats screen.
- Icons are **rendered from the 3D models** in a fixed icon-studio scene: same three-quarter angle, soft key light,
  transparent background, 512 px.

### 5.10 Audio (it's part of the feel)
Every machine gets a working loop and start/stop sounds, plus belt hum, an ambience bed per biome, and music
stingers on milestones and tower phases. Use MetaSounds. Sources are CC0 (freesound CC0 filter), royalty-free
bundles with a checked licence (e.g. Sonniss GDC), or recorded/synthesised, and every one is logged in `Credits.md`.

### 5.11 Technical standards
- 1 uu = 1 cm and the player is 180 cm tall. Foundation grid 800 × 800 cm (Satisfactory's grid; if the current code
  uses another size, migrate it). Walls are 800 × 400.
- Texel density: 512 px/m for machines and structures, with close-up detail from trims and detail normals.
- Textures: 2K maximum for heroes, 1K for props, shared 2K trims. Use virtual textures for terrain. The machine has
  16 GB of RAM, so keep memory down.
- Nanite on every static mesh except translucent ones. Hero machines ≤ 1M triangles, props ≤ 50k. Every hard
  edge gets a real bevel. Collision is simple and hand-made.
- Naming: `SM_ SK_ M_ MI_ MF_ T_*_BC/_N/_ORM NS_ BP_ DT_ WBP_`. Folders: `/Game/Blue/Art/<Category>/<Asset>/`.

---

## 6. The team: create `.claude/agents/*.md` once

| Agent | Model | Owns | Touches the editor? |
|---|---|---|---|
| `art-director` | opus | `Art/ArtBible.md`, reference board, Asset Cards, approvals | No |
| `game-designer` | opus | `Design/Progression.md`, items/recipes/milestone data (JSON for the data tables), playtime model | No |
| `narrative-designer` | opus | Story beats, ECHO and Ishani lines, flashback scripts, endings. Never breaks the fixed story core | No |
| `asset-modeler` | opus for heroes, sonnet for small props and items | **Exactly one asset per agent**: Blender build, bakes, export, preview renders | No |
| `material-artist` | opus | Master materials, trim sheets, decals, texture sets | Via the integrator |
| `environment-artist` | opus | Biome kits, PCG graphs, terrain, water, landmarks | Via the integrator |
| `lighting-tech` | opus | Sky, day/night, Lumen/MegaLights, post, scalability, performance | Via the integrator |
| `vfx-artist` | sonnet | Niagara systems | Via the integrator |
| `ui-artist` | sonnet | HUD, menus, icon studio | Via the integrator |
| `audio-designer` | sonnet | Sound sourcing and MetaSounds | Via the integrator |
| `engine-programmer` | opus | C++ systems (§8), builds, Live Coding | **Yes**, holding the lock |
| `ue-integrator` | sonnet | **The only agent that imports and places content** in the editor, working from `Production/ImportQueue.md` | **Yes**, holding the lock |
| `visual-qa` | opus | Independent screenshot reviews and scores (§9) | Read-only captures, holding the lock |
| `playtester` | sonnet | Scripted progression runs (`Tools/Dev`), timing, soft-locks, Fish API offline test | PIE, holding the lock |

**Rules**
- **The Unreal editor is one shared resource.** Only one agent at a time may touch it, holding
  `Production/EDITOR.lock` (write your agent name and time; delete it when done). Parallel editor calls crash it
  (`CLAUDE.md` §1.2, §1.10, §1.15). Imports use the deferred slate-tick pattern from §1.15, **one at a time**.
- **Parallelise everything else**: design, writing, Blender modelling, textures, VFX and UI planning.
- **One model = one agent.** That is the user's explicit wish, and hundreds of agents over the project is fine.
  Hero assets get a dedicated opus modeler. If the asset is rejected, **continue the same agent with SendMessage**
  so it keeps its context; don't spawn a fresh one. After 3 rounds, escalate to the art director.
- **Waves.** Run 3–6 modelers in parallel. Check free RAM before each wave. If less than 4 GB is free, run headless
  Blender one process at a time. Close Blender processes when finished.
- **QA is independent.** `visual-qa` never reviews work it made and scores before reading the modeler's
  self-assessment.

---

## 7. Asset pipeline

1. **Manifest:** `Production/AssetManifest.csv` with columns `id, name, category, phase, priority, hero(y/n),
   footprint, owner, status, score, notes`. It covers every machine, structure piece, item mesh, tool, vehicle,
   creature, wreck-kit piece, environment kit and flashback set.
2. **Asset Card** (`Art/Cards/<id>.md`, 60 lines or fewer): story purpose, gameplay footprint and port positions,
   silhouette description, moving parts, paint zones, lights and VFX hooks, real-world reference ideas, budgets,
   deliverables and an acceptance checklist.
3. **Kitbash library first.** Before any machine is modelled, build a shared library (`ArtSource/Kit/`) of bolts,
   rivet strips, vents, grilles, pipes and flanges, hoses, panels, hatches, ladders, railings, cable trays, warning
   plates and port frames. Every machine reuses it, which keeps the look consistent and saves tokens.
4. **Modelling.** Run Blender headless (`blender -b -P Tools/Art/<script>.py -- <card.json>`). Each asset is a
   parametric Python script, so iterations are cheap edits instead of rebuilds. Build hard-surface work with bevels
   and weighted normals, keep moving parts as separate objects with pivots, and assign material slots by material
   type. Bake AO and curvature for the wear masks. Render 4 preview angles plus a close-up to
   `ArtSource/<id>/preview/`. Install the latest stable Blender with `winget` if it's missing.
5. **Downloads.** Install **Blender MCP** (needs `uv`; then `claude mcp add blender uvx blender-mcp` and enable the
   add-on in Blender) for Poly Haven and Sketchfab search and download. It drives **one** Blender GUI instance, so only one agent uses it at a time. Parallel
   modelers use headless Blender instead.
6. **Sources (licence-checked; log each in `Credits.md`):**
   - Poly Haven and ambientCG (CC0).
   - Free Fab content, plus anything already in the user's Fab library.
   - Sketchfab models under CC0 or CC-BY only, with credit.
   - AI mesh generators (Hyper3D Rodin, Hunyuan3D) only for **organic** shapes like rocks, coral and creatures, and
     only if API keys are configured. Always clean up and re-material their output to match the bible.
7. **Import.** Export FBX/glTF and add a line to `Production/ImportQueue.md`. The integrator imports it, matches the
   sampler types (`CLAUDE.md` §1.16), enables Nanite, assigns MIs of the master material, sets collision, and drops
   the asset into **`L_LookDev`**. That level has a turntable, biome lighting presets, and neutral grey and chrome
   spheres.
8. **Review.** The Blender previews get a quick art-director pass. Then `visual-qa` scores the asset in `L_LookDev`
   and in context in the world (§9). Only assets scoring 8 or higher go into the game.

**Forbidden.** Ripping or extracting anything from Satisfactory's game files (models, textures, sounds, icons, UI).
Using FICSIT or Coffee Stain names and logos, or any other copyrighted characters or brands. Match the *quality* and
*art direction* with original work. Reference images live as URLs in `Art/References.md`, with local copies in
git-ignored `Art/_refs/`. Never ship them.

---

## 8. Engine backlog (`engine-programmer`, in priority order)

1. **Build tool and snapping.** Foundation grid, walls, ramps, stairs, catwalks and floating platforms. Edge
   snapping, nudge, multi-place, rotate, hologram valid/invalid, materialise effect, and dismantle with refund,
   including mass-dismantle.
2. **Belts.** Spline belts with curve limits, lifts, splitters, mergers and 3 speed tiers. Items render through ISM
   per item type, **never one actor per item**, and back up visibly when blocked.
3. **Machines.** Recipe selection UI, buffers, per-minute rate display, standby, and glow-shell overclocking. State
   drives animation, lights, VFX and sound. A significance manager turns off distant animation and VFX.
4. **Power.** Poles and cables with sag, circuits, the power graph, fuse trip and reset, batteries, and the
   lightning-rod storm mechanic.
5. **Fluids**, simplified as in §4.
6. **Progression.** Hub milestones, Tide Lab, Signal Tower phases, data cores → alternate recipes, Trade Buoy shop,
   and the to-do list.
7. **Player.** Gathering, workbench crafting, inventory with stacks, equipment (rebreather, glider-pack, scanner,
   salvage cutter for clearing kelp and foliage), zipline, skiff.
8. **Save/load with autosave** every 5 minutes. A 10-hour game needs it.
9. **Story systems.** Messages, flashbacks, replies, drawings, choices and endings. Fish API with timeout and
   bundled fallbacks, and a history so the twist can re-show old drawings.

Data stays in data tables, so balance changes never need C++.

---

## 9. Quality gates

**Visual score.** `visual-qa` scores 1–10 on each of:
- silhouette and detail density
- material richness and wear
- function readability
- animation and life
- lighting integration
- consistency with the bible

Each score is judged against the reference board side by side. An asset ships only with an **average of 8 or more
and no category below 7**.
- Capture with the VibeUE `capture_image` tool from the fixed cameras in `Production/QA_Cameras.json`. Every biome
  is shot at noon, golden hour and night, so progress stays comparable over time.
- Review at 1280×720. Use full resolution only for milestone reports.
- Nudge the camera before re-capturing (`CLAUDE.md` §1.16 explains the stale frames).

**Performance.** Detect the GPU first (`Get-CimInstance Win32_VideoController`). Targets are 60 fps at 1080p on the
High preset, and stable 30+ fps on Epic. Also check with a large factory running (200+ machines, belts full), and
watch RAM headroom on this 16 GB machine. Profile with the VibeUE `profiling` skill, `stat unit`, `stat gpu` and
Unreal Insights.

**Gameplay.** A full scripted progression runs with no soft-locks. Save/load round-trips correctly. The playtime
model and playtests agree on 10 h ± 1 h. The game also works with the Fish API offline.

---

## 10. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M0 | **Audit and plan** | Explore summary, `Production/Plan.md`, the art bible draft and reference board, the progression draft, the asset manifest, and the agent files created |
| M1 | **Vertical slice** (the most important milestone) | One 200 × 200 m corner of the Crash Reef at golden hour, at final quality. It includes the Lander Hub, Workbench, Smelter, Press, a Miner on a node, belts with items moving, a power pole with a sagging cable, foundations, ocean, foliage and sky. **It must score 8 or more against the references before anything else scales up.** It locks the bible in practice |
| M2 | Phase 1 complete | All Phase 1 content and systems (build tool, belts, power, save) at final quality |
| M3 | Phase 2 complete | Glimmers, Translator, Trade Buoy, floating platforms, Tide Lab, Fabricator |
| M4 | Phase 3 complete | Fluids, the skiff, tidal power |
| M5 | Phase 4 complete | Storm Spires and the storm mechanic |
| M6 | Phase 5 + endings | Choices, both endings, the twist, every flashback |
| M7 | Polish | Lighting, VFX, audio and UI passes, performance, a full playthrough timing, and zero placeholder art left |

Every milestone exits with a QA board, a scripted playtest, a commit (with the push rules in `CLAUDE.md`), updated
`README.md`, `SETUP.md` and `CLAUDE.md` (new gotchas go in §1), and a short report to me.

---

## 11. Token and context economy

- **Files are the memory.** Keep `Production/Log.md` (decisions, done, next, blockers) current, so any fresh
  session or agent can resume without re-reading everything.
- **Subagents get paths, not pastes.** Give each one its Asset Card path and the art bible path. Write every
  subagent prompt with an **identical fixed preamble in the same order** and put the variable part last, so the
  prompt cache hits.
- **Short reports.** Subagents report back in 15 lines or fewer: status, files produced, score and open issues.
  Details go into files.
- **Write once, call many.** Parametric Blender scripts, the kitbash library, master materials, and helpers under
  `Tools/Art/` and `Tools/Dev/`. Never regenerate the same boilerplate per asset.
- **Right-size the model.** Use sonnet (or haiku) for mechanical work: downloads, renames, data entry, the import
  queue. Use opus for art direction, hero assets, QA and C++ architecture.
- **Use Explore agents for code search.** Don't read big files you only need a fact from.
- **Respect the `CLAUDE.md` rules:** load VibeUE skills one at a time and only when needed, avoid `describe_toolset`,
  batch editor work into single `execute_python_code` calls with compact printed evidence, and never `time.sleep`
  inside them.
- Don't re-capture identical screenshots, and don't re-read a file you just wrote.

---

## 12. Definition of done

- A first playthrough takes about 10 h ± 1 h, covering 5 tower phases and two endings, and the story core is intact.
- The Fish API is used for the drawings, the Glimmers' language and the trades, with an offline fallback.
- No placeholder geometry or materials remain. Every shipped asset has scored 8 or more in `visual-qa`.
- The feature list in §4 works end to end, and save/load is solid.
- Performance targets in §9 are met. There are no crashes in a full scripted run.
- Docs are updated, `Credits.md` is complete, and everything is committed.

---

## 13. How to work with me

- I'm not watching every step. **Don't ask permission for routine work.** Keep moving through the milestones.
- Ask me only about irreversible actions (deleting large content, force-pushing, rewriting history), accounts or
  API keys (Sketchfab, Hyper3D, Fab), or a creative fork that changes the story. Put the questions in one batch,
  and keep the other tracks moving while you wait.
- At each milestone, send me a report of 10 lines or fewer with 3–4 screenshots.

**Start now with M0.**

---

*Addendum from the user, same message:* "and use git effectively".
