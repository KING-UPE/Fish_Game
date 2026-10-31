# Tools/Art — the asset pipeline

Card → parametric Blender script → per-part FBX + wear masks + previews → deferred UE import → QA.
Verified end to end on 2026-10-31 with `assets/_smoke.py` (Blender 5.2 → UE 5.8: scale, Y flip, pivots,
Nanite, slot names, vertex masks, collision).

## Layout
| Path | What |
|---|---|
| `run_blender.py` | The only way to run Blender: headless, one at a time (lock), waits for free RAM, logs to `ArtSource/_work/logs/` |
| `lib/bslib/` | Shared Blender helpers: `geo` (bevelled primitives, tubes, arrays, booleans, pivots, tri counts), `mats` (standard slot names), `masks` (BS_Mask vertex wear masks), `export` (per-part FBX + `assembly.json`), `preview` (4 views, close-up, plan view, contact sheet) |
| `kit/` | Kitbash library scripts (bolts, vents, grilles, pipes, hatches, ladders, railings, port frames…), M1 wave 2 |
| `assets/<id>.py` | One parametric script per asset (one modeler agent each) |
| `ue_import.py` | Editor-side import: `schedule(card_dir, dest)` then `status()` from a later call |

## Conventions (the contract between Blender and Unreal)
- 1 Blender unit = 1 m (lands as cm in UE). Footprint centred on the origin, base at Z = 0.
- **+X is the machine's front / output side.** UE flips Y: Blender (x, y, z) m → UE (100x, −100y, 100z) cm.
- Belt ports: centre at `bslib.PORT_HEIGHT` (1.0 m) above the base, inside a port frame (`Port_In` blue /
  `Port_Out` orange slots).
- Material slots use the names in `bslib/mats.py` `SLOTS` only; `ue_import.SLOT_MI` maps them to material
  instances of the masters. A new slot name needs both files and the bible.
- Moving parts are separate entries in the `parts` dict passed to `export.export_parts()`, each with its pivot
  (world point, metres). `assembly.json` records the UE-space offsets the engine uses to place them.
- Every exported part gets `BS_Mask` vertex colour: R edge wear, G AO, B cavity (Plan D13).

## Commands
```powershell
python Tools/Art/run_blender.py Tools/Art/assets/<id>.py -- ArtSource/<id>/card.json
python Tools/Art/run_blender.py --which
```
Outputs: `ArtSource/<id>/export/*.fbx` + `assembly.json` (git-ignored, regenerable),
`ArtSource/<id>/preview/*.png` (ignored) + `contact.jpg` (committed).
