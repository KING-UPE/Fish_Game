import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"D:\Game\FishGame\Saved\Desalinator"
os.makedirs(OUT_DIR, exist_ok=True)

# Helper for font loading
def get_font(size, bold=False):
    # Try system fonts
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def generate_decals():
    w, h = 2048, 2048
    img = Image.new("RGBA", (w, h), (38, 42, 48, 255))
    draw = ImageDraw.Draw(img)

    # 1. Background industrial metal panel tint with brushed noise
    import random
    random.seed(42)
    pixels = img.load()
    for y in range(0, h, 2):
        shade = random.randint(-4, 4)
        for x in range(w):
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (max(0, min(255, r + shade)), max(0, min(255, g + shade)), max(0, min(255, b + shade)), 255)
            if y + 1 < h:
                pixels[x, y+1] = pixels[x, y]

    f_huge = get_font(56, bold=True)
    f_large = get_font(44, bold=True)
    f_med = get_font(32, bold=True)
    f_small = get_font(24, bold=False)
    f_mono = get_font(26, bold=True)
    f_tiny = get_font(18, bold=False)

    # ----------------------------------------------------
    # Region 1: (0, 0) to (1024, 512) - Main Equipment Placard
    # ----------------------------------------------------
    # Metal placard plate
    draw.rectangle([30, 30, 994, 482], fill=(22, 25, 30, 255), outline=(180, 190, 205, 255), width=6)
    draw.rectangle([44, 44, 980, 468], outline=(100, 115, 130, 255), width=2)
    # Corner rivets
    for rx, ry in [(50, 50), (974, 50), (50, 462), (974, 462)]:
        draw.ellipse([rx-8, ry-8, rx+8, ry+8], fill=(160, 170, 185), outline=(50, 55, 65), width=2)
        draw.line([rx-5, ry, rx+5, ry], fill=(40, 45, 55), width=2)

    # Lore Header banner
    draw.rectangle([46, 46, 978, 120], fill=(245, 166, 35, 255))
    draw.text((70, 56), "PAPER KITE EXPEDITIONS // REG-9941", fill=(15, 18, 22), font=f_large)

    # Sub-banner
    draw.text((70, 140), "PROJECT BLUE // AUTOMATED EXTRACTION", fill=(100, 200, 255), font=f_med)
    draw.text((70, 190), "EQUIPMENT SPECIFICATION: VACUUM FLASH DESALINATOR MK-III", fill=(210, 220, 230), font=f_small)

    # Big stamped callout
    draw.rectangle([65, 240, 960, 350], fill=(30, 36, 45, 255), outline=(0, 229, 255, 255), width=3)
    draw.text((85, 255), "FLASH DESAL // PURITY 99.9%", fill=(0, 229, 255), font=f_huge)
    draw.text((85, 318), "HIGH-THROUGHPUT CONTINUOUS CONDENSATION SYSTEM", fill=(255, 195, 80), font=f_small)

    # Footer data
    draw.text((70, 380), "SERIAL NO: PK-EVAP-9941-DS08 // ASME-VIII CERTIFIED", fill=(170, 185, 200), font=f_mono)
    draw.text((70, 420), "EXPEDITION LIFE SUPPORT // WATER RECLAMATION CORE", fill=(140, 230, 140), font=f_small)

    # ----------------------------------------------------
    # Region 2: (1024, 0) to (2048, 512) - Technical Vacuum & Steam Spec Placard
    # ----------------------------------------------------
    draw.rectangle([1054, 30, 2018, 482], fill=(25, 22, 20, 255), outline=(220, 120, 40, 255), width=6)
    draw.rectangle([1068, 44, 2004, 468], outline=(140, 80, 30, 255), width=2)
    for rx, ry in [(1074, 50), (1998, 50), (1074, 462), (1998, 462)]:
        draw.ellipse([rx-8, ry-8, rx+8, ry+8], fill=(180, 170, 160), outline=(65, 55, 50), width=2)
        draw.line([rx-5, ry, rx+5, ry], fill=(55, 45, 40), width=2)

    # Header Warning Banner
    draw.rectangle([1070, 46, 2002, 120], fill=(215, 60, 40, 255))
    draw.text((1094, 56), "CAUTION: HIGH VOLTAGE / HIGH PRESSURE", fill=(255, 255, 255), font=f_large)

    draw.text((1094, 140), "OPERATING VACUUM: 0.08 BAR", fill=(255, 220, 50), font=f_huge)
    draw.text((1094, 215), "SATURATION EVAPORATION TEMPERATURE: 41.51 °C", fill=(230, 230, 230), font=f_med)
    draw.text((1094, 265), "MAX STEAM PRESSURE: 8.5 BAR // MOTIVE SUPPLY", fill=(255, 140, 60), font=f_small)
    draw.text((1094, 305), "IMPLOSION HAZARD: DO NOT BREACH FLANGES UNDER VACUUM", fill=(255, 90, 80), font=f_small)

    # Warning triangle
    tx, ty = 1880, 350
    draw.polygon([(tx, ty-60), (tx-55, ty+35), (tx+55, ty+35)], fill=(245, 166, 35), outline=(0, 0, 0), width=4)
    draw.text((tx-10, ty-30), "!", fill=(0, 0, 0), font=f_huge)

    draw.text((1094, 370), "EXPEDITION LIFE SUPPORT // RE-CIRCULATION LOOP", fill=(100, 210, 255), font=f_med)
    draw.text((1094, 420), "DESIGN VACUUM: -0.92 BAR GAUGE (0.08 BAR ABS)", fill=(180, 190, 200), font=f_mono)

    # ----------------------------------------------------
    # Region 3: (0, 512) to (1024, 1024) - Dual Output Separation Placard
    # ----------------------------------------------------
    draw.rectangle([30, 542, 994, 994], fill=(18, 28, 38, 255), outline=(0, 180, 240, 255), width=6)
    for rx, ry in [(50, 562), (974, 562), (50, 974), (974, 974)]:
        draw.ellipse([rx-8, ry-8, rx+8, ry+8], fill=(160, 175, 190), outline=(50, 60, 70), width=2)
        draw.line([rx, ry-5, rx, ry+5], fill=(40, 50, 60), width=2)

    draw.rectangle([46, 558, 978, 630], fill=(0, 140, 210, 255))
    draw.text((70, 568), "FRESH WATER / SALT SPLIT", fill=(255, 255, 255), font=f_large)

    # Fresh water split box
    draw.rectangle([60, 650, 964, 780], fill=(25, 45, 60), outline=(80, 200, 255), width=3)
    draw.text((80, 665), "OUTPUT [TOP]: 99.9% DISTILLED FRESH WATER", fill=(120, 230, 255), font=f_med)
    draw.text((80, 715), "VAPOR PERMEATE FLOW -> CONDENSER MANIFOLD HEADER", fill=(220, 235, 245), font=f_small)

    # Salt cake split box
    draw.rectangle([60, 800, 964, 930], fill=(45, 40, 30), outline=(240, 180, 60), width=3)
    draw.text((80, 815), "OUTPUT [BTM]: CRYSTALLIZED SALT CAKE HOPPER", fill=(255, 210, 100), font=f_med)
    draw.text((80, 865), "SOLID NACL PRECIPITATE -> GRAVITY HOPPER DISCHARGE", fill=(240, 230, 210), font=f_small)

    draw.text((70, 948), "CONTINUOUS DUAL-STAGE FRACTIONAL EXTRACTION", fill=(150, 220, 160), font=f_small)

    # ----------------------------------------------------
    # Region 4: (1024, 512) to (2048, 1024) - Hazard Chevron Stripes
    # ----------------------------------------------------
    # Bold 45 degree yellow and carbon black diagonal stripes
    stripe_w = 994
    stripe_h = 452
    sx0, sy0 = 1040, 532
    draw.rectangle([sx0, sy0, sx0 + stripe_w, sy0 + stripe_h], fill=(20, 20, 20, 255), outline=(255, 200, 0, 255), width=6)
    
    stripe_pitch = 90
    for offset in range(-stripe_h, stripe_w + stripe_h, stripe_pitch):
        poly = [
            (sx0 + offset, sy0),
            (sx0 + offset + 45, sy0),
            (sx0 + offset + 45 - stripe_h, sy0 + stripe_h),
            (sx0 + offset - stripe_h, sy0 + stripe_h),
        ]
        # Clip to rectangle
        clipped = []
        for px, py in poly:
            clipped.append((max(sx0+3, min(sx0+stripe_w-3, px)), max(sy0+3, min(sy0+stripe_h-3, py))))
        draw.polygon([
            (sx0 + offset, sy0),
            (sx0 + offset + 45, sy0),
            (sx0 + offset + 45 + stripe_h, sy0 + stripe_h),
            (sx0 + offset + stripe_h, sy0 + stripe_h),
        ], fill=(245, 166, 35, 255))
    
    # Overlay border to re-clean edges
    draw.rectangle([sx0, sy0, sx0 + stripe_w, sy0 + stripe_h], outline=(20, 20, 20, 255), width=8)
    draw.rectangle([sx0+8, sy0+8, sx0 + stripe_w-8, sy0 + stripe_h-8], outline=(255, 200, 0, 255), width=4)

    # Overlay black warning badge on top of chevron
    draw.rectangle([sx0 + 200, sy0 + 150, sx0 + stripe_w - 200, sy0 + stripe_h - 150], fill=(15, 15, 15, 240), outline=(255, 255, 255), width=3)
    draw.text((sx0 + 240, sy0 + 175), "CAUTION: HIGH PRESSURE / HIGH VACUUM", fill=(255, 200, 0), font=f_med)
    draw.text((sx0 + 320, sy0 + 225), "KEEP CLEAR OF EVAPORATION CHUTE", fill=(255, 255, 255), font=f_small)

    # ----------------------------------------------------
    # Region 5: (0, 1024) to (2048, 1536) - Conduit & Port Labels
    # ----------------------------------------------------
    labels = [
        ("INLET: RAW SEAWATER / BRINE // 35,000 PPM", (0, 140, 220), (50, 1060)),
        ("MOTIVE STEAM FEED // 180°C // 8.5 BAR", (230, 80, 40), (1050, 1060)),
        ("DISTILLED WATER HEADER // 99.9% PURITY", (0, 220, 180), (50, 1180)),
        ("SALT CAKE HOPPER RELEASE // KNIFE-GATE VALVE", (240, 180, 50), (1050, 1180)),
        ("VACUUM EJECTOR VENTURI NOZZLE // STAGE-2", (200, 140, 255), (50, 1300)),
        ("PRESSURE RELIEF VALVE // SETPOINT 9.0 BAR", (255, 70, 70), (1050, 1300)),
        ("PAPER KITE LIFE SUPPORT LOGISTICS // REG-9941", (255, 255, 255), (50, 1420)),
        ("EXPEDITION LIFE SUPPORT // RECLAIMED WATER", (100, 240, 255), (1050, 1420)),
    ]
    for text, col, (lx, ly) in labels:
        draw.rectangle([lx, ly, lx + 900, ly + 90], fill=(24, 28, 34), outline=col, width=3)
        draw.rectangle([lx, ly, lx + 20, ly + 90], fill=col)
        draw.text((lx + 35, ly + 25), text, fill=(240, 245, 250), font=f_small)

    # ----------------------------------------------------
    # Region 6: (0, 1536) to (2048, 2048) - Stamped Serial & Inspection Badges
    # ----------------------------------------------------
    # Metal plates grid
    draw.rectangle([50, 1560, 980, 1980], fill=(32, 35, 42), outline=(150, 160, 175), width=4)
    draw.text((80, 1590), "FICSIT INDUSTRIAL EXTRACTION", fill=(255, 170, 40), font=f_med)
    draw.text((80, 1640), "VESSEL ID: PK-FE-9941-C", fill=(255, 255, 255), font=f_large)
    draw.text((80, 1700), "DESIGN VACUUM: 0.08 BAR ABS", fill=(100, 220, 255), font=f_med)
    draw.text((80, 1750), "VOLUME: 3,200 L // CAPACITY: 120 L/MIN", fill=(200, 210, 220), font=f_small)
    draw.text((80, 1800), "INSPECTOR: CHIEF ENG. NEELA // OK", fill=(120, 240, 140), font=f_small)

    draw.rectangle([1050, 1560, 1980, 1980], fill=(32, 35, 42), outline=(150, 160, 175), width=4)
    draw.text((1080, 1590), "PROJECT BLUE LIFE SUPPORT CORE", fill=(0, 210, 255), font=f_med)
    draw.text((1080, 1640), "FRESH WATER / SALT SPLIT", fill=(255, 255, 255), font=f_large)
    draw.text((1080, 1700), "PURITY GUARANTEE: > 99.90% DISTILLATE", fill=(255, 210, 50), font=f_med)
    draw.text((1080, 1750), "ELECTRICAL: 480V 3-PHASE 60Hz // 4.0 kW", fill=(200, 210, 220), font=f_small)
    draw.text((1080, 1800), "PAPER KITE EXPEDITIONS // LIFE SUPPORT", fill=(140, 200, 255), font=f_small)

    img.save(os.path.join(OUT_DIR, "T_DesalDecals.png"))
    print("Saved T_DesalDecals.png")

