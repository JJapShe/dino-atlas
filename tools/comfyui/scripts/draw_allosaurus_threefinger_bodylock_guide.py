from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "allosaurus-fragilis-threefinger-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "allosaurus-threefinger-bodylock-crops-v10.png"
SHEET_OUT = ASSET_ROOT / "allosaurus-review-options-v10.png"

CURRENT = ASSET_ROOT / "allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png"
CURRENT_CROPS = ASSET_ROOT / "allosaurus-smoothbrow-threefinger-crops-v4.png"
LOW_HORN = ASSET_ROOT / "allosaurus-fragilis-lowhorn-threefinger-comparison-v4.png"
RIDGE_HAND = ASSET_ROOT / "allosaurus-fragilis-ridgehand-comparison-v4.png"
PREVIOUS_V3 = ASSET_ROOT / "allosaurus-fragilis-lowbrow-threefinger-imagegen-v3.png"
REVIEWABLE_HAND = ASSET_ROOT / "allosaurus-fragilis-reviewable-threefinger-imagegen-v3.png"
COMPACT_HAND = ASSET_ROOT / "allosaurus-fragilis-compacthands-imagegen-v2.png"


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


def draw_toes(draw, x, y, flip=1, scale=1.0):
    outline = (45, 35, 27)
    for idx in range(3):
        dx = (idx - 1) * 21 * scale
        pts = [
            (x + flip * (dx - 10 * scale), y),
            (x + flip * (dx + 18 * scale), y + 2 * scale),
            (x + flip * (dx + 42 * scale), y + 15 * scale),
            (x + flip * (dx + 4 * scale), y + 23 * scale),
        ]
        draw.polygon(pts, fill=(113, 89, 63), outline=outline)


def draw_three_finger_hand(draw, wrist, scale=1.0):
    wx, wy = wrist
    outline = (43, 33, 25)
    arm = (105, 82, 57)
    claw = (232, 210, 151)
    upper = [(wx - 88 * scale, wy - 22 * scale), (wx - 18 * scale, wy - 8 * scale), (wx - 26 * scale, wy + 20 * scale), (wx - 94 * scale, wy + 8 * scale)]
    fore = [(wx - 32 * scale, wy + 10 * scale), (wx + 20 * scale, wy + 24 * scale), (wx + 8 * scale, wy + 52 * scale), (wx - 44 * scale, wy + 32 * scale)]
    draw.polygon(upper, fill=arm, outline=outline)
    draw.polygon(fore, fill=(92, 70, 49), outline=outline)
    for idx, offset in enumerate([-12, 2, 16]):
        base_x = wx + offset * scale
        base_y = wy + (46 + (idx % 2) * 3) * scale
        finger = [
            (base_x - 4 * scale, base_y),
            (base_x + 8 * scale, base_y + 1 * scale),
            (base_x + (8 + idx * 6) * scale, base_y + 24 * scale),
            (base_x - 4 * scale, base_y + 20 * scale),
        ]
        draw.polygon(finger, fill=arm, outline=outline)
        draw.polygon(
            [
                (finger[2][0], finger[2][1]),
                (finger[2][0] + 9 * scale, finger[2][1] + 7 * scale),
                (finger[2][0] - 3 * scale, finger[2][1] + 11 * scale),
            ],
            fill=claw,
            outline=outline,
        )


