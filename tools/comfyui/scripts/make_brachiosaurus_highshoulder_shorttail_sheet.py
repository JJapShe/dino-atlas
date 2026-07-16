from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-shorttail-imagegen-v3.png"
TALL_FORELIMB = ASSET_ROOT / "brachiosaurus-altithorax-tallforelimb-shorttail-imagegen-v3.png"
PREVIOUS = ASSET_ROOT / "brachiosaurus-altithorax-balancedneck-imagegen-v2.png"
MODERATE = ASSET_ROOT / "brachiosaurus-altithorax-moderateneck-comparison-v2.png"
HIGHSHOULDER = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-imagegen-v1.png"
REALVIS = ASSET_ROOT / "brachiosaurus-altithorax-realvis-v2.png"

CONTACT_OUT = ASSET_ROOT / "brachiosaurus-review-options-v6.png"
CROP_OUT = ASSET_ROOT / "brachiosaurus-highshoulder-shorttail-crops-v3.png"


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
            "title": "selected v3: high shoulder / shorter-tail attempt",
            "note": "Best current Brachiosaurus read: taller forelimbs, high shoulders, rising neck, and full feet.",
        },
        {
            "path": TALL_FORELIMB,
            "title": "v3 tall-forelimb comparison",
            "note": "Very similar high-shoulder read; kept below selected because feet/tail edge are slightly less clean.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v2",
            "note": "Balanced neck and full body, but the shoulder/forelimb dominance is weaker at app scale.",
        },
        {
            "path": MODERATE,
            "title": "v2 moderate-neck comparison",
            "note": "Useful less-vertical neck, but lower shoulder read and longer tail drift more diplodocid.",
        },
        {
            "path": HIGHSHOULDER,
            "title": "v1 high-shoulder comparison",
            "note": "Strong high-shoulder intent, but the neck is too vertical and giraffe-like for first use.",
        },
        {
            "path": REALVIS,
            "title": "old RealVis comparison",
            "note": "Natural scene comparison retained below current imagegen candidates.",
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
        ("selected v3 full body", SELECTED, (0, 0, 1570, 1002)),
        ("selected v3 small head / nasal arch", SELECTED, (105, 80, 455, 250)),
        ("selected v3 rising neck", SELECTED, (170, 120, 760, 640)),
        ("selected v3 high shoulders", SELECTED, (515, 455, 990, 790)),
        ("selected v3 front vs hind feet", SELECTED, (470, 720, 1110, 980)),
        ("selected v3 tail length risk", SELECTED, (880, 535, 1570, 845)),
        ("v3 tall-forelimb comparison", TALL_FORELIMB, (0, 0, 1639, 960)),
        ("previous v2 full body", PREVIOUS, (0, 0, 1692, 929)),
        ("previous v2 tail length risk", PREVIOUS, (970, 460, 1692, 735)),
        ("v1 vertical-neck risk", HIGHSHOULDER, (0, 0, 1691, 930)),
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
    for path in (SELECTED, TALL_FORELIMB, PREVIOUS, MODERATE, HIGHSHOULDER, REALVIS):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
