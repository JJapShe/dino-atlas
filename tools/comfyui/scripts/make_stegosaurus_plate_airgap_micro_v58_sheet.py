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
AIRGAP_MASK = ASSET_ROOT / "stegosaurus-plate-airgap-i2i-mask-v49.png"
V51_CROPS = ASSET_ROOT / "stegosaurus-plate-airgap-i2i-v51-crops.png"

OUTPUTS = [
    (
        "seed 2026070858 d0.06",
        OUTPUT_ROOT / "stego_plate_airgap_micro_v58_custom_stegosaurus-stenops_seed2026070858_d06.png",
    ),
    (
        "seed 2026070859 d0.06",
        OUTPUT_ROOT / "stego_plate_airgap_micro_v58_custom_stegosaurus-stenops_seed2026070859_d06.png",
    ),
    (
        "seed 2026070858 d0.12",
        OUTPUT_ROOT / "stego_plate_airgap_micro_v58_custom_stegosaurus-stenops_seed2026070858_d12.png",
    ),
    (
        "seed 2026070859 d0.12",
        OUTPUT_ROOT / "stego_plate_airgap_micro_v58_custom_stegosaurus-stenops_seed2026070859_d12.png",
    ),
]

SELECTED = OUTPUTS[3][1]
COMPARISON_OUT = ASSET_ROOT / "stegosaurus-stenops-plate-airgap-micro-comparison-v58.png"
CONTACT_OUT = ASSET_ROOT / "stegosaurus-plate-airgap-micro-v58-review-sheet.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-plate-airgap-micro-v58-crops.png"
REVIEW_OUT = REVIEW_ROOT / "stego_plate_airgap_micro_v58_review.json"


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
            "title": "current v6: keep first",
            "note": "Best current Stegosaurus balance: alternating plate cue, low body, open feet, and four tail spikes.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v6 crop gate",
            "note": "Close review for plate row, surface, small head, four feet, and thagomizer count.",
        },
        {
            "path": COMPARISON_OUT,
            "title": "v58 micro air-gap comparison",
            "note": "Selected d0.12 micro seam edit. It preserves v6 but does not visibly solve the plate topology gate.",
        },
        {
            "path": AIRGAP_MASK,
            "title": "v49/v58 narrow seam mask",
            "note": "Only the narrow air gaps between existing plates were edited; body, feet, and tail were locked.",
        },
        {
            "path": V51_CROPS,
            "title": "previous stronger air-gap crops",
            "note": "Use v51 as the prior seam-edit comparison; v58 is even more conservative and mostly copies v6.",
        },
    ]
    for label, path in OUTPUTS:
        items.append(
            {
                "path": path,
                "title": f"v58 candidate {label}",
                "note": "Low-denoise seam edit candidate. Check whether the plate gaps or edges improve over v6.",
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
        ("current v6 full body", CURRENT, (0, 0, 1672, 940)),
        ("current v6 plate row", CURRENT, (170, 80, 1425, 500)),
        ("current v6 plate surface", CURRENT, (460, 110, 1040, 430)),
        ("current v6 four-spike tail", CURRENT, (1230, 420, 1665, 760)),
    ]
    for label, path in OUTPUTS:
        crops.extend(
            [
                (f"v58 {label} full body", path, (0, 0, 1672, 940)),
                (f"v58 {label} plate row", path, (170, 80, 1425, 500)),
                (f"v58 {label} plate surface", path, (460, 110, 1040, 430)),
                (f"v58 {label} tail preserved", path, (1230, 420, 1665, 760)),
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
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_airgap_micro_i2i_v58",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(AIRGAP_MASK),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(CONTACT_OUT),
                "cropSheet": relative(CROP_OUT),
                "decision": "diagnostic_only",
                "selectedSeed": 2026070859,
                "selectedDenoise": 0.12,
                "editMode": "stego_plate_air_gaps",
                "reasons": [
                    "very low denoise preserves the current v6 body, feet, four tail spikes, and plate row",
                    "plate gaps and plate edges remain too similar to v6 to justify a primary replacement",
                    "the result confirms that narrow seam edits are useful as preservation controls but not enough to solve exact staggered two-row plate topology",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Use Stegosauridae-specific LoRA training or a stronger local plate-structure synthesis pass before naturalization; do not keep repeating micro seam edits unless a new mask explicitly changes near/far plate bases.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in [CURRENT, CURRENT_CROPS, AIRGAP_MASK, V51_CROPS, *[path for _, path in OUTPUTS]]:
        if not path.exists():
            raise FileNotFoundError(path)

    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SELECTED, COMPARISON_OUT)
    make_contact_sheet()
    make_crop_sheet()
    write_review_json()
    print(COMPARISON_OUT)
    print(CONTACT_OUT)
    print(CROP_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
