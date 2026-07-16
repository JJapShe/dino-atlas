import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "early_sauropodomorph_plateosaurus" / "review"

PRIMARY = ASSET_ROOT / "plateosaurus-engelhardti-tripod-controlnet-v1.png"
THUMBTIP_OUTPUT = OUTPUT_ROOT / "plateosaurus_thumbtip_cue_v1_plateosaurus_thumb_claw_tips_plateosaurus-engelhardti_seed2026062602_d16.png"
THUMBTIP_ASSET = ASSET_ROOT / "plateosaurus-engelhardti-thumbtip-cue-v1.png"
FORELIMB_REF = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-ref-ipcontrol-v1.png"
GUIDE = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-reference-guide-v1.png"
SIX_LEG_REJECTION = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"
BALANCE_CONTACT = OUTPUT_ROOT / "plateosaurus_forelimb_balance_v1-contact-sheet.png"
THUMBTIP_CONTACT = OUTPUT_ROOT / "plateosaurus_thumbtip_cue_v1-contact-sheet.png"
THUMBTIP_CROPS = OUTPUT_ROOT / "plateosaurus_thumbtip_cue_v1-crop-sheet.png"


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


def make_crop_sheet(output):
    items = [
        ("current primary forelimb", PRIMARY),
        ("thumb-tip cue v1", THUMBTIP_ASSET),
        ("forelimb-ref comparison", FORELIMB_REF),
        ("six-leg rejection", SIX_LEG_REJECTION),
    ]
    crop_box = (315, 420, 570, 670)
    thumb_w = 320
    thumb_h = 240
    label_h = 34
    cols = 2
    rows = 2
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (label, path) in enumerate(items):
        image = Image.open(path).convert("RGB").crop(crop_box)
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    if not THUMBTIP_OUTPUT.exists():
        raise FileNotFoundError(THUMBTIP_OUTPUT)

    THUMBTIP_ASSET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(THUMBTIP_OUTPUT, THUMBTIP_ASSET)

    contact = REVIEW_ROOT / "plateosaurus_thumbtip_cue_v1_contact_sheet.png"
    crop_sheet = REVIEW_ROOT / "plateosaurus_thumbtip_cue_v1_forelimb_crops.png"
    app_contact = ASSET_ROOT / "plateosaurus-review-options-v8.png"
    app_crops = ASSET_ROOT / "plateosaurus-forelimb-crops-v3.png"

    items = [
        {
            "path": PRIMARY,
            "title": "current primary: count-safe tripod body",
            "note": "Keeps the two-hind-leg gate and overall body; hand/thumb cue stays weak.",
        },
        {
            "path": THUMBTIP_ASSET,
            "title": "thumb-tip cue v1: comparison only",
            "note": "Small hand-tip inpaint preserves limb count, but the thumb-claw cue is still subtle.",
        },
        {
            "path": FORELIMB_REF,
            "title": "forelimb-reference IP-Control comparison",
            "note": "Hands and head improve, but hind-leg contact is weaker than the primary.",
        },
        {
            "path": SIX_LEG_REJECTION,
            "title": "rejected: previous broad forelimb inpaint",
            "note": "Hand cue becomes clearer, but the overlapping area reads as extra legs.",
        },
        {
            "path": THUMBTIP_CONTACT,
            "title": "thumb-tip tiny-mask sweep",
            "note": "Low-denoise sweep succeeds as a no-extra-limb test, not as a final hand solution.",
        },
        {
            "path": BALANCE_CONTACT,
            "title": "rejected: forelimb balance ControlNet sweep",
            "note": "Lower ControlNet still weakens body/leg gate or drifts away from Plateosaurus.",
        },
    ]
    make_contact_sheet(items, contact)
    make_contact_sheet(items, app_contact)
    make_crop_sheet(crop_sheet)
    make_crop_sheet(app_crops)

    review = {
        "taxonId": "plateosaurus-engelhardti",
        "round": "plateosaurus_thumbtip_cue_v1",
        "date": "2026-06-26",
        "objective": "Test a safer Plateosaurus forelimb/thumb-claw improvement after previous broad forelimb edits created a six-leg read.",
        "selectedComparison": {
            "asset": str(THUMBTIP_ASSET.relative_to(ROOT)).replace("\\", "/"),
            "sourceOutput": str(THUMBTIP_OUTPUT.relative_to(ROOT)).replace("\\", "/"),
            "method": "tiny hand-tip inpaint over the current tripod primary",
            "settings": {
                "seed": 2026062602,
                "denoise": 0.16,
                "maskPreset": "plateosaurus_thumb_claw_tips",
                "checkpoint": "RealVisXL_V5.0_fp16.safetensors",
            },
            "reason": "It preserves the current primary's tail, two-hind-leg stance, and body while adding the least disruptive hand-tip cue.",
            "status": "comparison only; not promoted over the current primary",
            "remainingRisk": "The five-fingered hand and large thumb-claw cue remain too subtle for final approval.",
        },
        "rejected": [
            {
                "asset": "tools/comfyui/outputs/plateosaurus_forelimb_balance_v1-contact-sheet.png",
                "reason": "Lower-strength ControlNet from the forelimb/head guide either weakened hind-leg/ground-contact readability or drifted away from a Plateosaurus-like body.",
            },
            {
                "asset": "assets/dinosaurs/plateosaurus-engelhardti-forelimb-inpaint-v1.png",
                "reason": "Previous broad forelimb inpaint remains a six-leg rejection and must not be promoted.",
            },
        ],
        "reviewSheets": {
            "contactSheet": str(contact.relative_to(ROOT)).replace("\\", "/"),
            "forelimbCrops": str(crop_sheet.relative_to(ROOT)).replace("\\", "/"),
            "appContactSheet": str(app_contact.relative_to(ROOT)).replace("\\", "/"),
            "appForelimbCrops": str(app_crops.relative_to(ROOT)).replace("\\", "/"),
        },
        "nextRecommendation": "Keep the tripod primary first. The next meaningful improvement needs an early-sauropodomorph/Plateosaurus mini-LoRA or a staged workflow that first preserves the two-hind-leg body gate, then handles hand detail at close range.",
    }
    review_path = REVIEW_ROOT / "plateosaurus_thumbtip_cue_v1_review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"asset": str(THUMBTIP_ASSET), "contactSheet": str(contact), "forelimbCrops": str(crop_sheet)}, indent=2))


if __name__ == "__main__":
    main()
