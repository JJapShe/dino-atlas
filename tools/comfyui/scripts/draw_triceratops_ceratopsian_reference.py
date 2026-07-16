import argparse
import math
import random
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
COMFY_GUIDE_ROOT = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

WIDTH = 1152
HEIGHT = 768


def sc(points, scale):
    return [(int(round(x * scale)), int(round(y * scale))) for x, y in points]


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def add_noise(layer, mask, colors, seed, scale):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    bbox = mask.getbbox()
    if not bbox:
        return layer
    pixels = mask.load()
    x0, y0, x1, y1 = bbox
    for _ in range(5800):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if pixels[x, y] < 10:
            continue
        color = rng.choice(colors)
        if rng.random() < 0.22:
            radius = rng.uniform(0.55 * scale, 1.6 * scale)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, rng.randrange(9, 28)))
        else:
            draw.point((x, y), fill=(*color, rng.randrange(8, 30)))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_background(draw, scale):
    horizon = int(600 * scale)
    sky_top = (205, 223, 222)
    sky_low = (176, 205, 198)
    ground_top = (210, 198, 164)
    ground_low = (158, 142, 108)
    for y in range(HEIGHT * scale):
        if y < horizon:
            color = mix(sky_top, sky_low, y / horizon)
        else:
            color = mix(ground_top, ground_low, (y - horizon) / max(1, HEIGHT * scale - horizon))
        draw.line((0, y, WIDTH * scale, y), fill=color)
    draw.line((0, horizon, WIDTH * scale, horizon), fill=(145, 132, 96), width=max(2, scale))


