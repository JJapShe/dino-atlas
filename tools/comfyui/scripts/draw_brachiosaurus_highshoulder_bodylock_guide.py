from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "brachiosaurus-highshoulder-bodylock-crops-v8.png"
SHEET_OUT = ASSET_ROOT / "brachiosaurus-review-options-v8.png"

CURRENT = ASSET_ROOT / "brachiosaurus-altithorax-tail-reduced-i2i-v4.png"
CURRENT_CROPS = ASSET_ROOT / "brachiosaurus-tail-reduced-i2i-crops-v4.png"
SOURCE_V3 = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-shorttail-imagegen-v3.png"
TALL_FORELIMB_V3 = ASSET_ROOT / "brachiosaurus-altithorax-tallforelimb-shorttail-imagegen-v3.png"
BALANCED_V2 = ASSET_ROOT / "brachiosaurus-altithorax-balancedneck-imagegen-v2.png"
OLD_GUIDE = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-controlnet-v1.png"


def draw_wrapped(draw, xy, text, font, fill, max_chars=62, line_h=15, max_lines=2):
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
    outline = (55, 43, 33)
    fill = (112, 91, 68)
    pts = [
        (x - flip * 20 * scale, y),
        (x + flip * 58 * scale, y - 3 * scale),
        (x + flip * 88 * scale, y + 15 * scale),
        (x + flip * 12 * scale, y + 25 * scale),
        (x - flip * 28 * scale, y + 18 * scale),
    ]
    draw.polygon(pts, fill=fill, outline=outline)
    for idx in range(3):
        tx = x + flip * (26 + idx * 18) * scale
        draw.ellipse(
            (tx - 5 * scale, y + 11 * scale, tx + 13 * scale, y + 23 * scale),
            fill=(166, 139, 99),
            outline=outline,
        )


def draw_guide():
    img = Image.new("RGB", (1152, 768), (204, 225, 225))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 586, 1152, 768), fill=(205, 185, 134))
    for x in range(0, 1152, 48):
        y = 624 + (x * 9) % 64
        draw.line((x, y, x + 18, y - 20), fill=(130, 113, 76), width=2)
    for x in range(30, 1120, 115):
        y = 650 + (x * 5) % 50
        draw.ellipse((x, y, x + 26, y + 8), fill=(142, 122, 83), outline=(102, 84, 57))

    outline = (45, 35, 27)
    body = (118, 98, 72)
    dark = (88, 72, 53)
    light = (150, 127, 91)
    control = (205, 70, 48)

    tail = [(744, 440), (1018, 455), (1108, 492), (1034, 520), (730, 500)]
    body_poly = [
        (236, 392),
        (318, 296),
        (498, 266),
        (678, 320),
        (790, 398),
        (766, 510),
        (612, 574),
        (386, 560),
        (250, 504),
    ]
    belly = [(296, 492), (430, 540), (614, 540), (740, 496), (710, 570), (420, 610), (260, 548)]
    shoulder_mass = [(262, 372), (318, 292), (470, 270), (520, 350), (464, 478), (316, 500)]
    hip_mass = [(612, 338), (744, 388), (780, 486), (696, 538), (594, 506), (566, 406)]
    neck = [(246, 382), (176, 276), (116, 170), (90, 110), (132, 94), (200, 164), (286, 304), (324, 378)]
    head = [(54, 84), (112, 58), (184, 72), (208, 106), (164, 136), (88, 126)]

    for pts, fill in [
        (tail, dark),
        (body_poly, body),
        (belly, (98, 80, 59)),
        (shoulder_mass, light),
        (hip_mass, (105, 86, 63)),
        (neck, light),
        (head, (129, 106, 76)),
    ]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((108, 86, 122, 99), fill=(18, 15, 12))
    draw.arc((52, 96, 144, 140), 190, 350, fill=(34, 27, 20), width=2)
    draw.arc((86, 56, 182, 116), 200, 336, fill=(202, 174, 118), width=2)

    legs = [
        (304, 474, 364, 684, light, -1, 1.05),
        (430, 488, 486, 684, body, -1, 0.95),
        (604, 486, 656, 668, dark, 1, 0.88),
        (722, 470, 770, 648, body, 1, 0.82),
    ]
    for x0, y0, x1, y1, fill, flip, foot_scale in legs:
        leg = [(x0, y0), (x1, y0 + 8), (x1 - 8, y1), (x0 - 26, y1 - 10)]
        draw.polygon(leg, fill=fill, outline=outline)
        draw_foot(draw, x0 - 8 if flip < 0 else x0 + 4, y1 - 2, foot_scale, flip=flip)

    # Visible control marks for image-to-image / ControlNet review.
    draw.line((326, 304, 746, 398), fill=control, width=5)
    draw.line((332, 680, 762, 650), fill=control, width=4)
    draw.line((314, 474, 364, 684), fill=(230, 197, 108), width=4)
    draw.line((728, 470, 770, 648), fill=(230, 197, 108), width=4)
    draw.arc((84, 72, 338, 404), 250, 35, fill=control, width=4)
    draw.arc((728, 426, 1110, 524), 184, 350, fill=control, width=4)

    draw.text(
        (28, 32),
        "structure guide: high shoulders, taller forelimbs, rising neck, short thick tail, four pillar feet",
        fill=(38, 35, 31),
        font=font,
    )
    draw.text((828, 48), "tail shorter than diplodocids", fill=(108, 50, 37), font=font)
    draw.text((344, 246), "shoulders above hips", fill=(108, 50, 37), font=font)

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
        crop_tile(guide, (214, 238, 814, 570), "guide body: high shoulder slopes down to hip"),
        crop_tile(current, (360, 130, 1190, 600), "current v4 body slope crop"),
        crop_tile(guide, (270, 430, 830, 720), "guide legs: front limbs taller than hind limbs"),
        crop_tile(current, (340, 520, 1120, 960), "current v4 four pillar feet crop"),
        crop_tile(guide, (72, 58, 350, 414), "guide neck/head: rising neck, small nasal head"),
        crop_tile(current, (0, 0, 520, 420), "current v4 neck/head crop"),
        crop_tile(guide, (706, 410, 1132, 550), "guide tail: short thick taper, fully framed"),
        crop_tile(current, (920, 330, 1570, 725), "current v4 tail crop"),
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
        sheet_card(CURRENT, "current v4 candidate", "keep first; best tail-reduced high-shoulder compromise"),
        sheet_card(CURRENT_CROPS, "current v4 crop gate", "tail, hip blend, shoulder slope, feet review"),
        sheet_card(GUIDE_OUT, "new high-shoulder body-lock guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v4 crop gate", "compare shoulder height, legs, neck, and tail"),
        sheet_card(SOURCE_V3, "source v3 high-shoulder candidate", "strong body identity, kept below v4 for tail length"),
        sheet_card(TALL_FORELIMB_V3, "v3 tall-forelimb comparison", "useful tall-front-limb cue; weaker foot/tail edge"),
        sheet_card(BALANCED_V2, "previous v2 comparison", "good balanced neck, weaker short-tail body lock"),
        sheet_card(OLD_GUIDE, "older ControlNet comparison", "kept as historical guide-conditioned comparison"),
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
    draw.text((22, 20), "Brachiosaurus high-shoulder body-lock review v8", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the new guide to prevent diplodocid drift; it is not a promoted candidate.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, SOURCE_V3, TALL_FORELIMB_V3, BALANCED_V2, OLD_GUIDE):
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
