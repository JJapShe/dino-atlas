from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-longtail-nonhoof-imagegen-v4.png"
LOWBODY = ASSET_ROOT / "triceratops-horridus-lowbody-footreview-imagegen-v4.png"
PREVIOUS = ASSET_ROOT / "triceratops-horridus-toefrill-imagegen-v3.png"
PREVIOUS_CROP = ASSET_ROOT / "triceratops-toefrill-crops-v3.png"
CLOSED_BEAK = ASSET_ROOT / "triceratops-horridus-closedbeak-imagegen-v2.png"
FRILL_TOE = ASSET_ROOT / "triceratops-horridus-frilltoe-imagegen-v2.png"
RHINO_REJECT = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v10.png"
CROP_OUT = ASSET_ROOT / "triceratops-longtail-crops-v4.png"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (236, 232, 224))
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
            "title": "selected v4: long tail / non-hoofed feet",
            "note": "Best current anti-rhino read: long tail, closed beak, skull frill, three horns, visible toes.",
        },
        {
            "path": LOWBODY,
            "title": "v4 low-body comparison",
            "note": "Strong head/frill and foot visibility, but the rounder torso keeps more mammal-body risk.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: toe/frill v3",
            "note": "Good three-horn and toe read; v4 improves tail length and non-hoofed foot visibility.",
        },
        {
            "path": CLOSED_BEAK,
            "title": "previous closed-beak v2",
            "note": "Strong field-guide head, but feet and dry-ground review are softer than v4.",
        },
        {
            "path": FRILL_TOE,
            "title": "v2 open-mouth comparison",
            "note": "Strong frill and toe cues, but open mouth is less calm for the app representative.",
        },
        {
            "path": RHINO_REJECT,
            "title": "rhino-drift rejection",
            "note": "Failure gate: mammal body, hoof-like feet, and weak skull-frill connection.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v3 crop audit",
            "note": "Retained to compare v3 skull frill, three horns, feet, tail, and rhino-drift gate.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 242
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
        draw_wrapped(draw, (8, thumb_h + 29), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v4 full body", SELECTED, (0, 0, 1691, 930)),
        ("selected v4 skull frill", SELECTED, (1000, 145, 1605, 610)),
        ("selected v4 three horns + beak", SELECTED, (1040, 190, 1691, 610)),
        ("selected v4 non-hoofed feet", SELECTED, (410, 620, 1385, 920)),
        ("selected v4 long tail + hip", SELECTED, (0, 375, 640, 695)),
        ("v4 lowbody round-torso risk", LOWBODY, (0, 0, 1691, 930)),
        ("previous v3 full body", PREVIOUS, (0, 0, 1657, 949)),
        ("rhino-drift rejection body", RHINO_REJECT, (0, 130, 850, 690)),
    ]

    cols = 2
    thumb_w = 380
    thumb_h = 236
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
    for path in (SELECTED, LOWBODY, PREVIOUS, PREVIOUS_CROP, CLOSED_BEAK, FRILL_TOE, RHINO_REJECT):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
