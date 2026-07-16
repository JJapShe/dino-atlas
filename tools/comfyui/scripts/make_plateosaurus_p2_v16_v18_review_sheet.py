import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

CURRENT = ASSETS / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
CURRENT_CROPS = ASSETS / "plateosaurus-singleforelimb-smallhand-crops-v3.png"
V15 = ASSETS / "plateosaurus-engelhardti-imagegen-v15-source-candidate.png"
V16 = ASSETS / "plateosaurus-engelhardti-imagegen-v16-source-candidate.png"
V17 = ASSETS / "plateosaurus-engelhardti-imagegen-v17-source-candidate.png"
V18 = ASSETS / "plateosaurus-engelhardti-imagegen-v18-source-candidate.png"
SIXLEG_REJECT = ASSETS / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

REVIEW_SHEET = ASSETS / "plateosaurus-p2-v16-v18-review-sheet.png"
CROP_SHEET = ASSETS / "plateosaurus-p2-v16-v18-crops.png"
REVIEW_JSON = REVIEW_ROOT / "plateosaurus_p2_v16_v18_review.json"

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
        tile(CURRENT, "current v3 app-first seed", "Still safest count-level source: low head, full tail, two grounded hind legs, one lifted forelimb."),
        tile(V15, "v15 previous review hold", "Good body gate but soft hands; retained as a comparison under v3."),
        tile(V16, "v16 best p2 review hold", "Strong side silhouette and visible lifted hands; thumb claws read, but hooks may be overlong."),
        tile(V17, "v17 hand-overbuild reject", "Hands are visible but too human-like and over-digited for a positive Plateosaurus seed."),
        tile(V18, "v18 silhouette review hold", "Clean two-hind-leg stance and full tail, but neck is long and hand/thumb-claw detail is soft."),
        tile(SIXLEG_REJECT, "six-leg rejection gate", "Failure reference: do not promote any output with extra limb or forelimb-ground-contact read."),
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
        ("v15 previous hold", V15),
        ("v16 best p2 hold", V16),
        ("v17 hand reject", V17),
        ("v18 silhouette hold", V18),
    ]
    crops = [
        ("full body", (0.00, 0.07, 1.00, 0.92), (430, 210)),
        ("head/low neck", (0.00, 0.12, 0.34, 0.56), (360, 210)),
        ("forelimb/hand", (0.16, 0.36, 0.42, 0.72), (320, 210)),
        ("thumb-claw cue", (0.20, 0.42, 0.36, 0.70), (280, 210)),
        ("hind legs/feet", (0.33, 0.48, 0.68, 0.94), (360, 210)),
        ("tail", (0.50, 0.25, 1.00, 0.60), (380, 210)),
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
                "taxonId": "plateosaurus-engelhardti",
                "experiment": "p2_v16_v18_hand_visibility_candidates",
                "currentPrimary": relative(CURRENT),
                "candidateDecisions": [
                    {
                        "source": relative(V16),
                        "decision": "review_hold",
                        "reason": "Best P2 candidate: strong full-body Plateosaurus read, exactly two grounded hind legs, lifted forelimbs, and visible thumb-claw cue; keep below v3 because the claws may be overlong and hook-like.",
                    },
                    {
                        "source": relative(V17),
                        "decision": "reject_reference",
                        "reason": "Hands are visible but too human-like, over-digited, and overbuilt; useful only as a failure reference for hand exaggeration.",
                    },
                    {
                        "source": relative(V18),
                        "decision": "review_hold",
                        "reason": "Clean two-hind-leg silhouette and full tail, but the neck trends too long and hand/thumb-claw anatomy remains too soft for promotion.",
                    },
                ],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_primary",
                "reason": (
                    "P2 improves visible lifted hands compared with v3/v15, especially in v16, but none proves better small five-finger/thumb-claw anatomy without new risks. "
                    "Keep v3 first and use v16/v18 as review holds, with v17 as a strict hand-overbuild reject reference."
                ),
                "rejectIfPromoting": [
                    "forelimbs touch the ground or read as weight-bearing front legs",
                    "overlapping arms create a six-leg or extra-limb read",
                    "hands become human-like, over-digited, or giant theropod hook claws",
                    "head becomes predator-like, toothy, sauropod-like, or generic lizard-like",
                    "tail, feet, hands, or ground contact are hidden enough to block count review",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V15, V16, V17, V18, SIXLEG_REJECT]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
