from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-singleclub-imagegen-v1.png"
WIDE = ASSET_ROOT / "ankylosaurus-magniventris-singleclub-wide-v1.png"
LOWWIDE = ASSET_ROOT / "ankylosaurus-magniventris-lowwide-imagegen-v1.png"
TAILCLUB = ASSET_ROOT / "ankylosaurus-magniventris-tailclub-naturalized-v1.png"
STRUCTURE = ASSET_ROOT / "ankylosaurus-magniventris.png"
LORA = ASSET_ROOT / "ankylosaurus-magniventris-identity-recovery-sd15-lora-i2i-v1.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v4.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-singleclub-crops-v1.png"


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
            "title": "selected imagegen v1: single fused tail club",
            "note": "Best current Ankylosaurus read: low armored body, compact head, open feet, and one attached club.",
        },
        {
            "path": WIDE,
            "title": "single-club wide comparison",
            "note": "Good head-right comparison with a single club; body/feet are a bit less clear than selected.",
        },
        {
            "path": LOWWIDE,
            "title": "previous primary: low-wide imagegen",
            "note": "Strong body and armor, but the tail club reads slightly double-lobed and oversized.",
        },
        {
            "path": TAILCLUB,
            "title": "older tail-club naturalized comparison",
            "note": "Attached club is present, but the body/head drift toward lizard or crocodile.",
        },
        {
            "path": STRUCTURE,
            "title": "structure guide",
            "note": "Keeps the broad low body and club target explicit; guide only.",
        },
        {
            "path": LORA,
            "title": "SD1.5 LoRA i2i structure comparison",
            "note": "Useful for identity structure, but too flat and diagram-like for first image.",
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
        ("compact head / blunt snout", SELECTED, (30, 355, 410, 650)),
        ("low rounded osteoderms", SELECTED, (360, 220, 1050, 520)),
        ("single fused tail club", SELECTED, (1120, 405, 1536, 670)),
        ("four sturdy feet", SELECTED, (180, 615, 950, 905)),
        ("previous double-lobed club risk", LOWWIDE, (0, 305, 330, 555)),
        ("head-right single-club comparison", WIDE, (1115, 285, 1536, 635)),
        ("structure-guide club target", STRUCTURE, (820, 330, 1152, 560)),
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
    for path in (SELECTED, WIDE, LOWWIDE, TAILCLUB, STRUCTURE, LORA):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
