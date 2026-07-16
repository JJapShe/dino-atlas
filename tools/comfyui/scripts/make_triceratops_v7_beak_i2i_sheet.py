from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
SOURCE_V7 = ASSET_ROOT / "triceratops-horridus-lowbody-toe-frame-imagegen-v7.png"
SOURCE_V7_CROP = ASSET_ROOT / "triceratops-lowbody-toe-frame-crops-v7.png"
V8_REJECTION = ASSET_ROOT / "triceratops-closedbeak-v8-rejection-crops.png"
V8_REVIEW = ASSET_ROOT / "triceratops-review-options-v14.png"
PREVIOUS_V6 = ASSET_ROOT / "triceratops-horridus-closedbeak-toegate-imagegen-v6.png"
RHINO_REJECTION = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v15.png"
CROP_OUT = ASSET_ROOT / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"


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
            "title": "selected v9: v7 body + i2i closed beak",
            "note": "Low-strength mouth-seam inpaint keeps the v7 low body, long tail, toes, frill, and three horns while closing the beak read.",
        },
        {
            "path": SOURCE_V7,
            "title": "previous v7 source",
            "note": "Best body/feet gate, but the mouth reads more open than the selected v9 i2i repair.",
        },
        {
            "path": PREVIOUS_V6,
            "title": "previous v6 closed-beak gate",
            "note": "Useful cleaner-beak comparison, but v9 keeps the v7 lower elongated body and toe frame.",
        },
        {
            "path": SOURCE_V7_CROP,
            "title": "v7 crop audit",
            "note": "Previous crop gate retained to compare skull/frill, body, tail, feet, and beak risk.",
        },
        {
            "path": V8_REJECTION,
            "title": "v8 prompt-only rejection gate",
            "note": "Shows why prompt-only closed-beak retries are not enough: cleaner mouth but mammal-like torso drift.",
        },
        {
            "path": V8_REVIEW,
            "title": "v8 full review sheet",
            "note": "Full diagnostic sheet for v8 body-risk comparisons below the selected v9 i2i candidate.",
        },
        {
            "path": RHINO_REJECTION,
            "title": "old rhino-drift rejection",
            "note": "Failure gate: reject mammal torso, hoof-like feet, weak beak, or hidden dinosaur tail.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 66
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v9 full body", SELECTED, (0, 0, 1672, 941)),
        ("selected v9 head / frill", SELECTED, (40, 150, 610, 650)),
        ("selected v9 beak seam", SELECTED, (75, 500, 430, 625)),
        ("selected v9 front toes", SELECTED, (330, 650, 780, 875)),
        ("selected v9 rear toes", SELECTED, (750, 620, 1250, 870)),
        ("selected v9 low body / long tail", SELECTED, (500, 285, 1660, 675)),
        ("source v7 head / open-mouth risk", SOURCE_V7, (40, 150, 610, 650)),
        ("source v7 beak seam", SOURCE_V7, (75, 500, 430, 625)),
        ("previous v6 closed-beak head", PREVIOUS_V6, (55, 130, 640, 575)),
        ("v8 body-risk rejection sheet", V8_REJECTION, (0, 0, 760, 858)),
        ("old rhino-drift rejection", RHINO_REJECTION, (0, 0, 1536, 1024)),
    ]

    cols = 2
    thumb_w = 380
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
        SOURCE_V7,
        SOURCE_V7_CROP,
        V8_REJECTION,
        V8_REVIEW,
        PREVIOUS_V6,
        RHINO_REJECTION,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
