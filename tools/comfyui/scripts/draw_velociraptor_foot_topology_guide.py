from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
GUIDE_OUT = ASSET_ROOT / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
SHEET_OUT = ASSET_ROOT / "velociraptor-review-options-v18.png"
CROPS_OUT = ASSET_ROOT / "velociraptor-foot-topology-crops-v12.png"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
FOOT_I2I_REJECTION = ASSET_ROOT / "velociraptor-foot-i2i-v10-rejection-crops.png"
PROMPT_REJECTION = ASSET_ROOT / "velociraptor-prompt-v11-rejection-crops.png"
OLD_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"


def draw_plume(draw, points, fill, width=2):
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_toe(draw, base, mid, tip, fill, outline, width=10, claw=True):
    draw.line([base, mid, tip], fill=outline, width=width + 4, joint="curve")
    draw.line([base, mid, tip], fill=fill, width=width, joint="curve")
    if claw:
        claw_poly = [
            (tip[0] - 3, tip[1] - 6),
            (tip[0] + 22, tip[1] - 2),
            (tip[0] + 3, tip[1] + 7),
        ]
        draw.polygon(claw_poly, fill=(38, 33, 29), outline=outline)


def draw_sickle(draw, base, control, tip, fill, outline):
    left = []
    right = []
    for i in range(14):
        t = i / 13
        mt = 1 - t
        x = mt * mt * base[0] + 2 * mt * t * control[0] + t * t * tip[0]
        y = mt * mt * base[1] + 2 * mt * t * control[1] + t * t * tip[1]
        nx = -((tip[1] - base[1]) or 1)
        ny = (tip[0] - base[0]) or 1
        nlen = max(1, (nx * nx + ny * ny) ** 0.5)
        nx /= nlen
        ny /= nlen
        half = 12 * (1 - t) + 2 * t
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
    draw.polygon(left + list(reversed(right)), fill=outline)
    inner = []
    inner_r = []
    for i in range(14):
        t = i / 13
        mt = 1 - t
        x = mt * mt * base[0] + 2 * mt * t * control[0] + t * t * tip[0]
        y = mt * mt * base[1] + 2 * mt * t * control[1] + t * t * tip[1]
        nx = -((tip[1] - base[1]) or 1)
        ny = (tip[0] - base[0]) or 1
        nlen = max(1, (nx * nx + ny * ny) ** 0.5)
        nx /= nlen
        ny /= nlen
        half = 8 * (1 - t) + 1 * t
        inner.append((x + nx * half, y + ny * half))
        inner_r.append((x - nx * half, y - ny * half))
    draw.polygon(inner + list(reversed(inner_r)), fill=fill)
    draw.line([base, control, tip], fill=(228, 201, 142), width=2)


def draw_dromaeosaur_foot(draw, ankle, scale=1.0, mirror=False):
    sx = -1 if mirror else 1

    def p(dx, dy):
        return (int(ankle[0] + sx * dx * scale), int(ankle[1] + dy * scale))

    outline = (73, 54, 41)
    skin = (135, 105, 72)
    claw = (38, 33, 29)
    draw.line([p(0, -96), p(-6, -46), p(0, 0)], fill=outline, width=int(20 * scale))
    draw.line([p(0, -96), p(-6, -46), p(0, 0)], fill=skin, width=int(14 * scale))
    draw.ellipse([p(-14, -10), p(18, 18)], fill=skin, outline=outline, width=max(1, int(3 * scale)))

    draw_toe(draw, p(2, 7), p(50, 20), p(98, 14), skin, outline, width=max(5, int(8 * scale)))
    draw_toe(draw, p(-2, 8), p(42, 36), p(90, 42), skin, outline, width=max(5, int(8 * scale)))
    draw_sickle(draw, p(-4, -3), p(22, -60), p(6, -92), claw, outline)
    draw_toe(draw, p(-8, 8), p(-24, 20), p(-42, 18), skin, outline, width=max(4, int(6 * scale)), claw=False)


