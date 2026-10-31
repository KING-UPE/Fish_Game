import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"D:\Game\FishGame\Saved\DownloadedAssets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Stamped Geological Survey Tag Texture (1024x1024)
# -------------------------------------------------------------
def generate_survey_tag_texture():
    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (28, 30, 34, 255))
    draw = ImageDraw.Draw(img)

    # Outer border & bevel
    draw.rectangle([10, 10, W - 10, H - 10], outline=(70, 75, 82), width=6)
    draw.rectangle([25, 25, W - 25, H - 25], outline=(45, 48, 54), width=3)
    draw.rectangle([35, 35, W - 35, H - 35], fill=(36, 38, 42))

    # Corner mounting bolt plates
    bolt_radius = 22
    for bx, by in [(70, 70), (W - 70, 70), (70, H - 70), (W - 70, H - 70)]:
        draw.ellipse([bx - bolt_radius, by - bolt_radius, bx + bolt_radius, by + bolt_radius], fill=(20, 22, 24), outline=(80, 85, 95), width=3)
        draw.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(60, 65, 72))
        draw.line([bx - 10, by, bx + 10, by], fill=(15, 15, 18), width=3)

    # Top & bottom hazard stripe headers
    def draw_hazard_bar(y_start, height):
        stripe_w = 40
        for x in range(35, W - 35, stripe_w):
            poly = [(x, y_start), (min(x + stripe_w // 2, W - 35), y_start),
                    (min(x + stripe_w, W - 35), y_start + height), (x + stripe_w // 2, y_start + height)]
            draw.polygon([(x, y_start), (x + stripe_w, y_start), (x + stripe_w - height, y_start + height), (x - height, y_start + height)],
                         fill=(220, 175, 25))
            draw.polygon([(x + stripe_w, y_start), (x + 2 * stripe_w, y_start), (x + 2 * stripe_w - height, y_start + height), (x + stripe_w - height, y_start + height)],
                         fill=(25, 25, 28))

    draw.rectangle([35, 110, W - 35, 145], fill=(25, 25, 28))
    for x in range(35, W + 100, 50):
        draw.polygon([(x, 110), (x + 25, 110), (x - 10, 145), (x - 35, 145)], fill=(235, 180, 20))

    draw.rectangle([35, H - 150, W - 35, H - 115], fill=(25, 25, 28))
    for x in range(35, W + 100, 50):
        draw.polygon([(x, H - 150), (x + 25, H - 150), (x - 10, H - 115), (x - 35, H - 115)], fill=(235, 180, 20))

    # Header text box
    draw.rectangle([50, 170, W - 50, 240], fill=(20, 22, 25), outline=(60, 65, 75), width=2)
    
    # Try to load Arial or default font
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 24)
        font_main = ImageFont.truetype("arialbd.ttf", 46)
        font_stats = ImageFont.truetype("arialbd.ttf", 34)
        font_small = ImageFont.truetype("arial.ttf", 20)
        font_mono = ImageFont.truetype("courbd.ttf", 26)
    except Exception:
        font_header = font_sub = font_main = font_stats = font_small = font_mono = ImageFont.load_default()

    draw.text((70, 185), "PAPER KITE EXPEDITIONS // REG-9941", fill=(240, 242, 245), font=font_header)
    draw.text((700, 192), "GEOLOGICAL DIV.", fill=(235, 180, 20), font=font_sub)

    # Main Title Box
    draw.rectangle([50, 260, W - 50, 390], fill=(15, 17, 20), outline=(235, 180, 20), width=3)
    draw.rectangle([50, 260, 70, 390], fill=(235, 180, 20))
    draw.text((90, 275), "MAGNETITE SILT // HEAVY RESIDUE", fill=(255, 255, 255), font=font_main)
    draw.text((90, 335), "PROJECT BLUE // AUTOMATED EXTRACTION NODE", fill=(180, 190, 205), font=font_sub)

    # Data Grid
    boxes = [
        ("IRON FRACTION", "68.4 % wt.", 50, 420, 480, 530, (235, 180, 20)),
        ("SECTOR ASSIGNMENT", "SECTOR D-7", 520, 420, 970, 530, (80, 180, 240)),
        ("MINERAL PHASE", "Fe3O4 / FeTiO3 (ILMENITE)", 50, 550, 480, 660, (200, 210, 225)),
        ("SURVEY AUTHORITY", "KITE GEOLOGICAL", 520, 550, 970, 660, (235, 180, 20)),
        ("DENSITY CLASS", "5.17 g/cm3 [ULTRA-HEAVY]", 50, 680, 480, 790, (200, 210, 225)),
        ("RECOVERY PROTOCOL", "CONTINUOUS BUCKET SCOOP", 520, 680, 970, 790, (240, 120, 50)),
    ]

    for label, val, x1, y1, x2, y2, val_col in boxes:
        draw.rectangle([x1, y1, x2, y2], fill=(20, 22, 25), outline=(50, 55, 62), width=2)
        draw.text((x1 + 20, y1 + 15), label, fill=(130, 140, 155), font=font_small)
        draw.text((x1 + 20, y1 + 50), val, fill=val_col, font=font_stats)

    # Warning Box
    draw.rectangle([50, 810, W - 50, H - 170], fill=(45, 15, 15), outline=(220, 40, 40), width=2)
    draw.text((70, 825), "CAUTION: HIGH MAGNETIC FIELD // HEAVY MINERAL BED", fill=(255, 90, 90), font=font_header)
    draw.text((70, 868), "AUTHORIZED EXTRACTION MACHINERY ONLY -- WEAR RESPIRATORY FILTER", fill=(220, 220, 225), font=font_small)

    # Serial code & alignment markings
    draw.text((60, 55), "NODE-ID: MAG-9941-D7", fill=(160, 170, 185), font=font_mono)
    draw.text((W - 320, 55), "STATUS: SURVEYED / ACTIVE", fill=(80, 230, 120), font=font_mono)

    # Barcode representation
    random.seed(42)
    bx = 720
    by = H - 100
    for i in range(40):
        bw = random.choice([2, 4, 6, 8])
        draw.rectangle([bx, by, bx + bw, by + 35], fill=(220, 225, 235))
        bx += bw + random.choice([3, 5, 7])
    draw.text((720, H - 60), "SN-9941-MAG-68", fill=(140, 150, 165), font=font_small)

    out_path = os.path.join(OUTPUT_DIR, "T_BlackSand_SurveyTag.png")
    img.save(out_path)
    print("Saved Survey Tag Texture:", out_path)


# -------------------------------------------------------------
# 2. Hazard Stripe Texture (512x512)
# -------------------------------------------------------------
def generate_hazard_stripe_texture():
    W, H = 512, 512
    img = Image.new("RGBA", (W, H), (20, 20, 22, 255))
    draw = ImageDraw.Draw(img)

    stripe_w = 64
    for offset in range(-H, W + H, stripe_w * 2):
        poly = [
            (offset, 0),
            (offset + stripe_w, 0),
            (offset + stripe_w - H, H),
            (offset - H, H)
        ]
        draw.polygon(poly, fill=(245, 190, 15, 255))

    out_path = os.path.join(OUTPUT_DIR, "T_BlackSand_HazardStripe.png")
    img.save(out_path)
    print("Saved Hazard Stripe Texture:", out_path)


# -------------------------------------------------------------
# 3. Sparkling Magnetite Glitter & Normal Map (1024x1024)
# -------------------------------------------------------------
def generate_black_sand_detail_texture():
    W, H = 1024, 1024
    # Normal map with crystalline micro-facets and sand ripple waves
    normal_img = Image.new("RGBA", (W, H), (128, 128, 255, 255))
    normal_pixels = normal_img.load()

    # Glitter sparkle mask (R=Sparkle intensity, G=Facet variation, B=Wetness variation, A=255)
    sparkle_img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    sparkle_pixels = sparkle_img.load()

    random.seed(1337)
    # Pre-generate noise grid for smooth ripples
    grid_size = 64
    ripple_freq = 8.0

    print("Generating procedural micro-glitter and ripple maps...")
    for y in range(H):
        ny_norm = y / H
        for x in range(W):
            nx_norm = x / W

            # Dune ripple waves (diagonal primary ripples + secondary interference)
            rip1 = math.sin((nx_norm * 16.0 + ny_norm * 4.0) * math.pi * 2.0)
            rip2 = math.sin((nx_norm * 8.0 - ny_norm * 12.0) * math.pi * 2.0) * 0.4
            ripple = (rip1 + rip2) * 0.5

            # Crystalline grain micro-facets (high-frequency grain noise)
            grain_dx = (random.random() - 0.5) * 40.0
            grain_dy = (random.random() - 0.5) * 40.0

            # Normal vector perturbation
            dx = math.cos((nx_norm * 16.0 + ny_norm * 4.0) * math.pi * 2.0) * 25.0 + grain_dx
            dy = math.sin((nx_norm * 8.0 - ny_norm * 12.0) * math.pi * 2.0) * 15.0 + grain_dy

            nx = int(max(0, min(255, 128 + dx)))
            ny = int(max(0, min(255, 128 + dy)))
            nz = int(max(180, min(255, 255 - abs(dx) * 0.3 - abs(dy) * 0.3)))
            normal_pixels[x, y] = (nx, ny, nz, 255)

            # Sparkle / Glitter points (dense sparkling magnetite crystal flakes)
            is_sparkle = random.random() < 0.08
            sparkle_val = int(random.uniform(180, 255)) if is_sparkle else int(random.uniform(10, 45))
            wetness_val = int(220 + ripple * 30.0)
            facet_angle = int(random.uniform(0, 255))
            sparkle_pixels[x, y] = (sparkle_val, facet_angle, wetness_val, 255)

    norm_path = os.path.join(OUTPUT_DIR, "T_BlackSand_Normal.png")
    sparkle_path = os.path.join(OUTPUT_DIR, "T_BlackSand_Sparkle.png")
    normal_img.save(norm_path)
    sparkle_img.save(sparkle_path)
    print("Saved Normal Map:", norm_path)
    print("Saved Sparkle Map:", sparkle_path)

if __name__ == "__main__":
    generate_survey_tag_texture()
    generate_hazard_stripe_texture()
    generate_black_sand_detail_texture()
    print("ALL TEXTURES GENERATED SUCCESSFULLY!")
