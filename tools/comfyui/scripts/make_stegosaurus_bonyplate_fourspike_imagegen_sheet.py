from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "stegosaurus-stenops-bonyplate-fourspike-imagegen-v4.png"
PLATEGAP = ASSET_ROOT / "stegosaurus-stenops-plategap-fourspike-imagegen-v4.png"
PREVIOUS_SELECTED = ASSET_ROOT / "stegosaurus-stenops-smoothplate-fourspike-imagegen-v3.png"
TAILSPACE_V3 = ASSET_ROOT / "stegosaurus-stenops-tailspace-fourspike-imagegen-v3.png"
STRICT_V1 = ASSET_ROOT / "stegosaurus-stenops-strict-plates-imagegen-v1.png"
PLATE_GUIDE = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-review-options-v43.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-bonyplate-fourspike-crops-v4.png"


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
            "title": "selected imagegen v4: bony plates / four spikes",
            "note": "Best current app read: thicker bony plate surfaces, clear sky gaps, low body, and countable four-spike tail.",
        },
        {
            "path": PLATEGAP,
            "title": "v4 comparison: plate gaps / four spikes",
            "note": "Strong plate spacing and tail count, but plate shapes read more leaf-like than selected v4.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: smooth-plate v3",
            "note": "Keeps the natural low body and four spikes, but plate texture and alternating-row read are weaker.",
        },
        {
            "path": TAILSPACE_V3,
            "title": "v3 tail-space comparison",
            "note": "Very readable thagomizer, but the body and plate identity are weaker than selected v4.",
        },
        {
            "path": STRICT_V1,
            "title": "older strict plate imagegen",
            "note": "Useful broad-plate comparison; tail count and plate surface are less clean than selected v4.",
        },
        {
            "path": PLATE_GUIDE,
            "title": "dorsal plate lock guide",
            "note": "Project-owned target for future Stegosauridae LoRA or reference-conditioned i2i passes.",
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
        ("selected broad bony plates", SELECTED, (330, 115, 1265, 430)),
        ("selected plate surface texture", SELECTED, (490, 105, 1050, 355)),
        ("selected small low head", SELECTED, (60, 390, 385, 590)),
        ("selected four planted feet", SELECTED, (300, 570, 980, 820)),
        ("selected four-spike thagomizer", SELECTED, (1370, 370, 1768, 630)),
        ("v4 comparison leaf-like plate risk", PLATEGAP, (320, 80, 1260, 430)),
        ("previous v3 smoother plate risk", PREVIOUS_SELECTED, (215, 80, 1100, 455)),
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
        PLATEGAP,
        PREVIOUS_SELECTED,
        TAILSPACE_V3,
        STRICT_V1,
        PLATE_GUIDE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
