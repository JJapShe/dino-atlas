import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
ASSET_DIR = ROOT / "assets" / "dinosaurs"


def scaled(points, scale):
    return [(x * scale, y * scale) for x, y in points]


def clamp(value, low, high):
    return max(low, min(high, value))


def plate_points(cx, base_y, width, height, lean, asymmetry):
    apex_x = cx + lean + asymmetry * width * 0.06
    return [
        (cx - width * 0.46, base_y + height * 0.02),
        (cx - width * 0.60, base_y - height * 0.18),
        (cx + lean - width * 0.52, base_y - height * 0.56),
        (apex_x - width * 0.20, base_y - height * 0.90),
        (apex_x, base_y - height),
        (apex_x + width * 0.22, base_y - height * 0.90),
        (cx + lean + width * 0.52, base_y - height * 0.56),
        (cx + width * 0.60, base_y - height * 0.18),
        (cx + width * 0.46, base_y + height * 0.02),
    ]


def draw_background(draw, width, height, scale):
    for y in range(height * scale):
        t = y / (height * scale - 1)
        if t < 0.58:
            local = t / 0.58
            color = (
                int(177 * (1 - local) + 145 * local),
                int(202 * (1 - local) + 188 * local),
                int(203 * (1 - local) + 181 * local),
            )
        else:
            local = (t - 0.58) / 0.42
            color = (
                int(178 * (1 - local) + 125 * local),
                int(165 * (1 - local) + 117 * local),
                int(119 * (1 - local) + 84 * local),
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
    mask_pixels = mask.load()
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if mask_pixels[x, y] < 24:
            continue
        radius = rng.choice([1, 1, 2, 3]) * scale / 2
        tone = rng.choice(tones)
        alpha = rng.randrange(alpha_range[0], alpha_range[1])
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def add_shadow(base, points, scale, opacity=90, blur=12):
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.polygon(scaled(points, scale), fill=(18, 13, 9, opacity))
    return Image.alpha_composite(base, shadow.filter(ImageFilter.GaussianBlur(radius=blur * scale)))


def draw_body(layer, scale, omit_thagomizer=False):
    body = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(body)
    body_mask = Image.new("L", layer.size, 0)
    mask_draw = ImageDraw.Draw(body_mask)

    outline = (42, 32, 23, 255)
    body_fill = (91, 73, 48, 255)
    body_light = (136, 108, 69, 72)

    # Left-facing Stegosaurus body plan: small low head, heavy body, long raised tail.
    tail = [(770, 410), (1068, 338), (1102, 366), (818, 470)]
    neck = [(248, 397), (150, 372), (136, 424), (256, 458)]
    head = [(132, 366), (78, 370), (42, 400), (58, 438), (116, 458), (168, 442), (176, 395)]
    body_poly = [
        (220, 442),
        (254, 352),
        (344, 302),
        (472, 276),
        (628, 282),
        (760, 334),
        (838, 410),
        (806, 494),
        (682, 542),
        (500, 550),
        (344, 520),
        (246, 480),
    ]

    layer = add_shadow(layer, [(210, 532), (800, 520), (865, 555), (760, 596), (300, 590)], scale, 70, 13)

    for pts, fill in [
        (tail, (80, 61, 41, 255)),
        (neck, (82, 64, 43, 255)),
        (head, (93, 75, 51, 255)),
        (body_poly, body_fill),
    ]:
        sp = scaled(pts, scale)
        draw.polygon(sp, fill=fill)
        draw.line(sp + [sp[0]], fill=outline, width=max(3, 4 * scale), joint="curve")
        mask_draw.polygon(sp, fill=255)

    # Body highlights and belly shadow are soft, to avoid the hard cartoon feel of v1.
    draw.arc((270 * scale, 260 * scale, 778 * scale, 548 * scale), 188, 348, fill=body_light, width=5 * scale)
    draw.ellipse((100 * scale, 398 * scale, 114 * scale, 412 * scale), fill=(22, 18, 14, 255))

    legs = [
        [(298, 498), (356, 506), (340, 646), (282, 646), (270, 672), (356, 672)],
        [(444, 518), (506, 512), (496, 650), (434, 650), (420, 674), (512, 674)],
        [(648, 498), (708, 490), (716, 648), (654, 648), (640, 672), (728, 672)],
        [(764, 470), (816, 466), (834, 646), (776, 646), (762, 672), (850, 672)],
    ]
    for idx, leg in enumerate(legs):
        color = (58, 43, 30, 255) if idx in (0, 2) else (70, 51, 34, 255)
        pts = scaled(leg, scale)
        draw.polygon(pts, fill=color)
        draw.line(pts + [pts[0]], fill=(39, 29, 20, 210), width=max(2, 3 * scale), joint="curve")
        mask_draw.polygon(pts, fill=255)

    if not omit_thagomizer:
        spikes = [
            [(1058, 356), (1122, 334), (1082, 382)],
            [(1076, 378), (1134, 386), (1078, 410)],
            [(1050, 372), (1090, 326), (1078, 386)],
            [(1054, 394), (1102, 444), (1072, 406)],
        ]
        for pts in spikes:
            sp = scaled(pts, scale)
            draw.polygon(sp, fill=(128, 90, 53, 255))
            draw.line(sp + [sp[0]], fill=outline, width=max(2, 3 * scale), joint="curve")

    body = texture_into(
        body,
        body_mask,
        2026062401,
        [(54, 43, 30), (118, 92, 58), (78, 62, 42), (144, 119, 78)],
        4800,
        scale,
        (7, 26),
    )
    return Image.alpha_composite(layer, body)


def draw_plates(layer, scale):
    rng = random.Random(2026062402)
    plates = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    mask = Image.new("L", layer.size, 0)
    draw = ImageDraw.Draw(plates)
    mask_draw = ImageDraw.Draw(mask)

    far_specs = [
        (296, 382, 42, 70, -4),
        (376, 340, 54, 104, -3),
        (468, 308, 64, 142, -1),
        (574, 298, 72, 166, 1),
        (680, 320, 62, 124, 3),
        (768, 372, 44, 74, 4),
    ]
    near_specs = [
        (250, 410, 36, 52, -4),
        (330, 360, 54, 92, -3),
        (420, 320, 66, 134, -2),
        (524, 296, 78, 176, 0),
        (632, 304, 76, 164, 2),
        (730, 342, 58, 108, 3),
        (814, 394, 38, 58, 4),
    ]

    def draw_one(spec, far):
        cx, base_y, width, height, lean = spec
        points = plate_points(cx, base_y, width, height, lean, rng.uniform(-0.24, 0.24))
        pts = scaled(points, scale)
        fill = (107, 76, 47, 230) if far else (145, 96, 52, 248)
        edge = (43, 31, 23, 236 if not far else 200)
        rim = (196, 145, 84, 76 if not far else 48)
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=edge, width=max(2, int((3.6 if far else 4.6) * scale)), joint="curve")
        draw.line(pts[2:7], fill=rim, width=max(1, int(1.4 * scale)), joint="curve")
        mask_draw.polygon(pts, fill=255)

        # Central grooves should read as shallow scute texture, not leaf veins.
        groove_top = ((cx + lean * 0.86) * scale, (base_y - height * 0.84) * scale)
        groove_bottom = ((cx + lean * 0.12) * scale, (base_y - height * 0.16) * scale)
        draw.line([groove_top, groove_bottom], fill=(60, 42, 30, 78), width=max(1, int(1.2 * scale)))

        socket = [
            (cx - width * 0.48, base_y + height * 0.018),
            (cx + width * 0.48, base_y + height * 0.018),
        ]
        draw.line(scaled(socket, scale), fill=(30, 22, 16, 170), width=max(2, int(2.4 * scale)))

    for spec in far_specs:
        draw_one(spec, True)
    for spec in near_specs:
        draw_one(spec, False)

    plates = texture_into(
        plates,
        mask,
        2026062403,
        [(73, 51, 35), (155, 103, 56), (111, 76, 45), (188, 133, 75)],
        2100,
        scale,
        (8, 34),
    )
    plates.putalpha(plates.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.10 * scale)))
    return Image.alpha_composite(layer, plates)


