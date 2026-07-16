import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROP = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
GUIDE = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-v1.png"
REJECTED = ASSET_ROOT / "stegosaurus-stenops-schedule-i2i-v6source-rejected-v47.png"

CONTACT_OUT = ASSET_ROOT / "stegosaurus-schedule-i2i-rejection-sheet-v47.png"
REVIEW_OUT = REVIEW_ROOT / "stego_schedule_i2i_v47_review.json"


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
            "title": "current v6: keep first",
            "note": "Keeps the stronger natural body, broad separated plates, planted feet, and countable four-spike tail gate.",
        },
        {
            "path": CURRENT_CROP,
            "title": "current v6 crop gate",
            "note": "Use this to compare plate topology, plate surface, feet, small head, and four thagomizer spikes.",
        },
        {
            "path": GUIDE,
            "title": "plate topology structure guide",
            "note": "The schedule+i2i route should preserve staggered rows, visible gaps, and exactly four tail spikes.",
        },
        {
            "path": REJECTED,
            "title": "reject v47: schedule+i2i from v6",
            "note": "Reject: corner artifacts, unstable four-spike count, and no clear gain over the current v6 primary.",
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
                "taxonId": "stegosaurus-stenops",
                "experiment": "schedule_i2i_v47",
                "sourceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "outputImage": str(REJECTED.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(CONTACT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "rejected",
                "reasons": [
                    "large lower-corner artifacts remain visible",
                    "tail spike count is not reliably exactly four",
                    "plate topology is not enough of an improvement over current v6",
                ],
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Use stronger Stegosauridae LoRA or reference-conditioned ControlNet/i2i that locks two staggered plate rows and four thagomizer spikes without image-frame artifacts.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROP, GUIDE, REJECTED):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    write_review_json()
    print(CONTACT_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
