import argparse
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
                int(193 * (1 - local) + 159 * local),
                int(216 * (1 - local) + 195 * local),
                int(218 * (1 - local) + 178 * local),
            )
        else:
            local = (t - 0.62) / 0.38
            color = (
                int(185 * (1 - local) + 147 * local),
                int(170 * (1 - local) + 132 * local),
                int(126 * (1 - local) + 94 * local),
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
        alpha = rng.randrange(8, 34)
        r = rng.choice([1, 1, 2, 3]) * scale / 4
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_hand(draw, wrist, angle, scale, color, outline):
    wx, wy = wrist
    fingers = [
        (angle - 0.55, 34, 9),
        (angle - 0.12, 42, 10),
        (angle + 0.34, 30, 8),
    ]
    for a, length, claw in fingers:
        ex = wx + length * scale * __import__("math").cos(a)
        ey = wy + length * scale * __import__("math").sin(a)
        draw.line((wx, wy, ex, ey), fill=outline, width=max(3, int(1.8 * scale)))
        draw.line((wx, wy, ex, ey), fill=color, width=max(2, int(1.0 * scale)))
        cx = ex + claw * scale * __import__("math").cos(a - 0.2)
        cy = ey + claw * scale * __import__("math").sin(a - 0.2)
        draw.line((ex, ey, cx, cy), fill=(35, 25, 18, 255), width=max(2, int(1.0 * scale)))


def make_guide(output):
    width, height = 1152, 768
    scale = 4
    image = Image.new("RGB", (width * scale, height * scale))
    draw = ImageDraw.Draw(image)
    draw_background(draw, width, height, scale)
    rng = random.Random(2026062361)

    # Low Triassic dry-ground vegetation and stones, kept behind the animal.
    for _ in range(160):
        x = rng.randrange(0, width * scale)
        y = rng.randrange(int(height * 0.72 * scale), height * scale)
        tone = rng.choice([(78, 101, 70), (108, 117, 70), (134, 119, 77), (91, 80, 58)])
        draw.line((x, y, x + rng.randrange(-18, 18), y - rng.randrange(8, 34)), fill=tone, width=rng.randrange(1, 3))

    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = Image.new("L", image.size, 0)
    d = ImageDraw.Draw(layer)
    md = ImageDraw.Draw(mask)

    body = sc(
        [
            (412, 423),
            (474, 380),
            (606, 354),
            (734, 376),
            (798, 430),
            (766, 494),
            (628, 520),
            (494, 500),
        ],
        scale,
    )
    neck = sc([(748, 392), (835, 292), (875, 306), (798, 430)], scale)
    head = sc([(858, 275), (990, 246), (1075, 278), (1090, 312), (1010, 340), (875, 326)], scale)
    tail = sc([(424, 438), (190, 408), (42, 376), (182, 440), (414, 480)], scale)

    fill = (142, 92, 42, 255)
    light = (194, 146, 82, 255)
    cream = (220, 198, 142, 255)
    dark = (62, 42, 27, 255)
    outline = (48, 34, 24, 255)

    for shape in (tail, neck, body, head):
        d.polygon(shape, fill=fill)
        d.line(shape + [shape[0]], fill=outline, width=5 * scale)
        md.polygon(shape, fill=255)

    d.line(sc([(446, 457), (548, 488), (692, 492), (760, 456)], scale), fill=cream, width=14 * scale, joint="curve")
    d.line(sc([(805, 368), (868, 312), (980, 292), (1060, 294)], scale), fill=cream, width=10 * scale, joint="curve")
    d.ellipse((994 * scale, 274 * scale, 1014 * scale, 294 * scale), fill=(28, 24, 20, 255))

    # Hind legs are long and dominant; two separate feet are visible.
    hind_legs = [
        [(585, 493), (638, 502), (608, 655), (555, 663), (548, 628), (580, 585)],
        [(704, 476), (752, 488), (812, 628), (938, 640), (930, 674), (770, 672), (720, 610)],
    ]
    for pts in hind_legs:
        sp = sc(pts, scale)
        d.polygon(sp, fill=(103, 69, 39, 255))
        d.line(sp + [sp[0]], fill=outline, width=5 * scale)
        md.polygon(sp, fill=255)

    # Two small grasping forelimbs below the chest, not weight-bearing.
    forelimbs = [
        [(508, 454), (486, 505), (456, 552), (438, 548), (458, 492), (482, 438)],
        [(550, 458), (530, 516), (514, 568), (496, 566), (506, 512), (528, 450)],
    ]
    for idx, pts in enumerate(forelimbs):
        sp = sc(pts, scale)
        color = (107, 70, 39, 255) if idx == 0 else (124, 78, 41, 255)
        d.polygon(sp, fill=color)
        d.line(sp + [sp[0]], fill=outline, width=4 * scale)
        md.polygon(sp, fill=255)
    draw_hand(d, (438 * scale, 548 * scale), 2.42, scale, (134, 88, 48, 255), outline)
    draw_hand(d, (496 * scale, 566 * scale), 2.70, scale, (145, 96, 52, 255), outline)

    # Toes on hind feet.
    for x, y, direction in [(555, 662, -1), (825, 640, 1), (875, 645, 1)]:
        for offset in (-18, 0, 18):
            d.line(
                (
                    x * scale,
                    y * scale,
                    (x + direction * (44 + abs(offset) * 0.3)) * scale,
                    (y + offset * 0.30) * scale,
                ),
                fill=outline,
                width=3 * scale,
            )

    layer = draw_texture(layer, mask, 2026062362, [(86, 54, 30), (156, 102, 48), (206, 158, 88), (231, 208, 148)], 2200, scale)
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
        default=str(GUIDE_DIR / "coelophysis-bauri_forelimb_reference_v1.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "coelophysis-bauri-forelimb-reference-guide-v1.png"),
    )
    parser.add_argument("--sheet-output", default=str(ASSET_DIR / "coelophysis-forelimb-reference-sheet-v1.png"))
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
