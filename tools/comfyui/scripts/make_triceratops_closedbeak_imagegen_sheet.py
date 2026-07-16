from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-closedbeak-imagegen-v2.png"
FRILL_TOE = ASSET_ROOT / "triceratops-horridus-frilltoe-imagegen-v2.png"
PREVIOUS = ASSET_ROOT / "triceratops-horridus-sideprofile-imagegen-v1.png"
GUIDE = ASSET_ROOT / "triceratops-horridus-ceratopsian-reference-guide-v1.png"
MUTED_FRILL = ASSET_ROOT / "triceratops-horridus-frill-muted-v1.png"
RHINO_REJECT = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v8.png"
CROP_OUT = ASSET_ROOT / "triceratops-closedbeak-crops-v2.png"


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
            "title": "selected imagegen v2: closed beak / skull frill",
            "note": "Best current Triceratops read: three horns, closed beak, skull-attached frill, long tail, non-hoofed toes.",
        },
        {
            "path": FRILL_TOE,
            "title": "v2 comparison: strong frill and toes / open mouth",
            "note": "Strong ceratopsian read, but the open mouth is less calm for the app representative.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: strict side-profile imagegen v1",
            "note": "Clear identity, but smaller frill detail and toe/frill-edge review stayed pending.",
        },
        {
            "path": GUIDE,
            "title": "ceratopsian structure guide",
            "note": "Project-owned structure target for three horns, skull-attached frill, tail, and non-hoofed feet.",
        },
        {
            "path": MUTED_FRILL,
            "title": "previous muted-frill comparison",
            "note": "Useful history, but the frill still reads decorative and the body is less immediately ceratopsian.",
        },
        {
            "path": RHINO_REJECT,
            "title": "rhino-drift rejection",
            "note": "Kept as a failure gate: mammal body, hoof-like feet, and weak skull-frill connection.",
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
        ("selected full body", SELECTED, (0, 0, 1694, 929)),
        ("selected head + skull frill", SELECTED, (930, 80, 1590, 560)),
        ("selected three horns + closed beak", SELECTED, (1080, 140, 1665, 520)),
        ("selected front and rear feet", SELECTED, (360, 610, 1370, 900)),
        ("selected tail + hip", SELECTED, (0, 350, 560, 670)),
        ("v2 comparison open-mouth risk", FRILL_TOE, (0, 155, 650, 610)),
        ("previous primary frill/toes", PREVIOUS, (0, 0, 720, 720)),
        ("rhino-drift body rejection", RHINO_REJECT, (0, 130, 850, 690)),
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
    for path in (SELECTED, FRILL_TOE, PREVIOUS, GUIDE, MUTED_FRILL, RHINO_REJECT):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
