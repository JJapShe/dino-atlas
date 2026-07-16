from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "coelophysis-bauri-strict-imagegen-v1.png"
DRYGROUND = ASSET_ROOT / "coelophysis-bauri-dryground-bgreplace-v1.png"
PROMPT_ONLY = ASSET_ROOT / "coelophysis-bauri.png"
GROUND_CLEAN = ASSET_ROOT / "coelophysis-bauri-ground-clean-v1.png"
FORELIMB_GUIDE = ASSET_ROOT / "coelophysis-bauri-forelimb-reference-guide-v1.png"
LORA = ASSET_ROOT / "coelophysis-bauri-lora-ground-v1.png"

CONTACT_OUT = ASSET_ROOT / "coelophysis-review-options-v5.png"
CROP_OUT = ASSET_ROOT / "coelophysis-strict-crops-v1.png"


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
            "title": "selected imagegen v1: strict early theropod",
            "note": "Best current read: narrow toothed head, long tail, dry ground, two legs, and small forelimbs.",
        },
        {
            "path": DRYGROUND,
            "title": "previous primary: dry-ground repair",
            "note": "Preserves a clean body, but the head/forelimbs read more toy-like and less theropod-specific.",
        },
        {
            "path": PROMPT_ONLY,
            "title": "prompt-only comparison",
            "note": "Useful anatomy comparison, but the old perch/log scene was less suitable for the atlas.",
        },
        {
            "path": GROUND_CLEAN,
            "title": "ground cleanup comparison",
            "note": "Readable biped stance, but small forelimbs and toe count are softer.",
        },
        {
            "path": FORELIMB_GUIDE,
            "title": "forelimb reference guide",
            "note": "Keeps the target small grasping forelimbs explicit; guide only, not final art.",
        },
        {
            "path": LORA,
            "title": "generic LoRA comparison",
            "note": "Tail and legs are readable, but forelimbs and ground-contact toes remain less reliable.",
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
        ("narrow toothed head / neck", SELECTED, (1070, 260, 1485, 520)),
        ("small forelimbs / hands", SELECTED, (900, 430, 1215, 720)),
        ("two hind legs / three-toed feet", SELECTED, (560, 520, 1080, 910)),
        ("tail fully in frame", SELECTED, (45, 340, 720, 610)),
        ("previous primary forelimbs", DRYGROUND, (705, 165, 1125, 565)),
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
    for path in (SELECTED, DRYGROUND, PROMPT_ONLY, GROUND_CLEAN, FORELIMB_GUIDE, LORA):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
