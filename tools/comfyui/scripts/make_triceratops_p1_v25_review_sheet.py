import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V23 = ASSETS / "triceratops-horridus-toe-claw-matte-i2i-v23.png"
V24_REJECT = ASSETS / "triceratops-horridus-antirhino-lowdenoise-reject-v24.png"
V25 = ASSETS / "triceratops-horridus-imagegen-v25-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p1-v25-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p1-v25-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p1_v25_review.json"

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
        tile(CURRENT, "current v22 count-level pass", "Best current anti-rhino body with long tail and three-horn/frill read, still not final."),
        tile(V25, "v25 imagegen source candidate", "Fresh source candidate with good frill/tail/feet visibility; hold because beak appears open."),
        tile(V23, "v23 toe matte comparison", "Toe-claw matte route; useful for foot comparison but not a full representative upgrade."),
        tile(V24_REJECT, "v24 anti-rhino rejection", "Low-denoise attempt kept body but did not improve the beak/toe gates enough."),
        tile(GUIDE, "skull/frill body-lock guide", "Project-owned control target for skull-attached frill, closed beak, long tail, and non-hoofed toes."),
        tile(CURRENT_CROPS, "v21/v22 crop gate", "Existing close-review gate for feet, head, frill, beak, body, and tail."),
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
        ("current v22", CURRENT),
        ("v23 toe matte", V23),
        ("v24 reject", V24_REJECT),
        ("v25 source candidate", V25),
        ("body-lock guide", GUIDE),
        ("v22 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("head/frill/beak", (0.00, 0.10, 0.38, 0.62), (360, 210)),
        ("frill attachment", (0.15, 0.06, 0.44, 0.55), (300, 210)),
        ("front feet", (0.20, 0.58, 0.47, 0.93), (300, 210)),
        ("rear feet/tail base", (0.52, 0.48, 0.92, 0.92), (360, 210)),
        ("tail", (0.62, 0.28, 1.0, 0.68), (360, 210)),
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
                "taxonId": "triceratops-horridus",
                "experiment": "p1_v25_source_candidate",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V25),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V25 improves full-body visibility, tail length, frill attachment, and foot review compared with many older "
                    "prompt attempts, but the beak/mouth reads partly open and the heavy body still carries mild rhino risk. "
                    "Keep v22 first and use v25 only as a source/reference candidate."
                ),
                "rejectIfPromoting": [
                    "mouth or beak reads open",
                    "body reads as rhinoceros or mammal torso",
                    "feet collapse into hooves",
                    "frill appears shoulder-attached instead of skull-attached"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V23, V24_REJECT, V25, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
