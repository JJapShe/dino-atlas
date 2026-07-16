from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "coelophysis-bauri-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "coelophysis-bodylock-crops-v4.png"
SHEET_OUT = ASSET_ROOT / "coelophysis-review-options-v8.png"

CURRENT = ASSET_ROOT / "coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png"
CURRENT_CROPS = ASSET_ROOT / "coelophysis-slenderneck-smallhands-crops-v3.png"
OPEN_FEET = ASSET_ROOT / "coelophysis-bauri-slenderneck-openfeet-imagegen-v3.png"
COMPACT_HAND = ASSET_ROOT / "coelophysis-bauri-compacthands-imagegen-v2.png"
OPEN_LIMB = ASSET_ROOT / "coelophysis-bauri-openlimbs-imagegen-v2.png"
FORELIMB_GUIDE = ASSET_ROOT / "coelophysis-bauri-forelimb-reference-guide-v1.png"


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
    outline = (45, 35, 26)
    toe_fill = (124, 93, 61)
    for idx in range(3):
        dx = (idx - 1) * 15 * scale
        pts = [
            (x + flip * (dx - 7 * scale), y),
            (x + flip * (dx + 13 * scale), y + 2 * scale),
            (x + flip * (dx + 33 * scale), y + 11 * scale),
            (x + flip * (dx + 2 * scale), y + 17 * scale),
        ]
        draw.polygon(pts, fill=toe_fill, outline=outline)


def draw_small_three_finger_hand(draw, wrist, scale=1.0):
    wx, wy = wrist
    outline = (43, 32, 24)
    arm = (112, 82, 54)
    claw = (229, 210, 154)
    upper = [
        (wx - 46 * scale, wy - 12 * scale),
        (wx - 8 * scale, wy - 5 * scale),
        (wx - 14 * scale, wy + 13 * scale),
        (wx - 52 * scale, wy + 5 * scale),
    ]
    fore = [
        (wx - 18 * scale, wy + 8 * scale),
        (wx + 18 * scale, wy + 17 * scale),
        (wx + 9 * scale, wy + 34 * scale),
        (wx - 24 * scale, wy + 24 * scale),
    ]
    draw.polygon(upper, fill=arm, outline=outline)
    draw.polygon(fore, fill=(94, 69, 47), outline=outline)
    for idx, offset in enumerate([-8, 1, 10]):
        base_x = wx + offset * scale
        base_y = wy + (30 + idx) * scale
        finger = [
            (base_x - 3 * scale, base_y),
            (base_x + 6 * scale, base_y),
            (base_x + (8 + idx * 3) * scale, base_y + 15 * scale),
            (base_x - 3 * scale, base_y + 12 * scale),
        ]
        draw.polygon(finger, fill=arm, outline=outline)
        draw.polygon(
            [
                (finger[2][0], finger[2][1]),
                (finger[2][0] + 6 * scale, finger[2][1] + 5 * scale),
                (finger[2][0] - 2 * scale, finger[2][1] + 8 * scale),
            ],
            fill=claw,
            outline=outline,
        )


