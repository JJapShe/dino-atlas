import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-imagegen-v51-source-candidate.png"
V52 = ASSETS / "triceratops-horridus-imagegen-v52-source-candidate.png"
V53 = ASSETS / "triceratops-horridus-imagegen-v53-source-candidate.png"
V54 = ASSETS / "triceratops-horridus-imagegen-v54-source-candidate.png"
V43 = ASSETS / "triceratops-horridus-imagegen-v43-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p10-v52-v54-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p10-v52-v54-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p10_v52_v54_review.json"

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
    panel = Image.new("RGB", (size[0], size[1] + 86), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, size[1], size[0], size[1] + 6), fill=accent)
    draw.text((8, size[1] + 12), title[:72], fill=accent, font=FONT)
    draw_wrapped(draw, (8, size[1] + 36), note)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "v51 current primary color seed", "Current cool-color smoke-test seed; remains first until lower body and frill gate improves.", accent=(38, 116, 76)),
        tile(V52, "v52 cool blue mottled hold", "Best cool body mottling and toe visibility, but rounded high torso still carries rhino-body risk.", accent=(146, 99, 45)),
        tile(V53, "v53 teal/rust frill hold", "Strongest palette variation and frill accent, but body is too barrel-like for promotion.", accent=(146, 99, 45)),
        tile(V54, "v54 dark freckle hold", "Strong dark speckle contrast; head/frill and body mass still need stricter body-lock review.", accent=(146, 99, 45)),
        tile(V43, "previous anti-rhino comparison", "Older familiar Triceratops read kept for lower-body comparison against the colorful holds.", accent=(95, 98, 112)),
        tile(GUIDE, "skull-frill body-lock guide", "Use this control reference before promoting any colorful variant into positive training.", accent=(68, 92, 140)),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v51", CURRENT),
        ("v52 hold", V52),
        ("v53 hold", V53),
        ("v54 hold", V54),
        ("previous v43", V43),
        ("body-lock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.93), (430, 210)),
        ("head/frill/horns", (0.48, 0.08, 0.94, 0.68), (380, 210)),
        ("frill attachment", (0.42, 0.08, 0.73, 0.66), (330, 210)),
        ("body mass", (0.17, 0.16, 0.66, 0.72), (390, 210)),
        ("feet/toes", (0.20, 0.55, 0.82, 0.96), (390, 210)),
        ("tail", (0.00, 0.22, 0.38, 0.68), (360, 210)),
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
                "taxonId": "triceratops-horridus",
                "experiment": "p10_v52_v54_color_variation_bodylock_review",
                "currentPrimary": relative(CURRENT),
                "reviewHolds": [relative(V52), relative(V53), relative(V54), relative(V43)],
                "rejectReferences": [],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v51_primary_add_v52_v54_as_color_pattern_holds",
                "reason": (
                    "V52-v54 improve species-level color and pattern separation with cool mottling, teal/rust frill accents, and dark freckling. "
                    "None should replace v51 yet because the torso remains high or rounded enough to risk rhinoceros-like body shortcuts, and the skull-frill attachment still needs stricter body-lock review."
                ),
                "nextRoute": (
                    "Use v52-v54 as color-reference holds only. The next Triceratops pass should use the skull-frill body-lock guide or low-denoise i2i over v51/v52, preserving cool palettes while lowering the torso, separating non-hoofed toes, and proving that the frill is attached to the skull rather than the shoulder."
                ),
                "rejectIfPromoting": [
                    "torso or shoulder mass reads as rhinoceros-like",
                    "body becomes a round mammal barrel rather than low elongated ceratopsian form",
                    "frill attaches to shoulders, back, or torso instead of skull",
                    "horn count is not exactly two brow horns plus one nasal horn",
                    "feet become hoof-like or toe separation is hidden",
                    "tail is cropped, hidden, or tiny",
                    "color/pattern looks good but masks anatomical failure",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in [CURRENT, V52, V53, V54, V43, GUIDE]:
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
