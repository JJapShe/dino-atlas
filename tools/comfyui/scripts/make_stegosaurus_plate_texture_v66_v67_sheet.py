import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
COMFY_OUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
TOPOLOGY_GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-clean-v52.png"
V66_CONTACT = OUTPUTS / "stegosaurus_plate_topology_clean_v66-contact-sheet.png"
V66_RESULTS = OUTPUTS / "stegosaurus_plate_topology_clean_v66-results.json"
V67_CONTACT = OUTPUTS / "stegosaurus_plate_texture_lowdenoise_v67-contact-sheet.png"
V67_RESULTS = OUTPUTS / "stegosaurus_plate_texture_lowdenoise_v67-results.json"

V67_SOURCES = [
    (
        "seed 2026070121 d0.22",
        COMFY_OUT / "stegosaurus_plate_texture_lowdenoise_v67_plate_topology_texture_01_seed2026070121_d22_00001_.png",
    ),
    (
        "seed 2026070122 d0.22",
        COMFY_OUT / "stegosaurus_plate_texture_lowdenoise_v67_plate_topology_texture_01_seed2026070122_d22_00001_.png",
    ),
    (
        "seed 2026070121 d0.28",
        COMFY_OUT / "stegosaurus_plate_texture_lowdenoise_v67_plate_topology_texture_01_seed2026070121_d28_00001_.png",
    ),
    (
        "seed 2026070122 d0.28",
        COMFY_OUT / "stegosaurus_plate_texture_lowdenoise_v67_plate_topology_texture_01_seed2026070122_d28_00001_.png",
    ),
]

SELECTED_LABEL = "seed 2026070121 d0.28"
SELECTED_SOURCE = V67_SOURCES[2][1]
SELECTED_OUT = ASSETS / "stegosaurus-stenops-plate-texture-lowdenoise-v67.png"
REVIEW_SHEET = ASSETS / "stegosaurus-plate-texture-i2i-v66-v67-review-sheet.png"
CROP_SHEET = ASSETS / "stegosaurus-plate-texture-i2i-v67-crops.png"
V66_REJECTION_SHEET = ASSETS / "stegosaurus-plate-topology-clean-v66-rejection-sheet.png"
REVIEW_JSON = REVIEW_ROOT / "stego_plate_texture_i2i_v66_v67_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def maybe_relative(path_text):
    path = Path(path_text)
    try:
        return relative(path)
    except ValueError:
        return path_text


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
    panel = Image.new("RGB", (size[0], size[1] + 74), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def fractional_crop(image, box):
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def copy_assets():
    shutil.copy2(SELECTED_SOURCE, SELECTED_OUT)
    shutil.copy2(V66_CONTACT, V66_REJECTION_SHEET)


def make_review_sheet():
    items = [
        tile(CURRENT, "current v6: keep first for now", "Best current balance of body, plate row, four feet, and countable four-spike tail."),
        tile(SELECTED_OUT, "v67 selected review hold", "Low-denoise i2i improves rough bony surface while preserving body and tail count."),
        tile(V67_CONTACT, "v67 low-denoise texture sweep", "Four low-denoise variants. Best one is useful, but not a decisive replacement for v6."),
        tile(TOPOLOGY_GUIDE, "clean topology guide v52", "Good control target, but too schematic for training or direct app promotion."),
        tile(V66_REJECTION_SHEET, "v66 IP-Control rejection sheet", "Clean guide plus IP/Control drifts body identity or loses reliable tail-spike count."),
        tile(CURRENT_CROPS, "current v6 crop gate", "Use this crop sheet to keep checking plate row, feet, and thagomizer before promotion."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v6", CURRENT),
        ("v67 selected", SELECTED_OUT),
    ]
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
    sheet = Image.new("RGB", (gap + len(crops) * (col_w + gap), gap + len(rows) * (row_h + label_h + gap)), (232, 228, 218))
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
    v66_results = json.loads(V66_RESULTS.read_text(encoding="utf-8"))
    v67_results = json.loads(V67_RESULTS.read_text(encoding="utf-8"))
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_texture_i2i_v66_v67",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(SELECTED_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "v66RejectionSheet": relative(V66_REJECTION_SHEET),
                "v67ContactSheet": maybe_relative(str(V67_CONTACT)),
                "decision": "review_hold",
                "selectedSeed": 2026070121,
                "selectedDenoise": 0.28,
                "selectedLabel": SELECTED_LABEL,
                "routeSummary": [
                    "v66 used current v6 as style reference and the clean v52 topology guide as control; it generated obvious body or identity drift and should remain rejected",
                    "v67 used low-denoise i2i over current v6 with a rough bony plate texture prompt; it preserves body and tail count better than v66",
                    "v67 selected output is useful as a review hold because plate surface is rougher, but it does not yet prove a stronger staggered two-row topology than v6",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Use a Stegosauridae-specific LoRA or curated plate-structure seed expansion. Avoid higher-strength IP-Control from the clean topology guide unless a body-lock control is added.",
                "v66Outputs": [
                    {
                        "seed": item["seed"],
                        "ipWeight": item["ipWeight"],
                        "controlStrength": item["controlStrength"],
                        "image": maybe_relative(item["image"]),
                    }
                    for item in v66_results
                ],
                "v67Outputs": [
                    {
                        "seed": item["seed"],
                        "denoise": item["denoise"],
                        "image": maybe_relative(item["image"]),
                    }
                    for item in v67_results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [
        CURRENT,
        CURRENT_CROPS,
        TOPOLOGY_GUIDE,
        V66_CONTACT,
        V66_RESULTS,
        V67_CONTACT,
        V67_RESULTS,
        *[path for _, path in V67_SOURCES],
    ]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    copy_assets()
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(SELECTED_OUT)
    print(REVIEW_SHEET)
    print(CROP_SHEET)
    print(V66_REJECTION_SHEET)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
