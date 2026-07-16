import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

V63 = ASSETS / "velociraptor-mongoliensis-imagegen-v63-source-candidate.png"
V67 = ASSETS / "velociraptor-mongoliensis-imagegen-v67-source-candidate.png"
V68 = ASSETS / "velociraptor-mongoliensis-imagegen-v68-source-candidate.png"
V69 = ASSETS / "velociraptor-mongoliensis-imagegen-v69-source-candidate.png"
V65 = ASSETS / "velociraptor-mongoliensis-imagegen-v65-source-candidate.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p10-v67-v69-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p10-v67-v69-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p10_v67_v69_review.json"

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
        tile(V63, "current v63 primary", "Keep first: best current balance of dark speckled plumage, toothed snout, compact arms, and count-level foot cue.", accent=(38, 116, 76)),
        tile(V68, "v68 P10 best hold", "Best P10 balance of non-bird head, dark speckled plumage, folded arms, tail bands, and less-overbuilt feet.", accent=(146, 99, 45)),
        tile(V69, "v69 P10 color hold", "Stable color and body read, but near raised claw still grows into a large hook-like talon.", accent=(146, 99, 45)),
        tile(V67, "v67 P10 wing/hook risk", "Useful head and plumage, but forelimb reads wing-fan-like and both sickle claws become large hooks.", accent=(155, 66, 54)),
        tile(V65, "previous v65 hold", "Prior useful head/color hold; still risky because raised claw is too large for promotion.", accent=(95, 98, 112)),
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
        ("P10 v68 hold", V68),
        ("P10 v69 hold", V69),
        ("P10 v67 risk", V67),
        ("previous v65", V65),
        ("foot guide", FOOT_GUIDE),
        ("identity guide", IDENTITY_GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.08, 0.34, 0.54), (360, 210)),
        ("plumage color", (0.15, 0.15, 0.70, 0.66), (390, 210)),
        ("folded forelimb", (0.18, 0.28, 0.50, 0.78), (340, 210)),
        ("both feet", (0.16, 0.54, 0.84, 0.98), (410, 210)),
        ("near sickle toe", (0.14, 0.58, 0.54, 0.98), (340, 210)),
        ("tail stiffness", (0.50, 0.20, 1.00, 0.62), (410, 210)),
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
                "experiment": "p10_v67_v69_color_head_foot_review",
                "currentPrimary": relative(V63),
                "reviewHolds": [relative(V68), relative(V69), relative(V65)],
                "rejectReferences": [relative(V67)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v63_primary_add_v68_as_best_color_head_hold",
                "reason": (
                    "V67-v69 keep the useful dark speckled plumage, rust facial mask, toothed non-beak head, and long stiff tail direction. "
                    "V68 is the best P10 hold because its folded arms and head read are stable and its feet are less overbuilt than v67/v69. "
                    "No P10 candidate replaces v63 because the raised second-toe sickle claws still read too large or hook-like at crop scale."
                ),
                "nextRoute": (
                    "Keep v63 primary. Use v68 as a color/head reference hold only, then run foot-local i2i/control from v63 or v68 with the foot topology guide. "
                    "Do not promote a prettier render unless close crops prove two grounded walking toes plus one modest attached raised second-toe claw."
                ),
                "rejectIfPromoting": [
                    "head reads as modern bird, hawk, owl, rooster, or toothless beak",
                    "folded forelimbs become broad spread wings or long human-like hands",
                    "sickle claw reads as detached crescent, giant hook, black talon, or eagle talon",
                    "feet do not show two grounded walking toes plus one attached raised second toe",
                    "toe count becomes crowded, duplicated, or mammal-like",
                    "tail is cropped, duplicated, soft, or hidden",
                    "color improves but masks oversized hook-claw failure",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in [V63, V67, V68, V69, V65, FOOT_GUIDE, IDENTITY_GUIDE]:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
