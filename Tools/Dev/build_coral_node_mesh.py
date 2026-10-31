import math
import os
import random

class MeshBuilder:
    def __init__(self):
        self.vertices = []
        self.uvs = []
        self.normals = []
        # faces grouped by material name: list of ( (v_idx, vt_idx, vn_idx), ... )
        self.materials = {}
        self.current_material = "Slot_Basalt"
        
        # Default fallback normal & uv
        self.add_uv(0.0, 0.0) # uv index 1
        self.add_normal(0.0, 0.0, 1.0) # normal index 1

    def set_material(self, mat_name):
        self.current_material = mat_name
        if mat_name not in self.materials:
            self.materials[mat_name] = []

    def add_vertex(self, x, y, z):
        self.vertices.append((float(x), float(y), float(z)))
        return len(self.vertices) # 1-based index

    def add_uv(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_normal(self, nx, ny, nz):
        length = math.sqrt(nx*nx + ny*ny + nz*nz)
        if length > 1e-6:
            nx, ny, nz = nx/length, ny/length, nz/length
        else:
            nx, ny, nz = 0.0, 0.0, 1.0
        self.normals.append((float(nx), float(ny), float(nz)))
        return len(self.normals)

    def compute_normal(self, p1, p2, p3):
        ux, uy, uz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
        vx, vy, vz = p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]
        nx = uy*vz - uz*vy
        ny = uz*vx - ux*vz
        nz = ux*vy - uy*vx
        length = math.sqrt(nx*nx + ny*ny + nz*nz)
        if length > 1e-6:
            return (nx/length, ny/length, nz/length)
        return (0.0, 0.0, 1.0)

    def add_tri(self, v1, v2, v3, uv1=1, uv2=1, uv3=1, n1=None, n2=None, n3=None):
        if self.current_material not in self.materials:
            self.materials[self.current_material] = []
        if n1 is None:
            norm = self.compute_normal(self.vertices[v1-1], self.vertices[v2-1], self.vertices[v3-1])
            ni = self.add_normal(*norm)
            n1 = n2 = n3 = ni
        self.materials[self.current_material].append([(v1, uv1, n1), (v2, uv2, n2), (v3, uv3, n3)])

    def add_quad(self, v1, v2, v3, v4, uv1=1, uv2=1, uv3=1, uv4=1, n1=None, n2=None, n3=None, n4=None):
        if n1 is None:
            norm = self.compute_normal(self.vertices[v1-1], self.vertices[v2-1], self.vertices[v3-1])
            ni = self.add_normal(*norm)
            n1 = n2 = n3 = n4 = ni
        self.add_tri(v1, v2, v3, uv1, uv2, uv3, n1, n2, n3)
        self.add_tri(v1, v3, v4, uv1, uv3, uv4, n1, n3, n4)

    def add_polygon(self, v_indices, uv_indices=None, normal=None):
        """Fan triangulation of convex planar polygon"""
        if len(v_indices) < 3:
            return
        if uv_indices is None:
            uv_indices = [1] * len(v_indices)
        if normal is None:
            norm = self.compute_normal(self.vertices[v_indices[0]-1], self.vertices[v_indices[1]-1], self.vertices[v_indices[2]-1])
            ni = self.add_normal(*norm)
            normal = ni
        v0 = v_indices[0]
        uv0 = uv_indices[0]
        for i in range(1, len(v_indices)-1):
            self.add_tri(v0, v_indices[i], v_indices[i+1], uv0, uv_indices[i], uv_indices[i+1], normal, normal, normal)

    def add_cylinder(self, p1, p2, r1, r2, segments=12, capped=True):
        """Creates a cylinder/cone frustum between p1 and p2"""
        # Calculate coordinate frame along axis
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        h = math.sqrt(dx*dx + dy*dy + dz*dz)
        if h < 1e-5:
            return
        ax, ay, az = dx/h, dy/h, dz/h

        # Arbitrary perpendicular vector
        if abs(az) < 0.9:
            px, py, pz = -ay, ax, 0.0
        else:
            px, py, pz = 1.0, 0.0, 0.0
        plen = math.sqrt(px*px + py*py + pz*pz)
        px, py, pz = px/plen, py/plen, pz/plen
        # Second perpendicular
        qx = ay*pz - az*py
        qy = az*px - ax*pz
        qz = ax*py - ay*px

        ring1 = []
        ring2 = []
        for i in range(segments):
            th = 2 * math.pi * i / segments
            cx = math.cos(th)
            sx = math.sin(th)
            
            vx = px*cx + qx*sx
            vy = py*cx + qy*sx
            vz = pz*cx + qz*sx
            
            v1_pos = (p1[0] + vx*r1, p1[1] + vy*r1, p1[2] + vz*r1)
            v2_pos = (p2[0] + vx*r2, p2[1] + vy*r2, p2[2] + vz*r2)
            
            ring1.append(self.add_vertex(*v1_pos))
            ring2.append(self.add_vertex(*v2_pos))

        for i in range(segments):
            next_i = (i + 1) % segments
            self.add_quad(ring1[i], ring1[next_i], ring2[next_i], ring2[i])

        if capped:
            self.add_polygon(ring1[::-1])
            self.add_polygon(ring2)

    def add_hex_bolt(self, center, radius, height, normal=(0, 0, 1)):
        """Creates a hard-surface hexagonal bolt head with beveled chamfer"""
        cx, cy, cz = center
        nx, ny, nz = normal
        # Orientation vectors
        if abs(nz) > 0.9:
            rx, ry, rz = 1, 0, 0
        else:
            rx, ry, rz = 0, 0, 1
        # Cross product to get tangent
        tx = ny*rz - nz*ry
        ty = nz*rx - nx*rz
        tz = nx*ry - ny*rx
        tlen = math.sqrt(tx*tx + ty*ty + tz*tz)
        tx, ty, tz = tx/tlen, ty/tlen, tz/tlen
        # Bitangent
        bx = ny*tz - nz*ty
        by = nz*tx - nx*tz
        bz = nx*ty - ny*tx

        bottom_ring = []
        top_ring = []
        chamfer_ring = []
        for i in range(6):
            th = 2 * math.pi * i / 6
            c, s = math.cos(th), math.sin(th)
            ox = tx*c + bx*s
            oy = ty*c + by*s
            oz = tz*c + bz*s

            bottom_ring.append(self.add_vertex(cx + ox*radius, cy + oy*radius, cz + oz*radius))
            top_ring.append(self.add_vertex(cx + ox*radius + nx*(height*0.75), cy + oy*radius + ny*(height*0.75), cz + oz*radius + nz*(height*0.75)))
            chamfer_ring.append(self.add_vertex(cx + ox*(radius*0.82) + nx*height, cy + oy*(radius*0.82) + ny*height, cz + oz*(radius*0.82) + nz*height))

        for i in range(6):
            next_i = (i + 1) % 6
            self.add_quad(bottom_ring[i], bottom_ring[next_i], top_ring[next_i], top_ring[i])
            self.add_quad(top_ring[i], top_ring[next_i], chamfer_ring[next_i], chamfer_ring[i])
        self.add_polygon(chamfer_ring)

    def add_crystal_spire(self, base_pos, tip_pos, radius_base, radius_shoulder, shoulder_ratio=0.85, facets=6, twist_deg=0.0, bevel=True):
        """
        Creates a faceted prismatic crystal spire with natural twinning angles,
        growth striations, and pointed termination.
        """
        bx, by, bz = base_pos
        tx, ty, tz = tip_pos
        dx = tx - bx
        dy = ty - by
        dz = tz - bz
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        if length < 1e-4:
            return
        ax, ay, az = dx/length, dy/length, dz/length

        # Coordinate axes perpendicular to crystal direction
        if abs(az) < 0.9:
            px, py, pz = -ay, ax, 0.0
        else:
            px, py, pz = 1.0, 0.0, 0.0
        plen = math.sqrt(px*px + py*py + pz*pz)
        px, py, pz = px/plen, py/plen, pz/plen
        qx = ay*pz - az*py
        qy = az*px - ax*pz
        qz = ax*py - ay*px

        # Base, striation levels, shoulder, and apex tip
        # Striation levels simulate natural crystal growth steps
        z_levels = [0.0, 0.35, 0.65, shoulder_ratio]
        r_levels = [
            radius_base,
            radius_base * 0.92,
            radius_base * 0.85,
            radius_shoulder
        ]

        # Slight asymmetry in facet angles for natural prismatic crystal twinning
        base_angles = []
        for i in range(facets):
            # Hexagonal with slight asymmetric face widths
            w_mod = 1.0 + 0.15 * math.sin(i * 1.8)
            base_angles.append(2 * math.pi * i / facets + 0.05 * math.sin(i * 2.5))

        rings = []
        for lvl_idx, (t_rel, r_curr) in enumerate(zip(z_levels, r_levels)):
            ring = []
            cur_twist = math.radians(twist_deg) * t_rel
            cx_lvl = bx + dx * t_rel
            cy_lvl = by + dy * t_rel
            cz_lvl = bz + dz * t_rel

            for i in range(facets):
                th = base_angles[i] + cur_twist
                # Facet radius modulation
                r_facet = r_curr * (1.0 + 0.08 * math.cos(i * 3.0))
                c, s = math.cos(th), math.sin(th)
                vx = px*c + qx*s
                vy = py*c + qy*s
                vz = pz*c + qz*s

                v_idx = self.add_vertex(cx_lvl + vx*r_facet, cy_lvl + vy*r_facet, cz_lvl + vz*r_facet)
                ring.append(v_idx)
            rings.append(ring)

        # Connect cylindrical rings along the shaft
        for lvl in range(len(rings) - 1):
            rA = rings[lvl]
            rB = rings[lvl + 1]
            for i in range(facets):
                next_i = (i + 1) % facets
                self.add_quad(rA[i], rA[next_i], rB[next_i], rB[i])

        # Apex tip vertex
        apex_v = self.add_vertex(tx, ty, tz)
        top_ring = rings[-1]

        # Pyramidal / Rhombohedral termination
        for i in range(facets):
            next_i = (i + 1) % facets
            self.add_tri(top_ring[i], top_ring[next_i], apex_v)

        # Base bottom cap
        self.add_polygon(rings[0][::-1])

    def add_energy_vein_ribbon(self, points, width=2.5):
        """Creates a faceted bioluminescent energy filament along a 3D path"""
        if len(points) < 2:
            return
        prev_ring = None
        for i in range(len(points)):
            p = points[i]
            # Tangent direction
            if i == 0:
                tx = points[1][0] - p[0]
                ty = points[1][1] - p[1]
                tz = points[1][2] - p[2]
            elif i == len(points) - 1:
                tx = p[0] - points[i-1][0]
                ty = p[1] - points[i-1][1]
                tz = p[2] - points[i-1][2]
            else:
                tx = points[i+1][0] - points[i-1][0]
                ty = points[i+1][1] - points[i-1][1]
                tz = points[i+1][2] - points[i-1][2]
            tlen = math.sqrt(tx*tx + ty*ty + tz*tz)
            if tlen < 1e-4:
                continue
            tx, ty, tz = tx/tlen, ty/tlen, tz/tlen
            # Normal
            if abs(tz) > 0.8:
                nx, ny, nz = 1, 0, 0
            else:
                nx, ny, nz = 0, 0, 1
            bx = ty*nz - tz*ny
            by = tz*nx - tx*nz
            bz = tx*ny - ty*nx
            blen = math.sqrt(bx*bx + by*by + bz*bz)
            bx, by, bz = bx/blen, by/blen, bz/blen

            w = width * (1.0 + 0.3 * math.sin(i * 1.5))
            vL = self.add_vertex(p[0] - bx*w, p[1] - by*w, p[2] - bz*w)
            vR = self.add_vertex(p[0] + bx*w, p[1] + by*w, p[2] + bz*w)
            vC = self.add_vertex(p[0] + (tx*0.1 + nz*w*0.5), p[1] + (ty*0.1 + nz*w*0.5), p[2] + w*0.8) # Ridge peak
            curr_ring = (vL, vC, vR)

            if prev_ring:
                self.add_quad(prev_ring[0], curr_ring[0], curr_ring[1], prev_ring[1])
                self.add_quad(prev_ring[1], curr_ring[1], curr_ring[2], prev_ring[2])
            prev_ring = curr_ring

    def write_obj(self, filepath):
        with open(filepath, "w") as f:
            f.write("# SM_CoralOreNode - High-Fidelity Hard-Surface Mesh\n")
            f.write(f"# Vertices: {len(self.vertices)}\n")
            
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.6f} {vt[1]:.6f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.5f} {vn[1]:.5f} {vn[2]:.5f}\n")

            for mat_name, face_list in self.materials.items():
                if not face_list:
                    continue
                f.write(f"\nusemtl {mat_name}\n")
                f.write(f"g {mat_name}\n")
                for face in face_list:
                    f.write("f " + " ".join(f"{v}/{vt}/{vn}" for v, vt, vn in face) + "\n")
        print(f"Exported OBJ: {filepath} with {len(self.vertices)} verts and {sum(len(fl) for fl in self.materials.values())} tris across {len(self.materials)} material slots.")

print("MeshBuilder helper defined.")
