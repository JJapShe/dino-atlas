import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
ASSET_DIR = ROOT / "assets" / "dinosaurs"


def sc(points, scale):
    return [(x * scale, y * scale) for x, y in points]


def draw_background(draw, width, height, scale):
    for y in range(height * scale):
        t = y / (height * scale - 1)
        if t < 0.62:
            local = t / 0.62
            color = (
                int(194 * (1 - local) + 166 * local),
                int(218 * (1 - local) + 198 * local),
                int(218 * (1 - local) + 181 * local),
            )
        else:
            local = (t - 0.62) / 0.38
            color = (
                int(184 * (1 - local) + 145 * local),
                int(173 * (1 - local) + 133 * local),
                int(128 * (1 - local) + 92 * local),
            )
        draw.line((0, y, width * scale, y), fill=color)


def draw_texture(layer, mask, seed, tones, count, scale):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    bbox = mask.getbbox()
    if not bbox:
        return layer
    x0, y0, x1, y1 = bbox
    mask_pix = mask.load()
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if mask_pix[x, y] < 24:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(6, 28)
        radius = rng.choice([1, 1, 2, 3]) * scale / 4
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_hand(draw, wrist, angle, scale, skin, claw, outline):
    wx, wy = wrist
    palm = [
        (wx - 9 * scale, wy - 5 * scale),
        (wx + 10 * scale, wy - 8 * scale),
        (wx + 18 * scale, wy + 4 * scale),
        (wx + 4 * scale, wy + 13 * scale),
        (wx - 10 * scale, wy + 8 * scale),
    ]
    draw.polygon(palm, fill=skin, outline=outline)
    digits = [
        (angle - 0.60, 34, 15, 2.4),
        (angle - 0.20, 25, 8, 1.7),
        (angle + 0.16, 21, 6, 1.5),
        (angle + 0.48, 18, 5, 1.3),
    ]
    for idx, (digit_angle, length, claw_len, width) in enumerate(digits):
        ex = wx + length * scale * math.cos(digit_angle)
        ey = wy + length * scale * math.sin(digit_angle)
        draw.line((wx, wy, ex, ey), fill=outline, width=max(2, int((width + 1.0) * scale)))
        draw.line((wx, wy, ex, ey), fill=skin, width=max(1, int(width * scale)))
        cx = ex + claw_len * scale * math.cos(digit_angle - 0.20)
        cy = ey + claw_len * scale * math.sin(digit_angle - 0.20)
        draw.line(
            (ex, ey, cx, cy),
            fill=claw if idx == 0 else outline,
            width=max(2, int((1.7 if idx == 0 else 0.9) * scale)),
        )


