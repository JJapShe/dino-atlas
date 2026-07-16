import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-plate-relock-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"seed": 2026062881, "height": 1.00, "width": 1.00, "warm": 1.00, "tail": "medium"},
    "v1b": {"seed": 2026062882, "height": 0.92, "width": 1.06, "warm": 0.94, "tail": "subtle"},
    "v1c": {"seed": 2026062883, "height": 1.06, "width": 0.96, "warm": 1.06, "tail": "strong"},
}


FAR_PLATES = [
    (0.240, 0.435, 0.030, 0.070, -0.004),
    (0.300, 0.394, 0.038, 0.094, -0.003),
    (0.382, 0.350, 0.048, 0.124, -0.002),
    (0.485, 0.320, 0.056, 0.152, 0.000),
    (0.595, 0.325, 0.054, 0.142, 0.001),
    (0.700, 0.378, 0.044, 0.104, 0.003),
    (0.790, 0.444, 0.034, 0.074, 0.004),
    (0.852, 0.506, 0.024, 0.046, 0.004),
]

NEAR_PLATES = [
    (0.218, 0.458, 0.026, 0.054, -0.004),
    (0.270, 0.420, 0.034, 0.076, -0.003),
    (0.338, 0.378, 0.044, 0.104, -0.002),
    (0.430, 0.335, 0.056, 0.138, -0.001),
    (0.535, 0.312, 0.064, 0.170, 0.000),
    (0.645, 0.342, 0.052, 0.126, 0.002),
    (0.740, 0.404, 0.042, 0.090, 0.003),
    (0.815, 0.470, 0.030, 0.058, 0.004),
]


TAIL_VARIANTS = {
    "subtle": {
        "hub": [(1082, 326), (1104, 321), (1113, 329), (1105, 341), (1083, 339), (1074, 331)],
        "spikes": [
            ((1090, 321), (1102, 324), (1122, 296)),
            ((1102, 324), (1112, 330), (1133, 309)),
            ((1090, 337), (1102, 342), (1123, 368)),
            ((1103, 337), (1113, 342), (1132, 355)),
        ],
        "alpha": 0.88,
    },
    "medium": {
        "hub": [(1078, 323), (1107, 318), (1119, 328), (1108, 345), (1078, 342), (1066, 331)],
        "spikes": [
            ((1090, 318), (1104, 322), (1131, 286)),
            ((1104, 323), (1118, 331), (1144, 305)),
            ((1090, 340), (1105, 348), (1130, 386)),
            ((1105, 338), (1119, 345), (1143, 366)),
        ],
        "alpha": 0.96,
    },
    "strong": {
        "hub": [(1073, 321), (1108, 316), (1123, 328), (1109, 349), (1072, 345), (1057, 330)],
        "spikes": [
            ((1088, 316), (1106, 321), (1136, 280)),
            ((1105, 323), (1122, 332), (1150, 301)),
            ((1088, 342), (1106, 351), (1136, 395)),
            ((1106, 340), (1122, 349), (1150, 372)),
        ],
        "alpha": 1.0,
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


def make_old_plate_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    band = [
        (0.188, 0.475),
        (0.210, 0.385),
        (0.265, 0.292),
        (0.340, 0.220),
        (0.430, 0.144),
        (0.526, 0.090),
        (0.620, 0.124),
        (0.706, 0.230),
        (0.800, 0.370),
        (0.888, 0.535),
        (0.846, 0.560),
        (0.742, 0.488),
        (0.642, 0.438),
        (0.534, 0.418),
        (0.420, 0.428),
        (0.312, 0.460),
        (0.212, 0.505),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.6 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=32)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.96))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 21, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def plate_points(cx, base_y, width, height, lean, asymmetry):
    apex_x = cx + lean + asymmetry * width * 0.07
    shoulder_y = base_y - height * 0.60
    return [
        (cx - width * 0.48, base_y + height * 0.012),
        (cx - width * 0.62, base_y - height * 0.21),
        (cx + lean - width * 0.52, shoulder_y),
        (apex_x - width * 0.20, base_y - height * 0.90),
        (apex_x, base_y - height),
        (apex_x + width * 0.22, base_y - height * 0.90),
        (cx + lean + width * 0.52, shoulder_y),
        (cx + width * 0.62, base_y - height * 0.21),
        (cx + width * 0.48, base_y + height * 0.012),
    ]


def make_palette(source_large, variant):
    plate = average_color(source_large.convert("RGB"), (420 * 4, 170 * 4, 740 * 4, 310 * 4))
    body = average_color(source_large.convert("RGB"), (430 * 4, 355 * 4, 720 * 4, 465 * 4))
    warm = (132, 82, 44)
    base = tuple(
        clamp(int((plate[i] * 0.44 + body[i] * 0.16 + warm[i] * 0.40) * variant["warm"]), 58, 170)
        for i in range(3)
    )
    dark = tuple(max(18, int(channel * 0.44)) for channel in base)
    far = tuple(max(34, int(channel * 0.72)) for channel in base)
    light = (
        clamp(int(base[0] * 1.28 + 8), 70, 206),
        clamp(int(base[1] * 1.18 + 7), 56, 168),
        clamp(int(base[2] * 1.05 + 5), 42, 132),
    )
    return {"base": base, "dark": dark, "far": far, "light": light}


