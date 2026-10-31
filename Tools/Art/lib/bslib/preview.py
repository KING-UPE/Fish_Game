"""Preview renders: 4 three-quarter angles, 1 close-up and a top-down plan at 1280x720, plus contact.jpg.

    preview.render(card, objs, closeup=(x, y, z))   # closeup = world point to frame (default: front face, port height)

Uses EEVEE (fast on the iGPU) with a sun + sky + grey ground, and a 1.8 m scale figure so size reads.
The plan view draws one 8 m foundation cell so the footprint can be checked against the grid.
Writes ArtSource/<id>/preview/view_0..3.png, closeup.png, top.png and contact.jpg (3 x 2 grid).
"""
import math
import os

import bpy
import numpy as np
from mathutils import Vector

from . import log, out_dir
from . import geo

W, H = 1280, 720


def _engine(scene):
    for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = name
            return name
        except TypeError:
            continue
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    return "CYCLES"


def _stage(scene, lo, hi):
    world = bpy.data.worlds.get("BS_Preview") or bpy.data.worlds.new("BS_Preview")
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexGradient")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    ramp.color_ramp.elements[0].color = (0.32, 0.36, 0.42, 1)
    ramp.color_ramp.elements[1].color = (0.62, 0.74, 0.86, 1)
    nt.links.new(sky.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 0.8
    nt.links.new(bg.outputs[0], out.inputs[0])
    scene.world = world

    sun = bpy.data.lights.new("BS_Sun", "SUN")
    sun.energy = 3.5
    sun.angle = math.radians(3)
    s = bpy.data.objects.new("BS_Sun", sun)
    s.rotation_euler = (math.radians(50), 0, math.radians(35))
    scene.collection.objects.link(s)

    size = max((hi - lo).x, (hi - lo).y) * 30 + 200
    ground = geo.box("BS_Ground", (size, size, 0.02), loc=(0, 0, lo.z - 0.011), bevel=0)
    gm = bpy.data.materials.new("BS_GroundMat")
    gm.diffuse_color = (0.18, 0.18, 0.18, 1)
    gm.use_nodes = True
    next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1)
    ground.data.materials.append(gm)

    # 1.8 m scale figure beside the asset
    fig = geo.cyl("BS_ScaleFigure", 0.22, 1.8, loc=(lo.x - 0.8, lo.y - 0.8, lo.z + 0.9), bevel=0.1, verts=16)
    fm = bpy.data.materials.new("BS_FigureMat")
    fm.diffuse_color = (0.75, 0.75, 0.78, 1)
    fig.data.materials.append(fm)
    return [s, ground, fig]


def _camera(scene, target, dist, yaw, pitch, lens=40):
    cam_data = bpy.data.cameras.get("BS_Cam") or bpy.data.cameras.new("BS_Cam")
    cam_data.lens = lens
    cam = bpy.data.objects.get("BS_Cam") or bpy.data.objects.new("BS_Cam", cam_data)
    if cam.name not in scene.collection.objects:
        scene.collection.objects.link(cam)
    y, p = math.radians(yaw), math.radians(pitch)
    cam.location = target + Vector((math.cos(y) * math.cos(p), math.sin(y) * math.cos(p), math.sin(p))) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    return cam


def _contact(paths, out_path):
    tiles = []
    for p in paths:
        img = bpy.data.images.load(p)
        px = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        tiles.append(px.reshape(img.size[1], img.size[0], 4)[::2, ::2])
        bpy.data.images.remove(img)
    th, tw = tiles[0].shape[:2]
    sheet = np.zeros((th * 2, tw * 3, 4), dtype=np.float32)
    sheet[..., 3] = 1
    order = [(1, 0), (1, 1), (1, 2), (0, 0), (0, 1), (0, 2)]   # numpy row 0 = bottom of the image in Blender
    for t, (r, c) in zip(tiles, order):
        sheet[r * th:(r + 1) * th, c * tw:(c + 1) * tw] = t
    img = bpy.data.images.new("BS_Contact", tw * 3, th * 2)
    img.pixels.foreach_set(sheet.ravel())
    img.filepath_raw = out_path
    img.file_format = "JPEG"
    img.save()
    return out_path


def render(card, objs, closeup=None):
    scene = bpy.context.scene
    engine = _engine(scene)
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.image_settings.file_format = "PNG"
    try:
        scene.view_settings.view_transform = "AgX"
    except TypeError:
        scene.view_settings.view_transform = "Filmic"
    lo, hi = geo.bounds(objs)
    extra = _stage(scene, lo, hi)
    center = (lo + hi) / 2
    radius = (hi - lo).length / 2
    d = out_dir(card, "preview")
    paths = []
    for i, yaw in enumerate((-35, 55, 145, 235)):
        _camera(scene, center, radius * 3.0 + 1.5, yaw, 22)
        scene.render.filepath = os.path.join(d, f"view_{i}.png")
        bpy.ops.render.render(write_still=True)
        paths.append(scene.render.filepath)
    # default close-up: the front (output) face around port height, where most detail lives
    target = Vector(closeup) if closeup else Vector((hi.x, lo.y + (hi - lo).y * 0.3, lo.z + min(1.4, (hi - lo).z * 0.5)))
    _camera(scene, target, max(1.6, radius * 1.1), -30, 12, lens=45)
    scene.render.filepath = os.path.join(d, "closeup.png")
    bpy.ops.render.render(write_still=True)
    paths.append(scene.render.filepath)
    # top-down orthographic plan with an 8 m grid cell outline: checks the footprint against the grid
    cam = _camera(scene, center, 50, 0, 89.9)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max((hi - lo).x, (hi - lo).y, 8.0) * 1.25
    cell = geo.box("BS_GridCell", (8.0, 8.0, 0.01), loc=(0, 0, lo.z + 0.005), bevel=0)
    cell.display_type = "WIRE"
    wire = cell.modifiers.new("BS_Wire", "WIREFRAME")
    wire.thickness = 0.06
    cm = bpy.data.materials.new("BS_GridMat")
    cm.diffuse_color = (0.25, 0.9, 0.85, 1)
    cell.data.materials.append(cm)
    extra.append(cell)
    scene.render.filepath = os.path.join(d, "top.png")
    bpy.ops.render.render(write_still=True)
    cam.data.type = "PERSP"
    paths.append(scene.render.filepath)
    sheet = _contact(paths, os.path.join(d, "contact.jpg"))
    for o in extra:
        bpy.data.objects.remove(o, do_unlink=True)
    log(f"previews ({engine}): {d}; contact {sheet}")
    return paths
