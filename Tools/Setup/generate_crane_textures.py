"""Generate high-resolution industrial textures for Salvage Crane:
1. T_HazardStripes (512x512) - High-vis yellow and carbon-black industrial chevron stripes
2. T_CraneDecals (1024x1024) - Stamped factory signage plates with authentic FICSIT / Blue Project lore
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

TEX_DIR = r"D:\Game\FishGame\Saved\Textures"
os.makedirs(TEX_DIR, exist_ok=True)

def generate_hazard_stripes():
    size = 512
    stripe_w = 48
    img = Image.new("RGBA", (size, size), (240, 160, 10, 255)) # Warm FICSIT hazard yellow
    draw = ImageDraw.Draw(img)
    
    # Draw diagonal black stripes (angle 45 deg)
    black = (28, 28, 32, 255)
    for offset in range(-size, size * 2, stripe_w * 2):
        points = [
            (offset, 0),
            (offset + stripe_w, 0),
            (offset + stripe_w - size, size),
            (offset - size, size)
        ]
        draw.polygon(points, fill=black)
        
    # Add subtle grime / border wear
    for y in range(size):
        if y < 4 or y > size - 5:
            draw.line([(0, y), (size, y)], fill=(20, 20, 22, 180))
            
    path = os.path.join(TEX_DIR, "T_HazardStripes.png")
    img.save(path)
    print("Generated:", path)

def generate_crane_decals():
    size = 1024
    img = Image.new("RGBA", (size, size), (18, 20, 24, 255)) # Dark industrial steel plate background
    draw = ImageDraw.Draw(img)

    # Use default bitmap font or load a clean system font if available
    font_large = None
    font_med = None
    font_small = None
    for fpath in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/segoeuib.ttf"]:
        if os.path.exists(fpath):
            try:
                font_large = ImageFont.truetype(fpath, 34)
                font_med = ImageFont.truetype(fpath, 24)
                font_small = ImageFont.truetype(fpath, 16)
                break
            except Exception:
                pass
    if font_large is None:
        font_large = ImageFont.load_default()
        font_med = font_large
        font_small = font_large

    yellow = (245, 175, 20, 255)
    white = (240, 242, 245, 255)
    dark_gray = (35, 38, 44, 255)
    orange = (255, 105, 15, 255)
    cyan = (50, 215, 245, 255)

    def draw_beveled_box(x0, y0, x1, y1, fill, outline, width=3):
        draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)
        # Corner rivets
        r = 5
        for cx, cy in [(x0 + 12, y0 + 12), (x1 - 12, y0 + 12), (x0 + 12, y1 - 12), (x1 - 12, y1 - 12)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(80, 85, 95, 255), outline=(120, 125, 135, 255))

    # PLATE 1: Top Gantry Header Sign (0, 0 to 1024, 256)
    draw_beveled_box(20, 20, 1004, 236, (26, 28, 34, 255), yellow, 4)
    # Header yellow bar
    draw.rectangle([24, 24, 1000, 60], fill=yellow)
    draw.text((40, 28), "PAPER KITE EXPEDITIONS // REG-9941-EXT", fill=(20, 20, 20, 255), font=font_med)
    draw.text((720, 28), "CLASS: HEAVY SALVAGE", fill=(20, 20, 20, 255), font=font_med)
    
    draw.text((45, 80), "PROJECT BLUE // AUTOMATED EXTRACTION", fill=white, font=font_large)
    draw.text((45, 130), "KITE CARGO // AUTO-CRANE 01", fill=yellow, font=font_large)
    draw.text((45, 180), "OPERATIONAL STATUS: ACTIVE   |   SERVO TORQUE: 18,500 Nm", fill=(170, 180, 195, 255), font=font_small)
    draw.text((700, 180), "SYSTEM FW: v5.84-RELEASE", fill=cyan, font=font_small)

    # PLATE 2: SWL 25 TONNES & Caution Overhead Load (20, 270 to 500, 520)
    draw_beveled_box(20, 270, 500, 510, (26, 28, 34, 255), orange, 4)
    draw.rectangle([24, 274, 496, 310], fill=orange)
    draw.text((35, 278), "CAUTION: OVERHEAD LOAD", fill=(20, 20, 20, 255), font=font_med)
    draw.text((40, 330), "SWL: 25 TONNES", fill=yellow, font=font_large)
    draw.text((40, 385), "STAND CLEAR OF GANTRY HOIST", fill=white, font=font_med)
    draw.text((40, 430), "SAFETY HARNESS & HARD HAT MANDATORY", fill=(180, 185, 195, 255), font=font_small)
    draw.text((40, 460), "INSPECTION DATE: 2026-OCT // PASS", fill=cyan, font=font_small)

    # PLATE 3: WARNING: PINCH POINT & Claw Graphics (524, 270 to 1004, 510)
    draw_beveled_box(524, 270, 1004, 510, (26, 28, 34, 255), yellow, 4)
    draw.rectangle([528, 274, 1000, 310], fill=yellow)
    draw.text((540, 278), "WARNING: PINCH POINT", fill=(20, 20, 20, 255), font=font_med)
    draw.text((545, 330), "TRI-CLAW PNEUMATIC GRAPPLE", fill=white, font=font_large)
    draw.text((545, 385), "PRESSURE: 350 BAR // 5,000 PSI", fill=orange, font=font_med)
    draw.text((545, 430), "DISCONNECT PNEUMATIC FEED BEFORE SERVICE", fill=(180, 185, 195, 255), font=font_small)
    draw.text((545, 460), "MAGNETIC FLUX: 12.8 TESLA MAX", fill=cyan, font=font_small)

    # PLATE 4: High Voltage & Control Panel Status (20, 530 to 500, 770)
    draw_beveled_box(20, 530, 500, 770, (22, 24, 30, 255), (220, 40, 30, 255), 4)
    draw.rectangle([24, 534, 496, 570], fill=(220, 40, 30, 255))
    draw.text((35, 538), "DANGER: HIGH VOLTAGE // 480V", fill=white, font=font_med)
    draw.text((40, 590), "MAIN POWER DISTRIBUTION", fill=white, font=font_med)
    draw.text((40, 630), "CIRCUIT BREAKER: 400A / 3-PHASE", fill=yellow, font=font_small)
    draw.text((40, 660), "ISOLATE BEFORE OPENING ENCLOSURE", fill=(180, 185, 195, 255), font=font_small)
    draw.text((40, 700), "EMERGENCY SHUTOFF ACCESSIBLE ON FRONT", fill=orange, font=font_small)

    # PLATE 5: Digital Instrument Gauges & Readout Screen (524, 530 to 1004, 770)
    draw_beveled_box(524, 530, 1004, 770, (10, 18, 22, 255), cyan, 3)
    draw.rectangle([528, 534, 1000, 565], fill=(20, 45, 55, 255))
    draw.text((540, 538), "TELEMETRY MONITOR // EXTRACTION CYCLE", fill=cyan, font=font_small)
    draw.text((545, 580), "WINCH TENSION: 142.6 kN", fill=white, font=font_med)
    draw.text((545, 620), "CORE TEMP: 64.2 C  [NOMINAL]", fill=(70, 235, 120, 255), font=font_med)
    draw.text((545, 660), "CYCLE TIME: 2.0s  |  EFFICIENCY: 99.4%", fill=cyan, font=font_small)
    draw.text((545, 695), "SUBSEA SENSOR LINK: LOCKED", fill=(70, 235, 120, 255), font=font_small)
    draw.text((545, 725), "BUFFER CAPACITY: 20 / 20 UNITS", fill=yellow, font=font_small)

    # PLATE 6: Chevron Stripe Banners (20, 790 to 1004, 1004)
    banner_h = 45
    for row, y_top in enumerate([790, 845, 900, 955]):
        draw.rectangle([20, y_top, 1004, y_top + banner_h], fill=(26, 28, 32, 255), outline=dark_gray, width=2)
        # diagonal hazard chevrons inside banner
        bw = 35
        for x in range(20, 1004, bw * 2):
            pts = [(x, y_top), (min(x + bw, 1004), y_top), (min(x + bw - 20, 1004), y_top + banner_h), (max(x - 20, 20), y_top + banner_h)]
            draw.polygon(pts, fill=yellow)
        # Overlay text on banner
        if row == 0:
            draw.text((45, y_top + 10), "--- WARNING: AUTOMATIC CRANE GANTRY --- KEEP CLEAR ---", fill=(20, 20, 20, 255), font=font_med)
        elif row == 1:
            draw.text((45, y_top + 10), ">>> SWL 25T >>> OVERHEAD LOAD >>> MAXIMUM TRAVEL RADIUS 200CM >>>", fill=(20, 20, 20, 255), font=font_med)
        elif row == 2:
            draw.text((45, y_top + 10), "=== HIGH TENSION WIRE ROPE === NO STEP === ANCHORAGE POINT ===", fill=(20, 20, 20, 255), font=font_med)
        else:
            draw.text((45, y_top + 10), "/// PINCH POINT HAZARD /// ROTATING CRANE TURRET /// SAFETY ZONE ///", fill=(20, 20, 20, 255), font=font_med)

    path = os.path.join(TEX_DIR, "T_CraneDecals.png")
    img.save(path)
    print("Generated:", path)

if __name__ == "__main__":
    generate_hazard_stripes()
    generate_crane_decals()
