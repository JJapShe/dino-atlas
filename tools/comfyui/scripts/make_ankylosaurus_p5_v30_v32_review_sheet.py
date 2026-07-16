import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
V28 = ASSETS / "ankylosaurus-magniventris-imagegen-v28-source-candidate.png"
V30 = ASSETS / "ankylosaurus-magniventris-imagegen-v30-source-candidate.png"
V31 = ASSETS / "ankylosaurus-magniventris-imagegen-v31-source-candidate.png"
V32 = ASSETS / "ankylosaurus-magniventris-imagegen-v32-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p5-v30-v32-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p5-v30-v32-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p5_v30_v32_review.json"

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
        tile(CURRENT, "current v18 app first", "Still first: attached club and visible feet, but broad-skull identity remains count-level."),
        tile(V28, "v28 previous best hold", "Prior P4 hold; good armor/club balance, but head knobs and tail length remain risky."),
        tile(V30, "v30 compact armor hold", "Good rounded armor and single club, but head still reads lizard-like at close crop."),
        tile(V31, "v31 horn-risk hold", "Strong tank body and attached club, but the cheek knob can read like a horn."),
        tile(V32, "v32 best p5 review hold", "Best fresh low-body and armor read; still watch cheek knob and tail length."),
        tile(GUIDE, "armor tail-club guide", "Control target: broad skull, very short neck, low osteoderms, four sturdy feet, one attached club."),
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
        ("v28 prior hold", V28),
        ("v30 compact hold", V30),
        ("v31 horn-risk hold", V31),
        ("v32 best p5 hold", V32),
        ("armor tail-club guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("skull/snout", (0.00, 0.18, 0.34, 0.64), (360, 210)),
        ("armor rows", (0.16, 0.10, 0.74, 0.58), (390, 210)),
        ("feet/legs", (0.08, 0.56, 0.78, 0.96), (390, 210)),
        ("tail club", (0.60, 0.24, 1.0, 0.72), (390, 210)),
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
                "experiment": "p5_v30_v32_compact_tank_tailclub_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V32),
                "secondaryReviewHolds": [relative(V30), relative(V31)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v18_with_v32_review_hold",
                "reason": (
                    "V32 is the strongest fresh candidate because it improves the low tank-like body, rounded osteoderm rows, planted feet, "
                    "and one attached oval club while avoiding the longest-body drift from earlier prompt-only candidates. It stays review_hold "
                    "because the cheek knob can still read horn-like and the tail remains longer than ideal for a compact ankylosaurid. "
                    "V30 and V31 are useful comparison holds but retain lizard-head or horn-risk reads."
                ),
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
    required = [CURRENT, V28, V30, V31, V32, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
