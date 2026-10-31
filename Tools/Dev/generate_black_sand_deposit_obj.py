import os
import math
import random
from mesh_builder import MeshBuilder, OBJ_PATH

def build_model():
    mb = MeshBuilder()
    print("Building SM_BlackSandDeposit...")

    # =========================================================================
    # 1. QUARRY PIT TERRAIN & TERRACING (Material: Mat_BlackSand)
    # =========================================================================
    mb.set_material("Mat_BlackSand")

    NUM_RADIAL = 72    # 72 radial slices (every 5 degrees)
    NUM_RINGS = 36     # 36 concentric rings from center to perimeter

    # Bucket scoop cutter parameters
    # 4 distinct scoop passes made by continuous bucket wheel
    scoops = [
        # (center_x, center_y, center_z, radius, depth, angle_start, angle_end)
        (75.0, -25.0, 55.0, 28.0, 20.0),
        (85.0, 0.0, 65.0, 30.0, 22.0),
        (80.0, 28.0, 70.0, 26.0, 18.0),
        (65.0, 50.0, 50.0, 25.0, 16.0),
    ]

    def terrain_height(r, theta, x, y):
        """Calculates elevation Z for a given radial coordinate and Cartesian (x,y)."""
        # Base terrace profile
        if r < 38.0:
            # Pit floor / excavation trough
            base_z = 14.0 + (r / 38.0) * 4.0
        elif r < 46.0:
            # Wall 1: lower step
            t = (r - 38.0) / 8.0
            base_z = 18.0 + t * 18.0  # 18 -> 36
        elif r < 72.0:
            # Bench 1: Lower terrace
            base_z = 36.0 + ((r - 46.0) / 26.0) * 5.0
        elif r < 80.0:
            # Wall 2: mid step
            t = (r - 72.0) / 8.0
            base_z = 41.0 + t * 22.0  # 41 -> 63
        elif r < 104.0:
            # Bench 2: Mid terrace
            base_z = 63.0 + ((r - 80.0) / 24.0) * 7.0
        elif r < 112.0:
            # Wall 3: upper step
            t = (r - 104.0) / 8.0
            base_z = 70.0 + t * 22.0  # 70 -> 92
        elif r < 132.0:
            # Bench 3: Outer rim / upper bench
            base_z = 92.0 + ((r - 112.0) / 20.0) * 3.0
        else:
            # Outer embankment sloping down to Z = 0
            t = (r - 132.0) / 16.0
            base_z = 95.0 * (1.0 - t)

        # Micro-variations / natural mineral sediment dunes
        # Heavy ripple pattern across benches
        ripple1 = math.sin(x * 0.18 + y * 0.08) * 2.5
        ripple2 = math.cos(x * 0.08 - y * 0.22) * 1.8
        ripple = (ripple1 + ripple2) * (0.8 if 45.0 < r < 130.0 else 0.3)
        z = base_z + ripple

        # Apply bucket-wheel scoop cuts along excavation face (azimuth near +X)
        for sc_x, sc_y, sc_z, sc_r, sc_depth in scoops:
            dist_xy = math.hypot(x - sc_x, y - sc_y)
            if dist_xy < sc_r:
                # Radial scoop profile
                cutter_rad = sc_r
                radial_pen = math.sqrt(max(0.0, cutter_rad**2 - dist_xy**2))
                cut_z = sc_z - (cutter_rad - radial_pen) * 0.85
                
                # Bucket teeth striations along the scoop cut
                teeth_angle = math.atan2(y - sc_y, x - sc_x)
                teeth_grooves = math.sin(teeth_angle * 14.0) * 1.5

                target_z = cut_z + teeth_grooves
                if target_z < z:
                    z = max(14.0, target_z)

        return max(0.0, z)

    # Build radial grid vertices
    grid_v = []
    grid_uv = []

    # Center vertex (r = 0)
    center_z = terrain_height(0.0, 0.0, 0.0, 0.0)
    center_v = mb.add_vert(0.0, 0.0, center_z)
    center_uv = mb.add_uv(0.5, 0.5)

    ring_r_values = []
    # Concentric rings distribution: denser near step edges
    for ring_idx in range(NUM_RINGS):
        frac = (ring_idx + 1) / NUM_RINGS
        r = frac * 148.0
        ring_r_values.append(r)

    # Vertices for all rings
    ring_vert_indices = []
    ring_uv_indices = []

    for ring_idx, r in enumerate(ring_r_values):
        current_ring_v = []
        current_ring_uv = []
        for slice_idx in range(NUM_RADIAL):
            theta = 2.0 * math.pi * slice_idx / NUM_RADIAL
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = terrain_height(r, theta, x, y)
            
            # Clamp perimeter ring to exact 0.0 Z
            if ring_idx == NUM_RINGS - 1:
                z = 0.0

            v_idx = mb.add_vert(x, y, z)
            u = 0.5 + (x / 300.0)
            v = 0.5 + (y / 300.0)
            uv_idx = mb.add_uv(u, v)

            current_ring_v.append(v_idx)
            current_ring_uv.append(uv_idx)

        ring_vert_indices.append(current_ring_v)
        ring_uv_indices.append(current_ring_uv)

    # Compute normals and faces for the quarry surface
    # Center fan
    for s in range(NUM_RADIAL):
        s_next = (s + 1) % NUM_RADIAL
        v1 = center_v
        v2 = ring_vert_indices[0][s]
        v3 = ring_vert_indices[0][s_next]

        p1, p2, p3 = mb.verts[v1 - 1], mb.verts[v2 - 1], mb.verts[v3 - 1]
        v21 = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
        v31 = (p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2])
        fnx = v21[1]*v31[2] - v21[2]*v31[1]
        fny = v21[2]*v31[0] - v21[0]*v31[2]
        fnz = v21[0]*v31[1] - v21[1]*v31[0]
        n_idx = mb.add_normal(fnx, fny, fnz)

        uv1 = center_uv
        uv2 = ring_uv_indices[0][s]
        uv3 = ring_uv_indices[0][s_next]
        mb.add_tri(v1, v2, v3, uv1, uv2, uv3, n_idx, n_idx, n_idx)

    # Quads between rings
    for ring_idx in range(NUM_RINGS - 1):
        r_inner = ring_vert_indices[ring_idx]
        r_outer = ring_vert_indices[ring_idx + 1]
        uv_inner = ring_uv_indices[ring_idx]
        uv_outer = ring_uv_indices[ring_idx + 1]

        for s in range(NUM_RADIAL):
            s_next = (s + 1) % NUM_RADIAL
            v_tl = r_inner[s]
            v_tr = r_inner[s_next]
            v_br = r_outer[s_next]
            v_bl = r_outer[s]

            uv_tl = uv_inner[s]
            uv_tr = uv_inner[s_next]
            uv_br = uv_outer[s_next]
            uv_bl = uv_outer[s]

            p_tl = mb.verts[v_tl - 1]
            p_tr = mb.verts[v_tr - 1]
            p_br = mb.verts[v_br - 1]
            v21 = (p_tr[0]-p_tl[0], p_tr[1]-p_tl[1], p_tr[2]-p_tl[2])
            v31 = (p_br[0]-p_tl[0], p_br[1]-p_tl[1], p_br[2]-p_tl[2])
            fnx = v21[1]*v31[2] - v21[2]*v31[1]
            fny = v21[2]*v31[0] - v21[0]*v31[2]
            fnz = v21[0]*v31[1] - v21[1]*v31[0]
            n_idx = mb.add_normal(fnx, fny, fnz)

            mb.add_quad(v_tl, v_tr, v_br, v_bl, uv_tl, uv_tr, uv_br, uv_bl, n_idx, n_idx, n_idx, n_idx)

    # Watertight flat bottom disc at Z = 0
    bot_center_v = mb.add_vert(0.0, 0.0, 0.0)
    bot_center_uv = mb.add_uv(0.5, 0.5)
    bot_norm = mb.add_normal(0.0, 0.0, -1.0)
    outermost_ring = ring_vert_indices[-1]
    outermost_uv = ring_uv_indices[-1]

    for s in range(NUM_RADIAL):
        s_next = (s + 1) % NUM_RADIAL
        v1 = bot_center_v
        v2 = outermost_ring[s_next]
        v3 = outermost_ring[s]
        uv1 = bot_center_uv
        uv2 = outermost_uv[s_next]
        uv3 = outermost_uv[s]
        mb.add_tri(v1, v2, v3, uv1, uv2, uv3, bot_norm, bot_norm, bot_norm)

    print("Terrain & Quarry Pit generated.")

    # =========================================================================
    # 2. MINERAL CRYSTALS (Material: Mat_MagnetiteCrystals)
    # =========================================================================
    mb.set_material("Mat_MagnetiteCrystals")

    # Cluster 1: Massive Hero Outcrop on Upper Terrace Face (X=-75, Y=50)
    # Central massive octahedron
    mb.add_octahedron((-74.0, 48.0, 82.0), (32.0, 32.0, 44.0), rot=(35.0, 22.0, 15.0))
    # Supporting satellite octahedra
    mb.add_octahedron((-88.0, 38.0, 75.0), (20.0, 20.0, 28.0), rot=(15.0, -30.0, 45.0))
    mb.add_octahedron((-62.0, 58.0, 78.0), (22.0, 22.0, 30.0), rot=(-25.0, 40.0, 10.0))
    mb.add_octahedron((-80.0, 64.0, 72.0), (16.0, 16.0, 22.0), rot=(45.0, 10.0, -35.0))
    mb.add_octahedron((-58.0, 38.0, 68.0), (14.0, 14.0, 18.0), rot=(20.0, 55.0, 0.0))
    mb.add_octahedron((-95.0, 52.0, 70.0), (12.0, 12.0, 16.0), rot=(-10.0, -15.0, 60.0))

    # Cluster 2: Freshly Cut Mineral Vein exposed in Bucket Scoop (X=82, Y=-12)
    mb.add_octahedron((84.0, -14.0, 52.0), (22.0, 22.0, 32.0), rot=(60.0, 18.0, -25.0))
    mb.add_octahedron((75.0, -24.0, 46.0), (16.0, 16.0, 24.0), rot=(-40.0, 30.0, 15.0))
    mb.add_octahedron((88.0, -2.0, 58.0), (15.0, 15.0, 20.0), rot=(10.0, -45.0, 35.0))
    mb.add_octahedron((78.0, 5.0, 48.0), (12.0, 12.0, 16.0), rot=(80.0, 0.0, 20.0))

    # Cluster 3: Deep Pit Floor Nuggets (X=-15, Y=-22)
    mb.add_octahedron((-16.0, -24.0, 18.0), (18.0, 18.0, 22.0), rot=(12.0, 15.0, -40.0))
    mb.add_octahedron((-26.0, -15.0, 16.0), (14.0, 14.0, 18.0), rot=(-35.0, -20.0, 10.0))
    mb.add_octahedron((-8.0, -32.0, 17.0), (12.0, 12.0, 15.0), rot=(45.0, 30.0, 0.0))

    # Tabular Ilmenite Plates (thick beveled hexagonal tablets)
    for px, py, pz, sx, sy, sz, ryaw, rpitch in [
        (-70.0, 32.0, 70.0, 18.0, 16.0, 5.0, 30.0, 25.0),
        (-60.0, 68.0, 74.0, 15.0, 14.0, 4.5, -45.0, 15.0),
        (72.0, 20.0, 55.0, 16.0, 15.0, 5.0, 65.0, -20.0)
    ]:
        mb.add_box((px, py, pz), (sx, sy, sz), rot=(ryaw, rpitch, 0.0))

    print("Mineral crystals & ilmenite plates generated.")

    # =========================================================================
    # 3. INDUSTRIAL SURVEY STAKES & HAZARD PYLONS (Material: Mat_IndustrialMetal)
    # =========================================================================
    stake_coords = [
        (-102.0, -102.0),
        ( 102.0, -102.0),
        ( 102.0,  102.0),
        (-102.0,  102.0),
    ]

    stake_top_points = []

    for sx, sy in stake_coords:
        ground_z = terrain_height(math.hypot(sx, sy), math.atan2(sy, sx), sx, sy)
        target_top_z = 118.0

        # Base Footplate (22x22x3 cm)
        mb.set_material("Mat_IndustrialMetal")
        mb.add_box((sx, sy, ground_z + 1.5), (24.0, 24.0, 3.0))

        # 4 Anchor Hex Bolts
        for bx, by in [(-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)]:
            mb.add_hex_bolt((sx + bx, sy + by, ground_z + 3.0), radius=2.2, height=2.5, normal=(0, 0, 1))

        # 4 Welded Bracing Gussets (triangular flanges)
        for gx, gy, sz_x, sz_y in [
            (sx + 7.5, sy, 5.0, 3.0),
            (sx - 7.5, sy, 5.0, 3.0),
            (sx, sy + 7.5, 3.0, 5.0),
            (sx, sy - 7.5, 3.0, 5.0),
        ]:
            mb.add_box((gx, gy, ground_z + 8.0), (sz_x, sz_y, 10.0))

        # Main Heavy Steel H-Beam / Column (8x8 cm) from ground to sleeve
        sleeve_bottom_z = 88.0
        sleeve_top_z = 112.0
        mb.add_box((sx, sy, (ground_z + sleeve_bottom_z)*0.5), (8.0, 8.0, sleeve_bottom_z - ground_z))

        # Top column above sleeve
        mb.add_box((sx, sy, (sleeve_top_z + target_top_z)*0.5), (8.0, 8.0, target_top_z - sleeve_top_z))

        # Hazard Warning Sleeve (Material: Mat_HazardStripe)
        mb.set_material("Mat_HazardStripe")
        mb.add_box((sx, sy, (sleeve_bottom_z + sleeve_top_z)*0.5), (10.5, 10.5, sleeve_top_z - sleeve_bottom_z))

        # Optical Beacon / Warning Sensor (Material: Mat_Emissive & Mat_IndustrialMetal)
        mb.set_material("Mat_IndustrialMetal")
        mb.add_cylinder((sx, sy, target_top_z), (sx, sy, target_top_z + 1.5), r=4.8, segs=12)

        # Emissive Beacon Dome (Z reaches exactly 120.0 cm!)
        mb.set_material("Mat_Emissive")
        mb.add_cylinder((sx, sy, target_top_z + 1.5), (sx, sy, 120.0), r=3.6, segs=12, cap_top=True)

        # Inner Cable Lug Ring
        mb.set_material("Mat_IndustrialMetal")
        center_dir = (-sx / math.hypot(sx, sy), -sy / math.hypot(sx, sy))
        lug_pos = (sx + center_dir[0]*5.5, sy + center_dir[1]*5.5, sleeve_top_z)
        mb.add_box(lug_pos, (2.5, 2.5, 5.0))
        stake_top_points.append(lug_pos)

    # Perimeter Heavy Sagging Cable connecting the 4 posts
    mb.set_material("Mat_IndustrialMetal")
    for i in range(4):
        p_start = stake_top_points[i]
        p_end = stake_top_points[(i + 1) % 4]
        # Multi-segment catenary curve
        cable_segs = 14
        prev_p = p_start
        for step in range(1, cable_segs + 1):
            t = step / cable_segs
            cx = p_start[0] + (p_end[0] - p_start[0]) * t
            cy = p_start[1] + (p_end[1] - p_start[1]) * t
            # Natural parabolic sag
            sag = math.sin(t * math.pi) * 14.0
            cz = p_start[2] + (p_end[2] - p_start[2]) * t - sag
            curr_p = (cx, cy, cz)
            mb.add_cylinder(prev_p, curr_p, r=0.9, segs=8, cap_top=False, cap_bot=False)
            prev_p = curr_p

    # 3 Slanted Survey Marker Pins with Yellow Flags
    flag_locations = [
        (-124.0, 18.0, 18.0),
        ( 18.0, 124.0, -15.0),
        ( 116.0, -42.0, 22.0)
    ]
    for fx, fy, tilt_yaw in flag_locations:
        ground_z = terrain_height(math.hypot(fx, fy), math.atan2(fy, fx), fx, fy)
        # Steel pin driven at 15 deg tilt
        tilt_rad = math.radians(16.0)
        yaw_rad = math.radians(tilt_yaw)
        pin_len = 65.0
        p_base = (fx, fy, ground_z - 8.0)
        p_tip = (
            fx + math.cos(yaw_rad) * math.sin(tilt_rad) * pin_len,
            fy + math.sin(yaw_rad) * math.sin(tilt_rad) * pin_len,
            ground_z + math.cos(tilt_rad) * pin_len
        )
        mb.set_material("Mat_IndustrialMetal")
        mb.add_cylinder(p_base, p_tip, r=0.8, segs=8)

        # Yellow Triangular Survey Pennant (Flag)
        mb.set_material("Mat_HazardStripe")
        flag_tip = p_tip
        flag_mid = (
            p_tip[0] - math.cos(tilt_rad)*math.cos(yaw_rad)*22.0,
            p_tip[1] - math.cos(tilt_rad)*math.sin(yaw_rad)*22.0,
            p_tip[2] - math.cos(tilt_rad)*18.0
        )
        flag_end = (
            p_tip[0] + math.sin(yaw_rad)*24.0,
            p_tip[1] - math.cos(yaw_rad)*24.0,
            p_tip[2] - 8.0
        )
        # Add two-sided triangular flag
        n_flag = mb.add_normal(math.sin(yaw_rad), -math.cos(yaw_rad), 0.2)
        uv_f1 = mb.add_uv(0.0, 1.0)
        uv_f2 = mb.add_uv(0.0, 0.0)
        uv_f3 = mb.add_uv(1.0, 0.5)
        v_f1 = mb.add_vert(*flag_tip)
        v_f2 = mb.add_vert(*flag_mid)
        v_f3 = mb.add_vert(*flag_end)
        mb.add_tri(v_f1, v_f2, v_f3, uv_f1, uv_f2, uv_f3, n_flag, n_flag, n_flag)
        mb.add_tri(v_f1, v_f3, v_f2, uv_f1, uv_f3, uv_f2, n_flag, n_flag, n_flag)

    print("Industrial survey stakes, cables, and flags generated.")

    # =========================================================================
    # 4. INDUSTRIAL SURVEY TERMINAL & STAMPED TAG PLAQUE
    # =========================================================================
    # Location: front observation berm at (X=-10.0, Y=-115.0)
    tx, ty = -10.0, -115.0
    tz_ground = terrain_height(math.hypot(tx, ty), math.atan2(ty, tx), tx, ty)

    # Base mounting plate
    mb.set_material("Mat_IndustrialMetal")
    mb.add_box((tx, ty, tz_ground + 2.0), (32.0, 28.0, 4.0))
    for bx, by in [(-11.0, -9.0), (11.0, -9.0), (11.0, 9.0), (-11.0, 9.0)]:
        mb.add_hex_bolt((tx + bx, ty + by, tz_ground + 4.0), radius=2.0, height=2.2, normal=(0, 0, 1))

    # Heavy support stanchion column (12x12 cm tube)
    col_height = 42.0
    mb.add_box((tx, ty, tz_ground + 4.0 + col_height*0.5), (12.0, 12.0, col_height))

    # Instrument Terminal Head (Angled 32 degrees toward player standing at Y = -160)
    head_z = tz_ground + 4.0 + col_height + 16.0
    head_tilt = 32.0  # degrees pitch back
    head_size = (54.0, 12.0, 42.0)

    # Terminal casing body
    mb.add_box((tx, ty, head_z), head_size, rot=(0.0, head_tilt, 0.0))

    # Rear heatsink cooling fins
    for fin_offset in [-16.0, -8.0, 0.0, 8.0, 16.0]:
        mb.add_box((tx + fin_offset, ty + 7.5, head_z), (2.5, 5.0, 36.0), rot=(0.0, head_tilt, 0.0))

    # Conduit connector gland at base of head
    mb.add_cylinder((tx, ty, head_z - 16.0), (tx, ty, tz_ground + 25.0), r=3.2, segs=10)

    # =========================================================================
    # 5. STAMPED SURVEY PLAQUE FACE (Material: Mat_SurveyTag)
    # Dedicated planar UV rectangle [0,0] to [1,1] for crystal clear lore readability!
    # =========================================================================
    mb.set_material("Mat_SurveyTag")

    # The plaque is mounted on the front recessed face (-Y of terminal head)
    # Calculate tilted front surface corners
    plaque_w = 46.0 * 0.5
    plaque_h = 34.0 * 0.5
    y_front = -head_size[1]*0.5 - 0.4  # slight forward protrusion

    # Rotation matrix for head_tilt (Pitch around X axis)
    pitch_rad = math.radians(head_tilt)
    cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)

    def rot_head(lx, ly, lz):
        # Rotate around X by head_tilt
        ry = ly*cp - lz*sp
        rz = ly*sp + lz*cp
        return (tx + lx, ty + ry, head_z + rz)

    # 4 corners of front plaque
    c_tl = rot_head(-plaque_w, y_front,  plaque_h)
    c_tr = rot_head( plaque_w, y_front,  plaque_h)
    c_br = rot_head( plaque_w, y_front, -plaque_h)
    c_bl = rot_head(-plaque_w, y_front, -plaque_h)

    # Plaque normal vector (facing forward-upward)
    p_norm = (0.0, -cp, -sp)
    pn_idx = mb.add_normal(*p_norm)

    # UV coordinates strictly [0, 1]
    uv_tl = mb.add_uv(0.0, 0.0)
    uv_tr = mb.add_uv(1.0, 0.0)
    uv_br = mb.add_uv(1.0, 1.0)
    uv_bl = mb.add_uv(0.0, 1.0)

    v_tl = mb.add_vert(*c_tl)
    v_tr = mb.add_vert(*c_tr)
    v_br = mb.add_vert(*c_br)
    v_bl = mb.add_vert(*c_bl)

    mb.add_quad(v_tl, v_tr, v_br, v_bl, uv_tl, uv_tr, uv_br, uv_bl, pn_idx, pn_idx, pn_idx, pn_idx)

    # 4 corner mounting screws on the plaque
    mb.set_material("Mat_IndustrialMetal")
    for corner_x, corner_z in [
        (-plaque_w + 3.0,  plaque_h - 3.0),
        ( plaque_w - 3.0,  plaque_h - 3.0),
        ( plaque_w - 3.0, -plaque_h + 3.0),
        (-plaque_w + 3.0, -plaque_h + 3.0)
    ]:
        screw_p = rot_head(corner_x, y_front, corner_z)
        mb.add_hex_bolt(screw_p, radius=1.6, height=1.2, normal=p_norm)

    # Top Status Indicator LEDs on terminal top
    mb.set_material("Mat_IndustrialMetal")
    led_left_base = rot_head(-12.0, y_front - 2.0, plaque_h + 3.5)
    led_right_base = rot_head( 12.0, y_front - 2.0, plaque_h + 3.5)
    mb.add_cylinder(led_left_base, rot_head(-12.0, y_front - 3.5, plaque_h + 3.5), r=2.2, segs=8)
    mb.add_cylinder(led_right_base, rot_head( 12.0, y_front - 3.5, plaque_h + 3.5), r=2.2, segs=8)

    # Emissive LED lenses
    mb.set_material("Mat_Emissive")
    mb.add_cylinder(rot_head(-12.0, y_front - 3.5, plaque_h + 3.5), rot_head(-12.0, y_front - 5.0, plaque_h + 3.5), r=1.6, segs=8, cap_top=True)
    mb.add_cylinder(rot_head( 12.0, y_front - 3.5, plaque_h + 3.5), rot_head( 12.0, y_front - 5.0, plaque_h + 3.5), r=1.6, segs=8, cap_top=True)

    print("Industrial Survey Terminal & Plaque generated.")

    # =========================================================================
    # EXPORT OBJ
    # =========================================================================
    mb.export_obj(OBJ_PATH)

    # Verify Bounding Box
    all_x = [v[0] for v in mb.verts]
    all_y = [v[1] for v in mb.verts]
    all_z = [v[2] for v in mb.verts]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    min_z, max_z = min(all_z), max(all_z)

    print(f"=== BOUNDING BOX ===")
    print(f"  X: [{min_x:.2f}, {max_x:.2f}]  -> Size: {max_x - min_x:.2f} cm")
    print(f"  Y: [{min_y:.2f}, {max_y:.2f}]  -> Size: {max_y - min_y:.2f} cm")
    print(f"  Z: [{min_z:.2f}, {max_z:.2f}]  -> Height: {max_z - min_z:.2f} cm")
    print(f"  Center: ({(min_x + max_x)*0.5:.2f}, {(min_y + max_y)*0.5:.2f}, {(min_z + max_z)*0.5:.2f})")

if __name__ == "__main__":
    build_model()
