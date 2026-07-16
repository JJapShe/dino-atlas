import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
V25_CROPS = ASSET_ROOT / "velociraptor-modest-sickle-i2i-v25-crops.png"
V28_CROPS = ASSET_ROOT / "velociraptor-front-hook-micro-i2i-v28-crops.png"
MASK_SOURCE = OUTPUT_ROOT / "velociraptor_second_toe_topology_v30_custom_mask.png"
CONTACT_SOURCE = OUTPUT_ROOT / "velociraptor_second_toe_topology_v30-contact-sheet.png"
RESULTS_SOURCE = OUTPUT_ROOT / "velociraptor_second_toe_topology_v30-results.json"

SELECTED_LABEL = "seed 2026071011 d0.10"
SELECTED_SOURCE = OUTPUT_ROOT / "velociraptor_second_toe_topology_v30_custom_velociraptor-mongoliensis_seed2026071011_d10.png"

COMPARISON_OUT = ASSET_ROOT / "velociraptor-mongoliensis-second-toe-i2i-comparison-v30.png"
MASK_OUT = ASSET_ROOT / "velociraptor-second-toe-i2i-mask-v30.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "velociraptor-second-toe-i2i-v30-review-sheet.png"
CROPS_OUT = ASSET_ROOT / "velociraptor-second-toe-i2i-v30-crops.png"
REVIEW_OUT = REVIEW_ROOT / "velociraptor_second_toe_i2i_v30_review.json"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, font, fill, max_chars=58, line_h=15, max_lines=2):
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
        draw.text((x, y + idx * line_h), wrapped, fill=fill, font=font)


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    items = []
    for item in data:
        image = Path(item["image"])
        copied = OUTPUT_ROOT / f"velociraptor_second_toe_topology_v30_custom_velociraptor-mongoliensis_seed{item['seed']}_d{int(item['denoise'] * 100):02d}.png"
        items.append((f"seed {item['seed']} d{item['denoise']:.2f}", copied))
    return items


def copy_assets():
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SELECTED_SOURCE, COMPARISON_OUT)
    shutil.copyfile(MASK_SOURCE, MASK_OUT)


def make_review_sheet(outputs):
    items = [
        (
            CURRENT,
            "current v9: keep first",
            "Best current whole-body balance; foot anatomy still needs attached second-toe review.",
        ),
        (
            COMPARISON_OUT,
            "v30 second-toe topology comparison",
            "Selected low-denoise result for direct foot comparison; not promoted unless crops beat v9.",
        ),
        (
            CONTACT_SOURCE,
            "all v30 attempts",
            "Six tight-mask probes around the raised second-toe and rear toe cluster.",
        ),
        (
            MASK_OUT,
            "v30 second-toe mask",
            "V9-specific tight mask over foot/toe regions only.",
        ),
        (
            V25_CROPS,
            "v25 modest-sickle gate",
            "Previous local foot-tip comparison; useful but not enough for primary promotion.",
        ),
        (
            V28_CROPS,
            "v28 front-hook gate",
            "Previous hook-reduction route; too subtle or risky for promotion.",
        ),
    ]
    for label, path in outputs:
        items.append((path, f"v30 {label}", "Check toe attachment, no floating crescent, no extra toes, no ankle drift."))

    cols = 3
    thumb_w, thumb_h, label_h = 430, 242, 74
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (path, title, note) in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(path), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), title[:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 31), note, font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(REVIEW_SHEET_OUT)


def make_crop_sheet(outputs):
    crops = [
        ("current v9 full body", CURRENT, (0, 80, 1693, 850), (420, 190)),
        ("current v9 foot gate", CURRENT, (500, 590, 900, 845), (420, 250)),
        ("current v9 front claw", CURRENT, (545, 620, 730, 790), (360, 250)),
        ("current v9 rear toes", CURRENT, (675, 700, 870, 835), (360, 250)),
        ("v30 mask over foot", MASK_OUT, (500, 590, 900, 845), (420, 250)),
    ]
    for label, path in outputs:
        crops.extend(
            [
                (f"v30 {label} full body", path, (0, 80, 1693, 850), (420, 190)),
                (f"v30 {label} foot gate", path, (500, 590, 900, 845), (420, 250)),
                (f"v30 {label} front claw", path, (545, 620, 730, 790), (360, 250)),
                (f"v30 {label} rear toes", path, (675, 700, 870, 835), (360, 250)),
            ]
        )
    crops.extend(
        [
            ("current v9 crop audit", CURRENT_CROPS, (0, 0, 760, 760), (420, 250)),
            ("v25 crop gate", V25_CROPS, (0, 0, 760, 760), (420, 250)),
            ("v28 crop gate", V28_CROPS, (0, 0, 760, 760), (420, 250)),
        ]
    )

    cols = 2
    thumb_w, thumb_h, label_h = 430, 260, 38
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (label, path, box, size) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, size), ((thumb_w - size[0]) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:68], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(CROPS_OUT)


def write_review_json(outputs):
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "second_toe_topology_i2i_v30",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(REVIEW_SHEET_OUT),
                "cropSheet": relative(CROPS_OUT),
                "decision": "diagnostic_only",
                "selectedLabel": SELECTED_LABEL,
                "editMode": "velociraptor_second_toe_topology",
                "outputs": [{"label": label, "image": relative(path)} for label, path in outputs],
                "reasons": [
                    "the tight second-toe mask preserves the v9 whole body, head, feathered arms, tail, and leg count",
                    "the generated foot changes remain too subtle or smear the local toe detail rather than clearly proving attached second-toe topology",
                    "v9 remains the first candidate until a structure-aware foot route improves the sickle claw without toe drift",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "nextRoute": "Use a stronger line/depth foot control or dromaeosaur-specific conditioning; do not promote local foot edits unless close crops prove one raised second-toe claw is attached and walking toes remain grounded.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, V25_CROPS, V28_CROPS, MASK_SOURCE, CONTACT_SOURCE, RESULTS_SOURCE, SELECTED_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)
    outputs = load_outputs()
    copy_assets()
    make_review_sheet(outputs)
    make_crop_sheet(outputs)
    write_review_json(outputs)
    print(COMPARISON_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROPS_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
