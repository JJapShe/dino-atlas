from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-closedbeak-toegate-imagegen-v6.png"
LONGBACK = ASSET_ROOT / "triceratops-horridus-longback-toe-comparison-v6.png"
MOUTHRISK = ASSET_ROOT / "triceratops-horridus-frilltoe-mouthrisk-comparison-v6.png"
PREVIOUS = ASSET_ROOT / "triceratops-horridus-longbody-toes-imagegen-v5.png"
PREVIOUS_CROP = ASSET_ROOT / "triceratops-longbody-toes-crops-v5.png"
LOWBODY = ASSET_ROOT / "triceratops-horridus-nonhoof-lowbody-imagegen-v5.png"
LONGTAIL_V4 = ASSET_ROOT / "triceratops-horridus-longtail-nonhoof-imagegen-v4.png"
RHINO_REJECTION = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v12.png"
CROP_OUT = ASSET_ROOT / "triceratops-closedbeak-toegate-crops-v6.png"


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
            "title": "selected v6: closed beak / toe gate",
            "note": "Best current Triceratops read: skull frill, three horns, closed beak, long tail, and non-hoofed toes.",
        },
        {
            "path": LONGBACK,
            "title": "v6 long-back toe comparison",
            "note": "Strong toe and tail cues, but the beak gap and torso mass are weaker than selected v6.",
        },
        {
            "path": MOUTHRISK,
            "title": "v6 frill/toe mouth-risk comparison",
            "note": "Useful frill and feet comparison, but the mouth reads more open and the torso is rounder.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v5",
            "note": "Useful long-body candidate retained to compare torso, toes, and frill rim against selected v6.",
        },
        {
            "path": LOWBODY,
            "title": "previous low-body v5 comparison",
            "note": "Strong long-tail and non-hoof foot cues, but the head/frill read is slightly less clean.",
        },
        {
            "path": LONGTAIL_V4,
            "title": "previous long-tail v4 comparison",
            "note": "Retained as an older long-tail gate with more round-torso risk.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v5 crop audit",
            "note": "Kept below v6 for direct skull/frill, toe, body, and tail comparison.",
        },
        {
            "path": RHINO_REJECTION,
            "title": "rhino-drift rejection",
            "note": "Failure gate: reject rounded mammal torso, rhino feet, weak beak, or hidden dinosaur tail.",
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
        ("selected v6 full body", SELECTED, (0, 0, 1672, 941)),
        ("selected v6 skull-attached frill", SELECTED, (55, 130, 640, 575)),
        ("selected v6 three horns + closed beak", SELECTED, (65, 180, 535, 555)),
        ("selected v6 front non-hoofed feet", SELECTED, (330, 635, 725, 860)),
        ("selected v6 rear non-hoofed feet", SELECTED, (760, 625, 1260, 865)),
        ("selected v6 long tail / hip", SELECTED, (820, 330, 1655, 660)),
        ("v6 long-back beak/torso risk", LONGBACK, (70, 130, 730, 600)),
        ("v6 long-back toe comparison", LONGBACK, (340, 645, 1180, 870)),
        ("v6 mouth-risk comparison", MOUTHRISK, (60, 150, 720, 620)),
        ("previous v5 full body", PREVIOUS, (0, 0, 1774, 887)),
        ("previous v5 skull/frill comparison", PREVIOUS, (0, 105, 660, 520)),
        ("previous v5 rear foot comparison", PREVIOUS, (690, 520, 1115, 805)),
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
        LONGBACK,
        MOUTHRISK,
        PREVIOUS,
        PREVIOUS_CROP,
        LOWBODY,
        LONGTAIL_V4,
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
