import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
COMFY_OUTPUT = ROOT / "tools" / "comfyui" / "ComfyUI" / "output" / "dino_atlas"
REVIEW_DIR = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"

CURRENT = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSETS / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
PREVIOUS_REJECTION = ASSETS / "stegosaurus-plate-base-offset-v59-v60-rejection-crops.png"
V61_GUIDE_SOURCE = OUTPUTS / "stego_v6_broad_plate_graft_v61_v1b.png"
V61_MASK_SOURCE = OUTPUTS / "stego_v6_broad_plate_graft_v61_v1b-mask.png"
V61_CONTACT_SOURCE = OUTPUTS / "stego_v6_broad_plate_graft_v61-contact-sheet.png"
V62_CONTACT_SOURCE = OUTPUTS / "stegosaurus_plate_graft_naturalize_v62-contact-sheet.png"
V62_SELECTED_SOURCE = COMFY_OUTPUT / "stegosaurus_plate_graft_naturalize_v62_custom_stegosaurus-stenops_d24_00002_.png"
V63_CONTACT_SOURCE = OUTPUTS / "stego_synthetic_seed_v63-contact-sheet.png"
V63_SELECTED_SOURCE = OUTPUTS / "stego_synthetic_seed_v63_plate_count_01_seed2026071003.png"

V61_GUIDE_OUT = ASSETS / "stegosaurus-stenops-broad-plate-graft-guide-v61.png"
V61_MASK_OUT = ASSETS / "stegosaurus-broad-plate-graft-mask-v61.png"
V62_REJECTION_OUT = ASSETS / "stegosaurus-stenops-plate-graft-naturalize-rejected-v62.png"
V63_REJECTION_OUT = ASSETS / "stegosaurus-stenops-synthetic-platecount-rejected-v63.png"
REVIEW_SHEET_OUT = ASSETS / "stegosaurus-plate-graft-v61-v63-rejection-sheet.png"
CROPS_OUT = ASSETS / "stegosaurus-plate-graft-v61-v63-rejection-crops.png"
REVIEW_JSON_OUT = REVIEW_DIR / "stego_plate_graft_v61_v63_review.json"


def fit(image, size):
    canvas = Image.new("RGB", size, (242, 239, 231))
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def rel(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def copy_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    copies = [
        (V61_GUIDE_SOURCE, V61_GUIDE_OUT),
        (V61_MASK_SOURCE, V61_MASK_OUT),
        (V62_SELECTED_SOURCE, V62_REJECTION_OUT),
        (V63_SELECTED_SOURCE, V63_REJECTION_OUT),
    ]
    for src, dst in copies:
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, dst)


def wrap(draw, xy, text, max_chars=54, max_lines=3):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    for index, line in enumerate(lines[:max_lines]):
        draw.text((xy[0], xy[1] + index * 16), line, fill=(48, 43, 37), font=ImageFont.load_default())


def panel(path, title, note, size=(430, 246)):
    tile = Image.new("RGB", (size[0], size[1] + 100), (245, 243, 236))
    image = Image.open(path).convert("RGB")
    tile.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((10, size[1] + 10), title, fill=(134, 60, 44), font=ImageFont.load_default())
    wrap(draw, (10, size[1] + 32), note)
    return tile


