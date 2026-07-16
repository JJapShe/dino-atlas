from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "herrerasaurus-ischigualastensis-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "herrerasaurus-bodylock-crops-v3.png"
SHEET_OUT = ASSET_ROOT / "herrerasaurus-review-options-v8.png"

CURRENT = ASSET_ROOT / "herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png"
CURRENT_CROPS = ASSET_ROOT / "herrerasaurus-compacthands-crops-v2.png"
BALANCED_HAND = ASSET_ROOT / "herrerasaurus-ischigualastensis-balancedhands-imagegen-v2.png"
PREVIOUS_STRICT = ASSET_ROOT / "herrerasaurus-ischigualastensis-strict-imagegen-alt-v1.png"
HAND_RISK = ASSET_ROOT / "herrerasaurus-ischigualastensis-strict-imagegen-v1.png"
CLOSED_JAW = ASSET_ROOT / "herrerasaurus-ischigualastensis-closedjaw-headblend-v1.png"
LONG_ARMS = ASSET_ROOT / "herrerasaurus-ischigualastensis-longarms-ipcontrol-v1.png"


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
    toe_fill = (121, 91, 60)
    for idx in range(3):
        dx = (idx - 1) * 19 * scale
        pts = [
            (x + flip * (dx - 9 * scale), y),
            (x + flip * (dx + 15 * scale), y + 2 * scale),
            (x + flip * (dx + 38 * scale), y + 14 * scale),
            (x + flip * (dx + 3 * scale), y + 21 * scale),
        ]
        draw.polygon(pts, fill=toe_fill, outline=outline)


def draw_herrera_hand(draw, wrist, scale=1.0):
    wx, wy = wrist
    outline = (43, 32, 24)
    arm = (113, 83, 55)
    dark = (92, 68, 46)
    claw = (233, 211, 152)
    upper = [
        (wx - 66 * scale, wy - 18 * scale),
        (wx - 12 * scale, wy - 7 * scale),
        (wx - 20 * scale, wy + 17 * scale),
        (wx - 74 * scale, wy + 7 * scale),
    ]
    fore = [
        (wx - 28 * scale, wy + 8 * scale),
        (wx + 18 * scale, wy + 22 * scale),
        (wx + 5 * scale, wy + 48 * scale),
        (wx - 42 * scale, wy + 30 * scale),
    ]
    draw.polygon(upper, fill=arm, outline=outline)
    draw.polygon(fore, fill=dark, outline=outline)

    # Herrerasaurus hand target: three main clawed digits dominate; outer vestigial digits stay tiny.
    for idx, offset in enumerate([-15, -5, 7]):
        base_x = wx + offset * scale
        base_y = wy + (43 + (idx % 2) * 2) * scale
        finger = [
            (base_x - 4 * scale, base_y),
            (base_x + 8 * scale, base_y + 1 * scale),
            (base_x + (13 + idx * 4) * scale, base_y + 23 * scale),
            (base_x - 4 * scale, base_y + 19 * scale),
        ]
        draw.polygon(finger, fill=arm, outline=outline)
        draw.polygon(
            [
                (finger[2][0], finger[2][1]),
                (finger[2][0] + 9 * scale, finger[2][1] + 7 * scale),
                (finger[2][0] - 3 * scale, finger[2][1] + 10 * scale),
            ],
            fill=claw,
            outline=outline,
        )
    for offset in [-23, 20]:
        base_x = wx + offset * scale
        base_y = wy + 42 * scale
        nub = [
            (base_x - 3 * scale, base_y),
            (base_x + 4 * scale, base_y + 1 * scale),
            (base_x + 5 * scale, base_y + 9 * scale),
            (base_x - 3 * scale, base_y + 8 * scale),
        ]
        draw.polygon(nub, fill=(100, 74, 50), outline=outline)


