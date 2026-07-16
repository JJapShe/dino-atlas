import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V69 = ASSETS / "stegosaurus-stenops-plate-row-i2i-v69.png"
V70 = ASSETS / "stegosaurus-stenops-imagegen-v70-source-candidate.png"
V71 = ASSETS / "stegosaurus-stenops-imagegen-v71-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p1-v70-v71-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p1-v70-v71-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p1_v70_v71_review.json"

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
        tile(CURRENT, "current v6 count-level pass", "Best current app first candidate: four-spike tail and broad plates, but two-row topology is not final."),
        tile(V71, "v71 two-row plate source hold", "Best new plate-overlap read, but tail-spike count can collapse at review scale."),
        tile(V70, "v70 broad-plate source hold", "Broad plates and visible thagomizer, but plates still read mostly as a single row."),
        tile(V69, "v69 plate-row i2i hold", "Stable v6 body and tail with subtle plate-edge hardening; not stronger than v6."),
        tile(GUIDE, "plate topology guide", "Project-owned guide for staggered two-row plates, gaps, low body, and four thagomizer spikes."),
        tile(CURRENT_CROPS, "v6 crop gate", "Existing close-review gate for dorsal plates, plate gaps, tail spikes, feet, and body."),
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
        ("current v6", CURRENT),
        ("v71 source hold", V71),
        ("v70 source hold", V70),
        ("v69 i2i hold", V69),
        ("plate topology guide", GUIDE),
        ("v6 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("dorsal plates", (0.08, 0.06, 0.78, 0.50), (430, 210)),
        ("plate gaps/topology", (0.25, 0.04, 0.66, 0.43), (360, 210)),
        ("tail spikes", (0.72, 0.36, 1.0, 0.74), (330, 210)),
        ("feet/legs", (0.12, 0.58, 0.66, 0.94), (390, 210)),
        ("head/neck", (0.00, 0.28, 0.27, 0.66), (320, 210)),
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
                "experiment": "p1_v70_v71_plate_topology_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V71),
                "comparisonReviewHold": relative(V70),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V71 is the strongest new prompt-only plate-overlap candidate and reads slightly more like a staggered two-row plate arrangement than v70, "
                    "but it does not safely beat v6 because the tail-spike count can collapse at crop scale. V70 has strong broad plates and visible tail spikes, "
                    "but its plate bases still read mostly as a single row. Keep v6 first."
                ),
                "rejectIfPromoting": [
                    "dorsal plates read as a single connected sail or one decorative row",
                    "plates become leaf petals, flower petals, comb teeth, or feathers",
                    "tail has fewer or more than four countable thagomizer spikes",
                    "body drifts into ankylosaur, sauropod, theropod, turtle, or generic herbivore",
                    "feet, head, tail tip, or plate bases are hidden enough to block review"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V69, V70, V71, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
