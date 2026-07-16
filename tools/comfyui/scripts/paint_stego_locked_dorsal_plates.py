import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-natural-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Coordinates are tuned for the 1152x768 side-view Stegosaurus candidates.
# The locked gate favors clearly separated alternating plates over full realism.
NEAR_PLATES = [
    # cx, base_y, width, height, lean
    (0.160, 0.507, 0.036, 0.072, -0.004),
    (0.215, 0.465, 0.046, 0.105, -0.004),
    (0.285, 0.425, 0.058, 0.148, -0.002),
    (0.370, 0.397, 0.072, 0.205, 0.000),
    (0.472, 0.385, 0.082, 0.248, 0.002),
    (0.575, 0.397, 0.078, 0.225, -0.002),
    (0.668, 0.430, 0.064, 0.165, 0.002),
    (0.744, 0.468, 0.050, 0.112, 0.003),
    (0.807, 0.500, 0.036, 0.070, 0.003),
]

FAR_PLATES = [
    (0.188, 0.485, 0.038, 0.090, -0.004),
    (0.250, 0.444, 0.048, 0.126, -0.003),
    (0.326, 0.407, 0.058, 0.172, -0.001),
    (0.420, 0.389, 0.066, 0.218, 0.001),
    (0.525, 0.390, 0.068, 0.230, -0.001),
    (0.624, 0.414, 0.058, 0.178, 0.001),
    (0.707, 0.452, 0.046, 0.128, 0.003),
    (0.775, 0.488, 0.034, 0.082, 0.003),
]

VARIANTS = {
    "v1a": {"height": 0.96, "width": 1.00, "yoff": 0, "opacity": 1.00, "seed": 2026080101},
    "v1b": {"height": 1.04, "width": 0.96, "yoff": 2, "opacity": 0.96, "seed": 2026080102},
    "v1c": {"height": 0.90, "width": 1.08, "yoff": -2, "opacity": 1.00, "seed": 2026080103},
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


def make_old_plate_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)

    band = [
        (0.122, 0.515),
        (0.150, 0.430),
        (0.205, 0.320),
        (0.285, 0.232),
        (0.390, 0.145),
        (0.500, 0.108),
        (0.612, 0.142),
        (0.704, 0.245),
        (0.775, 0.372),
        (0.835, 0.502),
        (0.790, 0.518),
        (0.705, 0.478),
        (0.610, 0.438),
        (0.510, 0.416),
        (0.400, 0.417),
        (0.290, 0.438),
        (0.200, 0.474),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.6 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: min(224, int(p * 0.92)))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 20 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 17, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def plate_points(cx, base_y, width, height, lean):
    return [
        (cx - width * 0.43, base_y + height * 0.025),
        (cx - width * 0.58, base_y - height * 0.20),
        (cx + lean - width * 0.54, base_y - height * 0.50),
        (cx + lean - width * 0.30, base_y - height * 0.78),
        (cx + lean - width * 0.04, base_y - height * 1.00),
        (cx + lean + width * 0.27, base_y - height * 0.80),
        (cx + lean + width * 0.55, base_y - height * 0.52),
        (cx + width * 0.58, base_y - height * 0.21),
        (cx + width * 0.43, base_y + height * 0.025),
    ]


def scaled(spec, size, scale, variant):
    cx, base_y, width, height, lean = spec
    w, h = size
    return (
        cx * w * scale,
        base_y * h * scale + variant["yoff"] * scale,
        width * variant["width"] * w * scale,
        height * variant["height"] * h * scale,
        lean * w * scale,
    )


def draw_back_attachment(layer, size, scale, body_dark):
    draw = ImageDraw.Draw(layer)
    width, height = size
    back = [
        (0.130, 0.500),
        (0.195, 0.466),
        (0.285, 0.425),
        (0.395, 0.395),
        (0.505, 0.388),
        (0.610, 0.407),
        (0.710, 0.452),
        (0.835, 0.505),
    ]
    points = [(x * width * scale, y * height * scale) for x, y in back]
    draw.line(points, fill=(*body_dark, 132), width=max(5, int(2.1 * scale)), joint="curve")
    draw.line(points, fill=(218, 196, 144, 46), width=max(2, int(0.8 * scale)), joint="curve")


