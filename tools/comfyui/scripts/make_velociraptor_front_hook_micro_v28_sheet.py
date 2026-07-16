import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
MODEST_V25 = ASSET_ROOT / "velociraptor-mongoliensis-modest-sickle-i2i-comparison-v25.png"
MODEST_V25_CROPS = ASSET_ROOT / "velociraptor-modest-sickle-i2i-v25-crops.png"
HOOK_REJECT_V26 = ASSET_ROOT / "velociraptor-mongoliensis-front-hook-rejected-v26.png"
HOOK_REJECT_V26_CROPS = ASSET_ROOT / "velociraptor-front-hook-v26-rejection-crops.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
MASK = OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_mask.png"

OUTPUTS = [
    (
        "seed 2026070860 d0.04",
        OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_velociraptor-mongoliensis_seed2026070860_d04.png",
    ),
    (
        "seed 2026070861 d0.04",
        OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_velociraptor-mongoliensis_seed2026070861_d04.png",
    ),
    (
        "seed 2026070860 d0.08",
        OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_velociraptor-mongoliensis_seed2026070860_d08.png",
    ),
    (
        "seed 2026070861 d0.08",
        OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_velociraptor-mongoliensis_seed2026070861_d08.png",
    ),
    (
        "seed 2026070860 d0.12",
        OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_velociraptor-mongoliensis_seed2026070860_d12.png",
    ),
    (
        "seed 2026070861 d0.12",
        OUTPUT_ROOT / "velociraptor_front_hook_micro_v28_velociraptor_v9_front_hook_reduce_tight_velociraptor-mongoliensis_seed2026070861_d12.png",
    ),
]

SELECTED_LABEL, SELECTED = OUTPUTS[2]
COMPARISON_OUT = ASSET_ROOT / "velociraptor-mongoliensis-front-hook-micro-i2i-comparison-v28.png"
CONTACT_OUT = ASSET_ROOT / "velociraptor-front-hook-micro-i2i-v28-review-sheet.png"
CROP_OUT = ASSET_ROOT / "velociraptor-front-hook-micro-i2i-v28-crops.png"
MASK_OUT = ASSET_ROOT / "velociraptor-front-hook-micro-i2i-mask-v28.png"
REVIEW_OUT = REVIEW_ROOT / "velociraptor_front_hook_micro_i2i_v28_review.json"


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
            "title": "current v9: keep first",
            "note": "Best current balance: toothed snout, folded feathered hands, long tail, and restrained sickle cue.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v9 crop gate",
            "note": "Reference crop sheet for non-beak head, folded hands, front/rear foot cues, and tail.",
        },
        {
            "path": COMPARISON_OUT,
            "title": "v28 micro front-hook comparison",
            "note": "Very low-denoise front-hook edit. It is preserved as comparison evidence, not a primary replacement.",
        },
        {
            "path": MODEST_V25,
            "title": "v25 modest-sickle comparison",
            "note": "Prior useful local foot-tip i2i; does not clearly beat v9 but remains the best comparison route.",
        },
        {
            "path": HOOK_REJECT_V26,
            "title": "v26 front-hook rejection",
            "note": "Tighter front-hook reduction lengthened the foot/toe read and stays diagnostic only.",
        },
        {
            "path": FOOT_GUIDE,
            "title": "foot topology guide",
            "note": "Manual reference for attached raised second-toe sickle claws, not final art.",
        },
    ]
    for label, path in OUTPUTS:
        items.append(
            {
                "path": path,
                "title": f"v28 candidate {label}",
                "note": "Check whether the front raised claw becomes smaller without changing walking toes or body.",
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
        ("current v9 full body", CURRENT, (0, 0, 1693, 929)),
        ("current v9 front foot gate", CURRENT, (520, 595, 900, 875)),
        ("current v9 rear foot gate", CURRENT, (705, 585, 1095, 875)),
        ("current v9 head retained", CURRENT, (40, 115, 390, 370)),
        ("v25 comparison foot gate", MODEST_V25, (500, 610, 1085, 895)),
        ("v26 rejection foot gate", HOOK_REJECT_V26, (500, 610, 1085, 895)),
        ("v28 mask", MASK_OUT, (430, 560, 850, 865)),
    ]
    for label, path in OUTPUTS:
        crops.extend(
            [
                (f"v28 {label} full body", path, (0, 0, 1693, 929)),
                (f"v28 {label} front hook", path, (520, 595, 900, 875)),
                (f"v28 {label} rear foot preserved", path, (705, 585, 1095, 875)),
            ]
        )
    crops.extend(
        [
            ("v25 full crop audit", MODEST_V25_CROPS, (0, 0, 800, 572)),
            ("v26 rejection crop audit", HOOK_REJECT_V26_CROPS, (0, 0, 800, 572)),
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
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "front_hook_micro_i2i_v28",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(CONTACT_OUT),
                "cropSheet": relative(CROP_OUT),
                "decision": "comparison_only",
                "selectedSeed": 2026070860,
                "selectedDenoise": 0.08,
                "selectedLabel": SELECTED_LABEL,
                "editMode": "velociraptor_reduce_front_hook",
                "maskPreset": "velociraptor_v9_front_hook_reduce_tight",
                "reasons": [
                    "micro-denoise edits preserve the v9 full body, head, hands, tail, and rear foot",
                    "front-hook size changes are subtle and do not clearly improve the attached second-toe anatomy over v9",
                    "higher local denoise previously lengthened the foot/toe read in v26, so v28 is kept as comparison evidence",
                    "current v9 remains the primary until a structure-aware foot route improves the sickle claw without toe drift",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Build a hand-drawn second-toe topology mask or use a dromaeosaur-specific LoRA; simple front-hook reduction masks are too weak at low denoise and risky at higher denoise.",
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
        MODEST_V25,
        MODEST_V25_CROPS,
        HOOK_REJECT_V26,
        HOOK_REJECT_V26_CROPS,
        FOOT_GUIDE,
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
