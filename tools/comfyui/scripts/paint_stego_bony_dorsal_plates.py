import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-strong-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Normalized against the 1152x768 Stegosaurus side-view candidates.
# The count target is 17 visible plates: two staggered rows, broad and separate.
NEAR_PLATES = [
    (0.150, 0.515, 0.030, 0.070, -0.006),
    (0.205, 0.485, 0.042, 0.105, -0.005),
    (0.275, 0.445, 0.052, 0.150, -0.003),
    (0.360, 0.410, 0.066, 0.205, 0.000),
    (0.462, 0.392, 0.078, 0.245, 0.002),
    (0.565, 0.400, 0.074, 0.225, -0.001),
    (0.660, 0.430, 0.060, 0.170, 0.002),
    (0.740, 0.470, 0.046, 0.115, 0.003),
    (0.805, 0.505, 0.032, 0.072, 0.004),
]

FAR_PLATES = [
    (0.178, 0.500, 0.034, 0.086, -0.004),
    (0.240, 0.462, 0.044, 0.125, -0.003),
    (0.318, 0.426, 0.054, 0.170, -0.001),
    (0.412, 0.400, 0.062, 0.215, 0.001),
    (0.515, 0.396, 0.064, 0.225, -0.001),
    (0.615, 0.416, 0.056, 0.180, 0.001),
    (0.700, 0.452, 0.044, 0.128, 0.003),
    (0.772, 0.490, 0.032, 0.082, 0.003),
]

