import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-strong-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Gap center, upper valley y, top width, base width, curve lean.
SEAMS = [
    (0.202, 0.405, 0.008, 0.012, -0.006),
    (0.246, 0.330, 0.010, 0.014, -0.005),
    (0.294, 0.265, 0.011, 0.015, -0.003),
    (0.345, 0.215, 0.012, 0.016, -0.002),
    (0.398, 0.168, 0.012, 0.017, 0.000),
    (0.455, 0.135, 0.013, 0.017, 0.001),
    (0.515, 0.142, 0.013, 0.017, 0.001),
    (0.575, 0.188, 0.012, 0.016, 0.002),
    (0.634, 0.255, 0.011, 0.015, 0.003),
    (0.690, 0.332, 0.010, 0.014, 0.004),
    (0.742, 0.405, 0.009, 0.012, 0.004),
    (0.790, 0.462, 0.007, 0.010, 0.004),
]

BACK_CURVE = [
    (0.150, 0.510),
    (0.210, 0.476),
    (0.285, 0.438),
    (0.380, 0.405),
    (0.490, 0.392),
    (0.605, 0.414),
    (0.715, 0.466),
    (0.835, 0.520),
]

VARIANTS = {
    "v1a": {"width": 0.68, "depth": 0.74, "feather": 2.2, "edge": 0.48, "seed": 2026081618},
    "v1b": {"width": 0.82, "depth": 0.84, "feather": 2.2, "edge": 0.60, "seed": 2026081619},
    "v1c": {"width": 0.96, "depth": 0.92, "feather": 2.0, "edge": 0.70, "seed": 2026081620},
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


def interpolate_back_y(x):
    for (x0, y0), (x1, y1) in zip(BACK_CURVE, BACK_CURVE[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / max(1e-6, x1 - x0)
            return y0 * (1 - t) + y1 * t
    return BACK_CURVE[0][1] if x < BACK_CURVE[0][0] else BACK_CURVE[-1][1]


def old_plate_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    band = [
        (0.112, 0.545),
        (0.132, 0.430),
        (0.190, 0.300),
        (0.292, 0.185),
        (0.415, 0.078),
        (0.520, 0.055),
        (0.632, 0.092),
        (0.732, 0.230),
        (0.812, 0.390),
        (0.866, 0.535),
        (0.800, 0.558),
        (0.705, 0.506),
        (0.606, 0.464),
        (0.498, 0.450),
        (0.386, 0.462),
        (0.282, 0.490),
        (0.190, 0.528),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=2.0 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=24)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.94))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 17, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def synthesize_gap_background(source, scale, seed):
    rng = random.Random(seed)
    width, height = source.size
    top = average_color(source, (0, 12, width, 72))
    mid = average_color(source, (width * 0.78, height * 0.18, width - 10, height * 0.36))
    low = average_color(source, (width * 0.80, height * 0.32, width - 8, height * 0.50))
    small = Image.new("RGB", source.size)
    draw = ImageDraw.Draw(small)
    for y in range(height):
        t = y / max(1, height - 1)
        if t < 0.34:
            local = t / 0.34
            a, b = top, mid
        else:
            local = (t - 0.34) / 0.28
            local = min(1.0, local)
            a, b = mid, low
        noise = rng.randint(-3, 3)
        color = tuple(clamp(int(a[i] * (1 - local) + b[i] * local + noise), 0, 255) for i in range(3))
        draw.line((0, y, width, y), fill=color)

    # Reintroduce a little source-like horizontal softness so the gaps are not flat blue slits.
    soft = source.filter(ImageFilter.GaussianBlur(radius=18))
    small = Image.blend(small, soft, 0.18).filter(ImageFilter.GaussianBlur(radius=1.4))
    return small.resize((width * scale, height * scale), Image.Resampling.BICUBIC).convert("RGBA")


def gap_polygon(seam, size, scale, variant):
    width, height = size
    x, top_y, top_w, base_w, lean = seam
    base_y = interpolate_back_y(x)
    base_y = top_y + (base_y - top_y) * variant["depth"]
    cx_top = (x + lean * 0.22) * width * scale
    cx_mid = (x + lean * 0.70) * width * scale
    cx_base = (x + lean) * width * scale
    y_top = top_y * height * scale
    y_mid = (top_y * 0.44 + base_y * 0.56) * height * scale
    y_base = base_y * height * scale
    top_px = top_w * variant["width"] * width * scale
    base_px = base_w * variant["width"] * width * scale
    mid_px = (top_px * 0.60 + base_px * 0.40)
    return [
        (cx_top - top_px * 0.50, y_top),
        (cx_top + top_px * 0.50, y_top),
        (cx_mid + mid_px * 0.55, y_mid),
        (cx_base + base_px * 0.50, y_base),
        (cx_base - base_px * 0.50, y_base),
        (cx_mid - mid_px * 0.55, y_mid),
    ]


def add_gap_edge_marks(image, seams, size, scale, variant, seed):
    rng = random.Random(seed)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    width, height = size
    for seam in seams:
        x, top_y, top_w, base_w, lean = seam
        base_y = interpolate_back_y(x)
        base_y = top_y + (base_y - top_y) * variant["depth"]
        y0 = top_y * height * scale
        y1 = base_y * height * scale
        cx0 = (x + lean * 0.22) * width * scale
        cx1 = (x + lean) * width * scale
        top_px = top_w * variant["width"] * width * scale
        base_px = base_w * variant["width"] * width * scale
        for side in (-1, 1):
            points = [
                (cx0 + side * top_px * 0.52, y0),
                ((cx0 + cx1) * 0.5 + side * (top_px + base_px) * 0.30, (y0 + y1) * 0.52),
                (cx1 + side * base_px * 0.52, y1),
            ]
            alpha = int((96 if side < 0 else 72) * variant["edge"])
            draw.line(points, fill=(33, 26, 19, alpha), width=max(2, int(0.7 * scale)), joint="curve")
            if side > 0 and rng.random() < 0.65:
                highlight = [(px + 1.2 * scale, py) for px, py in points]
                draw.line(highlight, fill=(142, 113, 82, int(34 * variant["edge"])), width=max(1, int(0.45 * scale)), joint="curve")
    return Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(radius=0.18 * scale)))