def draw_single_plate(draw, mask_draw, spec, size, scale, variant, palette, far_row):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale, variant)
    points = plate_points(cx, base_y, plate_w, plate_h, lean)
    if far_row:
        fill = (*palette["far_fill"], int(205 * variant["opacity"]))
        outline = (*palette["outline"], int(184 * variant["opacity"]))
        ridge = (*palette["ridge"], int(92 * variant["opacity"]))
        highlight = (*palette["highlight"], int(48 * variant["opacity"]))
    else:
        fill = (*palette["near_fill"], int(232 * variant["opacity"]))
        outline = (*palette["outline"], int(218 * variant["opacity"]))
        ridge = (*palette["ridge"], int(118 * variant["opacity"]))
        highlight = (*palette["highlight"], int(68 * variant["opacity"]))

    base_shadow = (
        cx - plate_w * 0.50,
        base_y - plate_h * 0.05,
        cx + plate_w * 0.50,
        base_y + plate_h * 0.11,
    )
    draw.ellipse(base_shadow, fill=(28, 23, 17, 58 if not far_row else 42))
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=max(3, int(1.05 * scale)), joint="curve")
    mask_draw.polygon(points, fill=255)

    center_top = (cx + lean * 0.45, base_y - plate_h * 0.82)
    center_base = (cx + lean * 0.10, base_y - plate_h * 0.035)
    draw.line([center_base, center_top], fill=ridge, width=max(2, int(0.8 * scale)))
    for frac in (0.25, 0.42, 0.59, 0.74):
        left = (cx - plate_w * (0.36 - frac * 0.12), base_y - plate_h * frac)
        right = (cx + plate_w * (0.38 - frac * 0.12), base_y - plate_h * frac)
        mid = (cx + lean * 0.24, base_y - plate_h * (frac + 0.08))
        draw.line([left, mid], fill=(*palette["ridge"], 52), width=max(1, int(0.55 * scale)))
        draw.line([right, mid], fill=(*palette["ridge"], 47), width=max(1, int(0.55 * scale)))

    draw.line(points[2:6], fill=highlight, width=max(2, int(0.8 * scale)), joint="curve")


def add_plate_texture(layer, plate_mask, size, scale, seed, palette):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    width, height = size
    for _ in range(5000):
        x = rng.randrange(int(width * 0.12 * scale), int(width * 0.84 * scale))
        y = rng.randrange(int(height * 0.08 * scale), int(height * 0.54 * scale))
        if plate_mask.getpixel((x, y)) < 24:
            continue
        tone = rng.choice(
            [
                palette["outline"],
                palette["ridge"],
                palette["near_fill"],
                palette["far_fill"],
                palette["highlight"],
            ]
        )
        alpha = rng.randrange(4, 25)
        if rng.random() < 0.22:
            radius = rng.randrange(1, max(2, int(2.2 * scale)))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            draw.point((x, y), fill=(*tone, alpha))

    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), plate_mask))
    return Image.alpha_composite(layer, texture)


def make_palette(source_large):
    body_mid = average_color(source_large.convert("RGB"), (430 * 4, 305 * 4, 610 * 4, 380 * 4))
    body_dark = tuple(max(24, int(channel * 0.50)) for channel in body_mid)
    near_fill = (
        clamp(int(body_mid[0] * 0.72 + 46), 70, 146),
        clamp(int(body_mid[1] * 0.68 + 38), 62, 132),
        clamp(int(body_mid[2] * 0.62 + 28), 48, 104),
    )
    far_fill = tuple(max(42, int(channel * 0.74)) for channel in near_fill)
    outline = tuple(max(24, int(channel * 0.45)) for channel in near_fill)
    ridge = tuple(max(38, int(channel * 0.58)) for channel in near_fill)
    highlight = (
        clamp(int(near_fill[0] * 1.35), 105, 204),
        clamp(int(near_fill[1] * 1.26), 92, 180),
        clamp(int(near_fill[2] * 1.10), 70, 140),
    )
    return {
        "body_dark": body_dark,
        "near_fill": near_fill,
        "far_fill": far_fill,
        "outline": outline,
        "ridge": ridge,
        "highlight": highlight,
    }


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    width, height = base.size
    scale = 4
    erase_mask = make_old_plate_mask(base.size, scale)
    cleaned = inpaint_region(base, erase_mask).resize((width * scale, height * scale), Image.Resampling.LANCZOS)
    cleaned = cleaned.convert("RGBA")
    source_large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(source_large)

    layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", cleaned.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(plate_mask)

    draw_back_attachment(layer, base.size, scale, palette["body_dark"])
    for spec in FAR_PLATES:
        draw_single_plate(draw, mask_draw, spec, base.size, scale, variant, palette, True)
    for spec in NEAR_PLATES:
        draw_single_plate(draw, mask_draw, spec, base.size, scale, variant, palette, False)

    layer = add_plate_texture(layer, plate_mask, base.size, scale, variant["seed"], palette)
    soft_mask = plate_mask.filter(ImageFilter.GaussianBlur(radius=1.7))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.26))

    composite = Image.alpha_composite(cleaned, layer)
    result = composite.resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    plate_mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(42, 39, 35), font=ImageFont.load_default())
        tiles.append(tile)

    cols = min(3, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_locked_dorsal_plates_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "previous natural plate candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"locked alternating plates {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
