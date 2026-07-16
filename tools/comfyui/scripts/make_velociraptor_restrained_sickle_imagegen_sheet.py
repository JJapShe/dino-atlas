from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-restrained-sickle-imagegen-v6.png"
FOOT_REVIEW = ASSET_ROOT / "velociraptor-mongoliensis-foldedarm-footreview-imagegen-v6.png"
PREVIOUS_SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-compactarm-toothedsickle-imagegen-v5.png"
RAISEDTOE_V5 = ASSET_ROOT / "velociraptor-mongoliensis-raisedtoe-toothedsnout-imagegen-v5.png"
COMPACTFEATHER_V5 = ASSET_ROOT / "velociraptor-mongoliensis-compactfeather-sickleclaw-imagegen-v5.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v12.png"
CROP_OUT = ASSET_ROOT / "velociraptor-restrained-sickle-crops-v6.png"


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
            "title": "selected imagegen v6: restrained sickle / folded arms",
            "note": "Best current app read: toothed snout, long tail, body feathers, folded arms, and visible sickle-claw cues.",
        },
        {
            "path": FOOT_REVIEW,
            "title": "v6 comparison: folded-arm foot review",
            "note": "Good body/tail read, but foot claws and forelimb feathers remain less balanced than selected v6.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: compact-arm toothed-sickle v5",
            "note": "Strong teeth and paired sickle cues, but arm feathers read more wing-like at close review.",
        },
        {
            "path": RAISEDTOE_V5,
            "title": "v5 raised-toe comparison",
            "note": "Useful toothed-snout comparison, with higher wing/hook risk around the forelimbs.",
        },
        {
            "path": COMPACTFEATHER_V5,
            "title": "v5 compact-feather comparison",
            "note": "Calmer arm profile, but softer snout teeth and less diagnostic head read at app scale.",
        },
        {
            "path": FOOT_GUIDE,
            "title": "foot reference guide",
            "note": "Project-owned target for later dromaeosaur LoRA or reference-conditioned i2i foot passes.",
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
        ("selected toothed snout", SELECTED, (135, 175, 555, 360)),
        ("selected folded forelimbs", SELECTED, (450, 405, 705, 620)),
        ("selected front foot / sickle", SELECTED, (620, 600, 910, 820)),
        ("selected rear foot / sickle", SELECTED, (805, 505, 1105, 775)),
        ("selected tail/body balance", SELECTED, (850, 290, 1720, 520)),
        ("v6 comparison foot risk", FOOT_REVIEW, (585, 515, 1075, 820)),
        ("previous v5 wing/hook risk", PREVIOUS_SELECTED, (510, 385, 980, 760)),
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
        FOOT_REVIEW,
        PREVIOUS_SELECTED,
        RAISEDTOE_V5,
        COMPACTFEATHER_V5,
        FOOT_GUIDE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
