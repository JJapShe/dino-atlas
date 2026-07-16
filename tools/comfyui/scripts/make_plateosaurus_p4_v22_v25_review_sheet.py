import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

CURRENT = ASSETS / "plateosaurus-engelhardti-imagegen-v20-source-candidate.png"
V22 = ASSETS / "plateosaurus-engelhardti-imagegen-v22-source-candidate.png"
V23 = ASSETS / "plateosaurus-engelhardti-imagegen-v23-source-candidate.png"
V24 = ASSETS / "plateosaurus-engelhardti-imagegen-v24-source-candidate.png"
V25 = ASSETS / "plateosaurus-engelhardti-imagegen-v25-source-candidate.png"
PREVIOUS = ASSETS / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
GUIDE = ASSETS / "plateosaurus-engelhardti-bodylock-guide-v1.png"
SIXLEG_REJECT = ASSETS / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

REVIEW_SHEET = ASSETS / "plateosaurus-p4-v22-v25-review-sheet.png"
CROP_SHEET = ASSETS / "plateosaurus-p4-v22-v25-crops.png"
REVIEW_JSON = REVIEW_ROOT / "plateosaurus_p4_v22_v25_review.json"

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


def tile(path, title, note, size=(430, 242), accent=(132, 61, 43)):
    panel = Image.new("RGB", (size[0], size[1] + 94), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, size[1], size[0], size[1] + 6), fill=accent)
    draw.text((8, size[1] + 12), title[:70], fill=accent, font=FONT)
    draw_wrapped(draw, (8, size[1] + 35), note)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v20: anatomy-first seed", "Good two lifted forelimbs and no-six-leg body, but color remains sandy/tan.", accent=(95, 98, 112)),
        tile(V25, "v25 selected: dark speckled color pass", "Best P4 balance: distinct charcoal-green speckles, compact lifted hands, and two grounded hind legs.", accent=(38, 116, 76)),
        tile(V23, "v23 color hold: red-clay dorsal", "Strong red-clay color separation, but hand/finger length remains hook-risk.", accent=(146, 99, 45)),
        tile(V22, "v22 color hold: olive mottled", "Useful olive/cream mottling, but hands are still long and hooked.", accent=(146, 99, 45)),
        tile(V24, "v24 reject: hook-hand and leg overlap", "Distinct slate/ochre bands, but hands lengthen and hind-leg overlap is less safe.", accent=(150, 61, 48)),
        tile(PREVIOUS, "previous v3 hold", "Older no-six-leg comparison with weaker far forelimb visibility and plainer color.", accent=(95, 98, 112)),
        tile(GUIDE, "bodylock guide", "Target: two grounded hind legs, two lifted compact hands, no forelimb ground contact.", accent=(68, 92, 140)),
        tile(SIXLEG_REJECT, "six-leg rejection gate", "Failure reference: any extra limb or ground-contact forelimb blocks promotion.", accent=(150, 61, 48)),
    ]
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    REVIEW_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v20", CURRENT),
        ("selected v25", V25),
        ("v23 color hold", V23),
        ("v22 color hold", V22),
        ("v24 reject", V24),
        ("previous v3", PREVIOUS),
        ("bodylock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.06, 1.00, 0.93), (430, 210)),
        ("head/low neck", (0.00, 0.08, 0.34, 0.56), (360, 210)),
        ("forelimbs/hands", (0.12, 0.32, 0.45, 0.72), (340, 210)),
        ("thumb-claw cue", (0.17, 0.37, 0.36, 0.70), (300, 210)),
        ("hind legs/feet", (0.33, 0.48, 0.70, 0.96), (360, 210)),
        ("tail and bands", (0.50, 0.25, 1.00, 0.63), (380, 210)),
        ("color/pattern", (0.18, 0.18, 0.78, 0.58), (390, 210)),
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
                "experiment": "p4_v22_v25_color_pattern_no_six_leg_candidates",
                "previousPrimary": relative(CURRENT),
                "selectedCandidate": relative(V25),
                "colorReviewHolds": [relative(V23), relative(V22)],
                "rejectReferences": [relative(V24)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v25_for_color_separation_with_no_six_leg_gate_pending_human_review",
                "reason": (
                    "V25 is the best P4 color-pattern balance: it separates Plateosaurus from the sandy/tan gallery with charcoal green-gray skin, cream speckles, and darker tail bands while preserving two grounded hind legs and short lifted forelimbs. "
                    "V23 has the strongest red-clay color variation but keeps longer hook-risk fingers; v22 is useful olive/cream color evidence but also keeps long hands; v24 is rejected because hand length and hind-leg overlap are less safe."
                ),
                "nextRoute": (
                    "Use v25 as the current color-separated smoke-test seed. Future localized hand i2i should preserve the dark speckled color, two grounded hind legs, full tail, and lifted forelimbs while shortening the fingers and clarifying the larger thumb-claw cue."
                ),
                "rejectIfPromoting": [
                    "forelimbs touch the ground or read as weight-bearing front legs",
                    "overlapping arms create a six-leg or extra-limb read",
                    "hands become long dangling theropod hooks",
                    "color collapses back to plain sandy tan",
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
    required = [CURRENT, V22, V23, V24, V25, PREVIOUS, GUIDE, SIXLEG_REJECT]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
