import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
IDENTITY_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png"
V22_SHEET = ASSET_ROOT / "velociraptor-schedule-i2i-rejection-sheet-v22.png"
V23 = ASSET_ROOT / "velociraptor-mongoliensis-identity-controlnet-rejected-v23.png"
V24 = ASSET_ROOT / "velociraptor-mongoliensis-v9-identity-ipi2i-rejected-v24.png"

SHEET_OUT = ASSET_ROOT / "velociraptor-identity-v23-v24-rejection-sheet.png"
CROP_OUT = ASSET_ROOT / "velociraptor-identity-v23-v24-rejection-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_identity_v23_v24_review.json"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def wrap(text, max_chars=64):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_note(draw, xy, text, font, fill, max_lines=2):
    x, y = xy
    for idx, line in enumerate(wrap(text)[:max_lines]):
        draw.text((x, y + idx * 15), line, fill=fill, font=font)


def make_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v9: keep first",
            "note": "Best current balance: non-beak toothed snout, feathered body, folded hands, long tail, restrained attached sickle cue.",
        },
        {
            "path": CURRENT_CROPS,
            "title": "current v9 crop gate",
            "note": "Use this to compare head, folded arm feathers, feet, attached claw cue, and tail before promotion.",
        },
        {
            "path": IDENTITY_GUIDE,
            "title": "identity body-lock guide",
            "note": "Useful control reference only; direct ControlNet should not be promoted if it loses feathered dromaeosaur identity.",
        },
        {
            "path": V22_SHEET,
            "title": "previous v22 schedule+i2i failures",
            "note": "Earlier guided i2i did not beat v9; v23/v24 test the remaining ControlNet/IP-i2i paths.",
        },
        {
            "path": V23,
            "title": "reject v23: identity ControlNet",
            "note": "Clean body, but plumage weakens and attached raised second-toe sickle evidence is worse than v9.",
        },
        {
            "path": V24,
            "title": "reject v24: v9 IP-i2i with guide",
            "note": "Preserves some guide anatomy, but collapses into flat guide-like art and loses app-ready natural quality.",
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
        draw.text((8, thumb_h + 8), item["title"][:68], fill=(132, 61, 43), font=font)
        draw_note(draw, (8, thumb_h + 31), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(SHEET_OUT)


def make_crops():
    crops = [
        ("current v9 full - keep", CURRENT, (0, 0, 1672, 941)),
        ("current v9 toothed snout", CURRENT, (0, 120, 560, 380)),
        ("current v9 folded feathered hands", CURRENT, (300, 410, 760, 760)),
        ("current v9 foot / attached cue", CURRENT, (480, 570, 1085, 930)),
        ("reject v23 full", V23, (0, 0, 768, 512)),
        ("reject v23 head - generic", V23, (430, 80, 760, 250)),
        ("reject v23 weak plumage", V23, (260, 160, 600, 380)),
        ("reject v23 feet - no clear sickle", V23, (250, 285, 620, 505)),
        ("reject v24 full", V24, (0, 0, 768, 512)),
        ("reject v24 head - guide-flat", V24, (0, 95, 245, 250)),
        ("reject v24 arms - sketch-like", V24, (250, 230, 500, 420)),
        ("reject v24 feet - guide art", V24, (305, 300, 730, 505)),
    ]

    cols = 4
    thumb_w = 300
    thumb_h = 210
    label_h = 42
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    font = ImageFont.load_default()
    for idx, (label, path, box) in enumerate(crops):
        crop = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(crop, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), label[:52], fill=(42, 39, 35), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    sheet.save(CROP_OUT)


def write_review():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    review = {
        "taxon": "velociraptor-mongoliensis",
        "decision": "diagnostic_only_rejected",
        "currentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
        "outputs": [
            {
                "route": "identity_controlnet_v23",
                "seed": 2026070201,
                "strength": 0.50,
                "endPercent": 0.64,
                "image": str(V23.relative_to(ROOT)).replace("\\", "/"),
                "fail": [
                    "feathered dromaeosaur identity weakens",
                    "attached raised second-toe sickle claw is less clear than current v9",
                    "head and body read as a generic theropod instead of a feathered Velociraptor",
                ],
            },
            {
                "route": "v9_identity_ipadapter_i2i_v24",
                "seed": 2026070261,
                "denoise": 0.42,
                "ipWeight": 0.38,
                "image": str(V24.relative_to(ROOT)).replace("\\", "/"),
                "fail": [
                    "output collapses into flat guide-like art",
                    "not app-ready natural paleoart quality",
                    "does not improve the v9 head/feather/attached-sickle balance",
                ],
            },
        ],
        "reviewSheet": str(SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
        "cropSheet": str(CROP_OUT.relative_to(ROOT)).replace("\\", "/"),
        "nextAction": (
            "Keep v9 as primary. Future attempts should preserve the v9 natural image and use a more localized "
            "foot/head mask or stronger dromaeosaur-specific conditioning; do not promote guide-source whole-body "
            "ControlNet or IP-i2i outputs that lose feathers or natural image quality."
        ),
    }
    REVIEW_JSON.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    for path in (CURRENT, CURRENT_CROPS, IDENTITY_GUIDE, V22_SHEET, V23, V24):
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
