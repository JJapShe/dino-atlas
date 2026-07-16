from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "stegosaurus-stenops-strict-plates-imagegen-v1.png"
FIRST_PASS = ASSET_ROOT / "stegosaurus-stenops-plate-thagomizer-imagegen-v1.png"
SOFTCLEAN = ASSET_ROOT / "stegosaurus-stenops-thagomizer-softclean-v1.png"
THAGOMIZER_REPAIR = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-thagomizer-v1.png"
PLATE_GUIDE = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"
PLATE_REFERENCE = ASSET_ROOT / "stegosaurus-stenops-plate-thagomizer-reference-v1.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-review-options-v40.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-strict-imagegen-crops-v1.png"


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
            "title": "selected imagegen v1: strict plates / thagomizer",
            "note": "Best current natural read: broad separated plates, low body, open feet, and clearer tail spikes.",
        },
        {
            "path": FIRST_PASS,
            "title": "first imagegen pass: stronger body / extra-spike risk",
            "note": "Strong plate row and stance, but the tail tip may read as more than four spikes.",
        },
        {
            "path": SOFTCLEAN,
            "title": "previous primary: thagomizer soft-clean",
            "note": "Useful plate gate, but body/leg proportions and tail-tip artifacts stay weaker.",
        },
        {
            "path": THAGOMIZER_REPAIR,
            "title": "previous thagomizer repair",
            "note": "Before soft-clean; keeps broad plates but has wire-like tail artifacts.",
        },
        {
            "path": PLATE_GUIDE,
            "title": "dorsal-plate lock v2 guide",
            "note": "Stricter structure target for countable plates and four-spike thagomizer.",
        },
        {
            "path": PLATE_REFERENCE,
            "title": "plate + thagomizer reference",
            "note": "Project-owned diagnostic target for future LoRA or i2i routes.",
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
        ("broad separated plates", SELECTED, (250, 120, 1190, 545)),
        ("tail-tip thagomizer", SELECTED, (40, 490, 360, 705)),
        ("small low head", SELECTED, (1160, 390, 1536, 725)),
        ("four sturdy legs / open feet", SELECTED, (210, 590, 1040, 930)),
        ("first-pass extra-spike risk", FIRST_PASS, (0, 360, 410, 690)),
        ("previous primary plates", SOFTCLEAN, (110, 95, 870, 390)),
        ("previous primary tail artifact", SOFTCLEAN, (900, 250, 1152, 520)),
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
    for path in (SELECTED, FIRST_PASS, SOFTCLEAN, THAGOMIZER_REPAIR, PLATE_GUIDE, PLATE_REFERENCE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
