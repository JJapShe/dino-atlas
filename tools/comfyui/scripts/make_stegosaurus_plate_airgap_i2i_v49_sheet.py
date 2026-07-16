import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
GUIDE = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-v1.png"
GUIDE_CROPS = ASSET_ROOT / "stegosaurus-plate-topology-crops-v12.png"
TEXTURE_V48 = ASSET_ROOT / "stegosaurus-stenops-texture-i2i-comparison-v48.png"
AIRGAP_V49 = ASSET_ROOT / "stegosaurus-stenops-plate-airgap-i2i-comparison-v49.png"
AIRGAP_MASK = ASSET_ROOT / "stegosaurus-plate-airgap-i2i-mask-v49.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-plate-airgap-i2i-v49-review-sheet.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-plate-airgap-i2i-v49-crops.png"
REVIEW_OUT = REVIEW_ROOT / "stego_plate_airgap_i2i_v49_review.json"


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
            "title": "current v6: keep first",
            "note": "Best current balance: alternating plate cue, low body, open feet, and four countable tail spikes.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v6 crop gate",
            "note": "Close review for plate row, plate surface, small head, feet, and four-spike thagomizer.",
        },
        {
            "path": AIRGAP_V49,
            "title": "v49 plate air-gap i2i comparison",
            "note": "Narrow seam-mask i2i slightly clarifies gaps while preserving the tail, but is not a clear primary upgrade.",
        },
        {
            "path": AIRGAP_MASK,
            "title": "v49 custom seam mask",
            "note": "White marks the narrow gaps edited between plates; body, legs, and tail were intentionally unmasked.",
        },
        {
            "path": TEXTURE_V48,
            "title": "v48 texture i2i comparison",
            "note": "Prior texture comparison kept for checking why texture alone did not beat v6 plate/tail gates.",
        },
        {
            "path": GUIDE,
            "title": "plate topology guide",
            "note": "Reference-control target for staggered near/far plate rows, visible gaps, and four tail spikes.",
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
        ("current v6 full body - keep first", CURRENT, (0, 0, 1672, 940)),
        ("current v6 plate row", CURRENT, (170, 80, 1425, 500)),
        ("current v6 plate surface", CURRENT, (460, 110, 1040, 430)),
        ("current v6 four-spike thagomizer", CURRENT, (1230, 420, 1665, 760)),
        ("current v6 feet", CURRENT, (300, 620, 1065, 910)),
        ("v49 full body", AIRGAP_V49, (0, 0, 1672, 940)),
        ("v49 plate row air gaps", AIRGAP_V49, (170, 80, 1425, 500)),
        ("v49 plate surface", AIRGAP_V49, (460, 110, 1040, 430)),
        ("v49 four-spike thagomizer preserved", AIRGAP_V49, (1230, 420, 1665, 760)),
        ("v49 feet preserved", AIRGAP_V49, (300, 620, 1065, 910)),
        ("v49 custom seam mask", AIRGAP_MASK, (0, 0, 1672, 940)),
        ("topology guide", GUIDE, (0, 0, 1152, 768)),
        ("guide crop gate", GUIDE_CROPS, (0, 0, 760, 858)),
        ("v48 texture comparison", TEXTURE_V48, (0, 0, 1672, 936)),
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
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_airgap_i2i_v49",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "maskImage": str(AIRGAP_MASK.relative_to(ROOT)).replace("\\", "/"),
                "comparisonImage": str(AIRGAP_V49.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "comparison_only",
                "reasons": [
                    "narrow seam-mask i2i preserves the v6 body, feet, and four-spike thagomizer",
                    "plate gaps are slightly clearer, but the improvement is subtle",
                    "current v6 remains the stronger primary because it already has better app-scale plate and tail balance",
                    "future work should use a topology-aware mask or Stegosauridae LoRA rather than whole-body texture i2i",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "selectedSeed": 2026070352,
                "selectedDenoise": 0.10,
                "editMode": "stego_plate_air_gaps",
                "nextRoute": "Try a hand-drawn near/far plate-base topology mask or Stegosauridae LoRA; do not promote subtle seam edits unless plate-row topology and four-spike tail readability improve together.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, GUIDE_CROPS, TEXTURE_V48, AIRGAP_V49, AIRGAP_MASK):
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
