import os
from PIL import Image, ImageDraw, ImageFont
import unreal

# Generate a small test texture
img_dir = r"D:\Game\FishGame\Saved\TempTextures"
os.makedirs(img_dir, exist_ok=True)
img_path = os.path.join(img_dir, "T_TestDecal.png")

img = Image.new("RGBA", (256, 256), (30, 35, 40, 255))
draw = ImageDraw.Draw(img)
draw.rectangle([10, 10, 246, 246], outline=(255, 180, 0, 255), width=4)
draw.text((20, 30), "TEST DECAL", fill=(255, 255, 255, 255))
img.save(img_path)

tools = unreal.AssetToolsHelpers.get_asset_tools()
task = unreal.AssetImportTask()
task.filename = img_path
task.destination_path = "/Game/Blue/Materials"
task.destination_name = "T_TestDecal"
task.replace_existing = True
task.automated = True
task.save = True

tools.import_asset_tasks([task])
tex = unreal.load_object(None, "/Game/Blue/Materials/T_TestDecal.T_TestDecal")
print("Imported texture:", tex)