def make_variant(source, output, gap_mask_output, variant_name):
    variant = VARIANTS[variant_name]
    source_image = Image.open(source).convert("RGB")
    width, height = source_image.size
    scale = 4
    base = source_image.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    cleanup_mask = old_plate_mask(source_image.size, scale)
    cleaned = inpaint_region(source_image, cleanup_mask).resize((width * scale, height * scale), Image.Resampling.LANCZOS)
    cleaned = cleaned.convert("RGBA")
    gap_background = synthesize_gap_background(source_image, scale, variant["seed"])

    gap_mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(gap_mask)
    for seam in SEAMS:
        draw.polygon(gap_polygon(seam, source_image.size, scale, variant), fill=255)
    gap_mask = gap_mask.filter(ImageFilter.GaussianBlur(radius=variant["feather"] * scale))

    cleaned_alpha = gap_mask.point(lambda p: int(p * 0.14))
    cleaned.putalpha(cleaned_alpha)
    gap_background.putalpha(gap_mask)
    filled = Image.alpha_composite(base, gap_background)
    filled = Image.alpha_composite(filled, cleaned)
    filled = add_gap_edge_marks(filled, SEAMS, source_image.size, scale, variant, variant["seed"])

    # Restore a little original plate texture around the feathered gap shoulders.
    texture_alpha = ImageChops.subtract(
        gap_mask.filter(ImageFilter.GaussianBlur(radius=2.2 * scale)),
        gap_mask.filter(ImageFilter.GaussianBlur(radius=0.35 * scale)),
    ).point(lambda p: int(p * 0.22))
    texture = base.copy()
    texture.putalpha(texture_alpha)
    filled = Image.alpha_composite(filled, texture)

    output.parent.mkdir(parents=True, exist_ok=True)
    result = filled.resize(source_image.size, Image.Resampling.LANCZOS).convert("RGB")
    result.save(output)
    gap_mask.resize(source_image.size, Image.Resampling.LANCZOS).save(gap_mask_output)


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
    parser.add_argument("--prefix", default="stego_plate_gap_split_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: connected plate row")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"carved plate gaps {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
