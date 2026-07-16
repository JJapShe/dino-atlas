import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-plate-lock-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Tuned for the current plate-lock Stegosaurus candidate. The goal is not a
# final paleoart repaint; it is a stricter local target with angular, countable
# bony slabs instead of rounded flower-petal plates.
NEAR_PLATES = [
    # cx, base_y, width, height, lean
    (0.245, 0.442, 0.040, 0.070, -0.004),
    (0.300, 0.412, 0.050, 0.110, -0.003),
    (0.365, 0.382, 0.062, 0.152, -0.002),
    (0.438, 0.354, 0.078, 0.205, -0.001),
    (0.518, 0.336, 0.088, 0.245, 0.000),
    (0.600, 0.344, 0.084, 0.225, 0.002),
    (0.678, 0.376, 0.070, 0.165, 0.003),
    (0.742, 0.412, 0.054, 0.110, 0.004),
    (0.795, 0.442, 0.038, 0.070, 0.004),
]

FAR_PLATES = [
    (0.272, 0.430, 0.038, 0.085, -0.004),
    (0.330, 0.400, 0.048, 0.125, -0.003),
    (0.398, 0.368, 0.058, 0.170, -0.001),
    (0.475, 0.346, 0.070, 0.215, 0.000),
    (0.558, 0.344, 0.072, 0.225, 0.001),
    (0.638, 0.366, 0.062, 0.175, 0.002),
    (0.708, 0.398, 0.050, 0.125, 0.003),
    (0.768, 0.430, 0.036, 0.082, 0.004),
]

VARIANTS = {
    "v1a": {"height": 0.98, "width": 1.04, "yoff": 0, "edge": 1.00, "seed": 2026062301},
    "v1b": {"height": 0.88, "width": 1.16, "yoff": 7, "edge": 0.92, "seed": 2026062302},
    "v1c": {"height": 1.03, "width": 0.96, "yoff": -4, "edge": 1.08, "seed": 2026062303},
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


def old_plate_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    band = [
        (0.205, 0.472),
        (0.230, 0.374),
        (0.282, 0.278),
        (0.360, 0.190),
        (0.458, 0.114),
        (0.542, 0.078),
        (0.632, 0.120),
        (0.705, 0.220),
        (0.775, 0.350),
        (0.834, 0.472),
        (0.790, 0.492),
        (0.704, 0.444),
        (0.608, 0.410),
        (0.512, 0.396),
        (0.420, 0.405),
        (0.330, 0.430),
        (0.250, 0.462),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.6 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=20)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.88))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 17, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def make_palette(source_large):
    plate_mid = average_color(source_large.convert("RGB"), (470 * 4, 140 * 4, 650 * 4, 300 * 4))
    body_mid = average_color(source_large.convert("RGB"), (440 * 4, 330 * 4, 680 * 4, 440 * 4))
    sky_mid = average_color(source_large.convert("RGB"), (360 * 4, 80 * 4, 740 * 4, 160 * 4))

    near_fill = (
        clamp(int(plate_mid[0] * 0.80 + body_mid[0] * 0.18), 70, 140),
        clamp(int(plate_mid[1] * 0.80 + body_mid[1] * 0.16), 62, 128),
        clamp(int(plate_mid[2] * 0.78 + body_mid[2] * 0.14), 48, 110),
    )
    far_fill = tuple(max(42, int(channel * 0.76)) for channel in near_fill)
    edge = tuple(max(22, int(channel * 0.46)) for channel in near_fill)
    shadow = tuple(max(18, int(channel * 0.35)) for channel in near_fill)
    highlight = (
        clamp(int(near_fill[0] * 1.22 + sky_mid[0] * 0.08), 92, 172),
        clamp(int(near_fill[1] * 1.18 + sky_mid[1] * 0.06), 82, 160),
        clamp(int(near_fill[2] * 1.10 + sky_mid[2] * 0.05), 64, 134),
    )
    return {
        "near_fill": near_fill,
        "far_fill": far_fill,
        "edge": edge,
        "shadow": shadow,
        "highlight": highlight,
    }


def scaled(spec, size, scale, variant):
    cx, base_y, width, height, lean = spec
    image_w, image_h = size
    return (
        cx * image_w * scale,
        base_y * image_h * scale + variant["yoff"] * scale,
        width * variant["width"] * image_w * scale,
        height * variant["height"] * image_h * scale,
        lean * image_w * scale,
    )


def plate_points(cx, base_y, width, height, lean, asymmetry):
    top_x = cx + lean + asymmetry * width * 0.08
    shoulder_left = width * (0.50 + asymmetry * 0.05)
    shoulder_right = width * (0.50 - asymmetry * 0.05)
    top_half = width * 0.105
    return [
        (cx - width * 0.48, base_y + height * 0.020),
        (cx - width * 0.59, base_y - height * 0.155),
        (cx + lean * 0.15 - shoulder_left, base_y - height * 0.510),
        (top_x - width * 0.280, base_y - height * 0.835),
        (top_x - top_half, base_y - height * 0.985),
        (top_x + top_half, base_y - height * 0.992),
        (top_x + width * 0.290, base_y - height * 0.835),
        (cx + lean * 0.15 + shoulder_right, base_y - height * 0.510),
        (cx + width * 0.590, base_y - height * 0.155),
        (cx + width * 0.480, base_y + height * 0.020),
    ]


