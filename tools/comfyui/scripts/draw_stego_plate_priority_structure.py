import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

WIDTH = 1152
HEIGHT = 768


VARIANTS = {
    "v1a": {
        "seed": 2026063001,
        "plate_height": 0.96,
        "plate_width": 1.03,
        "body_y": 0,
        "tone": 0.98,
    },
    "v1b": {
        "seed": 2026063002,
        "plate_height": 0.90,
        "plate_width": 1.10,
        "body_y": 4,
        "tone": 1.00,
    },
    "v1c": {
        "seed": 2026063003,
        "plate_height": 1.04,
        "plate_width": 0.96,
        "body_y": -3,
        "tone": 0.95,
    },
}


PLATE_ROW = [
    # cx, base_y, width, height, lean. The row is drawn as separated flat
    # slabs; alternating tones hint at the staggered left/right arrangement
    # without turning the silhouette into a chunky double ridge.
    (228, 438, 24, 38, -3),
    (262, 424, 28, 48, -3),
    (302, 404, 34, 62, -3),
    (350, 382, 40, 80, -2),
    (404, 360, 48, 98, -2),
    (464, 342, 56, 120, -1),
    (532, 328, 66, 146, 0),
    (604, 330, 66, 148, 1),
    (676, 350, 58, 124, 2),
    (740, 378, 48, 98, 3),
    (796, 408, 40, 74, 4),
    (840, 436, 30, 52, 4),
    (872, 456, 22, 34, 4),
]


def sc(points, scale):
    return [(int(round(x * scale)), int(round(y * scale))) for x, y in points]


def clamp(value, low, high):
    return max(low, min(high, value))


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def tone(color, factor):
    return tuple(clamp(int(channel * factor), 0, 255) for channel in color)


