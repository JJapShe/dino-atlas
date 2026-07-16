from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-lowbody-toe-frame-imagegen-v7.png"
CLOSEDBEAK_BODY = ASSET_ROOT / "triceratops-horridus-closedbeak-body-comparison-v7.png"
MOUTHGAP = ASSET_ROOT / "triceratops-horridus-mouthgap-comparison-v7.png"
PREVIOUS = ASSET_ROOT / "triceratops-horridus-closedbeak-toegate-imagegen-v6.png"
PREVIOUS_CROP = ASSET_ROOT / "triceratops-closedbeak-toegate-crops-v6.png"
LONGBODY_V5 = ASSET_ROOT / "triceratops-horridus-longbody-toes-imagegen-v5.png"
GUIDE = ASSET_ROOT / "triceratops-horridus-ceratopsian-reference-guide-v1.png"
RHINO_REJECTION = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v13.png"
CROP_OUT = ASSET_ROOT / "triceratops-lowbody-toe-frame-crops-v7.png"


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
            "title": "selected v7: low body / toe-frame",
            "note": "Best current body/feet read: low long ceratopsian torso, long tail, three horns, frill, and visible toes.",
        },
        {
            "path": CLOSEDBEAK_BODY,
            "title": "v7 closed-beak body comparison",
            "note": "Strong closed-beak cue, but the body is a little rounder and less low/long than selected v7.",
        },
        {
            "path": MOUTHGAP,
            "title": "v7 mouth-gap comparison",
            "note": "Useful long body and feet, but the beak gap is too open for the representative slot.",
        },
        {
            "path": PREVIOUS,
            "title": "previous primary v6",
            "note": "Good closed-beak and three-horn gate; kept below v7 because the torso is rounder and less dinosaur-long.",
        },
        {
            "path": PREVIOUS_CROP,
            "title": "previous v6 crop audit",
            "note": "Use below v7 to compare old skull/frill, beak, feet, tail, and torso-risk crops.",
        },
        {
            "path": LONGBODY_V5,
            "title": "older long-body v5 comparison",
            "note": "Useful toe and long-tail comparison retained below the v7 and v6 candidates.",
        },
        {
            "path": GUIDE,
            "title": "ceratopsian structure guide",
            "note": "Project-owned target for future ControlNet, mini-LoRA, or reference-conditioned i2i passes.",
        },
        {
            "path": RHINO_REJECTION,
            "title": "rhino-drift rejection",
            "note": "Failure gate: reject mammal torso, rhino shoulder, hoof-like feet, weak beak, or hidden dinosaur tail.",
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
        ("selected v7 full body", SELECTED, (0, 0, 1672, 941)),
        ("selected v7 skull-attached frill", SELECTED, (55, 130, 690, 575)),
        ("selected v7 three horns / beak", SELECTED, (65, 175, 560, 560)),
        ("selected v7 front non-hoofed toes", SELECTED, (330, 650, 780, 875)),
        ("selected v7 rear non-hoofed toes", SELECTED, (750, 620, 1250, 870)),
        ("selected v7 low body / long tail", SELECTED, (500, 285, 1660, 675)),
        ("v7 closed-beak comparison", CLOSEDBEAK_BODY, (55, 145, 700, 610)),
        ("v7 closed-beak foot/body", CLOSEDBEAK_BODY, (295, 560, 1260, 880)),
        ("v7 mouth-gap comparison", MOUTHGAP, (60, 145, 700, 610)),
        ("previous v6 full body", PREVIOUS, (0, 0, 1672, 941)),
        ("previous v6 head / beak gate", PREVIOUS, (55, 130, 640, 575)),
        ("rhino-drift rejection", RHINO_REJECTION, (0, 0, 1536, 1024)),
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
        CLOSEDBEAK_BODY,
        MOUTHGAP,
        PREVIOUS,
        PREVIOUS_CROP,
        LONGBODY_V5,
        GUIDE,
        RHINO_REJECTION,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
