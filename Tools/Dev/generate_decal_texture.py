import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_decal_texture(filepath):
    width = 2048
    height = 2048
    img = Image.new("RGBA", (width, height), (22, 26, 32, 255))
    draw = ImageDraw.Draw(img)

    # Try loading system font or fallback
    def get_font(size, bold=False):
        font_names = [
            "C:\\Windows\\Fonts\\consola.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        ]
        for fn in font_names:
            if os.path.exists(fn):
                try:
                    return ImageFont.truetype(fn, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_title = get_font(52, bold=True)
    font_large = get_font(42, bold=True)
    font_med = get_font(30, bold=True)
    font_body = get_font(24, bold=False)
    font_small = get_font(18, bold=False)
    font_gauge = get_font(28, bold=True)

    # -------------------------------------------------------------
    # 1. Main Data Plate (Top-Left: x: 40..980, y: 40..980)
    # -------------------------------------------------------------
    x0, y0, x1, y1 = 40, 40, 980, 980
    # Background plate with dark slate and border
    draw.rectangle([x0, y0, x1, y1], fill=(16, 20, 26, 255), outline=(70, 85, 105, 255), width=4)
    draw.rectangle([x0+8, y0+8, x1-8, y1-8], outline=(40, 50, 65, 255), width=2)
    # Corner mounting bolts
    for cx, cy in [(x0+24, y0+24), (x1-24, y0+24), (x0+24, y1-24), (x1-24, y1-24)]:
        draw.ellipse([cx-12, cy-12, cx+12, cy+12], fill=(90, 105, 120, 255), outline=(130, 145, 160, 255), width=2)
        draw.ellipse([cx-6, cy-6, cx+6, cy+6], fill=(45, 55, 65, 255))

    # Top header bar (Teal industrial header)
    draw.rectangle([x0+40, y0+30, x1-40, y0+120], fill=(18, 56, 74, 255), outline=(0, 160, 190, 255), width=3)
    draw.text((x0+60, y0+42), "PAPER KITE EXPEDITIONS // REG-9941", fill=(0, 230, 255, 255), font=font_small)
    draw.text((x0+60, y0+68), "PROJECT BLUE HYDRO", fill=(255, 255, 255, 255), font=font_large)

    # Machine title block
    draw.text((x0+50, y0+150), "EQUIPMENT SPECIFICATION DATA", fill=(140, 165, 185, 255), font=font_small)
    draw.line([x0+50, y0+175, x1-50, y0+175], fill=(70, 85, 105, 255), width=2)

    draw.text((x0+50, y0+200), "SUBMERSIBLE TURBINE #03", fill=(255, 215, 60, 255), font=font_title)
    draw.text((x0+50, y0+270), "DESIGNATION: HEAVY MARINE INTAKE VOLUTE", fill=(200, 215, 230, 255), font=font_med)

    specs = [
        ("MODEL NUMBER:", "PK-PUMP-5000-REV4"),
        ("SERIAL NUMBER:", "SN-9941-BRINE-0038A"),
        ("SYSTEM CLASS:", "INDUSTRIAL CONTINUOUS EXTRACTION"),
        ("DISCHARGE FLANGE:", "DN 400 PN 16 HIGH PRESSURE"),
        ("MOTOR SPEC:", "400 kW // 3.3 kV SUBMERSIBLE INDUCTION"),
        ("IMPELLER:", "BRONZE-ALUMINUM 5-VANE DUAL ENCLOSED"),
        ("HOUSING:", "MARINE EPOXY RESIN COATED DUCTILE IRON"),
        ("CORROSION RATING:", "CLASS V IMMERSED SEAWATER"),
    ]
    cur_y = y0 + 340
    for label, val in specs:
        draw.text((x0+50, cur_y), label, fill=(130, 150, 170, 255), font=font_body)
        draw.text((x0+380, cur_y), val, fill=(240, 245, 250, 255), font=font_body)
        cur_y += 42

    # Bottom stamped stamp
    draw.rectangle([x0+50, y1-150, x1-50, y1-40], fill=(24, 30, 38, 255), outline=(0, 140, 170, 255), width=2)
    draw.text((x0+70, y1-135), "FACTORY CERTIFIED // INSPECTION OK // QC-9941", fill=(0, 200, 230, 255), font=font_small)
    draw.text((x0+70, y1-105), "AUTOMATED OCEANIC EXTRACTION INFRASTRUCTURE", fill=(180, 200, 215, 255), font=font_med)
    draw.text((x0+70, y1-68), "FICSIT COMPLIANT INDUSTRIAL GRADE", fill=(255, 170, 40, 255), font=font_small)

    # -------------------------------------------------------------
    # 2. Intake Warning & Flow Spec Plate (Top-Right: x: 1068..2008, y: 40..980)
    # -------------------------------------------------------------
    x0, y0, x1, y1 = 1068, 40, 2008, 980
    draw.rectangle([x0, y0, x1, y1], fill=(18, 20, 24, 255), outline=(80, 90, 100, 255), width=4)

    # Hazard Chevron Stripes at top (y0+10 to y0+60)
    stripe_w = 40
    for sx in range(x0+10, x1-10, stripe_w):
        poly = [
            (sx, y0+10),
            (min(x1-10, sx+25), y0+10),
            (min(x1-10, sx+5), y0+60),
            (max(x0+10, sx-20), y0+60),
        ]
        draw.polygon(poly, fill=(255, 185, 0, 255))
    draw.line([x0+10, y0+60, x1-10, y0+60], fill=(0, 0, 0, 255), width=3)

    # Massive bold stamped rating
    draw.rectangle([x0+40, y0+90, x1-40, y0+260], fill=(12, 14, 18, 255), outline=(255, 185, 0, 255), width=4)
    draw.text((x0+60, y0+105), "INTAKE VOLUMETRIC CAPACITY", fill=(255, 195, 30, 255), font=font_med)
    draw.text((x0+60, y0+148), "BRINE INTAKE // 5000 L/MIN", fill=(255, 255, 255, 255), font=font_title)
    draw.text((x0+60, y0+215), "CONTINUOUS HYDRAULIC DISPLACEMENT", fill=(0, 215, 245, 255), font=font_small)

    # Depth & pressure ratings
    draw.rectangle([x0+40, y0+290, x1-40, y0+450], fill=(20, 28, 38, 255), outline=(0, 160, 220, 255), width=3)
    draw.text((x0+60, y0+305), "OPERATIONAL IMMERSION RATING", fill=(140, 190, 225, 255), font=font_small)
    draw.text((x0+60, y0+338), "MAX DEPTH: 50M", fill=(0, 240, 255, 255), font=font_title)
    draw.text((x0+60, y0+405), "HYDROSTATIC TEST PRESSURE: 25.0 BAR (362 PSI)", fill=(230, 240, 250, 255), font=font_med)

    # Warning section
    draw.rectangle([x0+40, y0+480, x1-40, y0+740], fill=(35, 15, 15, 255), outline=(230, 50, 40, 255), width=3)
    draw.text((x0+60, y0+495), "▲ CAUTION: HIGH VOLTAGE / HIGH PRESSURE ▲", fill=(255, 70, 60, 255), font=font_med)
    draw.line([x0+60, y0+535, x1-60, y0+535], fill=(180, 40, 40, 255), width=2)

    warn_lines = [
        "DO NOT SERVICE WHILE UNDERWATER POWER IS ENERGIZED",
        "HIGH SUCTION VELOCITY AT STRAINER BASKET",
        "KEEP CLEAR OF BELL HOUSING DURING OPERATION",
        "ANTI-FOULING ZINC ANODES MUST BE INSPECTED EVERY 200 HRS",
        "SACRIFICIAL ANODE TYPE: 4x HIGH PURITY ZINC BLOCKS",
        "REPLACE WHEN ANODE CONSUMPTION EXCEEDS 60%",
    ]
    wy = y0 + 550
    for wl in warn_lines:
        draw.text((x0+60, wy), "• " + wl, fill=(245, 215, 215, 255), font=font_body)
        wy += 30

    # Bottom hazard stripe
    for sx in range(x0+10, x1-10, stripe_w):
        poly = [
            (sx, y1-60),
            (min(x1-10, sx+25), y1-60),
            (min(x1-10, sx+5), y1-10),
            (max(x0+10, sx-20), y1-10),
        ]
        draw.polygon(poly, fill=(255, 185, 0, 255))

    # -------------------------------------------------------------
    # 3. Analog Pressure Gauge Dial Face (Bottom-Left: x: 40..980, y: 1068..2008)
    # -------------------------------------------------------------
    x0, y0, x1, y1 = 40, 1068, 980, 2008
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    radius = 420

    # Outer brass / steel gauge rim
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=(220, 222, 225, 255), outline=(70, 75, 80, 255), width=12)
    draw.ellipse([cx-(radius-20), cy-(radius-20), cx+(radius-20), cy+(radius-20)], fill=(245, 245, 240, 255), outline=(150, 155, 160, 255), width=4)

    # Dial face markings (from -220 deg to +40 deg, span 260 deg, corresponding to 0 to 25 BAR)
    # 0 to 25 BAR
    start_angle = 140 # degrees in math (140 deg is lower-left)
    total_span = 260
    max_val = 25

    # Color sectors arcs (draw tick colored bands)
    # Safe zone: 8 to 16 BAR (green)
    # Warning zone: 16 to 20 BAR (amber)
    # Danger zone: 20 to 25 BAR (red)
    r_band = radius - 60
    for v in range(0, max_val * 10 + 1):
        frac = v / (max_val * 10)
        ang_deg = 140 + frac * 260
        ang_rad = math.radians(ang_deg)
        x_pt = cx + r_band * math.cos(ang_rad)
        y_pt = cy + r_band * math.sin(ang_rad)

        color_sec = (40, 40, 40, 255)
        if 80 <= v <= 160:
            color_sec = (40, 180, 80, 255)
        elif 160 < v <= 200:
            color_sec = (240, 170, 20, 255)
        elif v > 200:
            color_sec = (220, 40, 30, 255)

        draw.ellipse([x_pt-3, y_pt-3, x_pt+3, y_pt+3], fill=color_sec)

    # Ticks and numbers
    for b in range(0, max_val + 1):
        frac = b / max_val
        ang_deg = 140 + frac * 260
        ang_rad = math.radians(ang_deg)
        cos_a = math.cos(ang_rad)
        sin_a = math.sin(ang_rad)

        is_major = (b % 5 == 0)
        t_len = 35 if is_major else 18
        p1 = (cx + (radius - 50) * cos_a, cy + (radius - 50) * sin_a)
        p2 = (cx + (radius - 50 - t_len) * cos_a, cy + (radius - 50 - t_len) * sin_a)
        draw.line([p1, p2], fill=(20, 25, 30, 255), width=4 if is_major else 2)

        if is_major:
            tx = cx + (radius - 120) * cos_a - 15
            ty = cy + (radius - 120) * sin_a - 15
            draw.text((tx, ty), str(b), fill=(20, 25, 30, 255), font=font_gauge)

    # Dial branding text
    draw.text((cx-170, cy-140), "PROJECT BLUE HYDRO", fill=(40, 80, 120, 255), font=font_med)
    draw.text((cx-90, cy-95), "PRESSURE", fill=(20, 25, 30, 255), font=font_large)
    draw.text((cx-60, cy-50), "BAR x 10", fill=(100, 105, 110, 255), font=font_body)
    draw.text((cx-120, cy+90), "EN 837-1 MARINE", fill=(120, 125, 130, 255), font=font_small)

    # Needle pointing to 16.0 BAR (operational pressure)
    needle_val = 16.0
    needle_ang = math.radians(140 + (needle_val / max_val) * 260)
    nx_tip = cx + (radius - 80) * math.cos(needle_ang)
    ny_tip = cy + (radius - 80) * math.sin(needle_ang)
    nx_tail = cx - 50 * math.cos(needle_ang)
    ny_tail = cy - 50 * math.sin(needle_ang)
    draw.line([(nx_tail, ny_tail), (nx_tip, ny_tip)], fill=(210, 30, 20, 255), width=6)
    # Center needle cap
    draw.ellipse([cx-25, cy-25, cx+25, cy+25], fill=(40, 45, 50, 255), outline=(180, 185, 190, 255), width=4)
    draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=(200, 180, 50, 255))

    # -------------------------------------------------------------
    # 4. Digital Flow Readout & Pipe Decal (Bottom-Right: x: 1068..2008, y: 1068..2008)
    # -------------------------------------------------------------
    x0, y0, x1, y1 = 1068, 1068, 2008, 2008
    draw.rectangle([x0, y0, x1, y1], fill=(16, 20, 26, 255), outline=(60, 75, 90, 255), width=4)

    # Upper section: Digital Flow Telemetry Screen
    draw.rectangle([x0+30, y0+30, x1-30, y0+420], fill=(8, 16, 12, 255), outline=(0, 220, 120, 255), width=4)
    # Glowing digital screen header
    draw.rectangle([x0+35, y0+35, x1-35, y0+90], fill=(12, 35, 22, 255))
    draw.text((x0+50, y0+45), "SYS MONITOR // HYDRO-TELEMETRY // ONLINE", fill=(0, 255, 140, 255), font=font_med)

    # Big digital readout
    draw.text((x0+50, y0+110), "EXTRACTION FLOW RATE", fill=(100, 200, 140, 255), font=font_body)
    draw.text((x0+50, y0+145), "5,000.00", fill=(0, 255, 150, 255), font=font_title)
    draw.text((x0+330, y0+165), "L / MIN", fill=(80, 220, 130, 255), font=font_large)

    screen_stats = [
        ("IMPELLER RPM:", "3,600 RPM", (0, 255, 150, 255)),
        ("INLET PRESSURE:", "1.02 BAR", (0, 255, 150, 255)),
        ("DISCHARGE HEAD:", "16.4 BAR", (0, 255, 150, 255)),
        ("BEARING TEMP:", "42.1 °C [NORMAL]", (0, 255, 150, 255)),
        ("SALINITY LEVEL:", "35.2 PSU [BRINE]", (0, 220, 255, 255)),
        ("TURBINE STATUS:", "CONTINUOUS LOAD 100%", (0, 255, 150, 255)),
    ]
    sy = y0 + 225
    for lbl, val, col in screen_stats:
        draw.text((x0+50, sy), lbl, fill=(110, 170, 140, 255), font=font_small)
        draw.text((x0+280, sy), val, fill=col, font=font_small)
        sy += 30

    # Lower section: Pipe Stamped Decal Plaque
    draw.rectangle([x0+30, y0+470, x1-30, y1-30], fill=(22, 32, 44, 255), outline=(0, 180, 230, 255), width=4)

    # Pipe hazard stripes at ends
    for px in range(x0+35, x0+120, 20):
        draw.polygon([(px, y0+475), (px+12, y0+475), (px+4, y1-35), (px-8, y1-35)], fill=(255, 180, 0, 255))
    for px in range(x1-120, x1-35, 20):
        draw.polygon([(px, y0+475), (px+12, y0+475), (px+4, y1-35), (px-8, y1-35)], fill=(255, 180, 0, 255))

    draw.text((x0+150, y0+500), "PAPER KITE EXPEDITIONS // RIGGING & FLUIDS", fill=(0, 220, 255, 255), font=font_small)
    draw.text((x0+150, y0+535), "HYDRO-LINE // SCH 80", fill=(255, 255, 255, 255), font=font_title)
    draw.text((x0+150, y0+605), "HIGH PRESSURE SEAWATER CONDUIT", fill=(255, 200, 50, 255), font=font_med)

    pipe_specs = [
        ("SERVICE:", "CONCENTRATED OCEAN BRINE EXTRACTION"),
        ("RATED PRESSURE:", "20.0 BAR (300 PSI) WORKING LOAD"),
        ("MATERIAL:", "TITANIUM-STABILIZED MARINE ALLOY"),
        ("FLOW CAPACITY:", "NOMINAL 5000 L/MIN // VELOCITY 3.2 M/S"),
        ("SPECIFICATION:", "PROJECT BLUE HYDRO HYDRO-STD-9941"),
    ]
    py = y0 + 660
    for plbl, pval in pipe_specs:
        draw.text((x0+150, py), plbl, fill=(130, 170, 200, 255), font=font_body)
        draw.text((x0+380, py), pval, fill=(240, 245, 250, 255), font=font_body)
        py += 38

    # Save image
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, format="PNG")
    print("Texture generated and saved to:", filepath)

if __name__ == "__main__":
    out_file = r"D:\Game\FishGame\Saved\DownloadedAssets\T_SeaPumpDecals.png"
    create_decal_texture(out_file)
