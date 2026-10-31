import os
import math
from PIL import Image, ImageDraw, ImageFont

TEXTURE_DIR = r"D:\Game\FishGame\Saved\Textures"
os.makedirs(TEXTURE_DIR, exist_ok=True)

def create_wiremill_decal_texture():
    W, H = 2048, 2048
    # Transparent / dark base
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Helper: draw hazard stripe band
    def draw_hazard_stripes(x, y, w, h, angle_deg=45, stripe_w=30):
        # Draw background yellow
        draw.rectangle([x, y, x + w, y + h], fill=(245, 185, 10, 255))
        # Draw black stripes
        stripe_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(stripe_img)
        diag = int(math.hypot(w, h))
        for sx in range(-diag, diag * 2, stripe_w * 2):
            pts = [
                (sx, 0),
                (sx + stripe_w, 0),
                (sx + stripe_w - int(h * math.tan(math.radians(angle_deg))), h),
                (sx - int(h * math.tan(math.radians(angle_deg))), h)
            ]
            sdraw.polygon(pts, fill=(20, 20, 22, 255))
        img.paste(stripe_img, (x, y), stripe_img)
        # Border
        draw.rectangle([x, y, x + w, y + h], outline=(20, 20, 22, 255), width=4)

    # 1. Main Upper Hazard Band (Top edge)
    draw_hazard_stripes(50, 50, 1948, 80, stripe_w=40)

    # 2. Main Machine Nameplate 1: EXTRUDO-WIRE // PRECISION 0.2MM
    # Large brushed aluminum plate with orange/dark border
    bx, by, bw, bh = 60, 170, 920, 320
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(30, 32, 36, 255), outline=(240, 120, 20, 255), width=6)
    draw.rectangle([bx + 10, by + 10, bx + bw - 10, by + bh - 10], outline=(120, 130, 140, 255), width=2)
    # Corner bolts
    for cx in [bx + 20, bx + bw - 20]:
        for cy in [by + 20, by + bh - 20]:
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(180, 185, 190, 255), outline=(40, 45, 50, 255), width=2)

    # Header banner
    draw.rectangle([bx + 12, by + 12, bx + bw - 12, by + 65], fill=(240, 120, 20, 255))
    draw.text((bx + 30, by + 22), "PROJECT BLUE // AUTOMATED EXTRACTION", fill=(10, 10, 12, 255))
    draw.text((bx + bw - 280, by + 22), "SPEC-9941-WM", fill=(10, 10, 12, 255))

    # Main text
    draw.text((bx + 40, by + 90), "EXTRUDO-WIRE", fill=(255, 255, 255, 255))
    draw.text((bx + 40, by + 150), "PRECISION 0.2MM ROTARY DRAWING LINE", fill=(245, 185, 10, 255))
    draw.text((bx + 40, by + 200), "MULTI-STAGE TUNGSTEN-CARBIDE DIES", fill=(190, 200, 210, 255))
    draw.text((bx + 40, by + 240), "PAPER KITE EXPEDITIONS // REG-9941", fill=(140, 150, 160, 255))
    draw.text((bx + 40, by + 275), "SYSTEM ID: PB-WM-PROG-04", fill=(100, 210, 255, 255))

    # 3. Signage 2: CORAL CONDUCTIVITY LINE
    bx, by, bw, bh = 1040, 170, 940, 320
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(25, 28, 32, 255), outline=(0, 200, 240, 255), width=6)
    draw.rectangle([bx + 10, by + 10, bx + bw - 10, by + bh - 10], outline=(80, 100, 120, 255), width=2)
    # Corner bolts
    for cx in [bx + 20, bx + bw - 20]:
        for cy in [by + 20, by + bh - 20]:
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(180, 185, 190, 255), outline=(40, 45, 50, 255), width=2)

    draw.rectangle([bx + 12, by + 12, bx + bw - 12, by + 65], fill=(0, 180, 220, 255))
    draw.text((bx + 30, by + 22), "CORAL CONDUCTIVITY LINE", fill=(10, 10, 12, 255))
    draw.text((bx + bw - 280, by + 22), "CLASS-1 SUPER-COND", fill=(10, 10, 12, 255))

    draw.text((bx + 40, by + 90), "HIGH PURITY CORAL DRAWING", fill=(255, 255, 255, 255))
    draw.text((bx + 40, by + 150), "LASER MICROMETER CALIBRATED", fill=(0, 230, 255, 255))
    draw.text((bx + 40, by + 200), "RHO: 1.68 x 10^-8 OHM-METRE // CONDUCTIVITY 99.8%", fill=(200, 210, 220, 255))
    draw.text((bx + 40, by + 240), "INGOT FEED: CONTINUOUS ROLLER INFEED", fill=(160, 170, 180, 255))
    draw.text((bx + 40, by + 275), "CAUTION: HIGH VOLTAGE / HIGH PRESSURE", fill=(255, 80, 70, 255))

    # 4. Signage 3: HIGH SPEED ROTARY SPOOL
    bx, by, bw, bh = 60, 530, 920, 300
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(32, 28, 26, 255), outline=(245, 185, 10, 255), width=6)
    # Header
    draw.rectangle([bx + 12, by + 12, bx + bw - 12, by + 65], fill=(245, 185, 10, 255))
    draw.text((bx + 30, by + 22), "HIGH SPEED ROTARY SPOOL", fill=(10, 10, 12, 255))
    draw.text((bx + bw - 260, by + 22), "1200 RPM MAX", fill=(10, 10, 12, 255))

    draw.text((bx + 40, by + 85), "SYNCHRONIZED CAPSTAN DRIVE", fill=(255, 255, 255, 255))
    draw.text((bx + 40, by + 135), "AUTOMATIC TRAVERSING LEVEL-WIND", fill=(245, 185, 10, 255))
    draw.text((bx + 40, by + 185), "DANCER TENSION ARM: CLOSED-LOOP FEEDBACK", fill=(200, 210, 220, 255))
    draw.text((bx + 40, by + 225), "KEEP HANDS CLEAR OF ROTATING CAPSTAN", fill=(255, 80, 70, 255))
    draw.text((bx + 40, by + 260), "PROJECT BLUE METALLURGY DIVISION", fill=(120, 200, 140, 255))

    # 5. Signage 4: PROJECT BLUE METALLURGY & CAUTION LABELS
    bx, by, bw, bh = 1040, 530, 940, 300
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(26, 30, 34, 255), outline=(220, 50, 40, 255), width=6)
    draw.rectangle([bx + 12, by + 12, bx + bw - 12, by + 65], fill=(220, 50, 40, 255))
    draw.text((bx + 30, by + 22), "CAUTION: HIGH VOLTAGE / HIGH PRESSURE", fill=(255, 255, 255, 255))
    draw.text((bx + bw - 240, by + 22), "ISO 45001 COMPLIANT", fill=(255, 255, 255, 255))

    draw.text((bx + 40, by + 85), "PROJECT BLUE METALLURGY", fill=(255, 255, 255, 255))
    draw.text((bx + 40, by + 135), "LUBRICANT BATH RECIRCULATION: 45 LITERS", fill=(100, 200, 255, 255))
    draw.text((bx + 40, by + 185), "DIE REDUCTION RATIO: 8:1 PROGRESSIVE", fill=(220, 225, 230, 255))
    draw.text((bx + 40, by + 225), "EMERGENCY STOP INTERLOCK ENGAGED", fill=(255, 200, 50, 255))
    draw.text((bx + 40, by + 260), "PAPER KITE EXPEDITIONS // FOUNDRY UNIT 03", fill=(140, 150, 160, 255))

    # 6. Gauge cluster & Circular dials (X: 60 to 980, Y: 870 to 1250)
    def draw_dial(cx, cy, r, title, val_str, unit, min_a=-135, max_a=135):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 22, 25, 255), outline=(180, 185, 190, 255), width=4)
        draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline=(80, 85, 90, 255), width=2)
        # Ticks
        for deg in range(min_a, max_a + 1, 15):
            rad = math.radians(deg - 90)
            x1 = cx + (r - 12) * math.cos(rad)
            y1 = cy + (r - 12) * math.sin(rad)
            x2 = cx + (r - 24) * math.cos(rad)
            y2 = cy + (r - 24) * math.sin(rad)
            col = (255, 80, 60, 255) if deg > 90 else (220, 220, 220, 255)
            draw.line([(x1, y1), (x2, y2)], fill=col, width=3)
        # Needle (at 25 degrees)
        nrad = math.radians(25 - 90)
        nx = cx + (r - 30) * math.cos(nrad)
        ny = cy + (r - 30) * math.sin(nrad)
        draw.line([(cx, cy), (nx, ny)], fill=(255, 50, 50, 255), width=4)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(220, 220, 220, 255))
        draw.text((cx - 45, cy + 30), title, fill=(180, 190, 200, 255))
        draw.text((cx - 35, cy + 55), f"{val_str} {unit}", fill=(245, 185, 10, 255))

    draw_dial(220, 1050, 130, "DIE PRESSURE", "68.5", "BAR")
    draw_dial(520, 1050, 130, "LINE TENSION", "48.2", "N")
    draw_dial(820, 1050, 130, "LUBE TEMP", "42.0", "°C")

    # 7. Wire Gauge Calibration Ruler (mm & AWG scale)
    rx, ry, rw, rh = 1040, 870, 940, 140
    draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(28, 30, 33, 255), outline=(180, 190, 200, 255), width=4)
    draw.text((rx + 20, ry + 15), "PRECISION WIRE CALIBRATION RULER (METRIC // AWG)", fill=(240, 180, 20, 255))
    # Ruler line
    draw.line([(rx + 30, ry + 65), (rx + rw - 30, ry + 65)], fill=(220, 220, 220, 255), width=3)
    for i in range(30):
        tx = rx + 40 + i * 29
        h_tick = 22 if i % 5 == 0 else 12
        draw.line([(tx, ry + 65), (tx, ry + 65 + h_tick)], fill=(220, 220, 220, 255), width=2 if i % 5 != 0 else 3)
        if i % 5 == 0:
            draw.text((tx - 10, ry + 95), f"{i*0.1:.1f}", fill=(200, 210, 220, 255))

    # 8. Large Laser Micrometer Warning & Beam Indicator
    lx, ly, lw, lh = 1040, 1040, 940, 220
    draw.rectangle([lx, ly, lx + lw, ly + lh], fill=(15, 25, 30, 255), outline=(0, 240, 255, 255), width=5)
    draw.text((lx + 30, ly + 25), "LASER MICROMETER OPTICAL SCANNER HEAD", fill=(0, 240, 255, 255))
    draw.text((lx + 30, ly + 75), "CLASS 3B LASER APERTURE - 488nm CYAN COHERENT", fill=(255, 255, 255, 255))
    draw.text((lx + 30, ly + 120), "RESOLUTION: 0.0001 mm | SAMPLING RATE: 10 kHz", fill=(180, 220, 235, 255))
    draw.text((lx + 30, ly + 165), "DO NOT STARE INTO BEAM // OPTICAL SENSOR SHIELDED", fill=(255, 80, 70, 255))

    # 9. Additional Hazard & Industrial Detail Bands (Bottom area)
    draw_hazard_stripes(60, 1300, 920, 70, stripe_w=35)
    draw_hazard_stripes(1040, 1300, 940, 70, stripe_w=35)

    # Technical schematics and barcodes
    def draw_barcode(bx, by, bw, bh, text_code):
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(255, 255, 255, 255))
        import random
        rng = random.Random(42)
        curr_x = bx + 15
        while curr_x < bx + bw - 20:
            bw_line = rng.choice([2, 4, 6, 8])
            draw.rectangle([curr_x, by + 10, curr_x + bw_line, by + bh - 25], fill=(0, 0, 0, 255))
            curr_x += bw_line + rng.choice([3, 5, 7])
        draw.text((bx + 20, by + bh - 20), text_code, fill=(0, 0, 0, 255))

    draw_barcode(60, 1400, 420, 110, "SN-WM-9941-EXTRUDO")
    draw_barcode(520, 1400, 440, 110, "PROJECT-BLUE-CORAL-04")
    draw_barcode(1040, 1400, 450, 110, "SPEC-DIES-TC-0200")
    draw_barcode(1520, 1400, 450, 110, "CALIBRATION-CERT-OK")

    # Stamped inspection stamp badges
    def draw_stamp(cx, cy, r, text1, text2):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(50, 180, 100, 255), width=4)
        draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline=(50, 180, 100, 255), width=2)
        draw.text((cx - 40, cy - 25), text1, fill=(50, 180, 100, 255))
        draw.text((cx - 35, cy + 5), text2, fill=(50, 180, 100, 255))

    draw_stamp(200, 1620, 90, "FICSIT", "QC-PASS")
    draw_stamp(450, 1620, 90, "PROJECT BLUE", "INSPECTED")
    draw_stamp(700, 1620, 90, "REG-9941", "VERIFIED")

    # Conduit / port markers
    for idx, (px, py, label) in enumerate([
        (1040, 1550, "COOLANT INLET [ISO VG 68]"),
        (1520, 1550, "PNEUMATIC SUPPLY [8.0 BAR]"),
        (1040, 1650, "HYDRAULIC RETURN [HPU-2]"),
        (1520, 1650, "480V 3-PHASE 60Hz 25kVA"),
    ]):
        draw.rectangle([px, py, px + 440, py + 70], fill=(30, 34, 38, 255), outline=(100, 110, 120, 255), width=3)
        draw.ellipse([px + 15, py + 18, px + 45, py + 48], fill=(240, 180, 20, 255))
        draw.text((px + 60, py + 25), label, fill=(240, 245, 250, 255))

    # Bottom border hazard stripes
    draw_hazard_stripes(50, 1920, 1948, 80, stripe_w=40)

    out_path = os.path.join(TEXTURE_DIR, "T_Decal_WireMill.png")
    img.save(out_path, "PNG")
    print(f"Created: {out_path} ({W}x{H})")
    return out_path

