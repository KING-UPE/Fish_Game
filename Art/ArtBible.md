# Blue Signal — Art Bible

> The single visual authority (owner: art-director; v1, 2026-10-31). Every visual agent reads this, not the Brief.
> Engine contract: `Design/Tech.md` §5. Slot names: `Tools/Art/lib/bslib/mats.py`. References: `Art/References.md`
> (ids `R###`). One asset's spec: `Art/Cards/<id>.md`. A card may override a rule only where it says
> "AD override" and why. Units: 1 uu = 1 cm, player 180 cm, +Z up, **+X = machine front / output side**.

## 1. Pillars (each with its test)
1. **Readable function.** A grey silhouette at 50 m tells you what the machine does. Test: render the card's
   silhouette flat black against sky; the family's signature shape (§4.6) must read.
2. **Chunky, believable industry.** Toy proportions (frames, bolts, hinges 1.3-1.5x real thickness) built from real
   materials. Every edge bevelled (>= 1 cm small parts, 2-4 cm panels, 6-10 cm big masses). Forms in 3 sizes:
   big masses (60% of the read), medium (30%: housings, tanks, hatches), fine (10%: bolts, hoses, decals). Detail
   clusters at points of interest (ports, hatches, moving parts, lamps); flat rest areas stay calm.
3. **Life.** What works moves, glows, steams and sounds. Idle and blocked are visible too (amber/orange lamp,
   a steam wisp, parts at rest). Nothing working is ever static.
4. **Scale contrast.** Player 180 cm, machines 4-14 m, nature 30-300 m (kelp 30-50 m, sea stacks 80-180 m,
   arches, a 300 m ring reef), and a ringed giant filling a quarter of the sky.
5. **Story in the surfaces.** Tier 1 is salvage: mismatched hull plates in the wreck's white/red livery, weld
   beads, patch plates, heavy salt and rust. Each tier gets cleaner and more confident (§5.4 wear table). Near
   the waterline everything carries salt crust and rust streaks. The dirty-power path stains the sea (§6.7).

## 2. Brand (original; never FICSIT / Coffee Stain or any real brand)
- **PAPER KITE WORKS** (short **PKW**): Isla's own maker's mark, printed by her fabricator on everything she
  builds. Named after the ship Skye named. **Logo:** a diamond kite tilted 12 deg clockwise, cross spars as
  stencil bridges, a curved tail of three small bows trailing down-left that ends in three concentric quarter-
  arcs (a signal). One colour, works as a stencil, reads at 32 px as "diamond with a tail". Wordmark below.
- **KEELSTAR SURVEY** (the legacy operator of the *Paper Kite*): only on wreck kit, cargo pods, the escape pod /
  Lander Hub and salvaged Tier 1 plates. **Logo:** a four-point star sitting on a short horizontal keel bar,
  inside a rounded rectangle. Hull mark `KSV-07 PAPER KITE`. Livery: Hull White + Survey Red stripe (§3).
- **Fonts (both SIL OFL, log in `Credits.md`):** stencils/labels **Big Shoulders Stencil** (Patric King,
  variable wght 100-900; use 700-900) R081; UI/plates **Barlow** + **Barlow Condensed** (Jeremy Tribby) R082.
- **Decal set** (`T_Decal_Atlas`, 2K, 8x8 cells of 256 px; mesh decals on the `Decal_Atlas` slot, §5.1):
  PKW logo + wordmark; Keelstar logo, `KSV-07`, cargo codes; model plates (`PKW SM-1 SMELTER · 4 MW ·
  BLU-0001`); flow arrows and `IN`/`OUT` chevrons; rotation arrows; our own pictograms in one style (black on
  yellow triangle: high voltage, hot surface, crush/pinch, rotating parts, fall, flammable, lifting point, no
  step, ear/eye protection); stencil digits 0-9; pipe flow bands (water, biofuel, tar, polymer); story marks
  (Isla's day tally on the Hub, Skye's fish doodle sticker on the multitool and Hub); grime (rust streak,
  salt ring, oil drip, scorch, weld burn). Decals stay legible: stencil cap height >= 12 cm on machines.

