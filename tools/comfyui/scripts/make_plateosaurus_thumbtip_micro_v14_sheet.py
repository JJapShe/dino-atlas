import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

CURRENT = ASSET_ROOT / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
CURRENT_CROPS = ASSET_ROOT / "plateosaurus-singleforelimb-smallhand-crops-v3.png"
BODYLOCK_GUIDE = ASSET_ROOT / "plateosaurus-engelhardti-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSET_ROOT / "plateosaurus-bodylock-crops-v4.png"
BODYLOCK_CONTROL = ASSET_ROOT / "plateosaurus-engelhardti-bodylock-control-comparison-v13.png"
SIXLEG_REJECT = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"
MASK = OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_mask.png"

OUTPUTS = [
    (
        "seed 2026070864 d0.06",
        OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026070864_d06.png",
    ),
    (
        "seed 2026070865 d0.06",
        OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026070865_d06.png",
    ),
    (
        "seed 2026070864 d0.10",
        OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026070864_d10.png",
    ),
    (
        "seed 2026070865 d0.10",
        OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026070865_d10.png",
    ),
    (
        "seed 2026070864 d0.16",
        OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026070864_d16.png",
    ),
    (
        "seed 2026070865 d0.16",
        OUTPUT_ROOT / "plateosaurus_thumbtip_micro_v14_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026070865_d16.png",
    ),
]

SELECTED_LABEL, SELECTED = OUTPUTS[2]
COMPARISON_OUT = ASSET_ROOT / "plateosaurus-engelhardti-thumbtip-micro-i2i-comparison-v14.png"
CONTACT_OUT = ASSET_ROOT / "plateosaurus-thumbtip-micro-i2i-v14-review-sheet.png"
CROP_OUT = ASSET_ROOT / "plateosaurus-thumbtip-micro-i2i-v14-crops.png"
MASK_OUT = ASSET_ROOT / "plateosaurus-thumbtip-micro-i2i-mask-v14.png"
REVIEW_OUT = REVIEW_ROOT / "plateosaurus_thumbtip_micro_i2i_v14_review.json"


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
    for idx, wrapped in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * line_h), wrapped, fill=fill, font=font)


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def make_contact_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v3: keep first",
            "note": "Best count read: herbivore head, full tail, two grounded hind legs, and lower six-leg risk.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v3 crop gate",
            "note": "Close review for single lifted forelimb, smaller hand/thumb-claw cue, hind legs, and full tail.",
        },
        {
            "path": COMPARISON_OUT,
            "title": "v14 thumb-tip micro i2i comparison",
            "note": "Low-denoise hand-tip edit kept as comparison evidence while v3 remains first.",
        },
        {
            "path": BODYLOCK_GUIDE,
            "title": "no-six-leg body-lock guide",
            "note": "Structure target for lifted forelimbs, two grounded hind legs, full tail, and thumb-claw cues.",
        },
        {
            "path": BODYLOCK_CONTROL,
            "title": "v13 body-lock ControlNet comparison",
            "note": "Cleaner no-six-leg silhouette but too plain/guide-like to replace v3.",
        },
        {
            "path": SIXLEG_REJECT,
            "title": "six-leg rejection gate",
            "note": "Keep as warning: forelimb edits can easily create extra leg reads.",
        },
    ]
    for label, path in OUTPUTS:
        items.append(
            {
                "path": path,
                "title": f"v14 candidate {label}",
                "note": "Check whether thumb-claw detail improves without making hands larger or weight-bearing.",
            }
        )

    cols = 3
    thumb_w = 430
    thumb_h = 242
    label_h = 74
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

    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("current v3 full body", CURRENT, (0, 0, 1628, 966)),
        ("current v3 single lifted forelimb", CURRENT, (395, 410, 640, 685)),
        ("current v3 small hand / thumb cue", CURRENT, (420, 505, 640, 715)),
        ("current v3 separated hind legs", CURRENT, (665, 535, 1110, 890)),
        ("current v3 head", CURRENT, (75, 165, 510, 350)),
        ("v14 mask", MASK_OUT, (360, 485, 560, 670)),
    ]
    for label, path in OUTPUTS:
        crops.extend(
            [
                (f"v14 {label} full body", path, (0, 0, 1628, 966)),
                (f"v14 {label} lifted forelimb", path, (395, 410, 640, 685)),
                (f"v14 {label} hand/thumb cue", path, (420, 505, 640, 715)),
                (f"v14 {label} hind legs", path, (665, 535, 1110, 890)),
            ]
        )
    crops.extend(
        [
            ("body-lock crop gate", BODYLOCK_CROPS, (0, 0, 760, 858)),
            ("v13 ControlNet comparison", BODYLOCK_CONTROL, (0, 0, 1152, 768)),
            ("six-leg rejection crop", SIXLEG_REJECT, (300, 280, 820, 740)),
        ]
    )

    cols = 2
    thumb_w = 420
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
        draw.text((8, thumb_h + 10), label[:68], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(CROP_OUT)


def write_review_json():
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "plateosaurus-engelhardti",
                "experiment": "thumbtip_micro_i2i_v14",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(CONTACT_OUT),
                "cropSheet": relative(CROP_OUT),
                "decision": "comparison_only",
                "selectedSeed": 2026070864,
                "selectedDenoise": 0.10,
                "selectedLabel": SELECTED_LABEL,
                "editMode": "plateosaurus_thumb_claw_tips",
                "maskPreset": "plateosaurus_thumb_claw_tips",
                "reasons": [
                    "low-denoise thumb-tip i2i preserves the v3 low herbivore head, full tail, two grounded hind legs, and lifted forelimb",
                    "the hand/thumb-claw cue can be compared against v3, but the edit is subtle and not a decisive representative upgrade",
                    "current v3 remains first because it keeps the strongest balance between hand visibility and no-six-leg risk",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Use a structure-aware hand topology mask or early-sauropodomorph LoRA if exact five-finger/thumb-claw anatomy must improve; avoid broad forelimb edits that create weight-bearing front limbs or six-leg reads.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in [
        CURRENT,
        CURRENT_CROPS,
        BODYLOCK_GUIDE,
        BODYLOCK_CROPS,
        BODYLOCK_CONTROL,
        SIXLEG_REJECT,
        MASK,
        *[path for _, path in OUTPUTS],
    ]:
        if not path.exists():
            raise FileNotFoundError(path)

    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SELECTED, COMPARISON_OUT)
    shutil.copy2(MASK, MASK_OUT)
    make_contact_sheet()
    make_crop_sheet()
    write_review_json()
    print(COMPARISON_OUT)
    print(CONTACT_OUT)
    print(CROP_OUT)
    print(MASK_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
