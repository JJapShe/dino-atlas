import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "theropod_allosaurus" / "review"

CURRENT = ASSET_ROOT / "allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png"
CURRENT_CROPS = ASSET_ROOT / "allosaurus-smoothbrow-threefinger-crops-v4.png"
BODYLOCK_GUIDE = ASSET_ROOT / "allosaurus-fragilis-threefinger-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSET_ROOT / "allosaurus-threefinger-bodylock-crops-v10.png"
PREVIOUS_V3 = ASSET_ROOT / "allosaurus-fragilis-lowbrow-threefinger-imagegen-v3.png"

MASK = OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_mask.png"
OUTPUTS = [
    (
        "seed 2026070862 d0.06",
        OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_allosaurus-fragilis_seed2026070862_d06.png",
    ),
    (
        "seed 2026070863 d0.06",
        OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_allosaurus-fragilis_seed2026070863_d06.png",
    ),
    (
        "seed 2026070862 d0.10",
        OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_allosaurus-fragilis_seed2026070862_d10.png",
    ),
    (
        "seed 2026070863 d0.10",
        OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_allosaurus-fragilis_seed2026070863_d10.png",
    ),
    (
        "seed 2026070862 d0.16",
        OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_allosaurus-fragilis_seed2026070862_d16.png",
    ),
    (
        "seed 2026070863 d0.16",
        OUTPUT_ROOT / "allosaurus_digit_micro_v11_allosaurus_hand_foot_tight_allosaurus-fragilis_seed2026070863_d16.png",
    ),
]

SELECTED_LABEL, SELECTED = OUTPUTS[2]
COMPARISON_OUT = ASSET_ROOT / "allosaurus-fragilis-digit-micro-i2i-comparison-v11.png"
CONTACT_OUT = ASSET_ROOT / "allosaurus-digit-micro-i2i-v11-review-sheet.png"
CROP_OUT = ASSET_ROOT / "allosaurus-digit-micro-i2i-v11-crops.png"
MASK_OUT = ASSET_ROOT / "allosaurus-digit-micro-i2i-mask-v11.png"
REVIEW_OUT = REVIEW_ROOT / "allosaurus_digit_micro_i2i_v11_review.json"


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
            "title": "current v4: keep first",
            "note": "Best current Allosaurus balance: smooth low brow, longer forelimbs, full tail, and open dry feet.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v4 crop gate",
            "note": "Close review for brow, three-finger hand gate, hind feet, and full tail.",
        },
        {
            "path": COMPARISON_OUT,
            "title": "v11 digit micro i2i comparison",
            "note": "Low-denoise hand/foot edit kept as comparison evidence while v4 remains first.",
        },
        {
            "path": BODYLOCK_GUIDE,
            "title": "three-finger body-lock guide",
            "note": "Structure reference for longer Allosaurus arms, exactly three fingers, open feet, and long tail.",
        },
        {
            "path": BODYLOCK_CROPS,
            "title": "body-lock crop gate",
            "note": "Guide-versus-current gate for future structure-aware i2i or LoRA routes.",
        },
        {
            "path": PREVIOUS_V3,
            "title": "previous v3 comparison",
            "note": "Useful hand readability comparison, but brow silhouette is less balanced than v4.",
        },
    ]
    for label, path in OUTPUTS:
        items.append(
            {
                "path": path,
                "title": f"v11 candidate {label}",
                "note": "Check whether hand and foot digits improve without changing the body, head, or tail.",
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
        ("current v4 full body", CURRENT, (0, 0, 1774, 887)),
        ("current v4 three-finger hand gate", CURRENT, (395, 420, 575, 615)),
        ("current v4 forelimb context", CURRENT, (340, 335, 620, 610)),
        ("current v4 hind feet / toes", CURRENT, (530, 615, 1035, 825)),
        ("current v4 smooth low brow", CURRENT, (45, 135, 480, 335)),
        ("v11 mask", MASK_OUT, (260, 470, 820, 760)),
    ]
    for label, path in OUTPUTS:
        crops.extend(
            [
                (f"v11 {label} full body", path, (0, 0, 1774, 887)),
                (f"v11 {label} hand gate", path, (395, 420, 575, 615)),
                (f"v11 {label} forelimb context", path, (340, 335, 620, 610)),
                (f"v11 {label} hind feet", path, (530, 615, 1035, 825)),
            ]
        )
    crops.extend(
        [
            ("body-lock crop gate", BODYLOCK_CROPS, (0, 0, 760, 858)),
            ("previous v3 hand comparison", PREVIOUS_V3, (390, 500, 610, 705)),
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
                "taxonId": "allosaurus-fragilis",
                "experiment": "digit_micro_i2i_v11",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(CONTACT_OUT),
                "cropSheet": relative(CROP_OUT),
                "decision": "comparison_only",
                "selectedSeed": 2026070862,
                "selectedDenoise": 0.10,
                "selectedLabel": SELECTED_LABEL,
                "editMode": "allosaurus_digit_cues",
                "maskPreset": "allosaurus_hand_foot_tight",
                "reasons": [
                    "low-denoise hand and foot i2i preserves the v4 smooth brow, body, tail, and medium forelimb scale",
                    "the edit can be compared for three-finger and three-toed cues, but exact digits remain close-review material",
                    "current v4 remains first unless a future pass clearly improves hand and foot readability together without changing the brow or body",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Use structure-aware hand/foot masks or an allosaurid LoRA if exact three-finger hand separation and toe anatomy need stronger improvement; avoid whole-body rerenders that drift toward T. rex skull or two-finger arms.",
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
        PREVIOUS_V3,
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