def draw_full_guide():
    image = Image.new("RGB", (1152, 768), (204, 224, 224))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 568, 1152, 768), fill=(202, 178, 132))
    for x in range(0, 1152, 36):
        y = 584 + (x * 17) % 86
        draw.line([(x, y), (x + 12, y - 22)], fill=(137, 121, 82), width=2)

    body = [(326, 312), (430, 238), (610, 234), (744, 288), (760, 366), (648, 420), (472, 424), (340, 374)]
    tail = [(734, 314), (1076, 244), (1104, 254), (764, 356)]
    neck = [(344, 304), (250, 222), (178, 212), (184, 252), (296, 336)]
    head = [(171, 207), (105, 218), (52, 244), (106, 265), (188, 250)]
    arm = [(424, 370), (388, 440), (418, 458), (456, 388)]
    fill = (124, 86, 50)
    outline = (69, 50, 34)

    for shape in [tail, body, neck, head, arm]:
        draw.polygon(shape, fill=fill, outline=outline)
    draw.ellipse((96, 232, 108, 242), fill=(25, 22, 18))
    draw.line((66, 247, 174, 250), fill=(37, 30, 23), width=2)
    for tx in range(82, 168, 13):
        draw.line((tx, 250, tx + 5, 258), fill=(236, 226, 196), width=2)

    # Folded contour feathers, kept close to the torso rather than wing-like.
    for x in range(392, 612, 26):
        draw_plume(draw, [(x, 300), (x - 18, 358), (x + 10, 402)], (86, 60, 38), width=3)
    for x in range(506, 1070, 34):
        draw.line((x, 306, x + 26, 295), fill=(87, 62, 40), width=2)

    # Legs and correctly separated foot topology cues.
    draw.line((502, 412, 464, 550), fill=outline, width=24)
    draw.line((502, 412, 464, 550), fill=(119, 83, 50), width=16)
    draw_dromaeosaur_foot(draw, (454, 556), scale=1.05, mirror=False)

    draw.line((638, 408, 694, 548), fill=outline, width=24)
    draw.line((638, 408, 694, 548), fill=(119, 83, 50), width=16)
    draw_dromaeosaur_foot(draw, (700, 552), scale=1.02, mirror=False)

    # Red-orange topology strokes make this guide useful for ControlNet/QA, not final art.
    guide = (204, 72, 49)
    draw.arc((430, 452, 506, 572), 224, 338, fill=guide, width=5)
    draw.arc((676, 444, 746, 568), 220, 338, fill=guide, width=5)

    GUIDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(GUIDE_OUT)
    return image


def fit_image(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (237, 234, 226))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def crop_tile(image, box, label, size=(360, 260)):
    crop = image.crop(box)
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (size[0], size[1] + 42), (246, 244, 237))
    tile.paste(crop, ((size[0] - crop.width) // 2, 0))
    draw = ImageDraw.Draw(tile)
    draw.text((10, size[1] + 12), label[:54], fill=(42, 38, 34), font=ImageFont.load_default())
    return tile


def make_crops(guide):
    tiles = [
        crop_tile(guide, (390, 430, 570, 650), "new guide near foot: two walking toes + raised second toe"),
        crop_tile(guide, (638, 420, 820, 650), "new guide far foot: same topology, no floating crescent"),
        crop_tile(Image.open(CURRENT).convert("RGB"), (360, 520, 610, 710), "current v9 front foot"),
        crop_tile(Image.open(CURRENT).convert("RGB"), (610, 520, 850, 710), "current v9 rear foot"),
    ]
    sheet = Image.new("RGB", (720, 604), (226, 222, 212))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % 2) * 360, (idx // 2) * 302))
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
        sheet_card(CURRENT, "current v9 candidate", "keep first; full body still best compromise"),
        sheet_card(CURRENT_CROPS, "current v9 crop gate", "toe and sickle-claw evidence to compare"),
        sheet_card(GUIDE_OUT, "new foot topology guide", "ControlNet/LoRA target: attached raised second toe"),
        sheet_card(CROPS_OUT, "new guide vs v9 foot crops", "human QA close gate for toe topology"),
        sheet_card(FOOT_I2I_REJECTION, "v10 foot-only i2i rejection", "floating/oversized claw failure route"),
        sheet_card(PROMPT_REJECTION, "v11 prompt-only rejection", "identity drift when prompt alone is tightened"),
        sheet_card(OLD_GUIDE, "previous foot guide", "retained but bird-head/body cue is weaker"),
    ]
    cols = 3
    gap = 14
    header_h = 86
    card_w, card_h = 360, 318
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * card_w + (cols + 1) * gap, header_h + rows * (card_h + gap) + gap), (226, 222, 212))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, header_h), fill=(28, 62, 48))
    draw.text((22, 20), "Velociraptor foot topology review v18", fill=(248, 246, 238), font=ImageFont.load_default())
    draw.text(
        (22, 46),
        "Use the new guide as a structure target; it is not final paleoart or a promoted candidate.",
        fill=(216, 226, 214),
        font=ImageFont.load_default(),
    )
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    guide = draw_full_guide()
    make_crops(guide)
    make_review_sheet()
    print(GUIDE_OUT)
    print(CROPS_OUT)
    print(SHEET_OUT)


if __name__ == "__main__":
    main()
