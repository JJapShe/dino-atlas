import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

CURRENT = ASSETS / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
CURRENT_CROPS = ASSETS / "plateosaurus-singleforelimb-smallhand-crops-v3.png"
V14 = ASSETS / "plateosaurus-engelhardti-thumbtip-micro-i2i-comparison-v14.png"
V15 = ASSETS / "plateosaurus-engelhardti-imagegen-v15-source-candidate.png"
GUIDE = ASSETS / "plateosaurus-engelhardti-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSETS / "plateosaurus-bodylock-crops-v4.png"
SIXLEG_REJECT = ASSETS / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

REVIEW_SHEET = ASSETS / "plateosaurus-p1-v15-review-sheet.png"
CROP_SHEET = ASSETS / "plateosaurus-p1-v15-crops.png"
REVIEW_JSON = REVIEW_ROOT / "plateosaurus_p1_v15_review.json"

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
        tile(CURRENT, "current v3 count-level train seed", "Best current app-first source: two grounded hind legs and lifted near forelimb, but far arm is hidden."),
        tile(V15, "v15 new imagegen review hold", "Fresh prompt-only candidate with stable bipedal body and visible short arms; hand/thumb-claw remains soft."),
        tile(V14, "v14 thumb-tip micro i2i hold", "Safest local hand-tip edit route so far, but too subtle to prove better finger anatomy."),
        tile(GUIDE, "body-lock guide", "Project-owned target for low head, long neck, full tail, lifted hands, and exactly two grounded hind legs."),
        tile(CURRENT_CROPS, "v3 crop gate", "Baseline close-review sheet for head, forelimb, small hand cue, hind legs, feet, and tail."),
        tile(SIXLEG_REJECT, "six-leg rejection reference", "Keep visible as a failure gate: overlapping forelimb edits must not become extra legs."),
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
        ("current v3", CURRENT),
        ("v15 source hold", V15),
        ("v14 micro i2i", V14),
        ("body-lock guide", GUIDE),
        ("v3 existing crop gate", CURRENT_CROPS),
        ("body-lock existing crop gate", BODYLOCK_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.08, 1.00, 0.92), (430, 210)),
        ("head/low neck", (0.00, 0.12, 0.34, 0.55), (360, 210)),
        ("forelimb/hand", (0.17, 0.38, 0.40, 0.72), (320, 210)),
        ("thumb-claw cue", (0.20, 0.43, 0.34, 0.69), (280, 210)),
        ("hind legs/feet", (0.33, 0.50, 0.68, 0.94), (360, 210)),
        ("tail", (0.50, 0.27, 1.00, 0.60), (380, 210)),
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
                "taxonId": "plateosaurus-engelhardti",
                "experiment": "p1_v15_source_candidate",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V15),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V15 preserves the useful low herbivore head, long forward neck, full tail, and exactly two large grounded hind legs. "
                    "Keep v3 first because v15 still does not prove the far forelimb or exact five-finger/thumb-claw hand anatomy, and the hands remain too soft for final Plateosaurus approval."
                ),
                "rejectIfPromoting": [
                    "forelimbs touch the ground or read as weight-bearing front legs",
                    "overlapping arms create a six-leg or extra-limb read",
                    "hands become giant theropod hook claws instead of small grasping hands",
                    "head becomes predator-like, toothy, sauropod-like, or generic lizard-like",
                    "tail, feet, hands, or ground contact are hidden enough to block count review"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V14, V15, GUIDE, BODYLOCK_CROPS, SIXLEG_REJECT]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
