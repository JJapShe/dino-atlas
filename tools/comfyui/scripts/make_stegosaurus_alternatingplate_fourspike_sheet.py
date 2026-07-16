from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
OVERLAP_RISK = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-overlap-comparison-v6.png"
EXTRASPIKE_RISK = ASSET_ROOT / "stegosaurus-stenops-extraspike-plate-comparison-v6.png"
PREVIOUS = ASSET_ROOT / "stegosaurus-stenops-staggerplate-fourspike-imagegen-v5.png"
PREVIOUS_CROP = ASSET_ROOT / "stegosaurus-staggerplate-fourspike-crops-v5.png"
BONYSURFACE_V5 = ASSET_ROOT / "stegosaurus-stenops-bonysurface-threespike-comparison-v5.png"
PREVIOUS_V4 = ASSET_ROOT / "stegosaurus-stenops-bonyplate-fourspike-imagegen-v4.png"
PLATE_GUIDE = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-review-options-v45.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"


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
            "title": "selected v6: alternating plates / four spikes",
            "note": "Best current plate-row read: clearer alternating two-row cue while keeping four countable thagomizer spikes.",
        },
        {
            "path": OVERLAP_RISK,
            "title": "v6 overlap comparison",
            "note": "Strong alternating plate cue, but the tail spikes overlap enough to weaken the four-spike count.",
        },
        {
            "path": EXTRASPIKE_RISK,
            "title": "v6 extra-spike risk comparison",
            "note": "Strong two-row plate cue, but the thagomizer can read as more than four spikes.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v5",
            "note": "Excellent four-spike gate retained below v6 because the alternating plate-row cue is weaker.",
        },
        {
            "path": BONYSURFACE_V5,
            "title": "v5 bony-surface three-spike risk",
            "note": "Useful bony plate surface, but the thagomizer reads as only three visible spikes.",
        },
        {
            "path": PREVIOUS_V4,
            "title": "previous bony-plate v4",
            "note": "Strong bony surface comparison retained below the v6 and v5 candidates.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v5 crop audit",
            "note": "Use below v6 to compare old plate row, plate surface, four feet, and four-spike tail gate.",
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
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v6 full body", SELECTED, (0, 0, 1672, 940)),
        ("selected v6 alternating plate row", SELECTED, (185, 80, 1190, 430)),
        ("selected v6 plate surface", SELECTED, (430, 90, 980, 360)),
        ("selected v6 small low head", SELECTED, (70, 390, 405, 610)),
        ("selected v6 four planted feet", SELECTED, (285, 600, 1080, 855)),
        ("selected v6 four thagomizer spikes", SELECTED, (1215, 355, 1660, 690)),
        ("v6 overlap tail-count risk", OVERLAP_RISK, (1210, 355, 1660, 690)),
        ("v6 extra-spike risk", EXTRASPIKE_RISK, (1200, 350, 1660, 700)),
        ("previous v5 full body", PREVIOUS, (0, 0, 1692, 929)),
        ("previous v5 plate row", PREVIOUS, (210, 95, 1225, 440)),
        ("previous v5 four-spike gate", PREVIOUS, (1265, 390, 1688, 700)),
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
        OVERLAP_RISK,
        EXTRASPIKE_RISK,
        PREVIOUS,
        PREVIOUS_CROP,
        BONYSURFACE_V5,
        PREVIOUS_V4,
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
