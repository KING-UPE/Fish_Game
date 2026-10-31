"""Wear masks baked into vertex colour (no unique textures needed; Plan D13).

Colour attribute `BS_Mask` (the only one exported, so UE imports it as vertex colour):
    R = edge wear   (convexity: 1 on bevelled outer edges)
    G = ambient occlusion (1 = open, 0 = occluded), baked with Cycles
    B = cavity      (concavity: 1 in creases and seams)
    A = 1
M_Factory_Master reads these for edge wear, AO dirt and cavity grime. Bevelled hard-surface meshes are dense
at edges, which is exactly where the mask needs resolution.
"""
import bpy
import numpy as np

from . import log

ATTR = "BS_Mask"


def _convexity(me):
    """Per-vertex convexity in [-1, 1] (+ = convex edge, - = concave crease)."""
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    nor = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("normal", nor)
    nor = nor.reshape(n, 3)
    e = np.empty(len(me.edges) * 2, dtype=np.int32)
    me.edges.foreach_get("vertices", e)
    e = e.reshape(-1, 2)
    acc = np.zeros(n, dtype=np.float32)
    cnt = np.zeros(n, dtype=np.float32)
    for a, b in ((0, 1), (1, 0)):
        d = co[e[:, b]] - co[e[:, a]]
        ln = np.linalg.norm(d, axis=1)
        ln[ln == 0] = 1
        dot = -np.einsum("ij,ij->i", d / ln[:, None], nor[e[:, a]])   # >0: neighbour below tangent = convex
        np.add.at(acc, e[:, a], dot)
        np.add.at(cnt, e[:, a], 1)
    cnt[cnt == 0] = 1
    return np.clip(acc / cnt * 3.0, -1, 1)


def _smooth(me, values, iterations=2):
    e = np.empty(len(me.edges) * 2, dtype=np.int32)
    me.edges.foreach_get("vertices", e)
    e = e.reshape(-1, 2)
    v = values.copy()
    for _ in range(iterations):
        acc = v.copy()
        cnt = np.ones_like(v)
        np.add.at(acc, e[:, 0], v[e[:, 1]])
        np.add.at(acc, e[:, 1], v[e[:, 0]])
        np.add.at(cnt, e[:, 0], 1)
        np.add.at(cnt, e[:, 1], 1)
        v = acc / cnt
    return v


def bake(obj, ao_samples=48, ao_distance=0.6):
    """Write BS_Mask on a finished mesh object (apply modifiers first). Removes other colour attributes."""
    me = obj.data
    for a in list(me.color_attributes):
        me.color_attributes.remove(a)
    attr = me.color_attributes.new(ATTR, "BYTE_COLOR", "POINT")

    conv = _smooth(me, _convexity(me))
    edge = np.clip(conv, 0, 1) ** 0.7
    cav = np.clip(-conv, 0, 1) ** 0.7

    # AO via Cycles bake into the colour attribute (G channel), then pack R/B around it.
    scene = bpy.context.scene
    prev_engine = scene.render.engine
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = ao_samples
    scene.render.bake.target = "VERTEX_COLORS"
    scene.world = scene.world or bpy.data.worlds.new("BS_World")
    scene.world.light_settings.distance = ao_distance
    me.color_attributes.active_color = attr
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.bake(type="AO")
        col = np.empty(len(me.vertices) * 4, dtype=np.float32)
        attr.data.foreach_get("color", col)
        ao = col.reshape(-1, 4)[:, 0]
    except RuntimeError as ex:  # no AO is better than no export
        log("AO bake failed, using 1.0:", ex)
        ao = np.ones(len(me.vertices), dtype=np.float32)
    scene.render.engine = prev_engine

    out = np.stack([edge, ao, cav, np.ones_like(ao)], axis=1).astype(np.float32).ravel()
    attr.data.foreach_set("color", out)
    me.color_attributes.active_color = attr
    me.color_attributes.render_color_index = 0
    log(f"masks {obj.name}: verts {len(me.vertices)}, edge mean {edge.mean():.2f}, ao mean {ao.mean():.2f}")
    return obj
