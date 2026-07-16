import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "theropod_tyrannosaurus" / "review"

CURRENT = ASSETS / "tyrannosaurus-rex-twofinger-hand-i2i-v4.png"
CURRENT_CROPS = ASSETS / "tyrannosaurus-twofinger-hand-i2i-crops-v4.png"
V12 = ASSETS / "tyrannosaurus-rex-imagegen-v12-source-candidate.png"
V13 = ASSETS / "tyrannosaurus-rex-imagegen-v13-source-candidate.png"
V14 = ASSETS / "tyrannosaurus-rex-imagegen-v14-source-candidate.png"
V15 = ASSETS / "tyrannosaurus-rex-imagegen-v15-source-candidate.png"
GUIDE = ASSETS / "tyrannosaurus-rex-twofinger-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSETS / "tyrannosaurus-twofinger-bodylock-crops-v8.png"

REVIEW_SHEET = ASSETS / "tyrannosaurus-p2-v13-v15-review-sheet.png"
CROP_SHEET = ASSETS / "tyrannosaurus-p2-v13-v15-crops.png"
REVIEW_JSON = REVIEW_ROOT / "tyrannosaurus_p2_v13_v15_review.json"

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
        tile(CURRENT, "current v4 count-level pass", "Best current seed: massive T. rex body and tiny arms; hand cue is small but safer than enlarged prompt-only arms."),
        tile(V15, "v15 tucked-hand hold", "Best P2 arm-scale hold: tiny tucked arm preserved, but two-finger detail can be too soft in crop review."),
        tile(V14, "v14 visible-twofinger hold", "Most visible two-finger cue, but the forelimb and hand can become too large for T. rex."),
        tile(V13, "v13 three-prong risk", "Good overall body, but the hand can read as three-pronged or too claw-heavy."),
        tile(V12, "previous v12 visible-hand hold", "Previous hand-visible source hold; useful comparison, but arm scale drifts larger than v4."),
        tile(GUIDE, "two-finger body-lock guide", "Project-owned control target for massive skull, tiny arms, exactly two fingers, and two hind legs."),
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
        ("v15 tucked-hand hold", V15),
        ("v14 visible-twofinger hold", V14),
        ("v13 three-prong risk", V13),
        ("previous v12 hold", V12),
        ("body-lock guide", GUIDE),
        ("v4 existing crop gate", CURRENT_CROPS),
        ("body-lock existing crop gate", BODYLOCK_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.92), (430, 210)),
        ("skull/brow", (0.00, 0.08, 0.30, 0.50), (350, 210)),
        ("chest/arms", (0.15, 0.28, 0.46, 0.70), (350, 210)),
        ("hand digits", (0.18, 0.36, 0.38, 0.72), (320, 210)),
        ("hind feet", (0.34, 0.58, 0.74, 0.96), (380, 210)),
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
                "taxonId": "tyrannosaurus-rex",
                "experiment": "p2_v13_v15_tiny_twofinger_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V15),
                "comparisonReviewHolds": [relative(V14), relative(V12)],
                "selectedRejectReferences": [relative(V13)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v4",
                "reason": (
                    "V15 is the best P2 source hold because it preserves the tiny tucked forelimb scale better than v14 and v12. "
                    "It still does not replace v4 because the hand digits can be too soft for exact two-finger proof. "
                    "V14 makes the two fingers more visible but enlarges the arm/hand. V13 has a useful full-body T. rex read but the hand can look three-pronged."
                ),
                "nextRoute": (
                    "Use v15 only as a copyright-safe source hold for a localized hand i2i or ControlNet pass. "
                    "Reject any result that gains visible fingers by making the arm allosaur-like, adding a third finger, hiding the feet, or weakening the massive T. rex body."
                ),
                "rejectIfPromoting": [
                    "forelimbs become medium-length or allosaur-like",
                    "visible hand shows a third finger, extra nub, or long dangling claws",
                    "hands are hidden enough to block two-finger review",
                    "feet, tail, or hind-leg count are cropped or hidden",
                    "jaw, brow, or pose becomes fantasy monster rather than naturalistic T. rex",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V12, V13, V14, V15, GUIDE, BODYLOCK_CROPS]
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
