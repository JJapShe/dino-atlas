from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-clearfeet-singleclub-imagegen-v4.png"
WIDESKULL = ASSET_ROOT / "ankylosaurus-magniventris-wideskull-club-imagegen-v4.png"
PREVIOUS_SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-widearmor-imagegen-v3.png"
WIDEARMOR_V3 = ASSET_ROOT / "ankylosaurus-magniventris-widearmor-comparison-imagegen-v3.png"
LOWCOMPACT_V2 = ASSET_ROOT / "ankylosaurus-magniventris-lowcompact-imagegen-v2.png"
TAILCLUB_REJECTION = ASSET_ROOT / "ankylosaurus-magniventris-tailclub-surface-v1.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v9.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-clearfeet-singleclub-crops-v4.png"


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
            "title": "selected imagegen v4: clear feet / single club",
            "note": "Best current app read: four open feet, dense armor rows, broad low body, and one attached oval tail club.",
        },
        {
            "path": WIDESKULL,
            "title": "v4 comparison: wide skull / club",
            "note": "Useful skull and club comparison, but the torso reads rounder and less compact at app scale.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: wide-armor v3",
            "note": "Strong armor identity and club read, but feet are less separated and the head is softer at close review.",
        },
        {
            "path": WIDEARMOR_V3,
            "title": "v3 longer-body comparison",
            "note": "Readable armor and club, but the longer body/tail read is weaker than selected v4.",
        },
        {
            "path": LOWCOMPACT_V2,
            "title": "older low-compact v2",
            "note": "Useful low-body comparison; v4 improves open feet and app-scale club readability.",
        },
        {
            "path": TAILCLUB_REJECTION,
            "title": "tail-club surface rejection",
            "note": "Failure gate: keep out low generic lizard/crocodile reads even when the club is visible.",
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
        ("selected full body", SELECTED, (0, 0, 1774, 887)),
        ("selected compact armored skull", SELECTED, (40, 285, 470, 560)),
        ("selected armor rows", SELECTED, (360, 210, 1165, 520)),
        ("selected single attached club", SELECTED, (1280, 310, 1715, 565)),
        ("selected front feet", SELECTED, (270, 585, 690, 800)),
        ("selected rear feet", SELECTED, (865, 585, 1250, 805)),
        ("v4 comparison round-torso risk", WIDESKULL, (0, 0, 1774, 887)),
        ("previous v3 head / foot risk", PREVIOUS_SELECTED, (0, 0, 1536, 1024)),
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
    for path in (
        SELECTED,
        WIDESKULL,
        PREVIOUS_SELECTED,
        WIDEARMOR_V3,
        LOWCOMPACT_V2,
        TAILCLUB_REJECTION,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
