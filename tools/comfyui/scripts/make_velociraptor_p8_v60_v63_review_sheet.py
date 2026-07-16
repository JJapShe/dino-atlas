import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-imagegen-v56-source-candidate.png"
V60 = ASSETS / "velociraptor-mongoliensis-imagegen-v60-source-candidate.png"
V61 = ASSETS / "velociraptor-mongoliensis-imagegen-v61-source-candidate.png"
V62 = ASSETS / "velociraptor-mongoliensis-imagegen-v62-source-candidate.png"
V63 = ASSETS / "velociraptor-mongoliensis-imagegen-v63-source-candidate.png"
PREVIOUS = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
IDENTITY_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "velociraptor-p8-v60-v63-review-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-p8-v60-v63-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_p8_v60_v63_review.json"

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
        tile(V63, "v63 selected plumage-color candidate", "Best P8 color/head/arm balance: dark speckled plumage, toothed snout, compact arms; toe gate still count-level.", accent=(38, 116, 76)),
        tile(CURRENT, "previous v56 modest-toe pass", "Safer older brown candidate; kept below v63 because color is less distinct and forelimb/texture are softer.", accent=(95, 98, 112)),
        tile(V60, "v60 cool-color hook-risk hold", "Good slate color and toothed head, but both feet overbuild into large hook claws.", accent=(146, 99, 45)),
        tile(V61, "v61 rust-color wing-risk hold", "Useful rust and barred tail color, but folded forelimbs read too wing-fan-like and the claw is large.", accent=(146, 99, 45)),
        tile(V62, "v62 dark-color hook-risk hold", "Strong dark speckled plumage and head, but the feet overcorrect into dramatic hook claws.", accent=(146, 99, 45)),
        tile(PREVIOUS, "previous v9 hold", "Older small-sickle comparison for restrained toe cue and feathered body.", accent=(95, 98, 112)),
        tile(FOOT_GUIDE, "foot topology guide", "Target: two grounded walking toes plus one attached raised second-toe sickle claw.", accent=(68, 92, 140)),
        tile(IDENTITY_GUIDE, "identity body-lock guide", "Target: toothed snout, folded feathered arms, feathered body, stiff tail, and attached raised toe.", accent=(68, 92, 140)),
    ]
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("selected v63", V63),
        ("previous v56", CURRENT),
        ("v60 hook-risk hold", V60),
        ("v61 wing-risk hold", V61),
        ("v62 hook-risk hold", V62),
        ("previous v9", PREVIOUS),
        ("foot topology guide", FOOT_GUIDE),
        ("identity guide", IDENTITY_GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (430, 210)),
        ("head/snout", (0.00, 0.08, 0.34, 0.53), (360, 210)),
        ("plumage color", (0.15, 0.16, 0.68, 0.65), (390, 210)),
        ("folded forelimb", (0.18, 0.32, 0.48, 0.77), (340, 210)),
        ("both feet", (0.20, 0.55, 0.83, 0.98), (410, 210)),
        ("near sickle toe", (0.18, 0.58, 0.53, 0.98), (340, 210)),
        ("tail stiffness", (0.50, 0.24, 1.00, 0.61), (410, 210)),
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
                "experiment": "p8_v60_v63_plumage_color_and_sickle_gate",
                "previousPrimary": relative(CURRENT),
                "selectedCandidate": relative(V63),
                "reviewHolds": [relative(V60), relative(V61), relative(V62), relative(CURRENT), relative(PREVIOUS)],
                "rejectReferences": [],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v63_for_distinct_plumage_color_with_count_level_toe_risk",
                "reason": (
                    "V63 is the best P8 response to the color-variation goal. It gives Velociraptor a more distinct dark charcoal, umber, pale-speckled, and rust-face plumage pattern while preserving a narrow toothed non-beak snout, compact folded forelimbs, two hind legs, and a long stiff tail. "
                    "Its sickle-toe anatomy is still count-level rather than final, but it is not more unsafe than v56 at app scale. V60 and v62 are kept as hook-risk color holds, and v61 is kept as a wing-risk color hold."
                ),
                "nextRoute": (
                    "Use v63 as the current app-first candidate and positive smoke-test seed for plumage color. The next useful route should be localized foot i2i or foot-topology ControlNet over v63 to keep the new color while reducing any hook-claw exaggeration."
                ),
                "rejectIfPromoting": [
                    "head reads as a modern bird, hawk, owl, rooster, or toothless beak",
                    "forelimbs become broad spread wings instead of compact folded feathered arms",
                    "sickle claw reads as a detached crescent, giant hook, black talon, or eagle talon",
                    "feet do not show two walking toes plus one attached raised second toe",
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
    required = [CURRENT, V60, V61, V62, V63, PREVIOUS, FOOT_GUIDE, IDENTITY_GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