## 3. Palette (UE values; `mats.py` colours are preview approximations)
| Use | Name | Hex |
|---|---|---|
| Paint Primary (default) | Beacon Yellow | `#F2B33D` |
| Paint Secondary (default) | Deep Hull Navy | `#2B3A4A` |
| Paint Detail (default; trims, stripe partner) | Hull Black | `#1E2226` |
| Hazard stripes | Detail x Primary, 45 deg, 12 cm bands | — |
| Bare / dark metal, rubber, glass tint | Steel / Gunmetal / Rubber / Smoke | `#9A9EA3` `#3A3D42` `#262626` `#88B8C8` |
| Decal white, warning red | Stencil White / Warning Red | `#ECE6D8` `#C8372D` |
| Wreck livery | Keelstar Hull White / Survey Red | `#E4E1DA` `#B8322A` |
| Emissive tech accents, screens, Tower core | Signal Teal | `#3FE0D0` |
| Port frames | In Blue / Out Orange | `#2F7BFF` / `#FF7A1A` |
| Status Working (x20) | Go Green | `#39D353` |
| Status NoRecipe / Starved (x8, 0.5 Hz blink) | Idle Amber | `#FFB020` |
| Status Blocked (x8, 2 Hz blink) | Jam Orange | `#FF6A13` |
| Status Unpowered / tripped (x6) | Fault Red | `#FF2D2D` |
| Status Standby (x2) | Dim White | `#DDE7EE` |
| Hologram valid / look outline (stencil 1) | Holo Teal | `#4FE3E8` |
| Hologram invalid | Holo Red | `#FF3B3B` |
| Dismantle highlight (stencil 2) | Dismantle Orange-Red | `#FF5A1F` |
| Glimmers, plankton, Glow Bank | Glimmer Blue / Violet / Pearl | `#4D9BFF` `#8F7BFF` `#EAF2FF` |
| Pollution | Tar Black / Murk | `#1A1512` `#4A5A3A` |

Rules: albedo stays in sRGB 30-240 (no pure black/white). Status lamps sit in a dark bezel, never on Primary
paint (amber on yellow vanishes). Factory light is teal/yellow; nature's light is blue/violet: never swap them.

## 4. Machines
### 4.1 Footprint and grid (Plan D10, Tech §3)
- Gameplay footprint = data row `Size` in foundation cells (1 = 800 cm, halves allowed) unless the producer
  rules otherwise. Outer dimensions are **even metres** so edges land on the 100 cm sub-grid when centred.
- The body fills the footprint to a **50 cm service margin**; nothing but port frames, cables and belts crosses
  the footprint edge. Height <= the row `Height`. Origin: footprint centre, base Z = 0.
- Sizes (proportion bar, `satisfactory.wiki.gg`, R001-R003): Smelter 5x10x8.5 m, Constructor 8x10x8.5, Assembler
  9x16x11. Ours may be chunkier, never spindlier.
### 4.2 Ports (bslib `PORT_HEIGHT`)
- Port point (`loc_cm`) = belt centreline at the **running surface, Z = 100 cm**, on the footprint edge, yaw
  facing out. Inputs on -X or the sides, outputs on +X. Solid and fluid ports share the 100 cm centre.
- **Port frame** (`Kit_PortFrame_Belt` / `_Pipe`): outer 190 x 150 cm (Z 40-190), opening 150 x 110 cm (Z 60-170), frame 20 cm
  thick, 30 cm deep, 5 cm emissive inner rim (`Port_In` blue / `Port_Out` orange), stencilled `IN`/`OUT` chevron
  on the lintel, black rubber strip curtain in the opening. Fluid port: Ø80 cm flange on a Ø50 cm stub, same rim
  colours as a ring. Belt: 100 cm running surface, 130 cm outer, 30 cm deep body under the surface.
