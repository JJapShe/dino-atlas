from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SOURCE = ASSET_ROOT / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
MASK_OUT = OUTPUT_ROOT / "triceratops_v9_allfeet_mask_v21.png"
SHEET_OUT = OUTPUT_ROOT / "triceratops_v9_allfeet_mask_v21-sheet.png"


# Current v9 image is 1672x936. These polygons cover only the visible lower
# feet and toe tips; upper legs, body, head, frill, horns, beak, and tail stay
# locked during inpaint.
FOOT_POLYGONS = [
    # front visible foot under the left forelimb
    [(330, 665), (485, 654), (574, 700), (556, 782), (380, 792), (306, 742)],
    # shadowed rear/front-overlap foot just behind it
    [(545, 668), (682, 664), (742, 716), (708, 792), (570, 790), (518, 732)],
    # middle/rear foot cluster
    [(775, 662), (940, 652), (1035, 704), (1008, 798), (828, 802), (746, 738)],
    # far rear foot near tail-side leg
    [(1038, 662), (1188, 654), (1278, 706), (1255, 786), (1082, 798), (1008, 740)],
]

TOE_LINES = [
    # short strokes over toe-tip zones to bias separation without redrawing legs
    [(344, 754), (520, 744)],
    [(566, 752), (700, 746)],
    [(812, 762), (1000, 756)],
    [(1072, 762), (1245, 754)],
]


def make_mask(source, output):
    image = Image.open(source).convert("RGB")
    scale = 4
    mask = Image.new("L", (image.width * scale, image.height * scale), 0)
    draw = ImageDraw.Draw(mask)
    for polygon in FOOT_POLYGONS:
        draw.polygon([(x * scale, y * scale) for x, y in polygon], fill=255)
    for line in TOE_LINES:
        draw.line([(x * scale, y * scale) for x, y in line], fill=255, width=28 * scale)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.2 * scale))
    mask = mask.resize(image.size, Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    mask.convert("RGB").save(output)
    return output


def make_sheet(source, mask, output):
    image = Image.open(source).convert("RGB")
    mask_image = Image.open(mask).convert("L")
    overlay = image.convert("RGBA")
    red = Image.new("RGBA", image.size, (220, 42, 32, 0))
    red.putalpha(mask_image.point(lambda p: int(p * 0.62)))
    overlay = Image.alpha_composite(overlay, red).convert("RGB")
    crop_box = (250, 580, 1330, 840)

    items = [
        (image.crop(crop_box), "v9 feet crop"),
        (mask_image.convert("RGB").crop(crop_box), "all-feet mask"),
        (overlay.crop(crop_box), "masked overlay"),
        (overlay, "full-body overlay"),
    ]
    thumb_w, thumb_h, label_h = 430, 190, 38
    sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * 2), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (item, label) in enumerate(items):
        item = item.copy()
        item.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(item, ((thumb_w - item.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % 2) * thumb_w, (idx // 2) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    mask = make_mask(SOURCE, MASK_OUT)
    make_sheet(SOURCE, mask, SHEET_OUT)
    print(mask)
    print(SHEET_OUT)


if __name__ == "__main__":
    main()
