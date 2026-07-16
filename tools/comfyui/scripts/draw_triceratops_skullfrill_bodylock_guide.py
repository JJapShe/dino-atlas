from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "triceratops-skullfrill-bodylock-crops-v10.png"
SHEET_OUT = ASSET_ROOT / "triceratops-review-options-v16.png"

CURRENT = ASSET_ROOT / "triceratops-horridus-lowbody-closedbeak-i2i-v9.png"
CURRENT_CROPS = ASSET_ROOT / "triceratops-lowbody-closedbeak-i2i-crops-v9.png"
V8_REJECTION = ASSET_ROOT / "triceratops-closedbeak-v8-rejection-crops.png"
OLD_RHINO = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"
OLD_GUIDE = ASSET_ROOT / "triceratops-horridus-ceratopsian-reference-guide-v1.png"


def draw_horn(draw, points, fill, outline):
    draw.polygon(points, fill=fill, outline=outline)
    base = ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
    draw.line((base, points[2]), fill=(248, 228, 166), width=2)


def draw_toes(draw, x, y, flip):
    for idx in range(3):
        dx = (idx - 1) * 15
        pts = [
            (x + flip * (dx - 10), y),
            (x + flip * (dx + 16), y + 2),
            (x + flip * (dx + 32), y + 14),
            (x + flip * (dx + 2), y + 17),
        ]
        draw.polygon(pts, fill=(150, 121, 82), outline=(45, 36, 28))


