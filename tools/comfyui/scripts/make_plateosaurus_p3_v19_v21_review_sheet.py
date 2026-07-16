import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

CURRENT = ASSETS / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
V16 = ASSETS / "plateosaurus-engelhardti-imagegen-v16-source-candidate.png"
V19 = ASSETS / "plateosaurus-engelhardti-imagegen-v19-source-candidate.png"
V20 = ASSETS / "plateosaurus-engelhardti-imagegen-v20-source-candidate.png"
V21 = ASSETS / "plateosaurus-engelhardti-imagegen-v21-source-candidate.png"
BODYLOCK_GUIDE = ASSETS / "plateosaurus-engelhardti-bodylock-guide-v1.png"
SIXLEG_REJECT = ASSETS / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

REVIEW_SHEET = ASSETS / "plateosaurus-p3-v19-v21-review-sheet.png"
CROP_SHEET = ASSETS / "plateosaurus-p3-v19-v21-crops.png"
REVIEW_JSON = REVIEW_ROOT / "plateosaurus_p3_v19_v21_review.json"

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
        tile(CURRENT, "current v3 app-first", "Safest old no-six-leg gate, but far forelimb is mostly hidden."),
        tile(V20, "v20 two-lifted-hands candidate", "Best P3 attempt: both lifted forelimbs visible and only hind legs touch ground."),
        tile(V19, "v19 hand-detail hold", "Good hand visibility, but fingers/claws trend long and hook-like."),
        tile(V21, "v21 silhouette hold", "Clean body and no-six-leg read, but far forelimb remains weak."),
        tile(V16, "previous v16 hand hold", "Older best hand-visibility hold with possible overlong hooks."),
        tile(BODYLOCK_GUIDE, "bodylock guide", "Target: two grounded hind legs, two lifted hands, no forelimb ground contact."),
        tile(SIXLEG_REJECT, "six-leg rejection gate", "Failure reference: any extra limb or ground-contact forelimb is unsafe."),
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
        ("v20 two-lifted-hands candidate", V20),
        ("v19 hand-detail hold", V19),
        ("v21 silhouette hold", V21),
        ("previous v16 hold", V16),
        ("bodylock guide", BODYLOCK_GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.07, 1.00, 0.92), (430, 210)),
        ("head/low neck", (0.00, 0.10, 0.34, 0.56), (360, 210)),
        ("both forelimbs/hands", (0.12, 0.34, 0.45, 0.72), (340, 210)),
        ("thumb-claw cue", (0.17, 0.39, 0.36, 0.70), (300, 210)),
        ("hind legs/feet", (0.33, 0.48, 0.70, 0.96), (360, 210)),
        ("tail", (0.50, 0.25, 1.00, 0.62), (380, 210)),
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
                "experiment": "p3_v19_v21_two_lifted_forelimb_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(V20),
                "comparisonReviewHolds": [relative(V19), relative(V21), relative(V16)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v20_to_count_level_pass_pending_human_review",
                "reason": (
                    "V20 is the best P3 balance because both short forelimbs are visible and lifted off the ground while only two large hind legs carry weight. "
                    "It improves the far-forelimb visibility weakness of v3 without the six-leg or forelimb-ground-contact failure. "
                    "It is not final because the hand/finger and thumb-claw shapes may still be overlong or hook-like."
                ),
                "nextRoute": (
                    "Use v20 as the next app-scale smoke-test source. Future localized hand i2i should preserve the v20 no-six-leg body while shortening the fingers and clarifying compact five-finger hands plus one larger thumb claw."
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
    required = [CURRENT, V16, V19, V20, V21, BODYLOCK_GUIDE, SIXLEG_REJECT]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