def generate_gauges():
    w, h = 2048, 2048
    img = Image.new("RGBA", (w, h), (18, 22, 28, 255))
    emis = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw_e = ImageDraw.Draw(emis)

    f_huge = get_font(72, bold=True)
    f_large = get_font(50, bold=True)
    f_med = get_font(34, bold=True)
    f_small = get_font(26, bold=False)
    f_mono = get_font(36, bold=True)

    # ----------------------------------------------------
    # Gauge 1: (0, 0) to (1024, 1024) - Digital Vacuum Readout Screen
    # ----------------------------------------------------
    # Slate bezel
    draw.rectangle([40, 40, 984, 984], fill=(12, 16, 22), outline=(60, 75, 95), width=10)
    draw.rectangle([70, 70, 954, 954], fill=(5, 10, 18), outline=(0, 150, 190), width=4)

    # Grid background on screen
    for gx in range(70, 954, 40):
        draw.line([(gx, 70), (gx, 954)], fill=(10, 25, 38), width=1)
    for gy in range(70, 954, 40):
        draw.line([(70, gy), (954, gy)], fill=(10, 25, 38), width=1)

    # Title header
    draw.text((100, 95), "SYSTEM: FLASH DESALINATOR MK-III", fill=(100, 200, 255), font=f_med)
    draw_e.text((100, 95), "SYSTEM: FLASH DESALINATOR MK-III", fill=(40, 120, 180), font=f_med)

    draw.text((100, 145), "PAPER KITE EXPEDITIONS // LIFE SUPPORT", fill=(150, 180, 200), font=f_small)

    # Big Digital Vacuum readout
    draw.rectangle([95, 210, 925, 420], fill=(8, 15, 25), outline=(0, 229, 255), width=4)
    draw_e.rectangle([95, 210, 925, 420], outline=(0, 229, 255), width=4)

    draw.text((130, 240), "OPERATING VACUUM:", fill=(255, 190, 50), font=f_small)
    draw_e.text((130, 240), "OPERATING VACUUM:", fill=(200, 140, 30), font=f_small)

    # Stamped bright readout: 0.08 BAR
    draw.text((130, 280), "0.08 BAR", fill=(0, 240, 255), font=f_huge)
    draw_e.text((130, 280), "0.08 BAR", fill=(0, 240, 255), font=f_huge)

    draw.text((620, 310), "ABS VACUUM", fill=(0, 200, 240), font=f_med)
    draw_e.text((620, 310), "ABS VACUUM", fill=(0, 200, 240), font=f_med)

    # Secondary parameters
    draw.text((100, 460), "SATURATION TEMP : 41.51 °C [FLASH BOIL]", fill=(120, 240, 140), font=f_mono)
    draw_e.text((100, 460), "SATURATION TEMP : 41.51 °C [FLASH BOIL]", fill=(60, 200, 80), font=f_mono)

    draw.text((100, 520), "WATER PURITY    : 99.94% DISTILLED", fill=(0, 220, 255), font=f_mono)
    draw_e.text((100, 520), "WATER PURITY    : 99.94% DISTILLED", fill=(0, 180, 240), font=f_mono)

    draw.text((100, 580), "SALT CAKE HOPPER: 68% CAPACITY [ACTIVE]", fill=(255, 210, 60), font=f_mono)
    draw_e.text((100, 580), "SALT CAKE HOPPER: 68% CAPACITY [ACTIVE]", fill=(200, 150, 40), font=f_mono)

    draw.text((100, 640), "VACUUM EJECTOR  : 8.5 BAR MOTIVE STEAM", fill=(255, 140, 100), font=f_mono)
    draw_e.text((100, 640), "VACUUM EJECTOR  : 8.5 BAR MOTIVE STEAM", fill=(200, 90, 60), font=f_mono)

    # Bar graph
    draw.rectangle([100, 720, 920, 770], fill=(15, 22, 30), outline=(100, 120, 140), width=2)
    # 92% vacuum level fill
    bar_w = int((920 - 100) * 0.92)
    draw.rectangle([104, 724, 104 + bar_w, 766], fill=(0, 220, 255))
    draw_e.rectangle([104, 724, 104 + bar_w, 766], fill=(0, 220, 255))
    draw.text((115, 785), "VACUUM DEPRESSION: -0.92 BAR GAUGE (92% EFFICIENCY)", fill=(200, 220, 240), font=f_small)

    # Status LED block
    draw.rectangle([100, 840, 500, 920], fill=(20, 60, 30), outline=(60, 220, 90), width=3)
    draw_e.rectangle([100, 840, 500, 920], fill=(20, 120, 40), outline=(60, 220, 90), width=3)
    draw.text((125, 860), "STATUS: OPTIMAL", fill=(120, 255, 140), font=f_med)
    draw_e.text((125, 860), "STATUS: OPTIMAL", fill=(120, 255, 140), font=f_med)

    draw.rectangle([540, 840, 920, 920], fill=(15, 45, 65), outline=(0, 180, 240), width=3)
    draw_e.rectangle([540, 840, 920, 920], fill=(15, 70, 100), outline=(0, 180, 240), width=3)
    draw.text((565, 860), "LIFE SUPPORT OK", fill=(0, 220, 255), font=f_med)
    draw_e.text((565, 860), "LIFE SUPPORT OK", fill=(0, 220, 255), font=f_med)

    # ----------------------------------------------------
    # Gauge 2: (1024, 0) to (2048, 1024) - Analog Vacuum Dial Gauge
    # ----------------------------------------------------
    cx, cy = 1536, 512
    r_outer = 450
    # Outer brass/bronze bezel
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=(45, 40, 35), outline=(210, 175, 90), width=14)
    # Dial face
    r_face = 410
    draw.ellipse([cx - r_face, cy - r_face, cx + r_face, cy + r_face], fill=(245, 242, 235), outline=(30, 30, 30), width=6)

    # Green vacuum operating arc (from angle 40 deg to 120 deg)
    # Scale: 0 to -1.0 bar (angle 220 deg down to -40 deg)
    draw.text((cx - 160, cy - 220), "VACUUM GAUGE", fill=(40, 45, 50), font=f_large)
    draw.text((cx - 130, cy - 160), "FLASH EVAPORATOR", fill=(100, 110, 120), font=f_small)
    draw.text((cx - 120, cy + 120), "-0.92 BAR GAUGE", fill=(0, 120, 160), font=f_med)
    draw.text((cx - 150, cy + 170), "0.08 BAR ABSOLUTE", fill=(180, 40, 30), font=f_med)

    # Dial ticks
    for i in range(11): # 0.0 to -1.0
        val = -i / 10.0
        # angle from 220 deg (0 bar) to -40 deg (-1.0 bar)
        ang = math.radians(220 - (260 * i / 10.0))
        x1 = cx + (r_face - 20) * math.cos(ang)
        y1 = cy - (r_face - 20) * math.sin(ang)
        x2 = cx + (r_face - 65) * math.cos(ang)
        y2 = cy - (r_face - 65) * math.sin(ang)
        draw.line([(x1, y1), (x2, y2)], fill=(20, 20, 20), width=6)
        tx = cx + (r_face - 105) * math.cos(ang) - 25
        ty = cy - (r_face - 105) * math.sin(ang) - 18
        draw.text((tx, ty), f"{val:.1f}", fill=(30, 30, 30), font=f_mono)

    # Subticks
    for i in range(51):
        ang = math.radians(220 - (260 * i / 50.0))
        x1 = cx + (r_face - 20) * math.cos(ang)
        y1 = cy - (r_face - 20) * math.sin(ang)
        x2 = cx + (r_face - 45) * math.cos(ang)
        y2 = cy - (r_face - 45) * math.sin(ang)
        draw.line([(x1, y1), (x2, y2)], fill=(70, 70, 70), width=3)

    # Needle pointing at -0.92 bar (i = 9.2)
    needle_ang = math.radians(220 - (260 * 9.2 / 10.0))
    nx = cx + (r_face - 40) * math.cos(needle_ang)
    ny = cy - (r_face - 40) * math.sin(needle_ang)
    draw.line([(cx, cy), (nx, ny)], fill=(220, 30, 30), width=8)
    draw_e.line([(cx, cy), (nx, ny)], fill=(255, 60, 60), width=6)
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(30, 30, 30), outline=(210, 175, 90), width=4)

    # ----------------------------------------------------
    # Gauge 3: (0, 1024) to (1024, 2048) - Steam Pressure Dial Gauge
    # ----------------------------------------------------
    cx3, cy3 = 512, 1536
    draw.ellipse([cx3 - r_outer, cy3 - r_outer, cx3 + r_outer, cy3 + r_outer], fill=(45, 40, 35), outline=(210, 175, 90), width=14)
    draw.ellipse([cx3 - r_face, cy3 - r_face, cx3 + r_face, cy3 + r_face], fill=(245, 242, 235), outline=(30, 30, 30), width=6)

    draw.text((cx3 - 170, cy3 - 220), "STEAM PRESSURE", fill=(40, 45, 50), font=f_large)
    draw.text((cx3 - 140, cy3 - 160), "MOTIVE RECIRCULATION", fill=(100, 110, 120), font=f_small)
    draw.text((cx3 - 110, cy3 + 130), "SET: 8.5 BAR MAX", fill=(180, 40, 30), font=f_med)

    for i in range(11): # 0 to 10 bar
        val = i
        ang = math.radians(220 - (260 * i / 10.0))
        x1 = cx3 + (r_face - 20) * math.cos(ang)
        y1 = cy3 - (r_face - 20) * math.sin(ang)
        x2 = cx3 + (r_face - 65) * math.cos(ang)
        y2 = cy3 - (r_face - 65) * math.sin(ang)
        col = (200, 30, 20) if i >= 8 else (20, 20, 20)
        draw.line([(x1, y1), (x2, y2)], fill=col, width=6)
        tx = cx3 + (r_face - 105) * math.cos(ang) - 15
        ty = cy3 - (r_face - 105) * math.sin(ang) - 18
        draw.text((tx, ty), f"{val}", fill=col, font=f_mono)

    # Needle pointing at 6.8 bar
    needle_ang3 = math.radians(220 - (260 * 6.8 / 10.0))
    nx3 = cx3 + (r_face - 40) * math.cos(needle_ang3)
    ny3 = cy3 - (r_face - 40) * math.sin(needle_ang3)
    draw.line([(cx3, cy3), (nx3, ny3)], fill=(220, 30, 30), width=8)
    draw_e.line([(cx3, cy3), (nx3, ny3)], fill=(255, 60, 60), width=6)
    draw.ellipse([cx3 - 24, cy3 - 24, cx3 + 24, cy3 + 24], fill=(30, 30, 30), outline=(210, 175, 90), width=4)

    # ----------------------------------------------------
    # Gauge 4: (1024, 1024) to (2048, 2048) - Condenser Flow & Purity Diagnostics
    # ----------------------------------------------------
    draw.rectangle([1064, 1064, 2008, 2008], fill=(10, 15, 22), outline=(0, 200, 240), width=8)
    draw.rectangle([1090, 1090, 1982, 1982], fill=(5, 8, 14), outline=(40, 80, 110), width=2)

    draw.text((1120, 1120), "DISTILLATION FRACTIONATION", fill=(0, 220, 255), font=f_large)
    draw_e.text((1120, 1120), "DISTILLATION FRACTIONATION", fill=(0, 150, 200), font=f_large)

    draw.text((1120, 1180), "EXPEDITION LIFE SUPPORT PURITY LOG", fill=(160, 190, 210), font=f_small)

    # Parameter boxes
    p_boxes = [
        ("PERMEATE TDS", "12.4 PPM", "PASS (NURSE GRADE)", (0, 240, 200)),
        ("RECIRCULATION", "18.5 L/MIN", "CONTINUOUS LOOP", (255, 190, 40)),
        ("SALT ACCUMULATION", "42.8 KG/H", "CYCLIC PURGE ON", (255, 120, 80)),
        ("VACUUM SEAL INTEGRITY", "100.0%", "ZERO LEAKAGE DETECTED", (100, 255, 120)),
    ]
    for idx, (title, val, desc, col) in enumerate(p_boxes):
        by = 1250 + idx * 165
        draw.rectangle([1120, by, 1950, by + 135], fill=(12, 20, 30), outline=col, width=3)
        draw_e.rectangle([1120, by, 1950, by + 135], outline=col, width=2)
        draw.text((1140, by + 15), title, fill=(180, 200, 220), font=f_small)
        draw.text((1140, by + 50), val, fill=col, font=f_huge)
        draw_e.text((1140, by + 50), val, fill=col, font=f_huge)
        draw.text((1550, by + 70), desc, fill=(210, 225, 240), font=f_small)

    img.save(os.path.join(OUT_DIR, "T_DesalGauges.png"))
    emis.save(os.path.join(OUT_DIR, "T_DesalGauges_Emissive.png"))
    print("Saved T_DesalGauges.png and T_DesalGauges_Emissive.png")

if __name__ == "__main__":
    generate_decals()
    generate_gauges()
