import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-imagegen-v86-source-candidate.png"
V90 = ASSETS / "stegosaurus-stenops-imagegen-v90-source-candidate.png"
V91 = ASSETS / "stegosaurus-stenops-imagegen-v91-source-candidate.png"
V92 = ASSETS / "stegosaurus-stenops-imagegen-v92-source-candidate.png"
PREVIOUS = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p8-v90-v92-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p8-v90-v92-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p8_v90_v92_review.json"

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
        tile(V92, "v92 selected upward-V plate candidate", "Best P8 balance: distinct bony plates plus four visible upward V thagomizer spikes.", accent=(38, 116, 76)),
        tile(CURRENT, "previous v86 count-level pass", "Safer older tail/body comparison, but plates are too close to skin color and leather-like.", accent=(95, 98, 112)),
        tile(V90, "v90 bony-plate review hold", "Strong separate plate color/material, but one tail spike can read too lateral.", accent=(146, 99, 45)),
        tile(V91, "v91 double-V review hold", "Good plate material and upward tail direction, but the tail can read as three spikes.", accent=(146, 99, 45)),
        tile(PREVIOUS, "previous v6 hold", "Older positive comparison for natural body and countable thagomizer.", accent=(95, 98, 112)),
        tile(GUIDE, "plate topology guide", "Target: staggered broad plates and exactly four countable tail spikes.", accent=(68, 92, 140)),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("selected v92", V92),
        ("previous v86", CURRENT),
        ("v90 hold", V90),
        ("v91 hold", V91),
        ("previous v6", PREVIOUS),
        ("plate topology guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("head/neck", (0.00, 0.28, 0.24, 0.69), (320, 210)),
        ("plate material", (0.20, 0.05, 0.66, 0.55), (380, 210)),
        ("plate gaps", (0.30, 0.04, 0.74, 0.50), (380, 210)),
        ("feet/legs", (0.12, 0.55, 0.68, 0.96), (380, 210)),
        ("tail V spikes", (0.66, 0.15, 1.00, 0.76), (380, 210)),
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
                "taxonId": "stegosaurus-stenops",
                "experiment": "p8_v90_v92_bony_plate_upward_v_thagomizer",
                "previousPrimary": relative(CURRENT),
                "selectedCandidate": relative(V92),
                "reviewHolds": [relative(V90), relative(V91), relative(CURRENT), relative(PREVIOUS)],
                "rejectReferences": [],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "promote_v92_for_bony_plate_material_and_upward_v_tail_spikes",
                "reason": (
                    "V92 is the best P8 response to the user review: the dorsal plates read as separate rust-red and pale-bone rough structures rather than same-color skin, "
                    "and the thagomizer is closest to four countable spikes rising upward in paired V shapes. V90 and v91 remain review holds because their plate material is useful "
                    "but the tail-spike count or angle is less safe. V86 remains as the previous body/tail comparison seed."
                ),
                "nextRoute": (
                    "Use v92 as the current app-first candidate and smoke-test seed. Future Stegosaurus passes should preserve its bony plate material and upward V-shaped paired thagomizer "
                    "while improving exact staggered two-row plate bases and keeping all four feet natural."
                ),
                "rejectIfPromoting": [
                    "plates share the same leather-like color or texture as the skin",
                    "tail spikes lie horizontally along the ground instead of rising into paired V shapes",
                    "tail tip shows fewer or more than exactly four thagomizer spikes",
                    "tail spikes radiate as a starburst or compass-rose arrangement",
                    "plates become leaf-like, fin-like, scalloped, or a single connected sail",
                    "body drifts toward ankylosaur, turtle, crocodile, or generic low reptile",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V90, V91, V92, PREVIOUS, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
