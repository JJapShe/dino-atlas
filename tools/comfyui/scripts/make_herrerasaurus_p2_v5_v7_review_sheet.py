import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_saurischian_herrerasaurus" / "review"

CURRENT = ASSETS / "herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png"
V4 = ASSETS / "herrerasaurus-ischigualastensis-imagegen-v4-source-candidate.png"
V5 = ASSETS / "herrerasaurus-ischigualastensis-imagegen-v5-source-candidate.png"
V6 = ASSETS / "herrerasaurus-ischigualastensis-imagegen-v6-source-candidate.png"
V7 = ASSETS / "herrerasaurus-ischigualastensis-imagegen-v7-source-candidate.png"
GUIDE = ASSETS / "herrerasaurus-ischigualastensis-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "herrerasaurus-p2-v5-v7-review-sheet.png"
CROP_SHEET = ASSETS / "herrerasaurus-p2-v5-v7-crops.png"
REVIEW_JSON = REVIEW_ROOT / "herrerasaurus_p2_v5_v7_review.json"

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
        tile(CURRENT, "current v2 count-level pass", "Safest compact-hand primary: good body, head, two legs, and tail; hand detail still soft."),
        tile(V4, "v4 previous review hold", "Good scene and full body, but hand count can read as too many equal fingers."),
        tile(V5, "v5 long-hook reject", "Strong body silhouette, but visible fingers become long dangling hooks."),
        tile(V6, "v6 compact-hand p2 hold", "Best P2 candidate: folded compact hands, closed head, full tail, and two grounded hind legs."),
        tile(V7, "v7 visible-hand reject", "Hands are easy to see but become too long and multi-fingered for positive training."),
        tile(GUIDE, "body-lock guide", "Project-owned target for narrow head, compact folded hands, two hind legs, and full tail."),
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
        ("v4 previous hold", V4),
        ("v5 long-hook reject", V5),
        ("v6 compact-hand hold", V6),
        ("v7 visible-hand reject", V7),
    ]
    crops = [
        ("full body", (0.00, 0.07, 1.00, 0.92), (430, 210)),
        ("head", (0.00, 0.12, 0.31, 0.50), (360, 210)),
        ("forelimb/hand", (0.17, 0.35, 0.42, 0.74), (320, 210)),
        ("hand digits", (0.20, 0.42, 0.36, 0.76), (280, 210)),
        ("hind legs/feet", (0.34, 0.52, 0.70, 0.95), (360, 210)),
        ("tail", (0.52, 0.25, 1.00, 0.62), (380, 210)),
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
                "taxonId": "herrerasaurus-ischigualastensis",
                "experiment": "p2_v5_v7_compact_hand_candidates",
                "currentPrimary": relative(CURRENT),
                "candidateDecisions": [
                    {
                        "source": relative(V5),
                        "decision": "reject_reference",
                        "reason": "Good light early-saurischian body silhouette, but the visible hands become long dangling hook claws.",
                    },
                    {
                        "source": relative(V6),
                        "decision": "review_hold",
                        "reason": "Best P2 candidate: compact folded hands, closed narrow head, full tail, and two grounded hind legs; keep below v2 because exact three-main-digit topology is still soft.",
                    },
                    {
                        "source": relative(V7),
                        "decision": "reject_reference",
                        "reason": "Hand visibility improves, but the fingers are too long, too numerous/equal, and too large for a positive Herrerasaurus seed.",
                    },
                ],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_primary",
                "reason": (
                    "V6 is the strongest P2 review hold, but the current v2 primary remains safer because it avoids long hook-hand drift. "
                    "V5 and v7 are strict failure references for hand exaggeration."
                ),
                "rejectIfPromoting": [
                    "visible hand reads as four or five equal long fingers",
                    "forelimbs become long dangling hook claws or oversized Allosaurus-like hands",
                    "arms shrink into tiny Tyrannosaurus proportions",
                    "body becomes bulky Allosaurus or Tyrannosaurus-like",
                    "extra legs, tail duplication, or hidden feet block count review",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V4, V5, V6, V7, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
