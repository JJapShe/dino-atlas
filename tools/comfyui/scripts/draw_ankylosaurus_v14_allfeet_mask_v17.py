from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"

SOURCE = ASSETS / "ankylosaurus-magniventris-broadskull-i2i-v14.png"
MASK_OUT = OUTPUTS / "ankylosaurus_v14_allfeet_mask_v17.png"
SHEET_OUT = OUTPUTS / "ankylosaurus_v14_allfeet_mask_v17-sheet.png"


FOOT_POLYGONS = [
    # front near foot and toe fan
    [(250, 650), (420, 640), (535, 690), (520, 805), (315, 820), (220, 755)],
    # front far foot in shadow
    [(535, 650), (710, 640), (805, 690), (780, 815), (590, 820), (500, 745)],
    # rear far foot under body
    [(755, 620), (930, 615), (1025, 665), (1000, 785), (805, 795), (720, 720)],
    # rear near foot and toe fan
    [(1040, 620), (1240, 615), (1360, 685), (1320, 815), (1100, 825), (995, 730)],
]

TOE_STROKES = [
    [(275, 770), (505, 758)],
    [(560, 770), (765, 760)],
    [(790, 745), (990, 738)],
    [(1080, 765), (1320, 752)],
]


def make_mask():
    image = Image.open(SOURCE).convert("RGB")
    scale = 4
    mask = Image.new("L", (image.width * scale, image.height * scale), 0)
    draw = ImageDraw.Draw(mask)
    for polygon in FOOT_POLYGONS:
        draw.polygon([(x * scale, y * scale) for x, y in polygon], fill=255)
    for stroke in TOE_STROKES:
        draw.line([(x * scale, y * scale) for x, y in stroke], fill=255, width=28 * scale)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.2 * scale))
    mask = mask.resize(image.size, Image.Resampling.LANCZOS)
    MASK_OUT.parent.mkdir(parents=True, exist_ok=True)
    mask.convert("RGB").save(MASK_OUT)
    return image, mask


def make_sheet(image, mask):
    mask_l = mask.convert("L")
    overlay = image.convert("RGBA")
    red = Image.new("RGBA", image.size, (220, 42, 32, 0))
    red.putalpha(mask_l.point(lambda p: int(p * 0.60)))
    overlay = Image.alpha_composite(overlay, red).convert("RGB")
    crop_box = (170, 560, 1435, 850)
    items = [
        (image.crop(crop_box), "v14 feet crop"),
        (mask_l.convert("RGB").crop(crop_box), "all-feet mask"),
        (overlay.crop(crop_box), "masked feet overlay"),
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
    SHEET_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHEET_OUT)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    image, mask = make_mask()
    make_sheet(image, mask)
    print(MASK_OUT)
    print(SHEET_OUT)


if __name__ == "__main__":
    main()
