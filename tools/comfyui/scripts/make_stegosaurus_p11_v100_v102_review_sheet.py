import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-imagegen-v92-source-candidate.png"
V100 = ASSETS / "stegosaurus-stenops-imagegen-v100-source-candidate.png"
V101 = ASSETS / "stegosaurus-stenops-imagegen-v101-source-candidate.png"
V102 = ASSETS / "stegosaurus-stenops-imagegen-v102-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p11-v100-v102-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p11-v100-v102-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p11_v100_v102_review.json"

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
        tile(
            CURRENT,
            "current v92: keep first, not final",
            "Still the safest current app candidate: rough bony plates plus closest upward-V tail compromise.",
            accent=(38, 116, 76),
        ),
        tile(
            V100,
            "v100 hold: best new bony plates, tail overcounts",
            "Useful plate material and color contrast, but tail can read as five spikes/radial cluster.",
            accent=(146, 99, 45),
        ),
        tile(
            V101,
            "v101 reject: tail spear and undercount risk",
            "Good plate color, but tail continues into a straight point and the thagomizer reads undercounted.",
            accent=(150, 61, 48),
        ),
        tile(
            V102,
            "v102 reject: tail-parallel lower point",
            "Strong bony plates, but lower tail point runs too parallel to the tail/ground and adds spear drift.",
            accent=(150, 61, 48),
        ),
        tile(
            GUIDE,
            "strict target: four upward spikes",
            "Target: separate bony plates, rounded tail base, exactly four spikes, all rising above ground/horizon.",
            accent=(68, 92, 140),
        ),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v92", CURRENT),
        ("P11 v100 hold", V100),
        ("P11 v101 reject", V101),
        ("P11 v102 reject", V102),
        ("strict guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("plate material", (0.18, 0.04, 0.66, 0.56), (380, 210)),
        ("plate bases", (0.24, 0.28, 0.70, 0.66), (380, 210)),
        ("tail silhouette", (0.56, 0.12, 1.00, 0.72), (430, 210)),
        ("ground-angle check", (0.61, 0.35, 1.00, 0.86), (430, 210)),
        ("spike count close", (0.70, 0.07, 1.00, 0.70), (360, 210)),
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
                "experiment": "p11_v100_v102_bony_plate_material_tail_gate",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(CURRENT),
                "reviewHolds": [relative(V100)],
                "rejectReferences": [relative(V101), relative(V102)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v92_first_hold_v100_for_plate_material_reject_v101_v102_tail_failures",
                "reason": (
                    "The P11 prompt-only pass improves dorsal-plate color and material separation, especially v100, where the plates read as rough opaque bone/keratin rather than skin. "
                    "However, none of v100-v102 beats the thagomizer gate. V100 can read as five spikes or a radial cluster, v101 leaves a straight tail-spear continuation and undercount risk, and v102 leaves a tail-parallel lower point. "
                    "Keep v92 first and use v100 only as a plate-material review hold."
                ),
                "nextRoute": (
                    "Use tail-local ControlNet/inpaint over v92 or v100 rather than another whole-body prompt-only retry. Preserve the rough pale-bone/rust plate material while forcing a rounded tail base and exactly four countable spikes, all rising upward relative to the ground/horizon."
                ),
                "rejectIfPromoting": [
                    "any spike lies parallel to the ground or horizon",
                    "any lower spike runs along the tail shaft",
                    "tail continues as a pointed horizontal spear beyond the spike base",
                    "spikes form a radial/starburst cluster instead of two upward V pairs",
                    "tail reads as three spikes plus a nub or five-plus spikes",
                    "dorsal plates share skin-like leather color or texture",
                    "plates become leaves, soft fins, a comb ridge, or a connected sail",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V100, V101, V102, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
