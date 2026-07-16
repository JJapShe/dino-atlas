import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-imagegen-v86-source-candidate.png"
PREVIOUS = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
V87 = ASSETS / "stegosaurus-stenops-imagegen-v87-source-candidate.png"
V88 = ASSETS / "stegosaurus-stenops-imagegen-v88-source-candidate.png"
V89 = ASSETS / "stegosaurus-stenops-imagegen-v89-source-candidate.png"
V84 = ASSETS / "stegosaurus-stenops-imagegen-v84-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p7-v87-v89-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p7-v87-v89-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p7_v87_v89_review.json"

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


def tile(path, title, note, size=(430, 242), accent=(132, 61, 43)):
    panel = Image.new("RGB", (size[0], size[1] + 78), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, size[1], size[0], size[1] + 6), fill=accent)
    draw.text((8, size[1] + 12), title[:70], fill=accent, font=FONT)
    draw_wrapped(draw, (8, size[1] + 35), note)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v86 count-level pass", "Still best combined broad plates, low body, four feet, and exactly four tail spikes.", accent=(38, 116, 76)),
        tile(V87, "v87 five-spike risk reject", "Similar body/plate read, but the tail can read as five spikes.", accent=(152, 66, 58)),
        tile(V88, "v88 leaf-plate review hold", "Tail is near four, but plates become larger, rounder, and more leaf/fan-like.", accent=(146, 99, 45)),
        tile(V89, "v89 stable-tail review hold", "Stable body and tail, but plates do not improve over v86 and head framing is tighter.", accent=(146, 99, 45)),
        tile(PREVIOUS, "previous v6 hold", "Older positive comparison for natural body and countable thagomizer.", accent=(95, 98, 112)),
        tile(V84, "v84 four-spike hold", "Useful four-spike comparison, but mid-back plates are oversized.", accent=(95, 98, 112)),
        tile(GUIDE, "plate topology guide", "Target: staggered broad plates and exactly four countable tail spikes.", accent=(68, 92, 140)),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v86", CURRENT),
        ("v87 five-spike risk", V87),
        ("v88 leaf-plate hold", V88),
        ("v89 stable-tail hold", V89),
        ("previous v6", PREVIOUS),
        ("v84 four-spike hold", V84),
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
                "experiment": "p7_v87_v89_alternating_plate_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(CURRENT),
                "reviewHolds": [relative(V88), relative(V89), relative(PREVIOUS), relative(V84)],
                "rejectReferences": [relative(V87)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v86_first_add_v88_v89_holds_and_v87_reject",
                "reason": (
                    "V86 remains the safest current app-first candidate. The P7 prompt-only candidates did not improve the alternating plate gate enough to justify promotion. "
                    "V87 has a similar body/plate read but the tail can read as five thagomizer spikes. V88 keeps a near-four tail but the dorsal plates become larger, rounder, and more leaf/fan-like. "
                    "V89 has a stable body and tail but does not beat v86 on plate topology and has tighter head framing."
                ),
                "nextRoute": (
                    "Keep v86 as the positive smoke-test seed. Use v88/v89 as review holds and v87 as a reject reference. "
                    "The next useful route should be localized plate-row i2i or Stegosauridae-specific LoRA/control training that offsets plate bases without changing the reliable v86 tail."
                ),
                "rejectIfPromoting": [
                    "tail tip shows fewer or more than exactly four large thagomizer spikes",
                    "plates become leaf-like, fin-like, scalloped, or a single connected sail",
                    "plate bases read as one centered row with no alternating left-right offset",
                    "plate gaps close enough to become a comb or continuous ridge",
                    "head, feet, or tail tip are cropped or hidden",
                    "body drifts toward ankylosaur, turtle, sauropod, or generic low reptile",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, PREVIOUS, V87, V88, V89, V84, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
