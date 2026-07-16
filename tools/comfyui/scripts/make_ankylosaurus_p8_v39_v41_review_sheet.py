import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

V38 = ASSETS / "ankylosaurus-magniventris-imagegen-v38-source-candidate.png"
V39 = ASSETS / "ankylosaurus-magniventris-imagegen-v39-source-candidate.png"
V40 = ASSETS / "ankylosaurus-magniventris-imagegen-v40-source-candidate.png"
V41 = ASSETS / "ankylosaurus-magniventris-imagegen-v41-source-candidate.png"
V34 = ASSETS / "ankylosaurus-magniventris-imagegen-v34-source-candidate.png"
GUIDE = ASSETS / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"

REVIEW_SHEET = ASSETS / "ankylosaurus-p8-v39-v41-review-sheet.png"
CROP_SHEET = ASSETS / "ankylosaurus-p8-v39-v41-crops.png"
REVIEW_JSON = REVIEW_ROOT / "ankylosaurus_p8_v39_v41_review.json"

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
        tile(V40, "v40 promoted p8 color/skull candidate", "Best P8 balance: red-ochre pattern plus stronger armored skull, cheek horns, compact body, and one club."),
        tile(V38, "previous v38 first", "Still strong compact body and club, but color is samey and the head reads smoother/lizard-like."),
        tile(V39, "v39 dark-olive review hold", "Good darker color and head armor, but side spikes and body mass need close review before promotion."),
        tile(V41, "v41 blue-gray review hold", "Strong cool color and skull horns; keep below v40 because horn size and head shape may be over-emphasized."),
        tile(V34, "previous v34 hold", "Older broad-skull app-first hold retained for body and club comparison."),
        tile(GUIDE, "armor tail-club guide", "Control target: broad skull, short neck, low osteoderms, four sturdy feet, one attached club."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("v40 promoted p8", V40),
        ("previous v38", V38),
        ("v39 dark-olive hold", V39),
        ("v41 blue-gray hold", V41),
        ("previous v34", V34),
        ("armor tail-club guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("skull armor/horns", (0.00, 0.15, 0.36, 0.66), (360, 210)),
        ("color pattern", (0.12, 0.14, 0.82, 0.72), (400, 210)),
        ("armor rows", (0.16, 0.10, 0.74, 0.58), (390, 210)),
        ("feet/legs", (0.08, 0.56, 0.78, 0.96), (390, 210)),
        ("tail club", (0.56, 0.24, 1.0, 0.74), (390, 210)),
        ("body compactness", (0.18, 0.20, 0.86, 0.84), (410, 210)),
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
                "experiment": "p8_v39_v41_color_pattern_armored_skull_candidates",
                "previousPrimary": relative(V38),
                "selectedPrimary": relative(V40),
                "selectedReviewHolds": [relative(V39), relative(V41), relative(V38), relative(V34)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v40_to_count_level_pass_for_color_and_skull_identity",
                "reason": (
                    "V40 improves the current gallery problem where many dinosaurs share similar tan-brown coloration, and it gives the strongest P8 armored-skull read: "
                    "clear cheek horns, rear skull-corner horn cues, a compact blunt head, low rounded osteoderm rows, four visible feet, and one attached oval tail club. "
                    "V38 remains a strong compact-body comparison but its smoother head and samey brown palette are weaker for app identity. "
                    "V39 and V41 are useful color/head-armor holds but need closer horn-size, body, and foot review before promotion."
                ),
                "remainingRisks": [
                    "skull horn size and exact cranial armor layout still need reference review",
                    "toe details are count-level rather than final",
                    "red-ochre pattern should stay naturalistic and not become fantasy saturation",
                    "tail club shape and attachment need final close crop review",
                ],
                "rejectIfPromoting": [
                    "body reads as crocodile, monitor lizard, pangolin, turtle, armadillo, rhinoceros, or fantasy armored reptile",
                    "skull becomes long and smooth like a lizard rather than broad, blunt, and armored",
                    "skull horns become oversized fantasy spikes or ceratopsian horns",
                    "tail club is missing, detached, doubled, soft, spiked, or replaced by a paddle",
                    "armor becomes tall Stegosaurus plates or fantasy spikes",
                    "feet are hidden, fused, extra, or the animal reads as six-legged",
                    "color becomes neon, toy-like, or plain samey tan-brown",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [V38, V39, V40, V41, V34, GUIDE]
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
