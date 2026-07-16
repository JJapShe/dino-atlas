from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "stegosaurus-stenops-strict-plates-imagegen-v1.png"
TAILROOM = ASSET_ROOT / "stegosaurus-stenops-tailroom-fourspike-imagegen-v2.png"
BROADPLATE = ASSET_ROOT / "stegosaurus-stenops-broadplate-fourspike-imagegen-v2.png"
FIRST_PASS = ASSET_ROOT / "stegosaurus-stenops-plate-thagomizer-imagegen-v1.png"
SOFTCLEAN = ASSET_ROOT / "stegosaurus-stenops-thagomizer-softclean-v1.png"
PLATE_REFERENCE = ASSET_ROOT / "stegosaurus-stenops-plate-thagomizer-reference-v1.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-review-options-v41.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-fourspike-crops-v2.png"


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
            "title": "selected v1: keep first for now",
            "note": "Still the best balance of low body, separated plates, open feet, and readable tail spikes.",
        },
        {
            "path": TAILROOM,
            "title": "v2 tail-room comparison: not promoted",
            "note": "More tail-tip room, but spike count remains visually ambiguous and plates keep a leaf-like surface.",
        },
        {
            "path": BROADPLATE,
            "title": "v2 broad-plate comparison: not promoted",
            "note": "Clean full body, but thagomizer count and plate texture are not clearly better than selected v1.",
        },
        {
            "path": FIRST_PASS,
            "title": "first imagegen pass: extra-spike risk",
            "note": "Strong plate row and stance, but the tail tip may read as more than four spikes.",
        },
        {
            "path": SOFTCLEAN,
            "title": "previous primary: soft-clean",
            "note": "Useful plate gate, but body/leg proportions and tail-tip artifacts stay weaker.",
        },
        {
            "path": PLATE_REFERENCE,
            "title": "plate + thagomizer reference",
            "note": "Project-owned diagnostic target for future Stegosaurus LoRA or reference-conditioned i2i.",
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
        ("selected v1 full body", SELECTED, (0, 0, 1536, 1024)),
        ("selected v1 thagomizer", SELECTED, (35, 480, 390, 725)),
        ("selected v1 broad plates", SELECTED, (250, 110, 1190, 545)),
        ("tail-room v2 full body", TAILROOM, (0, 0, 1774, 887)),
        ("tail-room v2 thagomizer risk", TAILROOM, (1320, 410, 1774, 650)),
        ("tail-room v2 leaf-like plates", TAILROOM, (420, 70, 1220, 440)),
        ("broad-plate v2 full body", BROADPLATE, (0, 0, 1774, 887)),
        ("broad-plate v2 thagomizer risk", BROADPLATE, (1310, 430, 1774, 660)),
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
    for path in (SELECTED, TAILROOM, BROADPLATE, FIRST_PASS, SOFTCLEAN, PLATE_REFERENCE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
