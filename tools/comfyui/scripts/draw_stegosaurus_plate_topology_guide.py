from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

GUIDE_OUT = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "stegosaurus-plate-topology-crops-v12.png"
SHEET_OUT = ASSET_ROOT / "stegosaurus-review-options-v46.png"

CURRENT = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
CURRENT_CROPS = ASSET_ROOT / "stegosaurus-alternatingplate-fourspike-crops-v6.png"
EXTRA_SPIKE = ASSET_ROOT / "stegosaurus-stenops-extraspike-plate-comparison-v6.png"
PLATE_PRIORITY = ASSET_ROOT / "stegosaurus-stenops-plate-priority-structure-v1.png"
LOWBODY_REVIEW = ASSET_ROOT / "stegosaurus-stenops-lowbody-plate-thagomizer-ipcontrol-v1.png"
PETAL_REJECT = ASSET_ROOT / "stegosaurus-stenops-plate-lock-ipcontrol-v1.png"


def draw_wrapped(draw, xy, text, font, fill, max_chars=60, line_h=15, max_lines=2):
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


def plate_polygon(cx, base_y, width, height, lean=0, base_drop=18):
    half = width / 2
    return [
        (int(cx - half), int(base_y)),
        (int(cx - half * 0.72 + lean), int(base_y - height * 0.72)),
        (int(cx + lean), int(base_y - height)),
        (int(cx + half * 0.72 + lean), int(base_y - height * 0.72)),
        (int(cx + half), int(base_y)),
        (int(cx + half * 0.56), int(base_y + base_drop)),
        (int(cx - half * 0.56), int(base_y + base_drop)),
    ]


def draw_plate(draw, cx, base_y, width, height, fill, outline, lean=0, guide_fill=None):
    pts = plate_polygon(cx, base_y, width, height, lean)
    draw.polygon(pts, fill=outline)
    inner = plate_polygon(cx, base_y - 2, width - 8, height - 8, lean, base_drop=14)
    draw.polygon(inner, fill=fill)
    draw.line((cx + lean, base_y - height + 10, cx, base_y + 10), fill=(91, 66, 43), width=2)
    draw.arc((cx - width * 0.26, base_y - height * 0.82, cx + width * 0.26, base_y - height * 0.12), 250, 292, fill=(225, 184, 106), width=2)
    if guide_fill:
        draw.ellipse((cx - 8, base_y + 10, cx + 8, base_y + 26), fill=guide_fill, outline=outline)


def draw_toes(draw, x, y, flip=1):
    for idx in range(3):
        dx = (idx - 1) * 17
        pts = [
            (x + flip * (dx - 8), y),
            (x + flip * (dx + 14), y - 1),
            (x + flip * (dx + 28), y + 10),
            (x + flip * (dx + 2), y + 15),
        ]
        draw.polygon(pts, fill=(100, 75, 52), outline=(45, 34, 25))


def draw_thagomizer(draw, base):
    x, y = base
    outline = (42, 33, 25)
    spike = (177, 112, 58)
    hub = (76, 54, 38)
    draw.ellipse((x - 22, y - 18, x + 24, y + 16), fill=hub, outline=outline, width=2)
    spikes = [
        [(x - 6, y - 8), (x + 112, y - 92), (x + 16, y + 2)],
        [(x + 5, y - 3), (x + 146, y - 30), (x + 20, y + 6)],
        [(x + 2, y + 5), (x + 132, y + 72), (x + 12, y + 10)],
        [(x - 8, y + 8), (x - 72, y + 104), (x + 3, y + 12)],
    ]
    for pts in spikes:
        draw.polygon(pts, fill=outline)
        inner = [
            (int((pts[0][0] * 0.72) + (pts[2][0] * 0.28)), int((pts[0][1] * 0.72) + (pts[2][1] * 0.28))),
            pts[1],
            (int((pts[2][0] * 0.72) + (pts[0][0] * 0.28)), int((pts[2][1] * 0.72) + (pts[0][1] * 0.28))),
        ]
        draw.polygon(inner, fill=spike)


