import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V33 = ASSETS / "triceratops-horridus-imagegen-v33-source-candidate.png"
V34 = ASSETS / "triceratops-horridus-imagegen-v34-source-candidate.png"
V35 = ASSETS / "triceratops-horridus-imagegen-v35-source-candidate.png"
V36 = ASSETS / "triceratops-horridus-imagegen-v36-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p4-v34-v36-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p4-v34-v36-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p4_v34_v36_review.json"

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
        tile(CURRENT, "current v22 count-level pass", "Current first, but not final: useful horns/frill/feet with remaining rhino-body risk."),
        tile(V35, "v35 best P4 review hold", "Best new anti-rhino balance: longer body and tail, closed beak, three horns, visible toes; still not final."),
        tile(V34, "v34 secondary review hold", "Good closed beak, skull frill, and three horns; torso remains too high and rounded."),
        tile(V36, "v36 round-body reject", "Feet and tail are useful, but the body returns to a rounded mammal-like mass."),
        tile(V33, "v33 previous hold", "Previous best prompt-only hold; useful head/frill/tail, but still shoulder-heavy."),
        tile(GUIDE, "skull-frill body-lock guide", "Control target for skull-attached frill, three horns, closed beak, long tail, and anti-rhino body."),
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
        ("v35 best hold", V35),
        ("v34 secondary hold", V34),
        ("v36 round-body reject", V36),
        ("v33 previous hold", V33),
        ("body-lock guide", GUIDE),
        ("v22 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("head/frill/horns", (0.00, 0.08, 0.42, 0.62), (380, 210)),
        ("frill attachment", (0.14, 0.05, 0.42, 0.52), (330, 210)),
        ("body anti-rhino", (0.25, 0.16, 0.78, 0.78), (390, 210)),
        ("feet/toes", (0.10, 0.58, 0.72, 0.96), (390, 210)),
        ("tail length", (0.58, 0.28, 1.0, 0.72), (360, 210)),
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
                "experiment": "p4_v34_v36_antirhino_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V35),
                "secondaryReviewHold": relative(V34),
                "selectedRejectReferences": [relative(V36)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "demote_app_status_to_reviewing_keep_current_v22",
                "reason": (
                    "The app status should be reviewing, not approved. V35 is the best fresh P4 candidate because it improves the low elongated body, long tail, closed beak, three-horn read, and visible non-hoofed toes. "
                    "It still stays below v22 because the torso and frill ornament are not fully reference-clean. V34 is a secondary review hold with useful skull/frill identity but a high rounded torso. "
                    "V36 is a reject reference because the body returns to a rounded mammal-like mass despite useful feet and tail cues."
                ),
                "nextRoute": (
                    "Continue with skull-frill body-lock i2i or a curated ceratopsian LoRA branch. Prompt-only candidates now improve identity, but they do not fully solve low elongated torso, toe detail, and anti-rhino body proportions together."
                ),
                "rejectIfPromoting": [
                    "reviewStatus is marked approved before close crop review",
                    "torso, shoulder mass, or feet read as rhinoceros-like",
                    "body is a round barrel rather than low elongated ceratopsian form",
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
    required = [CURRENT, CURRENT_CROPS, V33, V34, V35, V36, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
