"""Generate high-fidelity industrial PBR decal & signage textures for Seabed Drill.
Produces:
  D:/Game/FishGame/Saved/T_SeabedDrill_Decals_D.png (Albedo / Diffuse)
  D:/Game/FishGame/Saved/T_SeabedDrill_Decals_E.png (Emissive glow)
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

WIDTH = 2048
HEIGHT = 2048

# Create Base Albedo and Emissive images
albedo = Image.new("RGBA", (WIDTH, HEIGHT), (28, 30, 35, 255))
emissive = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))

draw_a = ImageDraw.Draw(albedo)
draw_e = ImageDraw.Draw(emissive)

# Try loading standard clean fonts or fallback
def get_font(size, bold=False):
    for f in ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf", "courbd.ttf" if bold else "cour.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()

font_huge = get_font(52, bold=True)
font_large = get_font(38, bold=True)
font_med_b = get_font(26, bold=True)
font_med = get_font(24, bold=False)
font_small = get_font(18, bold=False)
font_tiny = get_font(14, bold=True)

# Helper to draw beveled plate
def draw_plate(draw, x0, y0, x1, y1, fill=(35, 38, 44), border=(60, 65, 75), bevel=4):
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=border, width=bevel)
    # 4 corner bolts
    r = 8
    margin = 16
    for bx, by in [(x0 + margin, y0 + margin), (x1 - margin, y0 + margin),
                   (x0 + margin, y1 - margin), (x1 - margin, y1 - margin)]:
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=(85, 90, 100), outline=(20, 22, 25), width=2)
        draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(130, 135, 145))

# ==============================================================================
# SECTION 1: MAIN FACTORY LORE PLACARD (UV: X 0..1024, Y 0..512)
# "PROJECT BLUE // PNEUMATIC CORE DRILL", "DRILL DEPTH: 150M", "MAX PRESSURE: 400 BAR", "CORAL CORE EXTRACTION"
# ==============================================================================
draw_plate(draw_a, 20, 20, 1004, 492, fill=(24, 27, 32), border=(80, 88, 102), bevel=5)

# Top Header banner (Dark Navy with Cyan stripe)
draw_a.rectangle([30, 30, 994, 95], fill=(18, 32, 48))
draw_a.rectangle([30, 95, 994, 100], fill=(0, 180, 240))
draw_a.text((50, 48), "PAPER KITE EXPEDITIONS // REG-9941", fill=(160, 215, 255), font=font_med_b)
draw_a.text((720, 48), "AUTOMATED EXTRACTION", fill=(240, 190, 40), font=font_med_b)

# Main Title
draw_a.text((50, 120), "PROJECT BLUE // PNEUMATIC CORE DRILL", fill=(255, 255, 255), font=font_large)

# Caution Stripe Bar
draw_a.rectangle([50, 180, 974, 215], fill=(240, 160, 15))
draw_a.text((65, 186), "CAUTION: HIGH PRESSURE PNEUMATIC IMPACT DRILL // ROTARY CARBIDED CORE", fill=(10, 10, 10), font=font_small)

# Spec Grid Details
draw_a.rectangle([50, 235, 490, 455], fill=(18, 20, 24), outline=(45, 50, 60), width=2)
draw_a.text((65, 250), "SPECIFICATION // DEEP DRILL", fill=(0, 180, 240), font=font_small)
draw_a.text((65, 285), "• DRILL DEPTH: 150M", fill=(255, 255, 255), font=font_med_b)
draw_a.text((65, 325), "• MAX PRESSURE: 400 BAR", fill=(255, 200, 80), font=font_med_b)
draw_a.text((65, 365), "• CORAL CORE EXTRACTION", fill=(130, 230, 180), font=font_med_b)
draw_a.text((65, 405), "• SHAFT STROKE: 2400 MM", fill=(180, 190, 200), font=font_small)

draw_a.rectangle([510, 235, 974, 455], fill=(18, 20, 24), outline=(45, 50, 60), width=2)
draw_a.text((525, 250), "OPERATIONAL TELEMETRY", fill=(0, 180, 240), font=font_small)
draw_a.text((525, 285), "SERIAL NO: PCD-150-REG9941", fill=(220, 225, 230), font=font_med)
draw_a.text((525, 325), "IMPACT HAMMER: 4200 BPM", fill=(220, 225, 230), font=font_med)
draw_a.text((525, 365), "SEABED ANCHOR: QUAD-PAD PNEUMATIC", fill=(220, 225, 230), font=font_med)
draw_a.text((525, 405), "CORE SLAG FLUTE: DIRECT DISCHARGE", fill=(220, 225, 230), font=font_med)

# Emissive for main sign (text glow)
draw_e.rectangle([30, 95, 994, 100], fill=(0, 160, 220))
draw_e.text((720, 48), "AUTOMATED EXTRACTION", fill=(120, 90, 15), font=font_med_b)
draw_e.text((65, 285), "• DRILL DEPTH: 150M", fill=(140, 140, 140), font=font_med_b)
draw_e.text((65, 325), "• MAX PRESSURE: 400 BAR", fill=(180, 140, 40), font=font_med_b)
draw_e.text((65, 365), "• CORAL CORE EXTRACTION", fill=(50, 160, 90), font=font_med_b)

# ==============================================================================
# SECTION 2: DIGITAL TELEMETRY STATUS SCREEN (UV: X 1024..2048, Y 0..512)
# ==============================================================================
draw_plate(draw_a, 1044, 20, 2028, 492, fill=(10, 16, 22), border=(40, 70, 90), bevel=6)

# Screen interior glow
draw_a.rectangle([1064, 40, 2008, 472], fill=(6, 12, 16), outline=(20, 100, 120), width=2)
# Scanlines
for y in range(45, 470, 6):
    draw_a.line([(1065, y), (2007, y)], fill=(10, 24, 30))

draw_a.text((1085, 55), "▶ SEABED DRILL TELEMETRY // CORE EX-01", fill=(0, 240, 255), font=font_large)
draw_e.text((1085, 55), "▶ SEABED DRILL TELEMETRY // CORE EX-01", fill=(0, 240, 255), font=font_large)

draw_a.text((1085, 120), "SYSTEM STATUS: OPERATIONAL", fill=(80, 255, 120), font=font_med_b)
draw_e.text((1085, 120), "SYSTEM STATUS: OPERATIONAL", fill=(80, 255, 120), font=font_med_b)

draw_a.text((1085, 165), "PNEUMATIC ACCUMULATOR: 385.4 BAR [NORMAL]", fill=(255, 210, 50), font=font_med)
draw_e.text((1085, 165), "PNEUMATIC ACCUMULATOR: 385.4 BAR [NORMAL]", fill=(200, 160, 30), font=font_med)

draw_a.text((1085, 205), "ROTARY CUTTER HEAD: 420 RPM // FLUTES CLEAR", fill=(0, 220, 240), font=font_med)
draw_a.text((1085, 245), "CORAL SLAG EXTRACTION: 48.2 LITERS / MIN", fill=(255, 140, 160), font=font_med)
draw_a.text((1085, 285), "IMPACT CYLINDER TEMP: 68.4°C // COOLING OK", fill=(180, 220, 240), font=font_med)
draw_a.text((1085, 325), "SEABED ANCHOR STRAIN: 12.4 kN [STABLE]", fill=(180, 220, 240), font=font_med)

# Graphical bar meters on the screen
draw_a.rectangle([1085, 370, 1550, 400], fill=(15, 30, 40), outline=(0, 180, 220), width=1)
draw_a.rectangle([1088, 373, 1480, 397], fill=(0, 220, 180)) # 85% full bar
draw_e.rectangle([1088, 373, 1480, 397], fill=(0, 220, 180))
draw_a.text((1565, 375), "PNEUMATIC POWER: 86%", fill=(0, 220, 180), font=font_small)

draw_a.rectangle([1085, 415, 1550, 445], fill=(15, 30, 40), outline=(0, 180, 220), width=1)
draw_a.rectangle([1088, 418, 1430, 442], fill=(240, 180, 30)) # 75% full bar
draw_e.rectangle([1088, 418, 1430, 442], fill=(240, 180, 30))
draw_a.text((1565, 420), "SLAG FUNNEL CAPACITY: 74%", fill=(240, 180, 30), font=font_small)

# Waveform / status blip
points = []
for i in range(30):
    wx = 1750 + i * 8
    wy = 220 + math.sin(i * 0.8) * 25 + (15 if i % 6 == 0 else 0)
    points.append((wx, wy))
for i in range(len(points)-1):
    draw_a.line([points[i], points[i+1]], fill=(0, 255, 220), width=2)
    draw_e.line([points[i], points[i+1]], fill=(0, 255, 220), width=2)

# ==============================================================================
# SECTION 3: ANALOG PRESSURE GAUGE DIAL (UV: X 0..512, Y 512..1024)
# ==============================================================================
cx, cy, radius = 256, 768, 210
draw_a.ellipse([cx - radius - 15, cy - radius - 15, cx + radius + 15, cy + radius + 15], fill=(50, 54, 62), outline=(15, 17, 20), width=6)
draw_a.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(235, 238, 240), outline=(30, 35, 40), width=4)

# Gauge tick marks (240 degree sweep from 150 deg to 390 deg)
start_angle = 140
sweep = 260
for i in range(21):
    val = i * 25 # 0 to 500
    angle_rad = math.radians(start_angle + (i / 20.0) * sweep)
    x1 = cx + math.cos(angle_rad) * (radius - 10)
    y1 = cy + math.sin(angle_rad) * (radius - 10)
    tick_len = 25 if i % 4 == 0 else 12
    x2 = cx + math.cos(angle_rad) * (radius - 10 - tick_len)
    y2 = cy + math.sin(angle_rad) * (radius - 10 - tick_len)
    
    # Redline zone above 400 BAR (i >= 16)
    col = (220, 20, 20) if i >= 16 else (20, 25, 30)
    draw_a.line([(x1, y1), (x2, y2)], fill=col, width=4 if i % 4 == 0 else 2)
    
    if i % 4 == 0:
        tx = cx + math.cos(angle_rad) * (radius - 55) - 12
        ty = cy + math.sin(angle_rad) * (radius - 55) - 10
        draw_a.text((tx, ty), str(val), fill=col, font=font_small)

# Redline arc band
# Center text
draw_a.text((cx - 65, cy - 75), "PNEUMATIC", fill=(30, 40, 50), font=font_small)
draw_a.text((cx - 55, cy - 50), "PRESSURE", fill=(30, 40, 50), font=font_small)
draw_a.text((cx - 38, cy + 45), "BAR", fill=(200, 30, 30), font=font_med_b)
draw_a.text((cx - 65, cy + 75), "MAX 400 BAR", fill=(100, 110, 120), font=font_tiny)

# Indicator needle pointing to ~385 BAR
needle_val = 385.0
needle_angle = math.radians(start_angle + (needle_val / 500.0) * sweep)
nx = cx + math.cos(needle_angle) * (radius - 20)
ny = cy + math.sin(needle_angle) * (radius - 20)
draw_a.line([(cx, cy), (nx, ny)], fill=(220, 30, 20), width=5)
draw_e.line([(cx, cy), (nx, ny)], fill=(160, 20, 10), width=3)
# Center hub
draw_a.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(20, 22, 25), outline=(100, 105, 115), width=3)

# ==============================================================================
# SECTION 4: HAZARD WARNING CHEVRON STRIPES (UV: X 512..2048, Y 512..1024)
# ==============================================================================
# Long horizontal hazard stripe band (512, 512) to (2048, 768)
stripe_w = 40
draw_a.rectangle([520, 520, 2038, 750], fill=(235, 155, 10))
for sx in range(480, 2100, stripe_w * 2):
    pts = [
        (sx, 520),
        (sx + stripe_w, 520),
        (sx + stripe_w - 70, 750),
        (sx - 70, 750)
    ]
    draw_a.polygon(pts, fill=(20, 22, 25))

# Second hazard stripe band (narrow high-contrast border) (520, 760) to (2038, 860)
draw_a.rectangle([520, 765, 2038, 855], fill=(245, 180, 15))
for sx in range(480, 2100, 30 * 2):
    pts = [
        (sx, 765),
        (sx + 30, 765),
        (sx + 30 - 35, 855),
        (sx - 35, 855)
    ]
    draw_a.polygon(pts, fill=(15, 16, 18))

# Amber Beacon Texture Zone (UV: X 520..1024, Y 870..1020)
draw_a.rectangle([520, 870, 1020, 1020], fill=(255, 140, 0))
# Fresnel rings on amber beacon
for r in range(10, 70, 8):
    draw_a.ellipse([770 - r, 945 - r, 770 + r, 945 + r], outline=(255, 200, 50), width=3)
    draw_e.ellipse([770 - r, 945 - r, 770 + r, 945 + r], outline=(255, 180, 30), width=4)
draw_e.rectangle([520, 870, 1020, 1020], fill=(255, 120, 0))

# ==============================================================================
# SECTION 5: TECHNICAL STENCILS & BADGES (UV: X 0..2048, Y 1024..2048)
# ==============================================================================
# Slag Discharge Chute Placard
draw_plate(draw_a, 40, 1060, 980, 1480, fill=(30, 33, 38), border=(75, 80, 90), bevel=4)
draw_a.text((70, 1085), "PULVERIZED SLAG DISCHARGE CHUTE", fill=(240, 180, 40), font=font_large)
draw_a.text((70, 1145), "CORE OUTPUT // CONNECT HIGH-SPEED CONVEYOR BELT", fill=(220, 225, 230), font=font_med)
draw_a.text((70, 1190), "MATERIAL: PULVERIZED CORAL ORE (HIGH SILICA)", fill=(180, 230, 210), font=font_med)
draw_a.text((70, 1235), "GRAIN SIZE: 0.5 - 25.0 MM // FLUIDIZED FLOW", fill=(180, 190, 200), font=font_med)
draw_a.text((70, 1285), "▶ VIBRATION BAFFLES ACTIVE", fill=(80, 255, 140), font=font_med_b)
draw_e.text((70, 1285), "▶ VIBRATION BAFFLES ACTIVE", fill=(40, 180, 80), font=font_med_b)
draw_a.rectangle([70, 1340, 940, 1440], fill=(200, 140, 15))
draw_a.text((95, 1365), "DANGER: HIGH VELOCITY IMPACT SLAG // KEEP HANDS CLEAR", fill=(10, 10, 10), font=font_med_b)

# High Pressure Accumulator Tank Label (Tall Vertical Sign)
draw_plate(draw_a, 1040, 1060, 1500, 1980, fill=(26, 30, 36), border=(70, 75, 85), bevel=4)
draw_a.rectangle([1060, 1080, 1480, 1130], fill=(180, 30, 20))
draw_a.text((1080, 1090), "HIGH PRESSURE GAS", fill=(255, 255, 255), font=font_med_b)
draw_e.text((1080, 1090), "HIGH PRESSURE GAS", fill=(150, 20, 10), font=font_med_b)

draw_a.text((1075, 1160), "PNEUMATIC ACCUMULATOR", fill=(240, 240, 240), font=font_med_b)
draw_a.text((1075, 1205), "CORE PRESSURE: 400 BAR", fill=(240, 190, 30), font=font_large)
draw_e.text((1075, 1205), "CORE PRESSURE: 400 BAR", fill=(160, 120, 20), font=font_large)

draw_a.text((1075, 1270), "MEDIUM: NITROGEN GAS", fill=(180, 190, 200), font=font_med)
draw_a.text((1075, 1310), "VOLUME: 850 LITERS", fill=(180, 190, 200), font=font_med)
draw_a.text((1075, 1350), "BURST TEST: 650 BAR", fill=(180, 190, 200), font=font_med)
draw_a.text((1075, 1390), "SAFETY CODE: REG-9941-HP", fill=(180, 190, 200), font=font_med)

# Large vertical stencils
draw_a.text((1075, 1470), "PROJECT BLUE", fill=(0, 180, 240), font=font_huge)
draw_e.text((1075, 1470), "PROJECT BLUE", fill=(0, 140, 200), font=font_huge)
draw_a.text((1075, 1550), "SEABED DRILL", fill=(255, 255, 255), font=font_huge)
draw_a.text((1075, 1630), "DEEP EXTRACTION", fill=(200, 210, 220), font=font_large)

# Carbide Rotary Cutter Head Specs Placard
draw_plate(draw_a, 1540, 1060, 2010, 1980, fill=(28, 32, 38), border=(75, 80, 92), bevel=4)
draw_a.text((1565, 1090), "CARBIDE ROTARY HEAD", fill=(240, 180, 30), font=font_large)
draw_a.text((1565, 1145), "TUNGSTEN TEETH: 18x T-400", fill=(255, 255, 255), font=font_med_b)
draw_a.text((1565, 1190), "HARDNESS: 92 HRC CARBIDE", fill=(200, 210, 220), font=font_med)
draw_a.text((1565, 1230), "AUGER FLUTES: TRIPLE SPIRAL", fill=(200, 210, 220), font=font_med)
draw_a.text((1565, 1270), "CORE DIAMETER: 450 MM", fill=(200, 210, 220), font=font_med)
draw_a.text((1565, 1310), "ROTARY TORQUE: 18,500 NM", fill=(200, 210, 220), font=font_med)
draw_a.text((1565, 1350), "LUBRICATION: SEAWATER INJECT", fill=(180, 230, 255), font=font_med)

# Warning Symbol (Triangular Caution Sign)
tri_cx, tri_cy, tri_s = 1775, 1550, 130
pts = [
    (tri_cx, tri_cy - tri_s),
    (tri_cx + tri_s * 1.15, tri_cy + tri_s * 0.8),
    (tri_cx - tri_s * 1.15, tri_cy + tri_s * 0.8)
]
draw_a.polygon(pts, fill=(245, 180, 20), outline=(20, 22, 25))
draw_a.polygon([(tri_cx, tri_cy - tri_s + 20), (tri_cx + tri_s * 1.15 - 18, tri_cy + tri_s * 0.8 - 10), (tri_cx - tri_s * 1.15 + 18, tri_cy + tri_s * 0.8 - 10)], fill=(245, 180, 20), outline=(20, 22, 25), width=6)
# Exclamation mark
draw_a.rectangle([tri_cx - 8, tri_cy - 60, tri_cx + 8, tri_cy + 15], fill=(20, 22, 25))
draw_a.ellipse([tri_cx - 9, tri_cy + 35, tri_cx + 9, tri_cy + 53], fill=(20, 22, 25))

draw_a.text((1600, 1720), "HIGH VOLTAGE // IMPACT HAZARD", fill=(255, 200, 40), font=font_med_b)
draw_e.text((1600, 1720), "HIGH VOLTAGE // IMPACT HAZARD", fill=(180, 120, 20), font=font_med_b)
draw_a.text((1620, 1765), "DO NOT ENTER DRILL DERRICK", fill=(255, 255, 255), font=font_med)
draw_a.text((1640, 1800), "DURING ACTIVE EXTRACTION", fill=(255, 255, 255), font=font_med)

# Save images
out_dir = r"D:\Game\FishGame\Saved"
os.makedirs(out_dir, exist_ok=True)
albedo_path = os.path.join(out_dir, "T_SeabedDrill_Decals_D.png")
emissive_path = os.path.join(out_dir, "T_SeabedDrill_Decals_E.png")

albedo.save(albedo_path, format="PNG")
emissive.save(emissive_path, format="PNG")
print(f"Textures generated successfully!\n  Albedo: {albedo_path}\n  Emissive: {emissive_path}")
