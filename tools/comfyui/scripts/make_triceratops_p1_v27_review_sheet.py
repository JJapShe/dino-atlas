import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V25 = ASSETS / "triceratops-horridus-imagegen-v25-source-candidate.png"
V26 = ASSETS / "triceratops-horridus-imagegen-v26-source-candidate.png"
V27 = ASSETS / "triceratops-horridus-imagegen-v27-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p1-v27-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p1-v27-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p1_v27_review.json"

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
        tile(CURRENT, "current v22 count-level pass", "Current app first candidate: good horn/frill/tail/feet gate, still needs manual toe/body review."),
        tile(V27, "v27 closed-beak source hold", "Best new prompt-only beak closure, but round torso and leg overlap prevent promotion."),
        tile(V26, "v26 open-beak comparison", "Good Triceratops identity, but black mouth gap/open beak keeps it out of positive use."),
        tile(V25, "v25 previous source hold", "Full-body visibility is useful; mouth still reads partly open and body remains heavy."),
        tile(GUIDE, "skull/frill body-lock guide", "Project-owned target for three horns, skull-attached frill, closed beak, long tail, and toes."),
        tile(CURRENT_CROPS, "v21/v22 crop gate", "Existing close-review gate for head, frill, beak, body, feet, and tail."),
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
        ("v27 closed-beak hold", V27),
        ("v26 open-beak compare", V26),
        ("v25 source hold", V25),
        ("body-lock guide", GUIDE),
        ("v22 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("head/frill/beak", (0.00, 0.10, 0.38, 0.62), (360, 210)),
        ("mouth seam", (0.00, 0.26, 0.24, 0.58), (300, 210)),
        ("front feet", (0.18, 0.58, 0.47, 0.93), (300, 210)),
        ("rear feet/tail base", (0.47, 0.48, 0.90, 0.92), (360, 210)),
        ("tail", (0.58, 0.28, 1.0, 0.68), (360, 210)),
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
                "experiment": "p1_v26_v27_closed_beak_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V27),
                "comparisonReject": relative(V26),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V27 gives the best new prompt-only closed-beak read while keeping a skull-attached frill, three facial horns, a long tail, and visible non-hoofed toes. "
                    "Keep v22 first because v27 still has a rounded heavy torso and overlapping rear-leg read. V26 is useful as an open-beak rejection comparison."
                ),
                "rejectIfPromoting": [
                    "mouth seam reads open, black, toothy, or mammal-like",
                    "body becomes a rhinoceros torso, shoulder hump, or hoofed mammal",
                    "tail shortens or is hidden",
                    "frill separates from the skull or attaches to the shoulders",
                    "feet collapse into hooves, extra limbs, or hidden toe counts"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V25, V26, V27, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
