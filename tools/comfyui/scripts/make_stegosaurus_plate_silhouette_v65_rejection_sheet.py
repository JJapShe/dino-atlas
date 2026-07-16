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
CONTROL = ASSETS / "stegosaurus-stenops-plate-silhouette-control-v65.png"
CONTROL_MASK = ASSETS / "stegosaurus-plate-silhouette-control-mask-v65.png"
CONTROL_REVIEW = ASSETS / "stegosaurus-plate-silhouette-control-v65-review-sheet.png"
V54_V55_CROPS = ASSETS / "stegosaurus-v6-clean-guide-ipcontrol-v54-v55-rejection-crops.png"

LOW_SOURCE = OUTPUTS / "stegosaurus_plate_silhouette_ipcontrol_v65_style_transfer_stegosaurus-stenops_seed2026071201_iw48_cs26.png"
HIGH_SOURCE = OUTPUTS / "stegosaurus_plate_silhouette_ipcontrol_v65_style_transfer_stegosaurus-stenops_seed2026071202_iw48_cs34.png"
CONTACT = OUTPUTS / "stegosaurus_plate_silhouette_ipcontrol_v65-contact-sheet.png"
RESULTS = OUTPUTS / "stegosaurus_plate_silhouette_ipcontrol_v65-results.json"

LOW_OUT = ASSETS / "stegosaurus-stenops-plate-silhouette-ipcontrol-rejected-v65.png"
HIGH_OUT = ASSETS / "stegosaurus-stenops-plate-silhouette-ipcontrol-highcontrol-rejected-v65.png"
REVIEW_SHEET = ASSETS / "stegosaurus-plate-silhouette-ipcontrol-v65-rejection-sheet.png"
CROPS_OUT = ASSETS / "stegosaurus-plate-silhouette-ipcontrol-v65-rejection-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stego_plate_silhouette_ipcontrol_v65_review.json"

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
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 15), line, fill=(43, 39, 34), font=FONT)


def fractional_crop(image, box):
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def copy_assets():
    shutil.copy2(LOW_SOURCE, LOW_OUT)
    shutil.copy2(HIGH_SOURCE, HIGH_OUT)


def tile(path, title, note, size=(430, 242)):
    image = Image.open(path).convert("RGB")
    panel = Image.new("RGB", (size[0], size[1] + 74), (245, 243, 236))
    panel.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def make_review_sheet():
    items = [
        tile(CURRENT, "current v6: keep first", "Still better for Stegosaurus identity, broad plates, body, feet, and four-spike tail."),
        tile(CONTROL, "v65 plate silhouette control", "V6 body plus stronger plate silhouettes; useful as a control input, not final art."),
        tile(CONTACT, "v65 IP-Control sweep", "Reject all four: body drifts and plates become low combs, fans, or neck frills."),
        tile(LOW_OUT, "v65 low-control rejection", "Fails representative identity: weak thagomizer, generic herbivore body, comb-like plates."),
        tile(HIGH_OUT, "v65 high-control rejection", "Fails harder: front-heavy body drift, fan plates near shoulder, no four-spike thagomizer."),
        tile(V54_V55_CROPS, "previous v54/v55 rejection crops", "Confirms v6+guide IP-Control routes do not hold plates and thagomizer together."),
    ]
    cols = 3
    sheet = Image.new("RGB", (cols * items[0].width, 2 * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REVIEW_SHEET)


def make_crops():
    rows = [
        ("v6 current", CURRENT),
        ("v65 low reject", LOW_OUT),
        ("v65 high reject", HIGH_OUT),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (330, 190)),
        ("plate row", (0.12, 0.02, 0.84, 0.52), (330, 190)),
        ("head/neck", (0.0, 0.16, 0.36, 0.64), (250, 170)),
        ("feet/body", (0.12, 0.52, 0.78, 0.98), (330, 170)),
        ("tail/thagomizer", (0.56, 0.22, 1.0, 0.78), (310, 170)),
    ]
    gap = 10
    label_h = 38
    col_w = 340
    row_h = 228
    sheet = Image.new("RGB", (gap + len(crops) * (col_w + gap), gap + len(rows) * (row_h + label_h + gap)), (232, 228, 218))
    for row_idx, (row_label, path) in enumerate(rows):
        image = Image.open(path).convert("RGB")
        y = gap + row_idx * (row_h + label_h + gap)
        for col_idx, (crop_label, box, size) in enumerate(crops):
            x = gap + col_idx * (col_w + gap)
            tile = Image.new("RGB", (col_w, row_h + label_h), (245, 243, 236))
            tile.paste(fit(fractional_crop(image, box), size), ((col_w - size[0]) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((8, row_h + 7), f"{row_label}: {crop_label}"[:54], fill=(43, 39, 34), font=FONT)
            sheet.paste(tile, (x, y))
    sheet.save(CROPS_OUT)


def write_review_json():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_silhouette_ipcontrol_v65",
                "currentPrimary": relative(CURRENT),
                "controlSource": relative(CONTROL),
                "controlMask": relative(CONTROL_MASK),
                "controlReviewSheet": relative(CONTROL_REVIEW),
                "lowControlRejection": relative(LOW_OUT),
                "highControlRejection": relative(HIGH_OUT),
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROPS_OUT),
                "decision": "diagnostic_only",
                "seeds": [2026071201, 2026071202],
                "ipWeight": 0.48,
                "controlStrengths": [0.26, 0.34],
                "controlEnd": 0.46,
                "outputs": [
                    {
                        "seed": item["seed"],
                        "ipWeight": item["ipWeight"],
                        "controlStrength": item["controlStrength"],
                        "image": maybe_relative(item["image"]),
                    }
                    for item in results
                ],
                "reasons": [
                    "v65 control improves the local plate input compared with a plain cartoon guide, but IP-Control still drifts away from Stegosaurus body identity",
                    "generated plates become low combs, shoulder fans, or neck-frill-like rows instead of broad separated bony dorsal plates",
                    "the four-spike thagomizer gate fails, so none of the outputs can replace v6",
                    "future work needs a Stegosauridae-specific LoRA or reviewed plate-structure training set rather than more v6-reference IP-Control sweeps",
                ],
                "keepCurrentPrimary": relative(CURRENT),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, CONTROL, CONTROL_MASK, CONTROL_REVIEW, LOW_SOURCE, HIGH_SOURCE, CONTACT, RESULTS, V54_V55_CROPS):
        if not path.exists():
            raise FileNotFoundError(path)
    copy_assets()
    make_review_sheet()
    make_crops()
    write_review_json()
    print(LOW_OUT)
    print(HIGH_OUT)
    print(REVIEW_SHEET)
    print(CROPS_OUT)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