def draw_guide():
    img = Image.new("RGB", (1152, 768), (202, 224, 223))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 590, 1152, 768), fill=(204, 186, 142))
    for x in range(0, 1152, 42):
        y = 616 + (x * 11) % 62
        draw.line((x, y, x + 12, y - 20), fill=(137, 121, 84), width=2)

    outline = (42, 34, 26)
    body = (125, 101, 69)
    dark = (84, 66, 46)
    frill = (133, 111, 78)
    horn = (229, 205, 145)

    tail = [(780, 430), (1078, 348), (1120, 365), (824, 492)]
    body_poly = [(338, 398), (456, 346), (626, 328), (768, 352), (842, 408), (836, 500), (720, 562), (514, 570), (374, 526), (300, 462)]
    chest = [(304, 386), (400, 374), (440, 438), (408, 518), (326, 514), (278, 450)]
    neck = [(310, 392), (224, 380), (198, 426), (306, 466)]
    hip = [(718, 388), (806, 396), (842, 468), (804, 536), (718, 520), (688, 444)]
    for pts, fill in [(tail, dark), (body_poly, body), (hip, (103, 83, 58)), (chest, dark), (neck, dark)]:
        draw.polygon(pts, fill=fill, outline=outline)

    # Skull-attached frill, separated from the shoulder by a visible neck gap.
    frill_pts = [(212, 282), (274, 252), (350, 268), (412, 330), (420, 410), (374, 490), (292, 512), (222, 474), (184, 410), (176, 332)]
    draw.polygon(frill_pts, fill=frill, outline=outline)
    draw.arc((184, 296, 402, 504), 104, 264, fill=(205, 174, 112), width=3)
    for x, y in [(230, 314), (274, 292), (326, 302), (366, 338), (388, 388), (374, 444), (330, 482), (270, 486), (218, 444), (198, 382)]:
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(62, 49, 35))

    head = [(54, 414), (100, 374), (184, 366), (252, 398), (236, 446), (162, 472), (74, 458)]
    cheek = [(184, 394), (254, 400), (244, 452), (184, 468), (150, 430)]
    beak = [(32, 424), (66, 404), (78, 430), (58, 454)]
    for pts, fill in [(head, (116, 90, 59)), (cheek, (91, 70, 48)), (beak, (70, 55, 40))]:
        draw.polygon(pts, fill=fill, outline=outline)
    draw.ellipse((113, 397, 129, 413), fill=(18, 15, 12))
    draw.arc((60, 424, 146, 466), 188, 350, fill=(28, 22, 17), width=2)

    draw_horn(draw, [(148, 368), (184, 382), (128, 244)], horn, outline)
    draw_horn(draw, [(190, 380), (222, 398), (244, 254)], horn, outline)
    draw_horn(draw, [(58, 400), (82, 408), (38, 352)], horn, outline)

    for x0, y0, x1, y1, fill, flip in [
        (330, 490, 386, 650, dark, -1),
        (456, 500, 504, 660, (132, 101, 68), -1),
        (650, 498, 706, 662, dark, 1),
        (792, 476, 844, 652, (132, 101, 68), 1),
    ]:
        leg = [(x0, y0), (x1, y0), (x1 - 14, y1), (x0 - 28, y1 - 8)]
        draw.polygon(leg, fill=fill, outline=outline)
        foot = [(x0 - 42, y1 - 8), (x1 + 24, y1 - 4), (x1 + 50, y1 + 18), (x0 - 36, y1 + 20)]
        draw.polygon(foot, fill=(86, 66, 45), outline=outline)
        draw_toes(draw, x1 + (12 if flip > 0 else -18), y1 + 7, flip)

    # Body-lock guide lines: these are intentionally visible for ControlNet/QA.
    draw.arc((318, 360, 850, 598), 190, 350, fill=(224, 184, 95), width=3)
    draw.arc((334, 418, 832, 626), 10, 172, fill=(47, 36, 27), width=3)
    draw.line((252, 508, 310, 466), fill=(204, 72, 49), width=5)
    draw.line((410, 420, 472, 390), fill=(204, 72, 49), width=5)
    draw.text((28, 34), "structure guide: skull-attached frill, three horns, low long body, non-hoofed toes", fill=(38, 35, 31), font=ImageFont.load_default())

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
    crop = image.crop(box)
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (size[0], size[1] + 42), (246, 244, 237))
    tile.paste(crop, ((size[0] - crop.width) // 2, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((10, size[1] + 12), label[:58], fill=(42, 38, 34), font=ImageFont.load_default())
    return tile


def make_crops(guide):
    current = Image.open(CURRENT).convert("RGB")
    tiles = [
        crop_tile(guide, (150, 230, 450, 530), "guide skull: frill attached behind skull, not shoulder"),
        crop_tile(current, (0, 120, 470, 470), "current v9 skull/frill crop"),
        crop_tile(guide, (260, 330, 880, 650), "guide low body + long tail + four limbs"),
        crop_tile(current, (250, 360, 1110, 690), "current v9 low body/tail crop"),
        crop_tile(guide, (290, 560, 890, 720), "guide non-hoofed toes"),
        crop_tile(current, (250, 540, 760, 760), "current v9 front/rear toes"),
    ]
    sheet = Image.new("RGB", (760, 876), (226, 222, 212))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % 2) * 380, (idx // 2) * 292))
    sheet.save(CROPS_OUT)


def sheet_card(path, title, note, size=(360, 240)):
    tile = Image.new("RGB", (size[0], size[1] + 78), (246, 244, 237))
    tile.paste(fit_image(path, size), (0, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((10, size[1] + 10), title[:52], fill=(95, 57, 45), font=ImageFont.load_default())
    draw.text((10, size[1] + 32), note[:66], fill=(42, 38, 34), font=ImageFont.load_default())
    return tile


def make_review_sheet():
    cards = [
        sheet_card(CURRENT, "current v9 candidate", "keep first; best low-body closed-beak compromise"),
        sheet_card(CURRENT_CROPS, "current v9 crop gate", "head, frill, beak, toes, body and tail review"),
        sheet_card(GUIDE_OUT, "new skull/frill body-lock guide", "ControlNet/LoRA target, not final paleoart"),
        sheet_card(CROPS_OUT, "new guide vs v9 crop gate", "compare skull-attached frill and low body"),
        sheet_card(V8_REJECTION, "v8 closed-beak rejection", "mouth improved but rhino-like torso returned"),
        sheet_card(OLD_RHINO, "old rhino-drift rejection", "explicit failure comparison"),
        sheet_card(OLD_GUIDE, "previous ceratopsian guide", "useful but weaker body-lock markings"),
    ]
    cols = 3
    gap = 14
    header_h = 86
    card_w, card_h = 360, 318
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * card_w + (cols + 1) * gap, header_h + rows * (card_h + gap) + gap), (226, 222, 212))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, header_h), fill=(28, 62, 48))
    draw.text((22, 20), "Triceratops skull/frill body-lock review v16", fill=(248, 246, 238), font=ImageFont.load_default())
    draw.text((22, 46), "Use the new guide to prevent rhinoceros drift; it is not a promoted candidate.", fill=(216, 226, 214), font=ImageFont.load_default())
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    guide = draw_guide()
    make_crops(guide)
    make_review_sheet()
    print(GUIDE_OUT)
    print(CROPS_OUT)
    print(SHEET_OUT)


if __name__ == "__main__":
    main()
