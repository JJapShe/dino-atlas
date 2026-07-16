from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "coelophysis-bauri-compacthands-imagegen-v2.png"
OPEN_LIMBS = ASSET_ROOT / "coelophysis-bauri-openlimbs-imagegen-v2.png"
PREVIOUS_SELECTED = ASSET_ROOT / "coelophysis-bauri-strict-imagegen-v1.png"
DRYGROUND = ASSET_ROOT / "coelophysis-bauri-dryground-bgreplace-v1.png"
PROMPT_ONLY = ASSET_ROOT / "coelophysis-bauri.png"
FORELIMB_GUIDE = ASSET_ROOT / "coelophysis-bauri-forelimb-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "coelophysis-review-options-v6.png"
CROP_OUT = ASSET_ROOT / "coelophysis-compacthands-crops-v2.png"


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
            "note": "Best current app read: open dry ground, long tail, two legs, clearer feet, and less hook-like small hands.",
        },
        {
            "path": OPEN_LIMBS,
            "title": "v2 comparison: open limb visibility",
            "note": "Excellent full-tail and foot review, but the forelimb hand remains longer and more hook-like.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: strict imagegen v1",
            "note": "Strong narrow head and body gate, but tall plants and hand claws are weaker at close review.",
        },
        {
            "path": DRYGROUND,
            "title": "dry-ground repair comparison",
            "note": "Preserves the dry atlas scene, but the head and forelimbs are softer than the imagegen pair.",
        },
        {
            "path": PROMPT_ONLY,
            "title": "prompt-only comparison",
            "note": "Useful anatomy comparison, but the log/perch setting is less suitable for the atlas.",
        },
        {
            "path": FORELIMB_GUIDE,
            "title": "forelimb reference guide",
            "note": "Project-owned structure target for a future small-theropod LoRA or guided i2i route.",
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
        ("selected narrow head / neck", SELECTED, (95, 195, 560, 405)),
        ("selected compact hands", SELECTED, (560, 455, 760, 650)),
        ("selected two hind legs / feet", SELECTED, (720, 415, 1160, 790)),
        ("selected full tail", SELECTED, (760, 315, 1774, 520)),
        ("openlimbs v2 hand risk", OPEN_LIMBS, (475, 405, 690, 635)),
        ("previous primary hand claws", PREVIOUS_SELECTED, (900, 430, 1215, 720)),
        ("previous primary feet", PREVIOUS_SELECTED, (560, 520, 1080, 910)),
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
    for path in (SELECTED, OPEN_LIMBS, PREVIOUS_SELECTED, DRYGROUND, PROMPT_ONLY, FORELIMB_GUIDE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