def draw_back_socket(layer, size, scale, palette):
    width, height = size
    draw = ImageDraw.Draw(layer)
    points = [
        (0.220, 0.445),
        (0.292, 0.413),
        (0.378, 0.382),
        (0.480, 0.354),
        (0.582, 0.356),
        (0.680, 0.388),
        (0.782, 0.438),
    ]
    pixel_points = [(x * width * scale, y * height * scale) for x, y in points]
    draw.line(pixel_points, fill=(*palette["shadow"], 138), width=max(6, int(2.1 * scale)), joint="curve")
    draw.line(pixel_points, fill=(*palette["highlight"], 34), width=max(2, int(0.65 * scale)), joint="curve")


def draw_plate(draw, mask_draw, spec, size, scale, variant, palette, far_row, rng):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale, variant)
    points = plate_points(cx, base_y, plate_w, plate_h, lean, rng.uniform(-0.38, 0.38))
    if far_row:
        fill = (*palette["far_fill"], 214)
        outline = (*palette["edge"], int(170 * variant["edge"]))
        high = (*palette["highlight"], 36)
        low = (*palette["shadow"], 42)
    else:
        fill = (*palette["near_fill"], 242)
        outline = (*palette["edge"], int(224 * variant["edge"]))
        high = (*palette["highlight"], 56)
        low = (*palette["shadow"], 58)

    draw.ellipse(
        (cx - plate_w * 0.47, base_y - plate_h * 0.02, cx + plate_w * 0.47, base_y + plate_h * 0.11),
        fill=(*palette["shadow"], 44 if far_row else 58),
    )
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=255)

    lower = [
        points[0],
        points[1],
        (cx + lean - plate_w * 0.33, base_y - plate_h * 0.35),
        (cx + lean + plate_w * 0.36, base_y - plate_h * 0.35),
        points[8],
        points[9],
    ]
    draw.polygon(lower, fill=low)
    draw.line(points + [points[0]], fill=outline, width=max(3, int(1.05 * scale)), joint="curve")
    draw.line(points[2:8], fill=high, width=max(1, int(0.55 * scale)), joint="curve")
    draw.line((points[0], points[9]), fill=(*palette["shadow"], 155), width=max(3, int(1.15 * scale)))

    for _ in range(9 if far_row else 14):
        px = rng.uniform(cx - plate_w * 0.31, cx + plate_w * 0.31)
        py = rng.uniform(base_y - plate_h * 0.76, base_y - plate_h * 0.20)
        rr = rng.uniform(0.45 * scale, 1.35 * scale)
        tone = rng.choice([palette["edge"], palette["shadow"], palette["highlight"], palette["near_fill"]])
        draw.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(*tone, rng.randrange(14, 36)))


def add_plate_grain(layer, plate_mask, size, scale, seed, palette):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    width, height = size
    tones = [palette["edge"], palette["shadow"], palette["near_fill"], palette["far_fill"], palette["highlight"]]
    for _ in range(3600):
        x = rng.randrange(int(width * 0.20 * scale), int(width * 0.84 * scale))
        y = rng.randrange(int(height * 0.08 * scale), int(height * 0.50 * scale))
        if plate_mask.getpixel((x, y)) < 24:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(3, 20)
        if rng.random() < 0.16:
            r = rng.uniform(0.7 * scale, 1.8 * scale)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*tone, alpha))
        else:
            draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), plate_mask))
    return Image.alpha_composite(layer, texture)


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    width, height = base.size
    scale = 4
    erase_mask = old_plate_mask(base.size, scale)
    cleaned = inpaint_region(base, erase_mask).resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    source_large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(source_large)

    layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", cleaned.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(plate_mask)
    rng = random.Random(variant["seed"])

    draw_back_socket(layer, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(draw, mask_draw, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(draw, mask_draw, spec, base.size, scale, variant, palette, False, rng)

    layer = add_plate_grain(layer, plate_mask, base.size, scale, variant["seed"], palette)
    alpha = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.15 * scale))
    layer.putalpha(alpha)
    result = Image.alpha_composite(cleaned, layer)
    result = result.filter(ImageFilter.GaussianBlur(radius=0.04 * scale))
    result = result.resize(base.size, Image.Resampling.LANCZOS).convert("RGB")

    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    plate_mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def crop_plate_band(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    return image.crop((int(w * 0.16), int(h * 0.06), int(w * 0.86), int(h * 0.55)))


def make_contact_sheet(items, output, crop=False):
    thumb_w = 384
    thumb_h = 190 if crop else 256
    label_h = 42
    tiles = []
    for path, label in items:
        image = crop_plate_band(path) if crop else Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)
    cols = min(2 if not crop else len(tiles), len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_platelock_angular_slabs_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: rounded plate-lock candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"angular slab plates {variant_name}"))

    sheet_output = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_output = out_dir / f"{args.prefix}-plate-crops.png"
    make_contact_sheet(items, sheet_output, crop=False)
    make_contact_sheet(items, crop_output, crop=True)
    print(sheet_output)
    print(crop_output)


if __name__ == "__main__":
    main()
