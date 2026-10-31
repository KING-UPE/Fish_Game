# Asset Manifest (index for `Production/AssetManifest.csv`)

Owner: art-director. 344 rows, every art asset Blue Signal needs. Source data: `Design/Data/*.json` (54 buildables,
58 items), StoryBeats §1/§3, Blue_Signal §4-5, Plan §3 + D2-D5/D15. Checked by script: no missing buildable or item.

**Columns.** `id` PascalCase_With_Underscores = folder `ArtSource/<id>/` and `/Game/Blue/Art/<Category>/<id>/`
(buildable id minus `_` = buildables.json `Name`; items are `Item_<Name>`; equipment items are `Tool_<Name>`) ·
`category` (17 fixed values below) · `phase` first appearance 0-5 or E (endings) · `priority` P0 M1 slice / P1
needed for its phase's milestone / P2 polish · `hero` y = studied up close (machines, specials, landmarks,
first-person tools, creatures, cinematic sets) · `footprint` buildables in 100 cm cells = Size x 8 (h in notes),
others approx. metres · `owner` the discipline · `status` planned → carded → modelled → imported → approved ·
`score` QA average · `notes` brief + mesh sharing (`mesh = X + tint`). No commas inside fields.
Materials and VFX have no own category: they sit under the family they serve (`Kit_Mat_*`, `FX_*`, `*_Ground`).

| Category | Rows | | Category | Rows | | Category | Rows |
|---|---|---|---|---|---|---|---|
| KitbashKit | 36 | | Structure | 14 | | Sky | 8 |
| Special | 23 | | Item | 52 | | FlashbackSet | 8 |
| Machine | 11 | | Tool | 12 | | Cinematic | 23 |
| Extractor | 9 | | Vehicle | 2 | | UI | 28 |
| Power | 10 | | Creature | 8 | | EnvKit | 69 |
| Logistics | 12 | | WreckKit | 19 | | **Total** | **344** |

Priority: **P0 72** · P1 261 · P2 11. Hero 85. Owners: asset-modeler 203, environment-artist 58, ui-artist 30, material-artist 27, vfx-artist 20, narrative-designer 6.

## M1 slice (the 72 P0 rows) in build order
1. **Materials base** (material-artist, wave 1): Kit_Mat_FactoryMaster, Kit_Trims, Kit_Decals, Tool_BuildHologram.
2. **Kitbash library** (asset-modeler, wave 2; 30 parts): Kit_Bolt, Kit_RivetStrip, Kit_EdgeCap, Kit_Panel, Kit_Foot,
   Kit_PortFrame_Belt, Kit_PowerSocket, Kit_ControlPanel, Kit_StatusLight, Kit_WorkLight, Kit_Vent_Louvre, Kit_Grille,
   Kit_Fan, Kit_Hatch, Kit_Door_Service, Kit_Pipe_Straight, Kit_Pipe_Elbow, Kit_Pipe_Flange, Kit_Hose, Kit_Tank,
   Kit_Chimney, Kit_Piston, Kit_GearHousing, Kit_Gauge, Kit_Ladder, Kit_Railing, Kit_Grate, Kit_CableTray,
   Kit_Conduit, Kit_WarningPlate.
3. **Grid pieces** (sets scale for everything after): Foundation, Wall, Ramp.
4. **Heroes** (one opus modeler each, wave 3): Smelter, Press, Drill_Mk1, LanderHub, LanderHub_S1_SolarWing, Workbench.
5. **Logistics + power**: Belt_Mk1, Belt_Support, PowerPole, Power_Cable.
6. **Props**: Node_OreVent_Ferrite, Item_FerriteOre, Item_FerriteIngot, Item_FerritePlate, Item_FerriteRod, Wreck_HullPlate_A.
7. **Environment** (wave 3): Env_CrashReef_Ground, Env_Ocean_Water, Env_Ocean_Shoreline, Env_CrashReef_Cliff_A,
   Env_CrashReef_Rock_A, Env_CrashReef_Rock_B, Env_CrashReef_Coral_A, Env_CrashReef_Coral_B, Env_CrashReef_Tree_A,
   Env_CrashReef_Shrub_A, Env_CrashReef_GroundCover_A, Env_CrashReef_GroundCover_B, Env_CrashReef_Scatter.
8. **Sky + VFX** (wave 4): Sky_AtmosphereClouds, Sky_RingedPlanet, FX_Machine_Sparks, FX_Machine_Steam, FX_Machine_Impact, Tool_BuildMaterialiseFX.
