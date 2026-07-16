import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

PREVIOUS = ASSETS / "ankylosaurus-magniventris-imagegen-v34-source-candidate.png"
V32 = ASSETS / "ankylosaurus-magniventris-imagegen-v32-source-candidate.png"
V36 = ASSETS / "ankylosaurus-magniventris-imagegen-v36-source-candidate.png"
V37 = ASSETS / "ankylosaurus-magniventris-imagegen-v37-source-candidate.png"
V38 = ASSETS / "ankylosaurus-magniventris-imagegen-v38-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p7-v36-v38-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p7-v36-v38-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p7_v36_v38_review.json"

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
        tile(V38, "v38 promoted p7 candidate", "Best compact tank read: broad blunt head, low armor rows, four feet, and one attached club."),
        tile(PREVIOUS, "previous v34 first", "Strong previous candidate, but the tail/body read is longer than v38."),
        tile(V37, "v37 compact review hold", "Good compact armored body and club; framing is tighter and head reads slightly heavier."),
        tile(V36, "v36 long-tail hold", "Useful armor and club, but the tail/body proportion remains longer."),
        tile(V32, "previous v32 hold", "Older first image; still useful, but cheek knob and long-tail risk are stronger."),
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
        ("v38 promoted p7", V38),
        ("previous v34", PREVIOUS),
        ("v37 compact hold", V37),
        ("v36 long-tail hold", V36),
        ("previous v32", V32),
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
                "experiment": "p7_v36_v38_compact_tank_tailclub_candidates",
                "previousPrimary": relative(PREVIOUS),
                "selectedPrimary": relative(V38),
                "selectedReviewHolds": [relative(V37), relative(V36), relative(V32)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v38_to_count_level_pass",
                "reason": (
                    "V38 gives the best current compact Ankylosaurus read because the body is shorter and more tank-like than v34, "
                    "the skull stays broad and blunt, low rounded osteoderm rows remain clear, four sturdy feet are reviewable, "
                    "and the short thick tail ends in one attached oval club. V37 is a useful compact hold but is more tightly framed, "
                    "while v36 keeps more long-tail/body risk."
                ),
                "remainingRisks": [
                    "exact skull proportions and side armor layout still need reference review",
                    "toe details are count-level rather than final",
                    "tail club shape and attachment need final close crop review",
                ],
                "rejectIfPromoting": [
                    "body reads as crocodile, monitor lizard, pangolin, turtle, armadillo, rhinoceros, or fantasy armored reptile",
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
    required = [PREVIOUS, V32, V36, V37, V38, GUIDE]
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