- Power socket (`Kit_PowerSocket`): a short insulator mast (3 polymer sheds) on the roof or a side bracket; the
  cable attaches at its tip = rig `power`.
### 4.3 Moving parts (Tech §5 roles)
- Separate parts with the pivot on the mechanical axis (drum centre, piston rod line, hinge pin). Roles:
  Rotator, Piston (sine along axis), Oscillator (sine rotation), StatusLight, PortFrame, Static.
- Every machine: >= 1 primary motion + 1 secondary motion at a different rate (e.g. drum 90 deg/s + fan 360).
  No collision, no children, no intersection with the body over the full range (check both extremes).
  Moving parts <= 30% of the machine's triangles. Rates are at 100% clock; the engine scales them.
### 4.4 Status light
`StatusLight` part = `Kit_StatusLight` (caged beacon, lens >= 30 cm, `Emissive_Status`, dark bezel), top-front corner >= 250 cm,
visible from the front and both sides (XL machines: two). States, colours and blink: §3 + Tech §5 table.
### 4.5 Required detail (from `ArtSource/Kit/`, never re-modelled per asset)
Bare-metal frame, rubber hoses + gaskets, bolts/rivets, grilles/vents, a maintenance hatch, ladder + railing
(110 cm) on anything with a reachable top, a model plate, >= 2 warning pictograms, the PKW logo once per side
seen from a belt line. Doors 100 x 220 cm, ladder rungs every 30 cm, catwalk 400 x 200 (Tech §3).
### 4.6 Signature shapes (the 50 m read; no Satisfactory silhouettes)
| Family | Signature |
|---|---|
| Heat (Smelter, Kiln, Foundry) | Smelter: egg-shaped furnace with a glowing slot window and a slanted pour chute. Kiln: horizontal drum on riding rings (R016). Foundry: twin furnace towers + swinging ladle |
| Form (Press, Assembler, Manufactory) | Press: tall portal gantry, big piston head over an anvil bed (R018). Assembler: open bay, two arms over a turntable. Manufactory: hall with a roof gantry crane and lit windows |
| Fluid (Refinery, Sea/Tar/Pipe Pump) | Refinery: column tower + spherical tank + pipe rack. Sea Pump: pontoon + impeller housing. Tar Pump: nodding beam (Oscillator) |
| Extract (Drill Rig Mk1-3, Trench Drill, Kelp Harvester) | Drill: tripod derrick, spinning head, bucket elevator; Mk2/Mk3 add mass, not new shapes. Harvester: barge with a cutter wheel |
| Power (Kelp/Fuel Burner, Tidal Turbine, Salvaged Solar, Glow Bank, Accumulator, Lightning Rod) | Burners: boiler + stacks + flywheel. Turbine: twin rotors on a raisable crossbeam (R040). Solar: wreck wings on a sun tracker. Glow Bank: Glimmer light tanks pulsing blue-violet. Rod: mast + crystal crown |
| Story (Lander Hub, Tower, Tide Lab, Translator, Trade Buoy, Resonance Forge) | Hub: the escape pod with unfolded arms (D15). Tower: lattice mast that grows per phase, dish + beam. Forge and Glimmer tech: rings and curves, the only non-boxy machines |

## 5. Materials
### 5.1 Masters and slots
- **`M_Factory_Master`** for every buildable, wreck piece and item. One MI per slot, named exactly as `bslib.mats.SLOTS`:
  `Paint_Primary` `Paint_Secondary` `Paint_Detail` (customiser-driven) · `Metal_Bare` `Metal_Dark` `Rubber` ·
  `Glass` (**opaque**, dark, roughness 0.05: keeps Nanite) · `Emissive_Status` (CPD 0-3) · `Emissive_Tech`
  (Signal Teal, pulses with CPD 4) · `Port_In` `Port_Out`. **New slot `Decal_Atlas`** (mesh decals on a
  separate non-Nanite `Decals` part, <= 2k tris) must be added to `SLOTS` + `ue_import.SLOT_MI` (pipeline owner).
