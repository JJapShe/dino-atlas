import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

PRIMARY = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
PRIMARY_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
V56_V57_CROPS = ASSETS / "stegosaurus-plate-lora-i2i-v56-v57-rejection-crops.png"
V61_V63_CROPS = ASSETS / "stegosaurus-plate-graft-v61-v63-rejection-crops.png"
CONTACT_SOURCE = OUTPUTS / "stegosaurus_practicalfx_plate_lora_v64-contact-sheet.png"
MASK_SOURCE = OUTPUTS / "stegosaurus_practicalfx_plate_lora_v64_stego_dorsal_plates_mask.png"
RESULTS_SOURCE = OUTPUTS / "stegosaurus_practicalfx_plate_lora_v64-results.json"

SELECTED_LABEL = "seed 2026071111 d0.16"
SELECTED_SOURCE = OUTPUTS / "stegosaurus_practicalfx_plate_lora_v64_stego_dorsal_plates_stegosaurus-stenops_seed2026071111_s05_d16.png"

COMPARISON_OUT = ASSETS / "stegosaurus-stenops-practicalfx-plate-lora-rejected-v64.png"
MASK_OUT = ASSETS / "stegosaurus-practicalfx-plate-lora-mask-v64.png"
REVIEW_SHEET_OUT = ASSETS / "stegosaurus-practicalfx-plate-lora-v64-rejection-sheet.png"
CROPS_OUT = ASSETS / "stegosaurus-practicalfx-plate-lora-v64-rejection-crops.png"
REVIEW_JSON = REVIEW_DIR / "stego_practicalfx_plate_lora_v64_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (248, 247, 242))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def wrapped(draw, xy, text, max_chars=60, max_lines=2):
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
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 15), line, fill=(35, 32, 28), font=FONT)


def label_tile(title, note, path, size=(410, 230), label_h=76):
    tile = Image.new("RGB", (size[0], size[1] + label_h), (248, 247, 242))
    tile.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 8), title[:76], fill=(132, 61, 43), font=FONT)
    wrapped(draw, (8, size[1] + 31), note)
    return tile


def crop_tile(title, path, box, size):
    image = Image.open(path).convert("RGB").crop(box)
    tile = Image.new("RGB", (size[0], size[1] + 34), (248, 247, 242))
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((8, size[1] + 10), title[:68], fill=(24, 24, 22), font=FONT)
    return tile


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    outputs = []
    for item in data:
        path = OUTPUTS / (
            "stegosaurus_practicalfx_plate_lora_v64_stego_dorsal_plates_"
            f"stegosaurus-stenops_seed{item['seed']}_s05_d{int(item['denoise'] * 100):02d}.png"
        )
        outputs.append((f"seed {item['seed']} d{item['denoise']:.2f}", path))
    return outputs


