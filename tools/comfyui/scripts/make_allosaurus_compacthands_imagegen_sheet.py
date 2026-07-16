from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "allosaurus-fragilis-compacthands-imagegen-v2.png"
SUBTLEBROW = ASSET_ROOT / "allosaurus-fragilis-subtlebrow-imagegen-v2.png"
PREVIOUS_SELECTED = ASSET_ROOT / "allosaurus-fragilis-strict-imagegen-v1.png"
OPEN_FEET = ASSET_ROOT / "allosaurus-fragilis-openfeet-imagegen-v1.png"
HANDCUE = ASSET_ROOT / "allosaurus-fragilis-handcue-inpaint-v1.png"
REFERENCE = ASSET_ROOT / "allosaurus-fragilis.png"

CONTACT_OUT = ASSET_ROOT / "allosaurus-review-options-v7.png"
CROP_OUT = ASSET_ROOT / "allosaurus-compacthands-crops-v2.png"


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
            "title": "selected imagegen v2: compact hands",
            "note": "Best current app read: lower allosaur head, calmer brow, open feet, and shorter hand claws.",
        },
        {
            "path": SUBTLEBROW,
            "title": "v2 comparison: subtle brow risk",
            "note": "Lower brow intent, but hands read longer and the body/head drift slightly T. rex-like.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: strict imagegen v1",
            "note": "Strong side-profile body gate, but brow ridges and hand length are more dramatic.",
        },
        {
            "path": OPEN_FEET,
            "title": "open-feet imagegen comparison",
            "note": "Good foot review, but head ridges and hand hooks are stronger than selected v2.",
        },
        {
            "path": HANDCUE,
            "title": "hand-cue inpaint comparison",
            "note": "Natural scene remains useful, but grass and soft rear foot weaken the anatomy gate.",
        },
        {
            "path": REFERENCE,
            "title": "structure reference",
            "note": "Reference-card body plan retained for longer arms and allosaur proportions.",
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
        ("selected head / subtle brow", SELECTED, (70, 180, 480, 420)),
        ("selected compact hands", SELECTED, (420, 430, 660, 640)),
        ("selected hind feet / toes", SELECTED, (635, 560, 1105, 790)),
        ("selected full tail", SELECTED, (840, 320, 1774, 540)),
        ("subtlebrow v2 hand risk", SUBTLEBROW, (500, 430, 760, 650)),
        ("previous primary brow risk", PREVIOUS_SELECTED, (1130, 240, 1536, 560)),
        ("previous primary hands", PREVIOUS_SELECTED, (1020, 410, 1330, 720)),
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
    for path in (SELECTED, SUBTLEBROW, PREVIOUS_SELECTED, OPEN_FEET, HANDCUE, REFERENCE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