- Other masters: `M_Terrain_Master` (landscape layers + triplanar, RVT), `M_Rock_Master` (triplanar detail,
  world-aligned lichen/moss top blend, wet + salt bands), `M_Foliage_Master` (wind WPO, two-sided, subsurface,
  WPO disable distance), `M_Kelp` (sway + current WPO), UE Water + Single Layer Water, `M_Glow` (bioluminescent
  pulse), `MI_Hologram`, `MI_Materialise`, `M_Decal`, `M_PP_Outline`, `M_PP_Underwater`, UI materials.
### 5.2 Wear inputs (Plan D13: no unique textures by default)
- **`BS_Mask` vertex colour:** **R** edge wear (convex): paint chips to `Metal_Bare`, bare metal polishes
  brighter. **G** AO (1 open, 0 occluded): grime `#3A3226` multiply. **B** cavity (concave): grime + rust
  bleed source. All three are broken up by a tiling grunge noise so edges never read as clean lines.
- Detail normal: paint orange-peel / brushed metal / rubber grain, tiling at 512 px/m.
- Shared **trims** (2K, 512 px/m): `T_Trim_Panels` (seams, bevel strips, rivet rows), `T_Trim_Grilles`
  (masked louvres, perforated plate), `T_Trim_Edges` (weld beads, gaskets, chamfers). Stripes are procedural.
### 5.3 Salt, rust, wet (world-aligned; `MPC_World.SeaLevelZ`, default 0 cm)
| Height above sea | Layer |
|---|---|
| below 0 | algae tint `#4F6B3A` in cavities, barnacle detail normal, darkened albedo |
| 0 to +60 cm | wet band: albedo x0.6, roughness 0.15; moves with the swell on water buildings |
| 0 to +120 cm | full salt crust `#E9E4D6`, roughness 0.9, on up-facing faces and cavities, gone by +400 cm |
| 0 to +600 cm | rust streaks: world-aligned vertical streaks seeded at cavities/bolts (B mask), fading with height |

Strength = MI scalar `Wear` x height falloff. Floating platforms sit at Z -20 (Tech §3) and get every band.
### 5.4 Wear by tier (MI scalar `Wear`)
Wreck 1.2 (burnt, holed) · T1 salvage 1.0 (Keelstar plates, patches) · T2 0.7 · T3 0.5 · T4 0.35 · T5 0.25
(crisp paint, more `Emissive_Tech`). The clean-power path keeps these values; the dirty path adds soot (+0.2).
### 5.5 Texture rules
Texel density 512 px/m. Caps: hero unique set 2K, props 1K, trims 2K shared, decal atlas 2K, icons 512,
terrain through virtual textures, no 4K except the sky giant (§7). Sets: `T_<Asset>_BC` (sRGB, Default,
SAMPLERTYPE_Color), `_N` (Normalmap), `_ORM` (R AO, G rough, B metal; Masks, linear). Match sampler type to
compression (CLAUDE.md §1.16) or the whole material falls back to grey.

## 6. Biomes (data keys `CrashReef BlackSands KelpShallows TarShelves StormSpires GlimmerDeep`)
The Brief counts 5 island biomes; the data has 6 zones (Tar Shelves = the P3 open shelf). Each gets a post-process
volume (grade), fog, a PCG foliage set, one landmark visible from 1 km, ambient VFX and an audio bed.
### 6.1 Crash Reef (P1) — R041-R048
- Palette: lagoon `#3CCFC4`, shallows `#9EE6D8`, coral sand `#E8DCC0`, coral pinks `#E58A7A` `#F2B6A0`, screw-pine
  green `#6E9A4A`, wreck livery. Fog `#BFE3E6`, thin, strong height falloff.
- Foliage: beach vine + coral rubble (ground), stilt-root screw pines and salt bushes (mid), 12-18 m fan-leaf
  "kite palms" (tall); underwater branching coral, brain-coral domes, sea grass, giant clams.
