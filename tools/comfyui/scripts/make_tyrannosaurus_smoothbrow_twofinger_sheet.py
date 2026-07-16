from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "tyrannosaurus-rex-smoothbrow-twofinger-imagegen-v3.png"
CALMJAW = ASSET_ROOT / "tyrannosaurus-rex-calmjaw-twofinger-comparison-v3.png"
VISIBLEARMS = ASSET_ROOT / "tyrannosaurus-rex-visiblearms-comparison-v3.png"
PREVIOUS_SELECTED = ASSET_ROOT / "tyrannosaurus-rex-visible-twofinger-imagegen-v2.png"
BROADSIDE_V2 = ASSET_ROOT / "tyrannosaurus-rex-broadside-twofinger-comparison-v2.png"
PREVIOUS_V1 = ASSET_ROOT / "tyrannosaurus-rex-twofinger-imagegen-v1.png"

CONTACT_OUT = ASSET_ROOT / "tyrannosaurus-review-options-v6.png"
CROP_OUT = ASSET_ROOT / "tyrannosaurus-smoothbrow-twofinger-crops-v3.png"


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
            "title": "selected imagegen v3: smooth brow / two fingers",
            "note": "Best current app read: calmer head, tiny visible chest arms, two-finger cue, dry feet, and full tail.",
        },
        {
            "path": CALMJAW,
            "title": "v3 comparison: calm jaw two-finger",
            "note": "Useful hand comparison, but the body/leg read is less stable than selected v3.",
        },
        {
            "path": VISIBLEARMS,
            "title": "v3 comparison: visible arms",
            "note": "The arms are clear, but brow texture and hand count are less balanced than selected v3.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: visible two-finger v2",
            "note": "Strong T. rex body and hand cue, but the selected v3 has a calmer mouth and less horn-like brow read.",
        },
        {
            "path": BROADSIDE_V2,
            "title": "v2 broadside comparison",
            "note": "Strong dry-ground profile, but one hand can still read as three small claw tips.",
        },
        {
            "path": PREVIOUS_V1,
            "title": "older strict two-finger v1",
            "note": "Useful full-body comparison, but the tiny hand crop is harder to inspect at app scale.",
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
        ("selected full body", SELECTED, (0, 0, 1774, 887)),
        ("selected massive head / low brow", SELECTED, (85, 135, 500, 380)),
        ("selected tiny arms", SELECTED, (380, 335, 610, 575)),
        ("selected two-finger hands", SELECTED, (430, 400, 590, 615)),
        ("selected dry hind feet", SELECTED, (630, 605, 1125, 820)),
        ("selected full tail", SELECTED, (900, 300, 1774, 530)),
        ("previous v2 hand / brow risk", PREVIOUS_SELECTED, (1015, 185, 1525, 690)),
        ("v3 comparison hand risk", CALMJAW, (420, 350, 680, 625)),
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
    for path in (
        SELECTED,
        CALMJAW,
        VISIBLEARMS,
        PREVIOUS_SELECTED,
        BROADSIDE_V2,
        PREVIOUS_V1,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
