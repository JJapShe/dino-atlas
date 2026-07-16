import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
V79 = ASSETS / "stegosaurus-stenops-imagegen-v79-source-candidate.png"
V81 = ASSETS / "stegosaurus-stenops-imagegen-v81-source-candidate.png"
V82 = ASSETS / "stegosaurus-stenops-imagegen-v82-source-candidate.png"
V83 = ASSETS / "stegosaurus-stenops-imagegen-v83-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p5-v81-v83-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p5-v81-v83-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p5_v81_v83_review.json"

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
        tile(CURRENT, "current v6 count-level pass", "Still first because it keeps the safest four-spike read, though plates are less bold."),
        tile(V79, "v79 previous closest hold", "Prior best compromise; useful comparison but lower tail overlap can still read as extra spike."),
        tile(V81, "v81 broad-plate tail reject", "Good broad plate mass, but tail tip reads as five or more spikes."),
        tile(V82, "v82 best p5 review hold", "Best fresh tail-count candidate: broad plates and the clearest near-four thagomizer read."),
        tile(V83, "v83 lower-overlap hold", "Strong side body and plates, but the lower tail spike still overlaps enough to stay unsafe."),
        tile(GUIDE, "plate topology guide", "Project-owned target: staggered two-row plates and exactly four countable tail spikes."),
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
        ("v79 prior hold", V79),
        ("v81 tail reject", V81),
        ("v82 best p5 hold", V82),
        ("v83 lower-overlap hold", V83),
        ("plate topology guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("head/neck", (0.00, 0.28, 0.24, 0.69), (320, 210)),
        ("mid plates", (0.20, 0.05, 0.66, 0.53), (380, 210)),
        ("plate gaps", (0.30, 0.04, 0.74, 0.50), (380, 210)),
        ("feet/legs", (0.12, 0.55, 0.68, 0.96), (380, 210)),
        ("tail spikes", (0.68, 0.27, 1.00, 0.78), (380, 210)),
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
                "experiment": "p5_v81_v83_tail_count_locked_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V82),
                "secondaryReviewHold": relative(V83),
                "selectedRejectReferences": [relative(V81)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v6",
                "reason": (
                    "V82 is the best fresh candidate because the tail end most nearly resolves into four large thagomizer spikes while keeping broad separated plates. "
                    "It stays review_hold because the lower right spike area can still be read as overlapping geometry, and the alternating two-row plate topology is not proven stronger than v6. "
                    "V81 clearly overcounts the thagomizer. V83 keeps a useful body and plate read but still has lower-spike overlap risk."
                ),
                "rejectIfPromoting": [
                    "tail tip shows fewer or more than exactly four large spikes",
                    "any spike is duplicated by a lower shadow-like extra spur",
                    "plates read as leaves, fins, continuous sail panels, or armored shingles",
                    "plate row loses visible sky gaps between separate plates",
                    "legs or feet are hidden enough to block quadruped count",
                    "body drifts toward ankylosaur, turtle, sauropod, or theropod anatomy",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V79, V81, V82, V83, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
