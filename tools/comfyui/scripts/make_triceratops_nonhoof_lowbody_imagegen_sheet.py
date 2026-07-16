from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-longbody-toes-imagegen-v5.png"
LOWBODY = ASSET_ROOT / "triceratops-horridus-nonhoof-lowbody-imagegen-v5.png"
PREVIOUS_SELECTED = ASSET_ROOT / "triceratops-horridus-longtail-nonhoof-imagegen-v4.png"
LOWBODY_V4 = ASSET_ROOT / "triceratops-horridus-lowbody-footreview-imagegen-v4.png"
TOEFRILL_V3 = ASSET_ROOT / "triceratops-horridus-toefrill-imagegen-v3.png"
RHINO_REJECTION = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v11.png"
CROP_OUT = ASSET_ROOT / "triceratops-longbody-toes-crops-v5.png"


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
            "title": "selected imagegen v5: long body / visible toes",
            "note": "Best current app read: three horns, closed beak, skull frill, long tail, and separated non-hoofed feet.",
        },
        {
            "path": LOWBODY,
            "title": "v5 comparison: low body non-hoof",
            "note": "Strong long-tail and non-hoof foot cues, but the head/frill read is slightly less clean than selected v5.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: long-tail non-hoof v4",
            "note": "Keeps the three-horn identity but the torso is rounder and foot/toe review is less direct.",
        },
        {
            "path": LOWBODY_V4,
            "title": "v4 low-body comparison",
            "note": "Useful body comparison, but still carries stronger mammal-body risk at close review.",
        },
        {
            "path": TOEFRILL_V3,
            "title": "older toe/frill v3",
            "note": "Helpful three-horn and foot comparison; v5 keeps a longer tail and cleaner field-guide profile.",
        },
        {
            "path": RHINO_REJECTION,
            "title": "rhino-drift rejection",
            "note": "Failure gate: do not accept rounded mammal torso, rhino feet, or hidden dinosaur tail cues.",
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
        ("selected skull frill", SELECTED, (0, 105, 660, 520)),
        ("selected three horns + closed beak", SELECTED, (0, 130, 555, 470)),
        ("selected front non-hoofed feet", SELECTED, (220, 520, 560, 805)),
        ("selected rear non-hoofed feet", SELECTED, (690, 520, 1115, 805)),
        ("selected long tail / hip", SELECTED, (850, 300, 1774, 620)),
        ("v5 lowbody comparison", LOWBODY, (0, 0, 1774, 887)),
        ("previous v4 round-torso risk", PREVIOUS_SELECTED, (0, 0, 1691, 930)),
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
        LOWBODY,
        PREVIOUS_SELECTED,
        LOWBODY_V4,
        TOEFRILL_V3,
        RHINO_REJECTION,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
