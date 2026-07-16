from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"

SOURCE = ASSETS / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CLEAN_GUIDE = ASSETS / "stegosaurus-stenops-plate-topology-guide-clean-v52.png"
REJECTION_CROPS = ASSETS / "stegosaurus-plate-topology-control-v52-v53-rejection-crops.png"

CONTROL_OUT = ASSETS / "stegosaurus-stenops-plate-silhouette-control-v65.png"
MASK_OUT = ASSETS / "stegosaurus-plate-silhouette-control-mask-v65.png"
REVIEW_OUT = ASSETS / "stegosaurus-plate-silhouette-control-v65-review-sheet.png"

FONT = ImageFont.load_default()


def plate_polygon(cx, base_y, width, height, lean=0, shoulder=0.62, top_width=0.18):
    half = width / 2
    top_half = width * top_width / 2
    top_x = cx + lean
    return [
        (int(cx - half), int(base_y)),
        (int(cx - half * shoulder), int(base_y - height * 0.58)),
        (int(top_x - top_half), int(base_y - height)),
        (int(top_x + top_half), int(base_y - height)),
        (int(cx + half * shoulder), int(base_y - height * 0.58)),
        (int(cx + half), int(base_y)),
    ]


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (245, 243, 236))
    tile.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return tile


def draw_wrapped(draw, xy, text, max_chars=56, max_lines=2):
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
        draw.text((x, y + idx * 15), line, fill=(43, 39, 34), font=FONT)


def make_control():
    source = Image.open(SOURCE).convert("RGB")
    base = ImageEnhance.Color(source).enhance(0.82)
    base = ImageEnhance.Contrast(base).enhance(0.94)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(overlay)
    mask_draw = ImageDraw.Draw(mask)

    far_fill = (121, 78, 45, 218)
    near_fill = (91, 61, 39, 232)
    edge = (34, 27, 22, 255)
    rib = (178, 137, 82, 172)
    base_shadow = (28, 21, 17, 130)

    far_plates = [
        (315, 404, 48, 92, -8),
        (475, 365, 62, 130, -5),
        (635, 330, 76, 165, -2),
        (805, 318, 82, 176, 4),
        (975, 350, 70, 142, 6),
        (1130, 410, 54, 105, 3),
    ]
    near_plates = [
        (250, 430, 40, 70, -6),
        (390, 388, 58, 116, 0),
        (555, 345, 72, 150, 4),
        (725, 315, 82, 176, 5),
        (895, 325, 78, 165, -3),
        (1055, 372, 62, 125, -5),
        (1210, 438, 48, 88, -4),
    ]

    for cx, base_y, width, height, lean in far_plates:
        poly = plate_polygon(cx, base_y, width, height, lean, shoulder=0.7, top_width=0.2)
        draw.polygon(poly, fill=far_fill, outline=edge)
        mask_draw.polygon(poly, fill=255)
        draw.line((cx + lean, base_y - height + 22, cx, base_y - 18), fill=rib, width=2)
        draw.line((cx - width // 2, base_y, cx + width // 2, base_y), fill=base_shadow, width=5)

    for cx, base_y, width, height, lean in near_plates:
        poly = plate_polygon(cx, base_y, width, height, lean, shoulder=0.66, top_width=0.22)
        draw.polygon(poly, fill=near_fill, outline=edge)
        mask_draw.polygon(poly, fill=255)
        draw.line((cx + lean, base_y - height + 26, cx, base_y - 16), fill=rib, width=2)
        draw.line((cx - width // 2, base_y, cx + width // 2, base_y), fill=base_shadow, width=6)

    composited = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    CONTROL_OUT.parent.mkdir(parents=True, exist_ok=True)
    composited.save(CONTROL_OUT)
    mask.save(MASK_OUT)


def tile(path, title, note, size=(430, 242)):
    image = Image.open(path).convert("RGB")
    panel = Image.new("RGB", (size[0], size[1] + 74), (245, 243, 236))
    panel.paste(fit(image, size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def make_review_sheet():
    items = [
        tile(SOURCE, "current v6 first candidate", "Natural body and thagomizer gate, but plate topology still needs review."),
        tile(CONTROL_OUT, "v65 silhouette control source", "V6 body with stronger separated alternating plate silhouettes and no text labels."),
        tile(MASK_OUT, "v65 plate silhouette mask", "Documents the edited plate area only; body, feet, tail, and thagomizer are not target edits."),
        tile(CLEAN_GUIDE, "previous clean topology guide v52", "Plain guide failed as ControlNet because plates drifted into comb or sail reads."),
        tile(REJECTION_CROPS, "v52/v53 rejection crops", "Failure reference: do not promote text bleed, comb rows, sails, or weak thagomizer gates."),
    ]
    cols = 3
    sheet = Image.new("RGB", (cols * items[0].width, 2 * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(REVIEW_OUT)


def main():
    for path in (SOURCE, CLEAN_GUIDE, REJECTION_CROPS):
        if not path.exists():
            raise FileNotFoundError(path)
    make_control()
    make_review_sheet()
    print(CONTROL_OUT)
    print(MASK_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
