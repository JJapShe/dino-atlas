from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "brachiosaurus-altithorax-balancedneck-imagegen-v2.png"
MODERATE = ASSET_ROOT / "brachiosaurus-altithorax-moderateneck-comparison-v2.png"
PREVIOUS = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-imagegen-v1.png"
REALVIS = ASSET_ROOT / "brachiosaurus-altithorax-realvis-v2.png"
SIDEPROFILE = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-sideprofile-v1.png"
CONTROLNET = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-controlnet-v1.png"

CONTACT_OUT = ASSET_ROOT / "brachiosaurus-review-options-v5.png"
CROP_OUT = ASSET_ROOT / "brachiosaurus-balancedneck-crops-v2.png"


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
            "title": "selected imagegen v2: balanced neck / high shoulder",
            "note": "Keeps high shoulders and taller forelimbs while reducing the vertical giraffe-neck read.",
        },
        {
            "path": MODERATE,
            "title": "v2 comparison: moderate forward neck",
            "note": "Natural head-neck angle, but the body reads more diplodocid and the tail is too long.",
        },
        {
            "path": PREVIOUS,
            "title": "previous first: strict high-shoulder v1",
            "note": "Strong shoulder cue, but neck height is more dramatic and the skull/tail need tighter review.",
        },
        {
            "path": REALVIS,
            "title": "older RealVis comparison",
            "note": "Polished scene, but side-profile shoulder slope and rear foot review are weaker.",
        },
        {
            "path": SIDEPROFILE,
            "title": "high-shoulder side-profile comparison",
            "note": "Useful structure comparison; head and rear-foot visibility stay under review.",
        },
        {
            "path": CONTROLNET,
            "title": "high-shoulder ControlNet comparison",
            "note": "Locks shoulder height, but the render is flatter and less natural.",
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
        ("full selected body", SELECTED, (0, 0, 1692, 929)),
        ("compact head / nasal arch cue", SELECTED, (80, 40, 520, 330)),
        ("balanced high neck", SELECTED, (70, 80, 720, 560)),
        ("high shoulders / trunk slope", SELECTED, (460, 300, 1060, 690)),
        ("front limbs vs hind limbs", SELECTED, (480, 490, 1180, 900)),
        ("tail length risk", SELECTED, (980, 370, 1692, 710)),
        ("previous vertical-neck comparison", PREVIOUS, (0, 0, 1536, 1024)),
        ("moderate-neck comparison", MODERATE, (0, 0, 1774, 887)),
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
    for path in (SELECTED, MODERATE, PREVIOUS, REALVIS, SIDEPROFILE, CONTROLNET):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
