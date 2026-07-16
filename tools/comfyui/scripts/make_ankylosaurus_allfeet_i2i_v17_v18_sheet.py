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
V16_CROPS = ASSETS / "ankylosaurus-lora-i2i-v15-v16-crops.png"
MASK_SOURCE = OUTPUTS / "ankylosaurus_v14_allfeet_mask_v17.png"
MASK_SHEET = OUTPUTS / "ankylosaurus_v14_allfeet_mask_v17-sheet.png"
CONTACT_V17 = OUTPUTS / "ankylosaurus_allfeet_v17-contact-sheet.png"
CONTACT_V18 = OUTPUTS / "ankylosaurus_allfeet_lora_v18-contact-sheet.png"

V17_SELECTED = COMFY_OUTPUT / "ankylosaurus_allfeet_v17_custom_ankylosaurus-magniventris_d18_00002_.png"
V18_SELECTED = COMFY_OUTPUT / "ankylosaurus_allfeet_lora_v18_custom_ankylosaurus-magniventris_s06_d18_00002_.png"

V17_OUT = ASSETS / "ankylosaurus-magniventris-allfeet-i2i-comparison-v17.png"
V18_OUT = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
MASK_OUT = ASSETS / "ankylosaurus-allfeet-i2i-mask-v17.png"
REVIEW_SHEET = ASSETS / "ankylosaurus-allfeet-lora-i2i-v17-v18-review-sheet.png"
CROPS = ASSETS / "ankylosaurus-allfeet-lora-i2i-v17-v18-crops.png"
REVIEW_JSON = REVIEW_DIR / "anky_allfeet_lora_i2i_v17_v18_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (245, 243, 236))
    tile.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return tile


def wrap(draw, xy, text, max_chars=58, max_lines=2):
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
        draw.text((x, y + idx * 15), line, fill=(43, 39, 34), font=FONT)


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def copy_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(V17_SELECTED, V17_OUT)
    shutil.copy2(V18_SELECTED, V18_OUT)
    shutil.copy2(MASK_SOURCE, MASK_OUT)


def panel(path, title, note, size=(430, 242)):
    image = Image.open(path).convert("RGB")
    tile = Image.new("RGB", (size[0], size[1] + 74), (245, 243, 236))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    wrap(draw, (8, size[1] + 31), note)
    return tile


def make_review_sheet():
    items = [
        panel(PRIMARY, "current v14: previous first", "Strong body, armor, skull repair, and attached tail club; feet remain a little soft."),
        panel(V18_OUT, "v18 all-feet weak-LoRA candidate", "Best all-feet pass: feet read sturdier while skull, armor rows, body, and club stay stable."),
        panel(V17_OUT, "v17 all-feet no-LoRA comparison", "Same mask without LoRA. Useful preservation control, but feet are softer than v18."),
        panel(MASK_SHEET, "v17/v18 all-feet mask", "Mask covers lower foot regions only; skull, armor, tail shaft, and club remain unmasked."),
        panel(CONTACT_V17, "all v17 no-LoRA attempts", "Low-denoise all-feet probes with no LoRA."),
        panel(CONTACT_V18, "all v18 weak-LoRA attempts", "Weak Ankylosaurus LoRA probes. d0.18 gives the clearest sturdy-foot read."),
        panel(PRIMARY_CROPS, "v14 close-review gate", "Previous skull/body/feet/club gate."),
        panel(V16_CROPS, "v15/v16 previous LoRA gate", "Earlier weak-LoRA comparisons improved feet only slightly."),
    ]
    cols = 4
    w, h = items[0].size
    sheet = Image.new("RGB", (cols * w, ((len(items) + cols - 1) // cols) * h), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * w, (idx // cols) * h))
    sheet.save(REVIEW_SHEET)


def crop_tile(path, title, box, size):
    image = Image.open(path).convert("RGB").crop(box)
    tile = Image.new("RGB", (size[0], size[1] + 34), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 10), title[:64], fill=(24, 24, 22), font=FONT)
    return tile


def make_crops():
    rows = [
        ("v14 primary", PRIMARY),
        ("v17 no-LoRA all-feet", V17_OUT),
        ("v18 weak-LoRA all-feet", V18_OUT),
    ]
    crop_defs = [
        ("full body", (0, 90, 1768, 815), (360, 148)),
        ("skull/snout", (0, 180, 530, 520), (260, 170)),
        ("armor rows", (420, 180, 1240, 520), (320, 135)),
        ("feet strip", (170, 570, 1435, 845), (390, 125)),
        ("front feet", (180, 590, 790, 845), (300, 145)),
        ("rear feet", (750, 565, 1420, 845), (300, 145)),
        ("tail club", (1210, 365, 1768, 650), (280, 145)),
    ]
    gap = 12
    label_w = 150
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 44 + row_h * len(rows)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (gap, 12),
        "Ankylosaurus v17/v18 all-feet i2i crops: promote only if feet improve without skull, armor, body, or tail-club regression",
        fill=(24, 24, 22),
        font=FONT,
    )
    y = 44
    for label, path in rows:
        draw.rectangle([(0, y), (width, y + row_h - 1)], fill=(248, 247, 242))
        draw.text((gap, y + gap), label, fill=(24, 24, 22), font=FONT)
        x = label_w
        for title, box, size in crop_defs:
            tile = crop_tile(path, title, box, size)
            sheet.paste(tile, (x, y + gap))
            x += tile.width + gap
        y += row_h
    sheet.save(CROPS)


def write_review():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "allfeet_lora_i2i_v17_v18",
                "sourceImage": relative(PRIMARY),
                "maskImage": relative(MASK_OUT),
                "comparisonNoLora": relative(V17_OUT),
                "promotedCandidate": relative(V18_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROPS),
                "decision": "promote_candidate_pending_app_review",
                "selectedSeed": 2026070924,
                "selectedDenoise": 0.18,
                "lora": "Ankylosaurus_Dinosaur.safetensors",
                "loraStrength": 0.06,
                "clipStrength": 0.04,
                "reasons": [
                    "v18 keeps the v14 broad low body, compact skull, dense osteoderm rows, thick tail, and attached oval tail club",
                    "v18 improves visible sturdy-foot and toe separation compared with v14 and the previous v16 foot comparison",
                    "the change is local to the feet, so skull, armor layout, and tail club remain stable",
                ],
                "remainingRisks": [
                    "exact toe count and foot proportions still need final reference review",
                    "the skull remains acceptable but could still be broader and blunter in a future head-specific pass",
                ],
                "previousPrimary": relative(PRIMARY),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (PRIMARY, PRIMARY_CROPS, V16_CROPS, MASK_SOURCE, MASK_SHEET, CONTACT_V17, CONTACT_V18, V17_SELECTED, V18_SELECTED):
        if not path.exists():
            raise FileNotFoundError(path)
    copy_assets()
    make_review_sheet()
    make_crops()
    write_review()
    print(V17_OUT)
    print(V18_OUT)
    print(MASK_OUT)
    print(REVIEW_SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
