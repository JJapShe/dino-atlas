import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ankylosaur_armor_tailclub" / "review"

CURRENT = ASSET_ROOT / "ankylosaurus-magniventris-broadskull-singleclub-imagegen-v5.png"
CURRENT_CROPS = ASSET_ROOT / "ankylosaurus-broadskull-singleclub-crops-v5.png"
GUIDE = ASSET_ROOT / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"
OSTEODERM = ASSET_ROOT / "ankylosaurus-magniventris-schedule-i2i-osteoderm-comparison-v12.png"
CROP_READY = ASSET_ROOT / "ankylosaurus-magniventris-schedule-i2i-cropready-comparison-v12.png"
HORN_RISK = ASSET_ROOT / "ankylosaurus-magniventris-hornrisk-comparison-v5.png"
LONG_BODY = ASSET_ROOT / "ankylosaurus-magniventris-compactclub-longbody-comparison-v5.png"

CONTACT_OUT = ASSET_ROOT / "ankylosaurus-review-options-v12.png"
CROP_OUT = ASSET_ROOT / "ankylosaurus-schedule-i2i-crops-v12.png"
REVIEW_OUT = REVIEW_ROOT / "anky_schedule_i2i_v12_review.json"


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
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * line_h), line, fill=fill, font=font)


def make_contact_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v5: keep first",
            "note": "Strongest current representative: broad blunt skull, low armored body, four visible feet, and one attached oval club.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v5 crop gate",
            "note": "Use this to compare skull, armor rows, single club, front feet, rear feet, and v5 rejection gates.",
        },
        {
            "path": GUIDE,
            "title": "armor / tail-club structure guide",
            "note": "Reference target for broad skull, low armor rows, four sturdy feet, and one fused tail club.",
        },
        {
            "path": OSTEODERM,
            "title": "v12 schedule+i2i: osteoderm comparison",
            "note": "Keeps the low body and club; useful comparison, but it is not clearly stronger than v5 at app scale.",
        },
        {
            "path": CROP_READY,
            "title": "v12 schedule+i2i: crop-ready comparison",
            "note": "Similar to the osteoderm pass; feet and club remain readable, but v5 still has the stronger selected read.",
        },
        {
            "path": HORN_RISK,
            "title": "v5 rejection gate: horn-risk",
            "note": "Armor and club are strong, but horn-like skull projections block representative promotion.",
        },
        {
            "path": LONG_BODY,
            "title": "v5 long-body comparison",
            "note": "Good compact club comparison, but the torso and tail read less squat than the selected v5 candidate.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 72
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:80], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 30), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("current v5 full body - keep first", CURRENT, (0, 0, 1774, 887)),
        ("current v5 broad skull", CURRENT, (65, 315, 500, 585)),
        ("current v5 armor rows", CURRENT, (380, 205, 1185, 520)),
        ("current v5 single attached club", CURRENT, (1325, 320, 1745, 575)),
        ("v12 osteoderm full body", OSTEODERM, (0, 0, 1774, 887)),
        ("v12 osteoderm skull", OSTEODERM, (65, 315, 500, 585)),
        ("v12 osteoderm tail club", OSTEODERM, (1325, 320, 1745, 575)),
        ("v12 crop-ready full body", CROP_READY, (0, 0, 1774, 887)),
        ("v12 crop-ready feet", CROP_READY, (270, 570, 1285, 825)),
        ("v5 horn-risk rejection", HORN_RISK, (0, 0, 1672, 941)),
    ]

    cols = 2
    thumb_w = 380
    thumb_h = 250
    label_h = 36
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

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def write_review_json():
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "ankylosaurus-magniventris",
                "experiment": "schedule_i2i_v12",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "outputs": [
                    str(OSTEODERM.relative_to(ROOT)).replace("\\", "/"),
                    str(CROP_READY.relative_to(ROOT)).replace("\\", "/"),
                ],
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "comparison_only",
                "reasons": [
                    "the attached single tail club and broad low body survive",
                    "neither output clearly improves the current v5 primary",
                    "v5 remains the stronger app-scale representative read",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Use a stronger ankylosaurid LoRA or more local skull/club masking before replacing v5; avoid clean-corners postprocessing when it creates lower-frame blocks.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, GUIDE, OSTEODERM, CROP_READY, HORN_RISK, LONG_BODY):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    write_review_json()
    print(CONTACT_OUT)
    print(CROP_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
