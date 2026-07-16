from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "plateosaurus-engelhardti-herbivore-imagegen-v1.png"
ALT = ASSET_ROOT / "plateosaurus-engelhardti-herbivore-imagegen-alt-v1.png"
TRIPOD = ASSET_ROOT / "plateosaurus-engelhardti-tripod-controlnet-v1.png"
THUMBTIP = ASSET_ROOT / "plateosaurus-engelhardti-thumbtip-cue-v1.png"
FORELIMB_REF = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-ref-ipcontrol-v1.png"
SIX_LEG_REJECTION = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

CONTACT_OUT = ASSET_ROOT / "plateosaurus-review-options-v9.png"
CROP_OUT = ASSET_ROOT / "plateosaurus-herbivore-crops-v1.png"


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
            "title": "selected imagegen v1: herbivore body",
            "note": "Better low herbivore head, forward neck, lifted hands, and full tail than the old primary.",
        },
        {
            "path": ALT,
            "title": "imagegen alt: similar body, weaker leg read",
            "note": "Useful comparison, but hind legs overlap more and hand anatomy is busier.",
        },
        {
            "path": TRIPOD,
            "title": "previous primary: count-safe tripod",
            "note": "Still useful for limb-count comparison, but head and hand cues are weaker.",
        },
        {
            "path": THUMBTIP,
            "title": "thumb-tip cue comparison",
            "note": "Tiny hand cue preserved limb count but stayed too subtle for a first image.",
        },
        {
            "path": FORELIMB_REF,
            "title": "forelimb-reference IP-Control comparison",
            "note": "Hands and herbivore head improved, but hind-leg contact weakened.",
        },
        {
            "path": SIX_LEG_REJECTION,
            "title": "rejected: six-leg forelimb inpaint",
            "note": "Kept as a negative gate: clearer hand cue is not acceptable if it creates extra legs.",
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
        ("full selected body", SELECTED, (0, 0, 1536, 1024)),
        ("low herbivore head / forward neck", SELECTED, (60, 170, 500, 420)),
        ("lifted forelimbs / thumb-claw cue", SELECTED, (440, 430, 710, 680)),
        ("two large hind legs / feet", SELECTED, (650, 515, 990, 910)),
        ("previous primary forelimb", TRIPOD, (315, 410, 590, 700)),
        ("six-leg rejection comparison", SIX_LEG_REJECTION, (315, 410, 590, 700)),
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
    for path in (SELECTED, ALT, TRIPOD, THUMBTIP, FORELIMB_REF, SIX_LEG_REJECTION):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
