from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "tyrannosaurus-rex-twofinger-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "tyrannosaurus-twofinger-bodylock-crops-v8.png"
SHEET_OUT = ASSET_ROOT / "tyrannosaurus-review-options-v8.png"

CURRENT = ASSET_ROOT / "tyrannosaurus-rex-twofinger-hand-i2i-v4.png"
CURRENT_CROPS = ASSET_ROOT / "tyrannosaurus-twofinger-hand-i2i-crops-v4.png"
SOURCE_V3 = ASSET_ROOT / "tyrannosaurus-rex-smoothbrow-twofinger-imagegen-v3.png"
SOURCE_CROPS = ASSET_ROOT / "tyrannosaurus-smoothbrow-twofinger-crops-v3.png"
VISIBLE_ARMS = ASSET_ROOT / "tyrannosaurus-rex-visiblearms-comparison-v3.png"
BROADSIDE_V2 = ASSET_ROOT / "tyrannosaurus-rex-broadside-twofinger-comparison-v2.png"
LORA_V2 = ASSET_ROOT / "tyrannosaurus-rex-lora-v2.png"


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
    outline = (46, 36, 27)
    for idx in range(3):
        dx = (idx - 1) * 24 * scale
        pts = [
            (x + flip * (dx - 12 * scale), y),
            (x + flip * (dx + 20 * scale), y + 2 * scale),
            (x + flip * (dx + 46 * scale), y + 16 * scale),
            (x + flip * (dx + 4 * scale), y + 24 * scale),
        ]
        draw.polygon(pts, fill=(111, 87, 61), outline=outline)


def draw_two_finger_hand(draw, wrist, scale=1.0):
    wx, wy = wrist
    outline = (45, 35, 26)
    arm_fill = (103, 80, 56)
    claw = (232, 210, 151)
    upper = [(wx - 62 * scale, wy - 18 * scale), (wx - 10 * scale, wy - 6 * scale), (wx - 20 * scale, wy + 18 * scale), (wx - 72 * scale, wy + 6 * scale)]
    fore = [(wx - 22 * scale, wy + 10 * scale), (wx + 18 * scale, wy + 26 * scale), (wx + 4 * scale, wy + 48 * scale), (wx - 34 * scale, wy + 30 * scale)]
    draw.polygon(upper, fill=arm_fill, outline=outline)
    draw.polygon(fore, fill=(91, 70, 49), outline=outline)
    for idx, angle in enumerate([-1, 1]):
        base_x = wx + (6 + idx * 14) * scale
        base_y = wy + (42 + idx * 2) * scale
        finger = [
            (base_x - 4 * scale, base_y),
            (base_x + 8 * scale, base_y + 2 * scale),
            (base_x + (18 + angle * 6) * scale, base_y + 20 * scale),
            (base_x + angle * 4 * scale, base_y + 18 * scale),
        ]
        draw.polygon(finger, fill=arm_fill, outline=outline)
        draw.polygon(
            [
                (finger[2][0], finger[2][1]),
                (finger[2][0] + (10 + angle * 4) * scale, finger[2][1] + 6 * scale),
                (finger[2][0] - 2 * scale, finger[2][1] + 12 * scale),
            ],
            fill=claw,
            outline=outline,
        )


