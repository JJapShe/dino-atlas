import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V71 = ASSETS / "stegosaurus-stenops-imagegen-v71-source-candidate.png"
V72 = ASSETS / "stegosaurus-stenops-imagegen-v72-source-candidate.png"
V73 = ASSETS / "stegosaurus-stenops-imagegen-v73-source-candidate.png"
V74 = ASSETS / "stegosaurus-stenops-imagegen-v74-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p2-v72-v74-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p2-v72-v74-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p2_v72_v74_review.json"

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
    panel = Image.new("RGB", (size[0], size[1] + 82), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note, max_lines=3)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v6 count-level pass", "Still first because the tail count is readable, though plate topology is not final."),
        tile(V72, "v72 broad-plate source hold", "Best new plate identity: broad, rough, separated slabs. Reject for promotion unless tail overcount is solved."),
        tile(V73, "v73 clean-plate source hold", "Clean plate gaps and surface; tail reads closer to three spikes, so it cannot replace v6."),
        tile(V74, "v74 tail-count diagnostic", "Tail weapon is large and reviewable, but pose, legs, and plate count are weaker for a representative."),
        tile(V71, "previous v71 source hold", "Previous best prompt-only two-row cue, kept for continuity with the P1 gate."),
        tile(GUIDE, "plate topology guide", "Control target for staggered two-row plates, visible gaps, low body, and four thagomizer spikes."),
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
        ("v72 broad-plate hold", V72),
        ("v73 clean-plate hold", V73),
        ("v74 tail diagnostic", V74),
        ("previous v71", V71),
        ("plate topology guide", GUIDE),
        ("v6 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("dorsal plates", (0.08, 0.04, 0.80, 0.52), (430, 210)),
        ("plate gaps/topology", (0.22, 0.02, 0.72, 0.45), (360, 210)),
        ("tail spikes", (0.72, 0.30, 1.0, 0.76), (330, 210)),
        ("feet/legs", (0.10, 0.56, 0.68, 0.95), (390, 210)),
        ("head/neck", (0.00, 0.32, 0.30, 0.70), (320, 210)),
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
                "experiment": "p2_v72_v74_broad_plate_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedPlateReviewHold": relative(V72),
                "comparisonReviewHolds": [relative(V73), relative(V74), relative(V71)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V72 is the strongest new broad-plate identity candidate and gives the clearest rough separated slab-like Stegosaurus plates, "
                    "but its tail tip appears to overcount the thagomizer. V73 has cleaner plate gaps but undercounts tail spikes. "
                    "V74 makes the tail weapon more visible but weakens representative side-profile posture and plate count. Keep v6 first."
                ),
                "nextRoute": (
                    "Use v72 as a plate-texture/plate-size visual target, but pair it with a tail-tip structure guide or local tail i2i. "
                    "Do not promote any candidate unless broad separated plates and exactly four tail spikes pass in the same crop gate."
                ),
                "rejectIfPromoting": [
                    "tail has fewer or more than four countable thagomizer spikes",
                    "dorsal plates fuse into a single sail, fan, comb, or decorative leaf row",
                    "plate bases read as ankylosaur armor instead of upright Stegosaurus plates",
                    "body loses the low quadrupedal small-head Stegosaurus silhouette",
                    "feet, head, plate bases, or tail tip are hidden enough to block review"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V71, V72, V73, V74, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
