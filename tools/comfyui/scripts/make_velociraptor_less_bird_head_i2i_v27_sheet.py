import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
V25_CROPS = ASSET_ROOT / "velociraptor-modest-sickle-i2i-v25-crops.png"
V26_CROPS = ASSET_ROOT / "velociraptor-front-hook-v26-rejection-crops.png"

SELECTED_SOURCE = COMFY_OUTPUT / "next_velociraptor_v9_less_bird_head_v27_custom_velociraptor-mongoliensis_d10_00002_.png"
MASK_SOURCE = OUTPUT_ROOT / "next_velociraptor_v9_less_bird_head_v27_custom_mask.png"
CONTACT_SOURCE = OUTPUT_ROOT / "next_velociraptor_v9_less_bird_head_v27-contact-sheet.png"

SELECTED_OUT = ASSET_ROOT / "velociraptor-mongoliensis-less-bird-head-i2i-comparison-v27.png"
MASK_OUT = ASSET_ROOT / "velociraptor-less-bird-head-i2i-mask-v27.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "velociraptor-less-bird-head-i2i-v27-review-sheet.png"
CROPS_OUT = ASSET_ROOT / "velociraptor-less-bird-head-i2i-v27-crops.png"
REVIEW_OUT = REVIEW_ROOT / "velociraptor_less_bird_head_i2i_v27_review.json"


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


def copy_selected_assets():
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SELECTED_SOURCE, SELECTED_OUT)
    shutil.copyfile(MASK_SOURCE, MASK_OUT)


def make_review_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v9: keep first",
            "note": "Best current balance of toothed snout, folded feathered arms, long tail, and restrained sickle cue.",
        },
        {
            "path": SELECTED_OUT,
            "title": "v27 less-bird-head comparison",
            "note": "Head-only i2i reduces the yellow bird-eye read, but softens snout and feather texture.",
        },
        {
            "path": CONTACT_SOURCE,
            "title": "all v27 low-denoise attempts",
            "note": "Four head-mask attempts. None should replace v9 without stronger dromaeosaur identity control.",
        },
        {
            "path": MASK_OUT,
            "title": "v27 head-only mask",
            "note": "Mask covers head and front neck while leaving body, folded hands, feet, and tail untouched.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v9 close-review gate",
            "note": "Use this as the representative gate for head, hands, feet, tail, and whole-body silhouette.",
        },
        {
            "path": V25_CROPS,
            "title": "v25 foot comparison gate",
            "note": "Foot-tip i2i comparison remains useful, but it does not solve attached second-toe topology.",
        },
    ]

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
        draw_wrapped(draw, (8, thumb_h + 31), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(REVIEW_SHEET_OUT)


def make_crop_sheet():
    crops = [
        ("v9 full body", CURRENT, (0, 80, 1693, 850), (360, 164)),
        ("v27 full body", SELECTED_OUT, (0, 80, 1693, 850), (360, 164)),
        ("v9 head/snout", CURRENT, (0, 120, 500, 420), (280, 168)),
        ("v27 head/snout", SELECTED_OUT, (0, 120, 500, 420), (280, 168)),
        ("v9 eye/mouth", CURRENT, (25, 185, 405, 350), (280, 122)),
        ("v27 eye/mouth", SELECTED_OUT, (25, 185, 405, 350), (280, 122)),
        ("v9 folded hands", CURRENT, (240, 310, 720, 610), (280, 160)),
        ("v27 folded hands", SELECTED_OUT, (240, 310, 720, 610), (280, 160)),
        ("v9 front foot", CURRENT, (470, 610, 850, 920), (260, 176)),
        ("v27 front foot", SELECTED_OUT, (470, 610, 850, 920), (260, 176)),
        ("v9 rear foot", CURRENT, (720, 590, 1080, 920), (260, 176)),
        ("v27 rear foot", SELECTED_OUT, (720, 590, 1080, 920), (260, 176)),
        ("v9 tail/body", CURRENT, (700, 160, 1690, 530), (360, 135)),
        ("v27 tail/body", SELECTED_OUT, (700, 160, 1690, 530), (360, 135)),
        ("v25 foot gate", V25_CROPS, (0, 0, 860, 732), (360, 220)),
        ("v26 foot rejection", V26_CROPS, (0, 0, 860, 732), (360, 220)),
    ]

    cols = 4
    thumb_w = 310
    thumb_h = 190
    label_h = 38
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (label, path, box, size) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, size), ((thumb_w - size[0]) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:50], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(CROPS_OUT)


def write_review_json():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "less_bird_head_i2i_v27",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "comparisonImage": str(SELECTED_OUT.relative_to(ROOT)).replace("\\", "/"),
                "maskImage": str(MASK_OUT.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(REVIEW_SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROPS_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "comparison_only",
                "selectedSeed": 2026070283,
                "selectedDenoise": 0.10,
                "mask": "custom head and front-neck polygon over v9",
                "reasons": [
                    "v27 reduces the bright yellow modern-bird eye read compared with the current v9 image",
                    "v27 preserves the full body, folded hands, feet, and long tail because the mask is localized",
                    "v27 softens feather texture around the head and makes the snout read more generic reptile, so it should not replace v9",
                    "current v9 remains the stronger representative until a dromaeosaur-specific route improves the head without losing plumage or exact foot reviewability",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Use stronger dromaeosaur-specific conditioning or a custom reference-trained LoRA; keep localized masks, but require close head, feather, hand, foot, and tail crop gates before any promotion.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (
        CURRENT,
        CURRENT_CROPS,
        V25_CROPS,
        V26_CROPS,
        SELECTED_SOURCE,
        MASK_SOURCE,
        CONTACT_SOURCE,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    copy_selected_assets()
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(SELECTED_OUT)
    print(MASK_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROPS_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
