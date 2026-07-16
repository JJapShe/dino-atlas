import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

PRIMARY = ASSETS / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
V19 = ASSETS / "triceratops-horridus-nonhoof-toes-i2i-comparison-v19.png"
V9_CROPS = ASSETS / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"
V19_CROPS = ASSETS / "triceratops-nonhoof-toes-i2i-v19-crops.png"
MASK = ASSETS / "triceratops-nonhoof-toes-i2i-mask-v19.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

SELECTED = COMFY_OUTPUT / "next_triceratops_v9_nonhoof_toes_lora_v20_custom_triceratops-horridus_s08_d08_00001_.png"
CONTACT = OUTPUTS / "next_triceratops_v9_nonhoof_toes_lora_v20-contact-sheet.png"

SELECTED_ASSET = ASSETS / "triceratops-horridus-nonhoof-toes-lora-i2i-comparison-v20.png"
SHEET = ASSETS / "triceratops-nonhoof-toes-lora-i2i-v20-review-sheet.png"
CROPS = ASSETS / "triceratops-nonhoof-toes-lora-i2i-v20-crops.png"
REVIEW_JSON = REVIEW_DIR / "trike_nonhoof_toes_lora_i2i_v20_review.json"

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
            label_tile("v9 primary: keep first", PRIMARY, (430, 242)),
            label_tile("v19 no-LoRA toe comparison", V19, (430, 242)),
            label_tile("v20 weak TriceratopsXL LoRA toe comparison", SELECTED_ASSET, (430, 242)),
        ],
        [
            label_tile("all v20 weak-LoRA attempts", CONTACT, (430, 242)),
            label_tile("v9 close-review gate", V9_CROPS, (300, 420)),
            label_tile("v19 crop gate", V19_CROPS, (300, 420)),
            label_tile("v19/v20 foot mask", MASK, (300, 420)),
        ],
    ]
    gap = 16
    margin = 18
    title_h = 54
    row_heights = [max(tile.height for tile in row) for row in rows]
    width = max(sum(tile.width for tile in row) + gap * (len(row) - 1) for row in rows) + margin * 2
    height = title_h + sum(row_heights) + gap * (len(rows) - 1) + margin * 2
    sheet = Image.new("RGB", (width, height), (232, 229, 220))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (margin, margin),
        "Triceratops v20 weak-LoRA non-hoof toe i2i review: v9 remains primary; v20 is comparison evidence",
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
        ("v9 primary", PRIMARY),
        ("v19 no-LoRA toes", V19),
        ("v20 weak-LoRA toes", SELECTED_ASSET),
    ]
    crop_defs = [
        ("full body", (0, 140, 1672, 840), (360, 150)),
        ("head/frill/beak", (0, 160, 620, 610), (280, 200)),
        ("feet strip", (300, 620, 1300, 810), (360, 110)),
        ("front foot", (320, 635, 585, 790), (240, 145)),
        ("middle foot", (760, 640, 1065, 795), (240, 145)),
        ("rear foot", (1010, 635, 1280, 785), (240, 145)),
        ("tail/body", (760, 180, 1672, 560), (320, 135)),
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
        "Triceratops v20 LoRA toe-detail crops: reject if body, frill, horns, beak, tail, or middle/rear feet regress",
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
        "taxonId": "triceratops-horridus",
        "route": "local SDXL inpaint from v9 using tight foot-only mask plus weak TriceratopsXL LoRA",
        "source": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"),
        "selectedCandidate": str(SELECTED_ASSET.relative_to(ROOT)).replace("\\", "/"),
        "mask": str(MASK.relative_to(ROOT)).replace("\\", "/"),
        "lora": "TriceratopsXL0_4.safetensors",
        "loraStrength": 0.08,
        "clipStrength": 0.06,
        "seed": 2026070446,
        "denoise": 0.08,
        "decision": "keep as anatomy-review comparison; do not replace v9 primary",
        "passChecks": [
            "low elongated ceratopsian body preserved",
            "long single tail preserved",
            "four visible limbs preserved",
            "two brow horns, one nasal horn, closed beak, and skull-attached frill preserved",
            "front foot keeps a slightly separated non-hoof toe read without body regression",
        ],
        "remainingRisks": [
            "middle and rear feet are still not a decisive upgrade over v9 or v19",
            "weak LoRA does not improve frill rim detail",
            "representative polish and toe clarity are not strong enough to promote over v9",
        ],
        "nextRoute": "Use a targeted middle/rear-foot mask or ceratopsian-specific foot reference; do not promote toe-only LoRA outputs unless front, middle, and rear feet all improve without rhino body drift.",
    }
    REVIEW_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for path in (SELECTED, CONTACT, PRIMARY, V19, V9_CROPS, V19_CROPS, MASK, GUIDE):
        if not path.exists():
            raise FileNotFoundError(path)
    shutil.copy2(SELECTED, SELECTED_ASSET)
    make_sheet()
    make_crops()
    write_review()
    print(SELECTED_ASSET)
    print(SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
