import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "small_theropod_coelophysis" / "review"

CURRENT = ASSETS / "coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png"
CURRENT_CROPS = ASSETS / "coelophysis-slenderneck-smallhands-crops-v3.png"
OPENFEET = ASSETS / "coelophysis-bauri-slenderneck-openfeet-imagegen-v3.png"
V5 = ASSETS / "coelophysis-bauri-imagegen-v5-source-candidate.png"
GUIDE = ASSETS / "coelophysis-bauri-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSETS / "coelophysis-bodylock-crops-v4.png"

REVIEW_SHEET = ASSETS / "coelophysis-p1-v5-review-sheet.png"
CROP_SHEET = ASSETS / "coelophysis-p1-v5-crops.png"
REVIEW_JSON = REVIEW_ROOT / "coelophysis_p1_v5_review.json"

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
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v3 count-level pass", "Best current slender-neck candidate; very gracile, but forelimbs are subtle at app scale."),
        tile(V5, "v5 visible-forelimb source hold", "Fresh candidate with clearer tucked forelimbs and stable two-leg read, but body/head are a little heavier."),
        tile(OPENFEET, "v3 open-feet comparison", "Useful dry-ground comparison; hand and rear-foot reads stay below the selected v3."),
        tile(GUIDE, "body-lock guide", "Project-owned control target for S-neck, slim body, full tail, two hind legs, and small off-ground forelimbs."),
        tile(CURRENT_CROPS, "v3 crop gate", "Baseline close-review sheet for head, S-neck, small hands, legs, feet, and tail."),
        tile(BODYLOCK_CROPS, "body-lock crop gate", "Guide-versus-current gate for forelimbs-not-legs and hind-leg count."),
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
        ("v5 source hold", V5),
        ("open-feet v3", OPENFEET),
        ("body-lock guide", GUIDE),
        ("v3 existing crop gate", CURRENT_CROPS),
        ("body-lock existing crop gate", BODYLOCK_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.06, 1.00, 0.92), (430, 210)),
        ("head/S-neck", (0.00, 0.08, 0.32, 0.62), (360, 210)),
        ("forelimb/hand", (0.18, 0.37, 0.41, 0.73), (320, 210)),
        ("hand digits", (0.21, 0.42, 0.34, 0.70), (280, 210)),
        ("hind legs/feet", (0.32, 0.55, 0.71, 0.94), (360, 210)),
        ("tail", (0.48, 0.27, 1.00, 0.62), (380, 210)),
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
                "taxonId": "coelophysis-bauri",
                "experiment": "p1_v5_source_candidate",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V5),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V5 improves visible small forelimbs while keeping them off the ground, with two hind legs, dry feet, an S-curved neck, "
                    "and a full tail. Keep v3 first because v5 reads slightly heavier in the head/body and exact hand/toe anatomy still needs "
                    "close review."
                ),
                "rejectIfPromoting": [
                    "forelimbs touch the ground or read as extra legs",
                    "body becomes bulky raptor, Allosaurus, Tyrannosaurus, lizard, or sauropodomorph-like",
                    "head becomes bird-beaked or feathered",
                    "feet, small hands, or tail are hidden enough to block count review",
                    "scene becomes perched on a branch, log, or wet reed bank"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, OPENFEET, V5, GUIDE, BODYLOCK_CROPS]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