def draw_guide():
    img = Image.new("RGB", (1152, 768), (204, 226, 226))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 600, 1152, 768), fill=(207, 184, 131))
    for x in range(0, 1152, 42):
        y = 630 + (x * 7) % 68
        draw.line((x, y, x + 16, y - 15), fill=(133, 111, 73), width=2)

    outline = (42, 32, 24)
    body = (118, 88, 58)
    dark = (82, 61, 42)
    light = (151, 116, 78)
    control = (205, 70, 48)

    tail = [(640, 382), (1036, 348), (1128, 362), (1034, 394), (636, 438)]
    body_poly = [
        (276, 418),
        (380, 352),
        (546, 344),
        (672, 386),
        (704, 458),
        (620, 526),
        (420, 530),
        (298, 488),
    ]
    belly = [(306, 474), (430, 506), (604, 506), (680, 462), (620, 540), (416, 556), (294, 510)]
    neck = [(300, 414), (228, 330), (250, 278), (346, 350), (382, 418)]
    skull = [
        (74, 312),
        (146, 270),
        (252, 272),
        (328, 314),
        (302, 354),
        (184, 360),
        (88, 342),
    ]
    jaw = [(78, 327), (190, 330), (302, 326), (270, 350), (150, 352), (84, 340)]

    for pts, fill in [(tail, dark), (body_poly, body), (belly, (96, 71, 48)), (neck, dark), (skull, light), (jaw, (99, 72, 48))]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((148, 296, 161, 308), fill=(18, 14, 10))
    draw.arc((86, 324, 288, 356), 185, 348, fill=(28, 22, 17), width=2)

    # Forelimbs stay short, folded, and well above the ground so they do not read as extra legs.
    draw_small_three_finger_hand(draw, (406, 450), scale=0.92)
    draw_small_three_finger_hand(draw, (442, 456), scale=0.72)

    legs = [
        (500, 500, 528, 690, dark, -1, 0.82),
        (612, 492, 662, 690, body, 1, 0.88),
    ]
    for x0, y0, x1, y1, fill, flip, scale in legs:
        thigh = [(x0, y0), (x1 + 26, y0 + 8), (x1, y1 - 82), (x0 - 34, y1 - 92)]
        shin = [(x1 - 8, y1 - 88), (x1 + 24, y1 - 80), (x1 + 16, y1), (x1 - 18, y1 - 4)]
        draw.polygon(thigh, fill=fill, outline=outline)
        draw.polygon(shin, fill=(98, 72, 49), outline=outline)
        draw_toes(draw, x1 - 16 if flip < 0 else x1 - 6, y1 - 4, flip=flip, scale=scale)

    draw.line((86, 314, 326, 330), fill=control, width=5)
    draw.arc((234, 274, 718, 538), 184, 354, fill=control, width=4)
    draw.arc((640, 348, 1130, 396), 180, 352, fill=control, width=4)
    draw.ellipse((360, 414, 482, 494), outline=control, width=5)
    draw.text((368, 398), "small folded hands, not legs", fill=(108, 50, 37), font=font)
    draw.text((74, 250), "narrow head + long S-neck", fill=(108, 50, 37), font=font)
    draw.text((28, 32), "structure guide: Coelophysis slim body, S-neck, small folded three-finger hands, two hind legs, long tail", fill=(38, 35, 31), font=font)

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
    crop = image.crop(box)
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    tile.paste(crop, ((size[0] - crop.width) // 2, (size[1] - crop.height) // 2))
    draw = ImageDraw.Draw(tile)
    draw.text((10, size[1] + 12), label[:58], fill=(42, 38, 34), font=ImageFont.load_default())
    return tile


def make_crops(guide):
    current = Image.open(CURRENT).convert("RGB")
    tiles = [
        crop_tile(guide, (60, 242, 352, 370), "guide skull: narrow head and long S-neck"),
        crop_tile(current, (70, 170, 540, 430), "current v3 head and S-neck crop"),
        crop_tile(guide, (346, 390, 500, 505), "guide hands: short folded three-finger forelimbs"),
        crop_tile(current, (450, 405, 700, 595), "current v3 small tucked hand crop"),
        crop_tile(guide, (260, 330, 732, 545), "guide body: gracile torso plus long tail base"),
        crop_tile(current, (350, 300, 1660, 555), "current v3 torso and full-tail crop"),
        crop_tile(guide, (470, 475, 705, 720), "guide legs: two long hind legs, dry three-toed feet"),
        crop_tile(current, (570, 430, 1080, 850), "current v3 hind legs and feet crop"),
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
        sheet_card(CURRENT, "current v3 candidate", "keep first; best gracile body, S-neck, tail, dry feet"),
        sheet_card(CURRENT_CROPS, "current v3 crop gate", "head, small hands, legs, feet, and tail review"),
        sheet_card(GUIDE_OUT, "new Coelophysis body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v3 crop gate", "compare S-neck, folded hands, two legs, feet, tail"),
        sheet_card(OPEN_FEET, "v3 open-feet comparison", "good dry-ground body; weaker hand and rear-foot crop"),
        sheet_card(COMPACT_HAND, "previous compact-hand v2", "kept for small-hand and foot comparison"),
        sheet_card(OPEN_LIMB, "previous open-limb v2", "good full body; hand claws too long"),
        sheet_card(FORELIMB_GUIDE, "older forelimb guide", "useful hand reference, but can overstate arm/leg risk"),
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
    draw.text((22, 20), "Coelophysis body-lock review v8", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the guide to keep the small theropod silhouette while preventing forelimbs from reading as extra legs.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, OPEN_FEET, COMPACT_HAND, OPEN_LIMB, FORELIMB_GUIDE):
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
