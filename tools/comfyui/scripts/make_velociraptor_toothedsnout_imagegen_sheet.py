from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-toothedsnout-sickleclaw-imagegen-v4.png"
DESERT = ASSET_ROOT / "velociraptor-mongoliensis-desert-sickleclaw-imagegen-v4.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-closearm-sickleclaw-imagegen-v2.png"
COMPACT = ASSET_ROOT / "velociraptor-mongoliensis-compactarm-sickleclaw-imagegen-v3.png"
WINGRISK = ASSET_ROOT / "velociraptor-mongoliensis-toothedhead-wingrisk-imagegen-v3.png"
NATURAL_PASS = ASSET_ROOT / "velociraptor-mongoliensis-natural-sickleclaw-imagegen-v2.png"
GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v6.png"
CROP_OUT = ASSET_ROOT / "velociraptor-toothedsnout-crops-v4.png"


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
            "title": "selected v4: toothed snout / reviewable feet",
            "note": "Best current read: less bird-like head, visible teeth, long tail, folded arms, and two raised claw cues.",
        },
        {
            "path": DESERT,
            "title": "v4 desert comparison: stronger foot but floaty pose",
            "note": "Good toothed head and sickle claw, but the raised leg pose is less stable for first-image use.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: close-arm v2",
            "note": "Balanced full body, but the head still drifts bird-like and foot hooks are more oversized.",
        },
        {
            "path": COMPACT,
            "title": "v3 compact-arm comparison",
            "note": "Good snout and body, but arm feathers and hook feet remain riskier at close review.",
        },
        {
            "path": WINGRISK,
            "title": "v3 toothed-head wing-risk comparison",
            "note": "Readable teeth and tail, but wing-like forelimbs and oversized toes are worse.",
        },
        {
            "path": NATURAL_PASS,
            "title": "wide v2 comparison",
            "note": "Useful full-body spacing; forelimb feathers read more wing-like than the selected v4.",
        },
        {
            "path": GUIDE,
            "title": "foot reference guide",
            "note": "Project structure target for raised second-toe claw and compact dromaeosaur body.",
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
        ("selected full body", SELECTED, (0, 0, 1692, 929)),
        ("selected toothed snout", SELECTED, (15, 135, 430, 315)),
        ("selected folded forelimbs", SELECTED, (430, 350, 720, 670)),
        ("selected rear foot raised claw", SELECTED, (725, 630, 1120, 880)),
        ("selected front foot raised claw", SELECTED, (490, 650, 845, 890)),
        ("v4 desert comparison full body", DESERT, (0, 0, 1691, 930)),
        ("v4 desert floaty foot risk", DESERT, (470, 575, 985, 855)),
        ("previous v2 head/foot comparison", PREVIOUS, (0, 0, 1672, 941)),
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
    for path in (SELECTED, DESERT, PREVIOUS, COMPACT, WINGRISK, NATURAL_PASS, GUIDE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
