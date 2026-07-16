import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
ASSET_DIR = ROOT / "assets" / "dinosaurs"


def sc(points, scale):
    return [(int(round(x * scale)), int(round(y * scale))) for x, y in points]


def plate_points(cx, base_y, width, height, lean, asymmetry):
    """Broad slab-like Stegosaurus plate, avoiding leaf or sail silhouettes."""
    top_x = cx + lean + asymmetry * width * 0.05
    return [
        (cx - width * 0.58, base_y + height * 0.025),
        (cx - width * 0.66, base_y - height * 0.12),
        (cx + lean * 0.12 - width * 0.55, base_y - height * 0.42),
        (top_x - width * 0.30, base_y - height * 0.82),
        (top_x - width * 0.10, base_y - height * 0.98),
        (top_x + width * 0.10, base_y - height),
        (top_x + width * 0.31, base_y - height * 0.82),
        (cx + lean * 0.12 + width * 0.55, base_y - height * 0.42),
        (cx + width * 0.66, base_y - height * 0.12),
        (cx + width * 0.58, base_y + height * 0.025),
    ]


def draw_gradient_background(draw, width, height, scale):
    for y in range(height * scale):
        t = y / (height * scale - 1)
        if t < 0.62:
            local = t / 0.62
            color = (
                int(188 * (1 - local) + 155 * local),
                int(211 * (1 - local) + 195 * local),
                int(209 * (1 - local) + 184 * local),
            )
        else:
            local = (t - 0.62) / 0.38
            color = (
                int(179 * (1 - local) + 127 * local),
                int(169 * (1 - local) + 120 * local),
                int(124 * (1 - local) + 85 * local),
            )
        draw.line((0, y, width * scale, y), fill=color)


def texture_into(layer, mask, seed, tones, count, scale, alpha_range=(8, 30)):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    bbox = mask.getbbox()
    if not bbox:
        return layer
    x0, y0, x1, y1 = bbox
    pixels = mask.load()
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if pixels[x, y] < 20:
            continue
        radius = rng.choice([1, 1, 2, 2, 3]) * scale / 3
        tone = rng.choice(tones)
        alpha = rng.randrange(alpha_range[0], alpha_range[1])
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def shadow_under(base, points, scale, opacity=80, blur=14):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.polygon(sc(points, scale), fill=(20, 15, 10, opacity))
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=blur * scale)))


def draw_body(base, scale):
    body = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(body)
    mask = Image.new("L", base.size, 0)
    mask_draw = ImageDraw.Draw(mask)

    outline = (38, 30, 23, 255)
    body_fill = (96, 78, 54, 255)
    body_side = (69, 55, 39, 255)

    base = shadow_under(base, [(170, 550), (844, 530), (924, 565), (770, 606), (238, 604)], scale, 80, 12)

    tail = [(792, 402), (1080, 338), (1114, 365), (824, 470)]
    neck = [(248, 394), (158, 370), (136, 418), (256, 456)]
    head = [(132, 365), (74, 371), (40, 402), (58, 438), (116, 458), (166, 441), (174, 394)]
    body_poly = [
        (220, 444),
        (256, 365),
        (350, 322),
        (478, 302),
        (626, 308),
        (760, 348),
        (840, 416),
        (808, 496),
        (682, 540),
        (502, 550),
        (348, 526),
        (248, 482),
    ]

    for pts, fill in [
        (tail, (78, 62, 44, 255)),
        (neck, (79, 63, 44, 255)),
        (head, (96, 78, 55, 255)),
        (body_poly, body_fill),
    ]:
        spts = sc(pts, scale)
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=outline, width=max(3, 4 * scale), joint="curve")
        mask_draw.polygon(spts, fill=255)

    # Low belly and shoulder shading: keeps the guide natural enough for IP-Adapter.
    draw.arc((284 * scale, 306 * scale, 802 * scale, 566 * scale), 190, 350, fill=(135, 112, 78, 80), width=4 * scale)
    draw.arc((304 * scale, 366 * scale, 780 * scale, 608 * scale), 10, 176, fill=(44, 34, 25, 92), width=4 * scale)
    draw.ellipse((100 * scale, 398 * scale, 114 * scale, 412 * scale), fill=(22, 18, 14, 255))

    legs = [
        [(296, 494), (356, 506), (340, 646), (282, 646), (270, 672), (358, 672)],
        [(444, 518), (504, 512), (496, 650), (434, 650), (420, 674), (514, 674)],
        [(650, 500), (708, 492), (716, 648), (654, 648), (640, 672), (730, 672)],
        [(766, 472), (818, 468), (834, 646), (776, 646), (762, 672), (852, 672)],
    ]
    for idx, pts in enumerate(legs):
        fill = body_side if idx in (0, 2) else (77, 58, 39, 255)
        spts = sc(pts, scale)
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=(37, 28, 20, 210), width=max(2, 3 * scale), joint="curve")
        mask_draw.polygon(spts, fill=255)

    spikes = [
        [(1062, 354), (1126, 330), (1083, 384)],
        [(1076, 376), (1136, 386), (1078, 410)],
        [(1052, 374), (1090, 324), (1078, 388)],
        [(1054, 394), (1104, 446), (1072, 406)],
    ]
    for pts in spikes:
        spts = sc(pts, scale)
        draw.polygon(spts, fill=(126, 88, 52, 255))
        draw.line(spts + [spts[0]], fill=outline, width=max(2, 3 * scale), joint="curve")

    body = texture_into(
        body,
        mask,
        2026062211,
        [(52, 42, 31), (118, 96, 65), (78, 63, 45), (148, 126, 88)],
        5000,
        scale,
        (7, 24),
    )
    return Image.alpha_composite(base, body)


