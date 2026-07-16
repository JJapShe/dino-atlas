import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

CURRENT = ASSET_ROOT / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
CURRENT_CROPS = ASSET_ROOT / "plateosaurus-singleforelimb-smallhand-crops-v3.png"
GUIDE = ASSET_ROOT / "plateosaurus-engelhardti-bodylock-guide-v1.png"
CONTROL_V13 = ASSET_ROOT / "plateosaurus-engelhardti-bodylock-control-comparison-v13.png"
SIX_LEG_REJECTION = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

CONTACT_OUT = ASSET_ROOT / "plateosaurus-review-options-v13.png"
CROP_OUT = ASSET_ROOT / "plateosaurus-bodylock-control-crops-v13.png"
REVIEW_OUT = REVIEW_ROOT / "plateosaurus_bodylock_control_v13_review.json"


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
            "title": "current v3: keep first",
            "note": "Best natural candidate: low herbivore head, full tail, two grounded hind legs, and one lifted forelimb cue.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v3 crop gate",
            "note": "Use this to review head, lifted hand/thumb-claw cue, two hind legs, full tail, and six-leg risks.",
        },
        {
            "path": GUIDE,
            "title": "no-six-leg body-lock guide",
            "note": "Structure target: exactly two grounded hind legs and short lifted hands held above the ground.",
        },
        {
            "path": CONTROL_V13,
            "title": "v13 ControlNet no-six-leg comparison",
            "note": "Good two-grounded-hind-leg silhouette and lifted hands, but too plain/guide-like and exact fingers remain soft.",
        },
        {
            "path": SIX_LEG_REJECTION,
            "title": "six-leg rejection gate",
            "note": "Keep this nearby as the failure pattern: forelimb edits can turn into extra grounded limbs.",
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
        ("current v3 full body - keep first", CURRENT, (0, 0, 1628, 1058)),
        ("current v3 lifted hand", CURRENT, (400, 455, 690, 760)),
        ("current v3 hind legs", CURRENT, (655, 600, 1145, 975)),
        ("current v3 full tail", CURRENT, (725, 390, 1615, 740)),
        ("v13 full body", CONTROL_V13, (0, 0, 1152, 768)),
        ("v13 low herbivore head", CONTROL_V13, (40, 120, 350, 300)),
        ("v13 lifted forelimbs", CONTROL_V13, (300, 330, 485, 520)),
        ("v13 two grounded hind legs", CONTROL_V13, (500, 390, 960, 735)),
        ("body-lock guide", GUIDE, (0, 0, 1152, 768)),
        ("six-leg rejection", SIX_LEG_REJECTION, (0, 0, 1536, 1024)),
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
                "taxonId": "plateosaurus-engelhardti",
                "experiment": "bodylock_control_v13",
                "controlSource": str(GUIDE.relative_to(ROOT)).replace("\\", "/"),
                "outputImage": str(CONTROL_V13.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "comparison_only",
                "reasons": [
                    "the two-grounded-hind-leg silhouette is clearer than many older failures",
                    "lifted forelimbs do not touch the ground",
                    "the render is too plain/guide-like and exact five-finger hand anatomy remains soft",
                    "current v3 remains the stronger natural representative",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Try low-denoise i2i plus body-lock control from the v3 natural source, or local hand/shadow masking, instead of pure guide ControlNet if a representative replacement is needed.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, CONTROL_V13, SIX_LEG_REJECTION):
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
