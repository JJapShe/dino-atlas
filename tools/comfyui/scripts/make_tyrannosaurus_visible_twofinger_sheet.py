from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "tyrannosaurus-rex-visible-twofinger-imagegen-v2.png"
BROADSIDE = ASSET_ROOT / "tyrannosaurus-rex-broadside-twofinger-comparison-v2.png"
PREVIOUS = ASSET_ROOT / "tyrannosaurus-rex-twofinger-imagegen-v1.png"
COMPACT = ASSET_ROOT / "tyrannosaurus-rex-compact-twofinger-inpaint-v1.png"
TUCKED = ASSET_ROOT / "tyrannosaurus-rex-tuckedarms-lora-v1.png"
LORA = ASSET_ROOT / "tyrannosaurus-rex-lora-v2.png"

CONTACT_OUT = ASSET_ROOT / "tyrannosaurus-review-options-v5.png"
CROP_OUT = ASSET_ROOT / "tyrannosaurus-visible-twofinger-crops-v2.png"


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
            "title": "selected v2: visible two-finger hands",
            "note": "Best current hand read: tiny chest-held arms with clearer two-clawed fingers on dry ground.",
        },
        {
            "path": BROADSIDE,
            "title": "v2 broadside comparison: finger-count risk",
            "note": "Strong body and dry-ground feet, but one hand can read as three small claw tips.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: strict two-finger v1",
            "note": "Strong full-body T. rex read, but the tiny hand crop is harder to inspect at card size.",
        },
        {
            "path": COMPACT,
            "title": "older compact inpaint comparison",
            "note": "Natural body scene with two-finger intent, but the hands are smaller and darker.",
        },
        {
            "path": TUCKED,
            "title": "tucked-arm LoRA comparison",
            "note": "Useful two-finger comparison, but old scene body and hand scale are weaker.",
        },
        {
            "path": LORA,
            "title": "LoRA v2 comparison",
            "note": "Earlier LoRA route kept a T. rex silhouette but hand and head crops are less reliable.",
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
        ("selected full body", SELECTED, (0, 0, 1691, 930)),
        ("selected head and jaws", SELECTED, (1260, 190, 1691, 500)),
        ("selected tiny arms", SELECTED, (1180, 390, 1525, 685)),
        ("selected two-finger crop", SELECTED, (1045, 420, 1285, 690)),
        ("selected dry hind feet", SELECTED, (660, 590, 1115, 835)),
        ("v2 broadside full body", BROADSIDE, (0, 0, 1692, 929)),
        ("v2 broadside hand risk", BROADSIDE, (1120, 380, 1455, 650)),
        ("previous v1 smaller hand", PREVIOUS, (840, 390, 1240, 710)),
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
    for path in (SELECTED, BROADSIDE, PREVIOUS, COMPACT, TUCKED, LORA):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
