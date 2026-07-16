from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-broadskull-singleclub-imagegen-v5.png"
LONG_BODY = ASSET_ROOT / "ankylosaurus-magniventris-compactclub-longbody-comparison-v5.png"
HORN_RISK = ASSET_ROOT / "ankylosaurus-magniventris-hornrisk-comparison-v5.png"
PREVIOUS_SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-clearfeet-singleclub-imagegen-v4.png"
PREVIOUS_CROPS = ASSET_ROOT / "ankylosaurus-clearfeet-singleclub-crops-v4.png"
WIDEARMOR_V3 = ASSET_ROOT / "ankylosaurus-magniventris-widearmor-imagegen-v3.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v10.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-broadskull-singleclub-crops-v5.png"


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
            "title": "selected imagegen v5: broad skull / single club",
            "note": "Best current app read: broad low body, blunt armored skull, four visible feet, and one attached oval tail club.",
        },
        {
            "path": LONG_BODY,
            "title": "v5 comparison: cleaner club / longer body",
            "note": "Useful single-club and head comparison, but the torso and tail read longer and less squat than selected v5.",
        },
        {
            "path": HORN_RISK,
            "title": "v5 rejection gate: horn-like skull side spikes",
            "note": "Armor and club are strong, but side projections risk reading as horns rather than low ankylosaur skull armor.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: clear-feet v4",
            "note": "Good open-foot and club gate, but the skull/body read is less broad and familiar than selected v5.",
        },
        {
            "path": PREVIOUS_CROPS,
            "title": "previous v4 crop audit",
            "note": "Keep as a comparison for the prior foot and tail-club gate.",
        },
        {
            "path": WIDEARMOR_V3,
            "title": "older wide-armor v3 comparison",
            "note": "Useful armor identity comparison retained below the v5 and v4 candidates.",
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
        ("selected broad blunt skull", SELECTED, (65, 315, 500, 585)),
        ("selected armor rows", SELECTED, (380, 205, 1185, 520)),
        ("selected single attached club", SELECTED, (1325, 320, 1745, 575)),
        ("selected front feet", SELECTED, (285, 575, 710, 805)),
        ("selected rear feet", SELECTED, (870, 570, 1285, 815)),
        ("v5 longer-body comparison", LONG_BODY, (0, 0, 1774, 887)),
        ("v5 horn-risk rejection", HORN_RISK, (0, 0, 1672, 941)),
        ("previous v4 full-body gate", PREVIOUS_SELECTED, (0, 0, 1774, 887)),
        ("previous v4 foot / club crops", PREVIOUS_CROPS, (0, 0, 720, 1144)),
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
    for path in (SELECTED, LONG_BODY, HORN_RISK, PREVIOUS_SELECTED, PREVIOUS_CROPS, WIDEARMOR_V3):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
