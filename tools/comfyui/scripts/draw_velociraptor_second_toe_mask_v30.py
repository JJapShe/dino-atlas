from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "assets/dinosaurs/velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
OUT_DIR = ROOT / "tools/comfyui/outputs"
ASSET_DIR = ROOT / "assets/dinosaurs"


def draw_mask(size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # V9-specific tight masks over the front raised second-toe claw base and
    # the rear foot toe cluster. Keep ankles/body untouched to avoid pose drift.
    draw.ellipse((598, 654, 692, 742), fill=255)
    draw.polygon([(584, 703), (668, 672), (707, 708), (648, 762), (573, 752)], fill=255)
    draw.ellipse((704, 723, 812, 782), fill=255)
    draw.polygon([(704, 746), (806, 724), (842, 754), (768, 798), (696, 782)], fill=255)

    return mask.filter(ImageFilter.GaussianBlur(2.2))


def make_overlay(source, mask):
    image = source.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 60, 45, 0))
    overlay.putalpha(mask.point(lambda value: min(150, value)))
    composed = Image.alpha_composite(image, overlay)

    draw = ImageDraw.Draw(composed)
    draw.rectangle((520, 610, 870, 830), outline=(255, 245, 80, 255), width=4)
    draw.text((532, 616), "v30 second-toe topology mask", fill=(255, 245, 80, 255))
    return composed.convert("RGB")


def make_crop_sheet(source, mask, overlay):
    crop_box = (500, 590, 900, 845)
    panels = [
        ("v9 foot source", source.crop(crop_box).convert("RGB")),
        ("v30 mask", Image.merge("RGB", (mask, mask, mask)).crop(crop_box)),
        ("v30 overlay", overlay.crop(crop_box)),
    ]
    panel_w, panel_h = 420, 300
    sheet = Image.new("RGB", (panel_w * len(panels), panel_h + 36), (238, 235, 226))
    for index, (label, image) in enumerate(panels):
        image.thumbnail((panel_w, panel_h))
        x = index * panel_w + (panel_w - image.width) // 2
        sheet.paste(image, (x, 0))
        draw = ImageDraw.Draw(sheet)
        draw.text((index * panel_w + 10, panel_h + 10), label, fill=(32, 30, 27))
    return sheet


def main():
    source = Image.open(SOURCE).convert("RGB")
    mask = draw_mask(source.size)
    overlay = make_overlay(source, mask)
    crop_sheet = make_crop_sheet(source, mask, overlay)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    mask.save(OUT_DIR / "velociraptor_second_toe_topology_v30_mask.png")
    overlay.save(OUT_DIR / "velociraptor_second_toe_topology_v30_mask_overlay.png")
    crop_sheet.save(OUT_DIR / "velociraptor_second_toe_topology_v30_mask_crop.png")
    mask.save(ASSET_DIR / "velociraptor-second-toe-i2i-mask-v30.png")
    crop_sheet.save(ASSET_DIR / "velociraptor-second-toe-mask-crop-v30.png")


if __name__ == "__main__":
    main()
