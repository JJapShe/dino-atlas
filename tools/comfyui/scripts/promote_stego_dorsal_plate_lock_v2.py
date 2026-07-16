import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SELECTED_OUTPUT = OUTPUT_ROOT / "stego_dorsal_plate_lock_v2_natural_balance_style_transfer_stegosaurus-stenops_seed2026062504_iw12_cs66.png"
SELECTED_ASSET = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-natural-v1.png"
GUIDE_ASSET = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"


def draw_wrapped(draw, xy, text, font, fill, max_chars=58, line_h=15, max_lines=2):
    x, y = xy
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
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * line_h), line, fill=fill, font=font)


def make_contact_sheet(items, output, cols=2, thumb_w=430, thumb_h=278):
    label_h = 58
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, item in enumerate(items):
        image = Image.open(item["path"]).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:64], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def make_plate_crop_sheet(source, output):
    image = Image.open(source).convert("RGB")
    crops = [
        ("full row: countable separate plates", (160, 128, 1010, 455)),
        ("neck plates: small to medium", (160, 185, 430, 455)),
        ("mid-back plates: broad individual slabs", (390, 90, 765, 455)),
        ("hip/tail-base plates + thagomizer context", (710, 190, 1130, 470)),
    ]
    thumb_w = 360
    thumb_h = 220
    label_h = 34
    sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * 2), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (label, box) in enumerate(crops):
        crop = image.crop(box)
        crop.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:62], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % 2) * thumb_w, (idx // 2) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    if not SELECTED_OUTPUT.exists():
        raise FileNotFoundError(SELECTED_OUTPUT)

    SELECTED_ASSET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SELECTED_OUTPUT, SELECTED_ASSET)

    contact = REVIEW_ROOT / "stego_dorsal_plate_lock_v2_ipcontrol_contact_sheet.png"
    app_contact = ASSET_ROOT / "stegosaurus-review-options-v39.png"
    items = [
        {
            "path": SELECTED_ASSET,
            "title": "selected natural: dorsal plate lock v2",
            "note": "Best balance: broad separate plates remain visible while body stays natural enough.",
        },
        {
            "path": ASSET_ROOT / "stegosaurus-stenops-plate-readable-natural-v1.png",
            "title": "previous first image",
            "note": "Natural, but dorsal plates collapse toward too few rounded fins.",
        },
        {
            "path": GUIDE_ASSET,
            "title": "new ControlNet structure guide",
            "note": "Alternating broad plate row used to lock the next generation pass.",
        },
        {
            "path": OUTPUT_ROOT / "stego_dorsal_plate_lock_v2_ipcontrol_style_transfer_stegosaurus-stenops_seed2026062504_iw08_cs74.png",
            "title": "stronger control comparison",
            "note": "Plate row is strong, but body and legs inherit too much guide geometry.",
        },
        {
            "path": OUTPUT_ROOT / "stego_dorsal_plate_lock_v2_natural_balance_style_transfer_stegosaurus-stenops_seed2026062506_iw12_cs66.png",
            "title": "rejected seed: plate drift",
            "note": "More natural body, but plates drift toward darker spikes and less broad slabs.",
        },
        {
            "path": OUTPUT_ROOT / "stego_dorsal_plate_lock_v2_natural_balance_style_transfer_stegosaurus-stenops_seed2026062504_iw12_cs72.png",
            "title": "rejected strength: still guide-heavy",
            "note": "Acceptable plate row, but no meaningful anatomy gain over the selected candidate.",
        },
    ]
    make_contact_sheet(items, contact)
    make_contact_sheet(items, app_contact)

    crops = REVIEW_ROOT / "stego_dorsal_plate_lock_v2_ipcontrol_plate_crops.png"
    app_crops = ASSET_ROOT / "stegosaurus-plate-crops-v11.png"
    make_plate_crop_sheet(SELECTED_ASSET, crops)
    make_plate_crop_sheet(SELECTED_ASSET, app_crops)

    review = {
        "taxonId": "stegosaurus-stenops",
        "round": "stego_dorsal_plate_lock_v2_ipcontrol",
        "date": "2026-06-25",
        "objective": "Replace the current Stegosaurus first image after review found that its dorsal plates still do not read well enough.",
        "selected": {
            "asset": str(SELECTED_ASSET.relative_to(ROOT)).replace("\\", "/"),
            "sourceOutput": str(SELECTED_OUTPUT.relative_to(ROOT)).replace("\\", "/"),
            "method": "IP-Adapter + ControlNet using the new dorsal-plate-lock v2 guide",
            "settings": {
                "seed": 2026062504,
                "ipWeight": 0.12,
                "ipWeightType": "style transfer",
                "controlStrength": 0.66,
                "controlEnd": 0.78,
                "checkpoint": "RealVisXL_V5.0_fp16.safetensors",
            },
            "reason": "The dorsal row now keeps broad, separate, countable plates at app scale instead of collapsing into a few rounded fins.",
            "remainingRisk": "The far alternating row is still implied more than fully resolved, and the tail spikes are visible but not final paleoart quality.",
        },
        "rejected": [
            {
                "asset": "assets/dinosaurs/stegosaurus-stenops-plate-readable-natural-v1.png",
                "reason": "Previous first image remains natural, but the plates are too few, rounded, and fin-like for the new plate gate.",
            },
            {
                "asset": "tools/comfyui/outputs/stego_dorsal_plate_lock_v2_ipcontrol_style_transfer_stegosaurus-stenops_seed2026062504_iw08_cs74.png",
                "reason": "Better plate lock, but the body and legs are more guide-like than the selected lower-strength pass.",
            },
            {
                "asset": "tools/comfyui/outputs/stego_dorsal_plate_lock_v2_natural_balance_style_transfer_stegosaurus-stenops_seed2026062506_iw12_cs66.png",
                "reason": "More natural body but plate silhouettes become darker, thinner, and less broadly slab-like.",
            },
            {
                "asset": "tools/comfyui/outputs/stego_dorsal_plate_lock_v2_natural_balance_style_transfer_stegosaurus-stenops_seed2026062504_iw12_cs72.png",
                "reason": "Close to selected but does not improve anatomy enough to offset the stronger control look.",
            },
        ],
        "reviewSheets": {
            "contactSheet": str(contact.relative_to(ROOT)).replace("\\", "/"),
            "plateCrops": str(crops.relative_to(ROOT)).replace("\\", "/"),
            "appContactSheet": str(app_contact.relative_to(ROOT)).replace("\\", "/"),
            "appPlateCrops": str(app_crops.relative_to(ROOT)).replace("\\", "/"),
        },
        "nextRecommendation": "Keep the v2 selected candidate first for MVP, but do not call the Stegosaurus final until a dedicated stegosaur plate LoRA or higher-fidelity reference-conditioned workflow resolves the alternating two-row plates more naturally.",
    }
    review_path = REVIEW_ROOT / "stego_dorsal_plate_lock_v2_ipcontrol_review.json"
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"asset": str(SELECTED_ASSET), "contactSheet": str(contact), "plateCrops": str(crops)}, indent=2))


if __name__ == "__main__":
    main()
