from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png"
LOWHORN = ASSET_ROOT / "allosaurus-fragilis-lowhorn-threefinger-comparison-v4.png"
RIDGEHAND = ASSET_ROOT / "allosaurus-fragilis-ridgehand-comparison-v4.png"
PREVIOUS = ASSET_ROOT / "allosaurus-fragilis-lowbrow-threefinger-imagegen-v3.png"
PREVIOUS_CROP = ASSET_ROOT / "allosaurus-lowbrow-threefinger-crops-v3.png"
REVIEWABLE = ASSET_ROOT / "allosaurus-fragilis-reviewable-threefinger-imagegen-v3.png"
MEDIUMARM = ASSET_ROOT / "allosaurus-fragilis-mediumarm-threefinger-imagegen-v3.png"
COMPACT = ASSET_ROOT / "allosaurus-fragilis-compacthands-imagegen-v2.png"

CONTACT_OUT = ASSET_ROOT / "allosaurus-review-options-v9.png"
CROP_OUT = ASSET_ROOT / "allosaurus-smoothbrow-threefinger-crops-v4.png"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (236, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, font, fill, max_chars=58, line_h=15, max_lines=2):
    x, y = xy
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * line_h), line, fill=fill, font=font)


def make_contact_sheet():
    items = [
        {
            "path": SELECTED,
            "title": "selected v4: smoother brow / three-finger gate",
            "note": "Best current brow silhouette; keeps full tail, open feet, and medium allosaur forelimbs.",
        },
        {
            "path": LOWHORN,
            "title": "v4 low-horn comparison",
            "note": "Useful body and hands, but paired brow bumps still read horn-like at close review.",
        },
        {
            "path": RIDGEHAND,
            "title": "v4 ridge-hand comparison",
            "note": "Clear feet and tail, but dorsal/brow texture is more dramatic and hands are softer.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v3",
            "note": "Stronger hand readability, but the brow ridge is higher than selected v4.",
        },
        {
            "path": REVIEWABLE,
            "title": "v3 reviewable-hand comparison",
            "note": "Very readable hand gate, retained as a close comparison for exact finger count.",
        },
        {
            "path": MEDIUMARM,
            "title": "v3 medium-arm comparison",
            "note": "Good arms, but the mouth and teeth read more monster-like.",
        },
        {
            "path": COMPACT,
            "title": "previous compact-hand v2",
            "note": "Stable full-body gate with less readable hands than the v3/v4 candidates.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v3 crop audit",
            "note": "Kept below v4 to compare old brow and stronger hand readability.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 242
    label_h = 66
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image = Image.open(item["path"])
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 29), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v4 full body", SELECTED, (0, 0, 1774, 887)),
        ("selected v4 smooth low brow", SELECTED, (45, 135, 480, 335)),
        ("selected v4 medium forelimbs", SELECTED, (340, 335, 620, 610)),
        ("selected v4 three-finger hand gate", SELECTED, (395, 420, 575, 615)),
        ("selected v4 hind feet / toes", SELECTED, (530, 615, 1035, 825)),
        ("selected v4 full tail", SELECTED, (805, 250, 1765, 510)),
        ("v4 low-horn brow risk", LOWHORN, (35, 135, 475, 345)),
        ("v4 low-horn hand comparison", LOWHORN, (380, 415, 600, 625)),
        ("v4 ridge-hand brow risk", RIDGEHAND, (45, 150, 520, 360)),
        ("previous v3 brow comparison", PREVIOUS, (50, 175, 465, 355)),
        ("previous v3 hand comparison", PREVIOUS, (390, 500, 610, 705)),
        ("previous v3 foot comparison", PREVIOUS, (610, 685, 1070, 895)),
    ]

    cols = 2
    thumb_w = 380
    thumb_h = 236
    label_h = 36
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (label, path, box) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def main():
    for path in (SELECTED, LOWHORN, RIDGEHAND, PREVIOUS, PREVIOUS_CROP, REVIEWABLE, MEDIUMARM, COMPACT):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
