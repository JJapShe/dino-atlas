import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-plate-relock-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {
        "seed": 2026062921,
        "height": 1.00,
        "width": 1.00,
        "warm": 1.00,
        "edge": 0.92,
        "tail": "medium",
    },
    "v1b": {
        "seed": 2026062922,
        "height": 0.94,
        "width": 1.08,
        "warm": 0.94,
        "edge": 0.82,
        "tail": "subtle",
    },
    "v1c": {
        "seed": 2026062923,
        "height": 1.06,
        "width": 0.96,
        "warm": 1.04,
        "edge": 1.00,
        "tail": "strong",
    },
}


# Side-view Stegosaurus plate targets for the current 1152x768 relock image.
# They intentionally leave sky/background gaps between plates instead of a
# continuous crest or shell band.
FAR_PLATES = [
    (0.248, 0.456, 0.030, 0.064, -0.003),
    (0.306, 0.414, 0.037, 0.087, -0.003),
    (0.382, 0.372, 0.048, 0.120, -0.002),
    (0.480, 0.338, 0.057, 0.151, -0.001),
    (0.590, 0.336, 0.058, 0.158, 0.001),
    (0.696, 0.382, 0.047, 0.112, 0.003),
    (0.788, 0.446, 0.035, 0.076, 0.004),
    (0.850, 0.506, 0.024, 0.047, 0.004),
]

NEAR_PLATES = [
    (0.220, 0.476, 0.026, 0.052, -0.004),
    (0.274, 0.438, 0.034, 0.074, -0.003),
    (0.342, 0.394, 0.043, 0.104, -0.002),
    (0.432, 0.352, 0.054, 0.135, -0.001),
    (0.538, 0.324, 0.063, 0.169, 0.000),
    (0.646, 0.354, 0.052, 0.128, 0.002),
    (0.742, 0.416, 0.041, 0.090, 0.003),
    (0.816, 0.486, 0.030, 0.058, 0.004),
]

TAIL_VARIANTS = {
    "subtle": {
        "hub": [(1078, 323), (1100, 319), (1112, 328), (1104, 340), (1080, 338), (1070, 330)],
        "spikes": [
            ((1087, 319), (1100, 322), (1122, 292)),
            ((1100, 324), (1113, 330), (1135, 308)),
            ((1088, 338), (1100, 344), (1121, 374)),
            ((1101, 337), (1114, 343), (1136, 362)),
        ],
        "alpha": 0.88,
    },
    "medium": {
        "hub": [(1074, 321), (1104, 316), (1118, 328), (1106, 346), (1074, 342), (1062, 330)],
        "spikes": [
            ((1086, 316), (1103, 321), (1130, 284)),
            ((1103, 323), (1118, 332), (1146, 303)),
            ((1086, 341), (1103, 350), (1130, 389)),
            ((1104, 339), (1119, 347), (1146, 369)),
        ],
        "alpha": 0.96,
    },
    "strong": {
        "hub": [(1070, 320), (1107, 315), (1123, 328), (1108, 350), (1070, 345), (1054, 330)],
        "spikes": [
            ((1085, 315), (1106, 320), (1138, 278)),
            ((1105, 323), (1123, 333), (1152, 300)),
            ((1086, 343), (1106, 352), (1138, 398)),
            ((1107, 340), (1123, 349), (1152, 374)),
        ],
        "alpha": 1.0,
    },
}


def clamp(value, low, high):
    return max(low, min(high, value))


def color_mix(a, b, ratio):
    return tuple(int(a[i] * (1 - ratio) + b[i] * ratio) for i in range(3))


def average_color(image, box):
    x0, y0, x1, y1 = box
    x0 = int(clamp(x0, 0, image.width - 1))
    y0 = int(clamp(y0, 0, image.height - 1))
    x1 = int(clamp(x1, x0 + 1, image.width))
    y1 = int(clamp(y1, y0 + 1, image.height))
    return image.crop((x0, y0, x1, y1)).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def make_existing_plate_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    # Covers the old rounded plate row while staying above the torso. The lower
    # boundary is intentionally tight so body-colored inpaint cannot become a
    # continuous dorsal band between the new plates.
    upper = [
        (0.190, 0.492),
        (0.205, 0.405),
        (0.260, 0.300),
        (0.340, 0.210),
        (0.442, 0.135),
        (0.532, 0.088),
        (0.624, 0.110),
        (0.714, 0.224),
        (0.810, 0.370),
        (0.895, 0.538),
        (0.852, 0.524),
        (0.742, 0.470),
        (0.636, 0.414),
        (0.526, 0.392),
        (0.410, 0.410),
        (0.300, 0.450),
        (0.205, 0.500),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in upper], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.2 * scale))


