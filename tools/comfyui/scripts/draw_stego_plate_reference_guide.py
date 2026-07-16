import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
ASSET_DIR = ROOT / "assets" / "dinosaurs"


def sc(points, scale):
    return [(x * scale, y * scale) for x, y in points]


def plate_points(cx, base_y, w, h, lean, asym=0.0):
    apex = (cx + lean + asym * w * 0.10, base_y - h)
    return [
        (cx - w * 0.44, base_y + h * 0.02),
        (cx - w * 0.56, base_y - h * 0.18),
        (cx + lean - w * 0.50, base_y - h * 0.55),
        (apex[0] - w * 0.22, base_y - h * 0.88),
        apex,
        (apex[0] + w * 0.22, base_y - h * 0.88),
        (cx + lean + w * 0.50, base_y - h * 0.55),
        (cx + w * 0.56, base_y - h * 0.18),
        (cx + w * 0.44, base_y + h * 0.02),
    ]


def draw_gradient_background(draw, width, height, scale):
    for y in range(height * scale):
        t = y / (height * scale - 1)
        if t < 0.62:
            local = t / 0.62
            color = (
                int(190 * (1 - local) + 152 * local),
                int(215 * (1 - local) + 194 * local),
                int(215 * (1 - local) + 176 * local),
            )
        else:
            local = (t - 0.62) / 0.38
            color = (
                int(184 * (1 - local) + 143 * local),
                int(174 * (1 - local) + 135 * local),
                int(137 * (1 - local) + 98 * local),
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
        if mask_pix[x, y] < 20:
            continue
        radius = rng.choice([1, 1, 2, 3]) * scale / 3
        tone = rng.choice(tones)
        alpha = rng.randrange(8, 36)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def make_guide(output):
    width, height = 1152, 768
    scale = 4
    image = Image.new("RGB", (width * scale, height * scale))
    draw = ImageDraw.Draw(image)
    draw_gradient_background(draw, width, height, scale)

    rng = random.Random(2026062331)
    # Ground details.
    for _ in range(260):
        x = rng.randrange(0, width * scale)
        y = rng.randrange(int(height * 0.72 * scale), height * scale)
        tone = rng.choice([(118, 105, 75), (92, 82, 61), (151, 139, 98), (69, 92, 62)])
        draw.line((x, y, x + rng.randrange(-18, 18), y - rng.randrange(8, 34)), fill=tone, width=rng.randrange(1, 4))

    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    body_draw = ImageDraw.Draw(layer)

    body_fill = (100, 79, 51, 255)
    body_shadow = (55, 42, 30, 255)
    body_high = (139, 111, 70, 255)
    outline = (45, 35, 25, 255)

    # Body, neck, head, and tail are deliberately simple but proportionally Stegosaurus-like.
    body = sc(
        [
            (280, 456),
            (320, 380),
            (420, 330),
            (570, 318),
            (725, 350),
            (818, 418),
            (788, 502),
            (656, 546),
            (486, 552),
            (350, 526),
        ],
        scale,
    )
    body_draw.polygon(body, fill=body_fill)
    body_draw.line(body + [body[0]], fill=outline, width=7 * scale)
    body_draw.arc((308 * scale, 316 * scale, 805 * scale, 566 * scale), 190, 355, fill=body_high, width=4 * scale)
    body_draw.arc((308 * scale, 356 * scale, 804 * scale, 610 * scale), 12, 174, fill=body_shadow, width=3 * scale)

    neck = sc([(770, 410), (890, 386), (898, 432), (795, 466)], scale)
    head = sc([(874, 378), (950, 362), (1030, 388), (1045, 428), (1016, 466), (928, 476), (870, 448)], scale)
    tail = sc([(300, 442), (56, 360), (92, 406), (270, 500)], scale)
    body_draw.polygon(tail, fill=(83, 64, 42, 255))
    body_draw.line(tail + [tail[0]], fill=outline, width=7 * scale)
    body_draw.polygon(neck, fill=(92, 70, 46, 255))
    body_draw.line(neck + [neck[0]], fill=outline, width=6 * scale)
    body_draw.polygon(head, fill=(105, 83, 55, 255))
    body_draw.line(head + [head[0]], fill=outline, width=6 * scale)
    body_draw.ellipse((992 * scale, 404 * scale, 1012 * scale, 424 * scale), fill=(30, 25, 20, 255))

    legs = [
        [(360, 505), (410, 515), (398, 650), (342, 650)],
        [(548, 512), (604, 516), (602, 650), (546, 650)],
        [(704, 486), (758, 494), (760, 650), (704, 650)],
        [(820, 475), (872, 482), (868, 650), (812, 650)],
    ]
    for idx, leg in enumerate(legs):
        color = (65, 48, 34, 255) if idx in (0, 2) else (76, 56, 39, 255)
        pts = sc(leg, scale)
        body_draw.polygon(pts, fill=color)
        foot = sc([(leg[2][0] - 6, 642), (leg[2][0] + 54, 642), (leg[2][0] + 54, 672), (leg[2][0] - 18, 672)], scale)
        body_draw.polygon(foot, fill=color)

    # Four-spike thagomizer at the tail tip.
    spikes = [
        [(58, 360), (4, 332), (46, 390)],
        [(78, 383), (16, 432), (104, 414)],
        [(90, 374), (52, 318), (124, 374)],
        [(72, 408), (24, 488), (112, 426)],
    ]
    for pts in spikes:
        sp = sc(pts, scale)
        body_draw.polygon(sp, fill=(125, 86, 49, 255))
        body_draw.line(sp + [sp[0]], fill=outline, width=5 * scale)

    image = Image.alpha_composite(image.convert("RGBA"), layer)

    # Alternating dorsal plates: far row first, then near row. They do not touch
    # each other, and the largest plates sit over the hips/mid-back.
    plate_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", image.size, 0)
    plate_draw = ImageDraw.Draw(plate_layer)
    mask_draw = ImageDraw.Draw(plate_mask)
    far_specs = [
        (330, 392, 42, 70, -3),
        (395, 356, 55, 104, -2),
        (478, 330, 66, 145, -1),
        (570, 318, 74, 170, 1),
        (662, 336, 64, 138, 2),
        (742, 380, 48, 92, 3),
    ]
    near_specs = [
        (288, 424, 34, 48, -2),
        (358, 378, 48, 86, -2),
        (435, 342, 62, 128, -1),
        (524, 318, 76, 178, 0),
        (620, 326, 74, 164, 1),
        (710, 362, 58, 112, 2),
        (786, 414, 40, 64, 2),
    ]

    def draw_one_plate(spec, far):
        cx, by, pw, ph, lean = spec
        pts = sc(plate_points(cx, by, pw, ph, lean, rng.uniform(-0.22, 0.22)), scale)
        fill = (122, 83, 46, 236) if far else (151, 98, 50, 250)
        edge = (45, 32, 24, 255)
        rim = (187, 135, 74, 90)
        plate_draw.polygon(pts, fill=fill)
        plate_draw.line(pts + [pts[0]], fill=edge, width=(5 if far else 6) * scale)
        plate_draw.line(pts[2:7], fill=rim, width=2 * scale, joint="curve")
        mask_draw.polygon(pts, fill=255)
        # Blunt pitted bony texture, not branching veins.
        for _ in range(10 if far else 15):
            px = rng.uniform((cx - pw * 0.32) * scale, (cx + pw * 0.32) * scale)
            py = rng.uniform((by - ph * 0.78) * scale, (by - ph * 0.18) * scale)
            rr = rng.uniform(1.0, 2.8) * scale
            plate_draw.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(69, 48, 34, rng.randrange(18, 42)))

    for spec in far_specs:
        draw_one_plate(spec, True)
    for spec in near_specs:
        draw_one_plate(spec, False)
    plate_layer = draw_texture(
        plate_layer,
        plate_mask,
        2026062332,
        [(76, 52, 35), (168, 117, 64), (115, 78, 44), (49, 36, 28)],
        1800,
        scale,
    )
    image = Image.alpha_composite(image, plate_layer)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.18 * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    image = ImageOps.mirror(image)

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
        default=str(GUIDE_DIR / "stegosaurus-stenops_plate_reference_v1.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "stegosaurus-stenops-plate-reference-guide-v1.png"),
    )
    parser.add_argument("--sheet-output", default=str(ASSET_DIR / "stegosaurus-plate-reference-sheet-v1.png"))
    args = parser.parse_args()

    guide_output = Path(args.guide_output).resolve()
    asset_output = Path(args.asset_output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    make_guide(guide_output)
    asset_output.parent.mkdir(parents=True, exist_ok=True)
    Image.open(guide_output).save(asset_output)
    make_contact_sheet([(asset_output, "plate reference guide")], sheet_output)
    print(guide_output)
    print(asset_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