- Landmark `Env_CrashReef_Landmark`: the *Paper Kite*'s 30 m tail fin standing on the reef (WreckKit parts),
  red beacon blinking, visible from the Hub; the broken hull lies scattered around it.
- VFX: reef-crest foam lines, drifting spray, caustics, fish schools, wreck smoke wisps (until the Hub is built).
- Audio: lagoon lapping, distant reef surf, hull creaks, wind in palms, alien bird calls.
- Noon: saturated turquoise, crisp shadows. Golden: peach key `#FFB27A`, pink cloud bellies, teal-gold water.
  Night: ring-lit blue `#1C2B44`, plankton sparkle in the wave break, the wreck's red beacon blinking.
### 6.2 Black Sands (P2) — R049-R055
- Palette: black sand `#1F1F22`, wet basalt `#2A2D30`, column grey `#3B3E42`, lichen `#7A8A6A`, sulphur `#C9A24A`.
  Fog `#9FA9B0` cool sea mist, rolling.
- Foliage: black moss cushions, silver dune grass, red-tipped "ember ferns"; lichen decals on the columns.
- Landmark `Env_BlackSands_Landmark`: a dormant 120 m cone with a steam plume seen from the Crash Reef; its
  seaward flank breaks into basalt columns and a sea cave that booms with every wave.
- VFX: steam vents with heat haze, surf bursts on column steps, sand glints.
- Audio: cave booms, pebble backwash, vent hiss, wind.
- Noon: black sand is the dark value anchor (machines pop). Golden: grazing light rims the hexagon tops.
  Night: vents glow `#FF6A2A`, columns silhouetted against the ring.
### 6.3 Kelp Shallows (P2) — R056-R061
- Palette: kelp olive-gold `#8A7A2E` (backlit `#B39B3A`), water green-teal `#2E8C86`, sand `#CDBF98`, Glimmer
  Blue. Fog `#A9D6CF` above, `#1E6A6A` underwater.
- Foliage: giant kelp 30-50 m with float bladders and surface canopy mats, sea palms on rocks, eelgrass, kelp rafts.
- Landmark `Env_KelpShallows_Landmark`, **the Kelp Cathedral**: 50-60 m kelp spires arching over a lagoon.
- VFX: god rays through the canopy, particulates, bubbles, drifting fronds, Glimmer flickers at dusk.
- Audio: muffled swell, kelp creak, water slapping floats, distant Glimmer tones.
- Noon: dappled light. Golden: kelp glows amber. Night: Glimmer lights moving between stalks (first sighting).
### 6.4 Tar Shelves (P3) — R062-R065
- Palette: limestone shelf `#B5AA92`, tar `#1A1512` with a thin-film oil sheen, algae rust `#8A5A2B`, drop-off
  blue `#13406B`. Fog `#C9C2B0` warm haze, denser over the seeps.
- Foliage: sea fans, tube sponges, salt scrub; bleached coral patches near the seeps.
- Landmark `Env_TarShelves_Landmark`, **the Chimney**: a 60 m tar-vent pillar with a constant smoke column,
  standing in a 200 m tar pool at the shelf edge.
- VFX: tar bubbles and burps, oily sheen, smoke plumes, heat shimmer, the "sea darkens" layer (BT_P3_02).
- Audio: tar bubbling, flat wind, distant whale-like calls.
- Noon: flat, bleached. Golden: rainbow sheen, smoky orange sky. Night: seep embers, almost no plankton.
### 6.5 Storm Spires (P4) — R066-R072
- Palette: slate `#4A4F55`, wet stone `#2F3338`, stack-top grass `#5E7A4E`, storm crystal `#C9B8FF` (emissive),
  storm sky `#3A4250`. Fog `#6E7A86`, dense and low, with rain.
