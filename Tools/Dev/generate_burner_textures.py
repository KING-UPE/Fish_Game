import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TEXTURE_DIR = r"D:\Game\FishGame\Saved\BurnerTextures"
os.makedirs(TEXTURE_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. DECAL & SIGNAGE ATLAS (2048 x 2048)
# -------------------------------------------------------------
# Layout:
# [0, 0, 1024, 512]: Main Stamped Sign: "BIO-TURBINE // 30MW PRIME POWER"
# [0, 512, 1024, 1024]: Secondary Sign: "BIOMASS COMBUSTION 900°C" + "PAPER KITE EXPEDITIONS // REG-9941"
# [1024, 0, 2048, 512]: Digital Telemetry Screen: "GRID FEED 33kV // 30MW" + Bar Graphs + Status
# [1024, 512, 2048, 1024]: High Voltage Hazard Sign: "CAUTION: HIGH VOLTAGE / HIGH PRESSURE" + "PROJECT BLUE POWER"
# [0, 1024, 2048, 1536]: Yellow & Black Hazard Caution Stripes
# [0, 1536, 2048, 2048]: Technical Details: Serial plates, dial gauges, arrow indicators, bolt washers

def create_decal_atlas():
    w, h = 2048, 2048
    diffuse = Image.new("RGBA", (w, h), (25, 27, 30, 255)) # Dark industrial cast iron background
    emissive = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw_d = ImageDraw.Draw(diffuse)
    draw_e = ImageDraw.Draw(emissive)

    # Try to load a nice font, or fallback to default
    font_large = None
    font_med = None
    font_small = None
    font_tiny = None
    for fpath in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/consola.ttf"]:
        if os.path.exists(fpath):
            try:
                font_large = ImageFont.truetype(fpath, 56)
                font_med = ImageFont.truetype(fpath, 38)
                font_small = ImageFont.truetype(fpath, 26)
                font_tiny = ImageFont.truetype(fpath, 18)
                break
            except Exception:
                pass
    if not font_large:
        font_large = font_med = font_small = font_tiny = ImageFont.load_default()

    # --- PANEL 1: [0, 0, 1024, 512] "BIO-TURBINE // 30MW PRIME POWER" ---
    draw_d.rectangle([20, 20, 1004, 492], fill=(32, 34, 38, 255), outline=(70, 75, 82, 255), width=6)
    # Stamped header band (FICSIT Industrial Amber Orange)
    draw_d.rectangle([26, 26, 1000, 110], fill=(235, 130, 20, 255))
    draw_d.text((50, 45), "PROJECT BLUE POWER SYSTEMS", fill=(15, 15, 18, 255), font=font_med)
    draw_d.text((720, 50), "[REG-9941]", fill=(30, 30, 35, 255), font=font_small)

    # Main text
    draw_d.text((50, 140), "BIO-TURBINE GENERATOR", fill=(240, 242, 245, 255), font=font_large)
    draw_d.text((50, 215), "MODEL: BT-30M // PRIME CONTINUOUS POWER", fill=(180, 190, 205, 255), font=font_med)
    draw_d.text((50, 275), "RATED CAPACITY: 30.0 MW @ 3,000 RPM", fill=(235, 160, 40, 255), font=font_med)
    draw_d.text((50, 335), "PAPER KITE EXPEDITIONS // INDUSTRIAL DIV.", fill=(140, 145, 155, 255), font=font_small)
    draw_d.text((50, 380), "THERMAL CYCLE: SUPERCRITICAL BIOMASS STEAM", fill=(120, 125, 135, 255), font=font_small)
    draw_d.text((50, 420), "AUTOMATED EXTRACTION & POWER GRID FEED", fill=(100, 105, 115, 255), font=font_tiny)

    # Small warning icon box in panel 1
    draw_d.rectangle([820, 140, 980, 300], fill=(200, 30, 25, 255), outline=(240, 240, 240, 255), width=4)
    draw_d.text((845, 175), "30 MW", fill=(255, 255, 255, 255), font=font_large)
    draw_d.text((838, 245), "HIGH POWER", fill=(255, 255, 255, 255), font=font_tiny)

    # --- PANEL 2: [0, 512, 1024, 1024] "BIOMASS COMBUSTION 900°C" ---
    draw_d.rectangle([20, 532, 1004, 1004], fill=(30, 32, 36, 255), outline=(70, 75, 82, 255), width=6)
    # Danger header
    draw_d.rectangle([26, 538, 1000, 620], fill=(210, 45, 25, 255))
    draw_d.text((50, 555), "DANGER: HIGH TEMPERATURE COMBUSTION", fill=(255, 255, 255, 255), font=font_med)

    draw_d.text((50, 650), "BIOMASS COMBUSTION 900°C", fill=(255, 140, 30, 255), font=font_large)
    draw_d.text((50, 725), "OPERATING CORE TEMP: 900°C - 1,150°C", fill=(240, 240, 245, 255), font=font_med)
    draw_d.text((50, 780), "CHAMBER PRESSURE: 4.8 BAR // CLOSED FLUE", fill=(200, 205, 215, 255), font=font_med)
    draw_d.text((50, 835), "CAUTION: DO NOT OPEN SIGHT PORT DURING COMBUSTION", fill=(235, 180, 40, 255), font=font_small)
    draw_d.text((50, 880), "FUEL SPECIFICATION: DRIED GLOWKELP / BIOFUEL BRIQUETTES", fill=(140, 150, 160, 255), font=font_small)
    draw_d.text((50, 930), "EMISSIONS CONTROL: INTEGRATED SPARK ARRESTOR & CATALYST", fill=(110, 115, 125, 255), font=font_tiny)

    # Flame icon box
    draw_d.rectangle([820, 650, 980, 810], fill=(235, 120, 20, 255), outline=(255, 255, 255, 255), width=4)
    draw_d.text((840, 700), "900°C", fill=(20, 20, 20, 255), font=font_large)
    draw_d.text((850, 765), "THERMAL", fill=(20, 20, 20, 255), font=font_tiny)

    # --- PANEL 3: [1024, 0, 2048, 512] Digital Telemetry Screen ---
    draw_d.rectangle([1044, 20, 2028, 492], fill=(8, 14, 22, 255), outline=(0, 180, 220, 255), width=6)
    # Screen background with scanline feel
    for yline in range(26, 486, 6):
        draw_d.line([1048, yline, 2024, yline], fill=(12, 22, 32, 255), width=1)

    # Screen UI Header
    draw_d.text((1070, 40), "PAPER KITE EXPEDITIONS // REG-9941 // SCADA TELEMETRY", fill=(0, 220, 255, 255), font=font_small)
    draw_d.line([1070, 75, 2000, 75], fill=(0, 180, 220, 255), width=2)

    # Big digital readouts
    draw_d.text((1070, 95), "30.00 MW", fill=(0, 255, 180, 255), font=font_large)
    draw_d.text((1380, 110), "NET GRID FEED // 33 kV", fill=(0, 210, 240, 255), font=font_med)

    draw_d.text((1070, 175), "RPM: 3,000", fill=(255, 200, 50, 255), font=font_med)
    draw_d.text((1300, 175), "CORE TEMP: 900°C", fill=(255, 120, 30, 255), font=font_med)
    draw_d.text((1680, 175), "P_CHAMBER: 4.8 BAR", fill=(0, 220, 255, 255), font=font_med)

    # Bar graphs on screen
    # 1. Output Power Bar
    draw_d.rectangle([1070, 230, 1980, 260], fill=(15, 30, 45, 255), outline=(0, 160, 200, 255), width=2)
    draw_d.rectangle([1074, 234, 1940, 256], fill=(0, 220, 160, 255)) # 96% full
    draw_d.text((1070, 268), "POWER OUTPUT: [|||||||||||||||||||||||||||||||||||||||] 100% NOMINAL", fill=(0, 200, 150, 255), font=font_tiny)

    # 2. Fuel Feed Rate Bar
    draw_d.rectangle([1070, 305, 1980, 335], fill=(15, 30, 45, 255), outline=(0, 160, 200, 255), width=2)
    draw_d.rectangle([1074, 309, 1850, 331], fill=(235, 160, 30, 255)) # 85% full
    draw_d.text((1070, 343), "BIOFUEL INTAKE: [||||||||||||||||||||||||||||||||||] 8.5 kg/min", fill=(220, 160, 30, 255), font=font_tiny)

    # Status indicators
    draw_d.rectangle([1070, 390, 1320, 450], fill=(0, 80, 40, 255), outline=(0, 255, 120, 255), width=2)
    draw_d.text((1090, 405), "[ONLINE // SYNC]", fill=(0, 255, 120, 255), font=font_small)

    draw_d.rectangle([1350, 390, 1600, 450], fill=(0, 60, 80, 255), outline=(0, 200, 255, 255), width=2)
    draw_d.text((1370, 405), "[GRID FEED: OK]", fill=(0, 220, 255, 255), font=font_small)

    draw_d.rectangle([1630, 390, 1980, 450], fill=(60, 30, 10, 255), outline=(255, 150, 0, 255), width=2)
    draw_d.text((1650, 405), "[TURBINE: PURGE OK]", fill=(255, 180, 40, 255), font=font_small)

    # Screen Emissive Copy
    emissive.paste(diffuse.crop([1044, 20, 2028, 492]), (1044, 20))

    # --- PANEL 4: [1024, 512, 2048, 1024] High Voltage Warning & Lore ---
    draw_d.rectangle([1044, 532, 2028, 1004], fill=(30, 32, 36, 255), outline=(70, 75, 82, 255), width=6)
    # High Voltage Danger Header
    draw_d.rectangle([1050, 538, 2022, 620], fill=(220, 180, 20, 255))
    draw_d.text((1075, 555), "WARNING: HIGH VOLTAGE / HIGH PRESSURE", fill=(10, 10, 12, 255), font=font_med)

    draw_d.text((1075, 650), "HIGH VOLTAGE GRID FEED", fill=(240, 240, 245, 255), font=font_large)
    draw_d.text((1075, 725), "TRANSFORMER POTENTIAL: 33,000 VOLTS AC // 50 Hz", fill=(235, 180, 40, 255), font=font_med)
    draw_d.text((1075, 780), "BUSBAR TERMINAL BAY // AUTHORIZED TECHNICIANS ONLY", fill=(210, 215, 225, 255), font=font_med)
    draw_d.text((1075, 835), "PROJECT BLUE // AUTOMATED EXTRACTION INFRASTRUCTURE", fill=(0, 200, 240, 255), font=font_small)
    draw_d.text((1075, 880), "FICSIT INDUSTRIAL SYSTEM COMPLIANT // CLASS-4 POWER PLANT", fill=(140, 145, 155, 255), font=font_small)
    draw_d.text((1075, 930), "EMERGENCY DISCONNECT: USE EXTERNAL BUSBAR TRIP SWITCH", fill=(200, 60, 40, 255), font=font_tiny)

    # High voltage lightning icon box
    draw_d.rectangle([1840, 650, 2000, 810], fill=(220, 180, 20, 255), outline=(20, 20, 20, 255), width=4)
    draw_d.text((1860, 695), "33 kV", fill=(10, 10, 10, 255), font=font_large)
    draw_d.text((1875, 765), "DANGER", fill=(10, 10, 10, 255), font=font_tiny)

    # --- PANEL 5: [0, 1024, 2048, 1536] Caution Hazard Stripes ---
    stripe_w = 64
    for sx in range(-500, 2600, stripe_w * 2):
        # 45 degree yellow and black stripes
        poly = [
            (sx, 1024),
            (sx + stripe_w, 1024),
            (sx + stripe_w + 512, 1536),
            (sx + 512, 1536)
        ]
        draw_d.polygon(poly, fill=(235, 175, 15, 255))
        poly_black = [
            (sx + stripe_w, 1024),
            (sx + stripe_w * 2, 1024),
            (sx + stripe_w * 2 + 512, 1536),
            (sx + stripe_w + 512, 1536)
        ]
        draw_d.polygon(poly_black, fill=(18, 18, 20, 255))

    # Add border around hazard stripe band
    draw_d.rectangle([0, 1024, 2048, 1044], fill=(40, 42, 48, 255))
    draw_d.rectangle([0, 1516, 2048, 1536], fill=(40, 42, 48, 255))

    # --- PANEL 6: [0, 1536, 2048, 2048] Detail Labels, Plates & Gauges ---
    # Background
    draw_d.rectangle([0, 1536, 2048, 2048], fill=(28, 30, 34, 255))

    # Serial plate 1: [50, 1570, 600, 1750]
    draw_d.rectangle([50, 1570, 600, 1750], fill=(40, 44, 50, 255), outline=(120, 125, 135, 255), width=3)
    draw_d.text((70, 1590), "PAPER KITE EXPEDITIONS // SERIAL NO.", fill=(220, 220, 225, 255), font=font_small)
    draw_d.text((70, 1630), "SN: KB-9941-FICSIT-30MW", fill=(255, 200, 40, 255), font=font_large)
    draw_d.text((70, 1700), "ASSEMBLY SPEC: UE5-HEAVY-INDUSTRIAL-REV3", fill=(130, 135, 145, 255), font=font_tiny)

    # Dial gauge 1: Pressure Gauge [650, 1570, 850, 1770]
    draw_d.ellipse([650, 1570, 850, 1770], fill=(230, 230, 225, 255), outline=(30, 30, 35, 255), width=6)
    draw_d.ellipse([670, 1590, 830, 1750], fill=(245, 245, 240, 255), outline=(80, 80, 90, 255), width=2)
    draw_d.text((720, 1630), "BAR", fill=(20, 20, 25, 255), font=font_small)
    draw_d.text((710, 1700), "4.8", fill=(180, 20, 10, 255), font=font_med)
    draw_d.line([750, 1670, 785, 1625], fill=(200, 20, 10, 255), width=4) # needle

    # Dial gauge 2: Temperature Gauge [900, 1570, 1100, 1770]
    draw_d.ellipse([900, 1570, 1100, 1770], fill=(230, 230, 225, 255), outline=(30, 30, 35, 255), width=6)
    draw_d.ellipse([920, 1590, 1080, 1750], fill=(245, 245, 240, 255), outline=(80, 80, 90, 255), width=2)
    draw_d.text((975, 1630), "°C x100", fill=(20, 20, 25, 255), font=font_small)
    draw_d.text((975, 1700), "9.0", fill=(210, 90, 15, 255), font=font_med)
    draw_d.line([1000, 1670, 1035, 1625], fill=(220, 70, 10, 255), width=4) # needle

    # Pipe Flow Arrows [1150, 1570, 2000, 1750]
    draw_d.rectangle([1150, 1580, 1980, 1660], fill=(235, 130, 20, 255))
    draw_d.text((1180, 1600), ">>> EXHAUST GAS FLOW >>> NOX FILTERED >>>", fill=(10, 10, 10, 255), font=font_med)

    draw_d.rectangle([1150, 1670, 1980, 1750], fill=(0, 180, 220, 255))
    draw_d.text((1180, 1690), ">>> COOLANT INJECTION >>> PRE-HEATER STAGE >>>", fill=(10, 10, 10, 255), font=font_med)

    # Save Diffuse and Emissive
    diffuse_path = os.path.join(TEXTURE_DIR, "T_BurnerDecals_D.png")
    emissive_path = os.path.join(TEXTURE_DIR, "T_BurnerDecals_E.png")
    diffuse.save(diffuse_path)
    emissive.save(emissive_path)
    print(f"Saved decal textures to {diffuse_path} and {emissive_path}")

    # Generate Roughness / Metallic / Normal map
    # ORM: R=Occlusion, G=Roughness, B=Metallic
    # Cast iron: Roughness ~0.7 (180), Metallic ~0.4 (100)
    # Screens: Roughness ~0.15 (38), Metallic ~0.0 (0)
    # Painted plates: Roughness ~0.45 (115), Metallic ~0.2 (50)
    orm = Image.new("RGB", (w, h), (255, 160, 80)) # Base ORM
    draw_orm = ImageDraw.Draw(orm)
    # Screen area is glossy, non-metallic
    draw_orm.rectangle([1044, 20, 2028, 492], fill=(255, 35, 10))
    # Gauges are glass face
    draw_orm.ellipse([650, 1570, 850, 1770], fill=(255, 30, 10))
    draw_orm.ellipse([900, 1570, 1100, 1770], fill=(255, 30, 10))
    orm_path = os.path.join(TEXTURE_DIR, "T_BurnerDecals_ORM.png")
    orm.save(orm_path)
    print(f"Saved ORM texture to {orm_path}")

# -------------------------------------------------------------
# 2. SIGHT HOLE COMBUSTION GLOW TEXTURE (1024 x 1024)
# -------------------------------------------------------------
def create_combustion_texture():
    w, h = 1024, 1024
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    em = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    
    # Generate intense procedural turbulent fire core
    cx, cy = w // 2, h // 2
    r_max = w * 0.45

    y, x = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
    normalized_dist = np.clip(dist_from_center / r_max, 0, 1.0)

    # Plasma turbulent noise simulation
    noise = np.sin(x * 0.05 + np.cos(y * 0.04)) * np.cos(y * 0.05 + np.sin(x * 0.04))
    noise2 = np.sin(x * 0.12 - y * 0.08) * np.sin(y * 0.1 + x * 0.07)
    combustion_val = np.clip(1.0 - normalized_dist * 0.85 + (noise * 0.15 + noise2 * 0.1), 0, 1.0)
    
    # Edge falloff
    edge_alpha = np.clip((1.0 - normalized_dist) * 3.0, 0, 1.0)

    # Color gradient: White core -> Bright Yellow -> Vivid Orange -> Deep Cherry Red
    r = np.clip(combustion_val * 280, 0, 255).astype(np.uint8)
    g = np.clip(combustion_val**1.8 * 230, 0, 255).astype(np.uint8)
    b = np.clip(combustion_val**3.5 * 140, 0, 255).astype(np.uint8)
    a = (edge_alpha * 255).astype(np.uint8)

    rgba = np.stack([r, g, b, a], axis=-1)
    fire_img = Image.fromarray(rgba, mode="RGBA")
    fire_path = os.path.join(TEXTURE_DIR, "T_CombustionSight_D.png")
    fire_img.save(fire_path)

    # Intense Emissive
    em_r = np.clip(combustion_val * 320, 0, 255).astype(np.uint8)
    em_g = np.clip(combustion_val**2.0 * 240, 0, 255).astype(np.uint8)
    em_b = np.clip(combustion_val**4.0 * 160, 0, 255).astype(np.uint8)
    em_rgba = np.stack([em_r, em_g, em_b, a], axis=-1)
    em_img = Image.fromarray(em_rgba, mode="RGBA")
    em_path = os.path.join(TEXTURE_DIR, "T_CombustionSight_E.png")
    em_img.save(em_path)
    print(f"Saved combustion textures to {fire_path} and {em_path}")

# -------------------------------------------------------------
# 3. SPARK ARRESTOR MESH TEXTURE (512 x 512)
# -------------------------------------------------------------
def create_spark_mesh_texture():
    w, h = 512, 512
    # Perforated metal / heavy wire screen
    mesh = Image.new("RGBA", (w, h), (18, 18, 20, 255))
    draw = ImageDraw.Draw(mesh)
    
    # Hexagonal / round perforation pattern
    step = 32
    radius = 11
    for row in range(-1, (h // step) + 2):
        y = row * step
        x_offset = (step // 2) if (row % 2 == 1) else 0
        for col in range(-1, (w // step) + 2):
            x = col * step + x_offset
            # Dark open hole
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(5, 5, 6, 255), outline=(45, 45, 50, 255), width=2)
            # Center subtle thermal glow inside the hole
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(60, 25, 10, 255))

    mesh_path = os.path.join(TEXTURE_DIR, "T_SparkArrestor_D.png")
    mesh.save(mesh_path)
    print(f"Saved spark arrestor texture to {mesh_path}")

if __name__ == "__main__":
    create_decal_atlas()
    create_combustion_texture()
    create_spark_mesh_texture()
    print("All textures created successfully!")
