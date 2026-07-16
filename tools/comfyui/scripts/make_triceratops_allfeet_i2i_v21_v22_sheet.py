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
PRIMARY_CROPS = ASSETS / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"
V20_CROPS = ASSETS / "triceratops-nonhoof-toes-lora-i2i-v20-crops.png"
MASK_SOURCE = OUTPUTS / "triceratops_v9_allfeet_mask_v21.png"
MASK_SHEET = OUTPUTS / "triceratops_v9_allfeet_mask_v21-sheet.png"
CONTACT_V21 = OUTPUTS / "triceratops_allfeet_nonhoof_v21-contact-sheet.png"
CONTACT_V22 = OUTPUTS / "triceratops_allfeet_lora_v22-contact-sheet.png"

V21_SELECTED = COMFY_OUTPUT / "triceratops_allfeet_nonhoof_v21_custom_triceratops-horridus_d18_00002_.png"
V22_SELECTED = COMFY_OUTPUT / "triceratops_allfeet_lora_v22_custom_triceratops-horridus_s06_d18_00002_.png"

V21_OUT = ASSETS / "triceratops-horridus-allfeet-i2i-comparison-v21.png"
V22_OUT = ASSETS / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
MASK_OUT = ASSETS / "triceratops-allfeet-i2i-mask-v21.png"
REVIEW_SHEET = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-review-sheet.png"
CROPS = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
REVIEW_JSON = REVIEW_DIR / "trike_allfeet_lora_i2i_v21_v22_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (245, 243, 236))
    tile.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return tile


def wrapped(draw, xy, text, max_chars=58, max_lines=2):
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
    shutil.copy2(V21_SELECTED, V21_OUT)
    shutil.copy2(V22_SELECTED, V22_OUT)
    shutil.copy2(MASK_SOURCE, MASK_OUT)


def tile(path, title, note, size=(430, 242)):
    image = Image.open(path).convert("RGB")
    panel = Image.new("RGB", (size[0], size[1] + 74), (245, 243, 236))
    panel.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    wrapped(draw, (8, size[1] + 31), note)
    return panel


def make_review_sheet():
    items = [
        tile(PRIMARY, "current v9: previous first", "Strong anti-rhino body/head gate, but feet still read slightly blocky."),
        tile(V22_OUT, "v22 all-feet weak-LoRA comparison", "Best all-feet pass: toe separation improves while body, frill, beak, horns, and tail stay stable."),
        tile(V21_OUT, "v21 all-feet no-LoRA comparison", "Same mask without LoRA. Useful preservation control, but toe separation is softer than v22."),
        tile(MASK_SHEET, "v21/v22 all-feet mask", "Mask covers visible lower feet only; head, frill, horns, body, and tail remain unmasked."),
        tile(CONTACT_V21, "all v21 no-LoRA attempts", "Low-denoise all-feet probes with no LoRA."),
        tile(CONTACT_V22, "all v22 weak-LoRA attempts", "Weak TriceratopsXL probes. d0.18 gives the clearest toe separation."),
        tile(PRIMARY_CROPS, "v9 close-review gate", "Use this as the previous body/head/feet/tail gate."),
        tile(V20_CROPS, "v20 previous toe gate", "Earlier weak-LoRA pass mostly improved the front foot only."),
    ]
    cols = 4
    panel_w = items[0].width
    panel_h = items[0].height
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * panel_w, rows * panel_h), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * panel_w, (idx // cols) * panel_h))
    sheet.save(REVIEW_SHEET)


def crop_tile(path, title, box, size):
    image = Image.open(path).convert("RGB").crop(box)
    panel = Image.new("RGB", (size[0], size[1] + 34), (248, 247, 242))
    panel.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 10), title[:64], fill=(24, 24, 22), font=FONT)
    return panel


def make_crops():
    rows = [
        ("v9 primary", PRIMARY),
        ("v21 no-LoRA all-feet", V21_OUT),
        ("v22 weak-LoRA all-feet", V22_OUT),
    ]
    crop_defs = [
        ("full body", (0, 140, 1672, 840), (360, 150)),
        ("head/frill/beak", (0, 150, 620, 610), (280, 205)),
        ("feet strip", (260, 610, 1325, 820), (380, 125)),
        ("front foot", (300, 635, 590, 810), (250, 150)),
        ("middle foot", (700, 630, 1035, 820), (250, 150)),
        ("rear foot", (990, 630, 1305, 810), (250, 150)),
        ("tail/body", (740, 180, 1672, 560), (320, 135)),
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
        "Triceratops v21/v22 all-feet i2i crops: promote only if all feet improve without rhino body, beak, horn, frill, or tail regression",
        fill=(24, 24, 22),
        font=FONT,
    )
    y = 44
    for label, path in rows:
        draw.rectangle([(0, y), (width, y + row_h - 1)], fill=(248, 247, 242))
        draw.text((gap, y + gap), label, fill=(24, 24, 22), font=FONT)
        x = label_w
        for title, box, size in crop_defs:
            panel = crop_tile(path, title, box, size)
            sheet.paste(panel, (x, y + gap))
            x += panel.width + gap
        y += row_h
    sheet.save(CROPS)


def write_review():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "triceratops-horridus",
                "experiment": "allfeet_lora_i2i_v21_v22",
                "sourceImage": relative(PRIMARY),
                "maskImage": relative(MASK_OUT),
                "comparisonNoLora": relative(V21_OUT),
                "comparisonWeakLora": relative(V22_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROPS),
                "decision": "promote_candidate_pending_app_review",
                "selectedSeed": 2026070914,
                "selectedDenoise": 0.18,
                "lora": "TriceratopsXL0_4.safetensors",
                "loraStrength": 0.06,
                "clipStrength": 0.04,
                "reasons": [
                    "v22 improves toe separation across the visible feet more than v19/v20 while preserving the v9 anti-rhino body gate",
                    "closed beak, two brow horns, one nasal horn, skull-attached frill, low elongated body, and long tail remain stable",
                    "white claw highlights are more visible, so final promotion still needs close human review against the crop sheet",
                ],
                "keepComparisonGate": relative(PRIMARY),
                "nextRoute": "If v22 is accepted manually, use it as the new Triceratops primary; otherwise keep v9 and try an even tighter toe-tip mask to reduce bright claw overemphasis.",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (PRIMARY, PRIMARY_CROPS, V20_CROPS, MASK_SOURCE, MASK_SHEET, CONTACT_V21, CONTACT_V22, V21_SELECTED, V22_SELECTED):
        if not path.exists():
            raise FileNotFoundError(path)
    copy_assets()
    make_review_sheet()
    make_crops()
    write_review()
    print(V21_OUT)
    print(V22_OUT)
    print(MASK_OUT)
    print(REVIEW_SHEET)
    print(CROPS)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
