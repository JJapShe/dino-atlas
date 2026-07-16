import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
GUIDE = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-v1.png"
REJECTED_V47 = ASSET_ROOT / "stegosaurus-stenops-schedule-i2i-v6source-rejected-v47.png"
COMPARISON_V48 = ASSET_ROOT / "stegosaurus-stenops-texture-i2i-comparison-v48.png"

SHEET_OUT = ASSET_ROOT / "stegosaurus-texture-i2i-v48-review-sheet.png"
CROP_OUT = ASSET_ROOT / "stegosaurus-texture-i2i-v48-crops.png"
REVIEW_JSON = REVIEW_ROOT / "stego_texture_i2i_v48_review.json"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, font, fill, max_chars=60, line_h=15, max_lines=2):
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
        draw.text((x, y + idx * line_h), line, fill=fill, font=font)


def make_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v6: keep first",
            "note": "Best natural Stegosaurus read: low body, broad separated plates, planted feet, and countable four-spike thagomizer.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v6 crop gate",
            "note": "Use this to compare plate row, plate surface, small head, feet, and four thagomizer spikes.",
        },
        {
            "path": GUIDE,
            "title": "plate topology structure guide",
            "note": "Reference target for staggered near/far rows, visible gaps, varied plate sizes, and exactly four tail spikes.",
        },
        {
            "path": REJECTED_V47,
            "title": "reject v47: artifacts and weak tail gate",
            "note": "Earlier v6-source schedule+i2i thickened plates but introduced lower-frame artifacts and weaker four-spike evidence.",
        },
        {
            "path": COMPARISON_V48,
            "title": "compare v48: low-denoise texture i2i",
            "note": "No frame artifact and natural enough, but plate topology and thagomizer count do not clearly improve on v6.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 76
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 31), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(SHEET_OUT)


def make_crops():
    crops = [
        ("current v6 full body", CURRENT, (0, 0, 1672, 940)),
        ("current v6 plate row", CURRENT, (185, 80, 1190, 430)),
        ("current v6 four spikes", CURRENT, (1215, 355, 1660, 690)),
        ("current v6 feet", CURRENT, (285, 600, 1080, 855)),
        ("v48 full body", COMPARISON_V48, (0, 0, 1672, 940)),
        ("v48 plate row", COMPARISON_V48, (185, 80, 1190, 430)),
        ("v48 thagomizer check", COMPARISON_V48, (1215, 355, 1660, 690)),
        ("v48 feet / no artifact", COMPARISON_V48, (285, 600, 1080, 855)),
        ("v47 artifact failure", REJECTED_V47, (0, 700, 1672, 940)),
        ("topology guide target", GUIDE, (0, 0, 1536, 1024)),
    ]

    cols = 2
    thumb_w = 380
    thumb_h = 250
    label_h = 38
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (label, path, box) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:58], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CROP_OUT)


def write_review():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    review = {
        "taxonId": "stegosaurus-stenops",
        "experiment": "texture_i2i_v48",
        "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
        "outputImage": str(COMPARISON_V48.relative_to(ROOT)).replace("\\", "/"),
        "reviewSheet": str(SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
        "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
        "promptId": "plate_topology_texture_01",
        "seed": 2026070351,
        "denoise": 0.24,
        "decision": "anatomy_review_comparison",
        "reasons": [
            "no lower-frame artifact like v47",
            "natural enough to keep as a comparison image",
            "does not clearly improve plate-row topology over the current v6 primary",
            "thagomizer count is not more reliable than v6",
        ],
        "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
        "nextRoute": "Keep v6 first. Use localized plate-row or tail-tip masking, or a stronger Stegosauridae LoRA/control route, rather than whole-body low-denoise i2i if the goal is exact two-row plates and four thagomizer spikes.",
    }
    REVIEW_JSON.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, REJECTED_V47, COMPARISON_V48):
        if not path.exists():
            raise FileNotFoundError(path)
    make_sheet()
    make_crops()
    write_review()
    print(SHEET_OUT)
    print(CROP_OUT)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