def draw_guide():
    img = Image.new("RGB", (1152, 768), (205, 225, 225))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 590, 1152, 768), fill=(204, 184, 132))
    for x in range(0, 1152, 46):
        y = 628 + (x * 11) % 70
        draw.line((x, y, x + 15, y - 20), fill=(132, 112, 74), width=2)

    outline = (42, 33, 25)
    body = (111, 89, 64)
    dark = (77, 60, 44)
    light = (142, 117, 82)
    control = (205, 70, 48)

    tail = [(686, 360), (1048, 316), (1128, 336), (1046, 380), (678, 430)]
    body_poly = [
        (214, 392),
        (328, 310),
        (512, 276),
        (674, 306),
        (778, 380),
        (778, 492),
        (640, 560),
        (414, 560),
        (260, 500),
    ]
    belly = [(260, 486), (424, 532), (640, 530), (756, 486), (710, 570), (418, 614), (250, 540)]
    neck = [(224, 386), (180, 332), (204, 286), (304, 314), (332, 380)]
    skull = [
        (24, 346),
        (82, 292),
        (194, 270),
        (302, 298),
        (332, 352),
        (286, 414),
        (156, 424),
        (56, 398),
    ]
    jaw = [(34, 366), (156, 374), (288, 366), (244, 406), (116, 412), (44, 394)]

    for pts, fill in [(tail, dark), (body_poly, body), (belly, (92, 72, 52)), (neck, dark), (skull, light), (jaw, (96, 75, 52))]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((130, 318, 146, 334), fill=(18, 14, 10))
    draw.arc((50, 362, 278, 414), 188, 350, fill=(28, 22, 17), width=3)
    draw.arc((80, 286, 280, 360), 195, 345, fill=(225, 194, 126), width=2)

    # Tiny forelimbs must stay small and chest-held, but two fingers are explicit.
    draw_two_finger_hand(draw, (372, 428), scale=1.0)
    draw_two_finger_hand(draw, (414, 436), scale=0.82)

    legs = [
        (492, 500, 552, 690, dark, -1, 1.0),
        (662, 486, 718, 690, body, 1, 1.0),
    ]
    for x0, y0, x1, y1, fill, flip, scale in legs:
        thigh = [(x0, y0), (x1 + 18, y0 + 8), (x1, y1 - 82), (x0 - 48, y1 - 90)]
        shin = [(x1 - 8, y1 - 92), (x1 + 30, y1 - 82), (x1 + 20, y1), (x1 - 24, y1 - 4)]
        draw.polygon(thigh, fill=fill, outline=outline)
        draw.polygon(shin, fill=(96, 74, 52), outline=outline)
        draw_toes(draw, x1 - 18 if flip < 0 else x1 - 8, y1 - 4, flip=flip, scale=scale)

    # Control strokes for QA and ControlNet.
    draw.line((78, 338, 318, 350), fill=control, width=5)
    draw.arc((204, 274, 790, 552), 190, 354, fill=control, width=4)
    draw.arc((674, 306, 1130, 382), 180, 350, fill=control, width=4)
    draw.ellipse((326, 386, 462, 508), outline=control, width=5)
    draw.text((344, 374), "tiny arms: 2 fingers only", fill=(108, 50, 37), font=font)
    draw.text((48, 252), "massive deep skull, no horns", fill=(108, 50, 37), font=font)
    draw.text((28, 32), "structure guide: massive T. rex body, tiny chest-held arms, exactly two fingers, heavy tail", fill=(38, 35, 31), font=font)

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
        crop_tile(guide, (12, 248, 352, 430), "guide skull: massive deep head, no horns/crest"),
        crop_tile(current, (0, 165, 520, 470), "current v4 skull crop"),
        crop_tile(guide, (300, 360, 490, 535), "guide arms: tiny chest-held, exactly two fingers"),
        crop_tile(current, (310, 330, 590, 555), "current v4 hand/arm crop"),
        crop_tile(guide, (190, 270, 810, 585), "guide body: robust torso + heavy balancing tail base"),
        crop_tile(current, (250, 250, 1225, 675), "current v4 torso/tail-base crop"),
        crop_tile(guide, (452, 470, 782, 724), "guide legs: exactly two strong hind legs"),
        crop_tile(current, (450, 560, 940, 920), "current v4 hind legs/feet crop"),
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
        sheet_card(CURRENT, "current v4 candidate", "keep first; best body plus compact two-finger cue"),
        sheet_card(CURRENT_CROPS, "current v4 crop gate", "hand, skull, feet, and tail preservation review"),
        sheet_card(GUIDE_OUT, "new two-finger body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v4 crop gate", "compare skull, tiny arms, two fingers, legs, tail"),
        sheet_card(SOURCE_V3, "source v3 body gate", "strong body and skull; hand cue was softer than v4"),
        sheet_card(SOURCE_CROPS, "source v3 crop gate", "previous skull, arm, feet, and tail close review"),
        sheet_card(VISIBLE_ARMS, "visible-arms comparison", "arms visible but count/brow balance weaker"),
        sheet_card(BROADSIDE_V2, "broadside v2 comparison", "strong pose but one hand risks three claw tips"),
        sheet_card(LORA_V2, "LoRA v2 comparison", "species LoRA shape source; logo/text risk remains"),
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
    draw.text((22, 20), "Tyrannosaurus two-finger body-lock review v8", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the new guide to prevent three-finger/allosaur-arm drift; it is not a promoted candidate.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, SOURCE_V3, SOURCE_CROPS, VISIBLE_ARMS, BROADSIDE_V2, LORA_V2):
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
