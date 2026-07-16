import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

PRIMARY = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
V49 = ASSETS / "stegosaurus-stenops-plate-airgap-i2i-comparison-v49.png"
V49_CROPS = ASSETS / "stegosaurus-plate-airgap-i2i-v49-crops.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

V50_SELECTED = COMFY_OUTPUT / "next_stegosaurus_v6_plate_row_v50_custom_stegosaurus-stenops_d18_00001_.png"
V51_SELECTED = COMFY_OUTPUT / "next_stegosaurus_v6_plate_airgap_v51_custom_stegosaurus-stenops_d18_00001_.png"
V50_MASK = OUTPUTS / "next_stegosaurus_v6_plate_row_v50_custom_mask.png"

V50_REJECTED_ASSET = ASSETS / "stegosaurus-stenops-plate-row-i2i-rejected-v50.png"
V50_MASK_ASSET = ASSETS / "stegosaurus-plate-row-i2i-mask-v50.png"
V51_ASSET = ASSETS / "stegosaurus-stenops-plate-airgap-i2i-comparison-v51.png"
V51_SHEET = ASSETS / "stegosaurus-plate-airgap-i2i-v51-review-sheet.png"
V51_CROPS = ASSETS / "stegosaurus-plate-airgap-i2i-v51-crops.png"
V50_REJECTION_CROPS = ASSETS / "stegosaurus-plate-row-i2i-v50-rejection-crops.png"
REVIEW_JSON = REVIEW_DIR / "stego_plate_i2i_v50_v51_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    copy = image.copy()
    copy.thumbnail(size, Image.LANCZOS)
    tile = Image.new("RGB", size, (255, 255, 255))
    tile.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return tile


def label_tile(title, path, size):
    image = Image.open(path).convert("RGB")
    tile = Image.new("RGB", (size[0], size[1] + 36), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 11), title, fill=(24, 24, 22), font=FONT)
    return tile


def crop_tile(title, path, box, size):
    image = Image.open(path).convert("RGB").crop(box)
    tile = Image.new("RGB", (size[0], size[1] + 34), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 10), title, fill=(24, 24, 22), font=FONT)
    return tile


def make_review_sheet():
    rows = [
        [
            label_tile("v6 primary: keep first", PRIMARY, (500, 280)),
            label_tile("v49 air-gap comparison", V49, (500, 280)),
            label_tile("v51 stronger air-gap comparison", V51_ASSET, (500, 280)),
        ],
        [
            label_tile("v51 crop audit", V51_CROPS, (360, 500)),
            label_tile("v49 crop comparison", V49_CROPS, (360, 500)),
            label_tile("v50 full row rejection", V50_REJECTION_CROPS, (360, 500)),
            label_tile("v50 row mask", V50_MASK_ASSET, (360, 500)),
            label_tile("plate topology guide", GUIDE, (360, 500)),
        ],
    ]
    gap = 16
    margin = 18
    title_h = 50
    row_heights = [max(tile.height for tile in row) for row in rows]
    width = max(sum(tile.width for tile in row) + gap * (len(row) - 1) for row in rows) + margin * 2
    height = title_h + sum(row_heights) + gap * (len(rows) - 1) + margin * 2
    sheet = Image.new("RGB", (width, height), (232, 229, 220))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (margin, margin),
        "Stegosaurus v51 review: keep v6 primary; v51/v49 are subtle gap comparisons; v50 full-row edit is rejected",
        fill=(24, 24, 22),
        font=FONT,
    )
    y = margin + title_h
    for row, row_h in zip(rows, row_heights):
        x = margin
        for tile in row:
            sheet.paste(tile, (x, y))
            x += tile.width + gap
        y += row_h + gap
    sheet.save(V51_SHEET)


def make_crop_sheet(output, items, title):
    crop_defs = [
        ("full body", (0, 90, 1672, 840), (360, 160)),
        ("plate row", (170, 115, 1120, 430), (380, 150)),
        ("plate bases", (260, 250, 1160, 550), (360, 145)),
        ("small head", (0, 340, 390, 620), (240, 150)),
        ("feet", (360, 565, 1170, 820), (320, 130)),
        ("thagomizer", (1040, 410, 1660, 690), (300, 140)),
    ]
    gap = 12
    label_w = 150
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 46 + row_h * len(items)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 14), title, fill=(24, 24, 22), font=FONT)
    y = 46
    for label, path in items:
        draw.rectangle([(0, y), (width, y + row_h - 1)], fill=(248, 247, 242))
        draw.text((gap, y + gap), label, fill=(24, 24, 22), font=FONT)
        x = label_w
        for crop_title, box, size in crop_defs:
            tile = crop_tile(crop_title, path, box, size)
            sheet.paste(tile, (x, y + gap))
            x += tile.width + gap
        y += row_h
    sheet.save(output)


def write_review_json():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "taxonId": "stegosaurus-stenops",
        "source": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"),
        "v50": {
            "route": "full dorsal plate-row local inpaint from v6",
            "selectedDiagnostic": str(V50_REJECTED_ASSET.relative_to(ROOT)).replace("\\", "/"),
            "mask": str(V50_MASK_ASSET.relative_to(ROOT)).replace("\\", "/"),
            "seed": 2026070354,
            "denoise": 0.18,
            "decision": "diagnostic only; reject as a primary because plate/body texture softens and does not beat v6",
        },
        "v51": {
            "route": "stronger narrow air-gap inpaint from v6 using the v49 seam mask",
            "selectedComparison": str(V51_ASSET.relative_to(ROOT)).replace("\\", "/"),
            "seed": 2026070356,
            "denoise": 0.18,
            "decision": "keep as anatomy-review comparison; do not replace v6 primary",
        },
        "passChecks": [
            "v51 preserves the v6 low body, small head, feet, and four-spike thagomizer",
            "v51 keeps the plate row mostly stable and slightly strengthens some gap/edge reads",
            "v50 demonstrates that broad plate-row inpaint softens the body and is too blunt for promotion",
        ],
        "remainingRisks": [
            "v51 does not clearly solve exact near/far two-row topology",
            "v51 does not improve enough over v49 to replace v6",
            "next route should use structure conditioning or a Stegosauridae LoRA rather than plain local inpaint",
        ],
    }
    REVIEW_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for path in (V50_SELECTED, V51_SELECTED, V50_MASK):
        if not path.exists():
            raise FileNotFoundError(path)
    shutil.copy2(V50_SELECTED, V50_REJECTED_ASSET)
    shutil.copy2(V51_SELECTED, V51_ASSET)
    shutil.copy2(V50_MASK, V50_MASK_ASSET)
    make_crop_sheet(
        V51_CROPS,
        [
            ("v6 primary", PRIMARY),
            ("v49 air-gap d10", V49),
            ("v51 air-gap d18", V51_ASSET),
            ("v50 row edit rejected", V50_REJECTED_ASSET),
        ],
        "Stegosaurus v51 crop audit: v6 remains primary; v51 is comparison, v50 is rejected",
    )
    make_crop_sheet(
        V50_REJECTION_CROPS,
        [
            ("v6 primary", PRIMARY),
            ("v50 row edit rejected", V50_REJECTED_ASSET),
            ("v51 air-gap comparison", V51_ASSET),
        ],
        "Stegosaurus v50 rejection crops: full row inpaint softens body/plates without beating v6",
    )
    make_review_sheet()
    write_review_json()
    print(V51_SHEET)
    print(V51_CROPS)
    print(V50_REJECTION_CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
