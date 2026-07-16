import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "tools" / "comfyui" / "outputs" / "app-gallery-samples.json"
OUT = ROOT / "assets" / "dinosaurs" / "candidate-review-dashboard-v1.png"


TAXON_LABELS = {
    "herrerasaurus-ischigualastensis": "Herrerasaurus",
    "coelophysis-bauri": "Coelophysis",
    "plateosaurus-engelhardti": "Plateosaurus",
    "allosaurus-fragilis": "Allosaurus",
    "apatosaurus-ajax": "Apatosaurus",
    "tyrannosaurus-rex": "Tyrannosaurus rex",
    "triceratops-horridus": "Triceratops",
    "stegosaurus-stenops": "Stegosaurus",
    "velociraptor-mongoliensis": "Velociraptor",
    "brachiosaurus-altithorax": "Brachiosaurus",
    "ankylosaurus-magniventris": "Ankylosaurus",
}


REVIEW_FOCUS = {
    "herrerasaurus-ischigualastensis": "compact hands, exact fingers/toes",
    "coelophysis-bauri": "slender neck, small hands, exact toes",
    "plateosaurus-engelhardti": "no extra limbs, small forelimb hand/thumb claw",
    "allosaurus-fragilis": "smooth brow, three-finger hands, toes",
    "apatosaurus-ajax": "small head, low neck, four open feet",
    "tyrannosaurus-rex": "tiny arms, exactly two fingers, skull texture",
    "triceratops-horridus": "three horns, attached frill, beak, toes",
    "stegosaurus-stenops": "alternating plates, bony surface, four tail spikes",
    "velociraptor-mongoliensis": "toothed snout, feathered body, sickle claw, toes",
    "brachiosaurus-altithorax": "high shoulders, rising neck, shorter tail, feet",
    "ankylosaurus-magniventris": "broad skull, armor rows, four feet, single club",
}


KIND_COLORS = {
    "count-level pass": (41, 111, 78),
    "primary generated": (133, 89, 48),
    "primary structure reference": (58, 94, 145),
    "anatomy review": (151, 87, 50),
    "structure reference": (89, 102, 130),
    "diagnostic only": (147, 67, 64),
}


DISPLAY_RANK = {
    "count-level pass": 0,
    "primary generated": 1,
    "anatomy review": 2,
    "primary structure reference": 3,
    "structure reference": 4,
    "diagnostic only": 5,
}


def fit_image(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (236, 233, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, font, fill, max_chars, line_h, max_lines):
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


def select_primary(items):
    return sorted(items, key=lambda item: DISPLAY_RANK.get(item.get("kind"), 9))[0]


def select_crop_gate(items):
    crop_items = [
        item
        for item in items
        if item.get("kind") == "anatomy review"
        and "crop" in " ".join(
            [
                item.get("title", ""),
                item.get("body", ""),
                item.get("variant", ""),
                item.get("source", ""),
            ]
        ).lower()
    ]
    if crop_items:
        return crop_items[0]
    review_items = [item for item in items if item.get("kind") == "anatomy review"]
    return review_items[0] if review_items else None


def paste_item_image(sheet, item, xy, size):
    x, y = xy
    path = ROOT / item.get("src", "")
    if path.exists():
        sheet.paste(fit_image(Image.open(path), size), (x, y))
        return
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((x, y, x + size[0], y + size[1]), fill=(222, 218, 208))
    draw.text((x + 18, y + 18), "missing image", fill=(104, 82, 70))


def draw_row(sheet, y, taxon_id, primary, crop_gate, font):
    draw = ImageDraw.Draw(sheet)
    row_x = 24
    row_w = sheet.width - 48
    row_h = 560
    primary_box = (340, 224)
    crop_box = (500, 486)
    info_x = row_x + primary_box[0] + crop_box[0] + 48

    draw.rounded_rectangle((row_x, y, row_x + row_w, y + row_h), radius=6, fill=(246, 244, 237))
    paste_item_image(sheet, primary, (row_x + 18, y + 18), primary_box)
    if crop_gate:
        paste_item_image(sheet, crop_gate, (row_x + primary_box[0] + 32, y + 18), crop_box)
    else:
        draw.rectangle(
            (row_x + primary_box[0] + 32, y + 18, row_x + primary_box[0] + 32 + crop_box[0], y + 18 + crop_box[1]),
            fill=(232, 229, 220),
        )
        draw.text((row_x + primary_box[0] + 52, y + 38), "no crop gate yet", fill=(104, 82, 70), font=font)

    kind = primary.get("kind", "")
    kind_color = KIND_COLORS.get(kind, (86, 86, 80))
    draw.rectangle((row_x + 18, y + 250, row_x + 24, y + row_h - 16), fill=kind_color)
    draw.text((row_x + 34, y + 248), "current candidate", fill=(95, 88, 78), font=font)
    draw_wrapped(draw, (row_x + 34, y + 266), primary.get("title", ""), font, (43, 39, 34), 54, 15, 1)
    crop_label_y = y + 18 + crop_box[1] + 8
    draw.text((row_x + primary_box[0] + 32, crop_label_y), "close review gate", fill=(95, 88, 78), font=font)
    draw_wrapped(
        draw,
        (row_x + primary_box[0] + 32, crop_label_y + 18),
        crop_gate.get("title", "") if crop_gate else "No crop/review sheet connected",
        font,
        (43, 39, 34),
        76,
        15,
        1,
    )

    draw.text((info_x, y + 22), TAXON_LABELS.get(taxon_id, taxon_id), fill=(31, 35, 31), font=font)
    draw.rectangle((info_x, y + 48, info_x + 122, y + 68), fill=kind_color)
    draw.text((info_x + 8, y + 53), kind, fill=(250, 248, 239), font=font)
    draw.text((info_x, y + 88), "Review focus", fill=(95, 88, 78), font=font)
    draw_wrapped(draw, (info_x, y + 108), REVIEW_FOCUS.get(taxon_id, ""), font, (45, 44, 39), 45, 17, 3)
    draw.text((info_x, y + 174), "Decision rule", fill=(95, 88, 78), font=font)
    draw_wrapped(
        draw,
        (info_x, y + 194),
        "Promote only after the crop gate still matches the species silhouette and countable traits.",
        font,
        (45, 44, 39),
        45,
        17,
        3,
    )


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    samples = data["samples"]
    rows = []
    for taxon_id in TAXON_LABELS:
        items = samples.get(taxon_id, [])
        if not items:
            continue
        rows.append((taxon_id, select_primary(items), select_crop_gate(items)))

    font = ImageFont.load_default()
    sheet_w = 1260
    header_h = 118
    row_h = 560
    gap = 16
    sheet_h = header_h + len(rows) * (row_h + gap) + 24
    sheet = Image.new("RGB", (sheet_w, sheet_h), (224, 220, 211))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet_w, header_h), fill=(28, 62, 48))
    draw.text((24, 22), "Dinosaur Atlas - candidate review dashboard", fill=(248, 246, 238), font=font)
    draw.text(
        (24, 50),
        "Left: current app-leading candidate. Middle: closest crop/review gate. Right: human QA focus.",
        fill=(219, 228, 216),
        font=font,
    )
    draw.text(
        (24, 76),
        "Generated from app-gallery-samples.json; these are MVP review candidates, not final scientific approvals.",
        fill=(190, 207, 190),
        font=font,
    )

    for idx, (taxon_id, primary, crop_gate) in enumerate(rows):
        draw_row(sheet, header_h + gap + idx * (row_h + gap), taxon_id, primary, crop_gate, font)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
