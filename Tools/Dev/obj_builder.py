import os
import math

class ObjMeshBuilder:
    def __init__(self):
        self.vertices = []   # list of (x, y, z)
        self.normals = []    # list of (nx, ny, nz)
        self.uvs = []        # list of (u, v)
        self.materials = {}  # mat_name -> list of faces [ [(v_idx, vt_idx, vn_idx), ...] ]
        self.current_mat = "default"

    def set_material(self, mat_name):
        self.current_mat = mat_name
        if mat_name not in self.materials:
            self.materials[mat_name] = []

    def add_vertex(self, x, y, z):
        self.vertices.append((float(x), float(y), float(z)))
        return len(self.vertices)

    def add_normal(self, nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz)
        if l > 1e-6:
            nx, ny, nz = nx/l, ny/l, nz/l
        else:
            nx, ny, nz = 0.0, 0.0, 1.0
        self.normals.append((float(nx), float(ny), float(nz)))
        return len(self.normals)

    def add_uv(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_face(self, v_indices, vt_indices, vn_indices):
        if self.current_mat not in self.materials:
            self.materials[self.current_mat] = []
        face = list(zip(v_indices, vt_indices, vn_indices))
        self.materials[self.current_mat].append(face)

    def add_quad(self, p0, p1, p2, p3, uv0=(0,0), uv1=(1,0), uv2=(1,1), uv3=(0,1), normal=None):
        if normal is None:
            # compute cross product (p1-p0) x (p3-p0)
            u = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            v = (p3[0]-p0[0], p3[1]-p0[1], p3[2]-p0[2])
            nx = u[1]*v[2] - u[2]*v[1]
            ny = u[2]*v[0] - u[0]*v[2]
            nz = u[0]*v[1] - u[1]*v[0]
            normal = (nx, ny, nz)
        
        n_idx = self.add_normal(*normal)
        v0 = self.add_vertex(*p0)
        v1 = self.add_vertex(*p1)
        v2 = self.add_vertex(*p2)
        v3 = self.add_vertex(*p3)

        t0 = self.add_uv(*uv0)
        t1 = self.add_uv(*uv1)
        t2 = self.add_uv(*uv2)
        t3 = self.add_uv(*uv3)

        # two triangles
        self.add_face([v0, v1, v2], [t0, t1, t2], [n_idx, n_idx, n_idx])
        self.add_face([v0, v2, v3], [t0, t2, t3], [n_idx, n_idx, n_idx])

    def add_box(self, cx, cy, cz, sx, sy, sz, uvs=None):
        """Add an oriented axis-aligned box with center (cx, cy, cz) and size (sx, sy, sz)."""
        hx, hy, hz = sx/2.0, sy/2.0, sz/2.0
        # 8 corners
        # Front face (+Y):
        # Back face (-Y):
        # Left face (-X):
        # Right face (+X):
        # Top face (+Z):
        # Bottom face (-Z):
        def_uv = ( (0,0), (1,0), (1,1), (0,1) ) if not uvs else uvs
        
        # +Z (Top)
        self.add_quad(
            (cx - hx, cy - hy, cz + hz),
            (cx + hx, cy - hy, cz + hz),
            (cx + hx, cy + hy, cz + hz),
            (cx - hx, cy + hy, cz + hz),
            *def_uv, normal=(0, 0, 1)
        )
        # -Z (Bottom)
        self.add_quad(
            (cx - hx, cy + hy, cz - hz),
            (cx + hx, cy + hy, cz - hz),
            (cx + hx, cy - hy, cz - hz),
            (cx - hx, cy - hy, cz - hz),
            *def_uv, normal=(0, 0, -1)
        )
        # +X (Right)
        self.add_quad(
            (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy + hy, cz - hz),
            (cx + hx, cy + hy, cz + hz),
            (cx + hx, cy - hy, cz + hz),
            *def_uv, normal=(1, 0, 0)
        )
        # -X (Left)
        self.add_quad(
            (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy - hy, cz - hz),
            (cx - hx, cy - hy, cz + hz),
            (cx - hx, cy + hy, cz + hz),
            *def_uv, normal=(-1, 0, 0)
        )
        # +Y (Front)
        self.add_quad(
            (cx + hx, cy + hy, cz - hz),
            (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy + hy, cz + hz),
            (cx + hx, cy + hy, cz + hz),
            *def_uv, normal=(0, 1, 0)
        )
        # -Y (Back)
        self.add_quad(
            (cx - hx, cy - hy, cz - hz),
            (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy - hy, cz + hz),
            (cx - hx, cy - hy, cz + hz),
            *def_uv, normal=(0, -1, 0)
        )

    def add_cylinder(self, p1, p2, radius, segments=16, capped=True, smooth=True):
        """Add a cylinder between p1 and p2 with radius."""
        # Axis vector
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        vz = p2[2] - p1[2]
        length = math.sqrt(vx*vx + vy*vy + vz*vz)
        if length < 1e-5:
            return
        ax, ay, az = vx/length, vy/length, vz/length

        # Choose robust perp vector
        if abs(ax) < 0.6:
            px, py, pz = 1.0, 0.0, 0.0
        elif abs(ay) < 0.6:
            px, py, pz = 0.0, 1.0, 0.0
        else:
            px, py, pz = 0.0, 0.0, 1.0
        # Gram-schmidt
        dot = px*ax + py*ay + pz*az
        ux, uy, uz = px - dot*ax, py - dot*ay, pz - dot*az
        ul = math.sqrt(ux*ux + uy*uy + uz*uz)
        ux, uy, uz = ux/ul, uy/ul, uz/ul

        # Third basis vector w = a x u
        wx = ay*uz - az*uy
        wy = az*ux - ax*uz
        wz = ax*uy - ay*ux

        # Generate ring points at p1 and p2
        ring1_v = []
        ring2_v = []
        ring_n = []
        ring_raw_n = []
        ring_uv1 = []
        ring_uv2 = []

        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)

            rx = radius * (cos_t * ux + sin_t * wx)
            ry = radius * (cos_t * uy + sin_t * wy)
            rz = radius * (cos_t * uz + sin_t * wz)

            nx = cos_t * ux + sin_t * wx
            ny = cos_t * uy + sin_t * wy
            nz = cos_t * uz + sin_t * wz

            v1_idx = self.add_vertex(p1[0] + rx, p1[1] + ry, p1[2] + rz)
            v2_idx = self.add_vertex(p2[0] + rx, p2[1] + ry, p2[2] + rz)
            n_idx = self.add_normal(nx, ny, nz)

            u_coord = i / segments
            uv1_idx = self.add_uv(u_coord, 0.0)
            uv2_idx = self.add_uv(u_coord, 1.0)

            ring1_v.append(v1_idx)
            ring2_v.append(v2_idx)
            ring_n.append(n_idx)
            ring_raw_n.append((nx, ny, nz))
            ring_uv1.append(uv1_idx)
            ring_uv2.append(uv2_idx)

        # Connect sides
        for i in range(segments):
            next_i = (i + 1) % segments
            v1_a, v2_a = ring1_v[i], ring2_v[i]
            v1_b, v2_b = ring1_v[next_i], ring2_v[next_i]

            na, nb = ring_n[i], ring_n[next_i]
            t1_a, t2_a = ring_uv1[i], ring_uv2[i]
            t1_b = self.add_uv((i + 1) / segments, 0.0)
            t2_b = self.add_uv((i + 1) / segments, 1.0)

            if smooth:
                self.add_face([v1_a, v1_b, v2_b], [t1_a, t1_b, t2_b], [na, nb, nb])
                self.add_face([v1_a, v2_b, v2_a], [t1_a, t2_b, t2_a], [na, nb, na])
            else:
                # Flat normal
                side_n = self.add_normal(
                    (ring_raw_n[i][0] + ring_raw_n[next_i][0]) / 2.0,
                    (ring_raw_n[i][1] + ring_raw_n[next_i][1]) / 2.0,
                    (ring_raw_n[i][2] + ring_raw_n[next_i][2]) / 2.0
                )
                self.add_face([v1_a, v1_b, v2_b], [t1_a, t1_b, t2_b], [side_n, side_n, side_n])
                self.add_face([v1_a, v2_b, v2_a], [t1_a, t2_b, t2_a], [side_n, side_n, side_n])

        # End caps
        if capped:
            # Bottom cap at p1 (normal: -axis)
            n_cap1 = self.add_normal(-ax, -ay, -az)
            v_center1 = self.add_vertex(p1[0], p1[1], p1[2])
            uv_center1 = self.add_uv(0.5, 0.5)

            for i in range(segments):
                next_i = (i + 1) % segments
                t_a = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*i/segments), 0.5 + 0.5*math.sin(2*math.pi*i/segments))
                t_b = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*next_i/segments), 0.5 + 0.5*math.sin(2*math.pi*next_i/segments))
                self.add_face([v_center1, ring1_v[next_i], ring1_v[i]], [uv_center1, t_b, t_a], [n_cap1, n_cap1, n_cap1])

            # Top cap at p2 (normal: +axis)
            n_cap2 = self.add_normal(ax, ay, az)
            v_center2 = self.add_vertex(p2[0], p2[1], p2[2])
            uv_center2 = self.add_uv(0.5, 0.5)

            for i in range(segments):
                next_i = (i + 1) % segments
                t_a = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*i/segments), 0.5 + 0.5*math.sin(2*math.pi*i/segments))
                t_b = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*next_i/segments), 0.5 + 0.5*math.sin(2*math.pi*next_i/segments))
                self.add_face([v_center2, ring2_v[i], ring2_v[next_i]], [uv_center2, t_a, t_b], [n_cap2, n_cap2, n_cap2])

    def add_cone_frustum(self, p1, p2, r1, r2, segments=16, capped=True, smooth=True):
        """Add a truncated cone from p1 (radius r1) to p2 (radius r2)."""
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        vz = p2[2] - p1[2]
        length = math.sqrt(vx*vx + vy*vy + vz*vz)
        if length < 1e-5:
            return
        ax, ay, az = vx/length, vy/length, vz/length

        # Choose robust perp vector
        if abs(ax) < 0.6:
            px, py, pz = 1.0, 0.0, 0.0
        elif abs(ay) < 0.6:
            px, py, pz = 0.0, 1.0, 0.0
        else:
            px, py, pz = 0.0, 0.0, 1.0
        dot = px*ax + py*ay + pz*az
        ux, uy, uz = px - dot*ax, py - dot*ay, pz - dot*az
        ul = math.sqrt(ux*ux + uy*uy + uz*uz)
        ux, uy, uz = ux/ul, uy/ul, uz/ul

        wx = ay*uz - az*uy
        wy = az*ux - ax*uz
        wz = ax*uy - ay*ux

        ring1_v = []
        ring2_v = []
        ring_n = []
        ring_uv1 = []
        ring_uv2 = []

        dr = r1 - r2
        norm_len = math.sqrt(length*length + dr*dr)
        sin_slope = length / norm_len
        cos_slope = dr / norm_len

        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)

            r1_x = r1 * (cos_t * ux + sin_t * wx)
            r1_y = r1 * (cos_t * uy + sin_t * wy)
            r1_z = r1 * (cos_t * uz + sin_t * wz)

            r2_x = r2 * (cos_t * ux + sin_t * wx)
            r2_y = r2 * (cos_t * uy + sin_t * wy)
            r2_z = r2 * (cos_t * uz + sin_t * wz)

            rad_x = cos_t * ux + sin_t * wx
            rad_y = cos_t * uy + sin_t * wy
            rad_z = cos_t * uz + sin_t * wz

            nx = sin_slope * rad_x + cos_slope * ax
            ny = sin_slope * rad_y + cos_slope * ay
            nz = sin_slope * rad_z + cos_slope * az

            v1_idx = self.add_vertex(p1[0] + r1_x, p1[1] + r1_y, p1[2] + r1_z)
            v2_idx = self.add_vertex(p2[0] + r2_x, p2[1] + r2_y, p2[2] + r2_z)
            n_idx = self.add_normal(nx, ny, nz)

            u_coord = i / segments
            uv1_idx = self.add_uv(u_coord, 0.0)
            uv2_idx = self.add_uv(u_coord, 1.0)

            ring1_v.append(v1_idx)
            ring2_v.append(v2_idx)
            ring_n.append(n_idx)
            ring_uv1.append(uv1_idx)
            ring_uv2.append(uv2_idx)

        for i in range(segments):
            next_i = (i + 1) % segments
            v1_a, v2_a = ring1_v[i], ring2_v[i]
            v1_b, v2_b = ring1_v[next_i], ring2_v[next_i]
            na, nb = ring_n[i], ring_n[next_i]
            t1_a, t2_a = ring_uv1[i], ring_uv2[i]
            t1_b = self.add_uv((i + 1) / segments, 0.0)
            t2_b = self.add_uv((i + 1) / segments, 1.0)

            self.add_face([v1_a, v1_b, v2_b], [t1_a, t1_b, t2_b], [na, nb, nb])
            self.add_face([v1_a, v2_b, v2_a], [t1_a, t2_b, t2_a], [na, nb, na])

        if capped:
            if r1 > 1e-4:
                n_cap1 = self.add_normal(-ax, -ay, -az)
                v_center1 = self.add_vertex(p1[0], p1[1], p1[2])
                uv_center1 = self.add_uv(0.5, 0.5)
                for i in range(segments):
                    next_i = (i + 1) % segments
                    t_a = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*i/segments), 0.5 + 0.5*math.sin(2*math.pi*i/segments))
                    t_b = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*next_i/segments), 0.5 + 0.5*math.sin(2*math.pi*next_i/segments))
                    self.add_face([v_center1, ring1_v[next_i], ring1_v[i]], [uv_center1, t_b, t_a], [n_cap1, n_cap1, n_cap1])

            if r2 > 1e-4:
                n_cap2 = self.add_normal(ax, ay, az)
                v_center2 = self.add_vertex(p2[0], p2[1], p2[2])
                uv_center2 = self.add_uv(0.5, 0.5)
                for i in range(segments):
                    next_i = (i + 1) % segments
                    t_a = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*i/segments), 0.5 + 0.5*math.sin(2*math.pi*i/segments))
                    t_b = self.add_uv(0.5 + 0.5*math.cos(2*math.pi*next_i/segments), 0.5 + 0.5*math.sin(2*math.pi*next_i/segments))
                    self.add_face([v_center2, ring2_v[i], ring2_v[next_i]], [uv_center2, t_a, t_b], [n_cap2, n_cap2, n_cap2])

    def add_hex_bolt(self, center, axis, radius, height):
        """Add a hexagonal bolt head at center pointing along axis."""
        p1 = center
        p2 = (center[0] + axis[0]*height, center[1] + axis[1]*height, center[2] + axis[2]*height)
        self.add_cylinder(p1, p2, radius, segments=6, capped=True, smooth=False)

    def write_obj(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write("# FishGame Hard-Surface Mesh\n")
            for x, y, z in self.vertices:
                f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
            for u, v in self.uvs:
                f.write(f"vt {u:.5f} {v:.5f}\n")
            for nx, ny, nz in self.normals:
                f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")
            
            for mat_name, faces in self.materials.items():
                if not faces:
                    continue
                f.write(f"usemtl {mat_name}\n")
                for face in faces:
                    face_str = " ".join(f"{v}/{vt}/{vn}" for v, vt, vn in face)
                    f.write(f"f {face_str}\n")
        print(f"Exported {filepath}: {len(self.vertices)} verts, {sum(len(f) for f in self.materials.values())} tris")

print("ObjMeshBuilder loaded successfully.")
