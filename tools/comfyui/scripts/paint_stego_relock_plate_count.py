import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-plate-relock-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v2a": {"seed": 2026062864, "plate_alpha": 0.58, "height": 1.00, "width": 1.00, "tail": "medium"},
    "v2b": {"seed": 2026062865, "plate_alpha": 0.50, "height": 0.92, "width": 1.08, "tail": "subtle"},
    "v2c": {"seed": 2026062866, "plate_alpha": 0.66, "height": 1.04, "width": 0.96, "tail": "strong"},
}


# Tuned to the current relock candidate at 1152x768. These add smaller
# alternating plates around the existing large row instead of replacing the
# body, so the route preserves the natural texture while improving count.
FAR_PLATES = [
    (0.285, 0.418, 0.028, 0.070, -0.004),
    (0.358, 0.382, 0.034, 0.086, -0.002),
    (0.455, 0.342, 0.038, 0.104, -0.001),
    (0.565, 0.336, 0.040, 0.110, 0.001),
    (0.675, 0.374, 0.036, 0.092, 0.002),
    (0.765, 0.430, 0.030, 0.070, 0.004),
    (0.832, 0.486, 0.024, 0.052, 0.005),
]

NEAR_PLATES = [
    (0.258, 0.442, 0.030, 0.064, -0.004),
    (0.318, 0.405, 0.036, 0.084, -0.003),
    (0.398, 0.360, 0.044, 0.106, -0.002),
    (0.505, 0.334, 0.050, 0.128, 0.000),
    (0.620, 0.344, 0.048, 0.116, 0.001),
    (0.724, 0.398, 0.038, 0.086, 0.003),
    (0.800, 0.456, 0.030, 0.066, 0.004),
    (0.858, 0.512, 0.022, 0.044, 0.004),
]

TAIL_VARIANTS = {
    "subtle": {
        "hub": [(1082, 326), (1102, 321), (1113, 329), (1104, 340), (1085, 338), (1075, 331)],
        "spikes": [
            ((1090, 322), (1101, 324), (1120, 298)),
            ((1100, 325), (1110, 330), (1133, 310)),
            ((1090, 337), (1102, 341), (1120, 366)),
            ((1102, 336), (1112, 340), (1132, 354)),
        ],
        "alpha": 0.74,
    },
    "medium": {
        "hub": [(1078, 323), (1104, 318), (1118, 328), (1107, 344), (1080, 341), (1067, 331)],
        "spikes": [
            ((1089, 319), (1103, 322), (1129, 289)),
            ((1102, 324), (1116, 331), (1142, 306)),
            ((1089, 340), (1104, 347), (1130, 382)),
            ((1104, 338), (1118, 344), (1141, 364)),
        ],
        "alpha": 0.84,
    },
    "strong": {
        "hub": [(1074, 321), (1106, 316), (1122, 328), (1108, 348), (1074, 344), (1058, 330)],
        "spikes": [
            ((1088, 317), (1105, 321), (1134, 282)),
            ((1103, 323), (1121, 332), (1149, 302)),
            ((1088, 342), (1105, 350), (1134, 392)),
            ((1105, 340), (1121, 348), (1149, 370)),
        ],
        "alpha": 0.92,
    },
}


def clamp(value, low, high):
    return max(low, min(high, value))


def average_color(image, box):
    x0, y0, x1, y1 = box
    x0 = int(clamp(x0, 0, image.width - 1))
    y0 = int(clamp(y0, 0, image.height - 1))
    x1 = int(clamp(x1, x0 + 1, image.width))
    y1 = int(clamp(y1, y0 + 1, image.height))
    return image.crop((x0, y0, x1, y1)).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def color_mix(a, b, ratio):
    return tuple(int(a[i] * (1 - ratio) + b[i] * ratio) for i in range(3))


def scale_point(point, scale):
    return (point[0] * scale, point[1] * scale)


def scale_poly(points, scale):
    return [scale_point(point, scale) for point in points]


def plate_points(cx, base_y, width, height, lean, asymmetry):
    apex_x = cx + lean + asymmetry * width * 0.08
    return [
        (cx - width * 0.48, base_y + height * 0.018),
        (cx - width * 0.62, base_y - height * 0.20),
        (cx + lean - width * 0.50, base_y - height * 0.58),
        (apex_x - width * 0.20, base_y - height * 0.91),
        (apex_x, base_y - height),
        (apex_x + width * 0.22, base_y - height * 0.91),
        (cx + lean + width * 0.52, base_y - height * 0.58),
        (cx + width * 0.62, base_y - height * 0.20),
        (cx + width * 0.48, base_y + height * 0.018),
    ]


def make_palette(source_large):
    plate = average_color(source_large.convert("RGB"), (420 * 4, 178 * 4, 760 * 4, 315 * 4))
    body = average_color(source_large.convert("RGB"), (480 * 4, 365 * 4, 710 * 4, 470 * 4))
    sky = average_color(source_large.convert("RGB"), (360 * 4, 60 * 4, 760 * 4, 160 * 4))
    warm_plate = (142, 92, 48)
    base = tuple(
        clamp(int(plate[i] * 0.52 + body[i] * 0.12 + warm_plate[i] * 0.36), 70, 178)
        for i in range(3)
    )
    dark = tuple(max(20, int(channel * 0.42)) for channel in base)
    far = tuple(max(34, int(channel * 0.72)) for channel in base)
    rim = color_mix(base, sky, 0.18)
    light = tuple(clamp(int(channel * 1.18), 70, 210) for channel in rim)
    return {"base": base, "dark": dark, "far": far, "light": light}