def smoothstep(edge0, edge1, value):
    t = clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def replace_mask_with_background(image, mask):
    """Fill the old plate area with blurred sky/tree colors, not body color."""
    source = image.convert("RGB")
    width, height = source.size
    sky = average_color(source, (int(width * 0.16), int(height * 0.05), int(width * 0.82), int(height * 0.19)))
    tree = average_color(source, (int(width * 0.12), int(height * 0.34), int(width * 0.92), int(height * 0.44)))
    grass = average_color(source, (int(width * 0.12), int(height * 0.52), int(width * 0.92), int(height * 0.62)))
    backdrop = Image.new("RGB", source.size, sky)
    draw = ImageDraw.Draw(backdrop)
    rng = random.Random(2026062920)
    for y in range(height):
        t_tree = smoothstep(height * 0.24, height * 0.47, y)
        t_grass = smoothstep(height * 0.47, height * 0.62, y)
        color = color_mix(sky, tree, t_tree)
        color = color_mix(color, grass, t_grass * 0.35)
        jitter = rng.randrange(-3, 4)
        color = tuple(clamp(channel + jitter, 0, 255) for channel in color)
        draw.line((0, y, width, y), fill=color)

    backdrop = backdrop.filter(ImageFilter.GaussianBlur(radius=12))
    # Retain a little of the original blurred background texture outside the
    # plate silhouettes to avoid a flat painted sky patch.
    original_blur = source.filter(ImageFilter.GaussianBlur(radius=18))
    backdrop = Image.blend(backdrop, original_blur, 0.22)
    alpha = mask.resize(source.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.96))
    layer = backdrop.convert("RGBA")
    layer.putalpha(alpha)
    base = source.convert("RGBA")
    return Image.alpha_composite(base, layer).convert("RGB")


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=28)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.96))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 23, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def plate_points(cx, base_y, width, height, lean, asymmetry):
    apex_x = cx + lean + asymmetry * width * 0.08
    left_shoulder = (cx + lean - width * 0.50, base_y - height * 0.58)
    right_shoulder = (cx + lean + width * 0.52, base_y - height * 0.56)
    return [
        (cx - width * 0.45, base_y + height * 0.010),
        (cx - width * 0.60, base_y - height * 0.20),
        left_shoulder,
        (apex_x - width * 0.22, base_y - height * 0.88),
        (apex_x - width * 0.055, base_y - height * 0.992),
        (apex_x + width * 0.055, base_y - height * 0.992),
        (apex_x + width * 0.23, base_y - height * 0.88),
        right_shoulder,
        (cx + width * 0.60, base_y - height * 0.20),
        (cx + width * 0.45, base_y + height * 0.010),
    ]


def make_palette(source_large, variant):
    plate = average_color(source_large.convert("RGB"), (420 * 4, 172 * 4, 744 * 4, 304 * 4))
    body = average_color(source_large.convert("RGB"), (460 * 4, 356 * 4, 730 * 4, 464 * 4))
    sky = average_color(source_large.convert("RGB"), (360 * 4, 54 * 4, 760 * 4, 150 * 4))
    warm = (136, 84, 43)
    base = tuple(
        clamp(int((plate[i] * 0.36 + body[i] * 0.20 + warm[i] * 0.44) * variant["warm"]), 54, 174)
        for i in range(3)
    )
    far = tuple(max(30, int(channel * 0.70)) for channel in base)
    dark = tuple(max(16, int(channel * 0.36)) for channel in base)
    mid_shadow = tuple(max(28, int(channel * 0.58)) for channel in base)
    light = color_mix(tuple(clamp(int(channel * 1.25 + 10), 70, 214) for channel in base), sky, 0.08)
    return {
        "base": base,
        "far": far,
        "dark": dark,
        "mid_shadow": mid_shadow,
        "light": light,
        "body": body,
    }


