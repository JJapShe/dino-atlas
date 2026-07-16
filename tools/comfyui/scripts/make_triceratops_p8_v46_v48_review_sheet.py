import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

V43 = ASSETS / "triceratops-horridus-imagegen-v43-source-candidate.png"
V46 = ASSETS / "triceratops-horridus-imagegen-v46-source-candidate.png"
V47 = ASSETS / "triceratops-horridus-imagegen-v47-source-candidate.png"
V48 = ASSETS / "triceratops-horridus-imagegen-v48-source-candidate.png"
V41 = ASSETS / "triceratops-horridus-imagegen-v41-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p8-v46-v48-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p8-v46-v48-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p8_v46_v48_review.json"

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
        tile(V43, "current v43 first candidate", "Keep first: strongest familiar Triceratops read with three horns, skull frill, tail, and toes."),
        tile(V46, "v46 p8 review hold", "Very close to v43. Useful source hold, but feet and rounded torso do not clearly beat v43."),
        tile(V47, "v47 p8 reject reference", "Strong head/frill, but foot/leg read is weaker and the body still carries round mammal-mass risk."),
        tile(V48, "v48 p8 review hold", "Good silhouette and long tail; keep below v43 until toe separation and body mass pass closer review."),
        tile(V41, "previous v41 low-body hold", "Lower anti-rhino body comparison retained below v43 for future body-lock work."),
        tile(GUIDE, "skull-frill body-lock guide", "Control target for skull-attached frill, low long body, long tail, and non-hoofed toes."),
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
        ("current v43 first", V43),
        ("v46 review hold", V46),
        ("v47 reject reference", V47),
        ("v48 review hold", V48),
        ("previous v41 hold", V41),
        ("body-lock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("head/frill/horns", (0.00, 0.08, 0.42, 0.66), (380, 210)),
        ("frill attachment", (0.12, 0.05, 0.42, 0.52), (330, 210)),
        ("body anti-rhino", (0.22, 0.16, 0.78, 0.78), (390, 210)),
        ("feet/toes", (0.10, 0.58, 0.72, 0.96), (390, 210)),
        ("tail length", (0.58, 0.24, 1.0, 0.72), (360, 210)),
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
                "taxonId": "triceratops-horridus",
                "experiment": "p8_v46_v48_antirhino_prompt_review",
                "selectedPrimary": relative(V43),
                "reviewHolds": [relative(V46), relative(V48), relative(V41)],
                "rejectReferences": [relative(V47)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v43_first_add_v46_v48_holds_and_v47_reject",
                "reason": (
                    "The P8 prompt pass did not produce a clear replacement for v43. V46 is a near-duplicate-style hold with useful familiar Triceratops cues, "
                    "but its rounded torso and foot details do not clearly improve the current first candidate. V48 has a good full silhouette and long tail but still needs toe and body-mass review. "
                    "V47 is kept as a reject reference because its foot and leg read is weaker despite a strong head and frill."
                ),
                "rejectIfPromoting": [
                    "torso, shoulder mass, or feet read as rhinoceros-like",
                    "body is a round mammal barrel rather than low elongated ceratopsian form",
                    "frill attaches to shoulders, back, or torso instead of skull",
                    "mouth opens or teeth appear",
                    "horn count is not exactly two brow horns plus one nasal horn",
                    "feet become hoof-like or hide toe separation",
                    "tail is cropped, hidden, or tiny",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [V43, V46, V47, V48, V41, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(
        json.dumps(
            {
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "review": relative(REVIEW_JSON),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
