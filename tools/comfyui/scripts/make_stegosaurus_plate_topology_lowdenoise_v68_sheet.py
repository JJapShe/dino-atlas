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
V67_REVIEW = ASSETS / "stegosaurus-stenops-plate-texture-lowdenoise-v67.png"
TOPOLOGY_GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-clean-v52.png"
V66_REJECT = ASSETS / "stegosaurus-plate-topology-clean-v66-rejection-sheet.png"

RESULTS_SOURCE = OUTPUTS / "stegosaurus_plate_topology_lowdenoise_v68-results.json"
CONTACT_SOURCE = OUTPUTS / "stegosaurus_plate_topology_lowdenoise_v68-contact-sheet.png"
SELECTED_SOURCE = OUTPUTS / "stegosaurus_plate_topology_lowdenoise_v68_plate_topology_side_profile_01_seed2026070162_d18.png"

SELECTED_OUT = ASSETS / "stegosaurus-stenops-plate-topology-lowdenoise-v68.png"
REVIEW_SHEET = ASSETS / "stegosaurus-plate-topology-lowdenoise-v68-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-plate-topology-lowdenoise-v68-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stego_plate_topology_lowdenoise_v68_review.json"

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


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    outputs = []
    for item in data:
        outputs.append(
            (
                f"{item['promptId']} seed {item['seed']} d{item['denoise']:.2f}",
                Path(item["image"]),
                item["variation"],
            )
        )
    return outputs


def make_review_sheet(outputs):
    items = [
        tile(CURRENT, "current v6 first candidate", "Best current representative: strong four-spike tail and readable Stegosaurus body."),
        tile(SELECTED_OUT, "v68 selected review hold", "Low-denoise topology prompt keeps body and tail, but two-row plate proof is still not decisive."),
        tile(V67_REVIEW, "v67 texture review hold", "Earlier low-denoise texture route; useful comparison but still below v6."),
        tile(CONTACT_SOURCE, "all v68 attempts", "Eight low-denoise RealVisXL i2i probes from v6 using topology and texture prompts."),
        tile(TOPOLOGY_GUIDE, "clean topology guide v52", "Project-owned guide for two staggered plate rows and four tail spikes."),
        tile(V66_REJECT, "v66 clean-guide rejection", "Higher structure guidance drifted body identity or weakened thagomizer evidence."),
        tile(CURRENT_CROPS, "v6 crop gate", "Use before promotion: plate row, feet, and thagomizer must all survive."),
    ]
    for label, path, variation in outputs:
        items.append(tile(path, f"v68 {label}", f"Prompt: {variation}"))

    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet(outputs):
    rows = [("current v6", CURRENT), ("v67 review", V67_REVIEW), ("v68 selected", SELECTED_OUT)]
    rows.extend((f"v68 {label}", path) for label, path, _ in outputs)
    rows.append(("v6 crop gate", CURRENT_CROPS))
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("dorsal plates", (0.08, 0.02, 0.78, 0.48), (430, 210)),
        ("plate surface", (0.30, 0.08, 0.62, 0.43), (300, 210)),
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
                "experiment": "plate_topology_lowdenoise_v68",
                "sourceImage": relative(CURRENT),
                "selectedReviewHold": relative(SELECTED_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "contactSheet": relative(CONTACT_SOURCE),
                "decision": "review_hold",
                "selectedSeed": 2026070162,
                "selectedDenoise": 0.18,
                "reason": (
                    "Low-denoise RealVisXL i2i from v6 keeps the recognizable Stegosaurus body and visible "
                    "thagomizer while slightly naturalizing plate texture, but it does not prove a stronger "
                    "staggered two-row plate topology than v6. Keep v6 first."
                ),
                "keepCurrentPrimary": relative(CURRENT),
                "outputs": [
                    {
                        "label": label,
                        "image": relative(path),
                        "variation": variation,
                        "decision": "review_hold" if path == SELECTED_SOURCE else "reject_reference",
                    }
                    for label, path, variation in outputs
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V67_REVIEW, TOPOLOGY_GUIDE, V66_REJECT, RESULTS_SOURCE, CONTACT_SOURCE, SELECTED_SOURCE]
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
