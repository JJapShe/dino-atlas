import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSET_ROOT / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSET_ROOT / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V23_FOOT_COMPARE = ASSET_ROOT / "triceratops-toe-claw-matte-i2i-v23-foot-compare.png"
V8_RHINO_REJECT = ASSET_ROOT / "triceratops-horridus-closedbeak-rhinorisk-comparison-v8.png"

RESULTS_SOURCE = OUTPUT_ROOT / "triceratops_antirhino_lowdenoise_v24-results.json"
CONTACT_SOURCE = OUTPUT_ROOT / "triceratops_antirhino_lowdenoise_v24-contact-sheet.png"

SELECTED_SOURCE = OUTPUT_ROOT / "triceratops_antirhino_lowdenoise_v24_anti_rhino_body_01_seed2026070142_d24.png"
SELECTED_OUT = ASSET_ROOT / "triceratops-horridus-antirhino-lowdenoise-reject-v24.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "triceratops-antirhino-lowdenoise-v24-rejection-sheet.png"
CROPS_OUT = ASSET_ROOT / "triceratops-antirhino-lowdenoise-v24-crops.png"
REVIEW_OUT = REVIEW_ROOT / "trike_antirhino_lowdenoise_v24_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def fit(image, size):
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
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
    for idx, item in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 15), item, fill=(43, 39, 34), font=FONT)


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    outputs = []
    for item in data:
        path = Path(item["image"])
        label = f"{item['promptId']} seed {item['seed']} d{item['denoise']:.2f}"
        outputs.append((label, path, item["variation"]))
    return outputs


def make_review_sheet(outputs):
    items = [
        (
            CURRENT,
            "current v22 first candidate",
            "Best current app image: recognizable Triceratops body, long tail, attached frill, closed beak.",
        ),
        (
            SELECTED_OUT,
            "v24 selected reject/reference",
            "Low-denoise anti-rhino attempt keeps body plan but does not improve feet; head/eye read softens.",
        ),
        (
            CONTACT_SOURCE,
            "all v24 attempts",
            "Eight low-denoise RealVisXL i2i probes from v22 using toe and anti-rhino prompts.",
        ),
        (
            CURRENT_CROPS,
            "v22 crop gate",
            "Baseline crop audit remains stronger for head, frill, tail, and readable full-body silhouette.",
        ),
        (
            V23_FOOT_COMPARE,
            "v23 foot comparison",
            "Previous foot-only matte probe; also not enough to replace v22.",
        ),
        (
            V8_RHINO_REJECT,
            "old rhino-drift rejection",
            "Explicit failure anchor: reject any future output that returns to this mammal torso/body read.",
        ),
    ]
    for label, path, variation in outputs:
        items.append((path, f"v24 {label}", f"Prompt: {variation}"))

    cols = 3
    thumb_w, thumb_h, label_h = 430, 242, 78
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    for idx, (path, title, note) in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(path), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), title[:70], fill=(132, 61, 43), font=FONT)
        draw_wrapped(draw, (8, thumb_h + 31), note)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(REVIEW_SHEET_OUT)


def make_crop_sheet(outputs):
    crop_defs = [
        ("full body", (0, 75, 1672, 830), (520, 234)),
        ("head/frill/beak", (0, 190, 610, 580), (390, 230)),
        ("feet strip", (350, 675, 1255, 825), (520, 180)),
        ("front toes", (390, 705, 570, 805), (360, 190)),
        ("middle toes", (585, 705, 735, 805), (320, 190)),
        ("rear toes", (875, 690, 1210, 805), (430, 190)),
        ("tail/body", (780, 245, 1665, 630), (520, 200)),
    ]
    rows = [("v22 current", CURRENT), ("v24 selected reject", SELECTED_OUT)]
    rows.extend((f"v24 {label}", path) for label, path, _ in outputs)
    rows.append(("v22 crop gate", CURRENT_CROPS))

    cols = 2
    thumb_w, thumb_h, label_h = 560, 270, 40
    tiles = []
    for label, path in rows:
        if path == CURRENT_CROPS:
            source = Image.open(path)
            tiles.append((label, path, (0, 0, source.width, min(source.height, 950)), (540, 260)))
            continue
        for title, box, size in crop_defs:
            tiles.append((f"{label} {title}", path, box, size))

    sheet_rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, sheet_rows * (thumb_h + label_h)), (232, 228, 218))
    for idx, (label, path, box, size) in enumerate(tiles):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, size), ((thumb_w - size[0]) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:84], fill=(43, 39, 34), font=FONT)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CROPS_OUT)


def write_review(outputs):
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "triceratops-horridus",
                "experiment": "antirhino_lowdenoise_v24",
                "sourceImage": relative(CURRENT),
                "selectedRejectReference": relative(SELECTED_OUT),
                "contactSheet": relative(CONTACT_SOURCE),
                "reviewSheet": relative(REVIEW_SHEET_OUT),
                "cropSheet": relative(CROPS_OUT),
                "decision": "reject_reference",
                "reason": (
                    "Low-denoise RealVisXL i2i avoided the old rhinoceros-body failure, but it did not "
                    "meaningfully improve toe anatomy over v22 and softened the head/eye read. Keep v22 "
                    "as the app-facing first candidate and use v24 only as a route-limit reference."
                ),
                "outputs": [
                    {
                        "label": label,
                        "image": relative(path),
                        "variation": variation,
                        "decision": "reject_reference",
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
    outputs = load_outputs()
    shutil.copyfile(SELECTED_SOURCE, SELECTED_OUT)
    make_review_sheet(outputs)
    make_crop_sheet(outputs)
    write_review(outputs)
    print(
        json.dumps(
            {
                "selected": relative(SELECTED_OUT),
                "reviewSheet": relative(REVIEW_SHEET_OUT),
                "cropSheet": relative(CROPS_OUT),
                "review": relative(REVIEW_OUT),
                "outputs": len(outputs),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