- Foliage: wind-bent "spire pines" (6-10 m) on stack tops, tussock, sea thrift; crystal clusters (PCG, not foliage).
- Landmark `Env_StormSpires_Landmark`, **the Crowned Spire**: a 150 m sea stack with an arch at its foot and a
  crystal crown that draws lightning.
- VFX: rain, lightning + flash, spray blasting up the cliffs, spindrift, crystal charge arcs.
- Audio: gale, thunder, rain, surf on cliffs, crystal hum.
- Noon (between storms): cold clean light, towering cumulus. Golden: storm break, god rays, a rainbow.
  Night: lightning-lit; the crystals glow violet.
### 6.6 Glimmer Deep (P5) — R073-R080, R106-R108
- Palette: deep water `#0B2A4A`, ring-reef coral `#D9D2C0`, Glimmer Blue / Violet / Pearl, vent-orange accents.
  Fog `#1F3C5E` above, `#0A1E33` underwater.
- Foliage: glowing coral fans, tube-worm forests (red plumes) at vents, glowing anemones, pearl clams, sea lilies.
- Landmark `Env_GlimmerDeep_Landmark`, **the Ring Reef**: a 300 m glowing atoll around a blue hole, the
  Elder's great lantern coral at its centre, trench vents glowing below.
- VFX: plankton glow in every wave, Glimmer schools, rising light motes, vent shimmer.
- Audio: Glimmer choir tones, deep hum, gentle swell, vent rumble.
- Noon: deep saturated blue against a white atoll. Golden: violet-pink sky. Night: the showcase; everything glows.
### 6.7 Ocean Health (all biomes)
`MPC_World.OceanHealth` (1 clean, 0 dark) lerps water absorption toward Murk `#4A5A3A`, cuts plankton and Glimmer
glow, desaturates coral and adds tar sheen near dirty factories. It must read at a glance from a cliff top.

## 7. Sky, light, post (owner: lighting-tech) — R083-R088
- **Sky Atmosphere** tinted a touch greener than Earth (zenith `#3D7FD0`, horizon `#BFE6F0`), strong Mie halo for
  sea haze. **Volumetric Clouds**: trade-wind cumulus by default, a low storm deck in the Storm Spires.
- **`Sky_RingedPlanet` "Halo"**: a banded teal-and-cream gas giant, 22 deg across, rings sweeping ~70 deg of sky,
  always above the eastern horizon. Day: pale and soft. Night: its lit side + ring-shine (`#9DB7E0`) is the
  moonlight. Two small moons (`Sky_Moons`). The only 4K textures in the game (planet 4K, ring strip 4K x 256).
- **Day/night:** a full cycle (length owned by design; default 40 min). Golden hour = sun < 12 deg: key `#FFB27A`,
  long shadows, rim light on machines; it is the hero time of day and lasts >= 4 min each way.
- **Night is never black:** ring-shine + plankton + Glimmers + factory lights. `Kit_WorkLight` floods are warm
  `#FFD9A0` (4000 K); machine lamps follow §3. MegaLights where the tier allows (§11), else emissive + few real lights.
- **Exposure:** clamped auto exposure per biome PPV (min/max EV100 within 2 stops); no adaptation pumping > 1 EV.
- **Post:** per-biome grade (saturation +-10% max, no heavy LUTs), subtle bloom, chromatic aberration 0, motion
  blur 0 (player option), grain 0. **Flashbacks only:** warm grade, grain 0.3, 2.39:1 letterbox, soft vignette.
- **Underwater** (`M_PP_Underwater`): depth absorption toward the biome's underwater fog, caustics on the seabed,
  god rays, particulates. Water: UE Water bodies + Single Layer Water + shoreline foam (`Env_Ocean_*`).