def draw_plate_rows(base, scale):
    rng = random.Random(2026062212)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    far_specs = [
        (286, 404, 34, 54, -4),
        (348, 368, 44, 82, -4),
        (420, 338, 54, 114, -2),
        (500, 320, 64, 148, -1),
        (590, 318, 66, 156, 1),
        (680, 342, 56, 118, 3),
        (760, 386, 42, 76, 4),
        (824, 426, 28, 46, 5),
    ]
    near_specs = [
        (246, 432, 28, 40, -5),
        (314, 392, 42, 72, -4),
        (386, 356, 56, 106, -2),
        (466, 326, 68, 142, -1),
        (552, 306, 78, 174, 0),
        (642, 314, 74, 162, 2),
        (728, 350, 62, 120, 3),
        (800, 398, 46, 78, 4),
    ]

    def draw_one(spec, far):
        cx, by, pw, ph, lean = spec
        points = plate_points(cx, by, pw, ph, lean, rng.uniform(-0.32, 0.32))
        pts = sc(points, scale)
        fill = (96, 73, 53, 218) if far else (132, 91, 57, 246)
        edge = (36, 28, 22, 210 if far else 255)
        highlight = (196, 151, 94, 52 if far else 78)
        shadow = (42, 29, 22, 74 if far else 106)
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=edge, width=max(3, int((4.0 if far else 5.6) * scale)), joint="curve")
        draw.line(pts[2:8], fill=highlight, width=max(1, int(1.2 * scale)), joint="curve")
        draw.line([pts[1], pts[2], pts[3]], fill=shadow, width=max(1, int(1.1 * scale)), joint="curve")
        mask_draw.polygon(pts, fill=255)

        # Heavy embedded socket at the skin line, so the plate reads as bone fixed in the back.
        socket = [
            (cx - pw * 0.52, by + ph * 0.02),
            (cx + pw * 0.52, by + ph * 0.02),
        ]
        draw.line(sc(socket, scale), fill=(24, 18, 14, 180 if far else 224), width=max(3, int(4.4 * scale)))

        for _ in range(12 if far else 18):
            px = rng.uniform((cx - pw * 0.34) * scale, (cx + pw * 0.34) * scale)
            py = rng.uniform((by - ph * 0.78) * scale, (by - ph * 0.18) * scale)
            rr = rng.uniform(0.75, 2.4) * scale
            tone = rng.choice([(66, 48, 35), (169, 126, 76), (92, 65, 42), (44, 33, 26)])
            draw.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(*tone, rng.randrange(14, 40)))

    for spec in far_specs:
        draw_one(spec, True)
    for spec in near_specs:
        draw_one(spec, False)

    layer = texture_into(
        layer,
        mask,
        2026062213,
        [(74, 53, 38), (145, 99, 61), (179, 132, 82), (54, 40, 31)],
        1900,
        scale,
        (6, 26),
    )
    layer.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.08 * scale)))
    return Image.alpha_composite(base, layer)


def make_guide(output):
    width, height = 1152, 768
    scale = 4
    base = Image.new("RGB", (width * scale, height * scale))
    draw = ImageDraw.Draw(base)
    draw_gradient_background(draw, width, height, scale)

    rng = random.Random(2026062214)
    for _ in range(360):
        x = rng.randrange(0, width * scale)
        y = rng.randrange(int(height * 0.69 * scale), height * scale)
        tone = rng.choice([(110, 98, 70), (86, 77, 58), (148, 135, 96), (72, 90, 62)])
        draw.line((x, y, x + rng.randrange(-18, 19), y - rng.randrange(6, 32)), fill=tone, width=rng.randrange(1, 4))

    image = base.convert("RGBA")
    # Far row goes down before the body; near row is drawn after the body.
    image = draw_plate_rows(image, scale)
    image = draw_body(image, scale)
    image = draw_plate_rows(image, scale)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.08 * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    image = ImageOps.autocontrast(image, cutoff=0.3)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def make_contact_sheet(items, output, thumb_w=384, thumb_h=256):
    label_h = 42
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)
    cols = min(3, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def crop_plate_band(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    return image.crop((int(w * 0.14), int(h * 0.07), int(w * 0.84), int(h * 0.54)))


def make_crop_sheet(items, output):
    thumb_w, thumb_h = 384, 180
    label_h = 38
    tiles = []
    for path, label in items:
        crop = crop_plate_band(path)
        crop.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:60], fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)
    sheet = Image.new("RGB", (thumb_w * len(tiles), thumb_h + label_h), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--guide-output",
        default=str(GUIDE_DIR / "stegosaurus-stenops_plate_lock_v1.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "stegosaurus-stenops-plate-lock-guide-v1.png"),
    )
    parser.add_argument("--sheet-output", default=str(ASSET_DIR / "stegosaurus-plate-lock-reference-sheet-v1.png"))
    parser.add_argument("--crop-output", default=str(ASSET_DIR / "stegosaurus-plate-crops-v3.png"))
    args = parser.parse_args()

    guide_output = Path(args.guide_output).resolve()
    asset_output = Path(args.asset_output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    crop_output = Path(args.crop_output).resolve()

    make_guide(guide_output)
    asset_output.parent.mkdir(parents=True, exist_ok=True)
    Image.open(guide_output).save(asset_output)

    comparisons = [
        (ASSET_DIR / "stegosaurus-stenops-plate-gate-ipcontrol-v1.png", "rejected petal-like current"),
        (ASSET_DIR / "stegosaurus-stenops-plate-reference-guide-v1.png", "older rounded guide"),
        (asset_output, "new plate-lock guide"),
    ]
    make_contact_sheet(comparisons, sheet_output)
    make_crop_sheet(comparisons, crop_output)

    print(guide_output)
    print(asset_output)
    print(sheet_output)
    print(crop_output)


if __name__ == "__main__":
    main()
