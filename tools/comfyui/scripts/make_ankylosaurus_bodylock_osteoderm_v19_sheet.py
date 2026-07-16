import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
CURRENT_CROPS = ASSETS / "ankylosaurus-allfeet-lora-i2i-v17-v18-crops.png"
V14_SOURCE = ASSETS / "ankylosaurus-magniventris-broadskull-i2i-v14.png"
TAILCLUB_GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"
LIZARD_DRIFT = ASSETS / "ankylosaurus-magniventris-tailclub-surface-v1.png"

RESULTS_SOURCE = OUTPUTS / "ankylosaurus_bodylock_osteoderm_lowdenoise_v19-results.json"
CONTACT_SOURCE = OUTPUTS / "ankylosaurus_bodylock_osteoderm_lowdenoise_v19-contact-sheet.png"
SELECTED_SOURCE = OUTPUTS / "ankylosaurus_bodylock_osteoderm_lowdenoise_v19_armor_tailclub_bodylock_01_seed2026070152_d22.png"

SELECTED_OUT = ASSETS / "ankylosaurus-magniventris-bodylock-osteoderm-lowdenoise-reject-v19.png"
REVIEW_SHEET = ASSETS / "ankylosaurus-bodylock-osteoderm-lowdenoise-v19-rejection-sheet.png"
CROPS = ASSETS / "ankylosaurus-bodylock-osteoderm-lowdenoise-v19-crops.png"
REVIEW_JSON = REVIEW_DIR / "anky_bodylock_osteoderm_lowdenoise_v19_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


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


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    outputs = []
    for item in data:
        path = Path(item["image"])
        label = f"{item['promptId']} seed {item['seed']} d{item['denoise']:.2f}"
        outputs.append((label, path, item["variation"]))
    return outputs


def panel(path, title, note, size=(430, 242)):
    tile = Image.new("RGB", (size[0], size[1] + 76), (245, 243, 236))
    tile.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    wrap(draw, (8, size[1] + 31), note)
    return tile


def make_review_sheet(outputs):
    items = [
        panel(CURRENT, "current v18 first candidate", "Best current app image: broad low armor, attached single club, and sturdier feet."),
        panel(SELECTED_OUT, "v19 selected reject/reference", "Low-denoise bodylock route keeps the club but does not beat v18 and can lengthen the lizard-like body."),
        panel(CONTACT_SOURCE, "all v19 attempts", "Eight RealVisXL low-denoise probes from v18 using bodylock and osteoderm prompts."),
        panel(CURRENT_CROPS, "v18 crop gate", "Baseline crop audit remains stronger for skull, armor, feet, and tail-club comparison."),
        panel(V14_SOURCE, "previous v14 body/head gate", "Earlier first candidate before all-feet v18; useful for checking skull and body drift."),
        panel(TAILCLUB_GUIDE, "armor/tail-club guide", "Project-owned structure guide: broad blunt skull, low body, rounded armor, single club."),
        panel(LIZARD_DRIFT, "tail-club lizard-drift failure", "Failure anchor: a tail club alone is not enough if the body reads like a generic lizard."),
    ]
    for label, path, variation in outputs:
        items.append(panel(path, f"v19 {label}", f"Prompt: {variation}"))

    cols = 3
    w, h = items[0].size
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (232, 228, 218))
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


def make_crops(outputs):
    rows = [("v18 current", CURRENT), ("v19 selected reject", SELECTED_OUT)]
    rows.extend((f"v19 {label}", path) for label, path, _ in outputs)
    rows.append(("v18 crop gate", CURRENT_CROPS))

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
    label_w = 178
    row_h = max(size[1] + 34 for _, _, size in crop_defs) + gap
    width = label_w + sum(size[0] for _, _, size in crop_defs) + gap * (len(crop_defs) + 1)
    height = 44 + row_h * len(rows)
    sheet = Image.new("RGB", (width, height), (236, 233, 224))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (gap, 12),
        "Ankylosaurus v19 low-denoise crops: keep below v18 unless skull breadth, low armor, feet, and single club improve together",
        fill=(24, 24, 22),
        font=FONT,
    )
    y = 44
    for label, path in rows:
        if path == CURRENT_CROPS:
            image = Image.open(path)
            sheet.paste(fit(image, (width - 2 * gap, row_h - gap)), (gap, y))
            y += row_h
            continue
        draw.rectangle([(0, y), (width, y + row_h - 1)], fill=(248, 247, 242))
        draw.text((gap, y + gap), label[:24], fill=(24, 24, 22), font=FONT)
        x = label_w
        for title, box, size in crop_defs:
            tile = crop_tile(path, title, box, size)
            sheet.paste(tile, (x, y + gap))
            x += tile.width + gap
        y += row_h
    sheet.save(CROPS)


def write_review(outputs):
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "bodylock_osteoderm_lowdenoise_v19",
                "sourceImage": relative(CURRENT),
                "selectedRejectReference": relative(SELECTED_OUT),
                "contactSheet": relative(CONTACT_SOURCE),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROPS),
                "decision": "reject_reference",
                "reason": (
                    "Whole-body low-denoise RealVisXL i2i from v18 preserves the attached single tail club "
                    "but does not improve skull breadth, foot clarity, or armor layout enough to replace v18. "
                    "Several outputs lengthen the body/snout and increase generic lizard-read risk."
                ),
                "outputs": [
                    {
                        "label": label,
                        "image": relative(path),
                        "variation": variation,
                        "decision": "reject_reference",
                    }
                    for label, path, variation in outputs
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V14_SOURCE, TAILCLUB_GUIDE, LIZARD_DRIFT, RESULTS_SOURCE, CONTACT_SOURCE, SELECTED_SOURCE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    outputs = load_outputs()
    shutil.copy2(SELECTED_SOURCE, SELECTED_OUT)
    make_review_sheet(outputs)
    make_crops(outputs)
    write_review(outputs)
    print(
        json.dumps(
            {
                "selected": relative(SELECTED_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROPS),
                "review": relative(REVIEW_JSON),
                "outputs": len(outputs),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
