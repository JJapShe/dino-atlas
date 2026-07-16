import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-imagegen-v56-source-candidate.png"
PREVIOUS = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
V57 = ASSETS / "velociraptor-mongoliensis-imagegen-v57-source-candidate.png"
V58 = ASSETS / "velociraptor-mongoliensis-imagegen-v58-source-candidate.png"
V59 = ASSETS / "velociraptor-mongoliensis-imagegen-v59-source-candidate.png"
V54 = ASSETS / "velociraptor-mongoliensis-imagegen-v54-source-candidate.png"
V55 = ASSETS / "velociraptor-mongoliensis-imagegen-v55-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p7-v57-v59-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p7-v57-v59-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p7_v57_v59_review.json"

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


def tile(path, title, note, size=(430, 242), accent=(132, 61, 43)):
    panel = Image.new("RGB", (size[0], size[1] + 78), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, size[1], size[0], size[1] + 6), fill=accent)
    draw.text((8, size[1] + 12), title[:70], fill=accent, font=FONT)
    draw_wrapped(draw, (8, size[1] + 35), note)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v56 count-level pass", "Still best balance: toothed non-beak head, feathers, folded arms, modest attached toe cue.", accent=(38, 116, 76)),
        tile(V57, "v57 curled-claw review hold", "Good body and clearer feet, but both raised claws trend curled and hook-like.", accent=(146, 99, 45)),
        tile(V58, "v58 overbuilt-foot reject", "Head/body useful, but feet become crowded with oversized claws and unclear toe count.", accent=(152, 66, 58)),
        tile(V59, "v59 head hold, hook-risk feet", "Good toothed head and silhouette, but raised claws are too hook-like for promotion.", accent=(146, 99, 45)),
        tile(PREVIOUS, "previous v9 hold", "Older compromise for feathered body and restrained raised-toe cue.", accent=(95, 98, 112)),
        tile(V54, "v54 clear-claw hold", "Clearer raised claws, but scale remains slightly dramatic.", accent=(95, 98, 112)),
        tile(V55, "v55 clear-claw hold", "Visible raised toes, less balanced head/hand and claw scale than v56.", accent=(95, 98, 112)),
        tile(FOOT_GUIDE, "foot topology guide", "Target: two grounded walking toes plus one attached raised second-toe sickle claw.", accent=(68, 92, 140)),
        tile(IDENTITY_GUIDE, "identity body-lock guide", "Target: toothed snout, folded feathered arms, feathered body, stiff tail, feet together.", accent=(68, 92, 140)),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v56", CURRENT),
        ("v57 curled-claw hold", V57),
        ("v58 overbuilt-foot reject", V58),
        ("v59 hook-risk hold", V59),
        ("previous v9", PREVIOUS),
        ("v54 clear-claw hold", V54),
        ("v55 clear-claw hold", V55),
        ("foot topology guide", FOOT_GUIDE),
        ("identity guide", IDENTITY_GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.10, 0.35, 0.52), (360, 210)),
        ("folded forelimb", (0.16, 0.34, 0.48, 0.76), (340, 210)),
        ("both feet", (0.24, 0.56, 0.82, 0.98), (400, 210)),
        ("near sickle toe", (0.23, 0.58, 0.56, 0.98), (340, 210)),
        ("far foot", (0.45, 0.56, 0.82, 0.98), (340, 210)),
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
                "experiment": "p7_v57_v59_modest_attached_sickle_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(CURRENT),
                "reviewHolds": [relative(V57), relative(V59), relative(PREVIOUS), relative(V54), relative(V55)],
                "rejectReferences": [relative(V58)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v56_first_add_v57_v59_holds_and_v58_reject",
                "reason": (
                    "V56 remains the safest current app-first candidate because the new P7 prompts do not beat its balance of toothed non-beak head, feathered dromaeosaur body, folded forelimbs, stiff tail, and modest attached raised-toe cues. "
                    "V57 has a useful body and clearer foot area but both raised claws trend curled and hook-like. V58 is rejected because the feet become crowded, overbuilt, and unclear in toe count. V59 has a good toothed head and side silhouette but the raised claws again become too hook-like for promotion."
                ),
                "nextRoute": (
                    "Keep v56 as the positive smoke-test seed. Use v57/v59 as review holds for head/body and foot visibility, and use v58 as a reject reference for overbuilt feet. "
                    "The next useful attempt should be localized foot i2i or a dromaeosaur-specific LoRA/ControlNet route that preserves v56 while making the near foot read as two grounded walking toes plus one small attached raised second toe."
                ),
                "rejectIfPromoting": [
                    "head reads as a modern bird, hawk, owl, parrot, or toothless beak",
                    "forelimbs become broad spread wings instead of folded feathered arms",
                    "sickle claw reads as a detached crescent, giant hook, black talon, or eagle talon",
                    "feet do not show two walking toes plus one attached raised second toe",
                    "toe count becomes crowded, duplicated, or mammal-like",
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
    required = [CURRENT, PREVIOUS, V57, V58, V59, V54, V55, FOOT_GUIDE, IDENTITY_GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
