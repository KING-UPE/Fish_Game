import os
import sys
import math

# Add current dir to sys.path
sys.path.append(r"D:\Game\FishGame\Tools\Dev")
from obj_builder import ObjMeshBuilder

def build_sea_pump_body(out_path):
    b = ObjMeshBuilder()

    # Materials
    MAT_BODY = "M_MarineEpoxy"
    MAT_BRASS = "M_BrassBronze"
    MAT_ZINC = "M_ZincDarkMetal"
    MAT_FLOW = "M_FlowIndicator"
    MAT_DECAL = "M_SignageDecals"

    # =========================================================================
    # 1. MARINE SKID BASE FOUNDATION (Z = 0 to 18 cm)
    # Fits within X: [-88, 88], Y: [-88, 88]
    # =========================================================================
    b.set_material(MAT_ZINC)

    # Perimeter heavy marine steel box beams (H-beams / channels)
    # Left and right side rails
    b.add_box(-82, 0, 8, 12, 172, 16)
    b.add_box(82, 0, 8, 12, 172, 16)
    # Front and back cross rails
    b.add_box(0, -80, 8, 152, 12, 16)
    b.add_box(0, 80, 8, 152, 12, 16)
    # Center cross reinforcement beams
    b.add_box(0, 0, 7, 152, 14, 14)
    b.add_box(-15, 0, 7, 14, 150, 14)
    b.add_box(35, 0, 7, 14, 150, 14)

    # 4 Heavy corner mounting footings / bolting pads with beveled gusset plates
    corners = [(-80, -78), (80, -78), (-80, 78), (80, 78)]
    for cx, cy in corners:
        # Footing sole plate
        b.set_material(MAT_ZINC)
        b.add_box(cx, cy, 3, 24, 24, 6)
        # Triangular gusset plates
        b.add_box(cx, cy + (6 if cy < 0 else -6), 11, 4, 12, 10)
        b.add_box(cx + (6 if cx < 0 else -6), cy, 11, 12, 4, 10)
        
        # Heavy anchor studs & nuts (Brass/Bronze marine hardware)
        b.set_material(MAT_BRASS)
        b.add_hex_bolt((cx, cy, 6), (0, 0, 1), 5.5, 7.0)
        b.add_cylinder((cx, cy, 13), (cx, cy, 18), 3.0, segments=8, capped=True)

    # =========================================================================
    # 2. SEAWATER STRAINER INTAKE BELL BASKET & ZINC ANODES (Suction intake)
    # Center at X = -38, Y = -20, Z = 10 to 52 cm
    # =========================================================================
    intake_cx, intake_cy = -38, -25

    # Flared bellmouth intake basket (Cone expanding down into suction mouth)
    b.set_material(MAT_BODY)
    b.add_cone_frustum((intake_cx, intake_cy, 45), (intake_cx, intake_cy, 18), 28, 42, segments=24, capped=False)
    # Bellmouth bottom rim flange
    b.set_material(MAT_ZINC)
    b.add_cylinder((intake_cx, intake_cy, 12), (intake_cx, intake_cy, 18), 44, segments=24, capped=True)
    # Central suction flow cone / diffuser bullet
    b.set_material(MAT_BRASS)
    b.add_cone_frustum((intake_cx, intake_cy, 14), (intake_cx, intake_cy, 36), 18, 2, segments=16, capped=True)

    # Perforated intake basket debris screen (Circumferential slotted screen slats)
    b.set_material(MAT_ZINC)
    num_slats = 16
    for i in range(num_slats):
        ang = 2.0 * math.pi * i / num_slats
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        p1 = (intake_cx + 43.5 * cos_a, intake_cy + 43.5 * sin_a, 17)
        p2 = (intake_cx + 29.0 * cos_a, intake_cy + 29.0 * sin_a, 44)
        b.add_cylinder(p1, p2, 2.2, segments=6, capped=True)

    # 6 Sacrificial Zinc Anodes mounted around the intake bell rim
    # Zinc prevents electrochemical corrosion in ocean brine
    num_anodes = 6
    for i in range(num_anodes):
        ang = 2.0 * math.pi * (i + 0.5) / num_anodes
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        ax = intake_cx + 48.0 * cos_a
        ay = intake_cy + 48.0 * sin_a
        az = 15.0

        # Cast zinc block (distinct rectangular anode ingot)
        b.set_material(MAT_ZINC)
        b.add_box(ax, ay, az, 14, 8, 6)

        # Anode mounting clamp bracket
        b.add_box(ax - 2*cos_a, ay - 2*sin_a, az, 4, 10, 8)

        # Dual bronze clamp retention bolts
        b.set_material(MAT_BRASS)
        bx1 = ax + 4 * (-sin_a)
        by1 = ay + 4 * cos_a
        bx2 = ax - 4 * (-sin_a)
        by2 = ay - 4 * cos_a
        b.add_hex_bolt((bx1, by1, az + 3), (0, 0, 1), 1.8, 3.0)
        b.add_hex_bolt((bx2, by2, az + 3), (0, 0, 1), 1.8, 3.0)

    # Intake Flange connecting basket to volute suction eye
    b.set_material(MAT_ZINC)
    b.add_cylinder((intake_cx, intake_cy, 45), (intake_cx, intake_cy, 53), 32, segments=20, capped=True)
    # Suction flange bolts
    b.set_material(MAT_BRASS)
    for i in range(12):
        ang = 2.0 * math.pi * i / 12
        fx = intake_cx + 29 * math.cos(ang)
        fy = intake_cy + 29 * math.sin(ang)
        b.add_hex_bolt((fx, fy, 53), (0, 0, 1), 2.4, 4.0)

    # =========================================================================
    # 3. CENTRIFUGAL IMPELLER VOLUTE CASING (Z = 45 to 118 cm)
    # Snail volute shell expanding around impeller hub (-18, 0, 76)
    # =========================================================================
    volute_cx, volute_cy, volute_cz = -18, 2, 76

    # Impeller hub / bearing snout protruding forward (+Y)
    b.set_material(MAT_BODY)
    b.add_cylinder((volute_cx, volute_cy, volute_cz), (volute_cx, volute_cy - 48, volute_cz), 22, segments=20, capped=True)
    # Bearing housing stepped collar
    b.set_material(MAT_ZINC)
    b.add_cylinder((volute_cx, volute_cy - 20, volute_cz), (volute_cx, volute_cy - 28, volute_cz), 25, segments=20, capped=True)
    b.add_cylinder((volute_cx, volute_cy - 44, volute_cz), (volute_cx, volute_cy - 50, volute_cz), 24, segments=20, capped=True)

    # Central heavy bronze impeller cap nut and lock ring
    b.set_material(MAT_BRASS)
    b.add_cylinder((volute_cx, volute_cy - 48, volute_cz), (volute_cx, volute_cy - 54, volute_cz), 12, segments=12, capped=True)
    b.add_hex_bolt((volute_cx, volute_cy - 54, volute_cz), (0, -1, 0), 8.0, 6.0)
    # Bronze grease fitting / lubrication port
    b.add_cylinder((volute_cx, volute_cy - 35, volute_cz + 22), (volute_cx, volute_cy - 35, volute_cz + 32), 2.5, segments=8, capped=True)
    b.add_hex_bolt((volute_cx, volute_cy - 35, volute_cz + 32), (0, 0, 1), 3.5, 4.0)

    # Spiral Volute Shell:
    # Modeled as multi-segmented curved toroidal sweep expanding in radius
    # from angle 0 (cutwater, radius ~38) around to angle 2*pi (discharge, radius ~62)
    b.set_material(MAT_BODY)
    volute_segments = 24
    spiral_points = []
    cross_radii = []

    for i in range(volute_segments + 1):
        frac = i / volute_segments
        # Archimedean spiral in X-Z plane
        theta = -math.pi * 0.5 + frac * 2.0 * math.pi
        r_spiral = 34.0 + frac * 22.0  # Center of chamber expands
        tube_r = 16.0 + frac * 8.0     # Tube cross-section expands from 16 to 24

        sx = volute_cx + r_spiral * math.cos(theta)
        sy = volute_cy
        sz = volute_cz + r_spiral * math.sin(theta)
        spiral_points.append((sx, sy, sz))
        cross_radii.append(tube_r)

    # Connect spiral volute segments
    for i in range(volute_segments):
        p_a = spiral_points[i]
        p_b = spiral_points[i+1]
        r_a = cross_radii[i]
        r_b = cross_radii[i+1]
        b.add_cone_frustum(p_a, p_b, r_a, r_b, segments=16, capped=False, smooth=True)

    # Volute Split-Case Perimeter Bolted Flange:
    # A heavy flange running along the outer meridian of the spiral
    b.set_material(MAT_ZINC)
    for i in range(0, volute_segments, 2):
        p1 = spiral_points[i]
        r1 = cross_radii[i]
        # Tangent and radial direction
        theta = -math.pi * 0.5 + (i / volute_segments) * 2.0 * math.pi
        fx = p1[0] + (r1 + 2.5) * math.cos(theta)
        fy = p1[1]
        fz = p1[2] + (r1 + 2.5) * math.sin(theta)

        # Bolting lug pad
        b.set_material(MAT_ZINC)
        b.add_box(fx, fy, fz, 9, 28, 9)

        # Flange bolt & nut (front and rear)
        b.set_material(MAT_BRASS)
        b.add_hex_bolt((fx, fy - 14, fz), (0, -1, 0), 2.5, 4.0)
        b.add_hex_bolt((fx, fy + 14, fz), (0, 1, 0), 2.5, 4.0)

    # Volute lower drain plugs and inspection ports
    b.set_material(MAT_BRASS)
    b.add_hex_bolt((volute_cx, volute_cy, volute_cz - 46), (0, 0, -1), 4.5, 5.0)
    b.add_hex_bolt((volute_cx - 30, volute_cy - 15, volute_cz - 35), (-0.7, -0.3, -0.6), 4.0, 5.0)

    # 4 Heavy structural stiffener ribs welded onto the volute face
    b.set_material(MAT_BODY)
    rib_angles = [0.2, 0.6, 1.1, 1.6]
    for ra in rib_angles:
        ang = ra * math.pi
        rx = volute_cx + 36 * math.cos(ang)
        rz = volute_cz + 36 * math.sin(ang)
        b.add_box(rx, volute_cy - 12, rz, 8, 14, 26)

    # =========================================================================
    # 4. OVERHEAD DISCHARGE MANIFOLD & FLANGED COUPLING (Z = 85 to 160 cm)
    # Rises from the spiral discharge throat at X = -38, Y = 18 to Z = 160 cm
    # =========================================================================
    dis_cx, dis_cy = -38, 20

    # Discharge throat transition from volute to vertical riser
    b.set_material(MAT_BODY)
    b.add_cone_frustum((spiral_points[-1][0], spiral_points[-1][1], spiral_points[-1][2]),
                       (dis_cx, dis_cy, 110), cross_radii[-1], 23, segments=16, capped=False)
    # Vertical discharge pipe column
    b.add_cylinder((dis_cx, dis_cy, 110), (dis_cx, dis_cy, 148), 22, segments=20, capped=False)

    # Top Heavy Discharge Flange (Z = 148 to 160 cm)
    # Flange outer diameter 64 cm (radius 32)
    b.set_material(MAT_ZINC)
    b.add_cylinder((dis_cx, dis_cy, 148), (dis_cx, dis_cy, 160), 32, segments=24, capped=True)
    # Raised Face Sealing Gasket Ring (Z = 159 to 160 cm, radius 25)
    b.set_material(MAT_BODY)
    b.add_cylinder((dis_cx, dis_cy, 158), (dis_cx, dis_cy, 160), 25, segments=24, capped=True)
    # Internal bore hole rim (Z = 159 to 160, radius 18)
    b.set_material(MAT_ZINC)
    b.add_cylinder((dis_cx, dis_cy, 159), (dis_cx, dis_cy, 160.2), 17.5, segments=20, capped=True)

    # 12 Perimeter Discharge Flange Bolts & Nuts
    b.set_material(MAT_BRASS)
    for i in range(12):
        ang = 2.0 * math.pi * i / 12
        bx = dis_cx + 28.5 * math.cos(ang)
        by = dis_cy + 28.5 * math.sin(ang)
        b.add_hex_bolt((bx, by, 160), (0, 0, 1), 2.2, 3.8)
        b.add_cylinder((bx, by, 163.8), (bx, by, 166.5), 1.2, segments=6, capped=True)

    # Discharge Pipe Reinforcement Band / Stiffener Collar
    b.set_material(MAT_ZINC)
    b.add_cylinder((dis_cx, dis_cy, 126), (dis_cx, dis_cy, 134), 24.5, segments=20, capped=True)

    # Heavy Diagonal Structural Support Truss (connecting discharge to motor mount)
    b.set_material(MAT_ZINC)
    b.add_cylinder((dis_cx, dis_cy, 120), (12, 10, 68), 5.0, segments=10, capped=True)
    b.add_cylinder((dis_cx, dis_cy, 142), (18, 12, 100), 4.5, segments=10, capped=True)

    # =========================================================================
    # 5. GLOWING GREEN OPERATIONAL FLOW INDICATOR (Z = 120 to 142 cm)
    # Mounted on the discharge manifold facing front/flank
    # =========================================================================
    flow_cx = dis_cx - 18
    flow_cy = dis_cy - 12
    flow_cz = 130

    # Flow sight-glass cell housing (Heavy brass / bronze cylinder)
    b.set_material(MAT_BRASS)
    b.add_cylinder((dis_cx - 14, dis_cy - 9, flow_cz), (flow_cx, flow_cy, flow_cz), 11, segments=16, capped=True)
    # Beveled retaining bezel rings
    b.add_cylinder((flow_cx - 2, flow_cy - 2, flow_cz - 12), (flow_cx - 2, flow_cy - 2, flow_cz + 12), 11.5, segments=16, capped=True)

    # Inner Glowing Flow Core (PBR Glowing Green Neon Material)
    b.set_material(MAT_FLOW)
    # Bright glowing cylinder window!
    p_window1 = (flow_cx, flow_cy, flow_cz - 8)
    p_window2 = (flow_cx, flow_cy, flow_cz + 8)
    b.add_cylinder(p_window1, p_window2, 8.5, segments=16, capped=True)

    # Front viewing window plate (Glowing emissive face)
    b.add_quad(
        (flow_cx - 8, flow_cy - 7, flow_cz - 7),
        (flow_cx + 5, flow_cy - 12, flow_cz - 7),
        (flow_cx + 5, flow_cy - 12, flow_cz + 7),
        (flow_cx - 8, flow_cy - 7, flow_cz + 7),
        uv0=(0, 0), uv1=(1, 0), uv2=(1, 1), uv3=(0, 1)
    )

    # =========================================================================
    # 6. ANALOG PRESSURE GAUGE ASSEMBLY (Z = 124 to 152 cm)
    # Mounted on discharge manifold at X = -56, Y = 28, Z = 138 cm
    # =========================================================================
    gauge_cx, gauge_cy, gauge_cz = -58, 26, 138

    # Isolation needle valve stem & handle connecting gauge to manifold
    b.set_material(MAT_ZINC)
    b.add_cylinder((dis_cx, dis_cy, gauge_cz), (gauge_cx + 10, gauge_cy, gauge_cz), 2.5, segments=8, capped=True)
    # Stainless valve body block
    b.add_box(gauge_cx + 10, gauge_cy, gauge_cz, 8, 8, 10)
    # Bronze valve cock handle
    b.set_material(MAT_BRASS)
    b.add_cylinder((gauge_cx + 10, gauge_cy, gauge_cz + 5), (gauge_cx + 10, gauge_cy, gauge_cz + 14), 1.8, segments=8, capped=True)
    b.add_box(gauge_cx + 10, gauge_cy, gauge_cz + 14, 4, 18, 3)

    # Gauge cylindrical body (depth 8 cm, radius 13 cm)
    # Facing towards -X (or slightly angled: normal = (-0.95, -0.3, 0))
    b.set_material(MAT_ZINC)
    p_gauge_back = (gauge_cx + 7, gauge_cy + 2, gauge_cz)
    p_gauge_front = (gauge_cx - 2, gauge_cy - 1, gauge_cz)
    b.add_cylinder(p_gauge_back, p_gauge_front, 13.5, segments=24, capped=True)

    # Brass Bezel Ring around front dial rim
    b.set_material(MAT_BRASS)
    b.add_cylinder(p_gauge_front, (gauge_cx - 4, gauge_cy - 1.6, gauge_cz), 14.2, segments=24, capped=True)

    # Recessed Circular Dial Face (Mapped to Quadrant 3: Bottom-Left of T_SeaPumpDecals.png)
    # U: [0.02, 0.48], V: [0.52, 0.98]
    b.set_material(MAT_DECAL)
    dial_norm = (-1.0, 0.0, 0.0)
    dial_r = 12.0
    dial_x = gauge_cx - 4.1
    # Generate circular polygon with UV mapping to quadrant 3
    dial_segs = 24
    uv_cx, uv_cy = 0.25, 0.75
    uv_r = 0.21
    v_center = b.add_vertex(dial_x, gauge_cy, gauge_cz)
    uv_center = b.add_uv(uv_cx, uv_cy)
    n_dial = b.add_normal(*dial_norm)

    dial_ring_v = []
    dial_ring_uv = []
    for i in range(dial_segs):
        ang = 2.0 * math.pi * i / dial_segs
        vy = gauge_cy - dial_r * math.cos(ang)
        vz = gauge_cz + dial_r * math.sin(ang)
        v_idx = b.add_vertex(dial_x, vy, vz)
        # UV coordinate: Note U increases with Y, V increases downwards (-Z)
        u_pt = uv_cx + uv_r * math.cos(ang)
        v_pt = uv_cy - uv_r * math.sin(ang)
        uv_idx = b.add_uv(u_pt, v_pt)
        dial_ring_v.append(v_idx)
        dial_ring_uv.append(uv_idx)

    for i in range(dial_segs):
        next_i = (i + 1) % dial_segs
        b.add_face([v_center, dial_ring_v[next_i], dial_ring_v[i]],
                   [uv_center, dial_ring_uv[next_i], dial_ring_uv[i]],
                   [n_dial, n_dial, n_dial])

    # =========================================================================
    # 7. WATERPROOF ELECTRICAL MOTOR DRIVE BELL & COOLING FINS (Z = 60 to 148 cm)
    # Centered at X = 34, Y = 0
    # =========================================================================
    motor_cx, motor_cy = 34, 0
    motor_z_bot = 62
    motor_z_top = 136
    motor_r = 30.0

    # Motor intermediate drive coupling housing (Z = 60 to 74 cm)
    b.set_material(MAT_ZINC)
    b.add_cylinder((motor_cx, motor_cy, motor_z_bot), (motor_cx, motor_cy, 75), 32, segments=24, capped=True)

    # Main Motor Cylindrical Barrel (Z = 75 to 135 cm)
    b.set_material(MAT_BODY)
    b.add_cylinder((motor_cx, motor_cy, 75), (motor_cx, motor_cy, motor_z_top), motor_r, segments=24, capped=True)

    # 24 Longitudinal Marine Cooling Fins wrapping around the motor barrel
    # Heavy rectangular fins: thickness 1.6 cm, depth 4.8 cm
    b.set_material(MAT_ZINC)
    num_fins = 24
    for i in range(num_fins):
        # Skip fins where junction box sits (angle near +X, i = 0 or 1 or 23)
        if i in [0, 1, 22, 23]:
            continue
        ang = 2.0 * math.pi * i / num_fins
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        fin_mid_r = motor_r + 2.2
        fx = motor_cx + fin_mid_r * cos_a
        fy = motor_cy + fin_mid_r * sin_a
        # Fin plate
        b.add_box(fx, fy, (76 + motor_z_top)/2, 4.4, 1.6, motor_z_top - 76)

    # Top Cast End-Bell Dome (Z = 136 to 146 cm)
    b.set_material(MAT_BODY)
    b.add_cone_frustum((motor_cx, motor_cy, motor_z_top), (motor_cx, motor_cy, 145), motor_r, 22, segments=24, capped=True)
    # End-bell center boss
    b.set_material(MAT_ZINC)
    b.add_cylinder((motor_cx, motor_cy, 144), (motor_cx, motor_cy, 149), 14, segments=16, capped=True)

    # Heavy Forged Marine Lifting Eye Lug (crane hoisting ring)
    # Outer ring radius 8 cm, cross thickness 3 cm
    b.set_material(MAT_ZINC)
    # Eye lug base block
    b.add_box(motor_cx, motor_cy, 151, 10, 6, 6)
    # Loop ring
    b.add_box(motor_cx - 5, motor_cy, 157, 4, 5, 8)
    b.add_box(motor_cx + 5, motor_cy, 157, 4, 5, 8)
    b.add_box(motor_cx, motor_cy, 161, 14, 5, 4)

    # Waterproof Electrical Terminal / Junction Box (Mounted at +X of motor)
    # X = 64 to 78, Y = -16 to 16, Z = 92 to 124 cm
    jbox_cx = motor_cx + motor_r + 8
    b.set_material(MAT_ZINC)
    b.add_box(jbox_cx, 0, 108, 14, 30, 30)
    # Beveled access cover plate
    b.set_material(MAT_BODY)
    b.add_box(jbox_cx + 8, 0, 108, 3, 28, 28)
    # 4 Corner terminal cover screws (Brass)
    b.set_material(MAT_BRASS)
    for sx, sz in [(-11, -11), (11, -11), (-11, 11), (11, 11)]:
        b.add_hex_bolt((jbox_cx + 9.5, sx, 108 + sz), (1, 0, 0), 1.6, 2.5)

    # Underwater Heavy Braided Power Umbilical Conduit:
    # Emerging from bottom cable gland of junction box (jbox_cx, 0, 92),
    # curving gracefully down towards base frame at (jbox_cx - 10, 15, 20)
    b.set_material(MAT_BRASS)
    b.add_cylinder((jbox_cx, 0, 93), (jbox_cx, 0, 86), 4.5, segments=12, capped=True)
    b.add_hex_bolt((jbox_cx, 0, 89), (0, 0, -1), 5.5, 4.0)

    # Curved umbilical segments
    b.set_material(MAT_ZINC)
    conduit_points = [
        (jbox_cx, 0, 86),
        (jbox_cx + 2, 4, 72),
        (jbox_cx, 10, 56),
        (jbox_cx - 6, 18, 40),
        (jbox_cx - 14, 25, 25),
        (jbox_cx - 24, 30, 14),
    ]
    for i in range(len(conduit_points) - 1):
        b.add_cylinder(conduit_points[i], conduit_points[i+1], 3.8, segments=10, capped=True)

    # Conduit bracket clamp on base frame
    b.set_material(MAT_BRASS)
    b.add_box(jbox_cx - 24, 30, 15, 6, 10, 8)

    # =========================================================================
    # 8. STAMPED FACTORY SIGNAGE & DECAL NAMEPLATES
    # Inset plates with high-precision UV mapping to T_SeaPumpDecals.png
    # =========================================================================
    b.set_material(MAT_DECAL)

    # Decal Plate A: Main Data Plate (Mounted on Motor Bell at -Y flank)
    # "PROJECT BLUE HYDRO // SUBMERSIBLE TURBINE #03"
    # UV Quadrant 1: Top-Left -> U: [0.03, 0.47], V: [0.03, 0.47]
    plate1_y = motor_cy - motor_r - 0.6
    plate1_cx = motor_cx
    plate1_cz = 104
    hw, hh = 16.0, 16.0
    # Add thin backing bezel
    b.set_material(MAT_ZINC)
    b.add_box(plate1_cx, plate1_y + 0.3, plate1_cz, hw*2 + 2, 1.2, hh*2 + 2)

    # Decal face
    b.set_material(MAT_DECAL)
    b.add_quad(
        (plate1_cx + hw, plate1_y - 0.4, plate1_cz - hh),
        (plate1_cx - hw, plate1_y - 0.4, plate1_cz - hh),
        (plate1_cx - hw, plate1_y - 0.4, plate1_cz + hh),
        (plate1_cx + hw, plate1_y - 0.4, plate1_cz + hh),
        uv0=(0.47, 0.47), uv1=(0.03, 0.47), uv2=(0.03, 0.03), uv3=(0.47, 0.03),
        normal=(0, -1, 0)
    )

    # Decal Plate B: Intake Warning & Flow Spec Plate (Mounted on Volute / Skid front)
    # "BRINE INTAKE // 5000 L/MIN // MAX DEPTH: 50M // CAUTION HIGH VOLTAGE"
    # UV Quadrant 2: Top-Right -> U: [0.53, 0.97], V: [0.03, 0.47]
    plate2_y = volute_cy - 48.6
    plate2_cx = volute_cx - 28.0
    plate2_cz = 74.0
    hw2, hh2 = 18.0, 16.0
    b.set_material(MAT_ZINC)
    b.add_box(plate2_cx, plate2_y + 0.3, plate2_cz, hw2*2 + 2, 1.2, hh2*2 + 2)

    b.set_material(MAT_DECAL)
    b.add_quad(
        (plate2_cx + hw2, plate2_y - 0.4, plate2_cz - hh2),
        (plate2_cx - hw2, plate2_y - 0.4, plate2_cz - hh2),
        (plate2_cx - hw2, plate2_y - 0.4, plate2_cz + hh2),
        (plate2_cx + hw2, plate2_y - 0.4, plate2_cz + hh2),
        uv0=(0.97, 0.47), uv1=(0.53, 0.47), uv2=(0.53, 0.03), uv3=(0.97, 0.03),
        normal=(0, -1, 0)
    )

    # Decal Plate C: Digital Telemetry Display Screen (Mounted on Junction Box front)
    # "SYS MONITOR // FLOW: 5,000 L/MIN // ONLINE"
    # UV Quadrant 4 (upper part): U: [0.53, 0.97], V: [0.53, 0.72]
    screen_x = jbox_cx + 9.6
    screen_cy = 0.0
    screen_cz = 108.0
    sw, sh = 11.0, 8.0
    b.add_quad(
        (screen_x, screen_cy - sw, screen_cz - sh),
        (screen_x, screen_cy + sw, screen_cz - sh),
        (screen_x, screen_cy + sw, screen_cz + sh),
        (screen_x, screen_cy - sw, screen_cz + sh),
        uv0=(0.53, 0.72), uv1=(0.97, 0.72), uv2=(0.97, 0.53), uv3=(0.53, 0.53),
        normal=(1, 0, 0)
    )

    # Write out OBJ file
    b.write_obj(out_path)


