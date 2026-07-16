from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "allosaurus-fragilis-lowbrow-threefinger-imagegen-v3.png"
REVIEWABLE = ASSET_ROOT / "allosaurus-fragilis-reviewable-threefinger-imagegen-v3.png"
MEDIUMARM = ASSET_ROOT / "allosaurus-fragilis-mediumarm-threefinger-imagegen-v3.png"
PREVIOUS = ASSET_ROOT / "allosaurus-fragilis-compacthands-imagegen-v2.png"
SUBTLEBROW = ASSET_ROOT / "allosaurus-fragilis-subtlebrow-imagegen-v2.png"
STRICT = ASSET_ROOT / "allosaurus-fragilis-strict-imagegen-v1.png"
OPENFEET = ASSET_ROOT / "allosaurus-fragilis-openfeet-imagegen-v1.png"

CONTACT_OUT = ASSET_ROOT / "allosaurus-review-options-v8.png"
CROP_OUT = ASSET_ROOT / "allosaurus-lowbrow-threefinger-crops-v3.png"


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
            "title": "selected v3: low brow / three-finger hands",
            "note": "Best current Allosaurus read: longer three-finger arms, full tail, open feet, and calm mouth.",
        },
        {
            "path": REVIEWABLE,
            "title": "v3 reviewable-hand comparison",
            "note": "Strong hands and body, but the paired brow bumps read more horn-like.",
        },
        {
            "path": MEDIUMARM,
            "title": "v3 medium-arm comparison",
            "note": "Good arms, but the open mouth and teeth read more monster-like.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v2",
            "note": "Stable full-body read, but hands became too compact and less allosaur-like.",
        },
        {
            "path": SUBTLEBROW,
            "title": "v2 subtle-brow comparison",
            "note": "Calmer brow, but hand/arm readability is weaker than selected v3.",
        },
        {
            "path": STRICT,
            "title": "v1 strict comparison",
            "note": "Clear side profile, but brow and hand length are more dramatic.",
        },
        {
            "path": OPENFEET,
            "title": "open-feet comparison",
            "note": "Useful foot gate retained below newer hand/brow candidates.",
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
        ("selected v3 full body", SELECTED, (0, 0, 1672, 940)),
        ("selected v3 low brow / no nose horn", SELECTED, (50, 175, 465, 355)),
        ("selected v3 medium forelimbs", SELECTED, (355, 385, 610, 690)),
        ("selected v3 three-finger hand", SELECTED, (390, 500, 610, 705)),
        ("selected v3 hind feet / toes", SELECTED, (610, 685, 1070, 895)),
        ("selected v3 full tail", SELECTED, (810, 360, 1665, 600)),
        ("v3 reviewable-hand horn-risk", REVIEWABLE, (50, 170, 620, 700)),
        ("v3 medium-arm open-mouth risk", MEDIUMARM, (45, 170, 620, 705)),
        ("previous v2 full body", PREVIOUS, (0, 0, 1774, 887)),
        ("previous v2 compact-hand comparison", PREVIOUS, (340, 355, 610, 660)),
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
    for path in (SELECTED, REVIEWABLE, MEDIUMARM, PREVIOUS, SUBTLEBROW, STRICT, OPENFEET):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
