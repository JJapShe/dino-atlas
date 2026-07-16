import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "theropod_allosaurus" / "review"

CURRENT = ASSETS / "allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png"
CURRENT_CROPS = ASSETS / "allosaurus-smoothbrow-threefinger-crops-v4.png"
V11_CROPS = ASSETS / "allosaurus-digit-micro-i2i-v11-crops.png"
V12_REJECT = ASSETS / "allosaurus-fragilis-imagegen-v12-source-candidate.png"
V13 = ASSETS / "allosaurus-fragilis-imagegen-v13-source-candidate.png"
GUIDE = ASSETS / "allosaurus-fragilis-threefinger-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "allosaurus-p1-v12-v13-review-sheet.png"
CROP_SHEET = ASSETS / "allosaurus-p1-v12-v13-crops.png"
REVIEW_JSON = REVIEW_ROOT / "allosaurus_p1_v12_v13_review.json"

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
        tile(CURRENT, "current v4 count-level pass", "Best current app candidate; smooth brow and medium arms, exact digit gate still close-review only."),
        tile(V13, "v13 smooth-brow source hold", "Better brow restraint and full-body read, but the visible hand can read as four fingers."),
        tile(V12_REJECT, "v12 horn/digit rejection", "Useful failure anchor: body is allosaur-like, but brow bumps and hand digits are too risky."),
        tile(V11_CROPS, "v11 digit micro crop gate", "Low-denoise hand/foot i2i evidence; preserves v4 but does not solve exact digits."),
        tile(CURRENT_CROPS, "v4 crop gate", "Baseline close-review sheet for hand, brow, feet, body, and tail."),
        tile(GUIDE, "three-finger body-lock guide", "Project-owned control target for low skull, medium arms, exactly three fingers, and two hind legs."),
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
        ("current v4", CURRENT),
        ("v13 smooth-brow hold", V13),
        ("v12 horn/digit reject", V12_REJECT),
        ("three-finger guide", GUIDE),
        ("v11 existing crop gate", V11_CROPS),
        ("v4 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.00, 0.06, 1.00, 0.92), (430, 210)),
        ("skull/brow", (0.00, 0.12, 0.31, 0.48), (360, 210)),
        ("forelimb/hand", (0.17, 0.36, 0.42, 0.74), (330, 210)),
        ("hand digits", (0.19, 0.42, 0.37, 0.73), (280, 210)),
        ("hind feet", (0.30, 0.62, 0.75, 0.94), (380, 210)),
        ("tail", (0.55, 0.27, 1.00, 0.64), (380, 210)),
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
        if path in (V11_CROPS, CURRENT_CROPS):
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
                "taxonId": "allosaurus-fragilis",
                "experiment": "p1_v12_v13_source_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V13),
                "selectedRejectReference": relative(V12_REJECT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V13 improves the smooth-brow full-body Allosaurus read compared with the v12 horn-risk candidate, "
                    "but the hand can still read as four fingers. Keep v4 first, keep v13 as review_hold only, and keep "
                    "v12 as a reject reference for horn-brow and ambiguous-digit drift."
                ),
                "rejectIfPromoting": [
                    "visible hand reads as four or five fingers instead of exactly three",
                    "brow ridges become raised horns, crown bumps, or fantasy crests",
                    "forelimbs shrink into tiny two-finger Tyrannosaurus arms",
                    "skull becomes deep and blocky like Tyrannosaurus",
                    "feet, hands, or tail are hidden enough to block count review"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V11_CROPS, V12_REJECT, V13, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