def draw_guide():
    image = Image.new("RGB", (1152, 768), (199, 222, 221))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 586, 1152, 768), fill=(204, 184, 135))
    for x in range(0, 1152, 34):
        y = 610 + (x * 19) % 86
        draw.line((x, y, x + 13, y - 22), fill=(132, 117, 82), width=2)

    outline = (37, 29, 22)
    body = (102, 73, 48)
    body_dark = (75, 54, 38)
    near_plate = (176, 111, 58)
    far_plate = (125, 83, 51)
    near_dot = (210, 82, 55)
    far_dot = (55, 105, 168)

    tail = [(774, 434), (1040, 356), (1076, 382), (808, 492)]
    body_poly = [
        (196, 440),
        (290, 374),
        (438, 338),
        (640, 338),
        (778, 384),
        (824, 456),
        (790, 522),
        (638, 574),
        (394, 572),
        (244, 522),
    ]
    neck = [(204, 430), (122, 400), (92, 432), (178, 482)]
    head = [(38, 432), (86, 390), (156, 382), (210, 414), (184, 462), (82, 472)]
    for pts, fill in [(tail, body_dark), (body_poly, body), (neck, body_dark), (head, (96, 69, 46))]:
        draw.polygon(pts, fill=fill, outline=outline)
    draw.ellipse((83, 414, 96, 427), fill=(19, 16, 13))
    draw.arc((44, 432, 142, 470), 194, 340, fill=(23, 19, 15), width=2)

    # Far row first, then near row. Colored sockets make the intended topology explicit.
    far_row = [
        (236, 404, 44, 72, -7),
        (338, 366, 58, 116, -5),
        (470, 336, 68, 150, -4),
        (616, 338, 72, 154, 2),
        (744, 380, 56, 110, 6),
        (834, 436, 38, 70, 6),
    ]
    near_row = [
        (276, 418, 48, 86, 5),
        (392, 376, 64, 130, 4),
        (536, 346, 78, 166, 0),
        (678, 360, 70, 146, -3),
        (786, 418, 50, 92, -4),
        (874, 470, 32, 58, -4),
    ]
    for cx, base_y, width, height, lean in far_row:
        draw_plate(draw, cx, base_y, width, height, far_plate, outline, lean=lean, guide_fill=far_dot)
    for cx, base_y, width, height, lean in near_row:
        draw_plate(draw, cx, base_y, width, height, near_plate, outline, lean=lean, guide_fill=near_dot)

    legs = [
        (292, 520, 344, 672, body_dark, -1),
        (446, 536, 498, 680, body, -1),
        (640, 530, 696, 682, body_dark, 1),
        (758, 506, 812, 666, body, 1),
    ]
    for x0, y0, x1, y1, fill, flip in legs:
        leg = [(x0, y0), (x1, y0 + 4), (x1 - 12, y1), (x0 - 24, y1 - 8)]
        foot = [(x0 - 42, y1 - 8), (x1 + 28, y1 - 8), (x1 + 42, y1 + 14), (x0 - 46, y1 + 16)]
        draw.polygon(leg, fill=fill, outline=outline)
        draw.polygon(foot, fill=(72, 54, 40), outline=outline)
        draw_toes(draw, x0 + 16, y1 + 4, flip=flip)

    draw_thagomizer(draw, (1040, 374))
    draw.arc((210, 330, 820, 540), 190, 352, fill=(204, 72, 49), width=4)
    draw.line((236, 432, 874, 486), fill=(55, 105, 168), width=3)
    draw.line((276, 452, 880, 506), fill=(210, 82, 55), width=3)
    draw.text((28, 32), "structure guide: two staggered plate rows, visible gaps, four-spike thagomizer", fill=(38, 35, 31), font=font)
    draw.text((28, 54), "blue sockets = far row, red sockets = near row; use as ControlNet/QA guide only", fill=(38, 35, 31), font=font)

    GUIDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(GUIDE_OUT)
    return image


