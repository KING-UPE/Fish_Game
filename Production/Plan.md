# Blue Signal — Production Plan

Owner: the producer (main session). Source brief: `Production/Brief.md`. Audit: `Production/Audit.md`.
Status and next steps: `Production/Log.md`. This file holds the **decisions**, the **milestone plan**, the
**engine backlog**, **risks** and **open questions**. Update it when a decision changes; never silently.

---

## 1. Decisions

| # | Date | Decision | Why |
|---|---|---|---|
| D1 | 2026-10-31 | **Git model.** `main` = last stable playable build; only verified milestones merge into it (`--no-ff`, tag `mN`). `dev` = production integration branch (started from the `wip/phase3` checkpoint `f3998e9`). Work happens on short branches `mN/<topic>` cut from `dev` and merged back `--no-ff`, so each deliverable is one revertable merge. Conventional commits with scopes (`feat(belts)`, `art(smelter)`, `docs(art)`, `chore(git)`). Agents never commit; the producer commits each deliverable. Push at milestone exits (CLAUDE.md account rule). | Untested WIP (save/load, weather) stays off `main`; history stays bisectable |
| D2 | 2026-10-31 | **Story beats win over the Brief's phase seed.** P3 ends with the scripted storm that breaks the relay (storm crystals + lightning rods arrive with it). P4 holds the power choice: burners (fast, dirty) vs tidal turbines + light cells (clean, needs Glimmer trust). The seed's "Tidal Generator in P3" moves to P4. Storm Spires is P4's biome and makes storms a recurring mechanic there. | Brief §4: "keep their story and only refit the factory content" |
| D3 | 2026-10-31 | **Echo** = the ship's AI from the story (sarcastic, warm, Ray's voice, two secrets), now running in Isla's suit. It is the tutorial voice the Brief calls ECHO. | Story doc is the authority on characters |
| D4 | 2026-10-31 | **No oxygen meter, no underwater survival.** The Brief's "rebreather" becomes a **dive mask** (underwater vision + swim speed). | Story doc: "No underwater survival, no oxygen meter" |
| D5 | 2026-10-31 | **One skiff**; the story doc's Drone Boat Dock is cut. Zipline + glider-pack for traversal. | Brief §4 cuts |
| D6 | 2026-10-31 | **Performance is re-baselined to this laptop (user's answer to Q1), with one rule: Epic is never cut to fit it.** Low / Medium / High get their speed targets on this Intel Iris Xe laptop (§6), and main development happens here, so every feature must run and be testable here on Low-High. **Epic keeps full Satisfactory-1.0 quality for strong PCs**: it is authored, kept working and documented (`Production/EpicTestPlan.md`) for the user to test later on a stronger PC. Here, Epic is only rendered for QA stills (frame rate ignored); hardware-RT-only features (hardware Lumen, anything needing DXR) must fall back cleanly on this GPU. | User decision 2026-10-31; measured hardware (Audit) |
| D7 | 2026-10-31 | **Parametric scripts are the art source of truth.** Commit `Tools/Art/**`, `ArtSource/<id>/card.json`, `selfcheck.md`, `preview/contact.jpg` and the imported `.uasset`s. Git-ignore `.blend`, raw exports, full-size previews and downloads (re-creatable; URLs in `Credits.md`). | GitHub's free LFS is 1 GB storage / 1 GB per month (Q2) |
| D8 | 2026-10-31 | The 14 role files live in `.claude/agents/`. Custom agent types load at session start, so until the next session they run as `general-purpose` agents told to read their role file. Every agent prompt starts with the same fixed preamble (`[Blue Signal production · fixed preamble v2]`) and puts the variable task last. | Prompt-cache hits; roles survive restarts |
| D9 | 2026-10-31 | **Architecture: keep** the data-driven buildable core (`FGTypes` rows, `AFGBuildable` buffers/refunds, extractor/generator/storage), `AFGTowerSite`, `UFGFishApi`, translator/trade buoy logic. **Rewrite**: belts → a world subsystem with spline belts and one shared ISM per item type; placement → 800 cm foundations with snapping; power → circuits with poles/cables/fuses; UI → UMG; input → Enhanced Input; the 1400-line controller → components (inventory, build tool, interaction, story); save → versioned and complete. | Audit risks 1-3 |
| D10 | 2026-10-31 | **Grid**: foundations 800 x 800 cm (walls 800 x 400). Buildings snap to a 100 cm sub-grid on foundations and to the 800 grid on terrain; small logistics may use half cells. | Brief §5.11; current code is 100 cm |
| D11 | 2026-10-31 | **Fish API offline fallback is fixed early (M2)**: bundle ~24 fallback puzzles (`/Game/Blue/FishApi/T_Fish_F#_C#`, generated original art), queue concurrent requests instead of dropping them, persist the history in the save. | Audit: fallback folder doesn't exist; DoD requires offline play |
| D12 | 2026-10-31 | Scripted tests always start with `FGNewGame` (PIE end autosaves, so runs otherwise resume the last one). | Audit |
| D13 | 2026-10-31 | **Wear masks live in vertex colour, not unique textures.** `bslib.masks` bakes `BS_Mask` (R edge wear from convexity, G Cycles AO, B cavity) on every exported part; `M_Factory_Master` reads it, plus shared trims, tiling detail textures and world-aligned salt/rust. Unique texture sets only where a card asks. | Bevelled Nanite meshes are dense at edges; saves disk, RAM, LFS and bake time |
| D14 | 2026-10-31 | Echo's mind runs on the wreck's core; the suit is only its link (narrative R4). That is why Echo "stays behind" in Ending A. | Ending A logic |
| D15 | 2026-10-31 | The Lander Hub is built from the escape pod, which is also Ending A's return capsule (R5). | Payoff for the hub |
| D16 | 2026-10-31 | P5 pacing: Echo's confession + Flashback 5 at P5 hub tier 1, then a stretch with Echo text-only, then the last real message + the choice (R12). | Avoids ~15 min without play |
| D17 | 2026-10-31 | The Fish API returns 0 fish ~1 time in 8: re-roll those for drawings and trades; keep them for the Elder's empty picture (R6). Flashback 4 hints Echo is Ray (voice filter drops), Flashback 5 confirms it (R3). | Narrative audit |
| D18 | 2026-10-31 | **Two projects, one repo, two folders (user: "Antigravity takes one branch", the producer is the boss).** Blue Signal (Unreal) lives in `D:\Game\FishGame` on `main` / `dev` / `mN/*`. The user's Antigravity agent builds *Tide & Treasure* (Node web game) in the git worktree `D:\Game\TideAndTreasure` on branch `tide-and-treasure` (first snapshot `b5e63cc`). Nobody switches branches, stashes or commits across folders. | At 22:39 the T&T start stashed Blue Signal and emptied this folder mid-run; one folder can hold only one branch |
| D19 | 2026-10-31 | **Everything in English, names too (user, Q4).** Ishani → **Isla** (island), Neela → **Skye** (she watches the sky for the blue light, keeping the title's double meaning), Ravi → **Ray** (a ray of light; Echo's voice), "Duwa" → "sweetheart", "Appa" → "Dad". `Production/Brief.md` keeps the old names verbatim; this decision overrides it. | User decision |
| D20 | 2026-10-31 | **Free only (user, Q2/Q3).** No paid LFS data pack, no paid API keys. Art comes from our own parametric Blender scripts plus CC0 sources (Poly Haven, ambientCG). LFS keeps only `.uasset`/`.umap` (git can't diff binaries and GitHub rejects files > 100 MB; LFS keeps clones light); regenerable sources stay git-ignored (D7). Keep LFS under ~800 MB of the free 1 GB and check before each push. Free MCPs/skills may be installed when a task needs them. Fonts under SIL OFL 1.1 are allowed (AgentRules §4). | User decision |

---

## 2. Milestones

| # | Milestone | Branches | Exit (Brief §10 + ours) |
|---|---|---|---|
| M0 | Audit and plan | `m0/plan` | Audit, this Plan, art bible + reference board, progression + playtime model, narrative beats, asset manifest, agent files; merged to `dev`, tagged `m0` |
| M1 | **Vertical slice** | `m1/pipeline`, `m1/kit`, `m1/materials`, `m1/<asset>`, `m1/belts`, `m1/build`, `m1/power`, `m1/env`, `m1/light` | 200 x 200 m Crash Reef corner at golden hour scores avg >= 8 / min 7 vs references (§9) |
| M2 | Phase 1 complete | `m2/*` | P1 content + build tool, belts, power, save at final quality; Fish API offline fallback; merge `dev` → `main` |
| M3 | Phase 2 | `m3/*` | Glimmers, Translator, Trade Buoy, platforms, Tide Lab, Suit Fabricator |
| M4 | Phase 3 | `m4/*` | Fluids, skiff, the storm beat |
| M5 | Phase 4 | `m5/*` | Storm Spires, storm mechanic, power choice |
| M6 | Phase 5 + endings | `m6/*` | Choices, both endings, twist, flashbacks |
| M7 | Polish | `m7/*` | Lighting/VFX/audio/UI passes, perf, full timed playthrough, zero placeholders |

Every exit: QA board, scripted playtest, commit + merge + tag + push, README/SETUP/CLAUDE updated, report.

---

## 3. M1 — vertical slice plan

**Scope** (one 200 x 200 m corner of the Crash Reef, golden hour, final quality): Lander Hub, Workbench,
Smelter, Constructor-class Press, Miner Mk1 on a ferrite node, Belt Mk1 (spline) with items moving, one power
pole pair with a sagging cable, a foundation pad (foundations + a wall + ramp), the ocean with shoreline foam,
layered foliage via PCG, coral sand, a wreck-kit piece, sky with clouds + ringed planet, post grade.

**Order of work** (parallel where it doesn't need the editor):

| Wave | Track | Who | Output |
|---|---|---|---|
| 1 | Pipeline | producer + engine-programmer | `Tools/Art/run_blender.py`, `Tools/Art/lib/` (bevel, weighted normals, bake AO/curvature, export, preview/contact sheet), `Tools/Art/ue_import.py` (deferred import), `L_LookDev`, `Production/QA_Cameras.json` |
| 1 | Cards | art-director | Cards for the 11 slice assets + kit |
| 1 | Materials | material-artist | `M_Factory_Master` + trims, `M_Hologram`, terrain/rock, foliage, water setup |
| 2 | Kitbash library | asset-modeler (opus) | `Tools/Art/kit/` parametric kit (~25 parts) |
| 2 | Engine | engine-programmer | 800 grid + foundations/wall/ramp + snapping; belt subsystem (spline, ISM per item); poles + catenary cable; machine state → emissive/anim hooks; materialise effect |
| 3 | Heroes | 1 modeler per asset (opus) | Hub, Workbench, Smelter, Press, Miner Mk1, Pole, Belt kit, Foundation set |
| 3 | Props | 1 modeler per asset (sonnet) | item meshes (ore, ingot, plate, rod), wreck piece, ferrite node |
| 3 | Environment | environment-artist (+ integrator) | slice terrain, cliffs/rocks, coral, PCG foliage, UE Water ocean |
| 3 | Lighting | lighting-tech (+ integrator) | golden-hour key, sky/clouds/planet, post, Dev/Target tiers |
| 4 | VFX/audio | vfx-artist, audio-designer | smelter sparks, press impact, steam, materialise; machine loops |
| 5 | QA loop | visual-qa → modelers (SendMessage) | scores; iterate until avg >= 8, min 7 |

Blender runs **one process at a time** while free RAM < 4 GB (it is ~0.4-2 GB with the editor open). Modelers
can still be spawned in parallel: they write scripts in parallel and take turns on Blender through
`run_blender.py`'s lock.

---

## 4. Engine backlog (priority order, Brief §8 refined by the audit)

1. **Placement**: 800 grid, foundations / walls / ramps / stairs / catwalks / floating platforms, edge snap, nudge,
   zoop, rotate, hologram valid/invalid (`M_Hologram`), materialise/dematerialise, dismantle + mass-dismantle
   with refund. Port-to-port snapping for belts.
2. **Belts**: `UFGBeltSubsystem` ticks all belts; spline belts with curve limits; one ISM per item type
   (world-wide, not per belt); lifts, splitters, mergers; Mk1-3 speeds; visible backing-up. Items on belts saved.
3. **Machines**: recipe picker (UMG), multiple ports, per-minute rate display, standby, glow-shell overclock;
   state → animation/emissive/VFX/audio; significance manager.
4. **Power**: circuits via poles + cables (catenary spline mesh), power graph, fuse trip/reset, batteries,
   lightning rods.
5. **Fluids** (simplified): pipes, pump, valve, throughput cap.
6. **Progression**: Hub milestones, Tide Lab, tower phases, data cores → alternates, Trade Buoy shop, to-do list.
7. **Player**: Enhanced Input; controller split into components; inventory with stacks; Workbench hold-to-craft;
   equipment (dive mask, glider-pack, scanner, salvage cutter); zipline; skiff.
8. **Save**: versioned, complete (belt items, machine progress, fuel, timers, trades, story queue, Fish API
   history, weather); autosave every 5 min (not on every PIE end once tests use `FGNewGame`).
9. **Story**: messages, Sequencer flashbacks, replies, drawings, choices, endings; Fish API queue + fallback.
10. **UI**: UMG HUD, build menu, milestone screen, recipe tooltips, power graph, production stats, settings.

---

## 5. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Iris Xe can't render or measure the Target tier | Can't verify §9 perf; slow iteration | Two tiers (D6); stills at High; ask for a GPU test machine (Q1) |
| RAM 0.4-2 GB free with the editor open | Blender/UBT stalls, editor crashes | One Blender at a time; close Blender after each run; ask the user to close heavy apps during sessions |
| D: has 16 GB free | DDC + textures + builds fill the disk | Texture budgets; shared trims; watch `Saved/` and DDC; consider moving DDC to C: |
| LFS quota 1 GB | Push fails mid-production | D7; ask about a data pack (Q2) |
| Procedural Blender art may not reach a Satisfactory-1.0 8/10 | M1 gate fails | Kitbash-first, trims, CC0 scans for organic shapes, strict QA loop; escalate after 3 rounds |
| One editor, many agents | Crashes from concurrent calls | `EDITOR.lock`; only 4 roles may touch it |
| Monolithic controller rewrite breaks P1-P2 | Regressions | Rewrite behind scripted tests (`test_building`, `test_phase2`) |

---

## 6. Performance targets (replace Brief §9 "Performance"; D6)

Measured on **this laptop** (Intel Iris Xe, i7-1165G7, 16 GB) in a **standalone game** run (`-game`, not PIE),
1080p output, `stat unit` over a fixed fly-through of the QA cameras. "Floor" = the 1% low frame rate.

| Preset | Internal res (TSR) | GI / reflections | Shadows | Target / floor fps | Large factory floor* |
|---|---|---|---|---|---|
| Low | 50% | no Lumen: skylight + SSAO, no SSR | shadow maps, short range | 60 / 45 | 40 |
| Medium | 58% | lightest software Lumen GI in 5.8 + SSR | VSM low (or CSM if faster) | 45 / 30 | 30 |
| High | 67% | software Lumen GI + reflections | VSM | 30 / 25 | 25 |
| **Epic** | 100% (strong PC) | full Lumen (hardware RT where present), MegaLights, high volumetrics | VSM high | **not measured here**: full quality, never reduced for this laptop | — |

\* 200+ machines running with full belts (the `FGStressFactory` test scene from `Design/Tech.md`).

- RAM: the standalone game stays under **5 GB** working set at High on this laptop.
- Every gameplay feature works on Low; visuals degrade, function doesn't.
- **Epic test kit** (deliverable, kept current from M1): the Epic section of `Config/DefaultScalability.ini`, a
  one-command switch (`FGQuality Epic` and the `sg.*` values), and `Production/EpicTestPlan.md`: what to install,
  how to launch, the camera path, what to measure (`stat unit`, `stat gpu`, Insights) and what to send back.
  Target on a strong PC (RTX 3070-class): 60 fps at 1080p, 30+ at 1440p.

## 7. Open questions for the user (batched)

- ~~Q1 Target hardware~~ **Answered 2026-10-31:** re-baseline Low/Medium/High to this laptop, keep Epic at full
  quality for strong PCs, keep Epic ready and documented for a later test (D6, §6).
- ~~Q2 Git LFS~~ **Answered 2026-10-31:** no paid data pack; stay inside the free 1 GB (D20).
- ~~Q3 Keys and libraries~~ **Answered 2026-10-31:** no paid keys; free sources and our own generated art; install
  free MCPs/skills when they are needed (D20).
- ~~Q4 Names~~ **Answered 2026-10-31:** everything in English, character names too (D19).
