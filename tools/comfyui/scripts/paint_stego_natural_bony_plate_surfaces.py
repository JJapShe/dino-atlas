import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-separated-plates-refine-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Tuned for the current 1152x768 separated-plate Stegosaurus candidate.
# This pass keeps the body/background and repaints only plate surfaces so they
# read as rough bony scutes rather than leaf-veined fins or cardboard overlays.
NEAR_PLATES = [
    (0.126, 0.520, 0.030, 0.056, -0.004),
    (0.168, 0.488, 0.040, 0.085, -0.004),
    (0.222, 0.450, 0.050, 0.122, -0.003),
    (0.288, 0.410, 0.060, 0.170, -0.002),
    (0.365, 0.383, 0.072, 0.220, 0.000),
    (0.450, 0.365, 0.078, 0.252, 0.001),
    (0.535, 0.365, 0.078, 0.260, -0.001),
    (0.620, 0.382, 0.070, 0.220, 0.002),
    (0.696, 0.420, 0.060, 0.158, 0.003),
    (0.758, 0.463, 0.048, 0.110, 0.004),
    (0.810, 0.505, 0.034, 0.070, 0.004),
]

VARIANTS = {
    "v1a": {"opacity": 0.42, "edge": 0.48, "texture": 0.65, "seed": 2026062311},
    "v1b": {"opacity": 0.54, "edge": 0.58, "texture": 0.85, "seed": 2026062312},
    "v1c": {"opacity": 0.64, "edge": 0.66, "texture": 0.95, "seed": 2026062313},
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


def scaled(spec, size, scale):
    cx, base_y, width, height, lean = spec
    w, h = size
    return cx * w * scale, base_y * h * scale, width * w * scale, height * h * scale, lean * w * scale


def plate_points(cx, base_y, width, height, lean, asymmetry):
    apex = cx + lean + width * asymmetry * 0.08
    shoulder_y = base_y - height * 0.58
    lower_y = base_y - height * 0.20
    return [
        (cx - width * 0.43, base_y + height * 0.018),
        (cx - width * 0.56, lower_y),
        (cx + lean - width * 0.50, shoulder_y),
        (apex - width * 0.20, base_y - height * 0.88),
        (apex, base_y - height),
        (apex + width * 0.20, base_y - height * 0.88),
        (cx + lean + width * 0.51, shoulder_y),
        (cx + width * 0.56, lower_y),
        (cx + width * 0.43, base_y + height * 0.018),
    ]


def make_palette(source_large):
    plate_mid = average_color(source_large.convert("RGB"), (420 * 4, 115 * 4, 690 * 4, 310 * 4))
    body_mid = average_color(source_large.convert("RGB"), (430 * 4, 315 * 4, 670 * 4, 430 * 4))
    sky_mid = average_color(source_large.convert("RGB"), (420 * 4, 55 * 4, 720 * 4, 145 * 4))
    base = (
        clamp(int(plate_mid[0] * 0.48 + body_mid[0] * 0.28 + 44), 68, 132),
        clamp(int(plate_mid[1] * 0.46 + body_mid[1] * 0.25 + 36), 58, 118),
        clamp(int(plate_mid[2] * 0.42 + body_mid[2] * 0.22 + 28), 44, 96),
    )
    far = tuple(max(36, int(channel * 0.72)) for channel in base)
    shadow = tuple(max(18, int(channel * 0.42)) for channel in base)
    highlight = (
        clamp(int(base[0] * 1.28 + sky_mid[0] * 0.05), 86, 168),
        clamp(int(base[1] * 1.20 + sky_mid[1] * 0.04), 76, 150),
        clamp(int(base[2] * 1.08 + sky_mid[2] * 0.04), 58, 124),
    )
    return {"base": base, "far": far, "shadow": shadow, "highlight": highlight}


def existing_plate_clip(source_large, scale):
    width, height = source_large.size
    clip = Image.new("L", source_large.size, 0)
    pixels = source_large.convert("RGB").load()
    clip_pixels = clip.load()

    # Hand-fit back line: only repaint pixels above the body ridge and in the
    # old plate row. This prevents ghost plates appearing in open sky/water.
    back = [
        (0.105, 0.540),
        (0.160, 0.505),
        (0.230, 0.468),
        (0.320, 0.430),
        (0.430, 0.395),
        (0.540, 0.390),
        (0.650, 0.420),
        (0.755, 0.472),
        (0.845, 0.528),
    ]

    def back_y(nx):
        for (x0, y0), (x1, y1) in zip(back, back[1:]):
            if x0 <= nx <= x1:
                t = (nx - x0) / max(1e-6, x1 - x0)
                return y0 * (1 - t) + y1 * t
        return back[0][1] if nx < back[0][0] else back[-1][1]

    for y in range(int(height * 0.055), int(height * 0.545)):
        ny = y / height
        for x in range(int(width * 0.095), int(width * 0.870)):
            nx = x / width
            if ny > back_y(nx) + 0.012:
                continue
            r, g, b = pixels[x, y]
            # Sky/water is blue-cyan; plate surfaces are muted brown/gray.
            brown_plate = r > 42 and g > 36 and b < 122 and b < r + 22 and abs(r - g) < 56
            dark_plate = r > 34 and g > 30 and b < 100 and (r + g) > b * 1.35
            if brown_plate or dark_plate:
                clip_pixels[x, y] = 255
    return clip.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(radius=0.35 * scale))


