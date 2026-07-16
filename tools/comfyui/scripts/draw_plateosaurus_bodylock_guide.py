from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "plateosaurus-engelhardti-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "plateosaurus-bodylock-crops-v4.png"
SHEET_OUT = ASSET_ROOT / "plateosaurus-review-options-v12.png"

CURRENT = ASSET_ROOT / "plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png"
CURRENT_CROPS = ASSET_ROOT / "plateosaurus-singleforelimb-smallhand-crops-v3.png"
THUMBCLAW = ASSET_ROOT / "plateosaurus-engelhardti-smallhand-thumbclaw-imagegen-v3.png"
BIPEDAL_RISK = ASSET_ROOT / "plateosaurus-engelhardti-bipedal-smallhand-imagegen-v3.png"
PREVIOUS_V2 = ASSET_ROOT / "plateosaurus-engelhardti-cleanlimbs-imagegen-v2.png"
FORELIMB_GUIDE = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-reference-guide-v1.png"
SIX_LEG_REJECTION = ASSET_ROOT / "plateosaurus-engelhardti-forelimb-inpaint-v1.png"


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
    toe_fill = (113, 86, 57)
    for idx in range(4):
        dx = (idx - 1.5) * 16 * scale
        pts = [
            (x + flip * (dx - 9 * scale), y),
            (x + flip * (dx + 12 * scale), y + 2 * scale),
            (x + flip * (dx + 34 * scale), y + 13 * scale),
            (x + flip * (dx + 1 * scale), y + 20 * scale),
        ]
        draw.polygon(pts, fill=toe_fill, outline=outline)


def draw_plateosaurus_hand(draw, wrist, scale=1.0):
    wx, wy = wrist
    outline = (43, 32, 24)
    arm = (116, 86, 55)
    dark = (93, 68, 45)
    claw = (235, 212, 148)
    upper = [
        (wx - 72 * scale, wy - 18 * scale),
        (wx - 12 * scale, wy - 8 * scale),
        (wx - 20 * scale, wy + 18 * scale),
        (wx - 80 * scale, wy + 8 * scale),
    ]
    fore = [
        (wx - 26 * scale, wy + 8 * scale),
        (wx + 18 * scale, wy + 20 * scale),
        (wx + 8 * scale, wy + 44 * scale),
        (wx - 38 * scale, wy + 30 * scale),
    ]
    draw.polygon(upper, fill=arm, outline=outline)
    draw.polygon(fore, fill=dark, outline=outline)
    for idx, offset in enumerate([-16, -7, 2, 11, 20]):
        base_x = wx + offset * scale
        base_y = wy + (38 + (idx % 2) * 2) * scale
        length = 27 if idx == 0 else 16 + idx * 2
        width = 7 if idx == 0 else 5
        finger = [
            (base_x - width * scale, base_y),
            (base_x + width * scale, base_y + 1 * scale),
            (base_x + (width + 2) * scale, base_y + length * scale),
            (base_x - (width + 2) * scale, base_y + (length - 3) * scale),
        ]
        draw.polygon(finger, fill=arm, outline=outline)
        if idx == 0:
            draw.polygon(
                [
                    (finger[2][0], finger[2][1]),
                    (finger[2][0] + 14 * scale, finger[2][1] + 9 * scale),
                    (finger[2][0] - 4 * scale, finger[2][1] + 13 * scale),
                ],
                fill=claw,
                outline=outline,
            )


