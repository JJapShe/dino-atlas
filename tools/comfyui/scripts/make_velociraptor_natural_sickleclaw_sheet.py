from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-closearm-sickleclaw-imagegen-v2.png"
NATURAL_PASS = ASSET_ROOT / "velociraptor-mongoliensis-natural-sickleclaw-imagegen-v2.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-sickleclaw-imagegen-v1.png"
GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"
LOW_LORA = ASSET_ROOT / "velociraptor-mongoliensis-footguide-low-lora-v1.png"
REAR_BLEND = ASSET_ROOT / "velociraptor-mongoliensis-rear-sickle-blend-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v4.png"
CROP_OUT = ASSET_ROOT / "velociraptor-head-foot-crops-v4.png"


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
            "title": "selected imagegen v2: close forelimbs / natural claws",
            "note": "Best current read: toothed dromaeosaur head, full tail, feathered body, visible natural-size sickle claws.",
        },
        {
            "path": NATURAL_PASS,
            "title": "wide v2 comparison: stronger spacing / wingier arms",
            "note": "Good full-body spacing and teeth, but the forelimb feathers can read more wing-like.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: strict sickle-claw imagegen v1",
            "note": "Clear feet and teeth, but the sickle claws are larger and more hook-like at crop scale.",
        },
        {
            "path": GUIDE,
            "title": "foot reference guide",
            "note": "Project structure target for raised second-toe claw and compact dromaeosaur body.",
        },
        {
            "path": LOW_LORA,
            "title": "previous low-LoRA comparison",
            "note": "Useful non-bird head direction, but feather signal and raised sickle cue are too subtle.",
        },
        {
            "path": REAR_BLEND,
            "title": "rear sickle-claw blend comparison",
            "note": "Useful rear-foot cue, but the head still reads too bird-like for promotion.",
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
        ("selected full body", SELECTED, (0, 0, 1672, 941)),
        ("selected toothed snout", SELECTED, (20, 125, 440, 330)),
        ("selected folded forelimbs", SELECTED, (300, 350, 610, 705)),
        ("selected rear foot + raised claw", SELECTED, (430, 690, 760, 900)),
        ("selected front foot + raised claw", SELECTED, (780, 640, 1135, 895)),
        ("wide v2 wingier forelimbs", NATURAL_PASS, (930, 390, 1270, 720)),
        ("previous oversized sickle cue", PREVIOUS, (710, 660, 1220, 940)),
        ("guide raised second toe", GUIDE, (620, 410, 1080, 735)),
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
    for path in (SELECTED, NATURAL_PASS, PREVIOUS, GUIDE, LOW_LORA, REAR_BLEND):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
