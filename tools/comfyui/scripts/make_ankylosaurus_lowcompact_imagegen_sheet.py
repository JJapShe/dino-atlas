from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-lowcompact-imagegen-v2.png"
ARMORED_CLUB = ASSET_ROOT / "ankylosaurus-magniventris-armoredclub-imagegen-v2.png"
PREVIOUS = ASSET_ROOT / "ankylosaurus-magniventris-singleclub-imagegen-v1.png"
LOW_WIDE = ASSET_ROOT / "ankylosaurus-magniventris-lowwide-imagegen-v1.png"
STRUCTURE_GUIDE = ASSET_ROOT / "ankylosaurus-magniventris.png"
WIDE_COMPARISON = ASSET_ROOT / "ankylosaurus-magniventris-singleclub-wide-v1.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v7.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-lowcompact-crops-v2.png"


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
            "title": "selected imagegen v2: low compact single club",
            "note": "Best current read: low wide armor, blunt head, four visible feet, one attached oval tail club.",
        },
        {
            "path": ARMORED_CLUB,
            "title": "v2 comparison: armored body / longer tail",
            "note": "Strong head, feet, and club, but the tail/body read is a little less compact.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: single-club imagegen v1",
            "note": "Clear single club and armor, but head/foot/body read is weaker than the compact v2 candidate.",
        },
        {
            "path": LOW_WIDE,
            "title": "previous low-wide comparison",
            "note": "Good broad body, but the tail club can read double-lobed/oversized.",
        },
        {
            "path": WIDE_COMPARISON,
            "title": "wide single-club comparison",
            "note": "Useful same-direction comparison; feet and skull are less crisp than v2.",
        },
        {
            "path": STRUCTURE_GUIDE,
            "title": "structure guide / original target",
            "note": "Project-owned tail-club and low-armor target retained for future ControlNet or i2i routes.",
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
        ("selected full body", SELECTED, (0, 0, 1694, 928)),
        ("selected blunt armored head", SELECTED, (20, 320, 390, 650)),
        ("selected armor plates", SELECTED, (420, 230, 1120, 590)),
        ("selected single attached club", SELECTED, (1280, 390, 1694, 690)),
        ("selected four visible feet", SELECTED, (280, 570, 1190, 850)),
        ("v2 comparison longer-tail risk", ARMORED_CLUB, (0, 0, 1694, 928)),
        ("previous primary head/club", PREVIOUS, (0, 0, 1536, 900)),
        ("previous double-lobed club risk", LOW_WIDE, (0, 260, 430, 610)),
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
    for path in (SELECTED, ARMORED_CLUB, PREVIOUS, LOW_WIDE, STRUCTURE_GUIDE, WIDE_COMPARISON):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
