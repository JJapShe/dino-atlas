from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-compactarm-toothedsickle-imagegen-v5.png"
RAISEDTOE = ASSET_ROOT / "velociraptor-mongoliensis-raisedtoe-toothedsnout-imagegen-v5.png"
COMPACTFEATHER = ASSET_ROOT / "velociraptor-mongoliensis-compactfeather-sickleclaw-imagegen-v5.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-toothedsnout-sickleclaw-imagegen-v4.png"
DESERT = ASSET_ROOT / "velociraptor-mongoliensis-desert-sickleclaw-imagegen-v4.png"
PREVIOUS_V2 = ASSET_ROOT / "velociraptor-mongoliensis-closearm-sickleclaw-imagegen-v2.png"
GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v11.png"
CROP_OUT = ASSET_ROOT / "velociraptor-compactarm-toothedsickle-crops-v5.png"


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
            "title": "selected v5: toothed snout / paired sickle claws",
            "note": "Best current app read: visible teeth, long stiff tail, compact arms, and front/rear raised claw cues.",
        },
        {
            "path": RAISEDTOE,
            "title": "v5 raised-toe comparison: stronger teeth",
            "note": "Good narrow toothed snout, but the arm feather bundle and hand claws read more wing/hook-like.",
        },
        {
            "path": COMPACTFEATHER,
            "title": "v5 compact-feather comparison: foot cue",
            "note": "Readable raised claw and calmer arm profile, but the snout teeth are softer than selected v5.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v4",
            "note": "Still strong, but selected v5 makes the paired sickle-claw cues and teeth more visible at app scale.",
        },
        {
            "path": DESERT,
            "title": "v4 desert comparison",
            "note": "Strong foot cue, but the raised-leg pose reads floatier and less stable for first-image use.",
        },
        {
            "path": PREVIOUS_V2,
            "title": "older close-arm v2 comparison",
            "note": "Balanced full body, but the head reads more bird-like and the feet are less diagnostic.",
        },
        {
            "path": GUIDE,
            "title": "foot reference guide",
            "note": "Project structure target for the raised second-toe claw and compact dromaeosaur proportions.",
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
        ("selected v5 full body", SELECTED, (0, 0, 1690, 931)),
        ("selected v5 toothed snout", SELECTED, (110, 165, 570, 345)),
        ("selected v5 compact forelimbs", SELECTED, (475, 385, 735, 650)),
        ("selected v5 front raised claw", SELECTED, (565, 620, 900, 830)),
        ("selected v5 rear raised claw", SELECTED, (860, 650, 1215, 855)),
        ("selected v5 tail/body balance", SELECTED, (720, 285, 1680, 500)),
        ("v5 raised-toe wing/hook risk", RAISEDTOE, (360, 380, 775, 850)),
        ("v5 compact-feather snout softness", COMPACTFEATHER, (90, 155, 560, 330)),
        ("previous v4 full body", PREVIOUS, (0, 0, 1692, 929)),
        ("previous v4 head/foot gate", PREVIOUS, (0, 135, 1120, 890)),
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
    for path in (SELECTED, RAISEDTOE, COMPACTFEATHER, PREVIOUS, DESERT, PREVIOUS_V2, GUIDE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