def build_pipe_straight(out_path):
    b = ObjMeshBuilder()

    MAT_BODY = "M_MarineEpoxy"
    MAT_BRASS = "M_BrassBronze"
    MAT_ZINC = "M_ZincDarkMetal"
    MAT_DECAL = "M_SignageDecals"

    # =========================================================================
    # SM_PipeStraight: High-Fidelity Marine Pipe / Riser Segment
    # Footprint: Centered at X=0, Y=0, Height: Z = 0 to 100 cm
    # Pipe diameter: 36 cm (radius 18), Flange diameter: 56 cm (radius 28)
    # =========================================================================

    # 1. Main Pipe Column (Z = 12 to 88 cm)
    b.set_material(MAT_BODY)
    b.add_cylinder((0, 0, 12), (0, 0, 88), 18.0, segments=24, capped=False, smooth=True)

    # Internal bore (Z = 0 to 100 cm)
    b.set_material(MAT_ZINC)
    b.add_cylinder((0, 0, 0), (0, 0, 100), 14.5, segments=20, capped=True, smooth=True)

    # 2. Bottom Heavy Marine Flange (Z = 0 to 13 cm)
    b.set_material(MAT_ZINC)
    b.add_cylinder((0, 0, 0), (0, 0, 12), 28.0, segments=24, capped=True)
    # Flange neck transition taper (Z = 12 to 18 cm)
    b.set_material(MAT_BODY)
    b.add_cone_frustum((0, 0, 12), (0, 0, 18), 28.0, 19.5, segments=24, capped=False)
    # Raised gasket ring on bottom face (Z = 0 to 1.5 cm)
    b.set_material(MAT_BRASS)
    b.add_cylinder((0, 0, -0.5), (0, 0, 1.5), 22.0, segments=24, capped=True)

    # 8 Bottom Flange Bolts & Nuts (Brass/Bronze marine hardware)
    b.set_material(MAT_BRASS)
    for i in range(8):
        ang = 2.0 * math.pi * i / 8
        bx = 24.0 * math.cos(ang)
        by = 24.0 * math.sin(ang)
        b.add_hex_bolt((bx, by, 12), (0, 0, 1), 2.2, 3.5)
        b.add_cylinder((bx, by, 15.5), (bx, by, 17.5), 1.2, segments=6, capped=True)

    # 3. Top Heavy Marine Flange (Z = 88 to 100 cm)
    b.set_material(MAT_ZINC)
    b.add_cylinder((0, 0, 88), (0, 0, 100), 28.0, segments=24, capped=True)
    # Flange neck transition taper (Z = 82 to 88 cm)
    b.set_material(MAT_BODY)
    b.add_cone_frustum((0, 0, 82), (0, 0, 88), 19.5, 28.0, segments=24, capped=False)
    # Raised gasket ring on top face (Z = 98.5 to 100.5 cm)
    b.set_material(MAT_BRASS)
    b.add_cylinder((0, 0, 98.5), (0, 0, 100.5), 22.0, segments=24, capped=True)

    # 8 Top Flange Bolts & Nuts
    b.set_material(MAT_BRASS)
    for i in range(8):
        ang = 2.0 * math.pi * i / 8
        bx = 24.0 * math.cos(ang)
        by = 24.0 * math.sin(ang)
        b.add_hex_bolt((bx, by, 100), (0, 0, 1), 2.2, 3.5)
        b.add_cylinder((bx, by, 103.5), (bx, by, 105.5), 1.2, segments=6, capped=True)

    # 4. Central Stiffener Clamp Collar Band (Z = 45 to 55 cm)
    b.set_material(MAT_ZINC)
    b.add_cylinder((0, 0, 45), (0, 0, 55), 20.8, segments=24, capped=True)
    # Collar clamping ears & retention bolts (at +X and -X)
    b.add_box(22, 0, 50, 4, 12, 10)
    b.add_box(-22, 0, 50, 4, 12, 10)
    b.set_material(MAT_BRASS)
    b.add_hex_bolt((24, 0, 50), (1, 0, 0), 1.8, 3.0)
    b.add_hex_bolt((-24, 0, 50), (-1, 0, 0), 1.8, 3.0)

    # Lifting Trunnion Eye Lug on the collar (+Y side)
    b.set_material(MAT_ZINC)
    b.add_box(0, 22, 50, 8, 4, 8)
    b.add_cylinder((0, 24, 50), (0, 28, 50), 3.5, segments=12, capped=True)

    # 5. Pressure Relief Bypass Valve (Mounted on -Y flank at Z = 50 cm)
    # Flanged branch tee
    b.set_material(MAT_BODY)
    b.add_cylinder((0, -18, 50), (0, -28, 50), 6.5, segments=16, capped=True)
    b.set_material(MAT_ZINC)
    b.add_cylinder((0, -28, 50), (0, -32, 50), 9.0, segments=16, capped=True)
    # Valve body block
    b.add_box(0, -37, 50, 10, 10, 12)
    # Blowoff discharge nozzle pointing down
    b.add_cylinder((0, -37, 44), (0, -37, 36), 3.5, segments=12, capped=True)

    # 4-Spoke Brass Turn Valve Wheel (diameter 18 cm, facing -Y)
    b.set_material(MAT_BRASS)
    # Valve bonnet & stem
    b.add_cylinder((0, -42, 50), (0, -48, 50), 2.2, segments=8, capped=True)
    # Wheel outer rim
    wheel_cy = -48.5
    for i in range(16):
        ang1 = 2.0 * math.pi * i / 16
        ang2 = 2.0 * math.pi * (i + 1) / 16
        p1 = (8.0 * math.cos(ang1), wheel_cy, 50 + 8.0 * math.sin(ang1))
        p2 = (8.0 * math.cos(ang2), wheel_cy, 50 + 8.0 * math.sin(ang2))
        b.add_cylinder(p1, p2, 1.2, segments=6, capped=True)
    # Wheel center hub
    b.add_cylinder((0, wheel_cy - 0.8, 50), (0, wheel_cy + 0.8, 50), 3.0, segments=10, capped=True)
    # 4 Wheel spokes
    for i in range(4):
        ang = 0.5 * math.pi * i
        p_spoke = (7.5 * math.cos(ang), wheel_cy, 50 + 7.5 * math.sin(ang))
        b.add_cylinder((0, wheel_cy, 50), p_spoke, 1.0, segments=6, capped=True)

    # 6. Stamped Pipe Specification Decal Plaque (Mounted on +X pipe wall at Z = 30 to 70 cm)
    # "HYDRO-LINE // SCH 80 // HIGH PRESSURE // BRINE FLOW // 5000 L/MIN"
    # Mapped to Quadrant 4 (lower part): U: [0.53, 0.97], V: [0.74, 0.98]
    plaque_x = 18.2
    plaque_w = 12.0  # Y half width
    plaque_h = 16.0  # Z half height
    b.set_material(MAT_ZINC)
    b.add_box(plaque_x + 0.2, 0, 50, 0.6, plaque_w*2 + 1, plaque_h*2 + 1)

    b.set_material(MAT_DECAL)
    b.add_quad(
        (plaque_x + 0.6, -plaque_w, 50 - plaque_h),
        (plaque_x + 0.6, plaque_w, 50 - plaque_h),
        (plaque_x + 0.6, plaque_w, 50 + plaque_h),
        (plaque_x + 0.6, -plaque_w, 50 + plaque_h),
        uv0=(0.53, 0.98), uv1=(0.97, 0.98), uv2=(0.97, 0.74), uv3=(0.53, 0.74),
        normal=(1, 0, 0)
    )

    b.write_obj(out_path)


if __name__ == "__main__":
    tank_path = r"D:\Game\FishGame\Saved\DownloadedAssets\SM_FluidTank.obj"
    pipe_path = r"D:\Game\FishGame\Saved\DownloadedAssets\SM_PipeStraight.obj"
    build_sea_pump_body(tank_path)
    build_pipe_straight(pipe_path)
    print("OBJ builds complete.")
