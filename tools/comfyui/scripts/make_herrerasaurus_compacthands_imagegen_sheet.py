from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png"
BALANCED = ASSET_ROOT / "herrerasaurus-ischigualastensis-balancedhands-imagegen-v2.png"
PREVIOUS_SELECTED = ASSET_ROOT / "herrerasaurus-ischigualastensis-strict-imagegen-alt-v1.png"
FIRST_PASS = ASSET_ROOT / "herrerasaurus-ischigualastensis-strict-imagegen-v1.png"
CLOSED_JAW_HEADBLEND = ASSET_ROOT / "herrerasaurus-ischigualastensis-closedjaw-headblend-v1.png"
LONG_ARMS = ASSET_ROOT / "herrerasaurus-ischigualastensis-longarms-ipcontrol-v1.png"

CONTACT_OUT = ASSET_ROOT / "herrerasaurus-review-options-v7.png"
CROP_OUT = ASSET_ROOT / "herrerasaurus-compacthands-crops-v2.png"


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
            "title": "selected imagegen v2: compact hands",
            "note": "Best balance so far: calmer closed head, full tail, dry ground, two hind legs, and smaller folded hands.",
        },
        {
            "path": BALANCED,
            "title": "v2 comparison: balanced arm length",
            "note": "Polished body and forelimb length, but the hand can read as too many long fingers at close review.",
        },
        {
            "path": PREVIOUS_SELECTED,
            "title": "previous primary: strict compact v1",
            "note": "Good two-leg body gate; smaller scene scale and dangling hand claws are weaker than selected v2.",
        },
        {
            "path": FIRST_PASS,
            "title": "strict imagegen v1: long-hand risk",
            "note": "Strong side-profile stance, but the hand claws are too long and remain a reject gate.",
        },
        {
            "path": CLOSED_JAW_HEADBLEND,
            "title": "closed-jaw head blend comparison",
            "note": "Useful previous body gate, but the head and forelimbs are less readable at app scale.",
        },
        {
            "path": LONG_ARMS,
            "title": "long-arm IP-Control comparison",
            "note": "Keeps the long-arm target visible, but open mouth and head bulk are less representative.",
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
        ("selected full body", SELECTED, (0, 0, 1774, 887)),
        ("selected closed head", SELECTED, (70, 175, 485, 365)),
        ("selected compact hands", SELECTED, (430, 405, 665, 635)),
        ("selected two hind legs / feet", SELECTED, (695, 440, 1085, 800)),
        ("selected full tail", SELECTED, (850, 315, 1774, 525)),
        ("balanced v2 hand-count risk", BALANCED, (420, 395, 700, 665)),
        ("previous primary hands", PREVIOUS_SELECTED, (270, 465, 570, 760)),
        ("long-arm comparison", LONG_ARMS, (610, 260, 920, 600)),
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
    for path in (SELECTED, BALANCED, PREVIOUS_SELECTED, FIRST_PASS, CLOSED_JAW_HEADBLEND, LONG_ARMS):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
