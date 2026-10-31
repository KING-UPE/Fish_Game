import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_survey_texture(output_path):
    w, h = 2048, 2048
    # Background: dark industrial painted steel / carbon composite
    img = Image.new("RGBA", (w, h), (26, 28, 32, 255))
    draw = ImageDraw.Draw(img)

    # Subtle metallic panel border
    draw.rectangle([20, 20, w - 21, h - 21], outline=(55, 60, 68, 255), width=8)
    draw.rectangle([40, 40, w - 41, h - 41], outline=(40, 45, 52, 255), width=4)

    # Top & Bottom Hazard Warning Stripes (Safety Orange & Black)
    stripe_height = 110
    stripe_w = 90
    
    # Top banner stripes
    for i in range(-10, w // stripe_w + 10):
        x0 = i * stripe_w * 2
        pts = [(x0, 45), (x0 + stripe_w, 45), (x0 + stripe_w + 80, 45 + stripe_height), (x0 + 80, 45 + stripe_height)]
        # Clip to banner box
        draw.polygon(pts, fill=(245, 140, 10, 255)) # FICSIT Safety Orange
    # Inner border for top stripe
    draw.rectangle([45, 45 + stripe_height, w - 46, 45 + stripe_height + 6], fill=(15, 16, 18, 255))

    # Bottom banner stripes
    for i in range(-10, w // stripe_w + 10):
        x0 = i * stripe_w * 2
        pts = [(x0, h - 45 - stripe_height), (x0 + stripe_w, h - 45 - stripe_height), (x0 + stripe_w + 80, h - 45), (x0 + 80, h - 45)]
        draw.polygon(pts, fill=(245, 140, 10, 255))
    draw.rectangle([45, h - 45 - stripe_height - 6, w - 46, h - 45 - stripe_height], fill=(15, 16, 18, 255))

    # Dark background plate for texts
    draw.rectangle([60, 180, w - 61, h - 180], fill=(18, 20, 24, 255))

    # Load system fonts or fallback
    def get_font(size, bold=False):
        font_names = ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf", "courbd.ttf" if bold else "cour.ttf"]
        for fn in font_names:
            try:
                return ImageFont.truetype(f"C:/Windows/Fonts/{fn}", size)
            except Exception:
                pass
        return ImageFont.load_default()

    font_title = get_font(72, bold=True)
    font_sub = get_font(44, bold=True)
    font_data = get_font(38, bold=True)
    font_mono = get_font(32, bold=False)
    font_small = get_font(24, bold=False)

    # Header Box
    draw.rectangle([80, 200, w - 81, 330], fill=(28, 32, 40, 255), outline=(70, 80, 95, 255), width=3)
    draw.text((110, 220), "PAPER KITE EXPEDITIONS // REG-9941", font=font_title, fill=(255, 255, 255, 255))
    draw.text((110, 290), "PROJECT BLUE // AUTOMATED EXTRACTION PROTOCOL", font=font_small, fill=(120, 200, 255, 255))
    draw.text((w - 520, 235), "SECTOR: DEEP REEF", font=font_sub, fill=(245, 140, 10, 255))

    # Primary Survey Anomaly Box (Glowing border & cyan text)
    draw.rectangle([80, 360, w - 81, 540], fill=(14, 26, 36, 255), outline=(0, 200, 255, 255), width=4)
    draw.text((110, 385), "SURVEY ANOMALY // CLASS-4", font=font_title, fill=(0, 240, 255, 255))
    draw.text((110, 470), "DESIGNATION: CORAL ORE NODE (BIOLUMINESCENT MATRIX)", font=font_sub, fill=(200, 230, 255, 255))

    # Data telemetry panels (2 columns)
    # Left column: Resonance & Hardness
    draw.rectangle([80, 570, 1000, 1000], fill=(22, 25, 30, 255), outline=(60, 70, 85, 255), width=2)
    draw.text((110, 595), "[ SPECTRAL RESONANCE DATA ]", font=font_sub, fill=(255, 180, 40, 255))
    
    # Large Resonance readout
    draw.rectangle([110, 660, 970, 780], fill=(10, 15, 20, 255), outline=(0, 180, 220, 255), width=2)
    draw.text((130, 675), "RESONANCE: 440 THZ", font=font_title, fill=(255, 60, 140, 255))
    draw.text((130, 745), "HARMONIC BAND: ULTRA-VIOLET COHERENT", font=font_mono, fill=(180, 210, 230, 255))

    # Mohs Hardness readout
    draw.rectangle([110, 800, 970, 920], fill=(10, 15, 20, 255), outline=(0, 180, 220, 255), width=2)
    draw.text((130, 815), "HIGH HARDNESS MOHS 9.2", font=font_title, fill=(255, 220, 50, 255))
    draw.text((130, 885), "DRILL BIT REQUIREMENT: TUNGSTEN-CARBIDE MK.3", font=font_mono, fill=(180, 210, 230, 255))

    draw.text((110, 940), "LATTICE: HEXAGONAL-BIPYRAMIDAL // TWINNING RATIO: 1.44", font=font_small, fill=(130, 150, 170, 255))

    # Right column: Extraction & Caution
    draw.rectangle([1040, 570, w - 81, 1000], fill=(22, 25, 30, 255), outline=(60, 70, 85, 255), width=2)
    draw.text((1070, 595), "[ EXTRACTION CLEARANCE & SAFETY ]", font=font_sub, fill=(255, 180, 40, 255))

    # Caution Banner Box
    draw.rectangle([1070, 660, w - 110, 780], fill=(50, 15, 15, 255), outline=(255, 40, 40, 255), width=3)
    draw.text((1090, 675), "CAUTION: HIGH VOLTAGE / HIGH PRESSURE", font=font_data, fill=(255, 80, 80, 255))
    draw.text((1090, 735), "DISCHARGE HAZARD: 12.4 KV PEAK EMISSION", font=font_mono, fill=(255, 180, 180, 255))

    # Status LEDs and indicators
    draw.rectangle([1070, 800, w - 110, 960], fill=(15, 18, 22, 255), outline=(50, 60, 75, 255), width=2)
    
    # 4 Status circles (LEDs)
    led_data = [
        ("CORE FLUX: LOCKED", (0, 255, 120, 255)),
        ("RESONANCE LOCK: ACTIVE", (0, 220, 255, 255)),
        ("PIEZO CHARGE: 88.5%", (255, 200, 30, 255)),
        ("VENT INTEGRITY: NOMINAL", (0, 255, 120, 255)),
    ]
    for idx, (label, col) in enumerate(led_data):
        y_pos = 815 + idx * 35
        # Outer ring
        draw.ellipse([1095, y_pos, 1115, y_pos + 20], fill=col, outline=(255, 255, 255, 255), width=1)
        draw.text((1130, y_pos), label, font=font_mono, fill=(220, 230, 240, 255))

    # Mid section: Simulated Oscilloscope Waveform Graphic (440 THz harmonic wave)
    draw.rectangle([80, 1030, w - 81, 1430], fill=(10, 14, 18, 255), outline=(0, 160, 220, 255), width=2)
    draw.text((110, 1045), "HARMONIC WAVEFORM OSCILLOSCOPE // FREQ = 440.00 THZ // PHASE = 0.618 RAD", font=font_mono, fill=(0, 220, 255, 255))
    
    # Oscilloscope Grid Lines
    for gy in range(1080, 1420, 35):
        draw.line([(90, gy), (w - 91, gy)], fill=(20, 35, 45, 255), width=1)
    for gx in range(100, w - 90, 80):
        draw.line([(gx, 1080), (gx, 1410)], fill=(20, 35, 45, 255), width=1)
    # Centerline
    draw.line([(90, 1245), (w - 91, 1245)], fill=(40, 70, 90, 255), width=2)

    # Waveform curve (superposition of 440 THz fundamental + 3rd harmonic)
    points_wave = []
    points_wave2 = []
    for px in range(100, w - 100):
        t = (px - 100) / 45.0
        # Fundamental wave
        y = 1245 - math.sin(t) * 90 - math.sin(t * 2.5) * 35 - math.sin(t * 0.3) * 15
        points_wave.append((px, y))
        # Resonant harmonic
        y2 = 1245 - math.cos(t * 1.8) * 60 - math.sin(t * 3.7) * 20
        points_wave2.append((px, y2))
    
    draw.line(points_wave2, fill=(255, 60, 140, 180), width=3) # Pink harmonic
    draw.line(points_wave, fill=(0, 255, 240, 255), width=4)    # Cyan fundamental

    # Lower Section: Stamped Hardware Specs, Serial Number, Barcode
    draw.rectangle([80, 1460, w - 81, 1820], fill=(22, 25, 30, 255), outline=(60, 70, 85, 255), width=2)
    
    draw.text((110, 1485), "STAMPED ASSET REGISTRATION & TELEMETRY", font=font_sub, fill=(220, 230, 240, 255))
    draw.text((110, 1545), "ASSET ID: PK-CR-9941-ORE-004", font=font_mono, fill=(180, 200, 220, 255))
    draw.text((110, 1590), "GRID ALLOCATION: 250cm x 250cm x 200cm // EXTRACTION RATE: 120/MIN", font=font_mono, fill=(180, 200, 220, 255))
    draw.text((110, 1635), "DEPLOYMENT NODE: SM_CoralOreNode // COLLISION: CONVEX HULL MATRIX", font=font_mono, fill=(180, 200, 220, 255))
    draw.text((110, 1680), "PROPERTY OF PAPER KITE EXPEDITIONS - ALL RIGHTS RESERVED", font=font_mono, fill=(120, 140, 160, 255))

    # Barcode
    bx = w - 620
    by = 1530
    draw.rectangle([bx - 15, by - 15, w - 110, by + 180], fill=(240, 245, 250, 255))
    bar_x = bx
    import random
    rng = random.Random(9941)
    while bar_x < w - 130:
        bar_w = rng.choice([2, 4, 6, 9])
        draw.rectangle([bar_x, by, bar_x + bar_w, by + 130], fill=(10, 15, 20, 255))
        bar_x += bar_w + rng.choice([3, 5, 7, 10])
    draw.text((bx + 30, by + 140), "* PK-REG-9941-CR-004 *", font=font_mono, fill=(10, 15, 20, 255))

    # Corner mounting bolt heads
    for cx in [70, w - 70]:
        for cy in [70, h - 70]:
            draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(70, 75, 85, 255), outline=(130, 140, 155, 255), width=3)
            draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(40, 45, 50, 255))
            draw.line([(cx - 12, cy), (cx + 12, cy)], fill=(120, 130, 145, 255), width=3)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated survey texture: {output_path} ({w}x{h})")

if __name__ == "__main__":
    generate_survey_texture(r"D:\Game\FishGame\Saved\T_CoralOre_SurveyPlaque.png")
