from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "apatosaurus-ajax-smallhead-imagegen-v2.png"
OPEN_FEET = ASSET_ROOT / "apatosaurus-ajax-openfeet-imagegen-v2.png"
PREVIOUS_SELECTED = ASSET_ROOT / "apatosaurus-ajax-lowneck-imagegen-v1.png"
EDGE_VOLUME = ASSET_ROOT / "apatosaurus-ajax-edge-volume-v1.png"
FLOODPLAIN = ASSET_ROOT / "apatosaurus-ajax-lowneck-floodplain-v1.png"
HIGH_NECK_REJECTION = ASSET_ROOT / "apatosaurus-ajax-lowneck-ipcontrol-v1.png"

CONTACT_OUT = ASSET_ROOT / "apatosaurus-review-options-v5.png"
CROP_OUT = ASSET_ROOT / "apatosaurus-smallhead-crops-v2.png"


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
            "title": "selected imagegen v2: small head / low neck",
            "note": "Best current app read: small blunt head, low forward neck, full tail, and four open feet.",
        },
        {
            "path": OPEN_FEET,
            "title": "v2 comparison: stronger foot hints",
            "note": "Good open feet and toe hints, but the head/neck read is heavier than selected v2.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: low-neck imagegen v1",
            "note": "Strong low-neck gate, but feet are more column-like and the head is less clean.",
        },
        {
            "path": EDGE_VOLUME,
            "title": "edge-volume polish comparison",
            "note": "Useful low-neck comparison, but feet sit behind a foreground rise.",
        },
        {
            "path": FLOODPLAIN,
            "title": "low-neck floodplain comparison",
            "note": "Structure preservation comparison with flatter body and pale-edge residue.",
        },
        {
            "path": HIGH_NECK_REJECTION,
            "title": "rejected: high-neck IP-Control drift",
            "note": "Natural texture comparison, but hidden legs and high-neck drift fail the app gate.",
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
        ("selected small head / low neck", SELECTED, (65, 270, 540, 430)),
        ("selected forequarters / front feet", SELECTED, (470, 435, 760, 725)),
        ("selected four pillar legs / feet", SELECTED, (460, 430, 1080, 760)),
        ("selected full tail", SELECTED, (930, 310, 1774, 535)),
        ("openfeet v2 foot hints", OPEN_FEET, (650, 470, 1130, 750)),
        ("previous primary head/neck", PREVIOUS_SELECTED, (0, 260, 560, 555)),
        ("previous primary column feet", PREVIOUS_SELECTED, (385, 510, 990, 910)),
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
    for path in (SELECTED, OPEN_FEET, PREVIOUS_SELECTED, EDGE_VOLUME, FLOODPLAIN, HIGH_NECK_REJECTION):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