def add_texture(layer, mask, bbox, palette, rng, scale, opacity):
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    x0, y0, x1, y1 = [int(v) for v in bbox]
    tones = [palette["base"], palette["dark"], palette["light"], palette["far"]]
    mask_pix = mask.load()
    for _ in range(520):
        x = rng.randrange(max(0, x0), min(layer.width, x1 + 1))
        y = rng.randrange(max(0, y0), min(layer.height, y1 + 1))
        if mask_pix[x, y] < 16:
            continue
        tone = rng.choice(tones)
        alpha = int(rng.randrange(7, 28) * opacity)
        if rng.random() < 0.18:
            radius = rng.choice([1, 1, 2, 3]) * scale / 3
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_plate(layer, total_mask, spec, base_size, scale, variant, palette, far_row, rng):
    image_w, image_h = base_size
    cx, base_y, width, height, lean = spec
    cx *= image_w * scale
    base_y *= image_h * scale
    width *= image_w * scale * variant["width"]
    height *= image_h * scale * variant["height"]
    lean *= image_w * scale
    points = plate_points(cx, base_y, width, height, lean, rng.uniform(-0.30, 0.30))

    mask = Image.new("L", layer.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=255)

    plate = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(plate)
    fill_rgb = palette["far"] if far_row else palette["base"]
    alpha = int((164 if far_row else 218) * variant["plate_alpha"])
    edge_alpha = int((162 if far_row else 224) * variant["plate_alpha"])
    draw.polygon(points, fill=(*fill_rgb, alpha))
    draw.line(points + [points[0]], fill=(*palette["dark"], edge_alpha), width=max(2, int(0.90 * scale)), joint="curve")
    draw.line(points[2:7], fill=(*palette["light"], int(54 * variant["plate_alpha"])), width=max(1, int(0.46 * scale)), joint="curve")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    plate = add_texture(plate, mask, (min(xs), min(ys), max(xs), max(ys)), palette, rng, scale, 0.8 if far_row else 1.0)
    layer.alpha_composite(plate)
    total_mask.paste(ImageChops.lighter(total_mask, mask))


def draw_socket(layer, base_size, scale, palette):
    image_w, image_h = base_size
    points = [
        (0.236, 0.448),
        (0.318, 0.404),
        (0.414, 0.364),
        (0.520, 0.342),
        (0.632, 0.352),
        (0.734, 0.402),
        (0.858, 0.512),
    ]
    draw = ImageDraw.Draw(layer)
    draw.line([(x * image_w * scale, y * image_h * scale) for x, y in points], fill=(*palette["dark"], 112), width=max(4, int(1.2 * scale)), joint="curve")


def draw_tail_spikes(layer, total_mask, source_large, scale, variant_name):
    spec = TAIL_VARIANTS[variant_name]
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(total_mask)
    tail_color = average_color(source_large.convert("RGB"), (1008 * scale, 292 * scale, 1120 * scale, 350 * scale))
    dark = tuple(max(18, int(channel * 0.42)) for channel in tail_color)
    keratin = (
        clamp(int(tail_color[0] * 0.86 + 30), 58, 180),
        clamp(int(tail_color[1] * 0.78 + 26), 48, 150),
        clamp(int(tail_color[2] * 0.68 + 20), 38, 122),
    )
    highlight = color_mix(keratin, (230, 207, 160), 0.30)
    alpha = spec["alpha"]

    hub = scale_poly(spec["hub"], scale)
    draw.polygon(hub, fill=(*color_mix(tail_color, dark, 0.22), int(146 * alpha)))
    mask_draw.polygon(hub, fill=170)
    for idx, (base_a, base_b, tip) in enumerate(spec["spikes"]):
        pts = scale_poly([base_a, base_b, tip], scale)
        tone = tuple(clamp(keratin[i] + idx * 3 - 4, 32, 190) for i in range(3))
        draw.polygon(pts, fill=(*tone, int(218 * alpha)))
        draw.line(pts + [pts[0]], fill=(*dark, int(118 * alpha)), width=max(2, int(0.55 * scale)), joint="curve")
        ridge_start = ((base_a[0] + base_b[0]) * 0.5, (base_a[1] + base_b[1]) * 0.5)
        ridge_end = (tip[0] * 0.78 + base_a[0] * 0.22, tip[1] * 0.78 + base_a[1] * 0.22)
        draw.line(scale_poly([ridge_start, ridge_end], scale), fill=(*highlight, int(64 * alpha)), width=max(1, int(0.34 * scale)))
        mask_draw.polygon(pts, fill=235)


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    rng = random.Random(variant["seed"])
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    palette = make_palette(large)

    overlay = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw_socket(overlay, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(overlay, mask, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(overlay, mask, spec, base.size, scale, variant, palette, False, rng)
    draw_tail_spikes(overlay, mask, large, scale, variant["tail"])

    soft_alpha = overlay.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.18 * scale))
    overlay.putalpha(soft_alpha)
    result = Image.alpha_composite(large, overlay).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def crop_plate_band(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    return image.crop((int(w * 0.16), int(h * 0.03), int(w * 0.92), int(h * 0.57)))


def crop_tail(path):
    image = Image.open(path).convert("RGB")
    return image.crop((850, 235, 1152, 430))


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
    parser.add_argument("--prefix", default="stego_relock_plate_count_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: relock candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"plate-count plus thagomizer {variant_name}"))
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
