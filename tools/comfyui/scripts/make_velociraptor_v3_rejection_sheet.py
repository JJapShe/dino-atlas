from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-closearm-sickleclaw-imagegen-v2.png"
COMPACT = ASSET_ROOT / "velociraptor-mongoliensis-compactarm-sickleclaw-imagegen-v3.png"
WINGRISK = ASSET_ROOT / "velociraptor-mongoliensis-toothedhead-wingrisk-imagegen-v3.png"
NATURAL_PASS = ASSET_ROOT / "velociraptor-mongoliensis-natural-sickleclaw-imagegen-v2.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-sickleclaw-imagegen-v1.png"
GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v5.png"
CROP_OUT = ASSET_ROOT / "velociraptor-v3-rejection-crops.png"


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
            "title": "selected v2: keep first",
            "note": "Best current balance: toothed snout, long tail, feathered body, folded arms, and visible sickle claws.",
        },
        {
            "path": COMPACT,
            "title": "v3 compact-arm comparison: not promoted",
            "note": "Good snout and body, but the hand/arm feathers still read wing-like and claws are oversized.",
        },
        {
            "path": WINGRISK,
            "title": "v3 toothed-head comparison: not promoted",
            "note": "Readable teeth and tail, but wing-like forelimbs and hook claws are worse at close review.",
        },
        {
            "path": NATURAL_PASS,
            "title": "wide v2 comparison",
            "note": "Good full-body spacing and teeth, but forelimb feathers can read more wing-like.",
        },
        {
            "path": PREVIOUS,
            "title": "previous v1: oversized claw cue",
            "note": "Clear feet and teeth, but the sickle claws are larger and more hook-like at crop scale.",
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
        ("selected v2 full body", SELECTED, (0, 0, 1672, 941)),
        ("selected v2 head", SELECTED, (20, 125, 440, 330)),
        ("selected v2 foot cue", SELECTED, (430, 640, 1135, 910)),
        ("compact v3 full body", COMPACT, (0, 0, 1692, 929)),
        ("compact v3 arm still wing-like", COMPACT, (900, 360, 1250, 700)),
        ("compact v3 foot hook risk", COMPACT, (720, 620, 1135, 885)),
        ("wingrisk v3 full body", WINGRISK, (0, 0, 1774, 887)),
        ("wingrisk v3 oversized toes", WINGRISK, (520, 600, 1010, 865)),
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
    for path in (SELECTED, COMPACT, WINGRISK, NATURAL_PASS, PREVIOUS, GUIDE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