def fit_image(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (237, 234, 226))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def fit_crop(image, box, size):
    crop = image.crop(box)
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (237, 234, 226))
    canvas.paste(crop, ((size[0] - crop.width) // 2, (size[1] - crop.height) // 2))
    return canvas


def crop_tile(image, box, label, size=(380, 250)):
    tile = Image.new("RGB", (size[0], size[1] + 42), (246, 244, 237))
    tile.paste(fit_crop(image, box, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((10, size[1] + 12), label[:58], fill=(42, 38, 34), font=ImageFont.load_default())
    return tile


def make_crops(guide):
    current = Image.open(CURRENT).convert("RGB")
    tiles = [
        crop_tile(guide, (200, 270, 900, 520), "guide two staggered rows: blue far, red near"),
        crop_tile(current, (235, 135, 1370, 535), "current v6 dorsal plate row"),
        crop_tile(guide, (220, 300, 900, 610), "guide gaps + varied plate sizes"),
        crop_tile(current, (470, 145, 1010, 435), "current v6 plate-surface crop"),
        crop_tile(guide, (930, 300, 1152, 520), "guide four-spike thagomizer"),
        crop_tile(current, (1360, 430, 1650, 760), "current v6 four-spike tail crop"),
        crop_tile(guide, (250, 500, 840, 720), "guide low body + four planted feet"),
        crop_tile(current, (270, 545, 1000, 810), "current v6 feet/body crop"),
    ]
    sheet = Image.new("RGB", (760, 1168), (226, 222, 212))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % 2) * 380, (idx // 2) * 292))
    sheet.save(CROPS_OUT)


def sheet_card(path, title, note, size=(360, 240)):
    tile = Image.new("RGB", (size[0], size[1] + 78), (246, 244, 237))
    tile.paste(fit_image(path, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()
    draw.text((10, size[1] + 10), title[:52], fill=(95, 57, 45), font=font)
    draw_wrapped(draw, (10, size[1] + 32), note, font, (42, 38, 34), max_chars=58)
    return tile


def make_review_sheet():
    cards = [
        sheet_card(CURRENT, "current v6 candidate", "keep first; best natural plate/thagomizer balance"),
        sheet_card(CURRENT_CROPS, "current v6 crop gate", "plate row, feet, and thagomizer close review"),
        sheet_card(GUIDE_OUT, "new plate topology guide", "ControlNet/QA target: two staggered plate rows"),
        sheet_card(CROPS_OUT, "new guide vs v6 crop gate", "compare row topology, gaps, feet, and tail spikes"),
        sheet_card(EXTRA_SPIKE, "v6 extra-spike comparison", "stronger row cue but tail count risk"),
        sheet_card(PLATE_PRIORITY, "older plate-priority guide", "useful target, weaker row-color topology"),
        sheet_card(LOWBODY_REVIEW, "low-body plate/thagomizer review", "body route, but plates/tail still weak"),
        sheet_card(PETAL_REJECT, "petal-like plate rejection", "do not use as positive plate seed"),
    ]
    cols = 3
    gap = 14
    header_h = 86
    card_w, card_h = 360, 318
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * card_w + (cols + 1) * gap, header_h + rows * (card_h + gap) + gap), (226, 222, 212))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, sheet.width, header_h), fill=(28, 62, 48))
    draw.text((22, 20), "Stegosaurus plate topology review v46", fill=(248, 246, 238), font=font)
    draw.text((22, 46), "Use the guide to lock staggered two-row plates before trusting texture polish.", fill=(216, 226, 214), font=font)
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, EXTRA_SPIKE, PLATE_PRIORITY, LOWBODY_REVIEW, PETAL_REJECT):
        if not path.exists():
            raise FileNotFoundError(path)
    guide = draw_guide()
    make_crops(guide)
    make_review_sheet()
    print(GUIDE_OUT)
    print(CROPS_OUT)
    print(SHEET_OUT)


if __name__ == "__main__":
    main()
