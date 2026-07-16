import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
V50 = ASSETS / "velociraptor-mongoliensis-imagegen-v50-source-candidate.png"
V51 = ASSETS / "velociraptor-mongoliensis-imagegen-v51-source-candidate.png"
V52 = ASSETS / "velociraptor-mongoliensis-imagegen-v52-source-candidate.png"
V53 = ASSETS / "velociraptor-mongoliensis-imagegen-v53-source-candidate.png"
V54 = ASSETS / "velociraptor-mongoliensis-imagegen-v54-source-candidate.png"
V55 = ASSETS / "velociraptor-mongoliensis-imagegen-v55-source-candidate.png"
V56 = ASSETS / "velociraptor-mongoliensis-imagegen-v56-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p6-v51-v56-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p6-v51-v56-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p6_v51_v56_review.json"

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
        tile(CURRENT, "current v9 count-level pass", "Best old compromise, but head/forelimb and exact foot topology remain soft."),
        tile(V56, "v56 modest-toe candidate", "Best P6 balance: attached raised toes are visible without returning to black hook drift."),
        tile(V54, "v54 clear-claw review hold", "Good head/body/foot visibility, but the claws are still slightly dramatic."),
        tile(V55, "v55 clear-claw review hold", "Visible raised toes, but head/hand and claw size remain less balanced than v56."),
        tile(V53, "v53 subtle-toe review hold", "Best small-claw scale, but the raised second-toe cue becomes too faint."),
        tile(V51, "v51 modest-claw review hold", "Good small-claw direction, but near foot and forelimb detail are softer than v53."),
        tile(V52, "v52 hook-risk hold", "Good toothy head/body, but the sickle claws return to large black hook shapes."),
        tile(V50, "previous v50 hook-risk hold", "Best P5 head/body/tail balance, but both raised claws are too large and dark."),
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
        ("v56 modest-toe candidate", V56),
        ("v54 clear-claw hold", V54),
        ("v55 clear-claw hold", V55),
        ("v53 subtle-toe hold", V53),
        ("v51 modest-claw hold", V51),
        ("v52 hook-risk hold", V52),
        ("previous v50 hold", V50),
        ("foot topology guide", FOOT_GUIDE),
        ("identity guide", IDENTITY_GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.12, 0.34, 0.52), (360, 210)),
        ("folded forelimb", (0.16, 0.34, 0.48, 0.76), (340, 210)),
        ("both feet", (0.24, 0.56, 0.78, 0.96), (400, 210)),
        ("near sickle toe", (0.25, 0.60, 0.55, 0.96), (340, 210)),
        ("far foot", (0.46, 0.56, 0.78, 0.96), (340, 210)),
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
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "p6_v51_v56_modest_sickle_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(V56),
                "comparisonReviewHolds": [relative(V54), relative(V55), relative(V53), relative(V51), relative(V52), relative(V50)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v56_to_count_level_pass_pending_human_review",
                "reason": (
                    "V56 is the best P6 balance because it reduces the oversized black-hook failure while preserving a full-body feathered dromaeosaur, a toothy non-beak head, folded forelimbs, a full stiff tail, and two visible feet. "
                    "It makes the attached raised second toes visible without the black-taloned v50/v52 look or the too-faint v53 cue. It is not final: the hand/forelimb crop still risks wing-hand ambiguity, and exact two walking toes plus raised second-toe topology remains count-level rather than reference-final. "
                    "V54 and v55 are useful clear-claw holds but the claws are still more dramatic than v56. V51/v53 are subtle-toe holds, while v52 and v50 remain hook-risk holds."
                ),
                "nextRoute": (
                    "Use v56 as the next app-scale smoke-test source and LoRA review hold/seed candidate only after crop review. "
                    "Future localized i2i should preserve v56 head/body/tail while sharpening the near foot into two grounded walking toes plus one small attached raised second toe."
                ),
                "rejectIfPromoting": [
                    "head becomes bird-beaked, hawk-like, chicken-like, or toothless",
                    "forelimbs become broad spread wings instead of folded feathered arms",
                    "sickle claw reads as detached crescent, giant hook, black talon, or eagle talon",
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
    required = [CURRENT, V50, V51, V52, V53, V54, V55, V56, FOOT_GUIDE, IDENTITY_GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