def add_mask_noise(layer, mask, rng, colors, count, scale, alpha=(8, 34)):
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    bbox = mask.getbbox()
    if not bbox:
        return layer

    pixels = mask.load()
    x0, y0, x1, y1 = bbox
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if pixels[x, y] < 16:
            continue
        color = rng.choice(colors)
        if rng.random() < 0.18:
            radius = rng.uniform(0.45 * scale, 1.55 * scale)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, rng.randrange(*alpha)))
        else:
            draw.point((x, y), fill=(*color, rng.randrange(*alpha)))

    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_background(draw, rng, scale):
    sky_top = (184, 215, 218)
    sky_low = (150, 190, 182)
    ground_top = (188, 174, 119)
    ground_low = (132, 122, 82)
    horizon = int(HEIGHT * 0.60 * scale)

    for y in range(HEIGHT * scale):
        if y < horizon:
            t = y / horizon
            color = mix(sky_top, sky_low, t)
        else:
            t = (y - horizon) / max(1, HEIGHT * scale - horizon)
            color = mix(ground_top, ground_low, t)
        draw.line((0, y, WIDTH * scale, y), fill=color)

    draw.rectangle((0, horizon, WIDTH * scale, HEIGHT * scale), fill=ground_top)
    for y in range(horizon, HEIGHT * scale):
        t = (y - horizon) / max(1, HEIGHT * scale - horizon)
        color = mix(ground_top, ground_low, t)
        draw.line((0, y, WIDTH * scale, y), fill=color)

    for _ in range(520):
        x = rng.randrange(0, WIDTH * scale)
        y = rng.randrange(horizon + 10 * scale, HEIGHT * scale)
        length = rng.randrange(8 * scale, 30 * scale)
        lean = rng.randrange(-8 * scale, 8 * scale)
        color = rng.choice([(79, 93, 54), (104, 110, 68), (143, 128, 82), (67, 78, 48)])
        draw.line((x, y, x + lean, y - length), fill=color, width=max(1, scale // 2))


def draw_body(layer, mask, rng, scale, variant):
    dy = variant["body_y"] * scale
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    outline = (34, 27, 21, 255)
    body_mid = tone((103, 78, 52), variant["tone"])
    body_dark = tone((70, 53, 37), variant["tone"])
    body_light = tone((144, 111, 72), variant["tone"])

    tail = sc([(770, 424), (1016, 344), (1064, 358), (808, 486)], scale)
    body = sc(
        [
            (232, 454),
            (284, 396),
            (408, 352),
            (552, 334),
            (700, 350),
            (818, 404),
            (878, 468),
            (836, 520),
            (700, 552),
            (512, 550),
            (354, 524),
            (266, 486),
        ],
        scale,
    )
    neck = sc([(292, 414), (178, 384), (154, 426), (304, 462)], scale)
    head = sc([(168, 378), (96, 382), (44, 410), (58, 442), (116, 462), (176, 444), (206, 404)], scale)
    belly = sc([(318, 538), (456, 566), (642, 568), (776, 536)], scale)

    shifted = []
    for shape in (tail, body, neck, head):
        shifted.append([(x, y + dy) for x, y in shape])
    tail, body, neck, head = shifted
    belly = [(x, y + dy) for x, y in belly]

    for pts, fill in ((tail, body_dark), (body, (*body_mid, 255)), (neck, body_dark), (head, (*body_mid, 255))):
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
        mask_draw.polygon(pts, fill=255)

    draw.line(belly, fill=(50, 39, 29, 150), width=max(2, 2 * scale), joint="curve")
    draw.arc((284 * scale, 324 * scale + dy, 850 * scale, 560 * scale + dy), 194, 350, fill=(*body_light, 148), width=max(3, 3 * scale))
    draw.arc((294 * scale, 382 * scale + dy, 864 * scale, 606 * scale + dy), 12, 174, fill=(46, 35, 26, 130), width=max(3, 3 * scale))
    draw.ellipse((105 * scale, 398 * scale + dy, 118 * scale, 412 * scale + dy), fill=(16, 14, 12, 255))

    legs = [
        ([(314, 500), (374, 512), (358, 646), (304, 646), (286, 672), (378, 672)], (55, 41, 30, 255)),
        ([(450, 518), (504, 516), (498, 650), (438, 650), (420, 674), (518, 674)], (75, 56, 39, 255)),
        ([(652, 512), (708, 508), (714, 650), (650, 650), (632, 674), (732, 674)], (55, 41, 30, 255)),
        ([(772, 492), (828, 488), (840, 650), (780, 650), (762, 674), (858, 674)], (76, 57, 40, 255)),
    ]
    for pts, fill in legs:
        spts = [(x, y + dy) for x, y in sc(pts, scale)]
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
        mask_draw.polygon(spts, fill=255)

    hub = sc([(1000, 348), (1036, 350), (1060, 366), (1038, 386), (1000, 380), (984, 362)], scale)
    hub = [(x, y + dy) for x, y in hub]
    draw.polygon(hub, fill=(95, 68, 44, 255))
    draw.line(hub + [hub[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
    mask_draw.polygon(hub, fill=255)

    spikes = [
        [(1012, 350), (1034, 356), (1076, 292)],
        [(1038, 356), (1058, 366), (1120, 326)],
        [(1010, 376), (1032, 386), (1074, 452)],
        [(1038, 376), (1058, 386), (1122, 426)],
    ]
    for pts in spikes:
        spts = [(x, y + dy) for x, y in sc(pts, scale)]
        draw.polygon(spts, fill=(154, 99, 56, 255))
        draw.line(spts + [spts[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
        mask_draw.polygon(spts, fill=255)

    return add_mask_noise(
        layer,
        mask,
        rng,
        [(51, 40, 31), (112, 85, 57), (152, 118, 76), (80, 60, 42)],
        4200,
        scale,
    )


def plate_polygon(cx, base_y, width, height, lean, asym):
    apex_x = cx + lean + width * asym * 0.10
    return [
        (cx - width * 0.43, base_y + height * 0.02),
        (cx - width * 0.58, base_y - height * 0.18),
        (cx + lean * 0.12 - width * 0.48, base_y - height * 0.52),
        (apex_x - width * 0.18, base_y - height * 0.86),
        (apex_x, base_y - height),
        (apex_x + width * 0.18, base_y - height * 0.86),
        (cx + lean * 0.12 + width * 0.48, base_y - height * 0.52),
        (cx + width * 0.58, base_y - height * 0.18),
        (cx + width * 0.43, base_y + height * 0.02),
    ]


def draw_one_plate(draw, mask_draw, spec, scale, variant, palette, rng, far=False):
    cx, base_y, width, height, lean = spec
    cx *= scale
    base_y = (base_y + variant["body_y"]) * scale
    width *= scale * variant["plate_width"] * (0.94 if far else 1.0)
    height *= scale * variant["plate_height"] * (0.92 if far else 1.0)
    lean *= scale

    points = plate_polygon(cx, base_y, width, height, lean, rng.uniform(-0.32, 0.32))
    fill = palette["far"] if far else palette["near"]
    edge = palette["edge_far"] if far else palette["edge"]
    high = palette["highlight_far"] if far else palette["highlight"]
    low = palette["shadow_far"] if far else palette["shadow"]

    socket_alpha = 55 if far else 72
    draw.ellipse((cx - width * 0.44, base_y - height * 0.02, cx + width * 0.44, base_y + height * 0.07), fill=(*low[:3], socket_alpha))
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=255)

    # Keep the plates as thin bony slabs. A heavy filled lower face makes them
    # read as rocks or a shell ridge instead of Stegosaurus dorsal plates.
    lower = [points[0], points[1], (cx + lean - width * 0.34, base_y - height * 0.18), (cx + lean + width * 0.35, base_y - height * 0.18), points[7], points[8]]
    draw.polygon(lower, fill=(*low[:3], 10 if far else 16))
    draw.line(points + [points[0]], fill=edge, width=max(3, int(1.25 * scale)), joint="curve")
    draw.line(points[2:7], fill=high, width=max(1, int(0.55 * scale)), joint="curve")
    draw.line((points[0], points[8]), fill=(*low[:3], 105), width=max(2, int(0.70 * scale)))

    ridge = [(points[4][0], points[4][1]), (cx + lean * 0.35, base_y - height * 0.30)]
    draw.line(ridge, fill=(*palette["edge"][:3], 70 if far else 88), width=max(1, int(0.45 * scale)))
    draw.line((points[1], points[7]), fill=(*palette["highlight"][:3], 28 if far else 42), width=max(1, int(0.35 * scale)))

    for _ in range(9 if far else 14):
        px = rng.uniform(cx - width * 0.28, cx + width * 0.28)
        py = rng.uniform(base_y - height * 0.76, base_y - height * 0.18)
        radius = rng.uniform(0.40 * scale, 1.20 * scale)
        color = rng.choice([palette["spot"], palette["highlight"], palette["shadow"], fill])
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(*color[:3], rng.randrange(14, 38)))


def draw_plates(layer, mask, rng, scale, variant):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    palette = {
        "near": (158, 98, 52, 246),
        "far": (128, 82, 51, 224),
        "edge": (34, 25, 18, 238),
        "edge_far": (35, 28, 22, 204),
        "highlight": (219, 159, 97, 72),
        "highlight_far": (190, 132, 78, 54),
        "shadow": (67, 43, 29, 88),
        "shadow_far": (53, 38, 28, 72),
        "spot": (236, 213, 171, 130),
    }

    for index, spec in enumerate(PLATE_ROW):
        cx, base_y, width, height, lean = spec
        offset = -4 if index % 2 else 3
        adjusted = (cx, base_y + offset, width, height * (0.96 if index % 2 else 1.0), lean)
        draw_one_plate(draw, mask_draw, adjusted, scale, variant, palette, rng, far=index % 2 == 0)

    return add_mask_noise(
        layer,
        mask,
        rng,
        [(65, 43, 30), (195, 126, 63), (234, 194, 142), (113, 69, 42)],
        1200,
        scale,
        alpha=(6, 28),
    )


def render_variant(name, variant, output_dir, scale=3):
    rng = random.Random(variant["seed"])
    canvas = Image.new("RGBA", (WIDTH * scale, HEIGHT * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_background(draw, rng, scale)

    body_mask = Image.new("L", canvas.size, 0)
    canvas = draw_body(canvas, body_mask, rng, scale, variant)

    plate_mask = Image.new("L", canvas.size, 0)
    canvas = draw_plates(canvas, plate_mask, rng, scale, variant)

    # A very small ground contact shadow keeps the guide from floating while
    # avoiding decorative effects that obscure leg count.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse((236 * scale, 632 * scale, 884 * scale, 720 * scale), fill=(24, 18, 12, 42))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14 * scale))
    canvas = Image.alpha_composite(shadow, canvas)

    image = canvas.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    output = output_dir / f"stego_plate_priority_structure_v1_{name}.png"
    image.save(output)
    return output


def label_image(path, label):
    image = Image.open(path).convert("RGB").resize((384, 256), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (384, 292), (244, 241, 232))
    canvas.paste(image, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 256, 384, 292), fill=(42, 35, 28))
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    draw.text((12, 266), label, fill=(245, 236, 214), font=font)
    return canvas


def make_contact_sheet(paths, sheet_output):
    labels = [
        "v1a - balanced plates",
        "v1b - lower broader plates",
        "v1c - taller strict plates",
    ]
    cells = [label_image(path, labels[index]) for index, path in enumerate(paths)]
    sheet = Image.new("RGB", (384 * len(cells), 292), (244, 241, 232))
    for index, cell in enumerate(cells):
        sheet.paste(cell, (index * 384, 0))
    sheet.save(sheet_output)


def make_crop_sheet(selected, crop_output):
    image = Image.open(selected).convert("RGB")
    crops = [
        ("dorsal plate row", (210, 148, 900, 488)),
        ("neck small plates", (198, 306, 406, 488)),
        ("mid-back large plates", (414, 150, 708, 470)),
        ("tail base plates + spikes", (730, 318, 1110, 482)),
    ]
    cell_w, cell_h = 360, 235
    sheet = Image.new("RGB", (cell_w * 2, cell_h * 2), (244, 241, 232))
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(sheet)
    for index, (label, box) in enumerate(crops):
        crop = image.crop(box)
        crop.thumbnail((cell_w, cell_h - 28), Image.Resampling.LANCZOS)
        x = (index % 2) * cell_w
        y = (index // 2) * cell_h
        sheet.paste(crop, (x + (cell_w - crop.width) // 2, y + 6))
        draw.rectangle((x, y + cell_h - 28, x + cell_w, y + cell_h), fill=(42, 35, 28))
        draw.text((x + 10, y + cell_h - 21), label, fill=(245, 236, 214), font=font)
    sheet.save(crop_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(OUTPUT_ROOT))
    parser.add_argument("--asset-output", default=str(ASSET_ROOT / "stegosaurus-stenops-plate-priority-structure-v1.png"))
    parser.add_argument("--sheet-output", default=str(ASSET_ROOT / "stegosaurus-review-options-v36.png"))
    parser.add_argument("--crop-output", default=str(ASSET_ROOT / "stegosaurus-plate-crops-v8.png"))
    parser.add_argument("--selected", choices=sorted(VARIANTS), default="v1b")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered = [render_variant(name, variant, output_dir) for name, variant in VARIANTS.items()]
    selected_path = output_dir / f"stego_plate_priority_structure_v1_{args.selected}.png"
    Image.open(selected_path).save(args.asset_output)
    make_contact_sheet(rendered, Path(args.sheet_output))
    make_crop_sheet(selected_path, Path(args.crop_output))

    print(f"selected={selected_path}")
    print(f"asset={args.asset_output}")
    print(f"sheet={args.sheet_output}")
    print(f"crops={args.crop_output}")


if __name__ == "__main__":
    main()