VARIANTS = {
    "v1a": {"height": 1.00, "width": 1.00, "yoff": 0, "opacity": 1.00, "seed": 2026080701},
    "v1b": {"height": 0.94, "width": 1.08, "yoff": 3, "opacity": 0.96, "seed": 2026080702},
    "v1c": {"height": 1.08, "width": 0.94, "yoff": -2, "opacity": 1.00, "seed": 2026080703},
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
        (0.108, 0.535),
        (0.142, 0.430),
        (0.205, 0.310),
        (0.292, 0.205),
        (0.392, 0.105),
        (0.505, 0.070),
        (0.620, 0.110),
        (0.715, 0.235),
        (0.795, 0.390),
        (0.850, 0.520),
        (0.792, 0.550),
        (0.705, 0.500),
        (0.610, 0.462),
        (0.505, 0.445),
        (0.395, 0.448),
        (0.292, 0.472),
        (0.195, 0.510),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.8 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=20)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.92))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 15, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def make_palette(source_large):
    body_mid = average_color(source_large.convert("RGB"), (430 * 4, 320 * 4, 620 * 4, 420 * 4))
    body_dark = tuple(max(24, int(channel * 0.45)) for channel in body_mid)
    body_warm = (
        clamp(int(body_mid[0] * 0.70 + 42), 72, 145),
        clamp(int(body_mid[1] * 0.64 + 36), 62, 128),
        clamp(int(body_mid[2] * 0.56 + 28), 48, 100),
    )
    near_fill = (
        clamp(int(body_warm[0] * 1.12), 78, 158),
        clamp(int(body_warm[1] * 1.04), 66, 138),
        clamp(int(body_warm[2] * 0.96), 50, 108),
    )
    far_fill = tuple(max(40, int(channel * 0.72)) for channel in near_fill)
    outline = tuple(max(20, int(channel * 0.42)) for channel in near_fill)
    rim = tuple(clamp(int(channel * 1.22), 82, 190) for channel in near_fill)
    return {
        "body_dark": body_dark,
        "near_fill": near_fill,
        "far_fill": far_fill,
        "outline": outline,
        "rim": rim,
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
    left_shoulder = 0.50 + asymmetry * 0.05
    right_shoulder = 0.52 - asymmetry * 0.04
    apex_x = cx + lean + width * asymmetry * 0.08
    return [
        (cx - width * 0.38, base_y + height * 0.020),
        (cx - width * left_shoulder, base_y - height * 0.18),
        (cx + lean - width * 0.48, base_y - height * 0.48),
        (cx + lean - width * 0.24, base_y - height * 0.78),
        (apex_x, base_y - height * 1.00),
        (cx + lean + width * 0.26, base_y - height * 0.77),
        (cx + width * right_shoulder, base_y - height * 0.46),
        (cx + width * 0.50, base_y - height * 0.18),
        (cx + width * 0.36, base_y + height * 0.020),
    ]


def draw_socket(layer, size, scale, palette):
    draw = ImageDraw.Draw(layer)
    width, height = size
    back = [
        (0.120, 0.512),
        (0.190, 0.482),
        (0.284, 0.442),
        (0.390, 0.410),
        (0.500, 0.398),
        (0.612, 0.414),
        (0.710, 0.455),
        (0.828, 0.512),
    ]
    points = [(x * width * scale, y * height * scale) for x, y in back]
    draw.line(points, fill=(*palette["body_dark"], 118), width=max(5, int(2.0 * scale)), joint="curve")
    draw.line(points, fill=(*palette["rim"], 42), width=max(2, int(0.7 * scale)), joint="curve")


def draw_plate(draw, mask_draw, spec, size, scale, variant, palette, far_row, rng):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale, variant)
    asymmetry = rng.uniform(-0.55, 0.55)
    points = plate_points(cx, base_y, plate_w, plate_h, lean, asymmetry)

    if far_row:
        fill = (*palette["far_fill"], int(216 * variant["opacity"]))
        outline = (*palette["outline"], int(198 * variant["opacity"]))
        rim = (*palette["rim"], int(54 * variant["opacity"]))
        shadow_alpha = 46
    else:
        fill = (*palette["near_fill"], int(238 * variant["opacity"]))
        outline = (*palette["outline"], int(226 * variant["opacity"]))
        rim = (*palette["rim"], int(76 * variant["opacity"]))
        shadow_alpha = 64

    draw.ellipse(
        (
            cx - plate_w * 0.52,
            base_y - plate_h * 0.035,
            cx + plate_w * 0.52,
            base_y + plate_h * 0.115,
        ),
        fill=(18, 15, 12, shadow_alpha),
    )
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=max(4, int(1.25 * scale)), joint="curve")
    mask_draw.polygon(points, fill=255)

    # Sparse blunt grooves and edge wear. Avoid branching leaf-vein patterns.
    top = base_y - plate_h
    for _ in range(5 if not far_row else 3):
        x = rng.uniform(cx - plate_w * 0.32, cx + plate_w * 0.30)
        y0 = rng.uniform(top + plate_h * 0.20, base_y - plate_h * 0.15)
        y1 = min(base_y - plate_h * 0.08, y0 + rng.uniform(plate_h * 0.12, plate_h * 0.28))
        draw.line(
            [(x, y0), (x + rng.uniform(-plate_w * 0.04, plate_w * 0.04), y1)],
            fill=(*palette["outline"], 44 if not far_row else 34),
            width=max(1, int(0.55 * scale)),
        )

    draw.line(points[1:5], fill=rim, width=max(2, int(0.75 * scale)), joint="curve")


def add_texture(layer, plate_mask, size, scale, seed, palette):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    width, height = size
    tones = [
        palette["outline"],
        palette["near_fill"],
        palette["far_fill"],
        palette["rim"],
        (42, 34, 25),
    ]
    for _ in range(5600):
        x = rng.randrange(int(width * 0.11 * scale), int(width * 0.84 * scale))
        y = rng.randrange(int(height * 0.06 * scale), int(height * 0.54 * scale))
        if plate_mask.getpixel((x, y)) < 24:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(4, 28)
        if rng.random() < 0.30:
            radius = rng.randrange(1, max(2, int(2.5 * scale)))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
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
    cleaned = inpaint_region(base, erase_mask).resize((width * scale, height * scale), Image.Resampling.LANCZOS)
    cleaned = cleaned.convert("RGBA")
    source_large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(source_large)

    layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", cleaned.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(plate_mask)
    rng = random.Random(variant["seed"])

    draw_socket(layer, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(draw, mask_draw, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(draw, mask_draw, spec, base.size, scale, variant, palette, False, rng)

    layer = add_texture(layer, plate_mask, base.size, scale, variant["seed"], palette)
    soft_mask = plate_mask.filter(ImageFilter.GaussianBlur(radius=1.1 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.10 * scale))

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
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)

    cols = min(2, len(tiles))
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
    parser.add_argument("--prefix", default="stego_bony_dorsal_plates_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"bony separated plates {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
