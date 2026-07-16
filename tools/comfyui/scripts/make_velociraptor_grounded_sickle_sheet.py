from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-grounded-sickle-imagegen-v7.png"
BIGHOOK = ASSET_ROOT / "velociraptor-mongoliensis-bighook-comparison-v7.png"
OPENMOUTH = ASSET_ROOT / "velociraptor-mongoliensis-openmouth-grounded-comparison-v7.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-restrained-sickle-imagegen-v6.png"
PREVIOUS_CROP = ASSET_ROOT / "velociraptor-restrained-sickle-crops-v6.png"
FOLDEDARM_V6 = ASSET_ROOT / "velociraptor-mongoliensis-foldedarm-footreview-imagegen-v6.png"
COMPACTARM_V5 = ASSET_ROOT / "velociraptor-mongoliensis-compactarm-toothedsickle-imagegen-v5.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v13.png"
CROP_OUT = ASSET_ROOT / "velociraptor-grounded-sickle-crops-v7.png"


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
            "title": "selected v7: grounded sickle / toothed head",
            "note": "Best current balance: less bird-like toothed head, grounded feet, folded arms, and attached sickle cues.",
        },
        {
            "path": BIGHOOK,
            "title": "v7 big-hook comparison",
            "note": "Strong head and body, but sickle claws remain larger and more hook-like than selected v7.",
        },
        {
            "path": OPENMOUTH,
            "title": "v7 open-mouth grounded comparison",
            "note": "Grounded feet are useful, but the mouth is too open and forelimb visibility is weaker.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v6",
            "note": "Good tooth/head gate, retained below v7 because the foot hooks read more floating and oversized.",
        },
        {
            "path": FOLDEDARM_V6,
            "title": "v6 folded-arm foot review",
            "note": "Useful body/tail comparison with weaker claw and forelimb balance.",
        },
        {
            "path": COMPACTARM_V5,
            "title": "previous compact-arm v5",
            "note": "Strong teeth and paired sickle cues, but arm feathers read more wing-like.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v6 crop audit",
            "note": "Use below v7 to compare old head, forelimb, foot, sickle, and tail/body balance.",
        },
        {
            "path": FOOT_GUIDE,
            "title": "foot reference guide",
            "note": "Project-owned target for later dromaeosaur LoRA or reference-conditioned i2i foot passes.",
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
        ("selected v7 full body", SELECTED, (0, 0, 1719, 915)),
        ("selected v7 toothed non-beak snout", SELECTED, (75, 165, 520, 345)),
        ("selected v7 compact folded forelimbs", SELECTED, (425, 430, 680, 645)),
        ("selected v7 front foot / attached sickle", SELECTED, (585, 630, 875, 830)),
        ("selected v7 rear foot / attached sickle", SELECTED, (805, 600, 1115, 830)),
        ("selected v7 long tail / body balance", SELECTED, (835, 290, 1715, 520)),
        ("v7 big-hook claw risk", BIGHOOK, (560, 600, 1015, 845)),
        ("v7 open-mouth risk", OPENMOUTH, (70, 150, 555, 365)),
        ("previous v6 full body", PREVIOUS, (0, 0, 1774, 887)),
        ("previous v6 front foot / sickle", PREVIOUS, (620, 600, 910, 820)),
        ("previous v6 rear foot / sickle", PREVIOUS, (805, 505, 1105, 775)),
        ("foot reference guide", FOOT_GUIDE, (0, 0, 1536, 1024)),
    ]

    cols = 2
    thumb_w = 380
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
    for path in (
        SELECTED,
        BIGHOOK,
        OPENMOUTH,
        PREVIOUS,
        PREVIOUS_CROP,
        FOLDEDARM_V6,
        COMPACTARM_V5,
        FOOT_GUIDE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
