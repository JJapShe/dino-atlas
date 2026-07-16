import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V27 = ASSETS / "triceratops-horridus-imagegen-v27-source-candidate.png"
V28 = ASSETS / "triceratops-horridus-imagegen-v28-source-candidate.png"
V29 = ASSETS / "triceratops-horridus-imagegen-v29-source-candidate.png"
V30 = ASSETS / "triceratops-horridus-imagegen-v30-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p2-v28-v30-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p2-v28-v30-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p2_v28_v30_review.json"

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


def tile(path, title, note, size=(430, 242)):
    panel = Image.new("RGB", (size[0], size[1] + 82), (245, 243, 236))
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
        tile(CURRENT, "current v22 app first", "Best current anti-rhino app candidate: v9 body preserved with better feet, but not final training material."),
        tile(V28, "v28 antirhino source hold", "Best new project-owned prompt candidate: clear horns, skull frill, long tail, and toes; torso still rounded."),
        tile(V30, "v30 antirhino source hold", "Similar strong head/frill/tail cue; frill rim and rounded torso keep it below v22."),
        tile(V29, "v29 rhino-body rejection", "Head is useful, but body is round and shoulder-heavy enough to reinforce rhinoceros drift."),
        tile(V27, "previous v27 closed-beak hold", "Previous closed-beak source hold; useful continuity for mouth seam and body risk review."),
        tile(GUIDE, "skull-frill body-lock guide", "Control target for skull-attached frill, three horns, closed beak, long tail, and anti-rhino body."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v22", CURRENT),
        ("v28 source hold", V28),
        ("v30 source hold", V30),
        ("v29 rhino reject", V29),
        ("previous v27", V27),
        ("body-lock guide", GUIDE),
        ("v22 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("head/frill/horns", (0.00, 0.08, 0.42, 0.62), (380, 210)),
        ("frill attachment", (0.14, 0.05, 0.40, 0.50), (330, 210)),
        ("body anti-rhino", (0.26, 0.20, 0.78, 0.78), (390, 210)),
        ("feet/toes", (0.12, 0.58, 0.70, 0.96), (390, 210)),
        ("tail length", (0.58, 0.30, 1.0, 0.70), (360, 210)),
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
                "experiment": "p2_v28_v30_antirhino_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V28),
                "comparisonReviewHold": relative(V30),
                "comparisonReject": relative(V29),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V28 is the best new project-owned prompt candidate because it keeps exactly three facial horns, a skull-attached frill, a long tail, "
                    "closed beak, and visible non-hoofed toes. It still does not replace v22 because the torso is rounded and mildly rhinoceros-like. "
                    "V30 is similar but the frill rim is more decorative. V29 should be a reject reference because the body is rounder and shoulder-heavy."
                ),
                "nextRoute": (
                    "Use v28 or v30 only as source/reference holds. The next useful route should lock a lower elongated ceratopsian torso and toe topology, "
                    "then preserve the strong head/frill/horn read with local i2i or a ceratopsian LoRA."
                ),
                "rejectIfPromoting": [
                    "torso, shoulder mass, or feet read as rhinoceros-like",
                    "frill attaches to shoulders, back, or torso instead of skull",
                    "mouth opens or teeth appear",
                    "horn count is not exactly two brow horns plus one nasal horn",
                    "feet become hoof-like or hide toe separation",
                    "tail is cropped, hidden, or short"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V27, V28, V29, V30, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
