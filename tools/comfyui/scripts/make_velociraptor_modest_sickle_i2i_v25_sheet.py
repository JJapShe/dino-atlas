import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
MODEST_V25 = ASSET_ROOT / "velociraptor-mongoliensis-modest-sickle-i2i-comparison-v25.png"
HOOK_REJECT_V26 = ASSET_ROOT / "velociraptor-mongoliensis-front-hook-rejected-v26.png"
V25_CONTACT = OUTPUT_ROOT / "next_velociraptor_v9_modest_sickle_v25-contact-sheet.png"
V25_FOOT_CROPS = OUTPUT_ROOT / "next_velociraptor_v9_modest_sickle_v25-foot-crops.png"
V26_FOOT_CROPS = OUTPUT_ROOT / "next_velociraptor_v9_front_hook_v26-foot-crops.png"

CONTACT_OUT = ASSET_ROOT / "velociraptor-modest-sickle-i2i-v25-review-sheet.png"
CROP_OUT = ASSET_ROOT / "velociraptor-modest-sickle-i2i-v25-crops.png"
REJECTION_OUT = ASSET_ROOT / "velociraptor-front-hook-v26-rejection-crops.png"
REVIEW_OUT = REVIEW_ROOT / "velociraptor_modest_sickle_i2i_v25_review.json"


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
            "title": "current v9: keep first",
            "note": "Best balance of toothed snout, folded feathered arms, full tail, and restrained raised sickle cue.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v9 crop gate",
            "note": "Close review for non-beak head, folded hands, front and rear foot sickle cues, and tail.",
        },
        {
            "path": MODEST_V25,
            "title": "v25 modest-sickle i2i comparison",
            "note": "Local foot-tip i2i keeps the body intact and modest sickle cue, but does not clearly beat v9.",
        },
        {
            "path": V25_FOOT_CROPS,
            "title": "v25 foot crop audit",
            "note": "Compare all v25 denoise/seed attempts against v9 before treating any as improvement.",
        },
        {
            "path": HOOK_REJECT_V26,
            "title": "v26 front-hook rejection",
            "note": "Tighter hook reduction preserved the body, but made toes longer and less dromaeosaur-foot clean.",
        },
        {
            "path": FOOT_GUIDE,
            "title": "foot topology guide",
            "note": "Use as the manual reference for attached raised second-toe sickle claws, not as final art.",
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
        ("current v9 full body - keep first", CURRENT, (0, 0, 1693, 929)),
        ("current v9 toothed non-beak snout", CURRENT, (40, 115, 390, 370)),
        ("current v9 folded feathered hands", CURRENT, (385, 430, 620, 690)),
        ("current v9 foot gate", CURRENT, (500, 610, 1085, 895)),
        ("current v9 long stiff tail", CURRENT, (700, 295, 1685, 565)),
        ("v25 full body", MODEST_V25, (0, 0, 1688, 928)),
        ("v25 head preserved", MODEST_V25, (40, 115, 390, 370)),
        ("v25 folded hands preserved", MODEST_V25, (385, 430, 620, 690)),
        ("v25 modest sickle foot check", MODEST_V25, (500, 610, 1085, 895)),
        ("v25 tail preserved", MODEST_V25, (700, 295, 1685, 565)),
        ("v25 all attempts foot crop", V25_FOOT_CROPS, (0, 0, 860, 732)),
        ("v26 rejection foot crop", V26_FOOT_CROPS, (0, 0, 860, 732)),
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
    Image.open(V26_FOOT_CROPS).save(REJECTION_OUT)


def write_review_json():
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "modest_sickle_i2i_v25",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "comparisonImage": str(MODEST_V25.relative_to(ROOT)).replace("\\", "/"),
                "rejectionImage": str(HOOK_REJECT_V26.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
                "rejectionCropSheet": str(REJECTION_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "comparison_only",
                "reasons": [
                    "v25 preserves the v9 full-body silhouette, toothed non-beak snout, folded arms, and long tail",
                    "v25 keeps a modest sickle-claw cue but does not clearly improve foot anatomy over v9",
                    "v26 tighter front-hook reduction creates longer, less reliable toes and stays diagnostic only",
                    "current v9 remains the stronger representative until a localized foot route visibly improves attached second-toe topology without toe drift",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "v25": {
                    "maskPreset": "velociraptor_v9_sickle_claw_tips",
                    "editMode": "velociraptor_modest_sickle_toes",
                    "selectedSeed": 2026070280,
                    "selectedDenoise": 0.12,
                },
                "v26": {
                    "maskPreset": "velociraptor_v9_front_hook_reduce_tight",
                    "editMode": "velociraptor_reduce_front_hook",
                    "selectedRejectedSeed": 2026070282,
                    "selectedRejectedDenoise": 0.10,
                },
                "nextRoute": "Try a hand-drawn second-toe topology mask or dromaeosaur-specific LoRA; whole-body guide-source ControlNet/IP-i2i and simple hook-reduction masks have not improved v9.",
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
        FOOT_GUIDE,
        MODEST_V25,
        HOOK_REJECT_V26,
        V25_CONTACT,
        V25_FOOT_CROPS,
        V26_FOOT_CROPS,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    write_review_json()
    print(CONTACT_OUT)
    print(CROP_OUT)
    print(REJECTION_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
