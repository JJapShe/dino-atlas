from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "assets/dinosaurs/stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
OUT_DIR = ROOT / "tools/comfyui/outputs"
ASSET_DIR = ROOT / "assets/dinosaurs"


def draw_mask(size):
    w, h = size
    sx = w / 1672
    sy = h / 940

    def p(points):
        return [(int(x * sx), int(y * sy)) for x, y in points]

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # V6-specific dorsal row mask. It touches each plate separately plus a
    # narrow attachment band, avoiding a large sky arch that would invite drift.
    plates = [
        (250, 370, 34, 94),
        (305, 320, 48, 122),
        (380, 270, 64, 145),
        (470, 215, 80, 172),
        (580, 170, 92, 196),
        (704, 150, 100, 210),
        (832, 150, 104, 212),
        (958, 184, 98, 194),
        (1078, 254, 84, 170),
        (1180, 334, 66, 130),
        (1272, 414, 48, 96),
    ]
    for cx, cy, rx, ry in plates:
        draw.ellipse((int((cx - rx) * sx), int((cy - ry) * sy), int((cx + rx) * sx), int((cy + ry) * sy)), fill=255)

    base_band = [
        (226, 466),
        (345, 424),
        (485, 378),
        (636, 352),
        (790, 350),
        (950, 380),
        (1108, 432),
        (1298, 508),
        (1290, 548),
        (1100, 488),
        (940, 434),
        (786, 406),
        (640, 404),
        (500, 430),
        (356, 470),
        (236, 506),
    ]
    draw.polygon(p(base_band), fill=255)

    # Keep a slightly softer edge where the mask meets the main body.
    return mask.filter(ImageFilter.GaussianBlur(2.4))


def make_overlay(source, mask):
    image = source.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 68, 36, 0))
    overlay.putalpha(mask.point(lambda value: min(150, value)))
    composed = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(composed)
    draw.rectangle((210, 70, 1340, 530), outline=(255, 245, 80, 255), width=4)
    draw.text((225, 88), "v69 dorsal plate row mask", fill=(255, 245, 80, 255), font=ImageFont.load_default())
    return composed.convert("RGB")


def make_crop_sheet(source, mask, overlay):
    crop_box = (170, 50, 1390, 570)
    panels = [
        ("v6 plate source", source.crop(crop_box).convert("RGB")),
        ("v69 mask", Image.merge("RGB", (mask, mask, mask)).crop(crop_box)),
        ("v69 overlay", overlay.crop(crop_box)),
    ]
    panel_w, panel_h = 420, 230
    label_h = 34
    sheet = Image.new("RGB", (panel_w * len(panels), panel_h + label_h), (238, 235, 226))
    draw = ImageDraw.Draw(sheet)
    for index, (label, image) in enumerate(panels):
        image.thumbnail((panel_w, panel_h))
        x = index * panel_w + (panel_w - image.width) // 2
        sheet.paste(image, (x, 0))
        draw.text((index * panel_w + 10, panel_h + 10), label, fill=(32, 30, 27), font=ImageFont.load_default())
    return sheet


def main():
    source = Image.open(SOURCE).convert("RGB")
    mask = draw_mask(source.size)
    overlay = make_overlay(source, mask)
    crop_sheet = make_crop_sheet(source, mask, overlay)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    mask.save(OUT_DIR / "stegosaurus_plate_row_v69_mask.png")
    overlay.save(OUT_DIR / "stegosaurus_plate_row_v69_mask_overlay.png")
    crop_sheet.save(OUT_DIR / "stegosaurus_plate_row_v69_mask_crop.png")
    mask.save(ASSET_DIR / "stegosaurus-plate-row-i2i-mask-v69.png")
    crop_sheet.save(ASSET_DIR / "stegosaurus-plate-row-mask-crop-v69.png")
    print(ASSET_DIR / "stegosaurus-plate-row-i2i-mask-v69.png")


if __name__ == "__main__":
    main()
