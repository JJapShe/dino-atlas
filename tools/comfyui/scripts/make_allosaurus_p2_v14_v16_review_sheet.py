import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "theropod_allosaurus" / "review"

CURRENT = ASSETS / "allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png"
V13 = ASSETS / "allosaurus-fragilis-imagegen-v13-source-candidate.png"
V14 = ASSETS / "allosaurus-fragilis-imagegen-v14-source-candidate.png"
V15 = ASSETS / "allosaurus-fragilis-imagegen-v15-source-candidate.png"
V16 = ASSETS / "allosaurus-fragilis-imagegen-v16-source-candidate.png"
GUIDE = ASSETS / "allosaurus-fragilis-threefinger-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "allosaurus-p2-v14-v16-review-sheet.png"
CROP_SHEET = ASSETS / "allosaurus-p2-v14-v16-crops.png"
REVIEW_JSON = REVIEW_ROOT / "allosaurus_p2_v14_v16_review.json"

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
        tile(CURRENT, "current v4 count-level pass", "Safest current app source: smooth brow, medium arms, and three-finger cue still needs close review."),
        tile(V13, "v13 previous review hold", "Good full-body smooth-brow read, but visible hand can read as four fingers."),
        tile(V14, "v14 horn-brow reject", "Three-finger cue is useful, but skull/brow ornament drifts too high."),
        tile(V15, "v15 three-finger review hold", "Best P2 hand candidate; brow is lower, but skull mass trends heavy/T. rex-like."),
        tile(V16, "v16 brow-risk reject", "Body and tail are useful, but brow/head detail and digit clarity are too risky."),
        tile(GUIDE, "three-finger body-lock guide", "Project-owned target for low skull, medium arms, exactly three fingers, two hind legs, and tail."),
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
        ("v13 previous hold", V13),
        ("v14 horn-brow reject", V14),
        ("v15 hand hold", V15),
        ("v16 brow-risk reject", V16),
    ]
    crops = [
        ("full body", (0.00, 0.06, 1.00, 0.92), (430, 210)),
        ("skull/brow", (0.00, 0.10, 0.33, 0.50), (360, 210)),
        ("forelimb/hand", (0.16, 0.34, 0.43, 0.75), (330, 210)),
        ("hand digits", (0.18, 0.40, 0.38, 0.73), (280, 210)),
        ("hind feet", (0.30, 0.58, 0.75, 0.95), (380, 210)),
        ("tail", (0.52, 0.25, 1.00, 0.64), (380, 210)),
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
                "taxonId": "allosaurus-fragilis",
                "experiment": "p2_v14_v16_three_finger_brow_candidates",
                "currentPrimary": relative(CURRENT),
                "candidateDecisions": [
                    {
                        "source": relative(V14),
                        "decision": "reject_reference",
                        "reason": "Useful three-finger cue, but the skull and brow ornament read too high and horn-like for the smooth-brow Allosaurus gate.",
                    },
                    {
                        "source": relative(V15),
                        "decision": "review_hold",
                        "reason": "Best P2 hand candidate with a clearer three-finger read and lower brow; keep below v4 because skull mass trends too heavy/Tyrannosaurus-like.",
                    },
                    {
                        "source": relative(V16),
                        "decision": "reject_reference",
                        "reason": "Body and tail are usable, but brow/head detail and digit clarity remain too risky for positive training.",
                    },
                ],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_primary",
                "reason": (
                    "V15 is a useful three-finger review hold, but none of the P2 candidates beats v4 on smooth brow, allosaur skull shape, "
                    "medium forelimb scale, and exact three-finger anatomy together. Keep v14/v16 as reject references."
                ),
                "rejectIfPromoting": [
                    "visible hand reads as two, four, or five fingers instead of exactly three",
                    "brow ridges become raised horns, crown bumps, or fantasy crests",
                    "forelimbs shrink into tiny two-finger Tyrannosaurus arms",
                    "skull becomes deep and blocky like Tyrannosaurus",
                    "feet, hands, or tail are hidden enough to block count review",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V13, V14, V15, V16, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
