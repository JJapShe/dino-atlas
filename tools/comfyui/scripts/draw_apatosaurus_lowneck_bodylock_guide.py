from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "apatosaurus-ajax-lowneck-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "apatosaurus-lowneck-bodylock-crops-v3.png"
SHEET_OUT = ASSET_ROOT / "apatosaurus-review-options-v6.png"

CURRENT = ASSET_ROOT / "apatosaurus-ajax-smallhead-imagegen-v2.png"
CURRENT_CROPS = ASSET_ROOT / "apatosaurus-smallhead-crops-v2.png"
OPEN_FEET = ASSET_ROOT / "apatosaurus-ajax-openfeet-imagegen-v2.png"
PREVIOUS = ASSET_ROOT / "apatosaurus-ajax-lowneck-imagegen-v1.png"
EDGE_VOLUME = ASSET_ROOT / "apatosaurus-ajax-edge-volume-v1.png"
HIGH_NECK_REJECT = ASSET_ROOT / "apatosaurus-ajax-lowneck-ipcontrol-v1.png"


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


def draw_foot(draw, x, y, scale, flip=1):
    outline = (54, 43, 32)
    fill = (111, 88, 63)
    pts = [
        (x - flip * 22 * scale, y),
        (x + flip * 56 * scale, y - 2 * scale),
        (x + flip * 92 * scale, y + 14 * scale),
        (x + flip * 18 * scale, y + 26 * scale),
        (x - flip * 30 * scale, y + 18 * scale),
    ]
    draw.polygon(pts, fill=fill, outline=outline)
    for idx in range(3):
        tx = x + flip * (24 + idx * 20) * scale
        draw.ellipse(
            (tx - 5 * scale, y + 10 * scale, tx + 13 * scale, y + 22 * scale),
            fill=(169, 140, 96),
            outline=outline,
        )


