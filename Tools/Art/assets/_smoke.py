"""Pipeline smoke test: a small bevelled block with a drum part. Not a game asset."""
import bslib
from bslib import geo, mats, export, preview

card = bslib.load_card()
bslib.reset_scene()
body = geo.box("Body", (3.0, 2.4, 2.0), loc=(0, 0, 1.0), bevel=0.04)
mats.assign(body, "Paint_Primary")
base = geo.box("Base", (3.4, 2.8, 0.3), loc=(0, 0, 0.15), bevel=0.03)
mats.assign(base, "Paint_Secondary")
port = geo.box("PortOut", (0.1, 1.0, 0.9), loc=(1.55, 0, bslib.PORT_HEIGHT), bevel=0.02)
mats.assign(port, "Port_Out")
hose = geo.tube("Hose", [(-1.0, 1.25, 1.6), (-0.4, 1.6, 2.4), (0.6, 1.3, 2.2)], 0.08)
mats.assign(hose, "Rubber")
drum = geo.cyl("Drum", 0.6, 1.2, loc=(0, 0, 2.6), rot=(90, 0, 0), bevel=0.03)
mats.assign(drum, "Metal_Bare")
lamp = geo.cyl("Lamp", 0.08, 0.1, loc=(1.2, -1.0, 2.05), bevel=0.01, verts=16)
mats.assign(lamp, "Emissive_Status")
rows = export.export_parts(card, {"Body": [body, base, port, hose, lamp], "Drum": [drum]}, pivots={"Drum": (0, 0, 2.6)})
objs = [o for o in __import__("bpy").data.objects if o.type == "MESH"]
preview.render(card, objs)
bslib.log("SMOKE_OK", rows)
