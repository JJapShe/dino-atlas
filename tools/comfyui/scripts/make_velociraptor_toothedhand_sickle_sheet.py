from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "velociraptor-mongoliensis-toothedhand-sickle-imagegen-v8.png"
BIRDHEAD_RISK = ASSET_ROOT / "velociraptor-mongoliensis-birdhead-risk-comparison-v8.png"
WINGARM_RISK = ASSET_ROOT / "velociraptor-mongoliensis-wingarm-risk-comparison-v8.png"
PREVIOUS = ASSET_ROOT / "velociraptor-mongoliensis-grounded-sickle-imagegen-v7.png"
PREVIOUS_CROP = ASSET_ROOT / "velociraptor-grounded-sickle-crops-v7.png"
BIGHOOK_V7 = ASSET_ROOT / "velociraptor-mongoliensis-bighook-comparison-v7.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"
SD15_REJECTION = ASSET_ROOT / "velociraptor-sd15-lora-i2i-v8-rejection-sheet.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v14.png"
CROP_OUT = ASSET_ROOT / "velociraptor-toothedhand-sickle-crops-v8.png"


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
            "title": "selected v8: toothed head / visible hands / sickle claws",
            "note": "Best current app read: non-beak toothed snout, visible folded hands, full tail, and attached sickle cues.",
        },
        {
            "path": BIRDHEAD_RISK,
            "title": "v8 bird-head risk comparison",
            "note": "Good low body and grounded feet, but the head still drifts closer to a bird-like profile.",
        },
        {
            "path": WINGARM_RISK,
            "title": "v8 wing-arm risk comparison",
            "note": "Hands are more visible, but the tall stance and arm feathers read too much like bird wings.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v7",
            "note": "Strong grounded feet and tail; kept below v8 because v8 improves the toothed snout and visible hand cue.",
        },
        {
            "path": BIGHOOK_V7,
            "title": "v7 big-hook comparison",
            "note": "Strong head/body comparison but sickle claws read larger and more hook-like than desired.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v7 crop audit",
            "note": "Use below v8 to compare old snout, forelimb, foot, sickle, and tail/body balance.",
        },
        {
            "path": SD15_REJECTION,
            "title": "SD1.5 Velociraptor LoRA+i2i rejection",
            "note": "Dedicated Velociraptor LoRA kept the guide too flat and bird-like; do not promote this route.",
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
        ("selected v8 full body", SELECTED, (0, 0, 1672, 941)),
        ("selected v8 toothed non-beak snout", SELECTED, (45, 275, 475, 470)),
        ("selected v8 visible folded hands", SELECTED, (400, 445, 685, 655)),
        ("selected v8 front foot / attached sickle", SELECTED, (620, 675, 960, 880)),
        ("selected v8 rear foot / attached sickle", SELECTED, (780, 625, 1110, 855)),
        ("selected v8 tail / body balance", SELECTED, (790, 330, 1640, 540)),
        ("v8 bird-head risk full body", BIRDHEAD_RISK, (0, 0, 1672, 941)),
        ("v8 wing-arm risk full body", WINGARM_RISK, (0, 0, 1672, 941)),
        ("previous v7 full body", PREVIOUS, (0, 0, 1719, 915)),
        ("previous v7 foot / claw crops", PREVIOUS_CROP, (0, 560, 760, 1300)),
        ("SD1.5 LoRA+i2i rejection sheet", SD15_REJECTION, (0, 0, 768, 596)),
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
        BIRDHEAD_RISK,
        WINGARM_RISK,
        PREVIOUS,
        PREVIOUS_CROP,
        BIGHOOK_V7,
        FOOT_GUIDE,
        SD15_REJECTION,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