def draw_guide():
    img = Image.new("RGB", (1152, 768), (204, 226, 226))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 602, 1152, 768), fill=(205, 183, 132))
    for x in range(0, 1152, 46):
        y = 630 + (x * 5) % 68
        draw.line((x, y, x + 16, y - 16), fill=(134, 112, 74), width=2)

    outline = (42, 32, 24)
    body = (116, 88, 59)
    dark = (82, 62, 42)
    light = (151, 118, 80)
    control = (205, 70, 48)

    tail = [(662, 394), (1018, 340), (1130, 360), (1020, 404), (656, 468)]
    body_poly = [
        (284, 420),
        (410, 326),
        (598, 320),
        (726, 382),
        (756, 472),
        (650, 558),
        (424, 558),
        (296, 504),
    ]
    belly = [(310, 486), (440, 528), (640, 528), (732, 470), (656, 588), (420, 604), (300, 526)]
    neck = [(296, 416), (214, 330), (188, 250), (250, 224), (360, 346), (392, 418)]
    skull = [
        (70, 236),
        (146, 190),
        (244, 198),
        (300, 242),
        (272, 286),
        (160, 292),
        (82, 272),
    ]
    jaw = [(74, 252), (170, 254), (282, 250), (252, 280), (140, 282), (80, 268)]

    for pts, fill in [(tail, dark), (body_poly, body), (belly, (96, 72, 48)), (neck, dark), (skull, light), (jaw, (99, 73, 49))]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((146, 220, 159, 233), fill=(18, 14, 10))
    draw.arc((80, 250, 274, 286), 188, 346, fill=(28, 22, 17), width=2)

    # Two lifted forelimbs must stay short, off the ground, and hand-like.
    draw_plateosaurus_hand(draw, (396, 456), scale=0.86)
    draw_plateosaurus_hand(draw, (444, 462), scale=0.68)

    legs = [
        (494, 520, 534, 694, dark, -1, 0.9),
        (650, 504, 706, 694, body, 1, 0.95),
    ]
    for x0, y0, x1, y1, fill, flip, scale in legs:
        thigh = [(x0, y0), (x1 + 34, y0 + 8), (x1, y1 - 86), (x0 - 42, y1 - 96)]
        shin = [(x1 - 10, y1 - 90), (x1 + 28, y1 - 78), (x1 + 18, y1), (x1 - 24, y1 - 4)]
        draw.polygon(thigh, fill=fill, outline=outline)
        draw.polygon(shin, fill=(98, 73, 49), outline=outline)
        draw_toes(draw, x1 - 18 if flip < 0 else x1 - 8, y1 - 4, flip=flip, scale=scale)

    draw.line((82, 242, 294, 254), fill=control, width=5)
    draw.arc((188, 224, 408, 432), 152, 312, fill=control, width=4)
    draw.arc((284, 318, 760, 570), 190, 352, fill=control, width=4)
    draw.arc((660, 342, 1132, 404), 180, 350, fill=control, width=4)
    draw.ellipse((350, 412, 488, 522), outline=control, width=5)
    draw.line((325, 548, 505, 548), fill=control, width=4)
    draw.text((340, 392), "lifted hands: 5 fingers + big thumb claw", fill=(108, 50, 37), font=font)
    draw.text((72, 176), "low herbivore head, forward neck", fill=(108, 50, 37), font=font)
    draw.text((328, 554), "no forelimb ground contact", fill=(108, 50, 37), font=font)
    draw.text((28, 32), "structure guide: Plateosaurus low head, long neck, two hind legs only on ground, lifted five-finger hands", fill=(38, 35, 31), font=font)

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
        crop_tile(guide, (54, 174, 318, 300), "guide head: low herbivore skull, not theropod predator"),
        crop_tile(current, (55, 175, 520, 410), "current v3 low herbivore head crop"),
        crop_tile(guide, (330, 386, 510, 535), "guide hands: lifted five fingers plus thumb claw"),
        crop_tile(current, (365, 365, 650, 620), "current v3 lifted forelimb/hand crop"),
        crop_tile(guide, (274, 306, 780, 582), "guide body: bipedal trunk, forelimbs off ground"),
        crop_tile(current, (250, 300, 1600, 655), "current v3 torso/tail and lifted-arm crop"),
        crop_tile(guide, (455, 492, 735, 726), "guide legs: exactly two hind legs on ground"),
        crop_tile(current, (610, 470, 1005, 850), "current v3 separated hind-leg crop"),
        crop_tile(Image.open(SIX_LEG_REJECTION).convert("RGB"), (330, 330, 760, 760), "rejection: forelimbs/overlap read as six legs"),
        crop_tile(current, (865, 405, 1620, 670), "current v3 full single tail crop"),
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
        sheet_card(CURRENT, "current v3 candidate", "keep first; best low head, two hind legs, lifted hand"),
        sheet_card(CURRENT_CROPS, "current v3 crop gate", "head, hand, hind legs, tail, and six-leg rejection"),
        sheet_card(GUIDE_OUT, "new Plateosaurus body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v3 crop gate", "compare no-six-leg stance, hands, feet, tail"),
        sheet_card(THUMBCLAW, "v3 thumb-claw comparison", "strong body, but hands still read hook-like"),
        sheet_card(BIPEDAL_RISK, "v3 extra-limb risk comparison", "overlapped forelimbs can read as extra limbs"),
        sheet_card(PREVIOUS_V2, "previous clean-limb v2", "good low head and two legs; larger hook hands"),
        sheet_card(FORELIMB_GUIDE, "older forelimb guide", "useful hand cue, but weaker no-six-leg control"),
        sheet_card(SIX_LEG_REJECTION, "six-leg rejection", "failure gate: do not promote this limb overlap"),
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
    draw.text((22, 20), "Plateosaurus no-six-leg body-lock review v12", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the guide to keep only two weight-bearing hind legs while preserving short lifted five-finger hands.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, THUMBCLAW, BIPEDAL_RISK, PREVIOUS_V2, FORELIMB_GUIDE, SIX_LEG_REJECTION):
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
