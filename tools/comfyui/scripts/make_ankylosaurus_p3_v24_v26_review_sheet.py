import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
CURRENT_CROPS = ASSETS / "ankylosaurus-allfeet-lora-i2i-v17-v18-crops.png"
V22 = ASSETS / "ankylosaurus-magniventris-imagegen-v22-source-candidate.png"
V23 = ASSETS / "ankylosaurus-magniventris-imagegen-v23-source-candidate.png"
V24 = ASSETS / "ankylosaurus-magniventris-imagegen-v24-source-candidate.png"
V25 = ASSETS / "ankylosaurus-magniventris-imagegen-v25-source-candidate.png"
V26 = ASSETS / "ankylosaurus-magniventris-imagegen-v26-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p3-v24-v26-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p3-v24-v26-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p3_v24_v26_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, max_chars=58, max_lines=3):
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
    panel = Image.new("RGB", (size[0], size[1] + 86), (245, 243, 236))
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
        tile(CURRENT, "current v18 app first", "Current count-level app first: attached club and visible feet, but broad-skull/identity still needs review."),
        tile(V25, "v25 compact skull hold", "Best P3 balance: compact broad head, low armor rows, four feet, and attached single club; check rear-leg overlap."),
        tile(V24, "v24 tail-club hold", "Good attached club and low armored body; mild long-snout and long-body lizard drift risk remains."),
        tile(V26, "v26 armor hold", "Strong low armor and blunt head read; rear feet/leg separation need close crop review before promotion."),
        tile(V22, "previous v22 hold", "Previous best prompt-only balance with broad skull, low armor, four feet, and attached club."),
        tile(V23, "previous v23 hold", "Previous low broad armor hold; useful comparison for body-length and monitor-lizard drift."),
        tile(GUIDE, "armor tail-club guide", "Control target: broad skull, very short neck, low osteoderms, four sturdy feet, one attached oval club."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v18", CURRENT),
        ("v25 compact skull hold", V25),
        ("v24 tail-club hold", V24),
        ("v26 armor hold", V26),
        ("previous v22 hold", V22),
        ("previous v23 hold", V23),
        ("armor tail-club guide", GUIDE),
        ("v18 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("skull/snout", (0.00, 0.20, 0.34, 0.62), (360, 210)),
        ("armor rows", (0.16, 0.12, 0.74, 0.58), (390, 210)),
        ("feet/legs", (0.08, 0.56, 0.78, 0.96), (390, 210)),
        ("tail club", (0.62, 0.26, 1.0, 0.70), (390, 210)),
        ("body compactness", (0.20, 0.22, 0.86, 0.82), (410, 210)),
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
        if path == CURRENT_CROPS:
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
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "p3_v24_v26_broadskull_armor_tailclub_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V25),
                "comparisonReviewHolds": [relative(V24), relative(V26), relative(V22), relative(V23)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V25 is the best P3 prompt-only hold because it most clearly combines a compact broad skull, low rounded osteoderm rows, "
                    "four grounded feet, and a single attached oval tail club. It remains below final approval because rear-leg separation and "
                    "exact ankylosaurid body compactness need human crop review. V24 keeps a clean club but has mild long-snout/long-body risk. "
                    "V26 has useful low armor and blunt-head cues but needs rear-foot separation review."
                ),
                "nextRoute": (
                    "Use v25 as the next project-owned review hold for i2i or ControlNet passes. Do not promote or train until the crop gate "
                    "confirms non-lizard proportions, four sturdy feet, rounded low armor, broad blunt skull, and one attached tail club together."
                ),
                "rejectIfPromoting": [
                    "body reads as crocodile, monitor lizard, pangolin, turtle, armadillo, or rhinoceros",
                    "skull becomes long and narrow or develops horns/frill",
                    "tail club is missing, detached, doubled, soft, spiked, or replaced by a paddle",
                    "armor becomes tall Stegosaurus plates or fantasy spikes",
                    "feet are hidden, fused, extra, or the animal reads as six-legged",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V22, V23, V24, V25, V26, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(
        json.dumps(
            {
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "review": relative(REVIEW_JSON),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
