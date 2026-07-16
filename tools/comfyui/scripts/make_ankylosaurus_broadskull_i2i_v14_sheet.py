import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

SELECTED = COMFY_OUTPUT / "next_ankylosaurus_v5_broadskull_v14_custom_ankylosaurus-magniventris_d12_00001_.png"
MASK = OUTPUTS / "next_ankylosaurus_v5_broadskull_v14_custom_mask.png"

V5 = ASSETS / "ankylosaurus-magniventris-broadskull-singleclub-imagegen-v5.png"
V5_CROPS = ASSETS / "ankylosaurus-broadskull-singleclub-crops-v5.png"
V13 = ASSETS / "ankylosaurus-magniventris-bodylock-i2i-comparison-v13.png"
V13_CROPS = ASSETS / "ankylosaurus-bodylock-i2i-crops-v13.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

SELECTED_ASSET = ASSETS / "ankylosaurus-magniventris-broadskull-i2i-v14.png"
MASK_ASSET = ASSETS / "ankylosaurus-broadskull-i2i-mask-v14.png"
SHEET = ASSETS / "ankylosaurus-broadskull-i2i-v14-review-sheet.png"
CROPS = ASSETS / "ankylosaurus-broadskull-i2i-v14-crops.png"
REVIEW_JSON = REVIEW_DIR / "anky_broadskull_i2i_v14_review.json"

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
    image = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = box
    x1 = max(0, min(x1, image.width))
    x2 = max(0, min(x2, image.width))
    y1 = max(0, min(y1, image.height))
    y2 = max(0, min(y2, image.height))
    crop = image.crop((x1, y1, x2, y2))
    tile = Image.new("RGB", (size[0], size[1] + 34), (248, 247, 242))
    tile.paste(fit(crop, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 10), title, fill=(24, 24, 22), font=FONT)
    return tile


def make_sheet():
    rows = [
        [
            label_tile("v14 selected: broad-skull local i2i", SELECTED_ASSET, (500, 250)),
            label_tile("v5 source: previous primary", V5, (500, 250)),
            label_tile("v13 body-lock comparison", V13, (500, 250)),
        ],
        [
            label_tile("v14 crop audit", CROPS, (360, 500)),
            label_tile("v5 crop gate", V5_CROPS, (360, 500)),
            label_tile("v13 crop comparison", V13_CROPS, (360, 500)),
            label_tile("head-only mask", MASK_ASSET, (360, 500)),
            label_tile("armor/tail-club guide", GUIDE, (360, 500)),
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
        "Ankylosaurus v14 broad-skull i2i review: promote only if head improves without body, feet, or club regression",
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
        ("v14 broad-skull i2i", SELECTED_ASSET),
        ("v5 previous primary", V5),
        ("v13 body-lock comparison", V13),
    ]
    crop_defs = [
        ("full body", (0, 70, 1774, 820), (360, 152)),
        ("skull/snout", (0, 230, 560, 570), (300, 180)),
        ("mouth/eye", (0, 330, 380, 540), (260, 140)),
        ("armor rows", (360, 120, 1220, 500), (320, 150)),
        ("feet", (430, 520, 1250, 760), (320, 130)),
        ("tail club", (1120, 360, 1774, 705), (300, 150)),
    ]
    gap = 12
    label_w = 150
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 46 + row_h * len(items)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (gap, 14),
        "Ankylosaurus v14 crop audit: skull, armor rows, feet, and attached single tail club",
        fill=(24, 24, 22),
        font=FONT,
    )
    y = 46
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
        "route": "local SDXL inpaint from v5 using a tight head-only mask",
        "source": str(V5.relative_to(ROOT)).replace("\\", "/"),
        "selectedCandidate": str(SELECTED_ASSET.relative_to(ROOT)).replace("\\", "/"),
        "mask": str(MASK_ASSET.relative_to(ROOT)).replace("\\", "/"),
        "seed": 2026070645,
        "denoise": 0.12,
        "decision": "promote ahead of v5 as the first count-level candidate",
        "passChecks": [
            "broad low armored body preserved",
            "dense low rounded osteoderm rows preserved",
            "four visible sturdy feet preserved",
            "thick low tail and single attached oval club preserved",
            "head reads slightly shorter and more blunt than the v5 source",
        ],
        "remainingRisks": [
            "species-level skull proportions still need reference review",
            "toe detail remains only count-level rather than final",
            "armor layout is strong at app scale but not scientifically audited plate-by-plate",
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
    make_crops()
    make_sheet()
    write_review()
    print(SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
