import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
CURRENT_CROPS = ASSETS / "ankylosaurus-allfeet-lora-i2i-v17-v18-crops.png"
V14 = ASSETS / "ankylosaurus-magniventris-broadskull-i2i-v14.png"
V19_REJECT = ASSETS / "ankylosaurus-magniventris-bodylock-osteoderm-lowdenoise-reject-v19.png"
V20 = ASSETS / "ankylosaurus-magniventris-imagegen-v20-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p1-v20-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p1-v20-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p1_v20_review.json"

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
        tile(CURRENT, "current v18 count-level pass", "Best current app candidate; four legs and attached club pass, skull/body still needs review."),
        tile(V20, "v20 imagegen source candidate", "Fresh project-owned candidate; clearer foot contact and club, hold for skull breadth and lizard-drift review."),
        tile(V14, "previous v14 body/head gate", "Earlier body-head gate useful for checking whether v20 improves feet without losing body identity."),
        tile(V19_REJECT, "v19 low-denoise rejection", "Reject anchor: whole-body i2i can keep the club but lengthen the lizard-like body."),
        tile(GUIDE, "armor/tail-club guide", "Project-owned structure target for broad skull, low body, armor rows, four feet, and one club."),
        tile(CURRENT_CROPS, "v17/v18 crop gate", "Existing close-review gate for skull, armor rows, feet, and attached tail club."),
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
        ("current v18", CURRENT),
        ("v20 source candidate", V20),
        ("v14 body/head gate", V14),
        ("v19 reject", V19_REJECT),
        ("armor/tail guide", GUIDE),
        ("v18 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.08, 1.00, 0.92), (430, 210)),
        ("skull/snout", (0.00, 0.18, 0.30, 0.58), (360, 210)),
        ("armor rows", (0.24, 0.12, 0.67, 0.58), (360, 210)),
        ("feet strip", (0.16, 0.54, 0.66, 0.92), (430, 210)),
        ("rear legs/hips", (0.48, 0.48, 0.78, 0.90), (330, 210)),
        ("tail club", (0.68, 0.23, 1.00, 0.62), (360, 210)),
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
        if path == CURRENT_CROPS:
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
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "p1_v20_source_candidate",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V20),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V20 is a project-owned source candidate with exactly four visible legs, planted feet, dense low rounded armor rows, "
                    "a thick tail, and one attached oval tail club. Keep it as review_hold rather than a positive seed because the skull "
                    "and body can still read slightly long or generic-reptile-like at close review."
                ),
                "rejectIfPromoting": [
                    "skull reads as a long monitor-lizard or crocodile snout",
                    "body reads as generic lizard, pangolin, turtle, armadillo, or fantasy reptile",
                    "tail club is detached, doubled, or replaced by spikes",
                    "feet are hidden, hoof-like, or create extra-limb ambiguity",
                    "armor becomes tall Stegosaurus-like plates instead of low rounded osteoderms"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V14, V19_REJECT, V20, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
