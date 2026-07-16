from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "plateosaurus-engelhardti-cleanlimbs-imagegen-v2.png"
SEPARATED = ASSET_ROOT / "plateosaurus-engelhardti-separatedlegs-imagegen-v2.png"
THUMBSMALL = ASSET_ROOT / "plateosaurus-engelhardti-thumbsmall-imagegen-v2.png"
PREVIOUS = ASSET_ROOT / "plateosaurus-engelhardti-herbivore-imagegen-v1.png"
TRIPOD = ASSET_ROOT / "plateosaurus-engelhardti-tripod-controlnet-v1.png"
SIX_LEG_REJECTION = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

CONTACT_OUT = ASSET_ROOT / "plateosaurus-review-options-v10.png"
CROP_OUT = ASSET_ROOT / "plateosaurus-cleanlimbs-crops-v2.png"


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
            "title": "selected imagegen v2: clean limbs / herbivore head",
            "note": "Best current balance: low herbivore head, small lifted hands, separated hind legs, full tail.",
        },
        {
            "path": SEPARATED,
            "title": "v2 comparison: best hind-leg separation / big hands",
            "note": "Good leg stride, but the hands read too large and predatory for first position.",
        },
        {
            "path": THUMBSMALL,
            "title": "v2 comparison: smaller hands / weaker leg separation",
            "note": "Hands are calmer, but hind legs overlap more and the limb count is less readable.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary: herbivore imagegen v1",
            "note": "Good herbivore identity, but hind legs overlap more and hands look more hook-like.",
        },
        {
            "path": TRIPOD,
            "title": "older count-safe tripod comparison",
            "note": "Useful limb-count comparison, but head and hand cues are weaker than the selected v2.",
        },
        {
            "path": SIX_LEG_REJECTION,
            "title": "rejected: six-leg forelimb inpaint",
            "note": "Kept as a negative gate: clearer hand cue is not acceptable if it creates extra legs.",
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
        ("selected herbivore head", SELECTED, (30, 170, 500, 405)),
        ("selected lifted small hands", SELECTED, (435, 445, 645, 680)),
        ("selected separated hind legs", SELECTED, (710, 500, 1170, 850)),
        ("selected full tail", SELECTED, (900, 330, 1694, 575)),
        ("separated pass large-hand risk", SEPARATED, (400, 430, 700, 700)),
        ("previous primary overlap/hands", PREVIOUS, (410, 390, 1030, 900)),
        ("six-leg rejection comparison", SIX_LEG_REJECTION, (315, 410, 590, 700)),
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
    for path in (SELECTED, SEPARATED, THUMBSMALL, PREVIOUS, TRIPOD, SIX_LEG_REJECTION):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