def draw_plate(layer, mask, spec, size, scale, palette, variant, clip, rng):
    cx, base_y, width, height, lean = scaled(spec, size, scale)
    points = plate_points(cx, base_y, width, height, lean, rng.uniform(-0.34, 0.34))
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    x0, x1 = int(min(xs)), int(max(xs))
    y0, y1 = int(min(ys)), int(max(ys))

    local_mask = Image.new("L", layer.size, 0)
    mask_draw = ImageDraw.Draw(local_mask)
    alpha = int(190 * variant["opacity"])
    mask_draw.polygon(points, fill=alpha)
    local_mask = ImageChops.multiply(local_mask, clip)

    surface = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    pixels = surface.load()
    mask_pixels = local_mask.load()
    fill = palette["base"]
    for y in range(max(0, y0), min(layer.size[1], y1 + 1)):
        vertical = (y - y0) / max(1, y1 - y0)
        for x in range(max(0, x0), min(layer.size[0], x1 + 1)):
            a = mask_pixels[x, y]
            if not a:
                continue
            horizontal = (x - x0) / max(1, x1 - x0)
            light = (1.0 - vertical) * 0.22 + (0.55 - abs(horizontal - 0.45)) * 0.08
            shade = vertical * 0.32 + horizontal * 0.06
            channels = []
            for idx, channel in enumerate(fill):
                value = channel * (1.0 - shade) + palette["shadow"][idx] * shade + palette["highlight"][idx] * light
                channels.append(clamp(int(value), 0, 255))
            pixels[x, y] = (*channels, a)

    draw = ImageDraw.Draw(surface)
    edge_alpha = int(112 * variant["edge"])
    rim_alpha = int(34 * variant["edge"])
    draw.line(points + [points[0]], fill=(*palette["shadow"], edge_alpha), width=max(3, int(0.88 * scale)), joint="curve")
    draw.line(points[2:7], fill=(*palette["highlight"], rim_alpha), width=max(2, int(0.52 * scale)), joint="curve")

    for _ in range(int(26 * variant["texture"])):
        px = rng.uniform(x0, x1)
        py = rng.uniform(y0, y1)
        ix, iy = int(px), int(py)
        if not (0 <= ix < layer.size[0] and 0 <= iy < layer.size[1]) or mask_pixels[ix, iy] < 8:
            continue
        radius = rng.uniform(0.45 * scale, 1.8 * scale)
        tone = rng.choice([palette["shadow"], palette["base"], palette["highlight"]])
        dot_alpha = rng.randrange(8, 24)
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(*tone, dot_alpha))

    base_shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(base_shadow)
    shadow_draw.ellipse(
        (
            cx - width * 0.48,
            base_y - height * 0.040,
            cx + width * 0.48,
            base_y + height * 0.100,
        ),
        fill=(12, 10, 8, 28),
    )
    layer.alpha_composite(base_shadow.filter(ImageFilter.GaussianBlur(radius=0.65 * scale)))
    layer.alpha_composite(surface.filter(ImageFilter.GaussianBlur(radius=0.05 * scale)))
    mask.paste(ImageChops.lighter(mask, local_mask))


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    width, height = base.size
    scale = 4
    large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(large)
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    clip = existing_plate_clip(large, scale)
    rng = random.Random(variant["seed"])

    for spec in NEAR_PLATES:
        draw_plate(layer, mask, spec, base.size, scale, palette, variant, clip, rng)

    # A very soft blend keeps the original lighting while suppressing the leaf-vein read.
    soft_alpha = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.16 * scale))
    layer.putalpha(soft_alpha)
    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


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
    parser.add_argument("--prefix", default="stego_natural_bony_plate_surfaces_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: separated but leaf/panel-like plates")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"natural bony plate surface {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