## 8. VFX (Niagara, owner: vfx-artist)
Systems = manifest `FX_*` ids, assets `NS_<Id>`: Machine_Sparks (smelter embers), Machine_Steam (+ heat haze),
Machine_Impact (press dust + sparks), Drill_Debris, Burner_Smoke, Power_Spark, Tool_BuildMaterialiseFX
(scan-line dissolve 0.8 s machines / 0.4 s structures + teal motes; reverse 0.5 s), ScannerPulse, Pickup,
Weather_Rain / Lightning / Fog, StormDamage, GlimmerSwarm, Ambient (spray, foam, plankton, bubbles,
particulates, motes), Skiff_Wake, Crash, **TransmissionBeam** (the payoff shot of every phase: teal core,
expanding rings up through the clouds, sky flash), EndA_Launch, EndB_OceanLights.
- Factory VFX are white/warm/teal; nature VFX are blue/violet; dirty-power smoke is brown-black.
- CPU sim < 200 particles, GPU above. Work VFX obey significance (Tech §5: 40 working NS, S1 at Niagara Low).
- Gameplay-critical VFX (materialise, dismantle, lightning warning, fuse trip, transmission beam) exist on every tier.

## 9. UI and icons (owner: ui-artist) — R101-R105
- Panels: dark translucent `#0E1620` at 82%, 1 px inner line `#FFFFFF14`, 6 px radius with one 12 px chamfered
  corner (our signature), Beacon Yellow = focus/selection, Signal Teal = info/progress, status colours from §3.
- Type: Barlow (body 16-18 px at 1080p, min 14), Barlow Condensed SemiBold caps for headers and rates,
  Big Shoulders Stencil only for titles and big numbers. Text contrast >= 4.5:1.
- Colour never works alone: status also has a shape (check / pause bars / jam chevrons / lightning bolt), and
  blink rates differ (§3) so green/amber/orange read for colour-blind players. Safe area 5%.
- Skye's drawings (Fish API pictures) show on paper with tape and a pencil count box; Glimmer glyphs are rounded
  2-3 px glowing strokes in Glimmer Blue.
- **Icon studio** (`L_IconStudio`): camera yaw 35 deg (front-left), pitch -25 deg, FOV 20 deg, object fills 80%
  of the frame, soft 5500 K key top-left, 30% fill, teal rim back-right, no ground, transparent background,
  512 px PNG -> `T_Icon_<Id>` (UI group, no mips). Same rig for items and buildables; never hand-drawn stand-ins.

## 10. Budgets, naming, folders
| Class (manifest category) | Triangles (Nanite source) | Textures | Collision (simple, hand-made) |
|---|---|---|---|
| Hero (`SignalTower`, `LanderHub`, `Manufactory`, landmarks) | <= 1M | trims + atlas; unique 2K set only if the card says | boxes/convex <= 16 |
| Machine / Extractor / Power | <= 400k (moving parts <= 30%) | trims + atlas, no unique | boxes/convex <= 12, Body part only |
| Structure (`Foundation`, `Wall`, `Ramp`...) | <= 60k | trims | 1 box (ramp/stairs: 1-2 convex) |
| Logistics (`Splitter`, `PowerPole`...) | <= 50k; belt/cable segment <= 3k + 2 LODs | trims | boxes; belts query-only |
| Kit piece (`Kit_*`) | <= 10k (bolt <= 300) | trims | none (host provides) |
| Item (`Item_*`, belt + hand) | <= 3k | shared 1K atlas per family | none |
| Prop / wreck piece | <= 50k (wreck hero <= 200k) | 1K | convex <= 8 |
| Rock / cliff / stack | <= 500k (landmark <= 2M) | `M_Rock_Master` triplanar, 2K | convex <= 32 |
| Foliage | tree <= 150k, bush <= 30k, ground cover <= 3k | 1K (2K atlas per biome) | trunks only |
| Creature (`SK_`) / cinematic character | <= 30k / <= 80k | 1K / 2K | capsule |
- **Nanite** on every opaque static mesh, foliage included (geometry leaves, no masked cards). Not Nanite:
  translucent, the `Decals` part, skeletal meshes, belt splines if `r.Nanite.AllowSplineMeshes` fails (Tech §2).
