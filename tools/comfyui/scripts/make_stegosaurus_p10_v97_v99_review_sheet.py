import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-imagegen-v92-source-candidate.png"
V97 = ASSETS / "stegosaurus-stenops-imagegen-v97-source-candidate.png"
V98 = ASSETS / "stegosaurus-stenops-imagegen-v98-source-candidate.png"
V99 = ASSETS / "stegosaurus-stenops-imagegen-v99-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p10-v97-v99-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p10-v97-v99-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p10_v97_v99_review.json"

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
            "Closest current bony-plate and upward-V compromise, but lower tail-point clarity still needs control/inpaint.",
            accent=(38, 116, 76),
        ),
        tile(
            V97,
            "v97 reject: lower spike still too level",
            "Body and plate material are useful, but the rear lower point still reads too ground-parallel.",
            accent=(150, 61, 48),
        ),
        tile(
            V98,
            "v98 reject: horizontal tail-point remains",
            "Upward pair is clear, but a straight side point continues along the tail direction.",
            accent=(150, 61, 48),
        ),
        tile(
            V99,
            "v99 reject: direction better, count/radial risk",
            "Best upward direction, but the thagomizer can read as five or a radial cluster instead of exactly four.",
            accent=(150, 61, 48),
        ),
        tile(
            GUIDE,
            "strict target: ground-relative upward V",
            "Target: rounded tail base, exactly four spikes, all tips above the horizon and not parallel to the ground.",
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
        ("v97 reject", V97),
        ("v98 reject", V98),
        ("v99 reject", V99),
        ("strict guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("plate material", (0.20, 0.05, 0.66, 0.55), (380, 210)),
        ("tail silhouette", (0.58, 0.12, 1.00, 0.72), (430, 210)),
        ("ground-angle check", (0.62, 0.36, 1.00, 0.86), (430, 210)),
        ("spike count close", (0.72, 0.08, 1.00, 0.70), (360, 210)),
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
                "experiment": "p10_v97_v99_ground_relative_upward_v_retry",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(CURRENT),
                "reviewHolds": [],
                "rejectReferences": [relative(V97), relative(V98), relative(V99)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v92_first_reject_v97_v99_for_tail_angle_or_count_failures",
                "reason": (
                    "The user clarified that the thagomizer is not parallel to the ground and must rise into a V relative to the ground/horizon. "
                    "V97 and v98 still leave a lower side point that reads too horizontal or tail-parallel. V99 moves the spikes upward better, but risks a five-spike or radial cluster read. "
                    "Keep v92 first for now, but treat all prompt-only retries as evidence that the next route needs tail-local ControlNet/inpaint rather than more whole-body prompting."
                ),
                "nextRoute": (
                    "Use a tail-only mask/control guide over v92. End the tail in a rounded base and force exactly four countable spikes with every spike tip above the horizon; "
                    "the two lower spikes must still angle upward, not sideways along the tail shaft."
                ),
                "rejectIfPromoting": [
                    "any spike lies parallel to the ground or horizon",
                    "any lower spike runs along the tail shaft",
                    "tail continues as a pointed horizontal extension beyond the spike base",
                    "spikes form a radial/starburst cluster instead of two upward V pairs",
                    "tail reads as three spikes plus a nub or five-plus spikes",
                    "dorsal plates share skin-like leather color or texture",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V97, V98, V99, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
