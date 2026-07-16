import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SOURCE = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
SOURCE_CROP = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
FOOT_I2I_REJECTION = ASSET_ROOT / "velociraptor-foot-i2i-v10-rejection-crops.png"
RESULTS = OUTPUT_ROOT / "velociraptor_sickle_toe_v11-results.json"
CONTACT = OUTPUT_ROOT / "velociraptor_sickle_toe_v11-contact-sheet.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v17.png"
CROP_OUT = ASSET_ROOT / "velociraptor-prompt-v11-rejection-crops.png"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
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


def load_v11_items():
    items = json.loads(RESULTS.read_text(encoding="utf-8"))
    for item in items:
        item["path"] = Path(item["image"])
        if not item["path"].exists():
            raise FileNotFoundError(item["path"])
    return items


def make_contact_sheet(v11_items):
    items = [
        {
            "path": SOURCE,
            "title": "current v9: keep first",
            "note": "Best current compromise: feathered body, toothed snout, folded hands, long tail, and a restrained attached foot cue.",
        },
        {
            "path": SOURCE_CROP,
            "title": "current v9 crop gate",
            "note": "Use this for exact foot, head, folded-hand, and tail review before accepting future replacements.",
        },
        {
            "path": FOOT_I2I_REJECTION,
            "title": "previous v10 foot-i2i rejection",
            "note": "Foot-only i2i created floating claws or oversized hooks, so prompt-only v11 was tested next.",
        },
        {
            "path": CONTACT,
            "title": "v11 prompt-only batch overview",
            "note": "Whole-body prompts reduced some claw risk but lost feather/dromaeosaur identity too often.",
        },
    ]
    for item in v11_items:
        items.append(
            {
                "path": item["path"],
                "title": f"reject v11: {item['promptId']}",
                "note": "Reject for weak plumage or generic theropod/bird-leg drift; do not promote above v9.",
            }
        )

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 72
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 30), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet(v11_items):
    crops = [
        ("current v9 full body - keep first", SOURCE, (0, 0, 1672, 941)),
        ("current v9 toothed snout", SOURCE, (0, 130, 520, 360)),
        ("current v9 folded hands", SOURCE, (300, 430, 760, 760)),
        ("current v9 feet / modest sickle", SOURCE, (500, 585, 1080, 930)),
    ]
    for item in v11_items:
        path = item["path"]
        label = item["promptId"]
        crops.extend(
            [
                (f"reject {label} full", path, (0, 0, 1152, 768)),
                (f"reject {label} head", path, (0, 80, 430, 320)),
                (f"reject {label} arms/body", path, (240, 260, 720, 610)),
                (f"reject {label} feet", path, (360, 470, 930, 750)),
            ]
        )

    cols = 4
    thumb_w = 300
    thumb_h = 210
    label_h = 40
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    font = ImageFont.load_default()

    for idx, (label, path, box) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 7), label[:50], fill=(42, 39, 35), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def main():
    for path in (SOURCE, SOURCE_CROP, FOOT_I2I_REJECTION, RESULTS, CONTACT):
        if not path.exists():
            raise FileNotFoundError(path)
    v11_items = load_v11_items()
    make_contact_sheet(v11_items)
    make_crop_sheet(v11_items)
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
