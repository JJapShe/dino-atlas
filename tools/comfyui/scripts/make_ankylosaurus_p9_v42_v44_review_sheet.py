import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

V40 = ASSETS / "ankylosaurus-magniventris-imagegen-v40-source-candidate.png"
V42 = ASSETS / "ankylosaurus-magniventris-imagegen-v42-source-candidate.png"
V43 = ASSETS / "ankylosaurus-magniventris-imagegen-v43-source-candidate.png"
V44 = ASSETS / "ankylosaurus-magniventris-imagegen-v44-source-candidate.png"
V38 = ASSETS / "ankylosaurus-magniventris-imagegen-v38-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p9-v42-v44-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p9-v42-v44-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p9_v42_v44_review.json"

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
        tile(V40, "current v40 count-level pass", "Keep first: compact low body, visible cheek horns, four legs, one attached club, and useful red-ochre color."),
        tile(V43, "v43 best P9 armored-skull hold", "Strongest new blunt helmet skull and cheek horns with darker color; hold because armor rows look slightly over-regular."),
        tile(V42, "v42 slate-blue armor hold", "Good head armor, pale horn tips, and color separation; hold because dorsal armor can read as oversized grid plates."),
        tile(V44, "v44 charcoal/russet color hold", "Useful color pattern and single club; hold because sunset lighting and regular back plates need stricter review."),
        tile(V38, "previous v38 body comparison", "Useful compact body comparison, but smoother lizard-like head and samey brown palette remain weaker."),
        tile(GUIDE, "armor tail-club guide", "Control target: broad blunt armored skull, short neck, low osteoderms, four sturdy feet, one attached club."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v40", V40),
        ("v43 best head hold", V43),
        ("v42 slate-blue hold", V42),
        ("v44 color hold", V44),
        ("previous v38", V38),
        ("armor guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("armored skull/horns", (0.00, 0.14, 0.34, 0.64), (360, 210)),
        ("cheek horns", (0.00, 0.18, 0.28, 0.56), (330, 210)),
        ("dorsal armor rows", (0.16, 0.10, 0.72, 0.56), (390, 210)),
        ("feet/leg count", (0.08, 0.56, 0.78, 0.96), (390, 210)),
        ("tail club", (0.58, 0.25, 1.0, 0.75), (390, 210)),
        ("color separation", (0.08, 0.12, 0.82, 0.74), (410, 210)),
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
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "p9_v42_v44_armored_skull_color_variation",
                "currentPrimary": relative(V40),
                "selectedReviewHolds": [relative(V43), relative(V42), relative(V44)],
                "rejectReferences": [],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v40_primary_add_v43_v42_v44_as_review_holds",
                "reason": (
                    "P9 directly targets the user's lizard-head concern. V43 has the strongest new broad armored skull, cheek horns, "
                    "rear skull-horn cues, dark color separation, four legs, and one attached tail club. V42 and V44 also improve "
                    "color and cranial armor readability. None should be promoted yet because the dorsal osteoderm rows can read as "
                    "too regular or plate-like, so v40 remains the count-level app primary until a stricter body-lock route preserves "
                    "the improved skull without over-regularizing the back armor."
                ),
                "remainingRisks": [
                    "dorsal armor rows may look too regular or tiled rather than naturally varied osteoderms",
                    "skull horns need to remain cheek/rear skull horns rather than fantasy spikes",
                    "front foot toe counts are still review-level, not final proof",
                    "color variation must not hide the broad low body or single tail club",
                ],
                "nextRoute": (
                    "Use v43 as the head/color reference with the armor-tailclub guide as structure control. "
                    "Apply low-denoise body-lock or ControlNet/i2i to preserve the broad blunt skull and cheek horns while softening "
                    "the over-regular dorsal plate grid. Reject any output with lizard/crocodile head, missing/doubled club, six legs, "
                    "turtle shell, fantasy spikes, or samey tan-brown collapse."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [V40, V42, V43, V44, V38, GUIDE]
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
