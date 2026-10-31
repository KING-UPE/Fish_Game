"""bslib: the shared Blender helpers for Blue Signal asset scripts (run inside Blender 4.x/5.x).

Asset scripts run through `python Tools/Art/run_blender.py <script> -- <card.json>` and use:

    import bslib
    from bslib import geo, mats, masks, preview, export
    card = bslib.load_card()            # the card.json passed after `--`
    bslib.reset_scene()
    body = geo.box("Body", (4, 4, 3), loc=(0, 0, 1.5), bevel=0.04)
    mats.assign(body, "Paint_Primary")
    ...
    parts = {"Body": [body, frame], "Drum": [drum]}         # part name -> objects; one static mesh each
    export.export_parts(card, parts, pivots={"Drum": (0, 0, 2.1)})
    preview.render(card, [obj for objs in parts.values() for obj in objs])

Units: 1 Blender unit = 1 m (exports land as cm in UE). Axes: +X is the machine's front (output side),
+Z up. Footprint is centred on the origin, base at Z = 0.
"""
import json
import os
import sys

import bpy

ROOT = os.environ.get("BS_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

GRID = 8.0            # foundation cell, metres (800 cm)
PORT_HEIGHT = 1.0     # standard belt-port centre height above the base, metres (bible §Machines)


def log(*a):
    print("[bs]", *a, flush=True)


def args():
    """Arguments after `--` on the Blender command line."""
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def load_card(path=None):
    """Load the asset card JSON (first script arg by default). Adds `_dir` = ArtSource/<id>."""
    path = path or (args()[0] if args() else None)
    if not path:
        raise SystemExit("bslib.load_card: pass ArtSource/<id>/card.json after --")
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    with open(path, encoding="utf-8") as f:
        card = json.load(f)
    card.setdefault("id", os.path.basename(os.path.dirname(path)))
    card["_dir"] = os.path.dirname(path)
    log("card", card["id"], card.get("name", ""))
    return card


def reset_scene():
    """Empty factory scene in metres."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0
    return s


def out_dir(card, sub):
    d = os.path.join(card["_dir"], sub)
    os.makedirs(d, exist_ok=True)
    return d
