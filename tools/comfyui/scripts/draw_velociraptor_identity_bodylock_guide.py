from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

GUIDE_OUT = ASSET_ROOT / "velociraptor-mongoliensis-identity-bodylock-guide-v1.png"
CROPS_OUT = ASSET_ROOT / "velociraptor-identity-bodylock-crops-v13.png"
SHEET_OUT = ASSET_ROOT / "velociraptor-review-options-v19.png"

CURRENT = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
FOOT_CROPS = ASSET_ROOT / "velociraptor-foot-topology-crops-v12.png"
BIRD_HEAD_RISK = ASSET_ROOT / "velociraptor-mongoliensis-birdhead-risk-comparison-v8.png"
PROMPT_REJECTION = ASSET_ROOT / "velociraptor-prompt-v11-rejection-crops.png"


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


def draw_feathers(draw, points, color, width=2):
    for p0, p1 in points:
        draw.line((p0, p1), fill=color, width=width)


def draw_toe(draw, base, mid, tip, fill, outline, width=9, claw=True):
    draw.line([base, mid, tip], fill=outline, width=width + 4, joint="curve")
    draw.line([base, mid, tip], fill=fill, width=width, joint="curve")
    if claw:
        claw_poly = [
            (tip[0] - 4, tip[1] - 6),
            (tip[0] + 22, tip[1] - 2),
            (tip[0] + 3, tip[1] + 8),
        ]
        draw.polygon(claw_poly, fill=(32, 29, 26), outline=outline)


def draw_sickle(draw, base, control, tip, fill, outline):
    draw.line([base, control, tip], fill=outline, width=18, joint="curve")
    draw.line([base, control, tip], fill=fill, width=12, joint="curve")
    draw.line([base, control, tip], fill=(224, 192, 132), width=2, joint="curve")


def draw_foot(draw, ankle, scale=1.0, mirror=False):
    sx = -1 if mirror else 1

    def p(dx, dy):
        return (int(ankle[0] + sx * dx * scale), int(ankle[1] + dy * scale))

    outline = (66, 48, 35)
    skin = (126, 88, 57)
    claw = (35, 31, 28)
    draw.line([p(0, -92), p(-6, -46), p(0, 0)], fill=outline, width=int(20 * scale))
    draw.line([p(0, -92), p(-6, -46), p(0, 0)], fill=skin, width=int(14 * scale))
    draw.ellipse([p(-13, -11), p(18, 17)], fill=skin, outline=outline, width=max(1, int(3 * scale)))
    draw_toe(draw, p(2, 7), p(50, 20), p(98, 14), skin, outline, width=max(5, int(8 * scale)))
    draw_toe(draw, p(-2, 8), p(42, 36), p(90, 42), skin, outline, width=max(5, int(8 * scale)))
    draw_sickle(draw, p(-4, -2), p(24, -60), p(6, -92), claw, outline)
    draw_toe(draw, p(-8, 8), p(-25, 20), p(-44, 18), skin, outline, width=max(4, int(6 * scale)), claw=False)


