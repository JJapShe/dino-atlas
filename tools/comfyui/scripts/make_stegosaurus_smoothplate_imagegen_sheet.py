from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "stegosaurus-stenops-smoothplate-fourspike-imagegen-v3.png"
TAILSPACE = ASSET_ROOT / "stegosaurus-stenops-tailspace-fourspike-imagegen-v3.png"
PREVIOUS = ASSET_ROOT / "stegosaurus-stenops-strict-plates-imagegen-v1.png"
TAILROOM = ASSET_ROOT / "stegosaurus-stenops-tailroom-fourspike-imagegen-v2.png"
BROADPLATE = ASSET_ROOT / "stegosaurus-stenops-broadplate-fourspike-imagegen-v2.png"
FIRST_PASS = ASSET_ROOT / "stegosaurus-stenops-plate-thagomizer-imagegen-v1.png"
PLATE_REFERENCE = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-review-options-v42.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-smoothplate-crops-v3.png"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
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
            "title": "selected v3: smoother plates / four-spike tail",
            "note": "Best current balance: natural body, separated broad plates, four countable tail spikes, open feet.",
        },
        {
            "path": TAILSPACE,
            "title": "v3 comparison: tail-space four-spike",
            "note": "Tail count is clear, but the body is rounder and the selected v3 has a stronger Stegosaurus read.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: strict plates v1",
            "note": "Strong plate row, but the tail spikes can read as more than four and plate texture is busier.",
        },
        {
            "path": TAILROOM,
            "title": "v2 tail-room comparison",
            "note": "More tail room, but thagomizer count and leaf-like plate texture remained risky.",
        },
        {
            "path": BROADPLATE,
            "title": "v2 broad-plate comparison",
            "note": "Clean full body, but the four-spike gate was not clearly better than the previous primary.",
        },
        {
            "path": FIRST_PASS,
            "title": "first strict imagegen pass",
            "note": "Good body and plates, but extra-spike risk keeps it below the selected v3 candidate.",
        },
        {
            "path": PLATE_REFERENCE,
            "title": "plate-lock structure guide",
            "note": "Project-owned guide retained for future Stegosauridae LoRA or reference-conditioned i2i.",
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
        ("selected full body", SELECTED, (0, 0, 1536, 1024)),
        ("selected four-spike thagomizer", SELECTED, (0, 410, 360, 710)),
        ("selected broad separated plates", SELECTED, (260, 110, 1250, 570)),
        ("selected small low head", SELECTED, (1140, 415, 1536, 650)),
        ("selected four planted feet", SELECTED, (520, 610, 1300, 890)),
        ("v3 tail-space comparison", TAILSPACE, (0, 0, 1691, 930)),
        ("v3 tail-space thagomizer", TAILSPACE, (0, 395, 450, 705)),
        ("previous primary extra-spike risk", PREVIOUS, (35, 480, 390, 725)),
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
        TAILSPACE,
        PREVIOUS,
        TAILROOM,
        BROADPLATE,
        FIRST_PASS,
        PLATE_REFERENCE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
