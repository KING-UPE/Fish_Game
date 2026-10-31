import os
from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGBA", (512, 512), (30, 35, 45, 255))
draw = ImageDraw.Draw(img)
draw.text((20, 20), "TEST DECAL", fill=(255, 255, 255, 255))
out_path = r"D:\Game\FishGame\Saved\DownloadedAssets\test_decal.png"
img.save(out_path)
print("Saved test decal to", out_path)
