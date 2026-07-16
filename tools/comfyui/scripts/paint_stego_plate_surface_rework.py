import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-locked-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Tuned to the current locked-plate Stegosaurus image. These overlays keep the
# existing body/background and only repaint the plate surfaces away from leaves.
NEAR_PLATES = [
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
    "v1a": {"opacity": 0.78, "warmth": 0.95, "seed": 2026080801},
    "v1b": {"opacity": 0.88, "warmth": 0.88, "seed": 2026080802},
    "v1c": {"opacity": 0.94, "warmth": 1.03, "seed": 2026080803},
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


def plate_points(cx, base_y, width, height, lean, asymmetry):
    apex_x = cx + lean + width * asymmetry * 0.06
    return [
        (cx - width * 0.43, base_y + height * 0.020),
        (cx - width * 0.56, base_y - height * 0.20),
        (cx + lean - width * 0.52, base_y - height * 0.50),
        (cx + lean - width * 0.28, base_y - height * 0.79),
        (apex_x, base_y - height * 1.00),
        (cx + lean + width * 0.30, base_y - height * 0.78),
        (cx + lean + width * 0.55, base_y - height * 0.50),
        (cx + width * 0.58, base_y - height * 0.20),
        (cx + width * 0.43, base_y + height * 0.020),
    ]


def scaled(spec, size, scale):
    cx, base_y, width, height, lean = spec
    image_w, image_h = size
    return (
        cx * image_w * scale,
        base_y * image_h * scale,
        width * image_w * scale,
        height * image_h * scale,
        lean * image_w * scale,
    )


def make_palette(source_large, variant):
    plate_sample = average_color(source_large.convert("RGB"), (420 * 4, 130 * 4, 670 * 4, 285 * 4))
    body_sample = average_color(source_large.convert("RGB"), (420 * 4, 340 * 4, 650 * 4, 430 * 4))
    warm = variant["warmth"]
    base = (
        clamp(int((plate_sample[0] * 0.58 + body_sample[0] * 0.30 + 36) * warm), 64, 138),
        clamp(int((plate_sample[1] * 0.54 + body_sample[1] * 0.28 + 30) * warm), 54, 124),
        clamp(int((plate_sample[2] * 0.46 + body_sample[2] * 0.22 + 22) * warm), 42, 100),
    )
    dark = tuple(max(24, int(channel * 0.42)) for channel in base)
    far = tuple(max(36, int(channel * 0.72)) for channel in base)
    light = (
        clamp(int(base[0] * 1.28), 90, 180),
        clamp(int(base[1] * 1.18), 78, 154),
        clamp(int(base[2] * 1.08), 62, 124),
    )
    return {"base": base, "far": far, "dark": dark, "light": light}


def draw_surface(draw, mask_draw, spec, size, scale, palette, variant, far_row, rng):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale)
    points = plate_points(cx, base_y, plate_w, plate_h, lean, rng.uniform(-0.45, 0.45))
    opacity = variant["opacity"]
    fill_rgb = palette["far"] if far_row else palette["base"]
    fill = (*fill_rgb, int((210 if far_row else 228) * opacity))
    outline = (*palette["dark"], int((188 if far_row else 220) * opacity))
    rim = (*palette["light"], int((42 if far_row else 58) * opacity))

    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=max(3, int(1.10 * scale)), joint="curve")
    mask_draw.polygon(points, fill=255)
    draw.line(points[1:5], fill=rim, width=max(2, int(0.7 * scale)), joint="curve")

    # Vertical wear marks are intentionally sparse and unbranched.
    for _ in range(3 if far_row else 5):
        x = rng.uniform(cx - plate_w * 0.27, cx + plate_w * 0.28)
        y0 = rng.uniform(base_y - plate_h * 0.78, base_y - plate_h * 0.28)
        y1 = min(base_y - plate_h * 0.10, y0 + rng.uniform(plate_h * 0.08, plate_h * 0.22))
        draw.line(
            [(x, y0), (x + rng.uniform(-plate_w * 0.035, plate_w * 0.035), y1)],
            fill=(*palette["dark"], int(38 * opacity)),
            width=max(1, int(0.5 * scale)),
        )


def add_pitted_texture(layer, plate_mask, size, scale, palette, seed, opacity):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    width, height = size
    tones = [palette["dark"], palette["base"], palette["far"], palette["light"], (42, 35, 28)]
    for _ in range(7200):
        x = rng.randrange(int(width * 0.10 * scale), int(width * 0.86 * scale))
        y = rng.randrange(int(height * 0.06 * scale), int(height * 0.54 * scale))
        if plate_mask.getpixel((x, y)) < 24:
            continue
        tone = rng.choice(tones)
        alpha = int(rng.randrange(4, 26) * opacity)
        if rng.random() < 0.34:
            radius = rng.randrange(1, max(2, int(2.4 * scale)))
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
    large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(large, variant)

    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(plate_mask)
    rng = random.Random(variant["seed"])

    for spec in FAR_PLATES:
        draw_surface(draw, mask_draw, spec, base.size, scale, palette, variant, True, rng)
    for spec in NEAR_PLATES:
        draw_surface(draw, mask_draw, spec, base.size, scale, palette, variant, False, rng)

    layer = add_pitted_texture(layer, plate_mask, base.size, scale, palette, variant["seed"], variant["opacity"])
    soft_mask = plate_mask.filter(ImageFilter.GaussianBlur(radius=0.55 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.08 * scale))

    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
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
    parser.add_argument("--prefix", default="stego_plate_surface_rework_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    items = [(source, "source locked-plate candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"matte bony plate surface {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
