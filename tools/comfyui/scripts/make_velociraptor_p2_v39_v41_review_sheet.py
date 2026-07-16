import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSETS / "velociraptor-small-sickle-crops-v9.png"
V38 = ASSETS / "velociraptor-mongoliensis-imagegen-v38-source-candidate.png"
V39 = ASSETS / "velociraptor-mongoliensis-imagegen-v39-source-candidate.png"
V40 = ASSETS / "velociraptor-mongoliensis-imagegen-v40-source-candidate.png"
V41 = ASSETS / "velociraptor-mongoliensis-imagegen-v41-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p2-v39-v41-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p2-v39-v41-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p2_v39_v41_review.json"

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
        tile(CURRENT, "current v9 count-level pass", "Best current balance: toothed snout, folded forelimbs, stiff tail, and small sickle cue."),
        tile(V39, "v39 closed-snout review hold", "Best fresh whole-body balance; closed toothed snout and plumage, but foot topology still needs crop proof."),
        tile(V40, "v40 open-mouth claw reject", "Both raised claws read clearly, but mouth and hook claws are too dramatic for representative promotion."),
        tile(V41, "v41 front-hook risk hold", "Good plumage and foot visibility, but the near raised claw can still read as an oversized front hook."),
        tile(V38, "v38 prior modest-sickle hold", "Prior best source for attached near-foot sickle cue; still risky in hand hooks and exact toe topology."),
        tile(FOOT_GUIDE, "foot topology guide", "Project-owned target: two grounded walking toes plus one attached raised second-toe sickle claw."),
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
        ("current v9", CURRENT),
        ("v39 hold", V39),
        ("v40 hook reject", V40),
        ("v41 front-hook risk", V41),
        ("v38 prior hold", V38),
        ("v9 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.12, 0.33, 0.50), (360, 210)),
        ("folded forelimb", (0.18, 0.34, 0.45, 0.72), (330, 210)),
        ("both feet", (0.28, 0.56, 0.70, 0.95), (380, 210)),
        ("near sickle toe", (0.30, 0.61, 0.51, 0.95), (320, 210)),
        ("far foot", (0.46, 0.56, 0.70, 0.95), (320, 210)),
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
                "experiment": "p2_v39_v41_closed_scout_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V39),
                "additionalReviewHold": relative(V41),
                "selectedRejectReferences": [relative(V40)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v9",
                "reason": (
                    "V39 is the best fresh whole-body balance because it keeps a closed toothed non-beak snout, dense feathers, folded forelimbs, and a restrained raised claw cue. "
                    "It still does not prove two grounded walking toes plus one attached raised second-toe sickle claw on both feet. V41 is useful as a foot-visibility hold but the near claw risks reading as an oversized front hook. "
                    "V40 is a reject reference because the open mouth and paired hook claws are too dramatic. Keep v9 first until head identity and exact foot topology pass together."
                ),
                "rejectIfPromoting": [
                    "sickle claw reads as a detached crescent or giant hook",
                    "feet do not show two walking toes plus one attached raised second toe",
                    "head becomes bird-beaked, toothless, rooster-like, or hawk-like",
                    "mouth/eye expression becomes too monster-like for a representative atlas image",
                    "forelimbs become spread wings or oversized dangling claws",
                    "tail is cropped, duplicated, soft, or hidden",
                    "extra legs, one-legged pose, hidden feet, text, or watermark",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V38, V39, V40, V41, FOOT_GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
