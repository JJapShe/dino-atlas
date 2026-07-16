import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "theropod_tyrannosaurus" / "review"

CURRENT = ASSETS / "tyrannosaurus-rex-twofinger-hand-i2i-v4.png"
V16 = ASSETS / "tyrannosaurus-rex-imagegen-v16-source-candidate.png"
V17 = ASSETS / "tyrannosaurus-rex-imagegen-v17-source-candidate.png"
V18 = ASSETS / "tyrannosaurus-rex-imagegen-v18-source-candidate.png"
V15 = ASSETS / "tyrannosaurus-rex-imagegen-v15-source-candidate.png"
GUIDE = ASSETS / "tyrannosaurus-rex-twofinger-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "tyrannosaurus-p3-v16-v18-review-sheet.png"
CROP_SHEET = ASSETS / "tyrannosaurus-p3-v16-v18-crops.png"
REVIEW_JSON = REVIEW_ROOT / "tyrannosaurus_p3_v16_v18_review.json"

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
        tile(CURRENT, "current v4 count-level pass", "Still safest: compact tiny arms, massive body, full tail, dry feet, but hand detail remains small."),
        tile(V18, "v18 best P3 tiny-arm hold", "Best new balance: very small T. rex arms and stable body, but hand digits remain crop-soft."),
        tile(V16, "v16 secondary P3 hold", "Good body, tail, legs, and tiny arm scale; hand reads two-pronged but overlaps shadow."),
        tile(V17, "v17 three-prong/arm risk", "Useful reject gate: polished T. rex body, but hand can read three-pronged and arm scale creeps larger."),
        tile(V15, "previous v15 tucked-hand hold", "P2 hold for comparison: tiny tucked arm scale, softer hand count than needed for promotion."),
        tile(GUIDE, "two-finger body-lock guide", "Project-owned control target for tiny chest arms, exactly two fingers, two hind legs, and heavy tail."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v4", CURRENT),
        ("v18 best P3 hold", V18),
        ("v16 secondary hold", V16),
        ("v17 reject risk", V17),
        ("previous v15 hold", V15),
        ("body-lock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.92), (430, 210)),
        ("skull/brow", (0.00, 0.08, 0.30, 0.50), (350, 210)),
        ("chest/arms", (0.15, 0.26, 0.46, 0.70), (350, 210)),
        ("hand digits", (0.18, 0.36, 0.38, 0.72), (320, 210)),
        ("hind feet", (0.34, 0.58, 0.76, 0.96), (380, 210)),
        ("tail/body balance", (0.45, 0.20, 1.00, 0.64), (400, 210)),
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
                "taxonId": "tyrannosaurus-rex",
                "experiment": "p3_v16_v18_tiny_arm_twofinger_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V18),
                "comparisonReviewHolds": [relative(V16), relative(V15)],
                "selectedRejectReferences": [relative(V17)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v4",
                "reason": (
                    "V18 is the best P3 prompt-only source hold because it keeps the tiny tucked T. rex arm scale, massive body, two hind legs, and long tail. "
                    "It still does not replace v4 because the exact two-finger hand cue remains too small and crop-soft. "
                    "V16 is a secondary hold with a useful body and tiny arms, but the hand overlaps shadow. "
                    "V17 is rejected as a positive seed because the hand can read three-pronged and the arm scale creeps larger."
                ),
                "nextRoute": (
                    "Use v18 or v16 only as copyright-safe source holds for localized low-denoise hand i2i or ControlNet. "
                    "Keep v17 as a negative gate for three-prong and allosaur-arm drift."
                ),
                "rejectIfPromoting": [
                    "forelimbs become medium-length or allosaur-like",
                    "visible hand shows a third finger, extra nub, or long dangling claws",
                    "hands are hidden enough to block two-finger review",
                    "feet, tail, or hind-leg count are cropped or hidden",
                    "brow develops horn-like spikes or fantasy-monster knobs",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V16, V17, V18, V15, GUIDE]
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
