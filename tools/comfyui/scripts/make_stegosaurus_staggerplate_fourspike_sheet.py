from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "stegosaurus-stenops-staggerplate-fourspike-imagegen-v5.png"
TAILCOUNT_OVERLAP = ASSET_ROOT / "stegosaurus-stenops-tailcount-overlap-comparison-v5.png"
BONYSURFACE_THREESPIKE = ASSET_ROOT / "stegosaurus-stenops-bonysurface-threespike-comparison-v5.png"
PREVIOUS = ASSET_ROOT / "stegosaurus-stenops-bonyplate-fourspike-imagegen-v4.png"
PREVIOUS_CROP = ASSET_ROOT / "stegosaurus-bonyplate-fourspike-crops-v4.png"
PLATEGAP_V4 = ASSET_ROOT / "stegosaurus-stenops-plategap-fourspike-imagegen-v4.png"
SMOOTHPLATE_V3 = ASSET_ROOT / "stegosaurus-stenops-smoothplate-fourspike-imagegen-v3.png"
PLATE_GUIDE = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-review-options-v44.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-staggerplate-fourspike-crops-v5.png"


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
            "title": "selected v5: staggered plates / four spikes",
            "note": "Best current tail-count read: four separated thagomizer spikes plus thick separated dorsal plates.",
        },
        {
            "path": TAILCOUNT_OVERLAP,
            "title": "v5 tail-count overlap comparison",
            "note": "Good plate row and body, but tail spikes overlap enough to risk a three-spike read.",
        },
        {
            "path": BONYSURFACE_THREESPIKE,
            "title": "v5 bony-surface three-spike risk",
            "note": "Useful bony plate surface, but the thagomizer reads as only three visible spikes.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v4",
            "note": "Strong bony plates, retained to compare plate surface against the clearer v5 four-spike tail.",
        },
        {
            "path": PLATEGAP_V4,
            "title": "v4 plate-gap comparison",
            "note": "Strong plate spacing and tail count, but plate shapes read more leaf-like.",
        },
        {
            "path": SMOOTHPLATE_V3,
            "title": "previous smooth-plate v3",
            "note": "Kept as a smoother plate and thagomizer comparison below v4/v5.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v4 crop audit",
            "note": "Use below v5 to compare bony surface, head, feet, and older tail-spike count.",
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
        ("selected v5 full body", SELECTED, (0, 0, 1692, 929)),
        ("selected v5 staggered plate row", SELECTED, (210, 95, 1225, 440)),
        ("selected v5 plate surface", SELECTED, (460, 95, 985, 370)),
        ("selected v5 small low head", SELECTED, (70, 420, 395, 620)),
        ("selected v5 four planted feet", SELECTED, (300, 615, 1035, 850)),
        ("selected v5 four separated thagomizer spikes", SELECTED, (1265, 390, 1688, 700)),
        ("v5 overlap tail-count risk", TAILCOUNT_OVERLAP, (1285, 380, 1670, 670)),
        ("v5 bony-surface three-spike risk", BONYSURFACE_THREESPIKE, (1260, 380, 1688, 690)),
        ("previous v4 full body", PREVIOUS, (0, 0, 1774, 887)),
        ("previous v4 bony plates", PREVIOUS, (330, 115, 1265, 430)),
        ("previous v4 thagomizer", PREVIOUS, (1370, 370, 1768, 630)),
        ("plate-lock structure guide", PLATE_GUIDE, (0, 0, 1536, 1024)),
    ]

    cols = 2
    thumb_w = 380
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
        TAILCOUNT_OVERLAP,
        BONYSURFACE_THREESPIKE,
        PREVIOUS,
        PREVIOUS_CROP,
        PLATEGAP_V4,
        SMOOTHPLATE_V3,
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
