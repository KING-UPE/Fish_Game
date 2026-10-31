import os
import math
import random

OUTPUT_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OBJ_PATH = os.path.join(OUTPUT_DIR, "SM_BlackSandDeposit.obj")

class MeshBuilder:
    def __init__(self):
        self.verts = []
        self.uvs = []
        self.normals = []
        self.materials = {}  # mat_name -> list of faces: [(v1, vt1, vn1), ...]
        self.current_mat = "Default"

    def set_material(self, name):
        self.current_mat = name
        if name not in self.materials:
            self.materials[name] = []

    def add_vert(self, x, y, z):
        self.verts.append((x, y, z))
        return len(self.verts)

    def add_uv(self, u, v):
        self.uvs.append((u, v))
        return len(self.uvs)

    def add_normal(self, nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        self.normals.append((nx/l, ny/l, nz/l))
        return len(self.normals)

    def add_tri(self, v1, v2, v3, uv1, uv2, uv3, n1, n2, n3):
        self.materials[self.current_mat].append([
            (v1, uv1, n1),
            (v2, uv2, n2),
            (v3, uv3, n3)
        ])

    def add_quad(self, v1, v2, v3, v4, uv1, uv2, uv3, uv4, n1, n2, n3, n4):
        self.add_tri(v1, v2, v3, uv1, uv2, uv3, n1, n2, n3)
        self.add_tri(v1, v3, v4, uv1, uv3, uv4, n1, n3, n4)

    def add_cylinder(self, p1, p2, r, segs=12, cap_top=True, cap_bot=True):
        """Adds a cylinder from p1 to p2 with radius r."""
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        if length < 1e-4:
            return
        # Orthonormal basis
        axis = (dx/length, dy/length, dz/length)
        up = (0, 0, 1) if abs(axis[2]) < 0.9 else (1, 0, 0)
        u_axis = (up[1]*axis[2] - up[2]*axis[1], up[2]*axis[0] - up[0]*axis[2], up[0]*axis[1] - up[1]*axis[0])
        u_len = math.sqrt(sum(c*c for c in u_axis))
        u_axis = tuple(c/u_len for c in u_axis)
        v_axis = (axis[1]*u_axis[2] - axis[2]*u_axis[1], axis[2]*u_axis[0] - axis[0]*u_axis[2], axis[0]*u_axis[1] - axis[1]*u_axis[0])

        ring_bot, ring_top = [], []
        norm_bot, norm_top = [], []
        uv_bot, uv_top = [], []

        for i in range(segs):
            theta = 2.0 * math.pi * i / segs
            ct, st = math.cos(theta), math.sin(theta)
            nx = u_axis[0]*ct + v_axis[0]*st
            ny = u_axis[1]*ct + v_axis[1]*st
            nz = u_axis[2]*ct + v_axis[2]*st
            norm_idx = self.add_normal(nx, ny, nz)

            bx = p1[0] + r*nx
            by = p1[1] + r*ny
            bz = p1[2] + r*nz
            tx = p2[0] + r*nx
            ty = p2[1] + r*ny
            tz = p2[2] + r*nz

            ring_bot.append(self.add_vert(bx, by, bz))
            ring_top.append(self.add_vert(tx, ty, tz))
            norm_bot.append(norm_idx)
            norm_top.append(norm_idx)

            u = i / segs
            uv_bot.append(self.add_uv(u, 0.0))
            uv_top.append(self.add_uv(u, 1.0))

        # Side quads
        for i in range(segs):
            next_i = (i + 1) % segs
            # Account for UV wrap
            uv_next_b = uv_bot[next_i] if next_i > 0 else self.add_uv(1.0, 0.0)
            uv_next_t = uv_top[next_i] if next_i > 0 else self.add_uv(1.0, 1.0)
            self.add_quad(
                ring_bot[i], ring_bot[next_i], ring_top[next_i], ring_top[i],
                uv_bot[i], uv_next_b, uv_next_t, uv_top[i],
                norm_bot[i], norm_bot[next_i], norm_top[next_i], norm_top[i]
            )

        # Caps
        if cap_bot:
            c_norm = self.add_normal(-axis[0], -axis[1], -axis[2])
            c_vert = self.add_vert(p1[0], p1[1], p1[2])
            c_uv = self.add_uv(0.5, 0.5)
            for i in range(segs):
                next_i = (i + 1) % segs
                self.add_tri(c_vert, ring_bot[next_i], ring_bot[i], c_uv, uv_bot[next_i], uv_bot[i], c_norm, c_norm, c_norm)

        if cap_top:
            c_norm = self.add_normal(axis[0], axis[1], axis[2])
            c_vert = self.add_vert(p2[0], p2[1], p2[2])
            c_uv = self.add_uv(0.5, 0.5)
            for i in range(segs):
                next_i = (i + 1) % segs
                self.add_tri(c_vert, ring_top[i], ring_top[next_i], c_uv, uv_top[i], uv_top[next_i], c_norm, c_norm, c_norm)

    def add_box(self, center, size, rot=(0,0,0)):
        """Adds an oriented box."""
        cx, cy, cz = center
        sx, sy, sz = size[0]*0.5, size[1]*0.5, size[2]*0.5
        yaw, pitch, roll = math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])

        # Rotation matrix
        cyaw, syaw = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)

        # Composite rotation (Z * Y * X)
        r00 = cyaw*cp
        r01 = cyaw*sp*sr - syaw*cr
        r02 = cyaw*sp*cr + syaw*sr
        r10 = syaw*cp
        r11 = syaw*sp*sr + cyaw*cr
        r12 = syaw*sp*cr - cyaw*sr
        r20 = -sp
        r21 = cp*sr
        r22 = cp*cr

        def transform(vx, vy, vz):
            rx = r00*vx + r01*vy + r02*vz + cx
            ry = r10*vx + r11*vy + r12*vz + cy
            rz = r20*vx + r21*vy + r22*vz + cz
            return rx, ry, rz

        def transform_n(nx, ny, nz):
            rx = r00*nx + r01*ny + r02*nz
            ry = r10*nx + r11*ny + r12*nz
            rz = r20*nx + r21*ny + r22*nz
            return rx, ry, rz

        corners = [
            (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
            (-sx, -sy,  sz), (sx, -sy,  sz), (sx, sy,  sz), (-sx, sy,  sz)
        ]
        v_idx = [self.add_vert(*transform(*c)) for c in corners]

        uv0 = self.add_uv(0, 0)
        uv1 = self.add_uv(1, 0)
        uv2 = self.add_uv(1, 1)
        uv3 = self.add_uv(0, 1)

        faces = [
            # bottom (-Z)
            (0, 3, 2, 1, (0, 0, -1)),
            # top (+Z)
            (4, 5, 6, 7, (0, 0, 1)),
            # front (-Y)
            (0, 1, 5, 4, (0, -1, 0)),
            # right (+X)
            (1, 2, 6, 5, (1, 0, 0)),
            # back (+Y)
            (2, 3, 7, 6, (0, 1, 0)),
            # left (-X)
            (3, 0, 4, 7, (-1, 0, 0)),
        ]

        for i1, i2, i3, i4, n in faces:
            norm_idx = self.add_normal(*transform_n(*n))
            self.add_quad(v_idx[i1], v_idx[i2], v_idx[i3], v_idx[i4], uv0, uv1, uv2, uv3, norm_idx, norm_idx, norm_idx, norm_idx)

    def add_octahedron(self, center, size, rot=(0,0,0)):
        """Adds a faceted magnetite octahedron crystal with sharp face normals."""
        cx, cy, cz = center
        rx, ry, rz = size[0]*0.5, size[1]*0.5, size[2]*0.5
        yaw, pitch, roll = math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])

        cyaw, syaw = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)

        r00 = cyaw*cp
        r01 = cyaw*sp*sr - syaw*cr
        r02 = cyaw*sp*cr + syaw*sr
        r10 = syaw*cp
        r11 = syaw*sp*sr + cyaw*cr
        r12 = syaw*sp*cr - cyaw*sr
        r20 = -sp
        r21 = cp*sr
        r22 = cp*cr

        def xform(vx, vy, vz):
            return (r00*vx + r01*vy + r02*vz + cx,
                    r10*vx + r11*vy + r12*vz + cy,
                    r20*vx + r21*vy + r22*vz + cz)

        # 6 cardinal vertices of octahedron
        top = xform(0, 0, rz)
        bot = xform(0, 0, -rz)
        px = xform(rx, 0, 0)
        nx = xform(-rx, 0, 0)
        py = xform(0, ry, 0)
        ny = xform(0, -ry, 0)

        tri_faces = [
            (top, px, py),
            (top, py, nx),
            (top, nx, ny),
            (top, ny, px),
            (bot, py, px),
            (bot, nx, py),
            (bot, ny, nx),
            (bot, px, ny),
        ]

        uv1 = self.add_uv(0.5, 1.0)
        uv2 = self.add_uv(0.0, 0.0)
        uv3 = self.add_uv(1.0, 0.0)

        for p1, p2, p3 in tri_faces:
            # Face normal
            v21 = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
            v31 = (p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2])
            fnx = v21[1]*v31[2] - v21[2]*v31[1]
            fny = v21[2]*v31[0] - v21[0]*v31[2]
            fnz = v21[0]*v31[1] - v21[1]*v31[0]
            n_idx = self.add_normal(fnx, fny, fnz)

            v1_i = self.add_vert(*p1)
            v2_i = self.add_vert(*p2)
            v3_i = self.add_vert(*p3)
            self.add_tri(v1_i, v2_i, v3_i, uv1, uv2, uv3, n_idx, n_idx, n_idx)

    def add_hex_bolt(self, center, radius, height, normal):
        """Adds a hexagonal bolt head."""
        axis = normal
        l = math.sqrt(sum(c*c for c in axis)) or 1.0
        axis = tuple(c/l for c in axis)
        p1 = center
        p2 = (center[0] + axis[0]*height, center[1] + axis[1]*height, center[2] + axis[2]*height)
        self.add_cylinder(p1, p2, radius, segs=6, cap_top=True, cap_bot=False)

    def export_obj(self, filepath):
        with open(filepath, "w") as f:
            f.write("# SM_BlackSandDeposit - FishGame High Fidelity Model\n")
            f.write(f"# Vertices: {len(self.verts)}\n")
            f.write(f"# Normals: {len(self.normals)}\n")
            f.write(f"# UVs: {len(self.uvs)}\n")

            for x, y, z in self.verts:
                f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
            for u, v in self.uvs:
                f.write(f"vt {u:.4f} {v:.4f}\n")
            for nx, ny, nz in self.normals:
                f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")

            for mat_name, faces in self.materials.items():
                if not faces:
                    continue
                f.write(f"usemtl {mat_name}\n")
                for tri in faces:
                    p1, p2, p3 = tri
                    f.write(f"f {p1[0]}/{p1[1]}/{p1[2]} {p2[0]}/{p2[1]}/{p2[2]} {p3[0]}/{p3[1]}/{p3[2]}\n")

        print(f"Exported OBJ: {filepath} with {len(self.verts)} verts and {sum(len(f) for f in self.materials.values())} triangles across {len(self.materials)} materials.")

print("MeshBuilder helper defined.")
