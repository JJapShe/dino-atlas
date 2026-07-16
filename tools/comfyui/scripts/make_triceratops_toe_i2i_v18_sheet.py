import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSET_ROOT / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
CURRENT_CROPS = ASSET_ROOT / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"
GUIDE = ASSET_ROOT / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"
REJECT_V17 = ASSET_ROOT / "triceratops-schedule-i2i-rejection-sheet-v17.png"
COMPARISON_V18 = ASSET_ROOT / "triceratops-horridus-toe-i2i-comparison-v18.png"

SHEET_OUT = ASSET_ROOT / "triceratops-toe-i2i-v18-review-sheet.png"
CROP_OUT = ASSET_ROOT / "triceratops-toe-i2i-v18-crops.png"
REVIEW_JSON = REVIEW_ROOT / "trike_toe_i2i_v18_review.json"


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
            "title": "current v9: keep first",
            "note": "Best low-body candidate: skull-attached frill, three horns, closed beak, long tail, and visible non-hoofed toes.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v9 crop gate",
            "note": "Use this to check beak seam, frill attachment, front/rear toes, low body, and long tail.",
        },
        {
            "path": GUIDE,
            "title": "skull/frill body-lock guide",
            "note": "Structure reference for preserving the low ceratopsian body while tightening only frill, horns, beak, and toes.",
        },
        {
            "path": REJECT_V17,
            "title": "reject v17: mouth reopens",
            "note": "Denoise 0.30 schedule+i2i kept the low body but reopened the closed-beak gate with visible teeth.",
        },
        {
            "path": COMPARISON_V18,
            "title": "compare v18: toe i2i d0.18",
            "note": "Closed beak survives and body remains low, but toes/frill/body detail do not clearly beat v9.",
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
        ("current v9 full body", CURRENT, (0, 0, 1672, 940)),
        ("current v9 closed beak", CURRENT, (0, 360, 430, 620)),
        ("current v9 head / frill", CURRENT, (0, 120, 680, 560)),
        ("current v9 front toes", CURRENT, (360, 600, 760, 860)),
        ("current v9 rear toes / tail", CURRENT, (730, 590, 1660, 820)),
        ("v18 full body", COMPARISON_V18, (0, 0, 1672, 940)),
        ("v18 closed beak preserved", COMPARISON_V18, (0, 360, 430, 620)),
        ("v18 head / frill", COMPARISON_V18, (0, 120, 680, 560)),
        ("v18 front toes", COMPARISON_V18, (360, 600, 760, 860)),
        ("v18 rear toes / tail", COMPARISON_V18, (730, 590, 1660, 820)),
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
        "taxonId": "triceratops-horridus",
        "experiment": "toe_i2i_v18",
        "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
        "outputImage": str(COMPARISON_V18.relative_to(ROOT)).replace("\\", "/"),
        "reviewSheet": str(SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
        "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
        "promptId": "toe_review_01",
        "seed": 2026070443,
        "denoise": 0.18,
        "decision": "anatomy_review_comparison",
        "reasons": [
            "closed-beak gate survives unlike v17",
            "low elongated ceratopsian body and long tail remain close to v9",
            "front and rear toes remain visible",
            "not a clear upgrade over v9 for frill detail, toe clarity, or representative polish",
        ],
        "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
        "nextRoute": "Keep v9 first. Use more localized toe or frill masking, or ceratopsian-specific LoRA/control, rather than whole-body i2i if the current beak/frill/body balance does not improve clearly.",
    }
    REVIEW_JSON.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, REJECT_V17, COMPARISON_V18):
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