def draw_plate_texture(plate_layer, mask, points, palette, rng, far_row, edge_strength):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, y0, x1, y1 = map(int, (min(xs), min(ys), max(xs), max(ys)))
    mask_pix = mask.load()
    draw = ImageDraw.Draw(plate_layer)
    width = max(1, x1 - x0)
    height = max(1, y1 - y0)
    base = palette["far"] if far_row else palette["base"]
    for y in range(max(0, y0), min(mask.height, y1 + 1)):
        row_t = clamp((y - y0) / height, 0.0, 1.0)
        for x in range(max(0, x0), min(mask.width, x1 + 1)):
            alpha = mask_pix[x, y]
            if alpha < 12:
                continue
            side_t = abs((x - x0) / width - 0.52)
            shade = 0.96 - row_t * 0.28 - side_t * 0.42
            if not far_row:
                shade += 0.08 * math.sin((x - x0) / max(1, width) * math.pi)
            noise = rng.randrange(-12, 13)
            rgb = tuple(clamp(int(channel * shade + noise), 18, 220) for channel in base)
            draw.point((x, y), fill=(*rgb, alpha))

    speckle = Image.new("RGBA", plate_layer.size, (0, 0, 0, 0))
    speckle_draw = ImageDraw.Draw(speckle)
    tones = [palette["dark"], palette["mid_shadow"], palette["light"], palette["base"]]
    count = 440 if far_row else 680
    for _ in range(count):
        x = rng.randrange(max(0, x0), min(mask.width, x1 + 1))
        y = rng.randrange(max(0, y0), min(mask.height, y1 + 1))
        if mask_pix[x, y] < 20:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(8, 34)
        if rng.random() < 0.22:
            radius = rng.choice([1, 1, 2, 3])
            speckle_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            speckle_draw.point((x, y), fill=(*tone, alpha))

    # Subtle vertical growth texture, not leaf veins.
    for frac in (0.30, 0.48, 0.66):
        top = ((points[4][0] + points[5][0]) * 0.5, (points[4][1] + points[5][1]) * 0.5)
        bottom = ((points[0][0] + points[8][0]) * 0.5, (points[0][1] + points[8][1]) * 0.5)
        start = (bottom[0] * (1 - frac) + top[0] * frac, bottom[1] * (1 - frac) + top[1] * frac)
        end = (bottom[0] * (1 - frac * 0.18) + top[0] * frac * 0.18, bottom[1] * (1 - frac * 0.18) + top[1] * frac * 0.18)
        ImageDraw.Draw(speckle).line([end, start], fill=(*palette["light"], 22 if far_row else 34), width=1)

    speckle.putalpha(ImageChops.multiply(speckle.getchannel("A"), mask))
    plate_layer.alpha_composite(speckle)
    outline = ImageDraw.Draw(plate_layer)
    outline_alpha = int((132 if far_row else 192) * edge_strength)
    outline.line(points + [points[0]], fill=(*palette["dark"], outline_alpha), width=3 if not far_row else 2, joint="curve")
    inner_alpha = int((36 if far_row else 56) * edge_strength)
    outline.line(points[2:8], fill=(*palette["light"], inner_alpha), width=1, joint="curve")


def draw_plate(layer, total_mask, spec, size, scale, variant, palette, far_row, rng):
    image_w, image_h = size
    cx, base_y, width, height, lean = spec
    cx *= image_w * scale
    base_y *= image_h * scale
    width *= image_w * scale * variant["width"]
    height *= image_h * scale * variant["height"]
    lean *= image_w * scale
    points = plate_points(cx, base_y, width, height, lean, rng.uniform(-0.25, 0.25))

    socket = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    socket_draw = ImageDraw.Draw(socket)
    socket_alpha = 72 if not far_row else 42
    socket_draw.ellipse(
        (
            cx - width * 0.50,
            base_y - height * 0.030,
            cx + width * 0.50,
            base_y + height * 0.080,
        ),
        fill=(*palette["dark"], socket_alpha),
    )
    layer.alpha_composite(socket.filter(ImageFilter.GaussianBlur(radius=1.0 * scale)))

    mask = Image.new("L", layer.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=224 if far_row else 255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=0.12 * scale))

    plate_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw_plate_texture(plate_layer, mask, points, palette, rng, far_row, variant["edge"])
    layer.alpha_composite(plate_layer)
    total_mask.paste(ImageChops.lighter(total_mask, mask))


def scale_poly(points, scale):
    return [(x * scale, y * scale) for x, y in points]


