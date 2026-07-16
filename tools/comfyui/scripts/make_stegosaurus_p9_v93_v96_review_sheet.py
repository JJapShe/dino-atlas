import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-imagegen-v92-source-candidate.png"
V93 = ASSETS / "stegosaurus-stenops-imagegen-v93-source-candidate.png"
V94 = ASSETS / "stegosaurus-stenops-imagegen-v94-source-candidate.png"
V95 = ASSETS / "stegosaurus-stenops-imagegen-v95-source-candidate.png"
V96 = ASSETS / "stegosaurus-stenops-imagegen-v96-source-candidate.png"
GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-v1.png"

REVIEW_SHEET = ASSETS / "stegosaurus-p9-v93-v96-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-p9-v93-v96-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stegosaurus_p9_v93_v96_review.json"

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
        tile(CURRENT, "current v92: keep as app first, not final", "Best current bony plates, but P9 adds stricter ground-relative upward-V tail gate.", accent=(38, 116, 76)),
        tile(V93, "v93 reject: horizontal tail extension", "Good plate material, but the tail tip still reads as a ground-parallel lower spike or tail point.", accent=(150, 61, 48)),
        tile(V94, "v94 reject: undercount risk", "Removes much of the flat lower spike, but the thagomizer reads closer to three large spikes.", accent=(150, 61, 48)),
        tile(V95, "v95 reject: 3+tail-point read", "Upward prongs are clearer, but the tail still continues as a small horizontal point after the spikes.", accent=(150, 61, 48)),
        tile(V96, "v96 reject: three-spike plus nub", "Best no-long-tail attempt, but still reads as three spikes plus a small side nub, not four upward spikes.", accent=(150, 61, 48)),
        tile(GUIDE, "strict target: upward V above ground", "Target: four countable spikes, two pairs, all rising above the tail line relative to the horizon.", accent=(68, 92, 140)),
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
        ("v93 reject", V93),
        ("v94 reject", V94),
        ("v95 reject", V95),
        ("v96 reject", V96),
        ("strict guide", GUIDE),
    ]
    crops = [
        ("full body", (0.00, 0.05, 1.00, 0.93), (430, 210)),
        ("plate material", (0.20, 0.05, 0.66, 0.55), (380, 210)),
        ("tail silhouette", (0.58, 0.13, 1.00, 0.72), (430, 210)),
        ("ground-angle check", (0.62, 0.42, 1.00, 0.88), (430, 210)),
        ("spike count close", (0.72, 0.10, 1.00, 0.70), (360, 210)),
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
                "experiment": "p9_v93_v96_ground_relative_upward_v_thagomizer",
                "currentPrimary": relative(CURRENT),
                "selectedCandidate": relative(CURRENT),
                "reviewHolds": [],
                "rejectReferences": [relative(V93), relative(V94), relative(V95), relative(V96)],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_v92_first_reject_v93_v96_for_ground_relative_tail_spike_failures",
                "reason": (
                    "The user clarified that the thagomizer must not be parallel to the ground; it must rise into an upward V relative to the ground/horizon. "
                    "V93-v96 improve the bony plate material but fail the stricter tail gate: v93 keeps a horizontal lower tail extension, v94 undercounts the spikes, "
                    "v95 reads as three spikes plus a horizontal tail point, and v96 reads as three spikes plus a small side nub. Keep v92 first as the current count-level pass, "
                    "but do not treat it as final because far-side spike clarity and ground-relative angle still need a localized control/inpaint route."
                ),
                "nextRoute": (
                    "Use a tail-only ControlNet or inpaint guide with a rounded tail base and four upward spikes above the horizon. Reject any output where the tail shaft continues "
                    "as a horizontal point beyond the thagomizer or where any spike lies parallel to the ground."
                ),
                "rejectIfPromoting": [
                    "any thagomizer spike lies parallel to the ground or horizon",
                    "tail shaft continues as a long straight point beyond the thagomizer",
                    "tail tip reads as three spikes plus a small side nub",
                    "tail tip reads as five or more spikes",
                    "spikes radiate in all directions instead of forming two upward V pairs",
                    "dorsal plates share the same leather-like color or texture as the skin",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, V93, V94, V95, V96, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
