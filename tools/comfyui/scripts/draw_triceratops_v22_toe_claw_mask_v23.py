from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "assets/dinosaurs/triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
OUT_DIR = ROOT / "tools/comfyui/outputs"
ASSET_DIR = ROOT / "assets/dinosaurs"


def draw_mask(size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # V22-specific tiny masks over bright claw highlights only. Avoid masking
    # full toes so the successful all-feet topology is preserved.
    ellipses = [
        (430, 742, 462, 780),
        (472, 735, 510, 778),
        (515, 736, 552, 780),
        (606, 740, 638, 784),
        (644, 735, 680, 784),
        (686, 735, 724, 780),
        (896, 731, 930, 770),
        (940, 728, 978, 772),
        (982, 730, 1020, 772),
        (1110, 720, 1142, 758),
        (1152, 722, 1188, 762),
    ]
    for box in ellipses:
        draw.ellipse(box, fill=255)

    return mask.filter(ImageFilter.GaussianBlur(1.6))


def make_overlay(source, mask):
    image = source.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 70, 40, 0))
    overlay.putalpha(mask.point(lambda value: min(150, value)))
    composed = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(composed)
    draw.rectangle((380, 690, 1225, 810), outline=(255, 245, 90, 255), width=3)
    draw.text((392, 696), "v23 toe-claw highlight mask", fill=(255, 245, 90, 255))
    return composed.convert("RGB")


def make_crop_sheet(source, mask, overlay):
    crop_box = (360, 675, 1245, 825)
    panels = [
        ("v22 foot source", source.crop(crop_box).convert("RGB")),
        ("v23 tiny claw mask", Image.merge("RGB", (mask, mask, mask)).crop(crop_box)),
        ("v23 overlay", overlay.crop(crop_box)),
    ]
    panel_w, panel_h = 430, 160
    sheet = Image.new("RGB", (panel_w * len(panels), panel_h + 36), (238, 235, 226))
    for index, (label, image) in enumerate(panels):
        image.thumbnail((panel_w, panel_h), Image.Resampling.LANCZOS)
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
    mask.save(OUT_DIR / "triceratops_v22_toe_claw_highlight_mask_v23.png")
    overlay.save(OUT_DIR / "triceratops_v22_toe_claw_highlight_overlay_v23.png")
    crop_sheet.save(OUT_DIR / "triceratops_v22_toe_claw_highlight_mask_crop_v23.png")
    mask.save(ASSET_DIR / "triceratops-toe-claw-highlight-i2i-mask-v23.png")
    crop_sheet.save(ASSET_DIR / "triceratops-toe-claw-highlight-mask-crop-v23.png")


if __name__ == "__main__":
    main()