def draw_guide():
    img = Image.new("RGB", (1152, 768), (204, 225, 225))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 590, 1152, 768), fill=(204, 184, 132))
    for x in range(0, 1152, 46):
        y = 630 + (x * 9) % 66
        draw.line((x, y, x + 16, y - 18), fill=(132, 112, 74), width=2)

    outline = (42, 33, 25)
    body = (112, 90, 64)
    dark = (79, 62, 44)
    light = (141, 116, 82)
    control = (205, 70, 48)

    tail = [(684, 390), (1038, 352), (1124, 374), (1042, 420), (680, 462)]
    body_poly = [
        (222, 416),
        (330, 338),
        (510, 310),
        (680, 340),
        (790, 404),
        (776, 505),
        (638, 570),
        (414, 568),
        (266, 510),
    ]
    belly = [(266, 496), (426, 538), (638, 536), (750, 496), (704, 580), (420, 616), (254, 548)]
    neck = [(226, 410), (184, 362), (210, 322), (304, 342), (336, 398)]
    skull = [
        (36, 376),
        (96, 326),
        (204, 308),
        (316, 334),
        (344, 382),
        (300, 432),
        (168, 438),
        (64, 416),
    ]
    jaw = [(42, 392), (170, 396), (306, 388), (266, 424), (136, 430), (48, 412)]

    for pts, fill in [(tail, dark), (body_poly, body), (belly, (93, 73, 52)), (neck, dark), (skull, light), (jaw, (97, 75, 52))]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((132, 350, 148, 365), fill=(18, 14, 10))
    draw.arc((54, 390, 288, 432), 188, 350, fill=(28, 22, 17), width=3)
    draw.arc((94, 312, 276, 374), 202, 336, fill=(225, 194, 126), width=2)

    # Allosaurus forelimbs are longer than T. rex arms but still non-weight-bearing.
    draw_three_finger_hand(draw, (382, 448), scale=1.0)
    draw_three_finger_hand(draw, (432, 456), scale=0.82)

    legs = [
        (500, 506, 558, 688, dark, -1, 0.95),
        (668, 496, 724, 690, body, 1, 0.95),
    ]
    for x0, y0, x1, y1, fill, flip, scale in legs:
        thigh = [(x0, y0), (x1 + 12, y0 + 8), (x1, y1 - 82), (x0 - 42, y1 - 88)]
        shin = [(x1 - 8, y1 - 88), (x1 + 28, y1 - 78), (x1 + 20, y1), (x1 - 22, y1 - 4)]
        draw.polygon(thigh, fill=fill, outline=outline)
        draw.polygon(shin, fill=(97, 75, 52), outline=outline)
        draw_toes(draw, x1 - 18 if flip < 0 else x1 - 8, y1 - 4, flip=flip, scale=scale)

    # Visible control marks for QA and ControlNet.
    draw.line((88, 366, 320, 376), fill=control, width=5)
    draw.arc((210, 304, 792, 558), 190, 354, fill=control, width=4)
    draw.arc((680, 350, 1124, 420), 180, 350, fill=control, width=4)
    draw.ellipse((310, 392, 478, 532), outline=control, width=5)
    draw.text((326, 378), "medium arms: 3 fingers", fill=(108, 50, 37), font=font)
    draw.text((56, 290), "lower allosaur skull, not T. rex", fill=(108, 50, 37), font=font)
    draw.text((28, 32), "structure guide: Allosaurus low skull, medium forelimbs, exactly three fingers, long tail", fill=(38, 35, 31), font=font)

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
        crop_tile(guide, (25, 292, 360, 445), "guide skull: lower allosaur head, no hornlike brow"),
        crop_tile(current, (0, 205, 500, 470), "current v4 skull crop"),
        crop_tile(guide, (300, 380, 500, 545), "guide arms: medium length, exactly three fingers"),
        crop_tile(current, (265, 335, 620, 585), "current v4 forelimb/hand crop"),
        crop_tile(guide, (208, 300, 812, 585), "guide body: lower theropod profile + long tail"),
        crop_tile(current, (240, 250, 1250, 660), "current v4 torso/tail crop"),
        crop_tile(guide, (460, 485, 790, 724), "guide legs: two hind legs, dry three-toed feet"),
        crop_tile(current, (435, 560, 960, 910), "current v4 hind legs/feet crop"),
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
        sheet_card(CURRENT, "current v4 candidate", "keep first; smoother brow plus three-finger gate"),
        sheet_card(CURRENT_CROPS, "current v4 crop gate", "skull, medium arms, feet, tail review"),
        sheet_card(GUIDE_OUT, "new three-finger body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v4 crop gate", "compare skull, three fingers, body, legs, tail"),
        sheet_card(LOW_HORN, "v4 low-horn comparison", "useful body and hands, but brow still horn-like"),
        sheet_card(RIDGE_HAND, "v4 ridge-hand comparison", "clear hand/tail but dorsal brow texture is stronger"),
        sheet_card(PREVIOUS_V3, "previous v3 body gate", "stronger hand readability, higher brow ridge"),
        sheet_card(REVIEWABLE_HAND, "v3 readable-hand comparison", "excellent hand gate, kept for finger-count review"),
        sheet_card(COMPACT_HAND, "previous compact-hand v2", "stable body gate, less readable hands than v3/v4"),
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
    draw.text((22, 20), "Allosaurus three-finger body-lock review v10", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the new guide to prevent T. rex or horned-monster drift; it is not a promoted candidate.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, LOW_HORN, RIDGE_HAND, PREVIOUS_V3, REVIEWABLE_HAND, COMPACT_HAND):
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
