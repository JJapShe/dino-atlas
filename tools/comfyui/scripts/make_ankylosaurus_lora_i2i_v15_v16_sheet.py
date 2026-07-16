import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

PRIMARY = ASSETS / "ankylosaurus-magniventris-broadskull-i2i-v14.png"
PRIMARY_CROPS = ASSETS / "ankylosaurus-broadskull-i2i-v14-crops.png"
PREVIOUS_CROPS = ASSETS / "ankylosaurus-broadskull-singleclub-crops-v5.png"
V15_CONTACT = OUTPUTS / "next_ankylosaurus_v14_osteoderm_lora_i2i_v15-contact-sheet.png"
V16_CONTACT = OUTPUTS / "next_ankylosaurus_v14_sturdy_toes_lora_i2i_v16-contact-sheet.png"
V16_MASK = ASSETS / "ankylosaurus-sturdy-toes-i2i-mask-v16.png"

V15_SOURCE = COMFY_OUTPUT / "next_ankylosaurus_v14_osteoderm_lora_i2i_v15_ankylosaurus_osteoderm_band_ankylosaurus-magniventris_s08_d16_00001_.png"
V16_SOURCE = COMFY_OUTPUT / "next_ankylosaurus_v14_sturdy_toes_lora_i2i_v16_custom_ankylosaurus-magniventris_s08_d14_00002_.png"

V15_ASSET = ASSETS / "ankylosaurus-magniventris-osteoderm-lora-i2i-comparison-v15.png"
V16_ASSET = ASSETS / "ankylosaurus-magniventris-sturdy-toes-lora-i2i-comparison-v16.png"
SHEET = ASSETS / "ankylosaurus-lora-i2i-v15-v16-review-sheet.png"
CROPS = ASSETS / "ankylosaurus-lora-i2i-v15-v16-crops.png"
REVIEW_JSON = REVIEW_DIR / "anky_lora_i2i_v15_v16_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (255, 255, 255))
    tile.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return tile


def label_tile(title, path, size):
    image = Image.open(path).convert("RGB")
    tile = Image.new("RGB", (size[0], size[1] + 44), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 9), title[:72], fill=(24, 24, 22), font=FONT)
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
            label_tile("v14 primary: keep first", PRIMARY, (410, 230)),
            label_tile("v15 weak Ankylosaurus LoRA osteoderm-band comparison", V15_ASSET, (410, 230)),
            label_tile("v16 weak Ankylosaurus LoRA sturdy-toe comparison", V16_ASSET, (410, 230)),
        ],
        [
            label_tile("v15 all osteoderm-band attempts", V15_CONTACT, (410, 300)),
            label_tile("v16 all sturdy-toe attempts", V16_CONTACT, (410, 300)),
            label_tile("v16 foot-only mask", V16_MASK, (410, 300)),
        ],
        [
            label_tile("v14 close-review gate", PRIMARY_CROPS, (410, 420)),
            label_tile("previous v5 body/club gate", PREVIOUS_CROPS, (410, 420)),
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
        "Ankylosaurus v15/v16 weak-LoRA i2i review: v14 remains primary; v15/v16 are comparison evidence",
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
        ("v14 primary", PRIMARY),
        ("v15 osteoderms", V15_ASSET),
        ("v16 sturdy toes", V16_ASSET),
    ]
    crop_defs = [
        ("full body", (0, 150, 1672, 840), (330, 138)),
        ("skull/snout", (85, 320, 560, 660), (250, 150)),
        ("mouth/eye", (120, 345, 500, 575), (250, 150)),
        ("armor rows", (505, 205, 1170, 520), (330, 150)),
        ("feet", (280, 610, 1290, 835), (330, 120)),
        ("tail club", (1140, 330, 1640, 650), (260, 150)),
    ]
    gap = 12
    label_w = 150
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 44 + row_h * len(items)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (gap, 12),
        "Ankylosaurus v15/v16 crops: reject if skull, armor rows, four feet, or attached single tail club regress",
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
        "taxonId": "ankylosaurus-magniventris",
        "route": "v14 source, weak Ankylosaurus_Dinosaur LoRA, osteoderm-band v15 and foot-only v16 inpaint",
        "source": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"),
        "selectedComparisons": [
            str(V15_ASSET.relative_to(ROOT)).replace("\\", "/"),
            str(V16_ASSET.relative_to(ROOT)).replace("\\", "/"),
        ],
        "lora": "Ankylosaurus_Dinosaur.safetensors",
        "loraStrength": 0.08,
        "clipStrength": 0.05,
        "v15": {
            "seed": 2026070747,
            "denoise": 0.16,
            "decision": "anatomy-review comparison; do not replace v14 primary",
        },
        "v16": {
            "seed": 2026070750,
            "denoise": 0.14,
            "mask": str(V16_MASK.relative_to(ROOT)).replace("\\", "/"),
            "decision": "anatomy-review comparison; possible foot-read improvement but not enough to replace v14 yet",
        },
        "passChecks": [
            "low armored body preserved",
            "broad blunt skull preserved",
            "single attached tail club preserved",
            "four visible feet preserved at app scale",
        ],
        "remainingRisks": [
            "v15 mostly preserves rather than improving armor layout",
            "v16 may slightly improve toe readability but needs close reference review before promotion",
            "exact toe count and armor-row layout still need final review",
        ],
        "nextRoute": "If continuing Ankylosaurus, use a tighter toe-tip mask or a reviewed ankylosaur foot reference; do not replace v14 unless feet and armor rows visibly improve together without weakening the skull or tail club.",
    }
    REVIEW_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for path in (PRIMARY, PRIMARY_CROPS, PREVIOUS_CROPS, V15_CONTACT, V16_CONTACT, V16_MASK, V15_SOURCE, V16_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)
    shutil.copy2(V15_SOURCE, V15_ASSET)
    shutil.copy2(V16_SOURCE, V16_ASSET)
    make_sheet()
    make_crops()
    write_review()
    print(V15_ASSET)
    print(V16_ASSET)
    print(SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