def make_review_sheet(outputs):
    items = [
        (
            "v6 primary: keep first",
            "Best current Stegosaurus balance, but plate rows still need stricter review.",
            PRIMARY,
        ),
        (
            "v64 practical-fx LoRA comparison",
            "Selected low-strength LoRA output for direct plate-band comparison; not promoted.",
            COMPARISON_OUT,
        ),
        (
            "all v64 attempts",
            "Six low-strength practical-fx LoRA plate-band i2i probes.",
            CONTACT_SOURCE,
        ),
        (
            "v64 plate-band mask",
            "Broad dorsal plate mask reused to test whether this LoRA improves plate identity.",
            MASK_OUT,
        ),
        (
            "v56/v57 generic LoRA failures",
            "Previous weak Dinosaur_Generator_v2 plate-band route for comparison.",
            V56_V57_CROPS,
        ),
        (
            "v61-v63 graft/synthetic failures",
            "Recent explicit graft and prompt-only routes; both remain diagnostic only.",
            V61_V63_CROPS,
        ),
    ]
    for label, path in outputs:
        items.append((f"v64 {label}", "Check separate broad plates, two-row cue, no sail/comb, tail gate intact.", path))

    cols = 3
    gap = 16
    margin = 18
    title_h = 58
    thumb_w, thumb_h, label_h = 410, 230, 76
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new(
        "RGB",
        (margin * 2 + cols * thumb_w + gap * (cols - 1), margin * 2 + title_h + rows * (thumb_h + label_h) + gap * (rows - 1)),
        (232, 229, 220),
    )
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (margin, margin),
        "Stegosaurus v64 dinosaur_practical_fx plate-band i2i: diagnostic; v6 remains first",
        fill=(24, 24, 22),
        font=FONT,
    )
    for idx, (title, note, path) in enumerate(items):
        tile = label_tile(title, note, path, (thumb_w, thumb_h), label_h)
        x = margin + (idx % cols) * (thumb_w + gap)
        y = margin + title_h + (idx // cols) * (thumb_h + label_h + gap)
        sheet.paste(tile, (x, y))
    sheet.save(REVIEW_SHEET_OUT)


def make_crops(outputs):
    crop_defs = [
        ("full body", (0, 145, 1672, 840), (330, 138)),
        ("full plate row", (170, 150, 1310, 525), (350, 150)),
        ("front plates/head", (0, 240, 640, 610), (270, 156)),
        ("mid plates", (505, 135, 1040, 500), (270, 156)),
        ("tail plates", (960, 255, 1395, 565), (260, 156)),
        ("tail/thagomizer", (1130, 395, 1672, 825), (270, 156)),
    ]
    rows = [("v6 primary", PRIMARY)] + [(f"v64 {label}", path) for label, path in outputs]
    rows.extend(
        [
            ("v6 crop audit", PRIMARY_CROPS),
            ("v56/v57 generic LoRA crops", V56_V57_CROPS),
        ]
    )
    cols = 2
    thumb_w, thumb_h, label_h = 430, 260, 38
    tiles = []
    for label, path in rows:
        if path in (PRIMARY_CROPS, V56_V57_CROPS):
            tiles.append((label, path, (0, 0, Image.open(path).width, min(Image.open(path).height, 900)), (420, 250)))
            continue
        for title, box, size in crop_defs:
            tiles.append((f"{label} {title}", path, box, size))

    sheet_rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, sheet_rows * (thumb_h + label_h)), (232, 228, 218))
    for idx, (label, path, box, size) in enumerate(tiles):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (248, 247, 242))
        tile.paste(crop_tile(label, path, box, size).crop((0, 0, size[0], size[1] + 34)), ((thumb_w - size[0]) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:68], fill=(24, 24, 22), font=FONT)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CROPS_OUT)


def write_review(outputs):
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "practicalfx_plate_lora_i2i_v64",
                "sourceImage": relative(PRIMARY),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(REVIEW_SHEET_OUT),
                "cropSheet": relative(CROPS_OUT),
                "decision": "diagnostic_only",
                "lora": "dinosaur_practical_fx.safetensors",
                "loraStrength": 0.05,
                "clipStrength": 0.03,
                "selectedLabel": SELECTED_LABEL,
                "outputs": [{"label": label, "image": relative(path)} for label, path in outputs],
                "reasons": [
                    "the low-strength practical-fx LoRA preserves the v6 body, feet, tail, and thagomizer better than broad structural retries",
                    "plate-band crops remain too close to v6 or slightly soften the dorsal plates without proving a stronger two-row topology",
                    "this route does not solve the user-facing plate identity problem, so v6 remains the first candidate",
                ],
                "nextRoute": "Do not repeat generic/practical-fx plate-band LoRA at similar settings; Stegosaurus needs a species/clade LoRA or a reviewed plate-structure training set that can learn separate broad plates before naturalization.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (PRIMARY, PRIMARY_CROPS, V56_V57_CROPS, V61_V63_CROPS, CONTACT_SOURCE, MASK_SOURCE, RESULTS_SOURCE, SELECTED_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)
    outputs = load_outputs()
    shutil.copyfile(SELECTED_SOURCE, COMPARISON_OUT)
    shutil.copyfile(MASK_SOURCE, MASK_OUT)
    make_review_sheet(outputs)
    make_crops(outputs)
    write_review(outputs)
    print(COMPARISON_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROPS_OUT)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