def draw_horn(draw, mask_draw, points, fill, outline, scale):
    pts = sc(points, scale)
    draw.polygon(pts, fill=fill)
    draw.line(pts + [pts[0]], fill=outline, width=max(3, int(2.2 * scale)), joint="curve")
    mask_draw.polygon(pts, fill=255)
    base_mid = ((pts[0][0] + pts[1][0]) // 2, (pts[0][1] + pts[1][1]) // 2)
    tip = pts[2]
    draw.line((base_mid, tip), fill=(246, 229, 175, 140), width=max(1, scale))


def draw_toes(draw, mask_draw, base_x, base_y, flip, scale, outline):
    toe_fill = (165, 138, 94, 255)
    for idx in range(3):
        dx = (idx - 1) * 17
        pts = [
            (base_x + flip * (dx - 11), base_y),
            (base_x + flip * (dx + 16), base_y + 4),
            (base_x + flip * (dx + 34), base_y + 17),
            (base_x + flip * (dx + 2), base_y + 20),
        ]
        spts = sc(pts, scale)
        draw.polygon(spts, fill=toe_fill)
        draw.line(spts + [spts[0]], fill=outline, width=max(2, int(1.7 * scale)))
        mask_draw.polygon(spts, fill=255)


def draw_triceratops(scale=3, seed=2026064401):
    rng = random.Random(seed)
    image = Image.new("RGBA", (WIDTH * scale, HEIGHT * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    body_mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(body_mask)
    draw_background(draw, scale)

    outline = (36, 30, 24, 255)
    body = (118, 96, 68, 255)
    body_dark = (79, 62, 43, 255)
    body_light = (164, 134, 88, 255)
    frill = (126, 105, 74, 255)
    horn = (230, 207, 150, 255)

    # Tail and body: long dinosaur tail, low quadrupedal ceratopsian trunk,
    # no rhinoceros shoulder hump.
    tail = sc([(766, 432), (1036, 354), (1115, 370), (816, 492)], scale)
    body_poly = sc(
        [
            (340, 394),
            (448, 346),
            (620, 324),
            (764, 348),
            (842, 405),
            (838, 504),
            (720, 565),
            (522, 572),
            (384, 536),
            (304, 474),
        ],
        scale,
    )
    hip = sc([(736, 384), (812, 394), (846, 468), (804, 536), (724, 520), (692, 446)], scale)
    chest = sc([(316, 386), (404, 372), (444, 440), (412, 518), (326, 514), (282, 454)], scale)
    neck = sc([(318, 394), (218, 384), (198, 430), (308, 464)], scale)

    for pts, fill in ((tail, body_dark), (body_poly, body), (hip, (101, 82, 58, 255)), (chest, body_dark), (neck, body_dark)):
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=outline, width=max(5, int(3.5 * scale)), joint="curve")
        mask_draw.polygon(pts, fill=255)

    # Skull-attached frill: large shield behind the head, separated from the
    # shoulder so it cannot read as a back sail.
    frill_pts = sc(
        [
            (212, 284),
            (270, 256),
            (346, 268),
            (405, 324),
            (418, 414),
            (374, 492),
            (292, 512),
            (226, 476),
            (186, 410),
            (176, 334),
        ],
        scale,
    )
    draw.polygon(frill_pts, fill=frill)
    draw.line(frill_pts + [frill_pts[0]], fill=outline, width=max(6, int(4.2 * scale)), joint="curve")
    mask_draw.polygon(frill_pts, fill=255)
    draw.arc((186 * scale, 294 * scale, 400 * scale, 500 * scale), 106, 262, fill=(190, 163, 108, 140), width=max(3, int(1.6 * scale)))
    for i, (x, y) in enumerate([(232, 314), (274, 294), (322, 300), (362, 336), (386, 386), (376, 444), (330, 482), (270, 486), (220, 444), (198, 384)]):
        r = (6 + (i % 2)) * scale
        draw.ellipse((x * scale - r, y * scale - r, x * scale + r, y * scale + r), fill=(58, 47, 34, 230))

    head = sc([(54, 412), (98, 374), (184, 366), (252, 398), (238, 446), (164, 470), (74, 456)], scale)
    beak = sc([(34, 424), (66, 404), (78, 428), (58, 452)], scale)
    cheek = sc([(186, 396), (254, 400), (246, 452), (184, 468), (152, 430)], scale)
    for pts, fill in ((head, (115, 89, 58, 255)), (cheek, (91, 70, 48, 255)), (beak, (73, 57, 42, 255))):
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=outline, width=max(4, int(3 * scale)), joint="curve")
        mask_draw.polygon(pts, fill=255)
    draw.ellipse((114 * scale, 398 * scale, 129 * scale, 413 * scale), fill=(18, 15, 12, 255))
    draw.arc((62 * scale, 424 * scale, 148 * scale, 466 * scale), 188, 350, fill=(27, 22, 18, 230), width=max(2, scale))

    # Two brow horns plus one short nasal horn.
    draw_horn(draw, mask_draw, [(150, 368), (184, 382), (130, 244)], horn, outline, scale)
    draw_horn(draw, mask_draw, [(190, 380), (222, 398), (244, 254)], horn, outline, scale)
    draw_horn(draw, mask_draw, [(58, 400), (82, 408), (39, 352)], horn, outline, scale)

    legs = [
        (330, 488, 386, 652, 0),
        (456, 500, 502, 660, 10),
        (650, 498, 706, 662, -6),
        (792, 476, 844, 652, -12),
    ]
    for x0, y0, x1, y1, lean in legs:
        pts = sc([(x0, y0), (x1, y0 + lean), (x1 - 12, y1), (x0 - 28, y1 - 8)], scale)
        draw.polygon(pts, fill=body_dark if x0 in (330, 650) else (132, 101, 68, 255))
        draw.line(pts + [pts[0]], fill=outline, width=max(4, int(2.8 * scale)), joint="curve")
        mask_draw.polygon(pts, fill=255)
        foot_dir = -1 if x0 < 560 else 1
        foot = sc([(x0 - 40, y1 - 8), (x1 + 22, y1 - 4), (x1 + 48, y1 + 20), (x0 - 36, y1 + 20)], scale)
        draw.polygon(foot, fill=(86, 66, 45, 255))
        draw.line(foot + [foot[0]], fill=outline, width=max(3, int(2.2 * scale)))
        mask_draw.polygon(foot, fill=255)
        draw_toes(draw, mask_draw, x1 + (12 if foot_dir > 0 else -18), y1 + 8, foot_dir, scale, outline)

    # Belly and shoulder guide lines.
    draw.arc((318 * scale, 362 * scale, 850 * scale, 596 * scale), 190, 350, fill=(190, 157, 103, 120), width=max(3, int(1.5 * scale)))
    draw.arc((336 * scale, 418 * scale, 832 * scale, 626 * scale), 10, 172, fill=(44, 35, 26, 150), width=max(3, int(1.5 * scale)))
    for x in (446, 628, 758):
        draw.arc((x * scale, 404 * scale, (x + 92) * scale, 566 * scale), 102, 250, fill=(56, 44, 32, 95), width=max(2, scale))

    image = add_noise(
        image,
        body_mask.filter(ImageFilter.GaussianBlur(radius=0.35 * scale)),
        [(75, 58, 40), (142, 111, 72), (176, 143, 94), (98, 76, 52)],
        seed,
        scale,
    )
    return image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGB")


def make_contact_sheet(items, output):
    thumb_w, thumb_h, label_h = 384, 256, 42
    tiles = []
    font = ImageFont.load_default()
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 11), label[:58], fill=(38, 35, 31), font=font)
        tiles.append(tile)
    cols = min(2, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=2026064401)
    args = parser.parse_args()

    asset = ASSET_ROOT / "triceratops-horridus-ceratopsian-reference-guide-v1.png"
    comfy = COMFY_GUIDE_ROOT / "triceratops-horridus_ceratopsian_reference_v1.png"
    review_sheet = OUTPUT_ROOT / "trike_ceratopsian_reference_guide_v1-contact-sheet.png"

    image = draw_triceratops(seed=args.seed)
    asset.parent.mkdir(parents=True, exist_ok=True)
    image.save(asset)
    comfy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(asset, comfy)
    make_contact_sheet(
        [
            (asset, "new skull-frill/body reference guide"),
            (ASSET_ROOT / "triceratops-horridus-microhorn-inpaint-v1.png", "current primary for comparison"),
            (Path("tools/comfyui/ComfyUI/input/dino_guides/triceratops-horridus_shape_v3.png"), "previous v3 structure guide"),
            (ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png", "rhino-drift rejection"),
        ],
        review_sheet,
    )
    print(asset)
    print(comfy)
    print(review_sheet)


if __name__ == "__main__":
    main()