def make_review_sheet():
    items = [
        panel(CURRENT, "current v6 primary", "Still first: natural body, readable plates, four-spike tail gate."),
        panel(V61_GUIDE_SOURCE, "v61 broad-plate graft guide", "Plate count improves but the plates read as pasted flat panels."),
        panel(V62_SELECTED_SOURCE, "v62 naturalized graft rejection", "Low-denoise naturalization keeps pasted-panel look and soft body boundary."),
        panel(V63_SELECTED_SOURCE, "v63 synthetic prompt rejection", "Prompt-only plate-count route drifts into thin comb/spike row."),
        panel(V61_CONTACT_SOURCE, "v61 graft sweep", "Useful structure experiment, not app-ready paleoart."),
        panel(V62_CONTACT_SOURCE, "v62 naturalize sweep", "All six outputs fail the natural plate integration gate."),
        panel(V63_CONTACT_SOURCE, "v63 prompt-only sweep", "No seed beats v6 across plate shape, body, and thagomizer together."),
        panel(PREVIOUS_REJECTION, "previous v59/v60 gate", "Base/gap offset route also stayed too close to v6."),
    ]
    cols = 4
    rows = 2
    header_h = 58
    sheet = Image.new("RGB", (cols * 430, header_h + rows * 346), (232, 228, 219))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, header_h), fill=(48, 67, 49))
    draw.text((14, 14), "Stegosaurus v61-v63 rejection: plate geometry needs real model support", fill=(245, 243, 236), font=ImageFont.load_default())
    draw.text((14, 34), "Keep v6 first; do not repeat pasted-plate grafts or prompt-only comb routes.", fill=(224, 228, 216), font=ImageFont.load_default())
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * 430, header_h + (idx // cols) * 346))
    REVIEW_SHEET_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(REVIEW_SHEET_OUT)


def crop_tile(path, title, box, size=(300, 150)):
    image = Image.open(path).convert("RGB")
    crop = image.crop(box)
    tile = Image.new("RGB", (size[0], size[1] + 34), (245, 243, 236))
    tile.paste(fit(crop, size), (0, 0))
    ImageDraw.Draw(tile).text((8, size[1] + 10), title[:48], fill=(48, 43, 37), font=ImageFont.load_default())
    return tile


def make_crops():
    paths = [
        ("v6 current", CURRENT),
        ("v61 pasted guide", V61_GUIDE_SOURCE),
        ("v62 naturalize reject", V62_SELECTED_SOURCE),
        ("v63 prompt reject", V63_SELECTED_SOURCE),
    ]
    crop_defs = [
        ("full", (0, 0, 1792, 1024), (340, 195)),
        ("plate band", (130, 40, 1335, 560), (360, 155)),
        ("tail/thagomizer", (1210, 420, 1792, 760), (300, 160)),
        ("feet/body", (120, 555, 1180, 900), (340, 135)),
    ]
    header_h = 48
    row_h = 230
    sheet_w = 1340
    sheet = Image.new("RGB", (sheet_w, header_h + len(paths) * row_h), (232, 228, 219))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, header_h), fill=(72, 56, 43))
    draw.text((12, 14), "Stegosaurus v61-v63 crops: reject if plates improve by becoming pasted panels or comb spikes", fill=(245, 243, 236), font=ImageFont.load_default())
    for row, (label, path) in enumerate(paths):
        y = header_h + row * row_h
        draw.text((10, y + 12), label, fill=(52, 48, 42), font=ImageFont.load_default())
        x = 116
        for title, box, size in crop_defs:
            tile = crop_tile(path, title, box, size)
            sheet.paste(tile, (x, y + 20))
            x += size[0] + 18
    sheet.save(CROPS_OUT)


def write_review_json():
    REVIEW_JSON_OUT.write_text(
        json.dumps(
            {
                "taxonId": "stegosaurus-stenops",
                "experiment": "plate_graft_v61_v63",
                "decision": "keep_current_primary",
                "currentPrimary": rel(CURRENT),
                "rejections": [
                    {
                        "asset": rel(V61_GUIDE_OUT),
                        "reason": "Improves plate count as a structure guide, but the plates look pasted and flat.",
                    },
                    {
                        "asset": rel(V62_REJECTION_OUT),
                        "reason": "Naturalization does not integrate the grafted plates; the body/plate boundary remains soft and artificial.",
                    },
                    {
                        "asset": rel(V63_REJECTION_OUT),
                        "reason": "Prompt-only synthetic seed drifts into thin comb-like spines rather than broad separate Stegosaurus plates.",
                    },
                ],
                "reviewSheet": rel(REVIEW_SHEET_OUT),
                "cropSheet": rel(CROPS_OUT),
                "nextRoute": "Do not repeat plate graft naturalization or prompt-only plate-count sweeps. Build a Stegosauridae-specific LoRA or a stronger plate-structure training set before another naturalization pass.",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, PREVIOUS_REJECTION, V61_GUIDE_SOURCE, V61_MASK_SOURCE, V61_CONTACT_SOURCE, V62_CONTACT_SOURCE, V62_SELECTED_SOURCE, V63_CONTACT_SOURCE, V63_SELECTED_SOURCE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    copy_assets()
    make_review_sheet()
    make_crops()
    write_review_json()
    for path in [V61_GUIDE_OUT, V61_MASK_OUT, V62_REJECTION_OUT, V63_REJECTION_OUT, REVIEW_SHEET_OUT, CROPS_OUT, REVIEW_JSON_OUT]:
        print(path)


if __name__ == "__main__":
    main()