- **Names:** `SM_ SK_ M_ MI_ MF_ T_*_BC/_N/_ORM NS_ BP_ DT_ DA_ WBP_ MPC_ PCG_ L_`. Asset names use the manifest
  id: `SM_<Id>_<Part>` (bslib: `mesh_name` + part, e.g. `SM_Smelter_Body`, `SM_Smelter_Drum`), `DA_<Id>_Visual`.
- **Folders:** `/Game/Blue/Art/<Category>/<Id>/` (Category = manifest category: Machine, Extractor, Power,
  Logistics, Structure, Special, Kit, Wreck, Env/<Biome>, Item, Tool, Creature, Sky, VFX);
  `/Game/Blue/Art/Materials/{Masters,Functions,Instances,Textures,Decals}`; `/Game/Blue/UI/Icons/`. Sources
  `ArtSource/<Id>/` (card.json, script output, previews); references only in git-ignored `Art/_refs/`.

## 11. Scalability tiers (Plan D6, §6) — Low/Medium/High run on the Iris Xe laptop; Epic is for strong PCs
| Feature | Low | Medium | High | Epic (never cut to fit the laptop) |
|---|---|---|---|---|
| GI / reflections | skylight + SSAO, no SSR | lightest software Lumen + SSR | software Lumen GI + refl. | full Lumen, hardware RT if present |
| Shadows / lights | CSM short, emissive lamps | VSM low | VSM, MegaLights if it holds | VSM high, MegaLights |
| Clouds / fog | low-res clouds, height fog | + volumetric fog low | medium | high, cloud shadows, light shafts |
| Foliage / VFX | 40% density, Niagara Low | 60% | 80% | 100%, full spawn |
| Water | no caustics, simple shore | caustics | + SSR on water | + full refraction detail |
Never scales: silhouettes, materials' colours, wear and status lights, port colours, holograms and the
outline, UI/icons, gameplay VFX (§8), landmark visibility at distance, the night staying playable, and every
story shot (the beam is simpler on Low, never missing). Hardware-RT-only features fall back cleanly (D6).

## 12. Satisfactory quality, our own look
- **Match** (R001-R008, side-by-side QA only): chunky proportions, bevel and wear density, lived-in factories,
  believable mechanical motion, readable ports and states, layered dense nature, dramatic skies, the build feel
  (hologram, snap, materialise).
- **Never copy:** their orange/grey/brown scheme, logos, mascots, stencils, fonts, HUD layout, icons, machine
  silhouettes, item models, flora, fauna, sounds or any file. No tracing or paint-overs of their shots.
- **Ours:** an ocean planet with floating platforms; a salvage-to-confident arc; Beacon Yellow / Hull Navy /
  Signal Teal; Glimmer bioluminescence; rounded Glimmer tech against boxy industry; the ringed giant Halo.

## 13. QA categories (Brief §9: approve at avg >= 8 and none < 7; 1280x720, noon / golden / night)
| Category | What an 8/10 looks like |
|---|---|
| Silhouette and detail density | the §4.6 signature reads as a black silhouette at 50 m; 3 form sizes; detail clustered at ports, hatches and moving parts; bevels catch light; no flat face > 1 m2 without a panel break |
| Material richness and wear | paint, bare metal, rubber and glass distinct at 5 m; chips only on convex edges, grime in recesses; salt/rust bands at the right height; tier wear right; no visible tiling at 10 m |
| Function readability | a new player names inputs, outputs and job without UI; ports framed blue/orange at 100 cm; status lamp seen from 3 sides; decals legible at 5 m |
| Animation and life | primary + secondary motion at believable rates; 0.6 s ramps; each state (Tech §5) changes lamp, motion, VFX and sound; no pops or intersections |
| Lighting integration | sits in all three presets without looking pasted: GI bounce, contact shadows, emissives bloom without clipping, readable at night, no leaks |
| Consistency with the bible | palette hexes, slot names, naming, budgets, kit pieces and decals as written here; nothing that reads as Satisfactory's design |
