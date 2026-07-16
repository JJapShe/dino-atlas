import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSETS / "ankylosaurus-magniventris-allfeet-lora-i2i-v18.png"
CURRENT_CROPS = ASSETS / "ankylosaurus-allfeet-lora-i2i-v17-v18-crops.png"
V20 = ASSETS / "ankylosaurus-magniventris-imagegen-v20-source-candidate.png"
V21 = ASSETS / "ankylosaurus-magniventris-imagegen-v21-source-candidate.png"
V22 = ASSETS / "ankylosaurus-magniventris-imagegen-v22-source-candidate.png"
V23 = ASSETS / "ankylosaurus-magniventris-imagegen-v23-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p2-v21-v23-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p2-v21-v23-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p2_v21_v23_review.json"

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
        tile(CURRENT, "current v18 app first", "Current app first: all-feet repair with broad low body and attached club, but still needs reference review."),
        tile(V22, "v22 balanced source hold", "Best new balance: broad skull, low armor, four feet, attached club; mild long-body lizard risk remains."),
        tile(V23, "v23 low-armor source hold", "Lowest, broadest new body and clean club; body and tail length still risk monitor-lizard drift."),
        tile(V21, "v21 horn-risk source hold", "Strong armor and club, but large skull-side projections can read as horns."),
        tile(V20, "previous v20 source hold", "Previous project-owned candidate with four feet and club; kept for continuity."),
        tile(GUIDE, "armor tail-club guide", "Control target for broad skull, low osteoderms, four sturdy feet, and one attached oval club."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v18", CURRENT),
        ("v22 balanced hold", V22),
        ("v23 low-armor hold", V23),
        ("v21 horn-risk hold", V21),
        ("previous v20", V20),
        ("armor tail-club guide", GUIDE),
        ("v18 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("skull/snout", (0.00, 0.24, 0.28, 0.62), (330, 210)),
        ("armor rows", (0.18, 0.14, 0.72, 0.58), (390, 210)),
        ("feet/legs", (0.10, 0.58, 0.72, 0.95), (390, 210)),
        ("tail club", (0.66, 0.28, 1.0, 0.66), (360, 210)),
        ("body length", (0.24, 0.24, 0.86, 0.80), (400, 210)),
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
                "experiment": "p2_v21_v23_armor_tailclub_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V22),
                "comparisonReviewHolds": [relative(V23), relative(V21), relative(V20)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V22 is the best new prompt-only balance: it keeps a broad blunt skull, low rounded armor, four planted feet, and one attached oval tail club. "
                    "It still stays below v18 because body and tail length can drift toward generic armored lizard. V23 improves the low broad armor read but has similar length risk. "
                    "V21 has strong armor and club but skull-side projections can read as horns."
                ),
                "nextRoute": (
                    "Use v22/v23 as project-owned source holds for future i2i or LoRA expansion. The next route should shorten the body/tail proportions and preserve the attached club, "
                    "broad skull, four sturdy feet, and low osteoderm rows together."
                ),
                "rejectIfPromoting": [
                    "body reads as crocodile, monitor lizard, pangolin, turtle, or armadillo",
                    "skull becomes long and narrow or develops horn-like side projections",
                    "tail club is missing, detached, doubled, soft, or replaced by spikes",
                    "armor becomes tall Stegosaurus-like plates or fantasy spikes",
                    "feet are hidden, extra limbs appear, or the animal becomes sprawled like a lizard"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V20, V21, V22, V23, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