def draw_guide():
    image = Image.new("RGB", (1152, 768), (202, 224, 224))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 574, 1152, 768), fill=(204, 181, 132))
    for x in range(0, 1152, 36):
        y = 600 + (x * 17) % 90
        draw.line((x, y, x + 13, y - 24), fill=(133, 117, 83), width=2)

    outline = (62, 44, 31)
    body = (130, 83, 48)
    body_dark = (88, 58, 38)
    feather = (73, 49, 33)
    guide = (204, 72, 49)

    tail = [(730, 320), (1084, 248), (1114, 260), (756, 366)]
    body_poly = [(310, 320), (424, 246), (610, 240), (744, 292), (762, 366), (650, 426), (470, 426), (340, 376)]
    neck = [(330, 316), (252, 226), (182, 212), (176, 254), (292, 340)]
    head = [(176, 206), (96, 214), (42, 240), (96, 266), (190, 252)]
    jaw = [(50, 244), (96, 235), (188, 244), (180, 256), (94, 260)]
    for pts, fill in [(tail, body_dark), (body_poly, body), (neck, body_dark), (head, body), (jaw, (98, 66, 44))]:
        draw.polygon(pts, fill=fill, outline=outline)

    draw.ellipse((96, 232, 108, 244), fill=(20, 17, 13))
    draw.line((54, 246, 184, 252), fill=(26, 22, 18), width=2)
    for tx in range(74, 170, 12):
        draw.line((tx, 252, tx + 5, 260), fill=(236, 226, 194), width=2)
    draw.line((48, 238, 184, 246), fill=guide, width=4)
    draw.text((42, 272), "toothed snout, not beak", fill=(40, 36, 31), font=font)

    # Folded forelimb feather fan stays tucked to the ribs, not spread as wings.
    arm = [(418, 368), (386, 448), (416, 468), (462, 388)]
    draw.polygon(arm, fill=(110, 70, 43), outline=outline)
    for idx, x in enumerate(range(390, 462, 12)):
        draw.line((x, 378, x - 26, 456 + idx * 3), fill=feather, width=4)
        draw.line((x + 3, 380, x - 8, 458 + idx * 3), fill=(168, 120, 70), width=2)
    draw.arc((354, 354, 480, 488), 95, 245, fill=guide, width=4)

    # Body feathers: dense but kept as body plumage, not scaly stripes.
    for x in range(330, 735, 24):
        draw.line((x, 306 + (x % 3) * 6, x + 18, 286 + (x % 5) * 4), fill=feather, width=2)
    for x in range(455, 1055, 32):
        draw.line((x, 330, x + 28, 318), fill=feather, width=2)
    for x in range(340, 650, 24):
        draw.arc((x, 332, x + 42, 402), 110, 195, fill=(162, 113, 68), width=2)

    # Legs and attached raised second-toe sickle claws.
    draw.line((506, 412, 462, 550), fill=outline, width=24)
    draw.line((506, 412, 462, 550), fill=(120, 82, 50), width=16)
    draw_foot(draw, (452, 558), scale=1.05)
    draw.line((636, 410, 698, 548), fill=outline, width=24)
    draw.line((636, 410, 698, 548), fill=(120, 82, 50), width=16)
    draw_foot(draw, (702, 554), scale=1.02)
    draw.arc((426, 452, 504, 574), 224, 338, fill=guide, width=5)
    draw.arc((676, 444, 748, 568), 220, 338, fill=guide, width=5)

    draw.line((744, 342, 1096, 254), fill=guide, width=4)
    draw.text((28, 32), "structure guide: toothed non-beak snout, folded feathered arms, stiff tail, attached sickle toes", fill=(38, 35, 31), font=font)
    draw.text((28, 54), "use as ControlNet/QA guide only; not final paleoart", fill=(38, 35, 31), font=font)

    GUIDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(GUIDE_OUT)
    return image


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
        crop_tile(guide, (34, 188, 210, 280), "guide head: narrow toothed snout, no bird beak"),
        crop_tile(current, (0, 190, 430, 390), "current v9 toothed non-beak snout"),
        crop_tile(guide, (340, 330, 500, 500), "guide folded feathered arm, not spread wing"),
        crop_tile(current, (355, 410, 560, 610), "current v9 folded hand/forelimb crop"),
        crop_tile(guide, (720, 240, 1125, 375), "guide long stiff balancing tail"),
        crop_tile(current, (640, 315, 1680, 535), "current v9 tail/body balance"),
        crop_tile(guide, (400, 445, 780, 660), "guide feet: attached raised second-toe claws"),
        crop_tile(current, (520, 615, 860, 830), "current v9 front/rear foot crop"),
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
        sheet_card(CURRENT, "current v9 candidate", "keep first; best current identity/foot compromise"),
        sheet_card(CURRENT_CROPS, "current v9 crop gate", "head, hands, feet, and tail close review"),
        sheet_card(GUIDE_OUT, "new identity body-lock guide", "ControlNet/QA target: head, plumage, feet, tail"),
        sheet_card(CROPS_OUT, "new guide vs v9 crop gate", "compare snout, folded arms, tail, and sickle toes"),
        sheet_card(FOOT_GUIDE, "previous foot topology guide", "kept for focused foot-only structure control"),
        sheet_card(FOOT_CROPS, "previous foot topology crops", "attached raised second toe comparison"),
        sheet_card(BIRD_HEAD_RISK, "bird-head risk comparison", "explicit rejection for modern-bird drift"),
        sheet_card(PROMPT_REJECTION, "v11 prompt-only rejection", "identity drift when prompt alone is tightened"),
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
    draw.text((22, 20), "Velociraptor identity body-lock review v19", fill=(248, 246, 238), font=font)
    draw.text((22, 46), "Use the guide to lock dromaeosaur identity before texture or foot polish.", fill=(216, 226, 214), font=font)
    for idx, card in enumerate(cards):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        sheet.paste(card, (x, y))
    sheet.save(SHEET_OUT)


def main():
    for path in (CURRENT, CURRENT_CROPS, FOOT_GUIDE, FOOT_CROPS, BIRD_HEAD_RISK, PROMPT_REJECTION):
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
