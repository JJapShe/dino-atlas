import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSETS / "velociraptor-small-sickle-crops-v9.png"
V39 = ASSETS / "velociraptor-mongoliensis-imagegen-v39-source-candidate.png"
V42 = ASSETS / "velociraptor-mongoliensis-imagegen-v42-source-candidate.png"
V43 = ASSETS / "velociraptor-mongoliensis-imagegen-v43-source-candidate.png"
V44 = ASSETS / "velociraptor-mongoliensis-imagegen-v44-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p3-v42-v44-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p3-v42-v44-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p3_v42_v44_review.json"

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
        tile(CURRENT, "current v9 count-level pass", "Current first: non-beak snout, folded arms, stiff tail, and small sickle cue; still not final topology."),
        tile(V43, "v43 attached-claw hold", "Best P3 head/body balance and attached modest claw cue; folded arms risk reading wing-like in crop."),
        tile(V44, "v44 foot-visibility hold", "Most visible foot/sickle area; near claw can still read too large and hook-like."),
        tile(V42, "v42 hook-risk hold", "Good toothed head and full body, but raised claws can look oversized and talon-like."),
        tile(V39, "previous v39 closed-snout hold", "Prior best closed-snout source; foot topology still did not prove attached raised second toe."),
        tile(FOOT_GUIDE, "foot topology guide", "Target: two grounded walking toes plus one attached raised second-toe sickle claw."),
        tile(IDENTITY_GUIDE, "identity body-lock guide", "Target: toothed non-beak head, folded arms, feathered body, stiff tail, and feet together."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v9", CURRENT),
        ("v43 attached-claw hold", V43),
        ("v44 foot-visibility hold", V44),
        ("v42 hook-risk hold", V42),
        ("previous v39 hold", V39),
        ("v9 existing crop gate", CURRENT_CROPS),
        ("foot topology guide", FOOT_GUIDE),
        ("identity guide", IDENTITY_GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.12, 0.34, 0.52), (360, 210)),
        ("folded forelimb", (0.16, 0.34, 0.48, 0.76), (340, 210)),
        ("both feet", (0.26, 0.56, 0.76, 0.96), (400, 210)),
        ("near sickle toe", (0.26, 0.60, 0.54, 0.96), (340, 210)),
        ("far foot", (0.46, 0.56, 0.76, 0.96), (340, 210)),
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
        if path == CURRENT_CROPS:
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
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "p3_v42_v44_toothed_head_attached_sickle_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V43),
                "comparisonReviewHolds": [relative(V44), relative(V39)],
                "selectedRejectReferences": [relative(V42)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v9",
                "reason": (
                    "V43 is the best P3 source hold because it keeps a toothy non-beak head, small feathered dromaeosaur body, long stiff tail, and attached modest sickle-claw cue. "
                    "It stays below promotion because the folded forelimb can read too wing-like and the foot topology still does not prove both two walking toes plus one attached raised second toe. "
                    "V44 has the most reviewable foot area but the near claw can read as an oversized hook. V42 keeps good head identity but the raised claws are too talon-like."
                ),
                "nextRoute": (
                    "Use v43 as a copyright-safe source hold for localized foot/forelimb i2i or ControlNet. Do not promote until the crop gate proves a toothed non-beak head, compact folded arms, "
                    "two grounded walking toes plus one attached raised second-toe sickle claw, and no bird/wing/talon drift together."
                ),
                "rejectIfPromoting": [
                    "head becomes bird-beaked, toothless, hawk-like, or rooster-like",
                    "forelimbs become spread wings or read as modern bird wings",
                    "sickle claw reads as detached crescent, giant hook, or eagle talon",
                    "feet do not show two walking toes plus one attached raised second toe",
                    "body becomes naked movie raptor, ostrich-like, or oversized monster raptor",
                    "tail is cropped, duplicated, soft, or hidden",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V39, V42, V43, V44, FOOT_GUIDE, IDENTITY_GUIDE]
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
