from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
GROUNDED_FOOT = ASSET_ROOT / "velociraptor-mongoliensis-grounded-foot-comparison-v9.png"
LARGE_CLAW_RISK = ASSET_ROOT / "velociraptor-mongoliensis-large-claw-risk-comparison-v9.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-toothedhand-sickle-imagegen-v8.png"
PREVIOUS_CROP = ASSET_ROOT / "velociraptor-toothedhand-sickle-crops-v8.png"
BIRDHEAD_RISK = ASSET_ROOT / "velociraptor-mongoliensis-birdhead-risk-comparison-v8.png"
WINGARM_RISK = ASSET_ROOT / "velociraptor-mongoliensis-wingarm-risk-comparison-v8.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v15.png"
CROP_OUT = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"


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
            "title": "selected v9: smaller attached sickle claws",
            "note": "Best current foot-scale read: restrained raised claws, toothed snout, folded hands, feathered body, and full tail.",
        },
        {
            "path": GROUNDED_FOOT,
            "title": "v9 grounded-foot comparison",
            "note": "Useful foot/body comparison, but the open mouth and head/neck read are weaker than the selected v9.",
        },
        {
            "path": LARGE_CLAW_RISK,
            "title": "v9 large-claw risk comparison",
            "note": "Good feather and tail cue, but the sickle claws get too large and hook-like again.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v8",
            "note": "Strong head/hand/tail read retained below v9 because the sickle claws are more oversized.",
        },
        {
            "path": BIRDHEAD_RISK,
            "title": "v8 bird-head risk comparison",
            "note": "Good low body and grounded feet, but the head still drifts closer to a bird-like profile.",
        },
        {
            "path": WINGARM_RISK,
            "title": "v8 wing-arm risk comparison",
            "note": "Hands are visible, but the arm feathers and stance read too much like bird wings.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v8 crop audit",
            "note": "Use below v9 to compare the older snout, hand, foot, sickle-claw, and tail/body balance.",
        },
        {
            "path": FOOT_GUIDE,
            "title": "foot reference guide",
            "note": "Project-owned target for a future dromaeosaur LoRA or reference-conditioned i2i foot pass.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 286
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
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v9 full body", SELECTED, (0, 0, 1672, 941)),
        ("selected v9 toothed non-beak snout", SELECTED, (25, 230, 480, 430)),
        ("selected v9 folded hands", SELECTED, (420, 455, 650, 660)),
        ("selected v9 front foot / smaller sickle", SELECTED, (560, 670, 880, 910)),
        ("selected v9 rear foot / smaller sickle", SELECTED, (720, 640, 1010, 900)),
        ("selected v9 tail / body balance", SELECTED, (820, 330, 1640, 545)),
        ("v9 grounded-foot comparison", GROUNDED_FOOT, (0, 0, 1672, 941)),
        ("v9 large-claw risk comparison", LARGE_CLAW_RISK, (0, 0, 1672, 941)),
        ("previous v8 full body", PREVIOUS, (0, 0, 1672, 941)),
        ("previous v8 foot crops", PREVIOUS_CROP, (380, 285, 760, 860)),
        ("previous v8 hand/head crops", PREVIOUS_CROP, (0, 250, 760, 570)),
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
        GROUNDED_FOOT,
        LARGE_CLAW_RISK,
        PREVIOUS,
        PREVIOUS_CROP,
        BIRDHEAD_RISK,
        WINGARM_RISK,
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
