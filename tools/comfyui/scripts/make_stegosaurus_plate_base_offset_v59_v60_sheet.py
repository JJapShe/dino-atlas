import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V58_CROPS = ASSET_ROOT / "stegosaurus-plate-airgap-micro-v58-crops.png"
MASK_SOURCE = OUTPUT_ROOT / "stegosaurus_plate_base_offset_mask_v59.png"
MASK_SHEET_SOURCE = OUTPUT_ROOT / "stegosaurus_plate_base_offset_mask_v59-sheet.png"
CONTACT_V59 = OUTPUT_ROOT / "stegosaurus_plate_base_offset_v59-contact-sheet.png"
CONTACT_V60 = OUTPUT_ROOT / "stegosaurus_plate_base_offset_v60-contact-sheet.png"

OUTPUTS = [
    (
        "v59 seed 2026070905 d0.10",
        OUTPUT_ROOT / "stegosaurus_plate_base_offset_v59_custom_stegosaurus-stenops_seed2026070905_d10.png",
    ),
    (
        "v59 seed 2026070906 d0.16",
        OUTPUT_ROOT / "stegosaurus_plate_base_offset_v59_custom_stegosaurus-stenops_seed2026070906_d16.png",
    ),
    (
        "v59 seed 2026070905 d0.22",
        OUTPUT_ROOT / "stegosaurus_plate_base_offset_v59_custom_stegosaurus-stenops_seed2026070905_d22.png",
    ),
    (
        "v60 seed 2026070907 d0.28",
        OUTPUT_ROOT / "stegosaurus_plate_base_offset_v60_custom_stegosaurus-stenops_seed2026070907_d28.png",
    ),
    (
        "v60 seed 2026070908 d0.34",
        OUTPUT_ROOT / "stegosaurus_plate_base_offset_v60_custom_stegosaurus-stenops_seed2026070908_d34.png",
    ),
]

SELECTED_LABEL, SELECTED = OUTPUTS[-1]
COMPARISON_OUT = ASSET_ROOT / "stegosaurus-stenops-plate-base-offset-rejected-v60.png"
MASK_OUT = ASSET_ROOT / "stegosaurus-plate-base-offset-mask-v59.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "stegosaurus-plate-base-offset-v59-v60-rejection-sheet.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-plate-base-offset-v59-v60-rejection-crops.png"
REVIEW_OUT = REVIEW_ROOT / "stego_plate_base_offset_v59_v60_review.json"


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


def copy_assets():
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SELECTED, COMPARISON_OUT)
    shutil.copy2(MASK_SOURCE, MASK_OUT)


def make_review_sheet():
    items = [
        (
            CURRENT,
            "current v6: keep first",
            "Best current natural Stegosaurus balance: low body, broad plates, feet, and four tail spikes.",
        ),
        (
            COMPARISON_OUT,
            "v60 base-offset diagnostic",
            "Strongest base/gap-mask attempt. It preserves v6 but does not clearly improve staggered topology.",
        ),
        (
            MASK_SHEET_SOURCE,
            "v59/v60 mask placement",
            "Mask targets plate bases and gaps, avoiding torso, feet, tail, and thagomizer.",
        ),
        (
            CONTACT_V59,
            "v59 low-denoise attempts",
            "Preservation check at d0.10/d0.16/d0.22; changes remain too subtle.",
        ),
        (
            CONTACT_V60,
            "v60 higher-denoise attempts",
            "Higher denoise still mostly copies v6 and does not create a reliable second row.",
        ),
        (
            V58_CROPS,
            "v58 previous seam gate",
            "Earlier narrow seam edits were also too weak; v59/v60 confirms the same route limit.",
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
    crop_rows = [
        ("current v6 full body", CURRENT, (0, 0, 1672, 940)),
        ("current v6 plate row", CURRENT, (170, 80, 1425, 500)),
        ("current v6 plate surface", CURRENT, (460, 110, 1040, 430)),
        ("current v6 four-spike tail", CURRENT, (1230, 420, 1665, 760)),
        ("selected v60 full body", COMPARISON_OUT, (0, 0, 1672, 940)),
        ("selected v60 plate row", COMPARISON_OUT, (170, 80, 1425, 500)),
        ("selected v60 plate surface", COMPARISON_OUT, (460, 110, 1040, 430)),
        ("selected v60 tail preserved", COMPARISON_OUT, (1230, 420, 1665, 760)),
    ]
    for label, path in OUTPUTS:
        crop_rows.append((f"{label} plate row", path, (170, 80, 1425, 500)))

    cols = 2
    thumb_w, thumb_h, label_h = 420, 250, 36
    rows = (len(crop_rows) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (label, path, box) in enumerate(crop_rows):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:68], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(CROP_OUT)


def write_review_json():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_base_offset_v59_v60",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(REVIEW_SHEET_OUT),
                "cropSheet": relative(CROP_OUT),
                "decision": "diagnostic_only",
                "selectedOutput": SELECTED_LABEL,
                "editMode": "stego_alternating_plate_bases",
                "reasons": [
                    "the localized base/gap mask preserves the v6 body, feet, tail, and four thagomizer spikes",
                    "low and higher denoise outputs remain visually close to v6 and do not create a reliable near/far two-row plate read",
                    "this confirms that simple base/gap masking is a preservation-safe diagnostic route, not a primary improvement route",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Move Stegosaurus improvement toward Stegosauridae-specific LoRA or explicit plate-structure synthesis followed by naturalization; avoid repeating narrow seam/base masks unless the mask supplies new plate geometry.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in [CURRENT, CURRENT_CROPS, V58_CROPS, MASK_SOURCE, MASK_SHEET_SOURCE, CONTACT_V59, CONTACT_V60, *[path for _, path in OUTPUTS]]:
        if not path.exists():
            raise FileNotFoundError(path)
    copy_assets()
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(COMPARISON_OUT)
    print(MASK_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROP_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
