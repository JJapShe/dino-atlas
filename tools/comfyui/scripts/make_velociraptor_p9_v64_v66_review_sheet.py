import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

V63 = ASSETS / "velociraptor-mongoliensis-imagegen-v63-source-candidate.png"
V64 = ASSETS / "velociraptor-mongoliensis-imagegen-v64-source-candidate.png"
V65 = ASSETS / "velociraptor-mongoliensis-imagegen-v65-source-candidate.png"
V66 = ASSETS / "velociraptor-mongoliensis-imagegen-v66-source-candidate.png"
V56 = ASSETS / "velociraptor-mongoliensis-imagegen-v56-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p9-v64-v66-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p9-v64-v66-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p9_v64_v66_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, max_chars=58, max_lines=3):
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
    panel = Image.new("RGB", (size[0], size[1] + 94), (245, 243, 236))
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
        tile(V63, "current v63 selected candidate", "Keep first: best current balance of dark speckled plumage, toothed snout, compact arms, and count-level foot cue.", accent=(38, 116, 76)),
        tile(V65, "v65 P9 review hold", "Best new non-bird head and long-tail silhouette. Keep as foot-local source candidate; sickle claw is still too large to promote.", accent=(146, 99, 45)),
        tile(V64, "v64 P9 hook/wing reject", "Strong color and teeth, but the near sickle claw overbuilds into a large hook and the forelimb reads wing-fan-like.", accent=(155, 66, 54)),
        tile(V66, "v66 P9 hand/claw reject", "Distinct red-ground color scene, but forelimb fingers become long hands and the raised claws remain oversized.", accent=(155, 66, 54)),
        tile(V56, "previous v56 safety hold", "Older restrained comparison for modest toe cue; less gallery-distinct plumage than v63 and v65.", accent=(95, 98, 112)),
        tile(FOOT_GUIDE, "foot topology guide", "Target: two grounded walking toes plus one attached raised second-toe sickle claw, modest scale.", accent=(68, 92, 140)),
        tile(IDENTITY_GUIDE, "identity body-lock guide", "Target: toothed non-beak snout, folded feathered arms, dense plumage, stiff tail, two hind legs.", accent=(68, 92, 140)),
    ]
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v63", V63),
        ("P9 v65 hold", V65),
        ("P9 v64 reject", V64),
        ("P9 v66 reject", V66),
        ("previous v56", V56),
        ("foot topology guide", FOOT_GUIDE),
        ("identity guide", IDENTITY_GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.08, 0.33, 0.53), (360, 210)),
        ("plumage color", (0.15, 0.16, 0.68, 0.65), (390, 210)),
        ("folded forelimb", (0.17, 0.31, 0.48, 0.78), (340, 210)),
        ("both feet", (0.18, 0.55, 0.84, 0.98), (410, 210)),
        ("near sickle toe", (0.15, 0.58, 0.52, 0.98), (340, 210)),
        ("tail stiffness", (0.50, 0.22, 1.00, 0.62), (410, 210)),
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
                "experiment": "p9_v64_v66_nonbird_head_and_plumage_variation",
                "currentPrimary": relative(V63),
                "reviewHolds": [relative(V65), relative(V56)],
                "rejectReferences": [relative(V64), relative(V66)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v63_primary_add_v65_as_review_hold_reject_v64_v66",
                "reason": (
                    "The P9 prompt-only pass improves species-level dark speckled and rust facial color variation, but none of v64-v66 beats v63 across the full identity gate. "
                    "V65 has the best new non-bird toothed head and long stiff tail silhouette, but its raised sickle claw still reads too large for promotion. "
                    "V64 overbuilds the claw and risks wing-fan forelimbs; v66 has useful color but long hand-like forelimb fingers and oversized raised claws."
                ),
                "nextRoute": (
                    "Use v65 only as a visual review hold and possible foot-local i2i source. The primary route remains v63 plus foot topology guide, with strict rejection for modern-bird head, wing-fan arms, detached or giant hook claws, and crowded toe counts."
                ),
                "rejectIfPromoting": [
                    "head reads as a modern bird, hawk, owl, rooster, or toothless beak",
                    "folded forelimbs become broad spread wings or long human-like hands",
                    "sickle claw reads as a detached crescent, giant hook, black talon, or eagle talon",
                    "feet do not show two grounded walking toes plus one attached raised second toe",
                    "toe count becomes crowded, duplicated, or mammal-like",
                    "tail is cropped, duplicated, soft, or hidden",
                    "plumage collapses back to plain samey brown without species-level distinction",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [V63, V64, V65, V66, V56, FOOT_GUIDE, IDENTITY_GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