def add_plate_texture(layer, mask, bbox, palette, rng, scale, far_row):
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    x0, y0, x1, y1 = [int(v) for v in bbox]
    tones = [palette["base"], palette["dark"], palette["light"], palette["far"]]
    mask_pix = mask.load()
    count = 420 if far_row else 680
    for _ in range(count):
        x = rng.randrange(max(0, x0), min(layer.width, x1 + 1))
        y = rng.randrange(max(0, y0), min(layer.height, y1 + 1))
        if mask_pix[x, y] < 20:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(7, 30)
        if rng.random() < 0.26:
            radius = rng.choice([1, 1, 2, 3]) * scale / 3
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_plate(layer, total_mask, spec, size, scale, variant, palette, far_row, rng):
    image_w, image_h = size
    cx, base_y, width, height, lean = spec
    cx *= image_w * scale
    base_y *= image_h * scale
    width *= image_w * scale * variant["width"]
    height *= image_h * scale * variant["height"]
    lean *= image_w * scale
    points = plate_points(cx, base_y, width, height, lean, rng.uniform(-0.28, 0.28))

    mask = Image.new("L", layer.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=255)

    plate = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(plate)
    fill_rgb = palette["far"] if far_row else palette["base"]
    fill_alpha = 220 if far_row else 246
    edge_alpha = 178 if far_row else 234
    draw.polygon(points, fill=(*fill_rgb, fill_alpha))
    draw.line(points + [points[0]], fill=(*palette["dark"], edge_alpha), width=max(2, int(0.80 * scale)), joint="curve")
    draw.line(points[2:7], fill=(*palette["light"], 48 if far_row else 64), width=max(1, int(0.36 * scale)), joint="curve")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    plate = add_plate_texture(plate, mask, (min(xs), min(ys), max(xs), max(ys)), palette, rng, scale, far_row)

    base_shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(base_shadow)
    shadow_draw.ellipse(
        (
            cx - width * 0.52,
            base_y - height * 0.035,
            cx + width * 0.52,
            base_y + height * 0.105,
        ),
        fill=(14, 10, 7, 48 if not far_row else 30),
    )
    layer.alpha_composite(base_shadow.filter(ImageFilter.GaussianBlur(radius=1.2 * scale)))
    layer.alpha_composite(plate)
    total_mask.paste(ImageChops.lighter(total_mask, mask))


def draw_socket(layer, size, scale, palette):
    image_w, image_h = size
    points = [
        (0.214, 0.462),
        (0.288, 0.418),
        (0.380, 0.372),
        (0.490, 0.338),
        (0.604, 0.344),
        (0.712, 0.394),
        (0.842, 0.512),
    ]
    draw = ImageDraw.Draw(layer)
    draw.line([(x * image_w * scale, y * image_h * scale) for x, y in points], fill=(*palette["dark"], 156), width=max(4, int(1.35 * scale)), joint="curve")


def scale_poly(points, scale):
    return [(x * scale, y * scale) for x, y in points]


def draw_tail_spikes(layer, total_mask, source_large, scale, variant_name):
    spec = TAIL_VARIANTS[variant_name]
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(total_mask)
    tail_color = average_color(source_large.convert("RGB"), (998 * scale, 292 * scale, 1118 * scale, 350 * scale))
    dark = tuple(max(18, int(channel * 0.42)) for channel in tail_color)
    keratin = (
        clamp(int(tail_color[0] * 0.82 + 34), 58, 182),
        clamp(int(tail_color[1] * 0.76 + 27), 48, 150),
        clamp(int(tail_color[2] * 0.66 + 20), 38, 122),
    )
    highlight = color_mix(keratin, (228, 205, 156), 0.28)
    alpha = spec["alpha"]
    hub = scale_poly(spec["hub"], scale)
    draw.polygon(hub, fill=(*color_mix(tail_color, dark, 0.28), int(172 * alpha)))
    mask_draw.polygon(hub, fill=180)

    for idx, (base_a, base_b, tip) in enumerate(spec["spikes"]):
        pts = scale_poly([base_a, base_b, tip], scale)
        tone = tuple(clamp(keratin[i] + idx * 2 - 3, 36, 190) for i in range(3))
        draw.polygon(pts, fill=(*tone, int(236 * alpha)))
        draw.line(pts + [pts[0]], fill=(*dark, int(130 * alpha)), width=max(2, int(0.55 * scale)), joint="curve")
        ridge_start = ((base_a[0] + base_b[0]) * 0.5, (base_a[1] + base_b[1]) * 0.5)
        ridge_end = (tip[0] * 0.78 + base_a[0] * 0.22, tip[1] * 0.78 + base_a[1] * 0.22)
        draw.line(scale_poly([ridge_start, ridge_end], scale), fill=(*highlight, int(70 * alpha)), width=max(1, int(0.34 * scale)))
        mask_draw.polygon(pts, fill=238)


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    rng = random.Random(variant["seed"])
    base = Image.open(source).convert("RGB")
    scale = 4
    erase_mask = make_old_plate_mask(base.size, scale)
    cleaned = inpaint_region(base, erase_mask)
    large = cleaned.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    source_large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    palette = make_palette(source_large, variant)

    overlay = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw_socket(overlay, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(overlay, mask, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(overlay, mask, spec, base.size, scale, variant, palette, False, rng)
    draw_tail_spikes(overlay, mask, source_large, scale, variant["tail"])

    soft_alpha = overlay.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.16 * scale))
    overlay.putalpha(soft_alpha)
    result = Image.alpha_composite(large, overlay).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def crop_plate_band(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    return image.crop((int(w * 0.14), int(h * 0.04), int(w * 0.91), int(h * 0.58)))


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
    parser.add_argument("--prefix", default="stego_opaque_plate_seed_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: relock candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"opaque plate seed {variant_name}"))
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
