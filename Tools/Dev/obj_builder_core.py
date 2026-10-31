import math
import numpy as np

class ObjMeshBuilder:
    def __init__(self):
        self.vertices = []
        self.uvs = []
        self.normals = []
        # groups by material name: list of faces, where face is list of (v_idx, vt_idx, vn_idx)
        self.materials = {}
        self.current_material = "default"

    def set_material(self, mat_name):
        self.current_material = mat_name
        if mat_name not in self.materials:
            self.materials[mat_name] = []

    def add_quad(self, p1, p2, p3, p4, uv1=(0,0), uv2=(1,0), uv3=(1,1), uv4=(0,1), normal=None):
        """Adds a quad as two triangles with outward normal."""
        p1 = np.array(p1, dtype=float)
        p2 = np.array(p2, dtype=float)
        p3 = np.array(p3, dtype=float)
        p4 = np.array(p4, dtype=float)
        
        if normal is None:
            n = np.cross(p2 - p1, p3 - p1)
            norm = np.linalg.norm(n)
            n = n / norm if norm > 1e-9 else np.array([0, 0, 1])
        else:
            n = np.array(normal, dtype=float)
            norm = np.linalg.norm(n)
            n = n / norm if norm > 1e-9 else np.array([0, 0, 1])

        v_base = len(self.vertices) + 1
        vt_base = len(self.uvs) + 1
        vn_base = len(self.normals) + 1

        self.vertices.extend([p1, p2, p3, p4])
        self.uvs.extend([uv1, uv2, uv3, uv4])
        self.normals.append(n)

        # Triangle 1: 1, 2, 3
        f1 = [
            (v_base, vt_base, vn_base),
            (v_base + 1, vt_base + 1, vn_base),
            (v_base + 2, vt_base + 2, vn_base)
        ]
        # Triangle 2: 1, 3, 4
        f2 = [
            (v_base, vt_base, vn_base),
            (v_base + 2, vt_base + 2, vn_base),
            (v_base + 3, vt_base + 3, vn_base)
        ]

        if self.current_material not in self.materials:
            self.materials[self.current_material] = []
        self.materials[self.current_material].extend([f1, f2])

    def add_box(self, min_pt, max_pt, uv_box=(0, 0, 1, 1)):
        x0, y0, z0 = min_pt
        x1, y1, z1 = max_pt
        u0, v0, u1, v1 = uv_box

        # Bottom (-Z)
        self.add_quad([x0, y1, z0], [x1, y1, z0], [x1, y0, z0], [x0, y0, z0],
                      (u0, v0), (u1, v0), (u1, v1), (u0, v1), normal=[0, 0, -1])
        # Top (+Z)
        self.add_quad([x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
                      (u0, v0), (u1, v0), (u1, v1), (u0, v1), normal=[0, 0, 1])
        # Front (-Y)
        self.add_quad([x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1],
                      (u0, v0), (u1, v0), (u1, v1), (u0, v1), normal=[0, -1, 0])
        # Back (+Y)
        self.add_quad([x1, y1, z0], [x0, y1, z0], [x0, y1, z1], [x1, y1, z1],
                      (u0, v0), (u1, v0), (u1, v1), (u0, v1), normal=[0, 1, 0])
        # Left (-X)
        self.add_quad([x0, y1, z0], [x0, y0, z0], [x0, y0, z1], [x0, y1, z1],
                      (u0, v0), (u1, v0), (u1, v1), (u0, v1), normal=[-1, 0, 0])
        # Right (+X)
        self.add_quad([x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1],
                      (u0, v0), (u1, v0), (u1, v1), (u0, v1), normal=[1, 0, 0])

    def add_cylinder(self, p1, p2, radius, segments=24, capped=True, uv_u_range=(0, 1), uv_v_range=(0, 1)):
        p1 = np.array(p1, dtype=float)
        p2 = np.array(p2, dtype=float)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length < 1e-9:
            return
        z_dir = axis / length

        # Find orthogonal vectors
        if abs(z_dir[0]) < 0.8 and abs(z_dir[1]) < 0.8:
            up = np.array([0, 0, 1])
        else:
            up = np.array([0, 1, 0])
        x_dir = np.cross(z_dir, up)
        x_dir /= np.linalg.norm(x_dir)
        y_dir = np.cross(z_dir, x_dir)

        ring1 = []
        ring2 = []
        normals = []

        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            dx = math.cos(theta)
            dy = math.sin(theta)
            radial = dx * x_dir + dy * y_dir
            pt1 = p1 + radius * radial
            pt2 = p2 + radius * radial
            ring1.append(pt1)
            ring2.append(pt2)
            normals.append(radial)

        # Quads around circumference
        u0, u1 = uv_u_range
        v0, v1 = uv_v_range
        for i in range(segments):
            ui0 = u0 + (u1 - u0) * (i / segments)
            ui1 = u0 + (u1 - u0) * ((i + 1) / segments)
            
            # Vertices
            v_b = len(self.vertices) + 1
            vt_b = len(self.uvs) + 1
            vn_b = len(self.normals) + 1

            self.vertices.extend([ring1[i], ring1[i+1], ring2[i+1], ring2[i]])
            self.uvs.extend([(ui0, v0), (ui1, v0), (ui1, v1), (ui0, v1)])
            self.normals.extend([normals[i], normals[i+1], normals[i+1], normals[i]])

            f1 = [(v_b, vt_b, vn_b), (v_b+1, vt_b+1, vn_b+1), (v_b+2, vt_b+2, vn_b+2)]
            f2 = [(v_b, vt_b, vn_b), (v_b+2, vt_b+2, vn_b+2), (v_b+3, vt_b+3, vn_b+3)]
            self.materials[self.current_material].extend([f1, f2])

        if capped:
            # End cap 1 (at p1, pointing -z_dir)
            n1 = -z_dir
            c1_idx = len(self.vertices) + 1
            c1_vt = len(self.uvs) + 1
            c1_vn = len(self.normals) + 1
            self.vertices.append(p1)
            self.uvs.append((0.5, 0.5))
            self.normals.append(n1)

            for i in range(segments):
                theta1 = 2.0 * math.pi * i / segments
                theta2 = 2.0 * math.pi * (i + 1) / segments
                u_a = 0.5 + 0.5 * math.cos(theta1)
                v_a = 0.5 + 0.5 * math.sin(theta1)
                u_b = 0.5 + 0.5 * math.cos(theta2)
                v_b = 0.5 + 0.5 * math.sin(theta2)

                v_b = len(self.vertices) + 1
                vt_b = len(self.uvs) + 1
                self.vertices.extend([ring1[i+1], ring1[i]])
                self.uvs.extend([(u_b, v_b), (u_a, v_a)])

                f = [(c1_idx, c1_vt, c1_vn), (v_b, vt_b, c1_vn), (v_b+1, vt_b+1, c1_vn)]
                self.materials[self.current_material].append(f)

            # End cap 2 (at p2, pointing +z_dir)
            n2 = z_dir
            c2_idx = len(self.vertices) + 1
            c2_vt = len(self.uvs) + 1
            c2_vn = len(self.normals) + 1
            self.vertices.append(p2)
            self.uvs.append((0.5, 0.5))
            self.normals.append(n2)

            for i in range(segments):
                theta1 = 2.0 * math.pi * i / segments
                theta2 = 2.0 * math.pi * (i + 1) / segments
                u_a = 0.5 + 0.5 * math.cos(theta1)
                v_a = 0.5 + 0.5 * math.sin(theta1)
                u_b = 0.5 + 0.5 * math.cos(theta2)
                v_b = 0.5 + 0.5 * math.sin(theta2)

                v_b = len(self.vertices) + 1
                vt_b = len(self.uvs) + 1
                self.vertices.extend([ring2[i], ring2[i+1]])
                self.uvs.extend([(u_a, v_a), (u_b, v_b)])

                f = [(c2_idx, c2_vt, c2_vn), (v_b, vt_b, c2_vn), (v_b+1, vt_b+1, c2_vn)]
                self.materials[self.current_material].append(f)

    def add_cone(self, p1, p2, r1, r2, segments=24, capped1=True, capped2=True):
        p1 = np.array(p1, dtype=float)
        p2 = np.array(p2, dtype=float)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length < 1e-9:
            return
        z_dir = axis / length

        if abs(z_dir[0]) < 0.8 and abs(z_dir[1]) < 0.8:
            up = np.array([0, 0, 1])
        else:
            up = np.array([0, 1, 0])
        x_dir = np.cross(z_dir, up)
        x_dir /= np.linalg.norm(x_dir)
        y_dir = np.cross(z_dir, x_dir)

        ring1 = []
        ring2 = []
        normals = []

        # Cone slope angle
        dr = r1 - r2
        slope = math.atan2(dr, length)
        cos_s = math.cos(slope)
        sin_s = math.sin(slope)

        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            dx = math.cos(theta)
            dy = math.sin(theta)
            radial = dx * x_dir + dy * y_dir
            pt1 = p1 + r1 * radial
            pt2 = p2 + r2 * radial
            ring1.append(pt1)
            ring2.append(pt2)
            n = cos_s * radial + sin_s * z_dir
            normals.append(n / np.linalg.norm(n))

        for i in range(segments):
            ui0 = i / segments
            ui1 = (i + 1) / segments
            v_b = len(self.vertices) + 1
            vt_b = len(self.uvs) + 1
            vn_b = len(self.normals) + 1

            self.vertices.extend([ring1[i], ring1[i+1], ring2[i+1], ring2[i]])
            self.uvs.extend([(ui0, 0), (ui1, 0), (ui1, 1), (ui0, 1)])
            self.normals.extend([normals[i], normals[i+1], normals[i+1], normals[i]])

            f1 = [(v_b, vt_b, vn_b), (v_b+1, vt_b+1, vn_b+1), (v_b+2, vt_b+2, vn_b+2)]
            f2 = [(v_b, vt_b, vn_b), (v_b+2, vt_b+2, vn_b+2), (v_b+3, vt_b+3, vn_b+3)]
            self.materials[self.current_material].extend([f1, f2])

        if capped1 and r1 > 0:
            c1_idx = len(self.vertices) + 1
            c1_vt = len(self.uvs) + 1
            c1_vn = len(self.normals) + 1
            self.vertices.append(p1)
            self.uvs.append((0.5, 0.5))
            self.normals.append(-z_dir)
            for i in range(segments):
                v_b = len(self.vertices) + 1
                vt_b = len(self.uvs) + 1
                self.vertices.extend([ring1[i+1], ring1[i]])
                self.uvs.extend([(0, 0), (1, 0)])
                self.materials[self.current_material].append([(c1_idx, c1_vt, c1_vn), (v_b, vt_b, c1_vn), (v_b+1, vt_b+1, c1_vn)])

        if capped2 and r2 > 0:
            c2_idx = len(self.vertices) + 1
            c2_vt = len(self.uvs) + 1
            c2_vn = len(self.normals) + 1
            self.vertices.append(p2)
            self.uvs.append((0.5, 0.5))
            self.normals.append(z_dir)
            for i in range(segments):
                v_b = len(self.vertices) + 1
                vt_b = len(self.uvs) + 1
                self.vertices.extend([ring2[i], ring2[i+1]])
                self.uvs.extend([(0, 0), (1, 0)])
                self.materials[self.current_material].append([(c2_idx, c2_vt, c2_vn), (v_b, vt_b, c2_vn), (v_b+1, vt_b+1, c2_vn)])

    def add_flange(self, p1, p2, r_inner, r_outer, segments=24):
        """Heavy bolted piping/vessel flange ring with hollow bore."""
        p1 = np.array(p1, dtype=float)
        p2 = np.array(p2, dtype=float)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length < 1e-9:
            return
        z_dir = axis / length

        if abs(z_dir[0]) < 0.8 and abs(z_dir[1]) < 0.8:
            up = np.array([0, 0, 1])
        else:
            up = np.array([0, 1, 0])
        x_dir = np.cross(z_dir, up)
        x_dir /= np.linalg.norm(x_dir)
        y_dir = np.cross(z_dir, x_dir)

        # Outer cylinder
        self.add_cylinder(p1, p2, r_outer, segments=segments, capped=False)
        # Inner cylinder (if hollow)
        if r_inner > 0:
            # Add inner cylinder with inward normals
            ring1_in = []
            ring2_in = []
            normals_in = []
            for i in range(segments + 1):
                theta = 2.0 * math.pi * i / segments
                radial = math.cos(theta) * x_dir + math.sin(theta) * y_dir
                ring1_in.append(p1 + r_inner * radial)
                ring2_in.append(p2 + r_inner * radial)
                normals_in.append(-radial)

            for i in range(segments):
                v_b = len(self.vertices) + 1
                vt_b = len(self.uvs) + 1
                vn_b = len(self.normals) + 1
                self.vertices.extend([ring1_in[i+1], ring1_in[i], ring2_in[i], ring2_in[i+1]])
                self.uvs.extend([(0,0), (1,0), (1,1), (0,1)])
                self.normals.extend([normals_in[i+1], normals_in[i], normals_in[i], normals_in[i+1]])
                self.materials[self.current_material].extend([
                    [(v_b, vt_b, vn_b), (v_b+1, vt_b+1, vn_b+1), (v_b+2, vt_b+2, vn_b+2)],
                    [(v_b, vt_b, vn_b), (v_b+2, vt_b+2, vn_b+2), (v_b+3, vt_b+3, vn_b+3)]
                ])

            # Annular end caps
            for cap_p, cap_n in [(p1, -z_dir), (p2, z_dir)]:
                sign = 1 if cap_n is z_dir else -1
                for i in range(segments):
                    t1 = 2.0 * math.pi * i / segments
                    t2 = 2.0 * math.pi * (i + 1) / segments
                    r_a = math.cos(t1) * x_dir + math.sin(t1) * y_dir
                    r_b = math.cos(t2) * x_dir + math.sin(t2) * y_dir
                    
                    p_out_a = cap_p + r_outer * r_a
                    p_out_b = cap_p + r_outer * r_b
                    p_in_a = cap_p + r_inner * r_a
                    p_in_b = cap_p + r_inner * r_b

                    if sign == 1:
                        self.add_quad(p_in_a, p_in_b, p_out_b, p_out_a, normal=cap_n)
                    else:
                        self.add_quad(p_in_b, p_in_a, p_out_a, p_out_b, normal=cap_n)

    def add_hex_bolt(self, pos, axis, radius, height):
        """Adds a 6-sided hex bolt head with washer."""
        pos = np.array(pos, dtype=float)
        axis = np.array(axis, dtype=float)
        axis /= np.linalg.norm(axis)
        p_top = pos + axis * height
        # Hex cylinder
        self.add_cylinder(pos, p_top, radius, segments=6, capped=True)
        # Circular washer at base
        p_washer = pos + axis * (height * 0.2)
        self.add_cylinder(pos, p_washer, radius * 1.35, segments=12, capped=False)

    def add_pipe_elbow(self, center, r_bend, r_pipe, plane="XY", angle_start=0, angle_end=90, segments_bend=12, segments_pipe=16):
        """Adds a smooth 90-deg or arbitrary toroidal pipe elbow."""
        center = np.array(center, dtype=float)
        rad_start = math.radians(angle_start)
        rad_end = math.radians(angle_end)

        rings = []
        ring_normals = []

        for b in range(segments_bend + 1):
            t_bend = rad_start + (rad_end - rad_start) * (b / segments_bend)
            if plane == "XY":
                c_bend = center + np.array([r_bend * math.cos(t_bend), r_bend * math.sin(t_bend), 0])
                tan_bend = np.array([-math.sin(t_bend), math.cos(t_bend), 0])
                norm_bend = np.array([math.cos(t_bend), math.sin(t_bend), 0])
                binorm = np.array([0, 0, 1])
            elif plane == "XZ":
                c_bend = center + np.array([r_bend * math.cos(t_bend), 0, r_bend * math.sin(t_bend)])
                tan_bend = np.array([-math.sin(t_bend), 0, math.cos(t_bend)])
                norm_bend = np.array([math.cos(t_bend), 0, math.sin(t_bend)])
                binorm = np.array([0, 1, 0])
            else: # YZ
                c_bend = center + np.array([0, r_bend * math.cos(t_bend), r_bend * math.sin(t_bend)])
                tan_bend = np.array([0, -math.sin(t_bend), math.cos(t_bend)])
                norm_bend = np.array([0, math.cos(t_bend), math.sin(t_bend)])
                binorm = np.array([1, 0, 0])

            ring = []
            norms = []
            for p in range(segments_pipe + 1):
                t_pipe = 2.0 * math.pi * p / segments_pipe
                radial = math.cos(t_pipe) * norm_bend + math.sin(t_pipe) * binorm
                ring.append(c_bend + r_pipe * radial)
                norms.append(radial)
            rings.append(ring)
            ring_normals.append(norms)

        for b in range(segments_bend):
            for p in range(segments_pipe):
                p1 = rings[b][p]
                p2 = rings[b][p+1]
                p3 = rings[b+1][p+1]
                p4 = rings[b+1][p]

                n1 = ring_normals[b][p]
                n2 = ring_normals[b][p+1]
                n3 = ring_normals[b+1][p+1]
                n4 = ring_normals[b+1][p]

                v_b = len(self.vertices) + 1
                vt_b = len(self.uvs) + 1
                vn_b = len(self.normals) + 1

                self.vertices.extend([p1, p2, p3, p4])
                self.uvs.extend([(p/segments_pipe, b/segments_bend),
                                 ((p+1)/segments_pipe, b/segments_bend),
                                 ((p+1)/segments_pipe, (b+1)/segments_bend),
                                 (p/segments_pipe, (b+1)/segments_bend)])
                self.normals.extend([n1, n2, n3, n4])

                self.materials[self.current_material].extend([
                    [(v_b, vt_b, vn_b), (v_b+1, vt_b+1, vn_b+1), (v_b+2, vt_b+2, vn_b+2)],
                    [(v_b, vt_b, vn_b), (v_b+2, vt_b+2, vn_b+2), (v_b+3, vt_b+3, vn_b+3)]
                ])

    def save_obj(self, filepath):
        with open(filepath, "w") as f:
            f.write("# FishGame Satisfactory-Grade Asset\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")
            for mat_name, faces in self.materials.items():
                if not faces:
                    continue
                f.write(f"usemtl {mat_name}\n")
                for face in faces:
                    pts = " ".join([f"{v}/{vt}/{vn}" for v, vt, vn in face])
                    f.write(f"f {pts}\n")
        print(f"Saved {filepath}: {len(self.vertices)} verts, {sum(len(fc) for fc in self.materials.values())} tris, {len(self.materials)} mats")
