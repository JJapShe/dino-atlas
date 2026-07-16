import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / "tools" / "comfyui" / "outputs" / "gallery-slot-generation-plan.json"
OUT_DIR = ROOT / "tmp" / "gallery-slot-audit"
MANIFEST = OUT_DIR / "manifest.json"

TAXA_PER_SHEET = 6
MAX_SLOTS = 7
LABEL_W = 290
CELL_W = 220
IMAGE_H = 142
CELL_H = 202
HEADER_H = 76
GAP = 10

ROLE_LABELS = {
    "representative": "REP",
    "color-pattern": "COLOR",
    "habitat-ecology": "HABITAT",
    "identity-anatomy": "ANATOMY",
    "interaction": "INTERACT",
    "social-growth-defense": "SOCIAL",
    "alternate-habitat-behavior": "ALT",
}

STATUS_COLORS = {
    "manual-review": (48, 122, 88),
    "manual-review-unregistered": (185, 124, 45),
    "generate": (164, 67, 61),
}


def load_font(size):
    for candidate in (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def fit_image(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (30, 34, 35))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def shorten(value, limit):
    value = str(value or "")
    return value if len(value) <= limit else f"{value[: limit - 3]}..."


def make_slot_cell(slot, fonts):
    cell = Image.new("RGB", (CELL_W, CELL_H), (42, 46, 47))
    draw = ImageDraw.Draw(cell)
    source = slot.get("currentSource") or slot.get("suggestedUnregisteredSource")
    if source:
        image_path = ROOT / source
        if image_path.exists():
            with Image.open(image_path) as image:
                cell.paste(fit_image(image, (CELL_W, IMAGE_H)), (0, 0))
        else:
            draw.rectangle((0, 0, CELL_W, IMAGE_H), fill=(110, 42, 42))
            draw.text((12, 58), "MISSING FILE", fill=(255, 230, 220), font=fonts["body"])
    else:
        draw.rectangle((0, 0, CELL_W, IMAGE_H), fill=(75, 43, 43))
        draw.text((55, 58), "GENERATE", fill=(255, 220, 210), font=fonts["body"])

    status = slot.get("status", "generate")
    status_color = STATUS_COLORS.get(status, (110, 110, 110))
    draw.rectangle((0, IMAGE_H, CELL_W, CELL_H), fill=(28, 31, 32))
    draw.rectangle((0, IMAGE_H, 6, CELL_H), fill=status_color)
    label = f"S{slot['slot']} {ROLE_LABELS.get(slot['role'], slot['role'])}"
    draw.text((12, IMAGE_H + 8), label, fill=(240, 239, 232), font=fonts["body_bold"])
    draw.text((12, IMAGE_H + 30), shorten(Path(source).name if source else status, 31), fill=(174, 184, 181), font=fonts["small"])
    draw.text((12, IMAGE_H + 45), shorten(slot.get("currentKind") or status, 31), fill=status_color, font=fonts["small"])
    return cell


def make_sheet(taxa, sheet_index):
    width = LABEL_W + MAX_SLOTS * (CELL_W + GAP) + GAP
    height = HEADER_H + len(taxa) * (CELL_H + GAP) + GAP
    sheet = Image.new("RGB", (width, height), (20, 24, 25))
    draw = ImageDraw.Draw(sheet)
    fonts = {
        "title": load_font(23),
        "body_bold": load_font(15),
        "body": load_font(14),
        "small": load_font(11),
    }
    draw.rectangle((0, 0, width, HEADER_H), fill=(24, 66, 56))
    draw.text((22, 16), f"Dino Atlas final gallery slot audit {sheet_index:02d}", fill=(244, 242, 232), font=fonts["title"])
    draw.text((22, 47), "Green: registered candidate  |  amber: unregistered review  |  red: generation required", fill=(195, 218, 207), font=fonts["small"])

    for row_index, taxon in enumerate(taxa):
        y = HEADER_H + GAP + row_index * (CELL_H + GAP)
        draw.rectangle((GAP, y, LABEL_W - GAP, y + CELL_H), fill=(31, 36, 37))
        draw.text((22, y + 16), shorten(taxon["taxon"], 34), fill=(235, 232, 220), font=fonts["body_bold"])
        draw.text((22, y + 42), shorten(taxon.get("name"), 35), fill=(160, 176, 172), font=fonts["small"])
        draw.text((22, y + 64), f"{taxon['period']} / {taxon['region']}", fill=(137, 157, 152), font=fonts["small"])
        draw.text((22, y + 88), f"slots {taxon['imageSlots']} / candidates {taxon['visibleCandidateCount']}", fill=(191, 189, 173), font=fonts["small"])
        for swatch_index, color in enumerate(taxon["paletteLock"]["swatches"]):
            x0 = 22 + swatch_index * 50
            draw.rectangle((x0, y + 119, x0 + 40, y + 145), fill=color)
        missing = [slot["slot"] for slot in taxon["slots"] if slot["status"] == "generate"]
        draw.text((22, y + 164), f"generate: {','.join(map(str, missing)) or 'none'}", fill=(221, 122, 105) if missing else (100, 195, 145), font=fonts["small"])

        for slot_index in range(MAX_SLOTS):
            x = LABEL_W + slot_index * (CELL_W + GAP)
            if slot_index < len(taxon["slots"]):
                cell = make_slot_cell(taxon["slots"][slot_index], fonts)
                sheet.paste(cell, (x, y))
            else:
                draw.rectangle((x, y, x + CELL_W, y + CELL_H), fill=(24, 27, 28))

    output = OUT_DIR / f"gallery-slot-audit-{sheet_index:02d}.png"
    sheet.save(output, optimize=True)
    return output


def main():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for start in range(0, len(plan["taxa"]), TAXA_PER_SHEET):
        chunk = plan["taxa"][start : start + TAXA_PER_SHEET]
        output = make_sheet(chunk, len(outputs) + 1)
        outputs.append(str(output.relative_to(ROOT)).replace("\\", "/"))
    MANIFEST.write_text(json.dumps({"sheets": outputs}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sheets": len(outputs), "output": str(OUT_DIR)}, indent=2))


if __name__ == "__main__":
    main()