def make_guide(output):
    width, height = 1152, 768
    scale = 4
    image = Image.new("RGB", (width * scale, height * scale))
    draw = ImageDraw.Draw(image)
    draw_background(draw, width, height, scale)
    rng = random.Random(2026062244)

    for _ in range(180):
        x = rng.randrange(0, width * scale)
        y = rng.randrange(int(height * 0.73 * scale), height * scale)
        tone = rng.choice([(74, 98, 68), (112, 121, 76), (143, 125, 78), (84, 72, 52)])
        draw.line((x, y, x + rng.randrange(-18, 18), y - rng.randrange(8, 34)), fill=tone, width=rng.randrange(1, 3))

    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = Image.new("L", image.size, 0)
    d = ImageDraw.Draw(layer)
    md = ImageDraw.Draw(mask)

    fill = (119, 82, 47, 255)
    fill_dark = (82, 57, 37, 255)
    belly = (182, 137, 78, 255)
    outline = (47, 34, 24, 255)
    claw = (224, 205, 143, 255)

    tail = sc([(720, 450), (1035, 414), (1120, 436), (1020, 464), (735, 496)], scale)
    body = sc(
        [
            (340, 420),
            (405, 374),
            (560, 350),
            (720, 374),
            (790, 430),
            (766, 494),
            (620, 524),
            (460, 506),
        ],
        scale,
    )
    neck = sc([(394, 416), (312, 374), (226, 354), (166, 356), (190, 386), (294, 396), (374, 444)], scale)
    head = sc([(88, 332), (184, 326), (236, 350), (220, 374), (132, 378), (52, 360)], scale)

    for shape in (tail, body, neck, head):
        d.polygon(shape, fill=fill)
        d.line(shape + [shape[0]], fill=outline, width=5 * scale)
        md.polygon(shape, fill=255)

    d.line(sc([(422, 456), (540, 494), (698, 498), (768, 462)], scale), fill=belly, width=14 * scale, joint="curve")
    d.line(sc([(78, 360), (136, 356), (206, 358), (224, 360)], scale), fill=belly, width=7 * scale, joint="curve")
    d.ellipse((132 * scale, 342 * scale, 146 * scale, 356 * scale), fill=(26, 22, 19, 255))
    d.line((68 * scale, 364 * scale, 220 * scale, 365 * scale), fill=outline, width=3 * scale)

    hind_legs = [
        [(555, 492), (610, 508), (582, 650), (518, 660), (510, 626), (548, 578)],
        [(690, 482), (742, 494), (806, 628), (932, 638), (922, 673), (768, 670), (720, 608)],
    ]
    for pts in hind_legs:
        sp = sc(pts, scale)
        d.polygon(sp, fill=fill_dark)
        d.line(sp + [sp[0]], fill=outline, width=5 * scale)
        md.polygon(sp, fill=255)

    # Short lifted forelimbs: smaller than the hind legs and deliberately above the ground.
    forelimbs = [
        [(420, 448), (396, 486), (365, 520), (348, 514), (365, 474), (394, 438)],
        [(468, 454), (444, 494), (414, 532), (396, 528), (414, 486), (444, 446)],
    ]
    wrists = [(348 * scale, 514 * scale, 2.58), (396 * scale, 528 * scale, 2.78)]
    for idx, pts in enumerate(forelimbs):
        sp = sc(pts, scale)
        color = (91, 62, 39, 255) if idx == 0 else (105, 69, 39, 255)
        d.polygon(sp, fill=color)
        d.line(sp + [sp[0]], fill=outline, width=4 * scale)
        md.polygon(sp, fill=255)
    for wx, wy, angle in wrists:
        draw_hand(d, (wx, wy), angle, scale, (126, 84, 47, 255), claw, outline)

    # Hind toes stay broad and grounded; hands remain lifted for a bipedal read.
    for x, y, direction in [(518, 660, -1), (820, 638, 1), (874, 642, 1)]:
        for offset in (-18, 0, 18):
            d.line(
                (
                    x * scale,
                    y * scale,
                    (x + direction * (44 + abs(offset) * 0.3)) * scale,
                    (y + offset * 0.28) * scale,
                ),
                fill=outline,
                width=3 * scale,
            )

    layer = draw_texture(
        layer,
        mask,
        2026062245,
        [(75, 50, 31), (132, 86, 42), (190, 141, 78), (220, 196, 137)],
        2400,
        scale,
    )
    image = Image.alpha_composite(image.convert("RGBA"), layer)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.14 * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def make_contact_sheet(paths, output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    tiles = []
    for path, label in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)
    sheet = Image.new("RGB", (len(tiles) * thumb_w, thumb_h + label_h), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--guide-output",
        default=str(GUIDE_DIR / "plateosaurus-engelhardti_forelimb_reference_v1.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "plateosaurus-engelhardti-forelimb-reference-guide-v1.png"),
    )
    parser.add_argument("--sheet-output", default=str(ASSET_DIR / "plateosaurus-forelimb-reference-sheet-v1.png"))
    args = parser.parse_args()

    guide_output = Path(args.guide_output).resolve()
    asset_output = Path(args.asset_output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    make_guide(guide_output)
    asset_output.parent.mkdir(parents=True, exist_ok=True)
    Image.open(guide_output).save(asset_output)
    make_contact_sheet([(asset_output, "forelimb reference guide")], sheet_output)
    print(guide_output)
    print(asset_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
