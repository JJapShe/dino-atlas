import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "sauropod_apatosaurus" / "review"

CURRENT = ASSETS / "apatosaurus-ajax-smallhead-imagegen-v2.png"
CURRENT_CROPS = ASSETS / "apatosaurus-smallhead-crops-v2.png"
V3 = ASSETS / "apatosaurus-ajax-imagegen-v3-source-candidate.png"
V4 = ASSETS / "apatosaurus-ajax-imagegen-v4-source-candidate.png"
V5 = ASSETS / "apatosaurus-ajax-imagegen-v5-source-candidate.png"
GUIDE = ASSETS / "apatosaurus-ajax-lowneck-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSETS / "apatosaurus-lowneck-bodylock-crops-v3.png"

REVIEW_SHEET = ASSETS / "apatosaurus-p1-v3-v5-review-sheet.png"
CROP_SHEET = ASSETS / "apatosaurus-p1-v3-v5-crops.png"
REVIEW_JSON = REVIEW_ROOT / "apatosaurus_p1_v3_v5_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, max_chars=58, max_lines=2):
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
        draw.text((x, y + idx * 15), wrapped, fill=(43, 39, 34), font=FONT)


def tile(path, title, note, size=(430, 242)):
    panel = Image.new("RGB", (size[0], size[1] + 76), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(V3, "v3 new count-level pass", "Best fresh prompt-only source: low neck, long horizontal tail, four visible legs, no high shoulder drift."),
        tile(CURRENT, "previous v2 train seed", "Stable older candidate; keep as comparison because skull and foot detail remain useful."),
        tile(V4, "v4 review hold", "Very similar low-neck result with clean feet, but slightly heavier head/neck and edge crop risk."),
        tile(V5, "v5 tail-tip risk hold", "Good low-neck body, but tail tip bends and rear foot overlap are weaker than v3."),
        tile(GUIDE, "low-neck body-lock guide", "Project-owned control target for low neck, similar limb height, four open feet, and long tail."),
        tile(CURRENT_CROPS, "v2 crop gate", "Existing close-review sheet for old first candidate and open-foot comparisons."),
    ]

    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    REVIEW_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("v3 new pass", V3),
        ("previous v2", CURRENT),
        ("v4 hold", V4),
        ("v5 tail risk", V5),
        ("body-lock guide", GUIDE),
        ("v2 existing crop gate", CURRENT_CROPS),
        ("body-lock crop gate", BODYLOCK_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.08, 1.00, 0.90), (430, 210)),
        ("head/low neck", (0.00, 0.22, 0.35, 0.58), (360, 210)),
        ("shoulder/torso", (0.20, 0.28, 0.60, 0.72), (360, 210)),
        ("front feet", (0.20, 0.55, 0.43, 0.93), (320, 210)),
        ("rear feet", (0.43, 0.55, 0.69, 0.93), (320, 210)),
        ("tail", (0.55, 0.30, 1.00, 0.62), (380, 210)),
    ]
    gap = 10
    label_h = 34
    col_w = 440
    row_h = 224
    sheet = Image.new(
        "RGB",
        (gap + len(crops) * (col_w + gap), gap + len(rows) * (row_h + label_h + gap)),
        (232, 228, 218),
    )
    for row_idx, (row_label, path) in enumerate(rows):
        image = Image.open(path).convert("RGB")
        y = gap + row_idx * (row_h + label_h + gap)
        if path in (CURRENT_CROPS, BODYLOCK_CROPS):
            sheet.paste(fit(image, (sheet.width - gap * 2, row_h + label_h)), (gap, y))
            continue
        for col_idx, (crop_label, box, size) in enumerate(crops):
            x = gap + col_idx * (col_w + gap)
            panel = Image.new("RGB", (col_w, row_h + label_h), (245, 243, 236))
            panel.paste(fit(fractional_crop(image, box), size), ((col_w - size[0]) // 2, 0))
            draw = ImageDraw.Draw(panel)
            draw.text((8, row_h + 8), f"{row_label}: {crop_label}"[:66], fill=(43, 39, 34), font=FONT)
            sheet.paste(panel, (x, y))
    sheet.save(CROP_SHEET)


def write_review_json():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "apatosaurus-ajax",
                "experiment": "p1_v3_v5_source_candidates",
                "previousPrimary": relative(CURRENT),
                "selectedPrimary": relative(V3),
                "reviewHolds": [relative(V4), relative(V5)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v3_count_level_pass",
                "reason": (
                    "V3 improves the low-neck Apatosaurus read over v2 by keeping the neck almost horizontal, the shoulders low, "
                    "the full long tail in frame, and exactly four visible pillar legs without Brachiosaurus drift. Keep v2 as a "
                    "supporting review hold because skull and foot detail remain count-level rather than final."
                ),
                "rejectIfPromoting": [
                    "neck rises into a vertical or Brachiosaurus-like pose",
                    "forelimbs become taller than hind limbs or shoulders peak above the hips",
                    "tail is cropped, duplicated, too short, or dragging on the ground",
                    "feet are hidden or shadows create extra limb silhouettes",
                    "head becomes predator-like, toothy, mammal-like, or too large"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V3, V4, V5, GUIDE, BODYLOCK_CROPS]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
