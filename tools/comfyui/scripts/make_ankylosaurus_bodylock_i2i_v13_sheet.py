import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSET_ROOT / "ankylosaurus-magniventris-broadskull-singleclub-imagegen-v5.png"
CURRENT_CROPS = ASSET_ROOT / "ankylosaurus-broadskull-singleclub-crops-v5.png"
GUIDE = ASSET_ROOT / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"
GUIDE_CROPS = ASSET_ROOT / "ankylosaurus-armor-tailclub-crops-v6.png"
SCHEDULE_V12 = ASSET_ROOT / "ankylosaurus-review-options-v12.png"
BODYLOCK_V13 = ASSET_ROOT / "ankylosaurus-magniventris-bodylock-i2i-comparison-v13.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v13.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-bodylock-i2i-crops-v13.png"
REVIEW_OUT = REVIEW_ROOT / "anky_bodylock_i2i_v13_review.json"


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
            "title": "current v5: keep first",
            "note": "Best current app read: broad blunt skull, squat armored body, four feet, one attached oval tail club.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v5 crop gate",
            "note": "Close review for skull, armor rows, front and rear feet, and single-club attachment.",
        },
        {
            "path": GUIDE,
            "title": "armor/tail-club structure guide",
            "note": "Project-owned control target for broad skull, low armor rows, four feet, and fused club.",
        },
        {
            "path": GUIDE_CROPS,
            "title": "guide crop gate",
            "note": "Use as a reference-control checklist before promoting any refined output.",
        },
        {
            "path": BODYLOCK_V13,
            "title": "v13 body-lock i2i comparison",
            "note": "Preserves count gates and club, but softer skull/texture means it stays below the current v5.",
        },
        {
            "path": SCHEDULE_V12,
            "title": "v12 schedule+i2i comparison",
            "note": "Prior low-denoise comparisons retained for checking club and armor-row drift.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 242
    label_h = 72
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 30), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("current v5 full body - keep first", CURRENT, (0, 0, 1774, 887)),
        ("current v5 broad blunt skull", CURRENT, (90, 245, 565, 520)),
        ("current v5 rounded armor rows", CURRENT, (470, 145, 1225, 470)),
        ("current v5 front feet", CURRENT, (265, 545, 785, 875)),
        ("current v5 rear feet", CURRENT, (880, 525, 1450, 875)),
        ("current v5 attached club", CURRENT, (1235, 300, 1774, 625)),
        ("v13 full body", BODYLOCK_V13, (0, 0, 1768, 880)),
        ("v13 skull softness check", BODYLOCK_V13, (75, 260, 565, 545)),
        ("v13 armor rows", BODYLOCK_V13, (465, 150, 1220, 475)),
        ("v13 front feet", BODYLOCK_V13, (275, 540, 790, 870)),
        ("v13 rear feet", BODYLOCK_V13, (885, 525, 1450, 870)),
        ("v13 attached single club", BODYLOCK_V13, (1235, 300, 1768, 630)),
        ("structure guide", GUIDE, (0, 0, 1152, 768)),
        ("v12 comparison sheet", SCHEDULE_V12, (0, 0, 1290, 628)),
    ]

    cols = 2
    thumb_w = 400
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
        draw.text((8, thumb_h + 10), label[:62], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def write_review_json():
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "bodylock_i2i_v13",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "outputImage": str(BODYLOCK_V13.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "comparison_only",
                "reasons": [
                    "preserves the low quadruped body, four visible feet, and a single attached tail club",
                    "remains a useful body-lock i2i comparison after v12 schedule prompts",
                    "skull and surface detail are softer than the current v5 representative",
                    "current v5 remains the stronger app-scale Ankylosaurus image",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "promptId": "armor_tailclub_bodylock_01",
                "seed": 2026070544,
                "denoise": 0.16,
                "nextRoute": "Keep v5 first; use v13 as a low-denoise body-lock comparison while searching for a species-specific Ankylosauridae LoRA or stronger reference-conditioned route that tightens skull, toe, and armor-row anatomy without losing the club.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, GUIDE_CROPS, SCHEDULE_V12, BODYLOCK_V13):
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
