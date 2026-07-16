from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "herrerasaurus-ischigualastensis-strict-imagegen-alt-v1.png"
FIRST_PASS = ASSET_ROOT / "herrerasaurus-ischigualastensis-strict-imagegen-v1.png"
CLOSED_JAW_HEADBLEND = ASSET_ROOT / "herrerasaurus-ischigualastensis-closedjaw-headblend-v1.png"
LONG_ARMS = ASSET_ROOT / "herrerasaurus-ischigualastensis-longarms-ipcontrol-v1.png"
CLOSED_JAW = ASSET_ROOT / "herrerasaurus-ischigualastensis-closedjaw-refine-v1.png"
REVISED_GUIDE = ASSET_ROOT / "herrerasaurus-ischigualastensis-revisedguide-ipcontrol-v1.png"

CONTACT_OUT = ASSET_ROOT / "herrerasaurus-review-options-v6.png"
CROP_OUT = ASSET_ROOT / "herrerasaurus-strict-crops-v1.png"


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


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def make_contact_sheet():
    items = [
        {
            "path": SELECTED,
            "title": "selected imagegen alt v1: compact forelimbs",
            "note": "Best current Herrerasaurus read: narrow head, calm mouth, long tail, two hind legs, and smaller hands.",
        },
        {
            "path": FIRST_PASS,
            "title": "strict imagegen v1: stronger two-leg stance",
            "note": "Good tail and leg count, but the dangling hand claws are too long and need caution.",
        },
        {
            "path": CLOSED_JAW_HEADBLEND,
            "title": "previous primary: closed-jaw head blend",
            "note": "Preserved the old body gate, but forelimbs and head shape are weaker than the new imagegen pair.",
        },
        {
            "path": LONG_ARMS,
            "title": "long-arm IP-Control comparison",
            "note": "Useful long-forelimb gate; open mouth and head bulk made it less representative.",
        },
        {
            "path": CLOSED_JAW,
            "title": "closed-jaw comparison",
            "note": "Calmer head comparison, but body surface and hands remain too soft for first position.",
        },
        {
            "path": REVISED_GUIDE,
            "title": "revised guide IP-Control comparison",
            "note": "Structure comparison for early-saurischian silhouette, feet, and forelimb review.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 64
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image = Image.open(item["path"])
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("full selected body", SELECTED, (0, 0, 1536, 1024)),
        ("narrow closed mouth / head", SELECTED, (60, 285, 430, 540)),
        ("compact forelimbs / hands", SELECTED, (270, 465, 570, 760)),
        ("two hind legs / open feet", SELECTED, (560, 455, 970, 885)),
        ("long single tail", SELECTED, (760, 350, 1536, 620)),
        ("v1 long hand risk", FIRST_PASS, (900, 405, 1215, 735)),
        ("previous primary forelimbs", CLOSED_JAW_HEADBLEND, (700, 250, 1125, 650)),
        ("previous primary full body", CLOSED_JAW_HEADBLEND, (0, 0, 1152, 768)),
    ]

    cols = 2
    thumb_w = 360
    thumb_h = 250
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
    for path in (SELECTED, FIRST_PASS, CLOSED_JAW_HEADBLEND, LONG_ARMS, CLOSED_JAW, REVISED_GUIDE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
