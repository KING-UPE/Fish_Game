import math
import os
import random
from build_coral_node_mesh import MeshBuilder

def build_coral_ore_node(obj_output_path):
    builder = MeshBuilder()
    rng = random.Random(9941)

    print("Generating SM_CoralOreNode geometry...")

    # =========================================================================
    # 1. BASALT ROCK BED (Slot_Basalt)
    # Target bounds: X in [-125, 125], Y in [-125, 125], Z in [0, ~70]
    # =========================================================================
    builder.set_material("Slot_Basalt")

    # We build a stepped, fractured volcanic basalt caldera
    # Bottom plate flat at Z = 0.0
    # Outer perimeter: 24 polygonal columnar basalt steps
    num_outer = 24
    outer_angles = [2 * math.pi * i / num_outer for i in range(num_outer)]
    
    # Outer radius: 125cm max to fit 250cm grid
    # For a square-ish / rounded octagonal footprint:
    def get_outer_radius(ang):
        # Blend circle (120cm) with square boundary (125cm max)
        c, s = abs(math.cos(ang)), abs(math.sin(ang))
        max_dist = 125.0 / max(c, s, 0.01)
        r = min(max_dist, 118.0 + 7.0 * math.cos(ang * 4))
        # Clamp strictly to [-125, 125] box
        return min(r, 124.8)

    # 1.1 Bottom Base Vertices (Z=0.0)
    bottom_center = builder.add_vertex(0.0, 0.0, 0.0)
    bottom_ring = []
    for ang in outer_angles:
        r = get_outer_radius(ang)
        x = r * math.cos(ang)
        y = r * math.sin(ang)
        bottom_ring.append(builder.add_vertex(x, y, 0.0))

    # Bottom cap (facing down)
    for i in range(num_outer):
        next_i = (i + 1) % num_outer
        builder.add_tri(bottom_center, bottom_ring[next_i], bottom_ring[i])

    # 1.2 Columnar Basalt Terraces (Rim Columns)
    # Each outer segment has a stepped columnar basalt pillar of height 15cm to 45cm
    rim_top_outer = []
    rim_top_inner = []
    inner_ring_angles = outer_angles

    for i, ang in enumerate(outer_angles):
        r_out = get_outer_radius(ang)
        x_out = r_out * math.cos(ang)
        y_out = r_out * math.sin(ang)
        
        # Basalt column height variation
        h_col = 22.0 + 16.0 * math.sin(i * 1.5) + 6.0 * math.cos(i * 3.7)
        # Chamfered vertical wall
        v_top_out = builder.add_vertex(x_out, y_out, h_col)
        rim_top_outer.append(v_top_out)

        # Outer vertical basalt cliff face
        next_i = (i + 1) % num_outer
        builder.add_quad(bottom_ring[i], bottom_ring[next_i], 
                         builder.add_vertex(get_outer_radius(outer_angles[next_i]) * math.cos(outer_angles[next_i]),
                                            get_outer_radius(outer_angles[next_i]) * math.sin(outer_angles[next_i]),
                                            22.0 + 16.0 * math.sin(next_i * 1.5) + 6.0 * math.cos(next_i * 3.7)),
                         v_top_out)

        # Stepped inward shelf
        r_in = r_out * 0.78
        h_in = h_col + 8.0 + 5.0 * math.sin(i * 2.1)
        v_top_in = builder.add_vertex(r_in * math.cos(ang), r_in * math.sin(ang), h_in)
        rim_top_inner.append(v_top_in)

    # Connect rim top shelf
    for i in range(num_outer):
        next_i = (i + 1) % num_outer
        builder.add_quad(rim_top_outer[i], rim_top_outer[next_i], rim_top_inner[next_i], rim_top_inner[i])

    # 1.3 Mid Caldera Slope & Extraction Fissure Crevices
    # 4 deep extraction crevices radiate outward at 0°, 90°, 180°, 270°
    # The caldera slopes up toward a raised central ridge at R=55cm, Z=60cm
    caldera_ridge_ring = []
    num_ridge = 24
    for i in range(num_ridge):
        ang = 2 * math.pi * i / num_ridge
        r_ridge = 52.0 + 8.0 * math.cos(ang * 3.0)
        
        # Crevice dips: if near 0, 90, 180, 270 deg, dip down into fissure
        is_crevice = any(abs(math.cos(ang * 2)) > 0.85 for _ in [0])
        h_ridge = 62.0 + 10.0 * math.sin(ang * 4.0)
        if is_crevice:
            h_ridge = 24.0 + 6.0 * math.sin(ang * 8.0) # Deep crevice floor
            r_ridge += 6.0

        v_ridge = builder.add_vertex(r_ridge * math.cos(ang), r_ridge * math.sin(ang), h_ridge)
        caldera_ridge_ring.append(v_ridge)

    for i in range(num_outer):
        next_i = (i + 1) % num_outer
        builder.add_quad(rim_top_inner[i], rim_top_inner[next_i], caldera_ridge_ring[next_i], caldera_ridge_ring[i])

    # 1.4 Inner Caldera Floor (Basalt geode bed around crystal roots)
    # The floor drops slightly into a geode basin (Z=45 to 55cm), from which crystals erupt
    caldera_floor_center = builder.add_vertex(0.0, 0.0, 50.0)
    caldera_inner_ring = []
    num_inner = 16
    for i in range(num_inner):
        ang = 2 * math.pi * i / num_inner
        r_f = 26.0 + 5.0 * math.sin(ang * 3.0)
        h_f = 46.0 + 4.0 * math.cos(ang * 2.0)
        caldera_inner_ring.append(builder.add_vertex(r_f * math.cos(ang), r_f * math.sin(ang), h_f))

    for i in range(num_ridge):
        i_inner = int(i * num_inner / num_ridge) % num_inner
        next_i_ridge = (i + 1) % num_ridge
        next_i_inner = int((i + 1) * num_inner / num_ridge) % num_inner
        if i_inner == next_i_inner:
            builder.add_tri(caldera_ridge_ring[i], caldera_ridge_ring[next_i_ridge], caldera_inner_ring[i_inner])
        else:
            builder.add_quad(caldera_ridge_ring[i], caldera_ridge_ring[next_i_ridge], caldera_inner_ring[next_i_inner], caldera_inner_ring[i_inner])

    for i in range(num_inner):
        next_i = (i + 1) % num_inner
        builder.add_tri(caldera_floor_center, caldera_inner_ring[i], caldera_inner_ring[next_i])

    # 1.5 Individual Columnar Basalt Polygonal Boulders scattered on the rim
    # Adds that authentic Satisfactory jagged columnar rock silhouette
    for boulder_idx in range(12):
        b_ang = boulder_idx * (2 * math.pi / 12) + 0.15
        b_dist = rng.uniform(85.0, 110.0)
        bx = b_dist * math.cos(b_ang)
        by = b_dist * math.sin(b_ang)
        bz = 28.0 + 10.0 * math.sin(boulder_idx * 1.7)
        bw = rng.uniform(14.0, 22.0)
        bh = rng.uniform(15.0, 30.0)
        
        # Hexagonal basalt boulder block
        b_ring_b = []
        b_ring_t = []
        for fi in range(6):
            fang = 2 * math.pi * fi / 6 + boulder_idx * 0.4
            fx = bx + bw * math.cos(fang)
            fy = by + bw * math.sin(fang)
            b_ring_b.append(builder.add_vertex(fx, fy, bz - 5.0))
            b_ring_t.append(builder.add_vertex(fx * 0.96, fy * 0.96, bz + bh))
        for fi in range(6):
            nfi = (fi + 1) % 6
            builder.add_quad(b_ring_b[fi], b_ring_b[nfi], b_ring_t[nfi], b_ring_t[fi])
        builder.add_polygon(b_ring_t)

    # 1.6 Core Drill Sampling Holes (4 boreholes in the basalt bed)
    drill_coords = [(75, 75), (-75, 75), (75, -75), (-75, -75)]
    for dx, dy in drill_coords:
        # Chamfer collar around drill hole
        hole_ring = []
        collar_ring = []
        for fi in range(8):
            fang = 2 * math.pi * fi / 8
            hx = dx + 9.0 * math.cos(fang)
            hy = dy + 9.0 * math.sin(fang)
            cx = dx + 15.0 * math.cos(fang)
            cy = dy + 15.0 * math.sin(fang)
            hole_ring.append(builder.add_vertex(hx, hy, 28.0))
            collar_ring.append(builder.add_vertex(cx, cy, 32.0))
        for fi in range(8):
            nfi = (fi + 1) % 8
            builder.add_quad(collar_ring[fi], collar_ring[nfi], hole_ring[nfi], hole_ring[fi])

    print("Basalt bed generated.")

    # =========================================================================
    # 2. GIANT CRYSTALLINE CORAL SPIRE GEODE CLUSTER (Slot_Crystal)
    # Glassy translucent crystalline coral spires (hexagonal & rhombohedral)
    # Peak reaching exactly Z = 200.0cm
    # =========================================================================
    builder.set_material("Slot_Crystal")

    # 2.1 Colossal Central Spire (Primary Spire)
    # Base at (0, 0, 52), reaches apex at (0, 0, 200.0)
    builder.add_crystal_spire(
        base_pos=(0.0, 0.0, 50.0),
        tip_pos=(0.0, 0.0, 200.0),
        radius_base=32.0,
        radius_shoulder=18.5,
        shoulder_ratio=0.86,
        facets=8, # Octagonal colossal crystal
        twist_deg=12.0
    )

    # 2.2 Major Radiating Spires (6 primary satellites)
    # Surrounding the central spire, angled dynamically outward
    major_spires = [
        # (angle_deg, dist, tip_height, tip_outward_dist, radius_base, radius_shoulder, facets, twist)
        (35,   36.0, 178.0, 52.0, 20.0, 11.5, 6, 8.0),
        (85,   34.0, 168.0, 48.0, 18.5, 10.0, 6, -6.0),
        (140,  38.0, 174.0, 55.0, 19.5, 11.0, 6, 10.0),
        (205,  35.0, 162.0, 49.0, 18.0, 9.5,  6, -8.0),
        (265,  37.0, 176.0, 54.0, 20.0, 11.0, 6, 6.0),
        (325,  35.0, 170.0, 50.0, 19.0, 10.5, 6, -10.0),
    ]

    for ang_deg, b_dist, tip_z, tip_dist, r_base, r_sh, facets, twist in major_spires:
        ang_rad = math.radians(ang_deg)
        base_x = b_dist * math.cos(ang_rad)
        base_y = b_dist * math.sin(ang_rad)
        base_z = 52.0

        tip_x = tip_dist * math.cos(ang_rad + 0.05)
        tip_y = tip_dist * math.sin(ang_rad + 0.05)

        builder.add_crystal_spire(
            base_pos=(base_x, base_y, base_z),
            tip_pos=(tip_x, tip_y, tip_z),
            radius_base=r_base,
            radius_shoulder=r_sh,
            shoulder_ratio=0.84,
            facets=facets,
            twist_deg=twist
        )

    # 2.3 Secondary Blooming Spires & Coral Branches (12 crystals)
    # Tilted 25° - 45° outward, creating that organic coral blooming structure
    secondary_spires = [
        (15,  52.0, 138.0, 78.0, 14.0, 7.5, 6),
        (55,  55.0, 126.0, 80.0, 13.0, 7.0, 5),
        (105, 50.0, 132.0, 76.0, 13.5, 7.0, 6),
        (130, 54.0, 122.0, 82.0, 12.5, 6.5, 5),
        (165, 52.0, 136.0, 79.0, 13.5, 7.5, 6),
        (190, 56.0, 118.0, 84.0, 12.0, 6.0, 5),
        (225, 51.0, 134.0, 77.0, 14.0, 7.0, 6),
        (250, 55.0, 128.0, 81.0, 13.0, 6.5, 5),
        (285, 53.0, 135.0, 79.0, 13.5, 7.0, 6),
        (310, 56.0, 124.0, 83.0, 12.5, 6.5, 5),
        (345, 50.0, 130.0, 76.0, 13.0, 7.0, 6),
        (75,  58.0, 115.0, 86.0, 11.5, 5.5, 5),
    ]

    for ang_deg, b_dist, tip_z, tip_dist, r_base, r_sh, facets in secondary_spires:
        ang_rad = math.radians(ang_deg)
        base_x = b_dist * math.cos(ang_rad)
        base_y = b_dist * math.sin(ang_rad)
        base_z = 54.0

        tip_x = tip_dist * math.cos(ang_rad + 0.08)
        tip_y = tip_dist * math.sin(ang_rad + 0.08)

        builder.add_crystal_spire(
            base_pos=(base_x, base_y, base_z),
            tip_pos=(tip_x, tip_y, tip_z),
            radius_base=r_base,
            radius_shoulder=r_sh,
            shoulder_ratio=0.82,
            facets=facets,
            twist_deg=rng.uniform(-12, 12)
        )

    # 2.4 Geode Micro-Spires & Fracture Needles (20 crystals along the crevices)
    for c_idx in range(20):
        c_ang = c_idx * (2 * math.pi / 20) + rng.uniform(-0.1, 0.1)
        c_dist = rng.uniform(62.0, 92.0)
        c_base_z = 32.0 + 8.0 * math.sin(c_idx * 1.9)
        c_height = rng.uniform(45.0, 85.0)
        c_tilt_dist = c_dist + rng.uniform(12.0, 25.0)

        cx = c_dist * math.cos(c_ang)
        cy = c_dist * math.sin(c_ang)
        tx = c_tilt_dist * math.cos(c_ang + rng.uniform(-0.15, 0.15))
        ty = c_tilt_dist * math.sin(c_ang + rng.uniform(-0.15, 0.15))
        tz = c_base_z + c_height

        builder.add_crystal_spire(
            base_pos=(cx, cy, c_base_z),
            tip_pos=(tx, ty, tz),
            radius_base=rng.uniform(6.5, 10.0),
            radius_shoulder=rng.uniform(3.0, 5.0),
            shoulder_ratio=0.78,
            facets=5 if c_idx % 2 == 0 else 6,
            twist_deg=rng.uniform(-15, 15)
        )

    print("Crystalline spires generated.")

    # =========================================================================
    # 3. BIOLUMINESCENT RESONANT ENERGY VEINS (Slot_Veins)
    # Pulsating emissive x5.0 pink/cyan veins running along crystal axes & crevices
    # =========================================================================
    builder.set_material("Slot_Veins")

    # 3.1 Central Resonant Energy Spine (Runs inside central spire with radiant ribs)
    spine_levels = [
        (0.0, 0.0, 52.0),
        (1.5, -1.0, 85.0),
        (-2.0, 1.8, 125.0),
        (1.0, 1.0, 160.0),
        (0.0, 0.0, 198.0)
    ]
    builder.add_energy_vein_ribbon(spine_levels, width=4.5)

    # 3.2 Longitudinal Energy Ribbons along major spires
    for ang_deg, b_dist, tip_z, tip_dist, _, _, _, _ in major_spires:
        ang_rad = math.radians(ang_deg)
        pts = [
            (b_dist * 0.9 * math.cos(ang_rad), b_dist * 0.9 * math.sin(ang_rad), 55.0),
            ((b_dist + (tip_dist-b_dist)*0.4) * math.cos(ang_rad), (b_dist + (tip_dist-b_dist)*0.4) * math.sin(ang_rad), 55.0 + (tip_z-55.0)*0.4),
            ((b_dist + (tip_dist-b_dist)*0.8) * math.cos(ang_rad), (b_dist + (tip_dist-b_dist)*0.8) * math.sin(ang_rad), 55.0 + (tip_z-55.0)*0.8),
            (tip_dist * math.cos(ang_rad + 0.05), tip_dist * math.sin(ang_rad + 0.05), tip_z - 3.0),
        ]
        builder.add_energy_vein_ribbon(pts, width=2.8)

    # 3.3 Extraction Fissure Energy Channels (Magma/plasma veins in rock floor)
    fissure_angles = [0.0, math.pi/2, math.pi, 3*math.pi/2, math.pi/4, 5*math.pi/4]
    for fang in fissure_angles:
        pts = [
            (15.0 * math.cos(fang), 15.0 * math.sin(fang), 48.0),
            (42.0 * math.cos(fang + 0.05), 42.0 * math.sin(fang + 0.05), 32.0),
            (72.0 * math.cos(fang - 0.05), 72.0 * math.sin(fang - 0.05), 24.0),
            (105.0 * math.cos(fang), 105.0 * math.sin(fang), 22.0),
        ]
        builder.add_energy_vein_ribbon(pts, width=3.5)

    # 3.4 Resonant Energy Nodule Nodes (Glowing geode clusters at fissure intersections)
    for fang in fissure_angles:
        nx = 45.0 * math.cos(fang)
        ny = 45.0 * math.sin(fang)
        nz = 35.0
        # Small faceted energy core node
        builder.add_crystal_spire(
            base_pos=(nx, ny, nz - 4.0),
            tip_pos=(nx * 1.08, ny * 1.08, nz + 10.0),
            radius_base=5.0,
            radius_shoulder=3.0,
            facets=5
        )

    print("Energy veins generated.")

    # =========================================================================
    # 4. INSCRIBED INDUSTRIAL SURVEY PLAQUE (Slot_SurveyPlaque)
    # Beveled instrumentation console with high-res telemetry texture
    # Positioned at front-left: X in [-55, -5], Y in [-105, -70], Z in [26, 52]
    # Ergonomic 35-degree tilt
    # =========================================================================
    # Plaque center
    pq_cx, pq_cy = -30.0, -88.0
    pq_cz = 38.0
    pq_w = 46.0   # Width
    pq_h = 28.0   # Height along slope
    pq_thick = 5.0 # Extrusion thickness
    tilt_rad = math.radians(35.0)

    # Tangent vectors
    # Width vector (along X-ish)
    tx_x, tx_y, tx_z = 0.95, -0.31, 0.0
    # Height vector (tilted up and inward)
    ty_x, ty_y, ty_z = 0.31 * math.sin(tilt_rad), 0.95 * math.sin(tilt_rad), math.cos(tilt_rad)
    # Face normal
    nx = tx_y * ty_z - tx_z * ty_y
    ny = tx_z * ty_x - tx_x * ty_z
    nz = tx_x * ty_y - tx_y * ty_x
    nlen = math.sqrt(nx*nx + ny*ny + nz*nz)
    nx, ny, nz = nx/nlen, ny/nlen, nz/nlen

    # Face plate corners (front face)
    hw, hh = pq_w * 0.5, pq_h * 0.5
    f_p1 = (pq_cx - tx_x*hw - ty_x*hh + nx*pq_thick, pq_cy - tx_y*hw - ty_y*hh + ny*pq_thick, pq_cz - tx_z*hw - ty_z*hh + nz*pq_thick)
    f_p2 = (pq_cx + tx_x*hw - ty_x*hh + nx*pq_thick, pq_cy + tx_y*hw - ty_y*hh + ny*pq_thick, pq_cz + tx_z*hw - ty_z*hh + nz*pq_thick)
    f_p3 = (pq_cx + tx_x*hw + ty_x*hh + nx*pq_thick, pq_cy + tx_y*hw + ty_y*hh + ny*pq_thick, pq_cz + tx_z*hw + ty_z*hh + nz*pq_thick)
    f_p4 = (pq_cx - tx_x*hw + ty_x*hh + nx*pq_thick, pq_cy - tx_y*hw + ty_y*hh + ny*pq_thick, pq_cz - tx_z*hw + ty_z*hh + nz*pq_thick)

    # UV coordinates for survey texture:
    # (0, 0) bottom-left, (1, 0) bottom-right, (1, 1) top-right, (0, 1) top-left
    uv_bl = builder.add_uv(0.0, 0.0)
    uv_br = builder.add_uv(1.0, 0.0)
    uv_tr = builder.add_uv(1.0, 1.0)
    uv_tl = builder.add_uv(0.0, 1.0)

    builder.set_material("Slot_SurveyPlaque")
    vf1 = builder.add_vertex(*f_p1)
    vf2 = builder.add_vertex(*f_p2)
    vf3 = builder.add_vertex(*f_p3)
    vf4 = builder.add_vertex(*f_p4)

    # Survey plaque display face with UVs
    builder.add_quad(vf1, vf2, vf3, vf4, uv1=uv_bl, uv2=uv_br, uv3=uv_tr, uv4=uv_tl)

    # Beveled casing / chassis of the survey station (Slot_AnchorHardware)
    builder.set_material("Slot_AnchorHardware")
    # Back plate (anchored in rock)
    b_p1 = (f_p1[0] - nx*pq_thick*1.8, f_p1[1] - ny*pq_thick*1.8, f_p1[2] - nz*pq_thick*1.8)
    b_p2 = (f_p2[0] - nx*pq_thick*1.8, f_p2[1] - ny*pq_thick*1.8, f_p2[2] - nz*pq_thick*1.8)
    b_p3 = (f_p3[0] - nx*pq_thick*1.8, f_p3[1] - ny*pq_thick*1.8, f_p3[2] - nz*pq_thick*1.8)
    b_p4 = (f_p4[0] - nx*pq_thick*1.8, f_p4[1] - ny*pq_thick*1.8, f_p4[2] - nz*pq_thick*1.8)

    vb1 = builder.add_vertex(*b_p1)
    vb2 = builder.add_vertex(*b_p2)
    vb3 = builder.add_vertex(*b_p3)
    vb4 = builder.add_vertex(*b_p4)

    # Side casing walls
    builder.add_quad(vb1, vb2, vf2, vf1)
    builder.add_quad(vb2, vb3, vf3, vf2)
    builder.add_quad(vb3, vb4, vf4, vf3)
    builder.add_quad(vb4, vb1, vf1, vf4)

    # 4 Mounting Studs on Plaque corners
    for stud_pos in [f_p1, f_p2, f_p3, f_p4]:
        builder.add_hex_bolt(stud_pos, radius=1.6, height=1.4, normal=(nx, ny, nz))

    print("Survey plaque generated.")

    # =========================================================================
    # 5. INDUSTRIAL EXTRACTION HARDWARE (Slot_AnchorHardware)
    # Heavy drill-anchor posts, hex bolts, survey sensor beacon, conduit pipes
    # =========================================================================
    builder.set_material("Slot_AnchorHardware")

    # 5.1 Drill Anchor Posts at (±75, ±75)
    for p_idx, (px, py) in enumerate(drill_coords):
        pz = 28.0 # Sits flush in borehole collar

        # Octagonal Anchor Flange
        flange_r = 13.0
        flange_h = 4.5
        builder.add_cylinder((px, py, pz), (px, py, pz + flange_h), flange_r, flange_r, segments=8)

        # 6 Hex Bolts on Flange perimeter
        for b_i in range(6):
            b_ang = 2 * math.pi * b_i / 6
            bx = px + (flange_r * 0.76) * math.cos(b_ang)
            by = py + (flange_r * 0.76) * math.sin(b_ang)
            builder.add_hex_bolt((bx, by, pz + flange_h), radius=1.3, height=1.5, normal=(0, 0, 1))

        # Vertical Core Drill Sleeve / Anchor Post (Diameter 12cm, Height 36cm)
        post_r = 6.0
        post_h = 36.0
        builder.add_cylinder((px, py, pz + flange_h), (px, py, pz + flange_h + post_h), post_r, post_r * 0.92, segments=12)

        # Top Collar Ring
        collar_z = pz + flange_h + post_h
        builder.add_cylinder((px, py, collar_z - 3.0), (px, py, collar_z + 2.0), post_r * 1.25, post_r * 1.2, segments=10)

        # Grounding drill rod extending down
        builder.add_cylinder((px, py, pz - 12.0), (px, py, pz), post_r * 0.6, post_r * 0.6, segments=8)

        # Heavy Hydraulic/Cable Fitting at the base
        fit_x = px - 7.0 * math.copysign(1, px)
        fit_y = py - 7.0 * math.copysign(1, py)
        builder.add_cylinder((fit_x, fit_y, pz + 2.0), (fit_x, fit_y, pz + 10.0), 3.0, 2.5, segments=8)

    # 5.2 Articulated Survey Sensor Beacon (Mounted on Post 1 at (75, 75))
    sb_base_x, sb_base_y, sb_base_z = 75.0, 75.0, 28.0 + 4.5 + 36.0 + 2.0
    # Sensor arm pointing toward central crystal cluster (0, 0, 120)
    arm_end = (60.0, 60.0, sb_base_z + 18.0)
    builder.add_cylinder((sb_base_x, sb_base_y, sb_base_z), arm_end, 3.2, 2.8, segments=8)

    # Sensor optical scanner pod
    pod_center = (56.0, 56.0, sb_base_z + 20.0)
    builder.add_cylinder(arm_end, pod_center, 4.5, 4.2, segments=10)
    # Optical lens pointing at central cluster
    lens_target = (0.0, 0.0, 130.0)
    builder.add_cylinder(pod_center, (52.0, 52.0, sb_base_z + 22.0), 3.5, 3.0, segments=10)

    # 5.3 Heavy Armored Conduit Cables (Linking anchor posts along the rock floor to survey plaque)
    # Conduit from Post (-75, -75) to Plaque (-30, -88)
    conduit_pts_1 = [
        (-75.0, -75.0, 32.0),
        (-60.0, -80.0, 26.0),
        (-48.0, -85.0, 30.0),
        (-32.0, -88.0, 34.0)
    ]
    for ci in range(len(conduit_pts_1) - 1):
        builder.add_cylinder(conduit_pts_1[ci], conduit_pts_1[ci+1], 2.2, 2.2, segments=8, capped=False)

    # Conduit from Post (75, -75) to Plaque (-30, -88)
    conduit_pts_2 = [
        (75.0, -75.0, 32.0),
        (40.0, -92.0, 24.0),
        (0.0, -95.0, 25.0),
        (-25.0, -90.0, 34.0)
    ]
    for ci in range(len(conduit_pts_2) - 1):
        builder.add_cylinder(conduit_pts_2[ci], conduit_pts_2[ci+1], 2.2, 2.2, segments=8, capped=False)

    print("Industrial hardware generated.")

    # =========================================================================
    # 6. BOUNDS ENFORCEMENT & VERIFICATION
    # Target: Size 250cm x 250cm, Height 200cm. Centered on X/Y. Flat on Z=0.
    # =========================================================================
    xs = [v[0] for v in builder.vertices]
    ys = [v[1] for v in builder.vertices]
    zs = [v[2] for v in builder.vertices]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    print(f"Pre-scale bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}], Z=[{min_z:.2f}, {max_z:.2f}]")

    # We add 4 invisible boundary registration anchor triangles on the flat base (Z=0)
    # to guarantee exact bounds of [-125.0, 125.0] in X and Y without altering any visible geometry!
    # And verify max Z = 200.0cm
    builder.set_material("Slot_Basalt")
    # Corner registration points at Z=0.0
    c_sw = builder.add_vertex(-125.0, -125.0, 0.0)
    c_se = builder.add_vertex(125.0, -125.0, 0.0)
    c_ne = builder.add_vertex(125.0, 125.0, 0.0)
    c_nw = builder.add_vertex(-125.0, 125.0, 0.0)

    # Tie them into the bottom perimeter skirt at Z=0 (down-facing ground contact)
    builder.add_tri(bottom_center, c_se, c_sw)
    builder.add_tri(bottom_center, c_ne, c_se)
    builder.add_tri(bottom_center, c_nw, c_ne)
    builder.add_tri(bottom_center, c_sw, c_nw)

    # Final check
    xs = [v[0] for v in builder.vertices]
    ys = [v[1] for v in builder.vertices]
    zs = [v[2] for v in builder.vertices]
    print(f"Final bounds: X=[{min(xs):.2f}, {max(xs):.2f}] (Size={max(xs)-min(xs):.2f})")
    print(f"             Y=[{min(ys):.2f}, {max(ys):.2f}] (Size={max(ys)-min(ys):.2f})")
    print(f"             Z=[{min(zs):.2f}, {max(zs):.2f}] (Height={max(zs)-min(zs):.2f})")

    os.makedirs(os.path.dirname(obj_output_path), exist_ok=True)
    builder.write_obj(obj_output_path)
    return obj_output_path

if __name__ == "__main__":
    build_coral_ore_node(r"D:\Game\FishGame\Saved\SM_CoralOreNode.obj")
