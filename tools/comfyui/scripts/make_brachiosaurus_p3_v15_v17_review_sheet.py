import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "sauropod_brachiosaurus" / "review"

CURRENT = ASSETS / "brachiosaurus-altithorax-tail-reduced-i2i-v4.png"
V13 = ASSETS / "brachiosaurus-altithorax-imagegen-v13-source-candidate.png"
V15 = ASSETS / "brachiosaurus-altithorax-imagegen-v15-source-candidate.png"
V16 = ASSETS / "brachiosaurus-altithorax-imagegen-v16-source-candidate.png"
V17 = ASSETS / "brachiosaurus-altithorax-imagegen-v17-source-candidate.png"
GUIDE = ASSETS / "brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "brachiosaurus-p3-v15-v17-review-sheet.png"
CROP_SHEET = ASSETS / "brachiosaurus-p3-v15-v17-crops.png"
REVIEW_JSON = REVIEW_ROOT / "brachiosaurus_p3_v15_v17_review.json"

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
        tile(V16, "v16 promoted p3 candidate", "Best p3 result: high shoulders, taller forelimbs, four feet, and the shortest robust tail."),
        tile(CURRENT, "previous v4 first", "Still useful as a tail-reduced i2i comparison, but tail is longer and thinner than v16."),
        tile(V15, "v15 long-tail hold", "Good body plan, but the tail remains too long for replacing the current candidate."),
        tile(V17, "v17 secondary hold", "Clear high-shoulder body and shorter tail than old p2, but not as compact as v16."),
        tile(V13, "v13 prior p2 hold", "Strong shoulder and foot read with recurring long thin tail risk."),
        tile(GUIDE, "body-lock guide", "Project-owned target for high shoulders, taller forelimbs, rising neck, and short thick tail."),
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
        ("v16 promoted p3", V16),
        ("previous v4", CURRENT),
        ("v15 long-tail hold", V15),
        ("v17 secondary hold", V17),
        ("v13 prior p2 hold", V13),
        ("body-lock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.92), (430, 210)),
        ("head/neck", (0.00, 0.02, 0.34, 0.52), (360, 210)),
        ("shoulder slope", (0.18, 0.18, 0.60, 0.68), (360, 210)),
        ("forelimb feet", (0.16, 0.50, 0.42, 0.95), (320, 210)),
        ("hind feet", (0.42, 0.50, 0.70, 0.95), (320, 210)),
        ("tail", (0.52, 0.28, 1.00, 0.70), (380, 210)),
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
                "taxonId": "brachiosaurus-altithorax",
                "experiment": "p3_v15_v17_short_tail_prompt_candidates",
                "previousPrimary": relative(CURRENT),
                "selectedPrimary": relative(V16),
                "selectedReviewHolds": [relative(V17), relative(V15), relative(V13)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v16",
                "reason": (
                    "V16 is the first prompt-only Brachiosaurus candidate in this route to combine the high shoulder, taller forelimbs, rising neck, four visible pillar feet, "
                    "and a visibly short thick tapering tail. V4 remains a useful i2i comparison, but v16 better solves the repeated diplodocid whip-tail failure. "
                    "V15 and v17 stay as review holds because their body plans are useful, but their tails read longer or less compact than v16."
                ),
                "rejectIfPromoting": [
                    "tail becomes a long thin diplodocid whip or is cropped",
                    "forelimbs and hind limbs become equal height or shoulder drops near hip line",
                    "neck becomes low and horizontal like Apatosaurus/Diplodocus",
                    "feet are hidden, fused, hoof-like, or unclear enough to block four-leg review",
                    "head becomes crocodile-like, toothed, predator-like, or too large",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V13, V15, V16, V17, GUIDE]
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
