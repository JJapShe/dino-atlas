import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V68 = ASSETS / "stegosaurus-stenops-plate-topology-lowdenoise-v68.png"
MASK_CROP = ASSETS / "stegosaurus-plate-row-mask-crop-v69.png"
MASK = ASSETS / "stegosaurus-plate-row-i2i-mask-v69.png"

RESULTS_SOURCE = OUTPUTS / "stegosaurus_plate_row_v69-results.json"
CONTACT_SOURCE = OUTPUTS / "stegosaurus_plate_row_v69-contact-sheet.png"
SELECTED_SOURCE = OUTPUTS / "stegosaurus_plate_row_v69_custom_stegosaurus-stenops_seed2026070170_d16.png"

SELECTED_OUT = ASSETS / "stegosaurus-stenops-plate-row-i2i-v69.png"
REVIEW_SHEET = ASSETS / "stegosaurus-plate-row-i2i-v69-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-plate-row-i2i-v69-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stego_plate_row_i2i_v69_review.json"

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


def tile(path, title, note, size=(430, 242)):
    panel = Image.new("RGB", (size[0], size[1] + 76), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def fractional_crop(image, box):
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def copied_output_path(item):
    return OUTPUTS / (
        f"stegosaurus_plate_row_v69_custom_{item['taxonId']}_seed{item['seed']}_d{int(item['denoise'] * 100):02d}.png"
    )


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    outputs = []
    for item in data:
        path = copied_output_path(item)
        outputs.append((f"seed {item['seed']} d{item['denoise']:.2f}", path, item))
    return outputs


def make_review_sheet(outputs):
    items = [
        tile(CURRENT, "current v6 first candidate", "Still first: natural body, readable plates, and countable four-spike thagomizer."),
        tile(SELECTED_OUT, "v69 selected review hold", "Custom plate-row mask keeps the body stable and slightly hardens plate edges, but is not a promotion."),
        tile(V68, "v68 topology review hold", "Earlier low-denoise topology attempt; useful comparison but not stronger than v6."),
        tile(CONTACT_SOURCE, "all v69 attempts", "Four custom-mask inpaint probes over the current v6 plate row."),
        tile(MASK_CROP, "v69 custom mask crop", "Shows the current plate-row mask used to avoid changing feet, body, and thagomizer."),
        tile(CURRENT_CROPS, "v6 crop gate", "Existing close-review gate remains the baseline before any promotion."),
    ]
    for label, path, _ in outputs:
        items.append(tile(path, f"v69 {label}", "Low-denoise plate-row inpaint; inspect plate gaps, bony surface, and tail preservation."))

    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet(outputs):
    rows = [("current v6", CURRENT), ("v68 review", V68), ("v69 selected", SELECTED_OUT)]
    rows.extend((f"v69 {label}", path) for label, path, _ in outputs)
    rows.append(("v6 crop gate", CURRENT_CROPS))
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("dorsal plates", (0.08, 0.02, 0.78, 0.48), (430, 210)),
        ("plate gaps", (0.19, 0.04, 0.66, 0.43), (360, 210)),
        ("tail spikes", (0.72, 0.32, 1.0, 0.78), (300, 210)),
        ("feet and legs", (0.02, 0.48, 0.70, 0.98), (430, 210)),
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
        if path == CURRENT_CROPS:
            sheet.paste(fit(image, (sheet.width - gap * 2, row_h + label_h)), (gap, y))
            continue
        for col_idx, (crop_label, box, size) in enumerate(crops):
            x = gap + col_idx * (col_w + gap)
            panel = Image.new("RGB", (col_w, row_h + label_h), (245, 243, 236))
            panel.paste(fit(fractional_crop(image, box), size), ((col_w - size[0]) // 2, 0))
            draw = ImageDraw.Draw(panel)
            draw.text((8, row_h + 8), f"{row_label}: {crop_label}"[:66], fill=(43, 39, 34), font=FONT)
            sheet.paste(panel, (x, y))
    sheet.save(CROP_SHEET)


def write_review_json(outputs):
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_row_i2i_v69",
                "sourceImage": relative(CURRENT),
                "mask": relative(MASK),
                "selectedReviewHold": relative(SELECTED_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "contactSheet": relative(CONTACT_SOURCE),
                "decision": "review_hold",
                "selectedSeed": 2026070170,
                "selectedDenoise": 0.16,
                "reason": (
                    "The custom v69 mask keeps the v6 body, legs, and four-spike thagomizer stable while slightly "
                    "hardening the dorsal plate edges. It remains a review hold because the alternating two-row "
                    "topology is still not clearly stronger than v6."
                ),
                "keepCurrentPrimary": relative(CURRENT),
                "outputs": [
                    {
                        "label": label,
                        "image": relative(path),
                        "seed": item["seed"],
                        "denoise": item["denoise"],
                        "decision": "review_hold" if path == SELECTED_SOURCE else "reject_reference",
                    }
                    for label, path, item in outputs
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V68, MASK, MASK_CROP, RESULTS_SOURCE, CONTACT_SOURCE, SELECTED_SOURCE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    outputs = load_outputs()
    shutil.copy2(SELECTED_SOURCE, SELECTED_OUT)
    make_review_sheet(outputs)
    make_crop_sheet(outputs)
    write_review_json(outputs)
    print(
        json.dumps(
            {
                "selected": relative(SELECTED_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "review": relative(REVIEW_JSON),
                "outputs": len(outputs),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
