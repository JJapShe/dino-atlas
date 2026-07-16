from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "ankylosaurus-magniventris-armor-tailclub-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "ankylosaurus-armor-tailclub-crops-v6.png"
SHEET_OUT = ASSET_ROOT / "ankylosaurus-review-options-v11.png"

CURRENT = ASSET_ROOT / "ankylosaurus-magniventris-broadskull-singleclub-imagegen-v5.png"
CURRENT_CROPS = ASSET_ROOT / "ankylosaurus-broadskull-singleclub-crops-v5.png"
HORN_RISK = ASSET_ROOT / "ankylosaurus-magniventris-hornrisk-comparison-v5.png"
LIZARD_DRIFT = ASSET_ROOT / "ankylosaurus-magniventris-tailclub-surface-v1.png"
OLD_GUIDE = ASSET_ROOT / "ankylosaurus-magniventris.png"


def draw_wrapped(draw, xy, text, font, fill, max_chars=64, line_h=15, max_lines=2):
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


def draw_toes(draw, x, y, flip=1):
    outline = (54, 43, 31)
    toe_fill = (126, 103, 75)
    for idx in range(4):
        dx = (idx - 1.5) * 17
        pts = [
            (x + flip * (dx - 8), y),
            (x + flip * (dx + 12), y - 2),
            (x + flip * (dx + 27), y + 10),
            (x + flip * (dx + 3), y + 16),
        ]
        draw.polygon(pts, fill=toe_fill, outline=outline)


def draw_osteoderm(draw, cx, cy, rx, ry, fill, outline):
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=outline)
    draw.ellipse((cx - rx + 3, cy - ry + 3, cx + rx - 3, cy + ry - 3), fill=fill)
    draw.arc((cx - rx + 7, cy - ry + 6, cx + rx - 5, cy + ry - 4), 190, 350, fill=(232, 203, 140), width=2)


