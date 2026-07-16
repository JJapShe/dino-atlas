import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "theropod_tyrannosaurus" / "review"

CURRENT = ASSET_ROOT / "tyrannosaurus-rex-twofinger-hand-i2i-v4.png"
CURRENT_CROPS = ASSET_ROOT / "tyrannosaurus-twofinger-hand-i2i-crops-v4.png"
GUIDE = ASSET_ROOT / "tyrannosaurus-rex-twofinger-bodylock-guide-v1.png"
REJECTED = ASSET_ROOT / "tyrannosaurus-rex-v4source-controlnet-rejected-v9.png"
VISIBLE_ARMS_RISK = ASSET_ROOT / "tyrannosaurus-rex-visiblearms-comparison-v3.png"

CONTACT_OUT = ASSET_ROOT / "tyrannosaurus-controlnet-v9-rejection-sheet.png"
CROP_OUT = ASSET_ROOT / "tyrannosaurus-controlnet-v9-rejection-crops.png"
REVIEW_OUT = REVIEW_ROOT / "trex_v4source_controlnet_v9_review.json"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
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
            continue
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
            "path": CURRENT,
            "title": "current v4: keep first",
            "note": "Best current representative: massive head, heavy tail, tiny chest arms, and compact two-finger hand cue.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v4 crop gate",
            "note": "Use this to compare the head, two-finger hands, feet, tail, and previous hand-risk comparisons.",
        },
        {
            "path": GUIDE,
            "title": "two-finger body-lock guide",
            "note": "Reference target for tiny arms and exactly two fingers per visible hand before any future polish.",
        },
        {
            "path": REJECTED,
            "title": "reject v9: v4-source ControlNet",
            "note": "Reject: forelimbs enlarge, hand count is less reliable, color drifts pale, and the scene loses the v4 dry profile.",
        },
        {
            "path": VISIBLE_ARMS_RISK,
            "title": "older visible-arm risk comparison",
            "note": "Keep nearby as the failure mode: making arms more visible can weaken the strict tiny-arm/two-finger gate.",
        },
    ]

    cols = 2
    thumb_w = 520
    thumb_h = 330
    label_h = 72
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:80], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 30), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("current v4 full body - keep first", CURRENT, (0, 0, 1774, 887)),
        ("current v4 tiny arms", CURRENT, (360, 320, 650, 650)),
        ("current v4 two-finger hands", CURRENT, (420, 380, 620, 650)),
        ("current v4 head", CURRENT, (85, 135, 500, 380)),
        ("reject v9 full body", REJECTED, (0, 0, 1152, 768)),
        ("reject v9 enlarged arms", REJECTED, (260, 300, 520, 585)),
        ("reject v9 hand ambiguity", REJECTED, (300, 395, 510, 610)),
        ("reject v9 pale head / open mouth", REJECTED, (50, 100, 450, 360)),
        ("body-lock guide", GUIDE, (0, 0, 1152, 768)),
        ("older visible-arm risk", VISIBLE_ARMS_RISK, (0, 0, 1672, 941)),
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
        draw.text((8, thumb_h + 10), label[:58], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def write_review_json():
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "tyrannosaurus-rex",
                "experiment": "v4source_controlnet_v9",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "outputImage": str(REJECTED.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "rejected",
                "reasons": [
                    "forelimbs enlarge toward allosaur-like arm scale",
                    "visible hand shape is less reliable for the exact two-finger gate",
                    "body color and setting drift away from the current v4 representative",
                    "no clear improvement over the current v4 primary",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Use local low-denoise hand masking or style-preserving i2i; do not promote whole-body ControlNet from the natural v4 source if it enlarges the arms.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, REJECTED, VISIBLE_ARMS_RISK):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    write_review_json()
    print(CONTACT_OUT)
    print(CROP_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