def make_guide(output, omit_thagomizer=False):
    width, height = 1152, 768
    scale = 3
    base = Image.new("RGB", (width * scale, height * scale))
    draw = ImageDraw.Draw(base)
    draw_background(draw, width, height, scale)

    rng = random.Random(2026062404)
    for _ in range(340):
        x = rng.randrange(0, width * scale)
        y = rng.randrange(int(height * 0.69 * scale), height * scale)
        tone = rng.choice([(111, 98, 70), (84, 75, 55), (147, 134, 94), (74, 91, 61)])
        draw.line((x, y, x + rng.randrange(-16, 18), y - rng.randrange(6, 30)), fill=tone, width=rng.randrange(1, 3))

    image = base.convert("RGBA")
    image = draw_plates(image, scale)
    image = draw_body(image, scale, omit_thagomizer=omit_thagomizer)
    image = draw_plates(image, scale)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.08 * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    image = ImageOps.autocontrast(image, cutoff=0.4)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 384, 256
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

    sheet = Image.new("RGB", (len(tiles) * thumb_w, thumb_h + label_h), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--guide-output",
        default=str(GUIDE_DIR / "stegosaurus-stenops_plate_gate_v3.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "stegosaurus-stenops-plate-gate-guide-v3.png"),
    )
    parser.add_argument("--sheet-output", default=str(ASSET_DIR / "stegosaurus-plate-gate-sheet-v3.png"))
    parser.add_argument("--omit-thagomizer", action="store_true")
    args = parser.parse_args()

    guide_output = Path(args.guide_output).resolve()
    asset_output = Path(args.asset_output).resolve()
    sheet_output = Path(args.sheet_output).resolve()

    make_guide(guide_output, omit_thagomizer=args.omit_thagomizer)
    asset_output.parent.mkdir(parents=True, exist_ok=True)
    Image.open(guide_output).save(asset_output)
    make_contact_sheet([(asset_output, "plate gate guide v2")], sheet_output)

    print(guide_output)
    print(asset_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
