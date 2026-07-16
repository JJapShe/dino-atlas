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
LABEL_GUIDE = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-v1.png"
CLEAN_GUIDE = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-clean-v52.png"
V51_CROPS = ASSET_ROOT / "stegosaurus-plate-airgap-i2i-v51-crops.png"

V52_SELECTED_SOURCE = OUTPUT_ROOT / "next_stegosaurus_plate_topology_control_v52_stegosaurus-stenops_seed2026070301_s50_e62.png"
V53_SELECTED_SOURCE = OUTPUT_ROOT / "next_stegosaurus_clean_plate_topology_control_v53_stegosaurus-stenops_seed2026070312_s50_e57.png"
V52_CONTACT = OUTPUT_ROOT / "next_stegosaurus_plate_topology_control_v52-contact-sheet.png"
V53_CONTACT = OUTPUT_ROOT / "next_stegosaurus_clean_plate_topology_control_v53-contact-sheet.png"

V52_REJECT_OUT = ASSET_ROOT / "stegosaurus-stenops-plate-topology-control-rejected-v52.png"
V53_REJECT_OUT = ASSET_ROOT / "stegosaurus-stenops-clean-plate-topology-control-rejected-v53.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "stegosaurus-plate-topology-control-v52-v53-rejection-sheet.png"
CROPS_OUT = ASSET_ROOT / "stegosaurus-plate-topology-control-v52-v53-rejection-crops.png"
REVIEW_OUT = REVIEW_ROOT / "stego_plate_topology_control_v52_v53_review.json"


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
    shutil.copyfile(V52_SELECTED_SOURCE, V52_REJECT_OUT)
    shutil.copyfile(V53_SELECTED_SOURCE, V53_REJECT_OUT)


def make_review_sheet():
    items = [
        {
            "path": CURRENT,
            "title": "current v6: keep first",
            "note": "Natural representative still has the best body, plate, feet, and four-spike balance.",
        },
        {
            "path": CLEAN_GUIDE,
            "title": "clean topology guide v52",
            "note": "Text-free project-owned guide. Useful as a reference, but not enough as ControlNet alone.",
        },
        {
            "path": V52_CONTACT,
            "title": "v52 labeled-guide ControlNet",
            "note": "Reject: guide labels and lines bleed into outputs, with text-like artifacts.",
        },
        {
            "path": V53_CONTACT,
            "title": "v53 clean-guide ControlNet",
            "note": "Reject: text bleed is fixed, but plates drift into sail, comb, or spike-row reads.",
        },
        {
            "path": V52_REJECT_OUT,
            "title": "v52 selected rejection",
            "note": "Large readable plates, but text artifacts and weak thagomizer/body gates make it diagnostic only.",
        },
        {
            "path": V53_REJECT_OUT,
            "title": "v53 selected rejection",
            "note": "No text pollution, but dorsal plates become a continuous comb/sail and tail spikes are unreliable.",
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
        ("v52 labeled-guide reject", V52_REJECT_OUT),
        ("v53 clean-guide reject", V53_REJECT_OUT),
    ]
    crops = [
        ("full body", (0.0, 0.06, 1.0, 0.92), (330, 190)),
        ("plate row", (0.16, 0.04, 0.83, 0.50), (330, 190)),
        ("head", (0.0, 0.22, 0.28, 0.58), (250, 170)),
        ("feet", (0.15, 0.58, 0.78, 0.98), (330, 170)),
        ("tail/thagomizer", (0.58, 0.28, 1.0, 0.78), (310, 170)),
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
                "experiment": "plate_topology_control_v52_v53",
                "currentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "cleanGuide": str(CLEAN_GUIDE.relative_to(ROOT)).replace("\\", "/"),
                "labeledGuideRejection": str(V52_REJECT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cleanGuideRejection": str(V53_REJECT_OUT.relative_to(ROOT)).replace("\\", "/"),
                "reviewSheet": str(REVIEW_SHEET_OUT.relative_to(ROOT)).replace("\\", "/"),
                "cropSheet": str(CROPS_OUT.relative_to(ROOT)).replace("\\", "/"),
                "decision": "diagnostic_only",
                "v52": {
                    "sourceGuide": str(LABEL_GUIDE.relative_to(ROOT)).replace("\\", "/"),
                    "seeds": [2026070301, 2026070302],
                    "strengths": [0.50, 0.62],
                    "endPercent": 0.62,
                    "reason": "Labeled topology guide causes text and line artifacts in ControlNet outputs.",
                },
                "v53": {
                    "sourceGuide": str(CLEAN_GUIDE.relative_to(ROOT)).replace("\\", "/"),
                    "seeds": [2026070311, 2026070312],
                    "strengths": [0.38, 0.50],
                    "endPercent": 0.58,
                    "reason": "Clean guide removes text bleed but still collapses separated plates into sail, comb, or spike-row reads.",
                },
                "keepCurrentPrimary": str(CURRENT.relative_to(ROOT)).replace("\\", "/"),
                "nextRoute": "Do not use the plate topology guide as plain canny ControlNet alone. Use it as a reference/control layer combined with v6 image conditioning, or train/use a Stegosauridae plate LoRA before another promotion attempt.",
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
        LABEL_GUIDE,
        CLEAN_GUIDE,
        V51_CROPS,
        V52_SELECTED_SOURCE,
        V53_SELECTED_SOURCE,
        V52_CONTACT,
        V53_CONTACT,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    copy_selected_assets()
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(V52_REJECT_OUT)
    print(V53_REJECT_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROPS_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