def create_terminal_screen_texture():
    W, H = 2048, 2048
    img = Image.new("RGBA", (W, H), (12, 16, 22, 255))
    draw = ImageDraw.Draw(img)

    # Subtle CRT scanline overlay
    for y in range(0, H, 4):
        draw.line([(0, y), (W, y)], fill=(8, 12, 16, 120), width=1)

    # Outer screen border bezel glow
    draw.rectangle([20, 20, W - 20, H - 20], outline=(0, 180, 240, 160), width=6)
    draw.rectangle([35, 35, W - 35, H - 35], outline=(0, 120, 180, 80), width=2)

    # Top Header
    draw.rectangle([40, 40, W - 40, 140], fill=(16, 28, 42, 255), outline=(0, 200, 255, 255), width=3)
    draw.text((70, 60), "PROJECT BLUE // AUTOMATED EXTRACTION OS v5.8", fill=(0, 230, 255, 255))
    draw.text((70, 95), "SYSTEM: WIRE MILL // SERIAL: PB-WM-9941", fill=(180, 200, 220, 255))
    draw.text((W - 480, 65), "ONLINE [ALL STAGES NOMINAL]", fill=(50, 240, 120, 255))
    draw.text((W - 480, 95), "UPTIME: 142:38:19", fill=(140, 160, 180, 255))

    # Left Column: Live Optical Laser Scanner Telemetry
    lx, ly, lw, lh = 60, 160, 920, 600
    draw.rectangle([lx, ly, lx + lw, ly + lh], fill=(14, 20, 30, 255), outline=(0, 180, 240, 255), width=3)
    draw.text((lx + 30, ly + 25), "LASER MICROMETER REAL-TIME OPTICAL PROFILE", fill=(0, 240, 255, 255))

    # Grid background for waveform
    gx, gy, gw, gh = lx + 30, ly + 70, lw - 60, 360
    draw.rectangle([gx, gy, gx + gw, gy + gh], fill=(8, 12, 18, 255), outline=(30, 50, 70, 255), width=2)
    for xi in range(gx, gx + gw, 60):
        draw.line([(xi, gy), (xi, gy + gh)], fill=(18, 30, 45, 255), width=1)
    for yi in range(gy, gy + gh, 45):
        draw.line([(gx, yi), (gx + gw, yi)], fill=(18, 30, 45, 255), width=1)

    # Tolerance limit lines (upper and lower bounds)
    mid_y = gy + gh // 2
    draw.line([(gx, mid_y - 80), (gx + gw, mid_y - 80)], fill=(220, 60, 50, 180), width=2)
    draw.text((gx + gw - 130, mid_y - 105), "+0.005 MAX", fill=(220, 60, 50, 255))
    draw.line([(gx, mid_y + 80), (gx + gw, mid_y + 80)], fill=(220, 60, 50, 180), width=2)
    draw.text((gx + gw - 130, mid_y + 85), "-0.005 MIN", fill=(220, 60, 50, 255))

    # Target line
    draw.line([(gx, mid_y), (gx + gw, mid_y)], fill=(50, 200, 100, 160), width=2)
    draw.text((gx + 15, mid_y - 25), "TARGET: 0.2000 mm", fill=(50, 200, 100, 255))

    # Measured waveform (cyan luminous line)
    pts = []
    for i in range(0, gw, 10):
        val = mid_y + int(math.sin(i * 0.08) * 12 + math.cos(i * 0.19) * 8)
        pts.append((gx + i, val))
    draw.line(pts, fill=(0, 255, 240, 255), width=4)

    # Sub-data readout
    draw.text((lx + 30, ly + 460), "CURRENT DIAMETER: 0.2002 mm [PASS]", fill=(50, 255, 120, 255))
    draw.text((lx + 30, ly + 505), "OVALITY: 0.0003 mm | SURFACE DEFECTS: 0", fill=(200, 220, 240, 255))
    draw.text((lx + 30, ly + 550), "CORAL CONDUCTIVITY: 99.84 % IACS [OPTIMAL]", fill=(245, 185, 10, 255))

    # Right Column: Multi-Stage Drawing Line Status
    rx, ry, rw, rh = 1040, 160, 940, 600
    draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(14, 20, 30, 255), outline=(240, 140, 20, 255), width=3)
    draw.text((rx + 30, ry + 25), "EXTRUDO-WIRE // 4-STAGE REDUCTION CASCADE", fill=(240, 160, 20, 255))

    # 4 Die stages telemetry cards
    stages = [
        ("DIE 1 (ENTRY)", "25.0 -> 16.0 mm", "184°C", "NORMAL", (50, 220, 100)),
        ("DIE 2 (INTER 1)", "16.0 -> 8.0 mm", "142°C", "NORMAL", (50, 220, 100)),
        ("DIE 3 (INTER 2)", "8.0 -> 3.2 mm", "98°C", "NORMAL", (50, 220, 100)),
        ("DIE 4 (FINISH)", "3.2 -> 0.2 mm", "62°C", "CALIBRATED", (0, 240, 255)),
    ]
    for idx, (title, red_str, temp_str, stat, col) in enumerate(stages):
        sy = ry + 80 + idx * 120
        draw.rectangle([rx + 25, sy, rx + rw - 25, sy + 100], fill=(20, 26, 36, 255), outline=(60, 75, 95, 255), width=2)
        draw.text((rx + 45, sy + 15), title, fill=(255, 255, 255, 255))
        draw.text((rx + 45, sy + 55), f"REDUCTION: {red_str}", fill=(180, 200, 220, 255))
        draw.text((rx + 500, sy + 25), f"DIE TEMP: {temp_str}", fill=(245, 185, 10, 255))
        draw.text((rx + 500, sy + 55), f"STATUS: {stat}", fill=(*col, 255))

    # Lower Left: Capstan & Take-Up Spool Motor Dynamics
    bx, by, bw, bh = 60, 800, 920, 600
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(14, 20, 30, 255), outline=(0, 200, 255, 255), width=3)
    draw.text((bx + 30, by + 25), "MOTORIZED TAKE-UP SPOOL & DANCER ARM", fill=(0, 230, 255, 255))

    # Gauges bar graphs
    bars = [
        ("SPOOL ROTATION SPEED", "1040 RPM / 1200 MAX", 0.86, (245, 185, 10)),
        ("DANCER ARM TENSION", "48.5 N / 60.0 N OPTIMAL", 0.80, (50, 240, 120)),
        ("LEVEL-WIND PITCH", "0.22 mm/rev", 0.65, (0, 200, 255)),
        ("SPOOL FILL CAPACITY", "42 % (840 METERS)", 0.42, (160, 180, 240)),
        ("LUBRICANT FLOW RATE", "3.8 L/min [RECIRC ACTIVE]", 0.76, (80, 220, 200)),
    ]
    for idx, (label, val_txt, pct, col) in enumerate(bars):
        byi = by + 80 + idx * 98
        draw.text((bx + 30, byi), label, fill=(220, 230, 240, 255))
        draw.text((bx + bw - 320, byi), val_txt, fill=(*col, 255))
        # Bar track
        draw.rectangle([bx + 30, byi + 35, bx + bw - 30, byi + 65], fill=(10, 15, 22, 255), outline=(50, 65, 80, 255), width=2)
        # Bar fill
        fill_w = int((bw - 64) * pct)
        draw.rectangle([bx + 32, byi + 37, bx + 32 + fill_w, byi + 63], fill=(*col, 255))

    # Lower Right: Machine System Interlocks & Alarms
    ix, iy, iw, ih = 1040, 800, 940, 600
    draw.rectangle([ix, iy, ix + iw, iy + ih], fill=(14, 20, 30, 255), outline=(50, 220, 120, 255), width=3)
    draw.text((ix + 30, iy + 25), "MACHINE INTERLOCKS & SAFETY CONTROLS", fill=(50, 230, 120, 255))

    interlocks = [
        ("EMERGENCY STOP (E-STOP)", "ARMED / READY", (50, 240, 100)),
        ("DIE SAFETY ENCLOSURE", "INTERLOCKED CLOSED", (50, 240, 100)),
        ("COOLANT BATH LEVEL", "OPTIMAL (45 L)", (50, 240, 100)),
        ("HYDRAULIC CLAMP PRESSURE", "145 BAR [LOCKED]", (50, 240, 100)),
        ("OPTICAL SCANNER PURGE AIR", "0.4 MPa [FLOWING]", (50, 240, 100)),
        ("MOTOR STATOR TEMP", "54°C [NOMINAL]", (50, 240, 100)),
        ("WIRE BREAK SENSOR", "CONTINUOUS TENSION", (50, 240, 100)),
    ]
    for idx, (name, val, col) in enumerate(interlocks):
        syi = iy + 80 + idx * 72
        draw.rectangle([ix + 25, syi, ix + iw - 25, syi + 55], fill=(20, 26, 36, 255), outline=(40, 55, 75, 255), width=2)
        draw.ellipse([ix + 45, syi + 15, ix + 70, syi + 40], fill=(*col, 255))
        draw.text((ix + 85, syi + 18), name, fill=(220, 230, 240, 255))
        draw.text((ix + iw - 320, syi + 18), val, fill=(*col, 255))

    # Bottom Area: Command Console & Action Bar
    cy = 1440
    draw.rectangle([60, cy, W - 60, H - 60], fill=(14, 20, 30, 255), outline=(120, 140, 160, 255), width=3)
    draw.text((90, cy + 30), "OPERATOR CONSOLE // INPUT CONTROLS", fill=(245, 185, 10, 255))

    # Button prompts
    buttons = [
        ("[F1] RE-CALIBRATE OPTICS", (0, 180, 240)),
        ("[F2] JOG CAPSTAN 10%", (240, 160, 20)),
        ("[F3] CYCLE LUBE PUMP", (50, 200, 120)),
        ("[F4] PURGE AIR BLAST", (180, 190, 210)),
        ("[E-STOP] SYSTEM SHUTDOWN", (240, 50, 40)),
    ]
    for idx, (btn, col) in enumerate(buttons):
        bx_btn = 90 + idx * 370
        if bx_btn + 340 < W - 60:
            draw.rectangle([bx_btn, cy + 90, bx_btn + 340, cy + 180], fill=(22, 30, 42, 255), outline=(*col, 255), width=3)
            draw.text((bx_btn + 20, cy + 125), btn, fill=(*col, 255))

    # Stamped footer
    draw.text((90, cy + 380), "PAPER KITE EXPEDITIONS // FOUNDRY AUTOMATION SYSTEMS // REG-9941 // WIRE-MILL-TERMINAL", fill=(100, 120, 140, 255))
    draw.text((W - 550, cy + 380), "ALL METALLURGICAL LOGS PERSISTED", fill=(60, 180, 100, 255))

    out_path = os.path.join(TEXTURE_DIR, "T_Screen_Terminal.png")
    img.save(out_path, "PNG")
    print(f"Created: {out_path} ({W}x{H})")
    return out_path

if __name__ == "__main__":
    create_wiremill_decal_texture()
    create_terminal_screen_texture()
