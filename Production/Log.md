# Production Log

Newest first. Each entry: what was decided/done, what's next, blockers. Keep it short; details live in files.

## 2026-11-01 (session 4) — M0 closed, M1 engine step 1 done
**Found on resume**: no agents running; stale `EDITOR.lock`; `Progression.md` and the playtime estimate still TODO;
step 1 C++ written but never built (it didn't compile).
**Done**: M0 merged to `dev`, tagged `m0` (D21, D22). Step 1 built and tested on `m1/core`: test_building and
test_phase2 pass end to end (`Production/TestLog.md`). Root cause of the "no collision" failures: 1-10 cm source meshes
whose convex hulls don't register (`Tools/Setup/05_mesh_collision.py`). Platform raised above the ocean plane.
**Open**: `Config/DefaultEngine.ini` (Nanite off, DX11, SM5) stays uncommitted until the user decides; it must be
settled before hero assets (wave 3) because it conflicts with the bible's Nanite rule and D6's Epic. `stat FG` counters
not yet read on screen. `stash@{0}` and `D:\Game\TideAndTreasure_stage` can still be deleted.
**Next**: M1 wave 1: slice cards, material masters, engine step 2 (`UFGFactorySubsystem`), then the kitbash library.

## 2026-10-31 (session 3) — finish M0, start M1 engine
**Recovered**: session 2's art-director and game-designer outputs were lost again (no `Art/`, no
`Design/Progression.md`, no playtime model); `Design/Data/*.json` survived and is now committed (`013d66a`).
**Done**: the fixed preamble text is now written down (`AgentRules.md` §8) plus a write-early rule (§7).
**In flight**: art-director A (ArtBible, References, card template), art-director B (AssetManifest.csv/.md),
game-designer (Progression.md, `Tools/Design/playtime_model.py --check`, Playtime.md), engine-programmer
(Tech §9 step 1: baseline tests, UFGCheatManager, UFGTestLibrary/FGDump, BuildId, UFGFactorySettings, stat FG;
holds `EDITOR.lock`; its Source changes go on `m1/core`, cut from `dev` after the m0 merge).
**Next**: review + commit the M0 docs on `m0/plan`, merge to `dev`, tag `m0`, push; then M1 wave 1 cards,
material masters and the kitbash library.
**Incident 22:39-23:30**: the user's Antigravity agent started *Tide & Treasure* in this folder: it stashed
Blue Signal (`stash@{1}`), switched to an orphan branch, later checked out `dev`. Agents were stopped mid-run.
Resolved with the user (Plan D18): Tide & Treasure moved to the worktree `D:\Game\TideAndTreasure` (branch
`tide-and-treasure`, snapshot `b5e63cc`); Blue Signal restored here on `m0/plan` (stash popped, newer drafts
from `Saved/BlueSignalRecovery/` laid on top) and committed (`1afa138`..`2a8569b`). A producer move script
briefly moved Art/ArtSource/Config/2 smoke assets to a staging folder; all moved back, nothing lost.
**User decisions**: D19 English names (Isla, Skye, Ray), D20 free only (no LFS pack, no paid keys; OFL fonts ok).
**Open**: `Config/DefaultEngine.ini` uncommitted change (Nanite off, DX11, SM5; matches the running editor,
origin unknown) — asked the user. `stash@{0}` (superseded partial CSV) and the empty
`D:\Game\TideAndTreasure_stage` can be deleted. Agents resumed (bible, progression, engine step 1).

## 2026-10-31 (session 2) — M0 continued
**Decided**: user answered Q1: Low/Medium/High speed targets on this laptop, Epic kept at full quality for
strong PCs and documented for a later test (Plan D6, §6; `Production/EpicTestPlan.md`).
**Recovered**: the previous session ended mid-run. `Design/Tech.md` (complete) and `Design/Data/*.json`
(complete, consistent) survived; `Art/*`, `Design/Progression.md` and the playtime model did not.
**Done**: art pipeline committed (`851a5d1`, verified Blender 5.2 → UE 5.8); Tech.md committed.
**In flight**: art-director (bible, references, card template, asset manifest), game-designer (Progression.md,
playtime model + `--check`).
**Next**: review both, merge `m0/plan` → `dev`, tag `m0`, push; M1 wave 1 (engine M1 steps per Tech.md §9,
material masters, slice cards, kitbash library).

## 2026-10-31 — M0 Audit and plan (in progress, branch `m0/plan`)
**Done**
- Checkpointed the previous session's uncommitted graphics work on `wip/phase3` (`f3998e9`); created `dev` and
  `m0/plan` from it (Plan D1).
- Saved the user's brief as `Production/Brief.md`; wrote `Production/AgentRules.md` (fixed preamble rules) and
  14 role files in `.claude/agents/`.
- Audit (`Production/Audit.md`): Iris Xe iGPU, 0.4 GB free RAM, D: 16 GB free, Blender missing (installing);
  code is a solid data-driven core with placeholder visuals, straight belts, global power, Canvas HUD.
- `Production/Plan.md`: decisions D1-D12, milestone/branch plan, M1 slice plan, engine backlog, risks, Q1-Q3.

**In flight**: art-director (bible, references, card template), game-designer (progression, data JSON,
playtime model), narrative-designer (beat sheet, line budget).

**Next**: asset manifest from the buildable list; merge `m0/plan` → `dev`, tag `m0`; start M1 wave 1
(pipeline tools, cards, materials).

**Blockers**: none. Questions Q1-Q3 (Plan §6) are asked but don't block M1.