def draw_tail_spikes(layer, total_mask, source_large, scale, variant_name, palette):
    spec = TAIL_VARIANTS[variant_name]
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(total_mask)
    tail_color = average_color(source_large.convert("RGB"), (996 * scale, 290 * scale, 1118 * scale, 350 * scale))
    dark = tuple(max(16, int(channel * 0.40)) for channel in tail_color)
    keratin = color_mix(tail_color, (172, 116, 68), 0.46)
    light = color_mix(keratin, (238, 214, 166), 0.26)
    alpha = spec["alpha"]

    hub = scale_poly(spec["hub"], scale)
    draw.polygon(hub, fill=(*color_mix(tail_color, dark, 0.24), int(160 * alpha)))
    mask_draw.polygon(hub, fill=174)
    for idx, (base_a, base_b, tip) in enumerate(spec["spikes"]):
        pts = scale_poly([base_a, base_b, tip], scale)
        tone = tuple(clamp(keratin[i] + idx * 3 - 4, 38, 192) for i in range(3))
        draw.polygon(pts, fill=(*tone, int(230 * alpha)))
        draw.line(pts + [pts[0]], fill=(*dark, int(120 * alpha)), width=max(2, int(0.55 * scale)), joint="curve")
        ridge_start = ((base_a[0] + base_b[0]) * 0.5, (base_a[1] + base_b[1]) * 0.5)
        ridge_end = (tip[0] * 0.78 + base_a[0] * 0.22, tip[1] * 0.78 + base_a[1] * 0.22)
        draw.line(scale_poly([ridge_start, ridge_end], scale), fill=(*light, int(64 * alpha)), width=max(1, int(0.34 * scale)))
        mask_draw.polygon(pts, fill=238)

    # Keep the tail-spike hub from reading as a second head.
    draw.line(scale_poly([(1058, 330), (1096, 330)], scale), fill=(*palette["dark"], 60), width=max(2, int(0.45 * scale)))


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    rng = random.Random(variant["seed"])
    base = Image.open(source).convert("RGB")
    scale = 4
    old_mask = make_existing_plate_mask(base.size, scale)
    cleaned = inpaint_region(base, old_mask)
    large = cleaned.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    source_large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    palette = make_palette(source_large, variant)

    overlay = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    for spec in FAR_PLATES:
        draw_plate(overlay, mask, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(overlay, mask, spec, base.size, scale, variant, palette, False, rng)
    draw_tail_spikes(overlay, mask, source_large, scale, variant["tail"], palette)

    # A very small blur/resharpen blend reduces pasted hard edges without making
    # the plates translucent.
    alpha = overlay.getchannel("A")
    overlay.putalpha(alpha.filter(ImageFilter.GaussianBlur(radius=0.04 * scale)))
    result = Image.alpha_composite(large, overlay).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def crop_plate_band(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    return image.crop((int(w * 0.14), int(h * 0.02), int(w * 0.91), int(h * 0.58)))


def crop_tail(path):
    image = Image.open(path).convert("RGB")
    return image.crop((840, 230, 1152, 430))


def make_contact_sheet(items, output, plate_crop_output, tail_crop_output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    sheets = []
    for crop_fn in (None, crop_plate_band, crop_tail):
        tiles = []
        for path, label in items:
            image = crop_fn(path) if crop_fn else Image.open(path).convert("RGB")
            image.thumbnail((thumb_w, thumb_h))
            tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
            tile.paste(image, ((thumb_w - image.width) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((10, thumb_h + 12), label[:58], fill=(42, 39, 35), font=ImageFont.load_default())
            tiles.append(tile)
        cols = min(2, len(tiles))
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
        for idx, tile in enumerate(tiles):
            sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
        sheets.append(sheet)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheets[0].save(output)
    sheets[1].save(plate_crop_output)
    sheets[2].save(tail_crop_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_individual_plate_lock_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: current relock")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"individual locked plates {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    plate_crop_sheet = out_dir / f"{args.prefix}-plate-crops.png"
    tail_crop_sheet = out_dir / f"{args.prefix}-tail-crops.png"
    make_contact_sheet(items, sheet, plate_crop_sheet, tail_crop_sheet)
    print(sheet)
    print(plate_crop_sheet)
    print(tail_crop_sheet)


if __name__ == "__main__":
    main()
