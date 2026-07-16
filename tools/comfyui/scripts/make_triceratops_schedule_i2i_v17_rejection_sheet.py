import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSET_ROOT / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
CURRENT_CROP = ASSET_ROOT / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"
GUIDE = ASSET_ROOT / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"
REJECT_SKULL = ASSET_ROOT / "triceratops-horridus-schedule-i2i-skullfrill-rejected-v17.png"
REJECT_TOE = ASSET_ROOT / "triceratops-horridus-schedule-i2i-toereview-rejected-v17.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-schedule-i2i-rejection-sheet-v17.png"
REVIEW_OUT = REVIEW_ROOT / "trike_schedule_i2i_v17_review.json"


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
            "title": "current v9: keep first",
            "note": "Best current low-body candidate: skull-attached frill, three horns, closed beak, long tail, and visible non-hoofed toes.",
        },
        {
            "path": CURRENT_CROP,
            "title": "current v9 crop gate",
            "note": "Use this to check closed beak, skull/frill attachment, front and rear toes, and low-body/long-tail silhouette.",
        },
        {
            "path": GUIDE,
            "title": "skull/frill body-lock guide",
            "note": "Future i2i or ControlNet should preserve the v9 body while tightening only frill, horn, beak, and toe details.",
        },
        {
            "path": REJECT_SKULL,
            "title": "reject v17: skull/frill schedule+i2i",
            "note": "Reject: the low body remains, but the closed-beak gate breaks and visible teeth return.",
        },
        {
            "path": REJECT_TOE,
            "title": "reject v17: toe-review schedule+i2i",
            "note": "Reject: toes stay visible, but the mouth opens with teeth and does not beat the v9 closed-beak candidate.",
        },
    ]

    cols = 2
    thumb_w = 520
    thumb_h = 330
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


def write_review_json():
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "triceratops-horridus",
                "experiment": "schedule_i2i_v17",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "outputs": [
                    str(REJECT_SKULL.relative_to(ROOT)).replace("\\", "/"),
                    str(REJECT_TOE.relative_to(ROOT)).replace("\\", "/"),
                ],
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "rejected",
                "reasons": [
                    "both low-denoise outputs reopen the closed-beak gate",
                    "visible teeth return in the mouth area",
                    "neither output is a clear improvement over the current v9 primary",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Use lower-strength local beak/frill masking or a ceratopsian-specific LoRA/ControlNet route; do not promote whole-body i2i if closed beak breaks.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROP, GUIDE, REJECT_SKULL, REJECT_TOE):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    write_review_json()
    print(CONTACT_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
