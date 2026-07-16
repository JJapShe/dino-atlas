import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

SELECTED = COMFY_OUTPUT / "next_triceratops_v9_nonhoof_toes_v19_custom_triceratops-horridus_d10_00002_.png"
MASK = OUTPUTS / "next_triceratops_v9_nonhoof_toes_v19_custom_mask.png"

PRIMARY = ASSETS / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
V18 = ASSETS / "triceratops-horridus-toe-i2i-comparison-v18.png"
V9_CROPS = ASSETS / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"
V18_CROPS = ASSETS / "triceratops-toe-i2i-v18-crops.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

SELECTED_ASSET = ASSETS / "triceratops-horridus-nonhoof-toes-i2i-comparison-v19.png"
MASK_ASSET = ASSETS / "triceratops-nonhoof-toes-i2i-mask-v19.png"
SHEET = ASSETS / "triceratops-nonhoof-toes-i2i-v19-review-sheet.png"
CROPS = ASSETS / "triceratops-nonhoof-toes-i2i-v19-crops.png"
REVIEW_JSON = REVIEW_DIR / "trike_nonhoof_toes_i2i_v19_review.json"


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


def make_sheet():
    rows = [
        [
            label_tile("v9 primary: keep first", PRIMARY, (500, 280)),
            label_tile("v18 toe i2i: anatomy review", V18, (500, 280)),
            label_tile("v19 selected: local toe comparison", SELECTED_ASSET, (500, 280)),
        ],
        [
            label_tile("v9 close-review gate", V9_CROPS, (360, 500)),
            label_tile("v18 crop comparison", V18_CROPS, (360, 500)),
            label_tile("v19 foot mask", MASK_ASSET, (360, 500)),
            label_tile("body-lock guide", GUIDE, (360, 500)),
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
        "Triceratops v19 non-hoof toe i2i review: v9 remains primary; v19 is comparison evidence",
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
        ("v18 comparison", V18),
        ("v19 local toe i2i", SELECTED_ASSET),
    ]
    crop_defs = [
        ("full body", (0, 140, 1672, 840), (360, 150)),
        ("head/frill/beak", (0, 160, 620, 610), (280, 200)),
        ("feet strip", (300, 620, 1300, 810), (360, 110)),
        ("front foot", (320, 635, 585, 790), (240, 145)),
        ("middle foot", (760, 640, 1065, 795), (240, 145)),
        ("rear foot", (1010, 635, 1280, 785), (240, 145)),
    ]
    gap = 12
    label_w = 140
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 44 + row_h * len(items)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (gap, 12),
        "Triceratops v19 toe-detail crops: reject if body count, frill, horns, beak, or toe read regresses",
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
        "route": "local SDXL inpaint from v9 using a tight foot-only mask",
        "source": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"),
        "selectedCandidate": str(SELECTED_ASSET.relative_to(ROOT)).replace("\\", "/"),
        "mask": str(MASK_ASSET.relative_to(ROOT)).replace("\\", "/"),
        "seed": 2026070445,
        "denoise": 0.10,
        "decision": "keep as anatomy-review comparison; do not replace v9 primary",
        "passChecks": [
            "low elongated ceratopsian body preserved",
            "long single tail preserved",
            "four visible limbs preserved",
            "two brow horns, one nasal horn, closed beak, and skull-attached frill preserved",
            "front foot gets a slightly clearer separated-toe read than v9",
        ],
        "remainingRisks": [
            "middle and rear feet are still not a decisive upgrade over v9",
            "local toe edit does not improve frill rim detail",
            "representative polish is not strong enough to promote over v9",
        ],
    }
    REVIEW_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    if not SELECTED.exists():
        raise FileNotFoundError(SELECTED)
    if not MASK.exists():
        raise FileNotFoundError(MASK)
    shutil.copy2(SELECTED, SELECTED_ASSET)
    shutil.copy2(MASK, MASK_ASSET)
    make_sheet()
    make_crops()
    write_review()
    print(SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