def draw_guide():
    img = Image.new("RGB", (1152, 768), (204, 225, 225))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 586, 1152, 768), fill=(205, 184, 132))
    for x in range(0, 1152, 44):
        y = 630 + (x * 7) % 66
        draw.line((x, y, x + 16, y - 18), fill=(130, 112, 75), width=2)
    for x in range(28, 1120, 105):
        y = 660 + (x * 5) % 48
        draw.ellipse((x, y, x + 24, y + 8), fill=(145, 123, 82), outline=(100, 84, 56))

    outline = (43, 34, 26)
    body = (117, 96, 69)
    dark = (88, 71, 51)
    light = (149, 125, 88)
    control = (205, 70, 48)

    tail = [(712, 418), (1008, 390), (1112, 410), (1030, 448), (720, 486)]
    body_poly = [
        (250, 410),
        (338, 344),
        (510, 320),
        (682, 344),
        (786, 408),
        (772, 510),
        (620, 574),
        (404, 568),
        (270, 508),
    ]
    belly = [(286, 498), (418, 540), (620, 542), (746, 500), (706, 580), (426, 612), (262, 550)]
    hip = [(598, 350), (736, 388), (780, 470), (704, 536), (594, 508), (552, 416)]
    shoulder = [(260, 402), (330, 352), (470, 328), (512, 396), (444, 492), (300, 506)]
    neck = [(266, 410), (166, 396), (76, 370), (34, 344), (46, 318), (122, 326), (238, 360), (318, 394)]
    head = [(16, 324), (58, 300), (126, 306), (150, 334), (116, 360), (46, 356)]

    for pts, fill in [
        (tail, dark),
        (body_poly, body),
        (belly, (98, 79, 57)),
        (hip, (104, 84, 60)),
        (shoulder, light),
        (neck, light),
        (head, (130, 106, 75)),
    ]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((67, 322, 81, 335), fill=(18, 15, 12))
    draw.arc((16, 326, 106, 366), 190, 350, fill=(33, 26, 19), width=2)

    legs = [
        (330, 500, 378, 668, light, -1, 0.92),
        (450, 506, 496, 682, body, -1, 0.9),
        (606, 502, 654, 676, dark, 1, 0.9),
        (724, 488, 768, 660, body, 1, 0.88),
    ]
    for x0, y0, x1, y1, fill, flip, foot_scale in legs:
        leg = [(x0, y0), (x1, y0 + 5), (x1 - 8, y1), (x0 - 24, y1 - 8)]
        draw.polygon(leg, fill=fill, outline=outline)
        draw_foot(draw, x0 - 8 if flip < 0 else x0 + 4, y1 - 2, foot_scale, flip=flip)

    # Control strokes stay visible for ControlNet and manual QA.
    draw.line((260, 388, 778, 404), fill=control, width=5)
    draw.line((330, 674, 770, 662), fill=control, width=4)
    draw.arc((24, 300, 324, 426), 180, 348, fill=control, width=4)
    draw.arc((708, 374, 1116, 460), 176, 356, fill=control, width=4)
    draw.line((326, 510, 378, 668), fill=(230, 197, 108), width=4)
    draw.line((726, 494, 768, 660), fill=(230, 197, 108), width=4)

    draw.text(
        (28, 32),
        "structure guide: low forward neck, similar pillar-limb height, long horizontal tail, four open feet",
        fill=(38, 35, 31),
        font=font,
    )
    draw.text((62, 286), "neck stays low and forward", fill=(108, 50, 37), font=font)
    draw.text((742, 358), "long tail, not cropped", fill=(108, 50, 37), font=font)
    draw.text((334, 308), "no high Brachiosaurus shoulder peak", fill=(108, 50, 37), font=font)

    GUIDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(GUIDE_OUT)
    return img


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
        crop_tile(guide, (10, 288, 340, 432), "guide neck/head: low forward, small blunt head"),
        crop_tile(current, (45, 250, 610, 455), "current v2 neck/head crop"),
        crop_tile(guide, (240, 300, 812, 570), "guide body: low shoulders, deep torso, no Brachiosaurus peak"),
        crop_tile(current, (400, 250, 1160, 610), "current v2 torso/shoulder crop"),
        crop_tile(guide, (300, 480, 820, 720), "guide legs: four open pillar feet, similar height"),
        crop_tile(current, (420, 430, 1140, 775), "current v2 four-foot crop"),
        crop_tile(guide, (700, 360, 1130, 490), "guide tail: long horizontal and fully framed"),
        crop_tile(current, (940, 305, 1774, 540), "current v2 full-tail crop"),
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
        sheet_card(CURRENT, "current v2 candidate", "keep first; best small-head low-neck compromise"),
        sheet_card(CURRENT_CROPS, "current v2 crop gate", "head, neck, feet, and tail review"),
        sheet_card(GUIDE_OUT, "new low-neck body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v2 crop gate", "compare low neck, shoulders, feet, and tail"),
        sheet_card(OPEN_FEET, "v2 open-feet comparison", "stronger foot hints, weaker head and neck read"),
        sheet_card(PREVIOUS, "previous v1 low-neck candidate", "good low-neck gate, weaker foot/head detail"),
        sheet_card(EDGE_VOLUME, "edge-volume comparison", "low-neck silhouette, but feet hidden by foreground rise"),
        sheet_card(HIGH_NECK_REJECT, "high-neck drift rejection", "natural texture but too high-necked and leg-hidden"),
    ]
    cols = 4
    gap = 14
    header_h = 86
    card_w, card_h = 360, 318
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * card_w + (cols + 1) * gap, header_h + rows * (card_h + gap) + gap), (226, 222, 212))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, sheet.width, header_h), fill=(28, 62, 48))
    draw.text((22, 20), "Apatosaurus low-neck body-lock review v6", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the new guide to prevent Brachiosaurus/generic sauropod drift; it is not a promoted candidate.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, OPEN_FEET, PREVIOUS, EDGE_VOLUME, HIGH_NECK_REJECT):
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
