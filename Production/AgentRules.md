# Agent Rules — the fixed preamble for every Blue Signal agent

Read this file first, then your own agent file in `.claude/agents/`, then only the files your task names.
These rules outrank speed. The producer (the main session) owns the plan, git and the final say.

## 1. Authorities (who decides what)
| Question | Authority file |
|---|---|
| Story, characters, beats, choices, endings | `Design/Blue_Signal.md` (fixed core; see `Production/Brief.md` §1) |
| Numbers: items, recipes, rates, milestones, playtime | `Design/Progression.md` + `Design/Data/*.json` |
| Look: palette, materials, budgets, naming, quality bar | `Art/ArtBible.md` |
| One asset's spec | `Art/Cards/<id>.md` |
| Plan, decisions, milestone scope | `Production/Plan.md` |
| Status, what's done, blockers | `Production/Log.md` |
| Editor crash rules and tooling | `CLAUDE.md` + `SETUP.md` (law) |

Don't read `Production/Brief.md` in full unless your task says so; the files above distil it.

## 2. Hard limits of this machine (plan for them)
- **GPU: Intel Iris Xe (integrated, ~2 GB shared). No hardware ray tracing.** Lumen runs in software mode only.
  Speed targets for Low / Medium / High are measured here (`Production/Plan.md` §6), and every feature must run
  and be testable here. **Epic keeps full Satisfactory-1.0 quality for strong PCs: never cut Epic to fit this
  laptop.** Epic is rendered here only for QA stills; hardware-RT-only features must fall back cleanly.
- **RAM: 16 GB, often < 1 GB free** with the editor open. Check free RAM before any heavy process
  (`(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB` GB). Below 4 GB: one Blender at a time.
  Always close the Blender process you started.
- **Disk: D: ~16 GB free.** Keep textures within the bible budgets; don't leave big temp files in the repo.

## 3. The Unreal editor is ONE shared resource
- Only `engine-programmer`, `ue-integrator`, `visual-qa` and `playtester` may touch it, and only while holding
  `Production/EDITOR.lock`.
- Take the lock: if the file is absent, write one line `<agent> <ISO time> <task>`. If it exists and is younger
  than 30 min, stop and report "blocked: editor locked by <agent>". Never delete someone else's lock; report a
  stale one to the producer. Delete your own lock as your last action, even on failure.
- Reach the editor through the `unreal` MCP tools (`execute_python_code`, `capture_image`), or
  `python Tools/ue.py <script.py>` when the MCP tools are missing.
- Crash rules you must not break (details in `CLAUDE.md` §1): no BP edits during PIE; no world-lifecycle calls
  (open_level, travel, quit) from Python during PIE; no runtime spawn through tooling during PIE; FBX/heavy
  imports only via the deferred slate-tick pattern (§1.15), one at a time; start every Python script with
  `import warnings; warnings.simplefilter("ignore")` and print evidence after each change; never `time.sleep`
  inside `execute_python_code` (wait from PowerShell instead); load VibeUE skills one at a time; never
  `describe_toolset`; never delete `Binaries/` or `Intermediate/`.
- The editor does NOT redraw on asset changes: nudge the camera before re-capturing (§1.16).

## 4. Files and git
- Write only the files your agent owns or your task names. Don't edit someone else's files; ask in your report.
- **Don't commit, push, switch branches, stash or reset.** The producer commits each deliverable.
- Parametric scripts are the source of truth for art: `Tools/Art/*.py` + `ArtSource/<id>/card.json`.
  `.blend` files, raw exports and downloads under `ArtSource/` are git-ignored and must be regenerable.
- Every third-party file (texture, mesh, sound, font) gets a line in `Credits.md`:
  `| asset id | file | source URL | author | licence |`. Allowed licences: CC0, CC-BY (credit), Fab free /
  user-owned, Sonniss GDC bundles, and SIL OFL 1.1 for fonts only. Anything else: don't use it. Nothing paid
  (Plan D20).
- **Forbidden:** anything ripped from Satisfactory's files; the names FICSIT / Coffee Stain or their logos; any
  other copyrighted brand or character. Match the quality with original work. Reference images stay in
  git-ignored `Art/_refs/` and are never imported into Content.

## 5. Naming and units (summary; full list in the bible)
1 uu = 1 cm. Player 180 cm. Foundation grid 800 x 800 cm, walls 800 x 400. Prefixes
`SM_ SK_ M_ MI_ MF_ T_*_BC/_N/_ORM NS_ BP_ DT_ WBP_`. Content folders `/Game/Blue/Art/<Category>/<Asset>/`.

## 6. Report back in 15 lines or fewer
```
STATUS: done | partial | blocked — one sentence
FILES: paths produced or changed
SCORE: (QA / self-check numbers, if any)
ISSUES: open problems, decisions you need from the producer
NEXT: the obvious next step
```
Details go into files, never into the report.

## 7. Write early, write often
A session can end mid-run (session 2 lost the art bible and the progression doc this way). Create each output
file **as soon as you start** (headings + `TODO`), then fill it section by section, saving after each one. Never
hold a whole document in your head until the end.

## 8. The fixed preamble (the producer pastes this verbatim at the top of every agent prompt)
```
[Blue Signal production · fixed preamble v2]
Project: D:\Game\FishGame, the UE 5.8 game "Blue Signal". You are one agent of the production team; the
producer (main session) owns the plan, git and the final say.
1. Read Production/AgentRules.md now and obey it. Then your role file in .claude/agents/, then only the
   files your task names.
2. Authorities: story Design/Blue_Signal.md · numbers Design/Progression.md + Design/Data/*.json · look
   Art/ArtBible.md · plan Production/Plan.md · status Production/Log.md · editor law CLAUDE.md + SETUP.md.
3. Never commit, push, switch branches, stash or reset. Write only files you own or the task names.
4. Only engine-programmer, ue-integrator, visual-qa and playtester touch the Unreal editor, and only while
   holding Production/EDITOR.lock.
5. Create output files at once and save after every section (AgentRules §7).
6. Report in 15 lines or fewer: STATUS / FILES / SCORE / ISSUES / NEXT.
--- TASK ---
```