def draw_guide():
    img = Image.new("RGB", (1152, 768), (204, 226, 226))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 596, 1152, 768), fill=(207, 184, 132))
    for x in range(0, 1152, 44):
        y = 628 + (x * 7) % 70
        draw.line((x, y, x + 16, y - 16), fill=(134, 112, 74), width=2)

    outline = (42, 32, 24)
    body = (116, 88, 59)
    dark = (82, 61, 42)
    light = (151, 117, 79)
    control = (205, 70, 48)

    tail = [(654, 390), (1036, 348), (1128, 366), (1034, 404), (650, 452)]
    body_poly = [
        (250, 410),
        (360, 330),
        (540, 314),
        (688, 352),
        (770, 420),
        (750, 512),
        (614, 574),
        (404, 560),
        (276, 496),
    ]
    belly = [(278, 488), (414, 532), (614, 532), (740, 496), (680, 584), (404, 612), (260, 538)]
    neck = [(252, 402), (194, 344), (212, 300), (316, 326), (356, 392)]
    skull = [
        (44, 350),
        (104, 298),
        (214, 284),
        (318, 314),
        (342, 362),
        (294, 410),
        (160, 418),
        (58, 394),
    ]
    jaw = [(48, 370), (172, 374), (304, 366), (262, 404), (132, 410), (56, 392)]

    for pts, fill in [(tail, dark), (body_poly, body), (belly, (96, 72, 49)), (neck, dark), (skull, light), (jaw, (99, 73, 49))]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((132, 326, 147, 340), fill=(18, 14, 10))
    draw.arc((54, 370, 288, 414), 188, 350, fill=(28, 22, 17), width=3)

    # Forelimbs must stay longer than T. rex arms but compact, folded, and non-weight-bearing.
    draw_herrera_hand(draw, (374, 450), scale=0.92)
    draw_herrera_hand(draw, (422, 456), scale=0.72)

    legs = [
        (492, 506, 540, 692, dark, -1, 0.92),
        (650, 494, 704, 692, body, 1, 0.96),
    ]
    for x0, y0, x1, y1, fill, flip, scale in legs:
        thigh = [(x0, y0), (x1 + 28, y0 + 8), (x1, y1 - 84), (x0 - 38, y1 - 94)]
        shin = [(x1 - 10, y1 - 88), (x1 + 28, y1 - 78), (x1 + 18, y1), (x1 - 22, y1 - 4)]
        draw.polygon(thigh, fill=fill, outline=outline)
        draw.polygon(shin, fill=(98, 73, 49), outline=outline)
        draw_toes(draw, x1 - 18 if flip < 0 else x1 - 8, y1 - 4, flip=flip, scale=scale)

    draw.line((76, 344, 326, 356), fill=control, width=5)
    draw.arc((210, 292, 780, 555), 190, 354, fill=control, width=4)
    draw.arc((650, 348, 1130, 404), 180, 350, fill=control, width=4)
    draw.ellipse((326, 396, 466, 524), outline=control, width=5)
    draw.text((330, 378), "compact arms: 3 main digits + tiny outers", fill=(108, 50, 37), font=font)
    draw.text((54, 266), "closed narrow head, not T. rex", fill=(108, 50, 37), font=font)
    draw.text((28, 32), "structure guide: Herrerasaurus narrow head, compact folded hands, two hind legs, full tail", fill=(38, 35, 31), font=font)

    GUIDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(GUIDE_OUT)
    return img


def fit_image(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (237, 234, 226))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
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
        crop_tile(guide, (34, 266, 360, 424), "guide head: narrow closed skull, not T. rex"),
        crop_tile(current, (60, 160, 540, 390), "current v2 closed-head crop"),
        crop_tile(guide, (310, 374, 490, 538), "guide hands: three main digits plus tiny outer digits"),
        crop_tile(current, (440, 365, 670, 590), "current v2 compact-hand crop"),
        crop_tile(guide, (230, 304, 790, 590), "guide body: slim saurischian torso and long tail base"),
        crop_tile(current, (300, 280, 1660, 570), "current v2 torso and full-tail crop"),
        crop_tile(guide, (456, 482, 736, 724), "guide legs: exactly two hind legs, dry three-toed feet"),
        crop_tile(current, (590, 430, 1070, 810), "current v2 hind legs and feet crop"),
        crop_tile(Image.open(BALANCED_HAND).convert("RGB"), (410, 360, 700, 650), "risk: balanced v2 hand may read as too many long fingers"),
        crop_tile(Image.open(LONG_ARMS).convert("RGB"), (250, 320, 575, 660), "risk: long-arm comparison can overlengthen hand claws"),
    ]
    sheet = Image.new("RGB", (760, 1460), (226, 222, 212))
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
        sheet_card(CURRENT, "current v2 candidate", "keep first; best closed head, tail, two legs, compact hands"),
        sheet_card(CURRENT_CROPS, "current v2 crop gate", "head, compact hands, hind legs, feet, and tail review"),
        sheet_card(GUIDE_OUT, "new Herrerasaurus body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v2 crop gate", "compare head, hands, two legs, feet, tail"),
        sheet_card(BALANCED_HAND, "balanced-arm v2 comparison", "polished body, but hand-count risk is higher"),
        sheet_card(PREVIOUS_STRICT, "previous strict compact v1", "good narrow head and body, smaller scene and weaker hands"),
        sheet_card(HAND_RISK, "strict v1 hand-risk comparison", "strong body gate, but dangling hand claws are too long"),
        sheet_card(CLOSED_JAW, "closed-jaw head-blend comparison", "useful body gate; weaker hand/body read"),
        sheet_card(LONG_ARMS, "long-arm IP-Control comparison", "kept as arm-length gate, but open mouth/head bulk weaker"),
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
    draw.text((22, 20), "Herrerasaurus compact-hand body-lock review v8", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the guide to preserve the narrow closed head, compact folded hands, two hind legs, and long tail.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, BALANCED_HAND, PREVIOUS_STRICT, HAND_RISK, CLOSED_JAW, LONG_ARMS):
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
