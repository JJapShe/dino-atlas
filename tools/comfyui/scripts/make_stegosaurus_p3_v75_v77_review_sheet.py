import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V72 = ASSETS / "stegosaurus-stenops-imagegen-v72-source-candidate.png"
V75 = ASSETS / "stegosaurus-stenops-imagegen-v75-source-candidate.png"
V76 = ASSETS / "stegosaurus-stenops-imagegen-v76-source-candidate.png"
V77 = ASSETS / "stegosaurus-stenops-imagegen-v77-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p3-v75-v77-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p3-v75-v77-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p3_v75_v77_review.json"

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
        tile(CURRENT, "current v6 count-level pass", "Best current balance: broad separated plates plus a more countable thagomizer than new prompt-only tries."),
        tile(V77, "v77 broad-plate review hold", "Strong broad plates and body, but tail spikes still overcount; keep below v6."),
        tile(V72, "v72 broad-plate prior hold", "Strongest earlier rough broad plate target; tail overcount blocks promotion."),
        tile(V75, "v75 overcount reject", "Very strong plates, but thagomizer clearly has too many spikes."),
        tile(V76, "v76 leaf-vein overcount reject", "Broad plates, but leaf-vein surface and too many tail spikes make it unsafe."),
        tile(GUIDE, "plate topology guide", "Project-owned guide for two staggered plate rows and exactly four tail spikes."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v6", CURRENT),
        ("v77 hold", V77),
        ("v72 prior hold", V72),
        ("v75 overcount reject", V75),
        ("v76 leaf/overcount reject", V76),
        ("plate topology guide", GUIDE),
        ("v6 crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("head/neck", (0.00, 0.30, 0.24, 0.68), (320, 210)),
        ("mid plates", (0.20, 0.06, 0.64, 0.52), (380, 210)),
        ("plate gaps", (0.28, 0.04, 0.72, 0.48), (380, 210)),
        ("feet/legs", (0.12, 0.55, 0.66, 0.96), (380, 210)),
        ("tail spikes", (0.70, 0.30, 1.00, 0.74), (360, 210)),
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
                "taxonId": "stegosaurus-stenops",
                "experiment": "p3_v75_v77_broad_plate_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V77),
                "selectedRejectReferences": [relative(V75), relative(V76)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v6",
                "reason": (
                    "V77 is the most useful fresh comparison because it keeps strong broad separated plates and a good Stegosaurus body, "
                    "but its tail still overcounts the thagomizer. V75 and V76 have similarly strong plate mass but clearly show too many tail spikes, "
                    "and V76 also risks leaf-vein plate surfaces. Keep v6 first until broad separated plates and exactly four thagomizer spikes pass in the same image."
                ),
                "rejectIfPromoting": [
                    "tail tip shows fewer or more than exactly four large spikes",
                    "plates read as leaves, leaf veins, fins, or a connected sail",
                    "plate row becomes a single wall without visible gaps",
                    "legs or feet are hidden enough to block quadruped count",
                    "body drifts toward ankylosaur, turtle, sauropod, or theropod anatomy"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V72, V75, V76, V77, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
