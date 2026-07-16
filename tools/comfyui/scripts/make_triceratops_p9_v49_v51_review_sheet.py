import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-imagegen-v43-source-candidate.png"
V49 = ASSETS / "triceratops-horridus-imagegen-v49-source-candidate.png"
V50 = ASSETS / "triceratops-horridus-imagegen-v50-source-candidate.png"
V51 = ASSETS / "triceratops-horridus-imagegen-v51-source-candidate.png"
V41 = ASSETS / "triceratops-horridus-imagegen-v41-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p9-v49-v51-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p9-v49-v51-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p9_v49_v51_review.json"

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
    panel = Image.new("RGB", (size[0], size[1] + 82), (245, 243, 236))
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
        tile(V51, "v51 selected cool-color candidate", "Best P9 color separation while keeping three horns, skull frill, long tail, and toes.", accent=(38, 116, 76)),
        tile(CURRENT, "previous v43 first candidate", "Strong familiar Triceratops read but samey tan-gray color beside other taxa.", accent=(95, 98, 112)),
        tile(V49, "v49 dark-speckle review hold", "Good dark mottling and frill spots, but head/frill contrast is rougher than v51.", accent=(146, 99, 45)),
        tile(V50, "v50 rust-frill review hold", "Useful warm frill accent, but body color is less distinct than v51.", accent=(146, 99, 45)),
        tile(V41, "previous v41 low-body hold", "Older low-body anti-rhino comparison retained for body-shape review.", accent=(95, 98, 112)),
        tile(GUIDE, "skull-frill body-lock guide", "Control target for skull-attached frill, low long body, long tail, and non-hoofed toes.", accent=(68, 92, 140)),
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
        ("selected v51", V51),
        ("previous v43", CURRENT),
        ("v49 hold", V49),
        ("v50 hold", V50),
        ("previous v41", V41),
        ("body-lock guide", GUIDE),
    ]
    crops = [
        ("full body", (0.0, 0.04, 1.0, 0.92), (430, 210)),
        ("head/frill/horns", (0.00, 0.08, 0.42, 0.66), (380, 210)),
        ("frill color", (0.12, 0.05, 0.43, 0.55), (330, 210)),
        ("body pattern", (0.22, 0.12, 0.78, 0.72), (390, 210)),
        ("feet/toes", (0.10, 0.58, 0.72, 0.96), (390, 210)),
        ("tail length", (0.58, 0.24, 1.0, 0.72), (360, 210)),
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
                "experiment": "p9_v49_v51_color_frill_pattern_review",
                "previousPrimary": relative(CURRENT),
                "selectedCandidate": relative(V51),
                "reviewHolds": [relative(V49), relative(V50), relative(CURRENT), relative(V41)],
                "rejectReferences": [],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v51_for_cool_color_pattern_and_frill_identity",
                "reason": (
                    "V51 is the best P9 balance between color differentiation and Triceratops identity. It adds a cooler blue-gray body with pale mottling, keeps the two brow horns, nasal horn, closed beak, "
                    "skull-attached frill, long tail, four dinosaur limbs, and separated non-hoofed toes. V49 and v50 are useful review holds for dark speckle and rust-frill variants but do not beat v51 overall."
                ),
                "nextRoute": (
                    "Use v51 as the current app-first color-pattern smoke-test seed. Future passes should preserve its cool non-sandy palette while improving exact toe anatomy, low elongated anti-rhino torso, "
                    "and frill/skull proportions through body-lock or localized foot/frill i2i."
                ),
                "rejectIfPromoting": [
                    "torso, shoulder mass, or feet read as rhinoceros-like",
                    "body becomes a round mammal barrel rather than low elongated ceratopsian form",
                    "frill attaches to shoulders, back, or torso instead of skull",
                    "mouth opens or teeth appear",
                    "horn count is not exactly two brow horns plus one nasal horn",
                    "feet become hoof-like or hide toe separation",
                    "tail is cropped, hidden, or tiny",
                    "color collapses back to the same sandy-brown palette as other taxa",
                    "frill color becomes a neon or ornamental fantasy fan",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V49, V50, V51, V41, GUIDE]
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
