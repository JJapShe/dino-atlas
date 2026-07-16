import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
CLEAN_GUIDE = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-clean-v52.png"
V52_V53_CROPS = ASSET_ROOT / "stegosaurus-plate-topology-control-v52-v53-rejection-crops.png"

V54_SELECTED_SOURCE = OUTPUT_ROOT / "next_stegosaurus_v6_clean_guide_ipcontrol_v54_style_transfer_stegosaurus-stenops_seed2026070322_iw38_cs34.png"
V55_SELECTED_SOURCE = OUTPUT_ROOT / "next_stegosaurus_v6_clean_guide_ipcontrol_v55_style_transfer_stegosaurus-stenops_seed2026070323_iw55_cs42.png"
V54_CONTACT = OUTPUT_ROOT / "next_stegosaurus_v6_clean_guide_ipcontrol_v54-contact-sheet.png"
V55_CONTACT = OUTPUT_ROOT / "next_stegosaurus_v6_clean_guide_ipcontrol_v55-contact-sheet.png"

V54_REJECT_OUT = ASSET_ROOT / "stegosaurus-stenops-v6-clean-guide-ipcontrol-rejected-v54.png"
V55_REJECT_OUT = ASSET_ROOT / "stegosaurus-stenops-v6-clean-guide-ipcontrol-rejected-v55.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "stegosaurus-v6-clean-guide-ipcontrol-v54-v55-rejection-sheet.png"
CROPS_OUT = ASSET_ROOT / "stegosaurus-v6-clean-guide-ipcontrol-v54-v55-rejection-crops.png"
REVIEW_OUT = REVIEW_ROOT / "stego_v6_clean_guide_ipcontrol_v54_v55_review.json"


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


def fractional_crop(image, box):
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def copy_selected_assets():
    shutil.copyfile(V54_SELECTED_SOURCE, V54_REJECT_OUT)
    shutil.copyfile(V55_SELECTED_SOURCE, V55_REJECT_OUT)


def make_review_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v6: keep first",
            "note": "Still the strongest natural representative for body, separated plates, feet, and thagomizer.",
        },
        {
            "path": CLEAN_GUIDE,
            "title": "clean topology guide",
            "note": "Useful reference layer, but its line control still overpowers plate shape when used directly.",
        },
        {
            "path": V54_CONTACT,
            "title": "v54 low IP-Control sweep",
            "note": "Reject: naturalistic, but Stegosaurus identity and broad plate/thagomizer gates collapse.",
        },
        {
            "path": V55_CONTACT,
            "title": "v55 higher IP-Control sweep",
            "note": "Reject: v6 style improves, but plates fuse into fan/sail shapes and tail spikes fail.",
        },
        {
            "path": V54_REJECT_OUT,
            "title": "v54 selected rejection",
            "note": "Shows low-strength hybrid drift: generic herbivore body, weak plates, no reliable thagomizer.",
        },
        {
            "path": V55_REJECT_OUT,
            "title": "v55 selected rejection",
            "note": "Shows high reference weight failure: large plate fan, lost four-spike tail gate, odd pose.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 242
    label_h = 74
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

    sheet.save(REVIEW_SHEET_OUT)


def make_crop_sheet():
    rows = [
        ("v6 current", CURRENT),
        ("v54 low hybrid reject", V54_REJECT_OUT),
        ("v55 high hybrid reject", V55_REJECT_OUT),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (330, 190)),
        ("plate row", (0.16, 0.02, 0.82, 0.50), (330, 190)),
        ("head/neck", (0.0, 0.18, 0.34, 0.62), (250, 170)),
        ("feet/body", (0.13, 0.52, 0.78, 0.98), (330, 170)),
        ("tail/thagomizer", (0.58, 0.25, 1.0, 0.78), (310, 170)),
    ]

    font = ImageFont.load_default()
    gap = 10
    label_h = 38
    col_w = 340
    row_h = 228
    sheet_w = gap + len(crops) * (col_w + gap)
    sheet_h = gap + len(rows) * (row_h + label_h + gap)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (232, 228, 218))

    for row_idx, (row_label, path) in enumerate(rows):
        image = Image.open(path).convert("RGB")
        y = gap + row_idx * (row_h + label_h + gap)
        for col_idx, (crop_label, box, size) in enumerate(crops):
            x = gap + col_idx * (col_w + gap)
            crop = fractional_crop(image, box)
            tile = Image.new("RGB", (col_w, row_h + label_h), (245, 243, 236))
            tile.paste(fit(crop, size), ((col_w - size[0]) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((8, row_h + 7), f"{row_label}: {crop_label}"[:54], fill=(43, 39, 34), font=font)
            sheet.paste(tile, (x, y))

    sheet.save(CROPS_OUT)


def write_review_json():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "v6_clean_guide_ipcontrol_v54_v55",
                "currentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "referenceImage": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "controlGuide": str(CLEAN_GUIDE.relative_to(ROOT)).replace("\\", "/"),
                "v54Rejection": str(V54_REJECT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "v55Rejection": str(V55_REJECT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(REVIEW_SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROPS_OUT.relative_to(ROOT)).replace("\\", "/"),
                "previousGuideOnlyGate": str(V52_V53_CROPS.relative_to(ROOT)).replace("\\", "/"),
                "decision": "diagnostic_only",
                "v54": {
                    "seeds": [2026070321, 2026070322],
                    "ipWeights": [0.28, 0.38],
                    "controlStrengths": [0.34],
                    "controlEnd": 0.56,
                    "reason": "Low IP-Control naturalizes the image but loses Stegosaurus plate and thagomizer identity.",
                },
                "v55": {
                    "seeds": [2026070323, 2026070324],
                    "ipWeights": [0.55],
                    "controlStrengths": [0.42, 0.54],
                    "controlEnd": 0.52,
                    "reason": "Higher reference weight preserves some texture, but plates fuse into fan/sail shapes and tail-spike evidence fails.",
                },
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "A Stegosauridae plate LoRA or plate-row-specific conditioning is needed; v6+clean-guide IP-Control alone does not preserve natural representative quality and exact plate/thagomizer gates together.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (
        CURRENT,
        CURRENT_CROPS,
        CLEAN_GUIDE,
        V52_V53_CROPS,
        V54_SELECTED_SOURCE,
        V55_SELECTED_SOURCE,
        V54_CONTACT,
        V55_CONTACT,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    copy_selected_assets()
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(V54_REJECT_OUT)
    print(V55_REJECT_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROPS_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