def draw_guide():
    img = Image.new("RGB", (1152, 768), (199, 220, 217))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle((0, 582, 1152, 768), fill=(203, 182, 132))
    for x in range(0, 1152, 38):
        y = 610 + (x * 13) % 84
        draw.line((x, y, x + 16, y - 24), fill=(131, 114, 80), width=2)
    for x in range(20, 1130, 90):
        y = 640 + (x * 7) % 60
        draw.ellipse((x, y, x + 24, y + 10), fill=(148, 127, 91), outline=(105, 88, 62))

    outline = (45, 36, 27)
    dark = (82, 67, 47)
    body = (113, 91, 61)
    armor = (168, 139, 88)
    armor_dark = (130, 105, 70)
    control = (204, 72, 49)

    tail = [(770, 468), (1025, 485), (1056, 512), (1018, 542), (750, 514)]
    club = (1004, 462, 1128, 554)
    body_poly = [
        (188, 452),
        (270, 386),
        (430, 330),
        (640, 326),
        (782, 374),
        (826, 456),
        (776, 540),
        (620, 590),
        (394, 584),
        (238, 532),
    ]
    belly = [(246, 504), (402, 552), (624, 560), (766, 514), (736, 590), (392, 626), (230, 570)]
    neck = [(188, 440), (142, 438), (124, 474), (190, 494)]
    skull = [(42, 452), (74, 416), (150, 396), (226, 420), (224, 472), (160, 500), (74, 492)]
    cheek = [(120, 432), (218, 424), (226, 464), (160, 492), (92, 476)]

    for pts, fill in [(tail, dark), (body_poly, body), (belly, (95, 77, 54)), (neck, dark), (skull, (104, 85, 59)), (cheek, (78, 63, 45))]:
        draw.polygon(pts, fill=fill, outline=outline)
    draw.ellipse(club, fill=outline)
    draw.ellipse((club[0] + 9, club[1] + 8, club[2] - 8, club[3] - 8), fill=(122, 100, 69))
    draw.line((765, 494, 1018, 508), fill=control, width=5)
    draw.arc((1004, 462, 1128, 554), 190, 340, fill=control, width=5)

    draw.ellipse((94, 430, 109, 443), fill=(20, 17, 13))
    draw.arc((48, 456, 146, 496), 188, 350, fill=(30, 25, 19), width=2)

    legs = [
        (282, 518, 330, 665, dark, -1),
        (424, 532, 474, 672, body, -1),
        (604, 530, 654, 672, dark, 1),
        (730, 506, 780, 654, body, 1),
    ]
    for x0, y0, x1, y1, fill, flip in legs:
        leg = [(x0, y0), (x1, y0 + 6), (x1 - 10, y1), (x0 - 24, y1 - 10)]
        foot = [(x0 - 38, y1 - 8), (x1 + 32, y1 - 6), (x1 + 48, y1 + 15), (x0 - 44, y1 + 18)]
        draw.polygon(leg, fill=fill, outline=outline)
        draw.polygon(foot, fill=(89, 71, 50), outline=outline)
        draw_toes(draw, x0 + 18, y1 + 5, flip=flip)

    # Low rounded armor rows: no Stegosaurus plates, no tall fantasy spikes.
    rows = [
        [(255, 398), (336, 368), (424, 350), (520, 344), (616, 350), (704, 378), (770, 424)],
        [(230, 448), (318, 416), (418, 394), (526, 388), (638, 402), (740, 438)],
        [(256, 494), (352, 470), (466, 454), (586, 458), (698, 488)],
        [(190, 430), (152, 424), (112, 430), (82, 448)],
        [(812, 474), (884, 484), (952, 496), (1032, 508)],
    ]
    for row_idx, row in enumerate(rows):
        for idx, (x, y) in enumerate(row):
            rx = 22 - min(8, row_idx * 3) + (idx % 2) * 2
            ry = 13 - min(5, row_idx * 2)
            draw_osteoderm(draw, x, y, rx, ry, armor if row_idx < 3 else armor_dark, outline)

    # Control strokes intentionally remain visible for image-to-image review.
    draw.arc((188, 312, 830, 590), 192, 350, fill=control, width=4)
    draw.line((130, 440, 220, 430), fill=control, width=4)
    draw.line((220, 526, 770, 540), fill=(45, 36, 27), width=3)
    draw.text(
        (28, 32),
        "structure guide: broad blunt skull, squat low armor rows, four sturdy feet, single fused tail club",
        fill=(38, 35, 31),
        font=font,
    )

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
        crop_tile(guide, (40, 370, 250, 520), "guide skull: broad blunt wedge, not crocodile snout"),
        crop_tile(current, (65, 315, 500, 585), "current v5 skull crop"),
        crop_tile(guide, (188, 300, 830, 600), "guide body: low squat armored mass"),
        crop_tile(current, (380, 205, 1185, 520), "current v5 armor rows crop"),
        crop_tile(guide, (740, 440, 1140, 570), "guide tail: one fused oval club, attached"),
        crop_tile(current, (1325, 320, 1745, 575), "current v5 tail club crop"),
        crop_tile(guide, (235, 500, 820, 720), "guide feet: four sturdy planted limbs"),
        crop_tile(current, (285, 575, 1285, 815), "current v5 front/rear feet crop"),
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
        sheet_card(CURRENT, "current v5 candidate", "keep first; best broad-skull single-club compromise"),
        sheet_card(CURRENT_CROPS, "current v5 crop gate", "skull, armor rows, club, and feet review"),
        sheet_card(GUIDE_OUT, "new armor/tail-club guide", "ControlNet/i2i structure target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v5 crop gate", "compare skull, armor rows, tail club, and feet"),
        sheet_card(HORN_RISK, "v5 horn-risk rejection", "strong club/feet but skull side projections read wrong"),
        sheet_card(LIZARD_DRIFT, "older lizard-drift rejection", "tail club present, but body is not ankylosaurid"),
        sheet_card(OLD_GUIDE, "older structure reference", "useful target, but less explicit for armor rows and feet"),
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
    draw.text((22, 20), "Ankylosaurus armor/tail-club review v11", fill=(248, 246, 238), font=font)
    draw.text(
        (22, 46),
        "Use the new guide to prevent lizard/crocodile drift; it is not a promoted candidate.",
        fill=(216, 226, 214),
        font=font,
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, HORN_RISK, LIZARD_DRIFT, OLD_GUIDE):
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
