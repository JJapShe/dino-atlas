import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

PREVIOUS = ASSETS / "ankylosaurus-magniventris-imagegen-v32-source-candidate.png"
V18 = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
V33 = ASSETS / "ankylosaurus-magniventris-imagegen-v33-source-candidate.png"
V34 = ASSETS / "ankylosaurus-magniventris-imagegen-v34-source-candidate.png"
V35 = ASSETS / "ankylosaurus-magniventris-imagegen-v35-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p6-v33-v35-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p6-v33-v35-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p6_v33_v35_review.json"

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
        tile(V34, "v34 promoted count-level pass", "Best current ankylosaurid read: broad blunt head, low tank body, dense armor, one attached club."),
        tile(PREVIOUS, "previous v32 count-level pass", "Previous first image; still useful, but cheek knob and long-tail risk are stronger."),
        tile(V33, "v33 compact-body hold", "Strong low body and attached club; tail remains long, so keep as comparison."),
        tile(V35, "v35 broad-armor hold", "Strong armor and body mass, but head reads a little longer and framing is tighter."),
        tile(V18, "previous v18 all-feet hold", "Earlier LoRA/i2i foot repair; useful but less immediate Ankylosaurus identity than v34."),
        tile(GUIDE, "armor tail-club guide", "Control target: broad skull, short neck, low osteoderms, four sturdy feet, one attached club."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("v34 promoted", V34),
        ("previous v32", PREVIOUS),
        ("v33 hold", V33),
        ("v35 hold", V35),
        ("previous v18 hold", V18),
        ("armor tail-club guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("skull/snout", (0.00, 0.18, 0.34, 0.64), (360, 210)),
        ("armor rows", (0.16, 0.10, 0.74, 0.58), (390, 210)),
        ("feet/legs", (0.08, 0.56, 0.78, 0.96), (390, 210)),
        ("tail club", (0.56, 0.24, 1.0, 0.74), (390, 210)),
        ("body compactness", (0.18, 0.20, 0.86, 0.84), (410, 210)),
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
                "experiment": "p6_v33_v35_compact_bluntskull_tailclub_candidates",
                "previousPrimary": relative(PREVIOUS),
                "promotedPrimary": relative(V34),
                "selectedReviewHolds": [relative(V33), relative(V35), relative(V18)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v34_to_count_level_pass",
                "reason": (
                    "V34 gives the strongest current Ankylosaurus read because the head is broader and blunter than v32, "
                    "the body is lower and more tank-like, the armor stays as low rounded osteoderms, all four feet remain visible, "
                    "and the tail ends in one attached oval club. V33 and v35 are useful review holds but keep more long-tail or tighter-frame risk."
                ),
                "remainingRisks": [
                    "tail still trends longer than ideal for a compact ankylosaurid",
                    "exact skull proportions and side armor layout need final reference review",
                    "toe shapes are count-level, not final approval",
                ],
                "rejectIfPromoting": [
                    "body reads as crocodile, monitor lizard, pangolin, turtle, armadillo, or rhinoceros",
                    "skull becomes long and narrow or develops horns/frill",
                    "tail is long and whip-like instead of short and thick",
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
    required = [PREVIOUS, V18, V33, V34, V35, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
