import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "small_theropod_coelophysis" / "review"

CURRENT = ASSETS / "coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png"
V5 = ASSETS / "coelophysis-bauri-imagegen-v5-source-candidate.png"
V6 = ASSETS / "coelophysis-bauri-imagegen-v6-source-candidate.png"
V7 = ASSETS / "coelophysis-bauri-imagegen-v7-source-candidate.png"
V8 = ASSETS / "coelophysis-bauri-imagegen-v8-source-candidate.png"
GUIDE = ASSETS / "coelophysis-bauri-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "coelophysis-p2-v6-v8-review-sheet.png"
CROP_SHEET = ASSETS / "coelophysis-p2-v6-v8-crops.png"
REVIEW_JSON = REVIEW_ROOT / "coelophysis_p2_v6_v8_review.json"

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
        tile(CURRENT, "current v3 count-level pass", "Safest current source: very gracile S-neck, full tail, two hind legs, subtle tucked forelimbs."),
        tile(V5, "v5 visible-forelimb hold", "Clearer forelimbs than v3, but head and torso read a little heavier."),
        tile(V6, "v6 gracile p2 hold", "Best new silhouette: slim body and S-neck; hands are visible but can lengthen slightly."),
        tile(V7, "v7 heavy-hand reject", "Forelimbs become too long/hook-like and the body reads heavier."),
        tile(V8, "v8 no-extra-leg hold", "Clean two-leg/no-extra-leg read; hand and toe detail still soft."),
        tile(GUIDE, "body-lock guide", "Project-owned target for slim body, S-neck, full tail, two hind legs, and off-ground forelimbs."),
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
        ("v5 previous hold", V5),
        ("v6 gracile hold", V6),
        ("v7 heavy-hand reject", V7),
        ("v8 no-extra-leg hold", V8),
    ]
    crops = [
        ("full body", (0.00, 0.06, 1.00, 0.92), (430, 210)),
        ("head/S-neck", (0.00, 0.08, 0.34, 0.64), (360, 210)),
        ("forelimb/hand", (0.17, 0.35, 0.42, 0.74), (320, 210)),
        ("hand digits", (0.20, 0.40, 0.35, 0.72), (280, 210)),
        ("hind legs/feet", (0.32, 0.52, 0.72, 0.95), (360, 210)),
        ("tail", (0.48, 0.25, 1.00, 0.62), (380, 210)),
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
                "taxonId": "coelophysis-bauri",
                "experiment": "p2_v6_v8_no_extra_leg_candidates",
                "currentPrimary": relative(CURRENT),
                "candidateDecisions": [
                    {
                        "source": relative(V6),
                        "decision": "review_hold",
                        "reason": "Best new P2 silhouette: slim Coelophysis body, S-curved neck, full tail, two grounded hind legs, and visible tucked forelimbs; keep below v3 because hand digits can still lengthen.",
                    },
                    {
                        "source": relative(V7),
                        "decision": "reject_reference",
                        "reason": "Body/head read heavier and forelimb hands become longer and more hook-like, increasing extra-limb and generic theropod drift risk.",
                    },
                    {
                        "source": relative(V8),
                        "decision": "review_hold",
                        "reason": "Clean two-hind-leg/no-extra-leg read with full tail and small off-ground forelimbs; keep below v3 because hand and toe details remain soft.",
                    },
                ],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_primary",
                "reason": (
                    "V6 and v8 add useful project-owned review holds, but neither proves cleaner hand/toe anatomy than the current v3 primary. "
                    "V7 is a strict reject reference for heavier body and long hook-hand drift."
                ),
                "rejectIfPromoting": [
                    "forelimbs touch the ground or read as extra legs",
                    "body becomes bulky raptor, Allosaurus, Tyrannosaurus, lizard, or sauropodomorph-like",
                    "head becomes bird-beaked or feathered",
                    "hands become oversized or long dangling hooks",
                    "feet, small hands, or tail are hidden enough to block count review",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V5, V6, V7, V8, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
