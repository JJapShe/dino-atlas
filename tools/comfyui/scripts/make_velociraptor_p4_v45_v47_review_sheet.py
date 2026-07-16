import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSETS / "velociraptor-small-sickle-crops-v9.png"
V43 = ASSETS / "velociraptor-mongoliensis-imagegen-v43-source-candidate.png"
V45 = ASSETS / "velociraptor-mongoliensis-imagegen-v45-source-candidate.png"
V46 = ASSETS / "velociraptor-mongoliensis-imagegen-v46-source-candidate.png"
V47 = ASSETS / "velociraptor-mongoliensis-imagegen-v47-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p4-v45-v47-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p4-v45-v47-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p4_v45_v47_review.json"

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
        tile(CURRENT, "current v9 count-level pass", "Current first image: usable small sickle cue, but still not final foot topology."),
        tile(V47, "v47 best P4 review hold", "Best new balance: closed toothy non-beak head, folded arms, attached sickle cue; claw still large."),
        tile(V45, "v45 secondary P4 hold", "Good head and visible sickle cues, but forelimb crop can still read rounded and wing-like."),
        tile(V46, "v46 open-mouth diagnostic", "Useful foot visibility, but open mouth and paired hooks risk monster/talon drift."),
        tile(V43, "previous v43 P3 hold", "Earlier best head/body balance; kept for continuity against the new P4 route."),
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
        ("v47 best P4 hold", V47),
        ("v45 secondary P4 hold", V45),
        ("v46 diagnostic", V46),
        ("previous v43 hold", V43),
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
                "experiment": "p4_v45_v47_closed_head_attached_sickle_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V47),
                "comparisonReviewHolds": [relative(V45), relative(V43)],
                "selectedRejectReferences": [relative(V46)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v9",
                "reason": (
                    "V47 is the best P4 source hold because it keeps a closed toothy non-beak snout, feathered dromaeosaur body, folded forelimbs, long stiff tail, "
                    "and an attached near-foot sickle-claw cue. It still stays below promotion because the sickle claw is slightly too large and the far-foot topology "
                    "does not prove the full two-walking-toes plus one attached raised second-toe pattern. V45 is a useful secondary hold, while V46 is rejected as a "
                    "positive source because its open mouth and paired hook claws risk reinforcing monster-like/talon outputs."
                ),
                "nextRoute": (
                    "Use v47 and v45 only as review holds for localized foot/forelimb i2i or ControlNet. Use v46 as a reject reference when training or prompting against "
                    "open-mouth monster drift and oversized hook claws. Do not promote until the crop gate proves head identity, folded non-wing arms, exact foot topology, "
                    "two hind legs, and a single tail together."
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
    required = [CURRENT, CURRENT_CROPS, V43, V45, V46, V47, FOOT_GUIDE, IDENTITY_GUIDE]
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
