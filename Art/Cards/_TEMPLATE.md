# <Id> — <Display Name>  (card v1, <date>, art-director)
> Manifest `<Id>` · category · phase P# · tier wear <x> (bible §5.4) · hero y/n · twin: `ArtSource/<Id>/card.json`
> (copy `Art/Cards/_TEMPLATE.card.json`; the `rig` block is the engine contract, Design/Tech.md §5). 60 lines max.

## 1. Story purpose
<1-3 lines: what it does for Isla, which beat it serves, what its surfaces say (salvage vs confident).>

## 2. Footprint and ports (UE cm, origin = footprint centre, base Z 0, +X = front/output)
- Footprint <X x Y> cells = <cm x cm>; body to a 50 cm margin = <bounds_cm>; height <= <cm> (data row `Height`).
- Placement: foundation (100 cm sub-grid) / terrain (800 grid) / node / water. Rotation 90 deg steps.
| Port | Dir | Kind | loc_cm | yaw | Frame |
|---|---|---|---|---|---|
| In0 | In | Solid | [-800, 0, 100] | 180 | `Kit_PortFrame_Belt`, blue rim |
| Out0 | Out | Solid | [800, 0, 100] | 0 | `Kit_PortFrame_Belt`, orange rim |
- Power socket `power` [x, y, z] on `Kit_PowerSocket`. Snaps (structures only): name / type / loc_cm / yaw.

## 3. Silhouette (the 50 m read; bible §4.6 family: <family>)
<2-3 lines in words: the one signature shape, mass split 60/30/10, where detail clusters.>
```
SIDE (from -Y, +X right)                TOP (+X right, +Y up)
  <ascii, 1 char = 50 cm, mark ports      <ascii, footprint box, ports,
   I/O at 100 cm, lamp L, pivots *>        lamp L, ladder H, hatch D>
```

## 4. Moving parts (pivot on the axis; no collision/children; primary + secondary at different rates; clear at both extremes)
| Part | Role | Pivot (Blender m) | Axis | Rate @100% | Amplitude | Notes / clearance |
|---|---|---|---|---|---|---|
| Drum | Rotator | (0, 0, 4.2) | [0,1,0] | 90 deg/s | - | primary motion |
| Fan | Rotator | ... | [0,0,1] | 360 deg/s | - | secondary motion |

## 5. Paint zones and materials (slots from `bslib.mats.SLOTS` only)
- Paint_Primary: <big masses>. Paint_Secondary: <frame/base>. Paint_Detail: <stripes, trims>.
- Metal_Bare / Metal_Dark: <frames, rails, gears>. Rubber: <hoses, gaskets>. Glass: <windows, opaque>.
- Emissive_Tech: <accents>. Decals (`Decal_Atlas`): model plate, PKW logo per visible side, >= 2 pictograms, flow arrows.

## 6. Lights, VFX, audio hooks (states: Tech §5 table)
- StatusLight: `Kit_StatusLight` at [x, y, z], seen from front + both sides. Work lights: <...>.
- WorkVFX: `NS_<FX id>` on part <part> at offset <cm>. Idle: <steam wisp>. Unpowered: spark burst.
- Audio: LoopWorking <...>, LoopIdle <...>, SfxStart/SfxStop <...>; emitter at <part>.

## 7. References (`Art/References.md`): R### <what to take> · R### <...> · bar R00# (side-by-side only)

## 8. Budgets (bible §10)
Tris <= <n> total, moving parts <= <n>; textures: trims + atlas (unique 2K only if stated here);
collision: <n> boxes/convex on Body; Nanite on, `Decals` part non-Nanite.

## 9. Kit pieces to reuse (`ArtSource/Kit/`, never re-modelled)
`Kit_PortFrame_Belt` `Kit_StatusLight` `Kit_PowerSocket` `Kit_Ladder` `Kit_Railing` `Kit_Hatch` `Kit_Bolt` ...

## 10. Deliverables
`Tools/Art/assets/<Id>.py` (parametric) · `ArtSource/<Id>/card.json` · export FBX per part + `assembly.json` ·
`preview/` 4 views + close-up + plan view, `contact.jpg` · `selfcheck.md` (tris, slots, pivots, ports measured).

## 11. Acceptance checklist
- [ ] Silhouette signature reads flat black at 50 m; 3 form sizes; every edge bevelled.
- [ ] Footprint, height, bounds_cm and every port loc/yaw match §2 within 1 cm; port centres at Z 100.
- [ ] Moving parts separate, pivots on axis, no intersection at both extremes, no collision.
- [ ] Only standard slot names; `BS_Mask` baked on every part; tris within §8.
- [ ] Status lamp visible from 3 sides; decals legible; kit pieces reused; wear matches tier.
- [ ] Previews + self-check delivered; art-director pass, then visual-qa avg >= 8, none < 7.
