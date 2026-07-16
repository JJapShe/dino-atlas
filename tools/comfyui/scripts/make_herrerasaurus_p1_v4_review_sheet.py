import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_saurischian_herrerasaurus" / "review"

CURRENT = ASSETS / "herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png"
CURRENT_CROPS = ASSETS / "herrerasaurus-compacthands-crops-v2.png"
BALANCED = ASSETS / "herrerasaurus-ischigualastensis-balancedhands-imagegen-v2.png"
V4 = ASSETS / "herrerasaurus-ischigualastensis-imagegen-v4-source-candidate.png"
GUIDE = ASSETS / "herrerasaurus-ischigualastensis-bodylock-guide-v1.png"
BODYLOCK_CROPS = ASSETS / "herrerasaurus-bodylock-crops-v3.png"

REVIEW_SHEET = ASSETS / "herrerasaurus-p1-v4-review-sheet.png"
CROP_SHEET = ASSETS / "herrerasaurus-p1-v4-crops.png"
REVIEW_JSON = REVIEW_ROOT / "herrerasaurus_p1_v4_review.json"

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
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v2 count-level pass", "Best current compact-hand candidate; closed head and two-leg stance pass count-level review."),
        tile(V4, "v4 Triassic source hold", "Fresh source candidate with better red floodplain scene, but hand count can read as too many long fingers."),
        tile(BALANCED, "balanced-hands v2 risk", "Useful forelimb-length comparison, but the hand crop can read as many equal fingers."),
        tile(GUIDE, "compact-hand body-lock guide", "Project-owned control target for narrow head, compact folded hands, two hind legs, and full tail."),
        tile(CURRENT_CROPS, "v2 crop gate", "Baseline close-review sheet for head, hands, hind legs, feet, and tail."),
        tile(BODYLOCK_CROPS, "body-lock crop gate", "Guide-versus-current gate for three-main-digit hand target and hind-leg count."),
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
        ("current v2", CURRENT),
        ("v4 source hold", V4),
        ("balanced v2 risk", BALANCED),
        ("body-lock guide", GUIDE),
        ("v2 existing crop gate", CURRENT_CROPS),
        ("body-lock existing crop gate", BODYLOCK_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.07, 1.00, 0.92), (430, 210)),
        ("head", (0.00, 0.12, 0.31, 0.50), (360, 210)),
        ("forelimb/hand", (0.18, 0.36, 0.40, 0.75), (320, 210)),
        ("hand digits", (0.21, 0.43, 0.35, 0.76), (280, 210)),
        ("hind legs/feet", (0.34, 0.55, 0.70, 0.95), (360, 210)),
        ("tail", (0.52, 0.27, 1.00, 0.62), (380, 210)),
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
        if path in (CURRENT_CROPS, BODYLOCK_CROPS):
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
                "taxonId": "herrerasaurus-ischigualastensis",
                "experiment": "p1_v4_source_candidate",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V4),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V4 improves the copyright-safe Triassic floodplain scene and keeps a full side-profile body, two hind legs, "
                    "long tail, and narrow closed head. Keep v2 first because v4's hand can still read as too many equal long fingers "
                    "rather than the three-main-digit plus tiny vestigial outer-digit target."
                ),
                "rejectIfPromoting": [
                    "visible hand reads as four or five equal long fingers",
                    "forelimbs touch the ground or become extra weight-bearing legs",
                    "arms shrink into tiny two-finger Tyrannosaurus proportions",
                    "body becomes bulky Allosaurus or Tyrannosaurus-like",
                    "head, feet, or tail are hidden enough to block count review"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, BALANCED, V4, GUIDE, BODYLOCK_CROPS]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
