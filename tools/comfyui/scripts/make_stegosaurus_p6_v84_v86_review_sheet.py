import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
V82 = ASSETS / "stegosaurus-stenops-imagegen-v82-source-candidate.png"
V84 = ASSETS / "stegosaurus-stenops-imagegen-v84-source-candidate.png"
V85 = ASSETS / "stegosaurus-stenops-imagegen-v85-source-candidate.png"
V86 = ASSETS / "stegosaurus-stenops-imagegen-v86-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p6-v84-v86-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p6-v84-v86-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p6_v84_v86_review.json"

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
    panel = Image.new("RGB", (size[0], size[1] + 86), (245, 243, 236))
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
        tile(V86, "v86 promoted count-level pass", "Best current plate-plus-tail balance: broad plates and four separated thagomizer spikes."),
        tile(CURRENT, "previous v6 count-level pass", "Still useful, but plates are less bold and the image is no longer the strongest first-card read."),
        tile(V84, "v84 four-spike hold", "Strong four-spike tail and broad plates, but mid plates are oversized and less natural."),
        tile(V85, "v85 three-spike risk reject", "Good body and plates, but the tail can read as only three countable spikes."),
        tile(V82, "previous v82 near-four hold", "Prior best P5 hold; broad plates, but lower tail geometry can read overlapped or duplicated."),
        tile(GUIDE, "plate topology guide", "Project-owned target: staggered broad plates and exactly four countable tail spikes."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("v86 promoted", V86),
        ("previous v6", CURRENT),
        ("v84 four-spike hold", V84),
        ("v85 three-spike risk", V85),
        ("previous v82 hold", V82),
        ("plate topology guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("head/neck", (0.00, 0.28, 0.24, 0.69), (320, 210)),
        ("mid plates", (0.20, 0.05, 0.66, 0.53), (380, 210)),
        ("plate gaps", (0.30, 0.04, 0.74, 0.50), (380, 210)),
        ("feet/legs", (0.12, 0.55, 0.68, 0.96), (380, 210)),
        ("tail spikes", (0.68, 0.22, 1.00, 0.82), (380, 210)),
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
                "experiment": "p6_v84_v86_four_spike_separation_candidates",
                "previousPrimary": relative(CURRENT),
                "promotedPrimary": relative(V86),
                "selectedReviewHold": relative(V84),
                "comparisonReviewHolds": [relative(V82)],
                "selectedRejectReferences": [relative(V85)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v86_to_count_level_pass",
                "reason": (
                    "V86 is the best current balance of a low quadrupedal Stegosaurus body, small head, broad separated dorsal plates, "
                    "four visible planted feet, and an unambiguous four-spike thagomizer. "
                    "V84 is useful four-spike review evidence but the mid plates are oversized and less natural. "
                    "V85 is rejected because the tail weapon can read as three countable spikes. "
                    "V82 remains a comparison hold because lower tail geometry can still read overlapped or duplicated."
                ),
                "remainingRisks": [
                    "alternating two-row plate topology is improved for first-card readability but still needs final reference review",
                    "plate surfaces and bases should be checked before final approval",
                    "far-side feet and exact toe shapes remain count-level rather than final",
                ],
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
    required = [CURRENT, V82, V84, V85, V86, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
