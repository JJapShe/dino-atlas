import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

V25 = ASSETS / "plateosaurus-engelhardti-imagegen-v25-source-candidate.png"
V26 = ASSETS / "plateosaurus-engelhardti-imagegen-v26-source-candidate.png"
V27 = ASSETS / "plateosaurus-engelhardti-imagegen-v27-source-candidate.png"
V28 = ASSETS / "plateosaurus-engelhardti-imagegen-v28-source-candidate.png"
V20 = ASSETS / "plateosaurus-engelhardti-imagegen-v20-source-candidate.png"
GUIDE = ASSETS / "plateosaurus-engelhardti-bodylock-guide-v1.png"
SIXLEG_REJECT = ASSETS / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"

REVIEW_SHEET = ASSETS / "plateosaurus-p5-v26-v28-review-sheet.png"
CROP_SHEET = ASSETS / "plateosaurus-p5-v26-v28-crops.png"
REVIEW_JSON = REVIEW_ROOT / "plateosaurus_p5_v26_v28_review.json"

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
        tile(V25, "current v25 color pass", "Keep first: dark speckles, two grounded hind legs, lifted forelimbs, and safer app-scale balance.", accent=(38, 116, 76)),
        tile(V27, "v27 best P5 no-six-leg hold", "Shortest lifted hands and cleanest two-hind-leg stance, but hand/finger details are partly fused and weak.", accent=(146, 99, 45)),
        tile(V28, "v28 P5 color/silhouette hold", "Good moss-green and burgundy pattern with no forelimb contact, but hands lengthen again.", accent=(146, 99, 45)),
        tile(V26, "v26 reject: hook hands", "Useful charcoal/copper color, but forelimb fingers are too long and hooked for promotion.", accent=(150, 61, 48)),
        tile(V20, "previous anatomy-first hold", "Safer lifted-forelimb comparison, but sandy color is less distinct than v25.", accent=(95, 98, 112)),
        tile(GUIDE, "bodylock guide", "Target: exactly two grounded hind legs, two compact lifted hands, no forelimb ground contact.", accent=(68, 92, 140)),
        tile(SIXLEG_REJECT, "six-leg rejection gate", "Failure reference: extra limb or ground-contact forelimb blocks promotion.", accent=(150, 61, 48)),
    ]
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v25", V25),
        ("v27 best hold", V27),
        ("v28 color hold", V28),
        ("v26 hook reject", V26),
        ("previous v20", V20),
        ("bodylock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.06, 1.00, 0.93), (430, 210)),
        ("head/neck", (0.00, 0.08, 0.34, 0.56), (360, 210)),
        ("lifted forelimbs", (0.12, 0.30, 0.45, 0.74), (340, 210)),
        ("hand/thumb cue", (0.16, 0.35, 0.36, 0.72), (300, 210)),
        ("grounded hind legs", (0.32, 0.48, 0.70, 0.96), (360, 210)),
        ("tail bands", (0.50, 0.25, 1.00, 0.63), (380, 210)),
        ("color pattern", (0.18, 0.18, 0.78, 0.58), (390, 210)),
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
                "experiment": "p5_v26_v28_no_six_leg_color_variation",
                "currentPrimary": relative(V25),
                "selectedReviewHolds": [relative(V27), relative(V28)],
                "rejectReferences": [relative(V26)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v25_primary_add_v27_v28_as_review_holds_reject_v26",
                "reason": (
                    "P5 tests whether the Plateosaurus route can preserve the P4 color-separation gain while improving the no-six-leg and lifted-hand gates. "
                    "V27 has the safest new two-grounded-hind-leg stance and shortest lifted forelimbs, but its hands are partly fused and the thumb-claw cue is weak. "
                    "V28 adds useful moss-green and burgundy variation with no forelimb ground contact, but the hands lengthen again. "
                    "V26 is rejected because the fingers become long hook-like claws despite useful charcoal/copper color."
                ),
                "nextRoute": (
                    "Keep v25 as the app-first color pass. Use v27 only as a no-six-leg/lifted-hand review reference, then run localized hand i2i or body-lock ControlNet over v25/v27 to shorten fingers, keep forelimbs off the ground, and preserve exactly two grounded hind legs."
                ),
                "rejectIfPromoting": [
                    "forelimbs touch the ground or become weight-bearing front legs",
                    "overlapping limbs create a six-leg or hidden-third-support read",
                    "hands become long theropod hooks",
                    "thumb-claw cue is absent or replaced by oversized predator claws",
                    "color collapses back to sandy tan",
                    "head becomes predator-like, toothy, sauropod-like, or generic lizard-like",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [V25, V26, V27, V28, V20, GUIDE, SIXLEG_REJECT]
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
