import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSETS / "velociraptor-small-sickle-crops-v9.png"
V35 = ASSETS / "velociraptor-mongoliensis-imagegen-v35-source-candidate.png"
V36 = ASSETS / "velociraptor-mongoliensis-imagegen-v36-source-candidate.png"
V37 = ASSETS / "velociraptor-mongoliensis-imagegen-v37-source-candidate.png"
V38 = ASSETS / "velociraptor-mongoliensis-imagegen-v38-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p1-v36-v38-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p1-v36-v38-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p1_v36_v38_review.json"

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
        tile(CURRENT, "current v9 count-level pass", "Best current representative: toothed snout, folded forelimbs, stiff tail, and smaller sickle cue."),
        tile(V38, "v38 modest sickle source hold", "Best new attached near-foot sickle cue, but hand hooks and exact toe topology need crop review."),
        tile(V37, "v37 large-hook rejection", "Good head/body silhouette, but both sickle claws are still too large and decorative."),
        tile(V36, "v36 oversized-claw rejection", "Toothed and feathered, but the raised claws overcorrect into giant hooks."),
        tile(V35, "v35 previous source hold", "Keeps small feathered dromaeosaur identity but sickle claw is not final-proof on both feet."),
        tile(FOOT_GUIDE, "foot topology guide", "Project-owned target for two walking toes plus one attached raised second-toe sickle claw."),
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
        ("v38 source hold", V38),
        ("v37 large-hook reject", V37),
        ("v36 oversized reject", V36),
        ("v35 source hold", V35),
        ("v9 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.12, 0.33, 0.50), (360, 210)),
        ("folded forelimb", (0.20, 0.35, 0.43, 0.72), (300, 210)),
        ("both feet", (0.30, 0.58, 0.70, 0.94), (360, 210)),
        ("near sickle toe", (0.30, 0.62, 0.51, 0.94), (300, 210)),
        ("far foot/tail base", (0.48, 0.55, 0.74, 0.92), (320, 210)),
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
                "experiment": "p1_v36_v38_modest_sickle_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V38),
                "comparisonRejects": [relative(V36), relative(V37)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "review_hold",
                "reason": (
                    "V38 is the best new prompt-only source for a subtler attached near-foot sickle cue while keeping the toothed snout, feathered body, folded forelimb, and full tail. "
                    "Keep v9 first because v38 still needs crop proof for exact raised second-toe topology and the hand claws can read too hook-like. V36 and v37 are overcorrection references with oversized sickle claws."
                ),
                "rejectIfPromoting": [
                    "sickle claw reads as a detached crescent or giant hook",
                    "feet do not show two walking toes plus one attached raised second toe",
                    "head becomes bird-beaked, toothless, rooster-like, or hawk-like",
                    "forelimbs become spread wings or oversized dangling claws",
                    "tail is cropped, duplicated, soft, or hidden",
                    "extra legs, one-legged pose, hidden feet, text, or watermark"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V35, V36, V37, V38, FOOT_GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
