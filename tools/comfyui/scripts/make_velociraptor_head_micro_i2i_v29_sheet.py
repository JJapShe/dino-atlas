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
V27_COMPARISON = ASSET_ROOT / "velociraptor-mongoliensis-less-bird-head-i2i-comparison-v27.png"
V27_CROPS = ASSET_ROOT / "velociraptor-less-bird-head-i2i-v27-crops.png"
V28_CROPS = ASSET_ROOT / "velociraptor-front-hook-micro-i2i-v28-crops.png"

SELECTED_SOURCE = COMFY_OUTPUT / "velociraptor_head_micro_v29_velociraptor_head_snout_velociraptor-mongoliensis_d09_00001_.png"
MASK_SOURCE = OUTPUT_ROOT / "velociraptor_head_micro_v29_velociraptor_head_snout_mask.png"
CONTACT_SOURCE = OUTPUT_ROOT / "velociraptor_head_micro_v29-contact-sheet.png"

SELECTED_OUT = ASSET_ROOT / "velociraptor-mongoliensis-head-micro-i2i-comparison-v29.png"
MASK_OUT = ASSET_ROOT / "velociraptor-head-micro-i2i-mask-v29.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "velociraptor-head-micro-i2i-v29-review-sheet.png"
CROPS_OUT = ASSET_ROOT / "velociraptor-head-micro-i2i-v29-crops.png"
REVIEW_OUT = REVIEW_ROOT / "velociraptor_head_micro_i2i_v29_review.json"


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
        (
            CURRENT,
            "current v9: still first",
            "Best current body, tail, folded hands, and attached modest sickle-claw balance.",
        ),
        (
            SELECTED_OUT,
            "v29 head micro i2i",
            "Selected low-denoise head-only edit. It reduces the bird-eye feel while preserving body and feet.",
        ),
        (
            CONTACT_SOURCE,
            "all v29 attempts",
            "Six low-denoise head-mask probes. Higher strength changes the head more but risks texture drift.",
        ),
        (
            MASK_OUT,
            "v29 head/snout mask",
            "Localized mask over the skull and snout only; feet, hands, torso, and tail stay locked.",
        ),
        (
            V27_CROPS,
            "v27 comparison gate",
            "Previous head-only probe reduced bird-eye read but softened the dromaeosaur head texture.",
        ),
        (
            V28_CROPS,
            "v28 foot gate",
            "Latest foot-hook micro probe remains diagnostic; v29 should be judged without reopening foot edits.",
        ),
    ]
    cols = 3
    thumb_w, thumb_h, label_h = 430, 242, 74
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (path, title, note) in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(path), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), title[:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 31), note, font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(REVIEW_SHEET_OUT)


def make_crop_sheet():
    crops = [
        ("v9 full body", CURRENT, (0, 80, 1693, 850), (360, 164)),
        ("v29 full body", SELECTED_OUT, (0, 80, 1693, 850), (360, 164)),
        ("v9 head/snout", CURRENT, (0, 115, 510, 430), (290, 178)),
        ("v29 head/snout", SELECTED_OUT, (0, 115, 510, 430), (290, 178)),
        ("v27 head/snout", V27_COMPARISON, (0, 115, 510, 430), (290, 178)),
        ("v9 eye/mouth", CURRENT, (20, 175, 420, 360), (290, 134)),
        ("v29 eye/mouth", SELECTED_OUT, (20, 175, 420, 360), (290, 134)),
        ("v27 eye/mouth", V27_COMPARISON, (20, 175, 420, 360), (290, 134)),
        ("v9 folded hands", CURRENT, (245, 310, 720, 610), (280, 160)),
        ("v29 folded hands", SELECTED_OUT, (245, 310, 720, 610), (280, 160)),
        ("v9 front foot", CURRENT, (470, 610, 850, 920), (260, 176)),
        ("v29 front foot", SELECTED_OUT, (470, 610, 850, 920), (260, 176)),
        ("v9 rear foot", CURRENT, (720, 590, 1080, 920), (260, 176)),
        ("v29 rear foot", SELECTED_OUT, (720, 590, 1080, 920), (260, 176)),
        ("v9 tail/body", CURRENT, (700, 160, 1690, 530), (360, 135)),
        ("v29 tail/body", SELECTED_OUT, (700, 160, 1690, 530), (360, 135)),
    ]
    cols = 4
    thumb_w, thumb_h, label_h = 310, 190, 38
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
                "experiment": "head_micro_i2i_v29",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "comparisonImage": str(SELECTED_OUT.relative_to(ROOT)).replace("\\", "/"),
                "maskImage": str(MASK_OUT.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(REVIEW_SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROPS_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "anatomy_review",
                "selectedSeed": 2026070901,
                "selectedDenoise": 0.09,
                "mask": "velociraptor_head_snout",
                "reasons": [
                    "v29 preserves the v9 body, folded forelimbs, long tail, two legs, and foot gates because the edit is localized to the head and snout",
                    "the selected output slightly reduces the modern-bird eye impression while keeping a toothed non-beak snout",
                    "the improvement is subtle and exact dromaeosaur skull/eye proportions still need reference review, so v9 remains primary for now",
                    "future promotion should require a crop gate that improves head identity without weakening the attached second-toe sickle-claw evidence",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Try a dromaeosaur-specific LoRA or stronger head reference conditioning, but keep the foot and tail locked unless the head crop clearly beats v9 and v27.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, V27_COMPARISON, V27_CROPS, V28_CROPS, SELECTED_SOURCE, MASK_SOURCE, CONTACT_SOURCE):
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
