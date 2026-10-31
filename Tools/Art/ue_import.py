"""Editor-side import of a bslib asset (run INSIDE the Unreal editor, e.g. via Tools/ue.py or execute_python_code).

Two calls, because heavy imports must not run inside the MCP task (CLAUDE.md §1.15):

    # call 1: schedule (returns immediately; the import runs on the next editor tick)
    import sys; sys.path.insert(0, r"D:/Game/FishGame/Tools/Art"); import importlib, ue_import
    importlib.reload(ue_import); ue_import.schedule(r"ArtSource/<id>", "/Game/Blue/Art/<Category>/<Asset>")

    # call 2, a few seconds later (wait from PowerShell, never time.sleep here): report + post-process
    import ue_import; print(ue_import.status())

What it does per part listed in ArtSource/<id>/export/assembly.json:
- legacy FBX importer (Interchange FBX off), static mesh, no materials/textures, normals imported,
  vertex colours REPLACED (the BS_Mask wear masks), Nanite on, no auto collision;
- material slots -> material instances by slot name (SLOT_MI below; missing MIs are reported, not faked);
- simple box collision on the part named "Body" unless the card says otherwise;
- saves every asset and records the assembly (part offsets) in the status for the BP/engine.
"""
import json
import os

import unreal

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MI_DIR = "/Game/Blue/Art/Materials/Instances"

# slot name (bslib.mats.SLOTS) -> material instance. Filled by the material artist's masters.
SLOT_MI = {name: f"{MI_DIR}/MI_{name}" for name in (
    "Paint_Primary", "Paint_Secondary", "Paint_Detail", "Metal_Bare", "Metal_Dark", "Rubber", "Glass",
    "Emissive_Status", "Emissive_Tech", "Port_In", "Port_Out")}

_g = globals()
_g.setdefault("_state", {"ran": True, "handle": None, "result": None})


def _import_fbx(fbx, dest, name):
    t = unreal.AssetImportTask()
    t.filename = fbx
    t.destination_path = dest
    t.destination_name = name
    t.replace_existing = True
    t.automated = True
    t.save = False
    ui = unreal.FbxImportUI()
    ui.import_mesh = True
    ui.import_as_skeletal = False
    ui.import_materials = False
    ui.import_textures = False
    ui.import_animations = False
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    d = ui.static_mesh_import_data
    d.set_editor_property("convert_scene_unit", True)   # bslib exports metres; without this 1 m lands as 1 cm
    d.set_editor_property("combine_meshes", True)
    d.set_editor_property("auto_generate_collision", False)
    d.set_editor_property("build_nanite", True)
    d.set_editor_property("generate_lightmap_u_vs", False)
    d.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
    d.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    t.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    return list(t.imported_object_paths)


def _post(sm, part, slots, card):
    notes = []
    for i, slot in enumerate(slots):
        mi_path = SLOT_MI.get(slot)
        if mi_path and unreal.EditorAssetLibrary.does_asset_exist(mi_path):
            sm.set_material(i, unreal.EditorAssetLibrary.load_asset(mi_path))
        else:
            notes.append(f"no MI for slot {slot}")
    coll_parts = card.get("collision_parts", ["Body"])
    if part in coll_parts:
        sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        sub.remove_collisions(sm)
        sub.add_simple_collisions(sm, unreal.ScriptCollisionShapeType.BOX)
    bb = sm.get_bounding_box()
    size = [round(v, 1) for v in (bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z)]
    return size, notes


def _run(card_dir, dest):
    asm_path = os.path.join(card_dir, "export", "assembly.json")
    asm = json.load(open(asm_path, encoding="utf-8"))
    card_path = os.path.join(card_dir, "card.json")
    card = json.load(open(card_path, encoding="utf-8")) if os.path.isfile(card_path) else {}
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    rows = []
    for p in asm["parts"]:
        fbx = os.path.join(card_dir, p["fbx"])
        paths = _import_fbx(fbx, dest, p["mesh"])
        sm_path = f"{dest}/{p['mesh']}"
        sm = unreal.EditorAssetLibrary.load_asset(sm_path)
        if not sm:
            rows.append({"part": p["part"], "error": f"import failed ({paths})"})
            continue
        size, notes = _post(sm, p["part"], p["slots"], card)
        unreal.EditorAssetLibrary.save_asset(sm_path)
        nanite = sm.get_editor_property("nanite_settings").get_editor_property("enabled")
        rows.append({"part": p["part"], "asset": sm_path, "size_cm": size, "nanite": nanite,
                     "offset_cm": p["offset_cm"], "notes": notes})
    return {"asset": asm["asset"], "dest": dest, "parts": rows}


def schedule(card_dir, dest):
    """Queue the import on the next editor tick (safe from inside execute_python_code)."""
    card_dir = card_dir if os.path.isabs(card_dir) else os.path.join(ROOT, card_dir)
    st = _g["_state"] = {"ran": False, "handle": None, "result": None}

    def _tick(_dt):
        if st["ran"]:
            return
        st["ran"] = True
        try:
            st["result"] = _run(card_dir, dest)
            unreal.log("BS_IMPORT_OK " + json.dumps(st["result"]))
        except Exception as ex:  # report, don't crash the editor tick
            st["result"] = {"error": repr(ex)}
            unreal.log_error("BS_IMPORT_ERR " + repr(ex))
        finally:
            unreal.unregister_slate_post_tick_callback(st["handle"])

    st["handle"] = unreal.register_slate_post_tick_callback(_tick)
    return f"scheduled import of {card_dir} -> {dest}"


def status():
    st = _g["_state"]
    return json.dumps({"ran": st["ran"], "result": st["result"]}, indent=1)
