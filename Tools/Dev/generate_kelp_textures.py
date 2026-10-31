import os
from PIL import Image, ImageDraw, ImageFont

def create_texture():
    W, H = 2048, 2048
    img = Image.new("RGBA", (W, H), (15, 18, 22, 255))
    draw = ImageDraw.Draw(img)

    # Helper fonts (fallback to default if specific ttf not found)
    try:
        font_huge = ImageFont.truetype("arialbd.ttf", 64)
        font_large = ImageFont.truetype("arialbd.ttf", 44)
        font_med = ImageFont.truetype("arialbd.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 24)
        font_tiny = ImageFont.truetype("arial.ttf", 18)
    except:
        font_huge = font_large = font_med = font_small = font_tiny = ImageFont.load_default()

    # SECTION 1: Top-Left (0, 0, 1024, 1024) -> Environmental Climate Monitoring Pod Screen
    # Background
    screen_rect = (40, 40, 984, 984)
    draw.rectangle(screen_rect, fill=(6, 16, 22, 255), outline=(0, 220, 160, 255), width=6)
    draw.rectangle((50, 50, 974, 974), fill=(8, 22, 30, 255), outline=(0, 120, 90, 255), width=2)

    # Screen Header Bar
    draw.rectangle((50, 50, 974, 130), fill=(0, 45, 40, 255))
    draw.text((70, 68), "PROJECT BLUE // BOTANY // HAB-04", fill=(0, 255, 180, 255), font=font_med)
    draw.text((720, 72), "[ LIVE MONITOR ]", fill=(100, 255, 200, 255), font=font_small)

    # Primary Title
    draw.text((80, 160), "GLOWKELP BIO-HAB", fill=(255, 255, 255, 255), font=font_huge)
    draw.text((80, 240), "AUTOMATED BIO-EXTRACTION & CULTIVATION", fill=(0, 220, 160, 255), font=font_med)

    # Main Metric Cards
    # Card 1: pH
    draw.rectangle((80, 310, 480, 470), fill=(12, 32, 40, 255), outline=(0, 180, 130, 255), width=3)
    draw.text((100, 325), "CONTAINMENT pH LEVEL", fill=(140, 210, 200, 255), font=font_small)
    draw.text((100, 360), "8.20", fill=(0, 255, 170, 255), font=font_huge)
    draw.text((320, 390), "pH [OPTIMAL]", fill=(100, 255, 150, 255), font=font_small)

    # Card 2: Salinity
    draw.rectangle((540, 310, 940, 470), fill=(12, 32, 40, 255), outline=(0, 180, 130, 255), width=3)
    draw.text((560, 325), "BRINE SALINITY", fill=(140, 210, 200, 255), font=font_small)
    draw.text((560, 360), "34.8", fill=(0, 255, 220, 255), font=font_huge)
    draw.text((740, 390), "PSU [3.5%]", fill=(100, 255, 200, 255), font=font_small)

    # Card 3: Nutrient Flow
    draw.rectangle((80, 500, 480, 660), fill=(12, 32, 40, 255), outline=(0, 150, 120, 255), width=2)
    draw.text((100, 515), "AEROPONIC MIST FLOW", fill=(140, 210, 200, 255), font=font_small)
    draw.text((100, 550), "124.5", fill=(0, 230, 255, 255), font=font_huge)
    draw.text((330, 580), "L / MIN", fill=(120, 230, 255, 255), font=font_small)

    # Card 4: Temperature
    draw.rectangle((540, 500, 940, 660), fill=(12, 32, 40, 255), outline=(0, 150, 120, 255), width=2)
    draw.text((560, 515), "CORE WATER TEMP", fill=(140, 210, 200, 255), font=font_small)
    draw.text((560, 550), "18.4 °C", fill=(0, 255, 180, 255), font=font_huge)
    draw.text((760, 580), "[NOMINAL]", fill=(100, 255, 150, 255), font=font_small)

    # Graph Section
    draw.rectangle((80, 690, 940, 850), fill=(10, 26, 34, 255), outline=(0, 100, 80, 255), width=2)
    draw.text((100, 705), "BIOLUMINESCENT EMISSION SPECTRUM (510nm CYCLING)", fill=(100, 200, 180, 255), font=font_tiny)
    # Draw simulated graph line
    import math
    pts = []
    for x in range(100, 920, 8):
        y = 780 - 45 * math.sin((x - 100) * 0.025) * math.cos((x - 100) * 0.012)
        pts.append((x, y))
    draw.line(pts, fill=(0, 255, 170, 255), width=3)

    # Status Footer
    draw.rectangle((80, 880, 940, 950), fill=(0, 60, 45, 255), outline=(0, 255, 180, 255), width=2)
    draw.text((100, 898), "SYSTEM: BIOMASS CULTIVATION CELL ACTIVE // STATUS: OPTIMAL", fill=(180, 255, 220, 255), font=font_med)

    # SECTION 2: Top-Right (1024, 0, 2048, 1024) -> Factory Stamped Decals
    # Decal A: White background with black/cyan text
    draw.rectangle((1080, 60, 1980, 280), fill=(240, 242, 245, 255), outline=(30, 35, 42, 255), width=8)
    draw.rectangle((1100, 80, 1140, 260), fill=(0, 180, 130, 255))
    draw.text((1170, 90), "PAPER KITE EXPEDITIONS // REG-9941", fill=(30, 35, 42, 255), font=font_large)
    draw.text((1170, 150), "PROJECT BLUE // AUTOMATED EXTRACTION", fill=(0, 140, 100, 255), font=font_med)
    draw.text((1170, 200), "FACILITY SECTOR 07 // DEEP WATER HARVESTING", fill=(80, 90, 100, 255), font=font_small)

    # Decal B: BIOMASS CULTIVATION CELL
    draw.rectangle((1080, 320, 1980, 520), fill=(240, 242, 245, 255), outline=(30, 35, 42, 255), width=8)
    draw.rectangle((1080, 320, 1980, 370), fill=(30, 35, 42, 255))
    draw.text((1110, 328), "HYDROPONIC GROWTH SYSTEM", fill=(255, 255, 255, 255), font=font_med)
    draw.text((1110, 390), "BIOMASS CULTIVATION CELL", fill=(15, 20, 25, 255), font=font_huge)
    draw.text((1110, 465), "SERIES 9-A // CAPACITY 1200L BRINE // GLOWKELP STRAIN 4", fill=(70, 80, 90, 255), font=font_small)

    # Decal C: STERILE ENVIRONMENT - CLASS 4
    draw.rectangle((1080, 560, 1980, 740), fill=(25, 30, 36, 255), outline=(0, 220, 160, 255), width=6)
    draw.text((1110, 580), "STERILE ENVIRONMENT // CLASS 4", fill=(0, 255, 180, 255), font=font_huge)
    draw.text((1110, 655), "AUTOMATED AEROPONIC ATOMIZERS IN CONTINUOUS OPERATION", fill=(200, 220, 220, 255), font=font_med)

    # Decal D: CAUTION HIGH PRESSURE / HIGH VOLTAGE
    draw.rectangle((1080, 780, 1980, 980), fill=(230, 160, 10, 255), outline=(20, 20, 20, 255), width=8)
    draw.rectangle((1100, 800, 1960, 960), fill=(20, 20, 20, 255))
    draw.text((1140, 815), "CAUTION: HIGH PRESSURE / HIGH VOLTAGE", fill=(255, 200, 20, 255), font=font_large)
    draw.text((1140, 875), "DEPRESSURIZE BRINE ACCUMULATOR BEFORE SERVICING", fill=(240, 240, 240, 255), font=font_med)
    draw.text((1140, 920), "AUTOMATIC DISCHARGE CYCLE ENGAGED EVERY 120 SECONDS", fill=(200, 170, 50, 255), font=font_small)

    # SECTION 3: Bottom-Left (0, 1024, 1024, 2048) -> Hazard Stripes & Technical Decals
    # Hazard Striping Panel (Diagonal Black and Yellow)
    stripe_w = 60
    for i in range(-500, 1500, stripe_w * 2):
        pts = [(i, 1050), (i + stripe_w, 1050), (i + stripe_w - 200, 1250), (i - 200, 1250)]
        clipped = [(max(40, min(984, x)), max(1050, min(1250, y))) for x, y in pts]
    # Simple crisp angled lines
    draw.rectangle((40, 1050, 984, 1250), fill=(235, 180, 15, 255))
    for x0 in range(-200, 1200, 80):
        draw.polygon([(x0, 1050), (x0 + 40, 1050), (x0 - 80, 1250), (x0 - 120, 1250)], fill=(20, 22, 25, 255))
    draw.rectangle((40, 1050, 984, 1250), outline=(10, 10, 10, 255), width=6)

    # Circular Pressure Gauge Dial Face (for SM_FluidTank)
    cx, cy, r = 300, 1550, 220
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(240, 242, 245, 255), outline=(30, 35, 40, 255), width=10)
    draw.ellipse((cx - r + 15, cy - r + 15, cx + r - 15, cy + r - 15), fill=(235, 238, 240, 255), outline=(80, 90, 100, 255), width=2)
    # Ticks
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        r_inner = r - (40 if deg % 30 == 0 else 25)
        x1 = cx + (r - 20) * math.cos(rad)
        y1 = cy + (r - 20) * math.sin(rad)
        x2 = cx + r_inner * math.cos(rad)
        y2 = cy + r_inner * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=(20, 25, 30, 255), width=(4 if deg % 30 == 0 else 2))
    draw.text((cx - 70, cy - 80), "BRINE", fill=(20, 30, 40, 255), font=font_med)
    draw.text((cx - 100, cy - 40), "PRESSURE", fill=(0, 140, 100, 255), font=font_small)
    draw.text((cx - 60, cy + 40), "BAR x 10", fill=(70, 80, 90, 255), font=font_small)
    # Dial needle pointing at 4.2 BAR
    n_rad = math.radians(220)
    draw.line([(cx, cy), (cx + (r - 50) * math.cos(n_rad), cy + (r - 50) * math.sin(n_rad))], fill=(210, 30, 20, 255), width=6)
    draw.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(40, 45, 50, 255))

    # Level Gauge Tube Strip (Vertical Sight Glass)
    draw.rectangle((650, 1320, 780, 1920), fill=(10, 25, 32, 255), outline=(50, 60, 70, 255), width=6)
    # Fluid filling 75%
    draw.rectangle((660, 1470, 770, 1910), fill=(0, 180, 140, 255))
    # Graduation marks
    for y in range(1340, 1910, 25):
        draw.line([(650, y), (680 if (y - 1340) % 100 == 0 else 665, y)], fill=(240, 250, 250, 255), width=3)
    draw.text((800, 1460), "75% - OPTIMAL LEVEL", fill=(0, 255, 180, 255), font=font_small)
    draw.text((800, 1500), "CHEM-9941 NUTRIENT", fill=(180, 200, 210, 255), font=font_small)

    # SECTION 4: Bottom-Right (1024, 1024, 2048, 2048) -> Large Markings & Brand
    draw.rectangle((1080, 1080, 1980, 1350), fill=(245, 245, 248, 255), outline=(40, 45, 50, 255), width=6)
    draw.text((1110, 1100), "GLOWKELP BIO-HAB // PH 8.2", fill=(10, 15, 20, 255), font=font_huge)
    draw.text((1110, 1190), "STATION 04 // PROJECT BLUE BOTANY", fill=(0, 160, 110, 255), font=font_large)
    draw.text((1110, 1260), "SATISFACTORY EXTRACTION STANDARD // CLASS A", fill=(80, 90, 100, 255), font=font_med)

    # Serial Plate
    draw.rectangle((1080, 1420, 1650, 1650), fill=(35, 40, 46, 255), outline=(120, 130, 140, 255), width=4)
    draw.text((1110, 1440), "SPECIFICATION PLATE", fill=(200, 210, 220, 255), font=font_small)
    draw.text((1110, 1480), "ASSET: KELP FARM AEROPONIC ARRAY", fill=(255, 255, 255, 255), font=font_med)
    draw.text((1110, 1530), "SERIAL: REG-9941-KF-004", fill=(0, 220, 160, 255), font=font_med)
    draw.text((1110, 1580), "POWER DRAW: 3.0 MW // BUFFER: 30 UNITS", fill=(180, 190, 200, 255), font=font_small)

    # LED Indicator Lights Panel
    draw.rectangle((1080, 1720, 1980, 1980), fill=(18, 22, 28, 255), outline=(60, 70, 80, 255), width=4)
    draw.text((1110, 1740), "AUTOMATION STATUS INDICATORS", fill=(180, 190, 200, 255), font=font_small)
    # LED 1: Green
    draw.ellipse((1120, 1800, 1170, 1850), fill=(0, 255, 120, 255), outline=(0, 180, 80, 255), width=3)
    draw.text((1190, 1812), "CIRCULATION PUMPS: ON", fill=(220, 255, 230, 255), font=font_med)
    # LED 2: Cyan
    draw.ellipse((1120, 1880, 1170, 1930), fill=(0, 220, 255, 255), outline=(0, 160, 200, 255), width=3)
    draw.text((1190, 1892), "NUTRIENT ATOMIZERS: PULSING", fill=(220, 245, 255, 255), font=font_med)

    out_path = r"D:\Game\FishGame\Saved\T_KelpFarm_Decals.png"
    img.save(out_path)
    print(f"Saved texture to {out_path} ({W}x{H})")

create_texture()
