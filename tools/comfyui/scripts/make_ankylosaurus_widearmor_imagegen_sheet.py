from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "ankylosaurus-magniventris-widearmor-imagegen-v3.png"
WIDE_COMPARISON = ASSET_ROOT / "ankylosaurus-magniventris-widearmor-comparison-imagegen-v3.png"
LOW_COMPACT = ASSET_ROOT / "ankylosaurus-magniventris-lowcompact-imagegen-v2.png"
ARMORED_CLUB = ASSET_ROOT / "ankylosaurus-magniventris-armoredclub-imagegen-v2.png"
SINGLE_CLUB = ASSET_ROOT / "ankylosaurus-magniventris-singleclub-imagegen-v1.png"
LOW_WIDE = ASSET_ROOT / "ankylosaurus-magniventris-lowwide-imagegen-v1.png"
STRUCTURE_GUIDE = ASSET_ROOT / "ankylosaurus-magniventris.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v8.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-widearmor-crops-v3.png"


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
            "title": "selected imagegen v3: wide armor / single club",
            "note": "Best current read: broader skull and shoulders, four feet, low armor rows, one attached oval club.",
        },
        {
            "path": WIDE_COMPARISON,
            "title": "v3 comparison: longer low body",
            "note": "Strong low-body silhouette, but the longer tail/body read stays below the selected candidate.",
        },
        {
            "path": LOW_COMPACT,
            "title": "previous primary: low-compact v2",
            "note": "Still useful; v3 improves the app-scale shoulder, skull, and armor identity read.",
        },
        {
            "path": ARMORED_CLUB,
            "title": "v2 comparison: armored body / longer tail",
            "note": "Strong head, feet, and club, but less compact and less familiar at app scale.",
        },
        {
            "path": SINGLE_CLUB,
            "title": "older single-club imagegen v1",
            "note": "Single club and armor are visible, but head, feet, and body mass are weaker.",
        },
        {
            "path": LOW_WIDE,
            "title": "older low-wide comparison",
            "note": "Broad body target, but the tail club can read double-lobed or oversized.",
        },
        {
            "path": STRUCTURE_GUIDE,
            "title": "structure guide / original target",
            "note": "Project-owned reference target retained for future ControlNet or i2i routes.",
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
        ("selected full body", SELECTED, (0, 150, 1536, 900)),
        ("selected broad blunt head", SELECTED, (0, 450, 390, 735)),
        ("selected shoulder armor rows", SELECTED, (360, 260, 960, 610)),
        ("selected single attached club", SELECTED, (1170, 390, 1536, 665)),
        ("selected four planted feet", SELECTED, (240, 600, 1120, 865)),
        ("v3 comparison longer-body risk", WIDE_COMPARISON, (0, 0, 1774, 887)),
        ("previous primary v2 full body", LOW_COMPACT, (0, 0, 1692, 929)),
        ("older double-lobed club risk", LOW_WIDE, (0, 260, 430, 610)),
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
        WIDE_COMPARISON,
        LOW_COMPACT,
        ARMORED_CLUB,
        SINGLE_CLUB,
        LOW_WIDE,
        STRUCTURE_GUIDE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
