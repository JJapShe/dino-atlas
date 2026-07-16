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
PRIMARY_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V55_REJECTION_CROPS = ASSETS / "stegosaurus-v6-clean-guide-ipcontrol-v54-v55-rejection-crops.png"
MASK = OUTPUTS / "next_stegosaurus_v6_plate_lora_i2i_v56_stego_dorsal_plates_mask.png"
V56_CONTACT = OUTPUTS / "next_stegosaurus_v6_plate_lora_i2i_v56-contact-sheet.png"
V57_CONTACT = OUTPUTS / "next_stegosaurus_v6_plate_lora_i2i_v57-contact-sheet.png"

V56_SOURCE = COMFY_OUTPUT / "next_stegosaurus_v6_plate_lora_i2i_v56_stego_dorsal_plates_stegosaurus-stenops_s07_d18_00001_.png"
V57_SOURCE = COMFY_OUTPUT / "next_stegosaurus_v6_plate_lora_i2i_v57_stego_dorsal_plates_stegosaurus-stenops_s07_d30_00001_.png"

V56_ASSET = ASSETS / "stegosaurus-stenops-plate-lora-i2i-rejected-v56.png"
V57_ASSET = ASSETS / "stegosaurus-stenops-plate-lora-i2i-rejected-v57.png"
SHEET = ASSETS / "stegosaurus-plate-lora-i2i-v56-v57-rejection-sheet.png"
CROPS = ASSETS / "stegosaurus-plate-lora-i2i-v56-v57-rejection-crops.png"
REVIEW_JSON = REVIEW_DIR / "stego_plate_lora_i2i_v56_v57_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (255, 255, 255))
    tile.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return tile


def label_tile(title, path, size):
    image = Image.open(path).convert("RGB")
    tile = Image.new("RGB", (size[0], size[1] + 46), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 10), title[:76], fill=(24, 24, 22), font=FONT)
    return tile


def crop_tile(title, path, box, size):
    image = Image.open(path).convert("RGB").crop(box)
    tile = Image.new("RGB", (size[0], size[1] + 34), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 10), title, fill=(24, 24, 22), font=FONT)
    return tile


def make_sheet():
    rows = [
        [
            label_tile("v6 primary: keep first", PRIMARY, (410, 230)),
            label_tile("v56 low denoise LoRA plate i2i: near-copy", V56_ASSET, (410, 230)),
            label_tile("v57 higher denoise LoRA plate i2i: softens without topology gain", V57_ASSET, (410, 230)),
        ],
        [
            label_tile("v56 all attempts", V56_CONTACT, (410, 300)),
            label_tile("v57 all attempts", V57_CONTACT, (410, 300)),
            label_tile("masked plate band used for both runs", MASK, (410, 300)),
        ],
        [
            label_tile("v6 close-review gate", PRIMARY_CROPS, (410, 420)),
            label_tile("previous v54/v55 IP-Control rejection crops", V55_REJECTION_CROPS, (410, 420)),
        ],
    ]
    gap = 16
    margin = 18
    title_h = 58
    row_heights = [max(tile.height for tile in row) for row in rows]
    width = max(sum(tile.width for tile in row) + gap * (len(row) - 1) for row in rows) + margin * 2
    height = title_h + sum(row_heights) + gap * (len(rows) - 1) + margin * 2
    sheet = Image.new("RGB", (width, height), (232, 229, 220))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (margin, margin),
        "Stegosaurus v56/v57 Dinosaur_Generator_v2 LoRA plate-band i2i: reject; v6 remains first",
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
    sheet.save(SHEET)


def make_crops():
    items = [
        ("v6 primary", PRIMARY),
        ("v56 low denoise", V56_ASSET),
        ("v57 high denoise", V57_ASSET),
    ]
    crop_defs = [
        ("full body", (0, 145, 1672, 840), (330, 138)),
        ("full plate row", (170, 185, 1290, 520), (330, 138)),
        ("front plates/head", (0, 250, 620, 605), (260, 150)),
        ("mid plates", (520, 185, 1025, 490), (260, 150)),
        ("tail plates", (980, 280, 1380, 560), (240, 150)),
        ("tail/thagomizer", (1130, 400, 1672, 820), (260, 150)),
    ]
    gap = 12
    label_w = 145
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 44 + row_h * len(items)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (gap, 12),
        "Stegosaurus v56/v57 plate-band LoRA i2i crops: reject if plate topology stays one-row, fused, or softened",
        fill=(24, 24, 22),
        font=FONT,
    )
    y = 44
    for label, path in items:
        draw.rectangle([(0, y), (width, y + row_h - 1)], fill=(248, 247, 242))
        draw.text((gap, y + gap), label, fill=(24, 24, 22), font=FONT)
        x = label_w
        for title, box, size in crop_defs:
            tile = crop_tile(title, path, box, size)
            sheet.paste(tile, (x, y + gap))
            x += tile.width + gap
        y += row_h
    sheet.save(CROPS)


def write_review():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "taxonId": "stegosaurus-stenops",
        "route": "v6 source, dorsal-plate-band inpaint, Dinosaur_Generator_v2.0 weak LoRA",
        "source": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"),
        "selectedOutputs": [
            str(V56_ASSET.relative_to(ROOT)).replace("\\", "/"),
            str(V57_ASSET.relative_to(ROOT)).replace("\\", "/"),
        ],
        "lora": "Dinosaur_Generator_v2.0-000011.safetensors",
        "loraStrength": 0.07,
        "clipStrength": 0.04,
        "seeds": [2026070356, 2026070357, 2026070358, 2026070359],
        "denoise": [0.12, 0.18, 0.24, 0.30],
        "decision": "diagnostic only; do not replace v6 primary",
        "findings": [
            "low denoise v56 mostly copies v6 and does not improve alternating two-row plate topology",
            "higher denoise v57 begins to soften plate/body texture without creating clearer separated staggered rows",
            "body, legs, and thagomizer mostly survive, but the key plate gate is not improved",
        ],
        "nextRoute": "Use a stegosaur-specific LoRA or explicit local plate paintover plus structure-aware refinement; weak generic dinosaur LoRA over the plate band is insufficient.",
    }
    REVIEW_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for path in (PRIMARY, PRIMARY_CROPS, V55_REJECTION_CROPS, MASK, V56_CONTACT, V57_CONTACT, V56_SOURCE, V57_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)
    shutil.copy2(V56_SOURCE, V56_ASSET)
    shutil.copy2(V57_SOURCE, V57_ASSET)
    make_sheet()
    make_crops()
    write_review()
    print(V56_ASSET)
    print(V57_ASSET)
    print(SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
