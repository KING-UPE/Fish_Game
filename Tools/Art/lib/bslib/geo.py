"""Hard-surface primitives with real bevels and weighted normals.

Every primitive gets a Bevel modifier (angle-limited, so only hard edges round) and a Weighted Normal
modifier; `finish()` applies them. Sizes are full extents in metres; `loc` is the centre unless noted.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

DEFAULT_BEVEL = 0.015     # 1.5 cm: the minimum "no razor edge" bevel on anything the player can touch
DEFAULT_SEGMENTS = 3


def _link(obj, collection=None):
    (collection or bpy.context.scene.collection).objects.link(obj)
    return obj


def _mesh_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return _link(bpy.data.objects.new(name, me))


def add_bevel(obj, width=DEFAULT_BEVEL, segments=DEFAULT_SEGMENTS, angle=30.0, harden=True):
    if width <= 0:
        return obj
    m = obj.modifiers.new("BS_Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle)
    m.profile = 0.6
    m.miter_outer = "MITER_ARC"
    m.harden_normals = harden
    m.use_clamp_overlap = True
    return obj


def add_weighted_normals(obj):
    m = obj.modifiers.new("BS_WNormal", "WEIGHTED_NORMAL")
    m.keep_sharp = True
    m.weight = 100
    m.mode = "FACE_AREA"
    return obj


def _place(obj, loc, rot):
    obj.location = Vector(loc)
    obj.rotation_euler = [math.radians(a) for a in rot]
    return obj


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=DEFAULT_BEVEL, segments=DEFAULT_SEGMENTS):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = _mesh_obj(name, bm)
    _place(obj, loc, rot)
    add_bevel(obj, bevel, segments)
    return add_weighted_normals(obj)


def cyl(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), verts=32, bevel=DEFAULT_BEVEL,
        segments=DEFAULT_SEGMENTS, cap=True):
    """Cylinder along local Z (rotate with rot=(90,0,0) etc.)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth)
    obj = _mesh_obj(name, bm)
    _place(obj, loc, rot)
    add_bevel(obj, bevel, segments)
    return add_weighted_normals(obj)


def cone(name, r1, r2, depth, loc=(0, 0, 0), rot=(0, 0, 0), verts=32, bevel=DEFAULT_BEVEL):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r1, radius2=r2, depth=depth)
    obj = _mesh_obj(name, bm)
    _place(obj, loc, rot)
    add_bevel(obj, bevel)
    return add_weighted_normals(obj)


def torus(name, major, minor, loc=(0, 0, 0), rot=(0, 0, 0), major_seg=48, minor_seg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=major_seg, minor_segments=minor_seg)
    obj = bpy.context.active_object
    obj.name = name
    _place(obj, loc, rot)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def tube(name, points, radius, verts=16, closed=False):
    """A pipe/hose through world-space points (smooth curve, converted to mesh by finish())."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = max(2, verts // 4)
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = Vector(p)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    sp.use_cyclic_u = closed
    obj = _link(bpy.data.objects.new(name, cu))
    return obj


def array(obj, count, offset, name=None):
    """Linear copies of obj (linked data) offset by `offset` each; returns the list incl. obj."""
    out = [obj]
    for i in range(1, count):
        c = obj.copy()
        c.data = obj.data
        c.location = obj.location + Vector(offset) * i
        if name:
            c.name = f"{name}_{i:02d}"
        _link(c)
        out.append(c)
    return out


def radial(obj, count, axis_center=(0, 0, 0), axis="Z"):
    """Copies of obj rotated around a vertical axis through axis_center."""
    out = [obj]
    c0 = Vector(axis_center)
    for i in range(1, count):
        a = 2 * math.pi * i / count
        c = obj.copy()
        c.data = obj.data
        rot = Matrix.Rotation(a, 4, axis)
        c.matrix_world = Matrix.Translation(c0) @ rot @ Matrix.Translation(-c0) @ obj.matrix_world
        _link(c)
        out.append(c)
    return out


def boolean(target, cutter, op="DIFFERENCE", apply=True, hide_cutter=True):
    m = target.modifiers.new("BS_Bool", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    # booleans must run before bevel so the cut edges get bevelled too
    while target.modifiers[0] != m:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_move_up(modifier=m.name)
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=m.name)
    if hide_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def finish(objs):
    """Convert curves, make single-user, apply all modifiers, smooth-shade. Returns mesh objects."""
    out = []
    for obj in list(objs):
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if obj.type == "CURVE":
            bpy.ops.object.convert(target="MESH")
            obj = bpy.context.active_object
            add_weighted_normals(obj)
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        for m in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
        for p in obj.data.polygons:
            p.use_smooth = True
        out.append(obj)
    return out


def join(objs, name):
    """Join finished mesh objects into one (keeps material slots)."""
    objs = finish(objs)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    return obj


def set_origin(obj, point):
    """Move obj's origin (pivot) to a world-space point without moving the geometry."""
    p = Vector(point)
    mw = obj.matrix_world.copy()
    local = mw.inverted() @ p
    obj.data.transform(Matrix.Translation(-local))
    obj.matrix_world = mw @ Matrix.Translation(local)
    return obj


def tri_count(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for o in objs:
        if o.type != "MESH":
            continue
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n += len(me.loop_triangles)
        o.evaluated_get(dg).to_mesh_clear()
    return n


def bounds(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi
