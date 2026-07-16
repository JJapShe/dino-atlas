from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
SMALLHAND = ASSET_ROOT / "plateosaurus-engelhardti-smallhand-thumbclaw-imagegen-v3.png"
BIPEDAL = ASSET_ROOT / "plateosaurus-engelhardti-bipedal-smallhand-imagegen-v3.png"
PREVIOUS = ASSET_ROOT / "plateosaurus-engelhardti-cleanlimbs-imagegen-v2.png"
SEPARATED = ASSET_ROOT / "plateosaurus-engelhardti-separatedlegs-imagegen-v2.png"
THUMBSMALL = ASSET_ROOT / "plateosaurus-engelhardti-thumbsmall-imagegen-v2.png"
SIXLEG_REJECT = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

CONTACT_OUT = ASSET_ROOT / "plateosaurus-review-options-v11.png"
CROP_OUT = ASSET_ROOT / "plateosaurus-singleforelimb-smallhand-crops-v3.png"


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
            "title": "selected v3: single forelimb / smaller hand",
            "note": "Best current count read: two hind legs, full tail, herbivore head, and reduced six-leg risk.",
        },
        {
            "path": SMALLHAND,
            "title": "v3 thumb-claw comparison",
            "note": "Good body/head, but the hands still read longer and more hook-like at app scale.",
        },
        {
            "path": BIPEDAL,
            "title": "v3 bipedal small-hand comparison",
            "note": "Smaller hand, but overlapping forelimbs create a possible extra-limb read.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v2",
            "note": "Strong earlier representative, but the selected v3 reduces the large hook-hand impression.",
        },
        {
            "path": SEPARATED,
            "title": "v2 separated-leg comparison",
            "note": "Clear hind-leg stride, but hands stay too large and hook-like.",
        },
        {
            "path": THUMBSMALL,
            "title": "v2 small-hand comparison",
            "note": "Calmer hands, but weaker hind-leg separation than selected v3.",
        },
        {
            "path": SIXLEG_REJECT,
            "title": "six-leg rejection gate",
            "note": "Keep as rejection reference: forelimb edits can easily create extra-leg reads.",
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
        ("selected v3 full body", SELECTED, (0, 0, 1628, 966)),
        ("selected v3 herbivore head", SELECTED, (75, 165, 510, 350)),
        ("selected v3 single lifted forelimb", SELECTED, (395, 410, 640, 685)),
        ("selected v3 small hand / thumb-claw cue", SELECTED, (420, 505, 640, 715)),
        ("selected v3 separated hind legs", SELECTED, (665, 535, 1110, 890)),
        ("selected v3 full tail", SELECTED, (835, 385, 1620, 665)),
        ("v3 thumb-claw hook-hand risk", SMALLHAND, (360, 380, 630, 675)),
        ("v3 bipedal extra-limb risk", BIPEDAL, (330, 380, 620, 675)),
        ("previous v2 full body", PREVIOUS, (0, 0, 1536, 1024)),
        ("previous v2 hook-hand comparison", PREVIOUS, (330, 360, 610, 675)),
        ("six-leg rejection crop", SIXLEG_REJECT, (300, 280, 820, 740)),
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
    for path in (SELECTED, SMALLHAND, BIPEDAL, PREVIOUS, SEPARATED, THUMBSMALL, SIXLEG_REJECT):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
