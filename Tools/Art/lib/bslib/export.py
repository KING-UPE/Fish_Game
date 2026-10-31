"""Export each moving part as its own static mesh with its pivot at the origin, plus an assembly file.

    export_parts(card, {"Body": [body], "Drum": [drum]}, pivots={"Drum": (0, 0, 2.1)})

writes ArtSource/<id>/export/SM_<Name>_<Part>.fbx for every part and ArtSource/<id>/export/assembly.json:
    {"asset": id, "parts": [{"part", "mesh", "fbx", "offset_cm": [x, y, z], "tris", "slots"}]}
`offset_cm` is the part pivot in Unreal space (cm, Y flipped: UE is left-handed), so the engine/BP places
the component there. Parts without a pivot keep the asset origin (0, 0, 0).
"""
import json
import os

import bpy
from mathutils import Vector

from . import log, out_dir
from . import geo, masks as _masks


def _ue_cm(v):
    return [round(v[0] * 100, 2), round(-v[1] * 100, 2), round(v[2] * 100, 2)]


def export_parts(card, parts, pivots=None, bake_masks=True, mesh_prefix=None):
    pivots = pivots or {}
    d = out_dir(card, "export")
    prefix = mesh_prefix or card.get("mesh_name") or f"SM_{card.get('name', card['id']).replace(' ', '')}"
    rows = []
    for part, objs in parts.items():
        obj = geo.join(objs, f"{prefix}_{part}") if len(objs) > 1 else geo.finish(objs)[0]
        obj.name = f"{prefix}_{part}"
        pivot = Vector(pivots.get(part, (0, 0, 0)))
        geo.set_origin(obj, pivot)
        if bake_masks:
            _masks.bake(obj)
        tris = geo.tri_count([obj])
        # export at the origin so the pivot becomes the mesh origin
        saved = obj.location.copy()
        obj.location = (0, 0, 0)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        fbx = os.path.join(d, f"{obj.name}.fbx")
        bpy.ops.export_scene.fbx(
            filepath=fbx, use_selection=True, object_types={"MESH"},
            # FBX_SCALE_NONE bakes metres->cm into the data (FBX_SCALE_UNITS imported 100x too small in UE 5.8)
            apply_unit_scale=True, apply_scale_options="FBX_SCALE_NONE", bake_space_transform=True,
            axis_forward="X", axis_up="Z", use_mesh_modifiers=True, mesh_smooth_type="FACE",
            use_tspace=False, add_leaf_bones=False, colors_type="LINEAR", path_mode="STRIP")
        obj.location = saved
        rows.append({"part": part, "mesh": obj.name, "fbx": os.path.relpath(fbx, card["_dir"]).replace("\\", "/"),
                     "offset_cm": _ue_cm(pivot), "tris": tris,
                     "slots": [s.material.name for s in obj.material_slots if s.material]})
        log(f"exported {obj.name}: {tris} tris, slots {rows[-1]['slots']}")
    with open(os.path.join(d, "assembly.json"), "w", encoding="utf-8") as f:
        json.dump({"asset": card["id"], "parts": rows}, f, indent=2)
    log("assembly.json", len(rows), "parts, total tris", sum(r["tris"] for r in rows))
    return rows
