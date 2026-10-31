"""Standard material slots. Slot NAMES are the contract with Unreal: the integrator maps each slot to a
material instance of the matching master (Art/ArtBible.md, Art/Materials.md). Blender colours are only
for preview renders; the final look comes from the UE masters.

If the bible renames a slot, change SLOTS here once; asset scripts only use the names.
"""
import bpy

# name: (preview base colour sRGB hex, metallic, roughness, emission strength)
SLOTS = {
    "Paint_Primary":   ("F2B33D", 0.0, 0.45, 0.0),   # Beacon Yellow (placeholder until the bible palette)
    "Paint_Secondary": ("2B3A4A", 0.0, 0.55, 0.0),   # Deep Hull Navy
    "Paint_Detail":    ("1C1C1C", 0.0, 0.5, 0.0),    # hazard stripes / trims (stripe pattern in UE)
    "Metal_Bare":      ("9A9EA3", 1.0, 0.35, 0.0),
    "Metal_Dark":      ("3A3D42", 1.0, 0.5, 0.0),
    "Rubber":          ("161616", 0.0, 0.85, 0.0),
    "Glass":           ("88B8C8", 0.0, 0.05, 0.0),
    "Emissive_Status": ("39D353", 0.0, 0.4, 6.0),    # status light; UE drives green/amber/red
    "Emissive_Tech":   ("3FE0D0", 0.0, 0.4, 4.0),    # Signal Teal accents
    "Port_In":         ("2F7BFF", 0.0, 0.4, 2.0),    # blue = input port frame
    "Port_Out":        ("FF7A1A", 0.0, 0.4, 2.0),    # orange = output port frame
}


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def get(name):
    """Get or create the preview material for a slot name."""
    if name not in SLOTS:
        raise KeyError(f"unknown material slot {name!r}; allowed: {', '.join(SLOTS)}")
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    hexc, metal, rough, emit = SLOTS[name]
    rgb = [_srgb_to_linear(int(hexc[i:i + 2], 16) / 255) for i in (0, 2, 4)]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        bsdf.inputs[key].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    if name == "Glass":
        bsdf.inputs["Alpha"].default_value = 0.35
    mat.diffuse_color = (*rgb, 1)
    return mat


def assign(objs, name):
    """Give each object exactly one slot (replaces existing slots). Use before joining parts."""
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    mat = get(name)
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
    return objs


def used_slots(obj):
    return [s.material.name for s in obj.material_slots if s.material]
