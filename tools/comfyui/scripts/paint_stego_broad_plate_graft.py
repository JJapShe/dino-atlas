import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-strong-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Tuned against the current 1152x768 natural Stegosaurus candidate. This pass
# intentionally favors a broad, countable plate silhouette over polish.
NEAR_PLATES = [
    # cx, base_y, width, height, lean
    (0.165, 0.505, 0.050, 0.078, -0.004),
    (0.235, 0.455, 0.064, 0.118, -0.003),
    (0.320, 0.412, 0.078, 0.150, -0.002),
    (0.420, 0.386, 0.090, 0.180, 0.000),
    (0.530, 0.382, 0.092, 0.188, 0.001),
    (0.640, 0.405, 0.082, 0.150, 0.002),
    (0.735, 0.455, 0.064, 0.108, 0.003),
    (0.808, 0.505, 0.046, 0.070, 0.004),
]

FAR_PLATES = [
    (0.198, 0.478, 0.046, 0.090, -0.003),
    (0.274, 0.432, 0.058, 0.120, -0.002),
    (0.366, 0.395, 0.070, 0.145, -0.001),
    (0.476, 0.378, 0.078, 0.165, 0.000),
    (0.586, 0.390, 0.076, 0.150, 0.001),
    (0.690, 0.430, 0.060, 0.112, 0.002),
    (0.770, 0.480, 0.044, 0.078, 0.003),
]

VARIANTS = {
    "v1a": {"height": 1.00, "width": 1.00, "yoff": 0, "seed": 2026062231, "opacity": 0.95},
    "v1b": {"height": 0.90, "width": 1.12, "yoff": 6, "seed": 2026062232, "opacity": 0.93},
    "v1c": {"height": 0.84, "width": 1.20, "yoff": 10, "seed": 2026062233, "opacity": 0.92},
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
        (0.115, 0.552),
        (0.128, 0.460),
        (0.168, 0.330),
        (0.248, 0.230),
        (0.360, 0.120),
        (0.470, 0.068),
        (0.586, 0.078),
        (0.690, 0.190),
        (0.780, 0.342),
        (0.850, 0.525),
        (0.816, 0.562),
        (0.706, 0.507),
        (0.594, 0.466),
        (0.482, 0.456),
        (0.370, 0.466),
        (0.260, 0.508),
        (0.162, 0.548),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.8 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=28)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.95))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 19, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


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
    apex_x = cx + lean + asymmetry * width * 0.06
    shoulder_y = base_y - height * 0.58
    lower_y = base_y - height * 0.20
    top_y = base_y - height
    return [
        (cx - width * 0.46, base_y + height * 0.012),
        (cx - width * 0.60, lower_y),
        (cx + lean - width * 0.54, shoulder_y),
        (apex_x - width * 0.22, top_y + height * 0.10),
        (apex_x, top_y),
        (apex_x + width * 0.24, top_y + height * 0.10),
        (cx + lean + width * 0.56, shoulder_y),
        (cx + width * 0.60, lower_y),
        (cx + width * 0.46, base_y + height * 0.012),
    ]


def make_palette(source_large):
    body = average_color(source_large.convert("RGB"), (430 * 4, 350 * 4, 690 * 4, 460 * 4))
    sky = average_color(source_large.convert("RGB"), (330 * 4, 80 * 4, 760 * 4, 180 * 4))
    base = (
        clamp(int(body[0] * 0.55 + 42), 70, 142),
        clamp(int(body[1] * 0.52 + 34), 58, 126),
        clamp(int(body[2] * 0.46 + 25), 42, 104),
    )
    far = tuple(max(34, int(channel * 0.72)) for channel in base)
    dark = tuple(max(18, int(channel * 0.38)) for channel in base)
    light = (
        clamp(int(base[0] * 1.24 + sky[0] * 0.05), 88, 176),
        clamp(int(base[1] * 1.16 + sky[1] * 0.04), 76, 154),
        clamp(int(base[2] * 1.08 + sky[2] * 0.03), 56, 126),
    )
    return {"base": base, "far": far, "dark": dark, "light": light}


def add_plate_texture(layer, mask, bbox, palette, scale, rng, opacity):
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    x0, y0, x1, y1 = bbox
    mask_pix = mask.load()
    tones = [palette["base"], palette["far"], palette["dark"], palette["light"]]
    for _ in range(180):
        x = rng.randrange(max(0, x0), min(layer.width, x1 + 1))
        y = rng.randrange(max(0, y0), min(layer.height, y1 + 1))
        if mask_pix[x, y] < 20:
            continue
        tone = rng.choice(tones)
        radius = rng.choice([1, 1, 2, 3]) * scale / 2
        alpha = int(rng.randrange(8, 30) * opacity)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_socket(layer, size, scale, palette):
    width, height = size
    points = [
        (0.135, 0.518),
        (0.205, 0.474),
        (0.298, 0.430),
        (0.405, 0.394),
        (0.522, 0.382),
        (0.636, 0.404),
        (0.738, 0.456),
        (0.835, 0.514),
    ]
    draw = ImageDraw.Draw(layer)
    scaled_points = [(x * width * scale, y * height * scale) for x, y in points]
    draw.line(scaled_points, fill=(*palette["dark"], 128), width=max(5, int(1.9 * scale)), joint="curve")


def draw_plate(layer, total_mask, spec, size, scale, variant, palette, far_row, rng):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale, variant)
    points = plate_points(cx, base_y, plate_w, plate_h, lean, rng.uniform(-0.28, 0.28))
    mask = Image.new("L", layer.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=255)

    plate = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(plate)
    fill_rgb = palette["far"] if far_row else palette["base"]
    alpha = int((188 if far_row else 232) * variant["opacity"])
    draw.polygon(points, fill=(*fill_rgb, alpha))
    draw.line(points + [points[0]], fill=(*palette["dark"], 212 if not far_row else 164), width=max(3, int(0.95 * scale)), joint="curve")
    draw.line(points[2:7], fill=(*palette["light"], 60 if not far_row else 42), width=max(2, int(0.65 * scale)), joint="curve")

    xs = [int(p[0]) for p in points]
    ys = [int(p[1]) for p in points]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    plate = add_plate_texture(plate, mask, bbox, palette, scale, rng, 0.75 if far_row else 1.0)

    base_shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(base_shadow)
    shadow_draw.ellipse(
        (
            cx - plate_w * 0.52,
            base_y - plate_h * 0.03,
            cx + plate_w * 0.52,
            base_y + plate_h * 0.12,
        ),
        fill=(10, 8, 6, 42 if not far_row else 26),
    )
    layer.alpha_composite(base_shadow.filter(ImageFilter.GaussianBlur(radius=1.5 * scale)))
    layer.alpha_composite(plate)
    total_mask.paste(ImageChops.lighter(total_mask, mask))


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    rng = random.Random(variant["seed"])
    base = Image.open(source).convert("RGB")
    width, height = base.size
    scale = 4
    erase_mask = old_plate_mask(base.size, scale)
    cleaned = inpaint_region(base, erase_mask).resize((width * scale, height * scale), Image.Resampling.LANCZOS)
    cleaned = cleaned.convert("RGBA")
    source_large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(source_large)

    plate_layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", cleaned.size, 0)
    draw_socket(plate_layer, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(plate_layer, plate_mask, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(plate_layer, plate_mask, spec, base.size, scale, variant, palette, False, rng)

    soft_alpha = plate_layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.18 * scale))
    plate_layer.putalpha(soft_alpha)
    result = Image.alpha_composite(cleaned, plate_layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    plate_mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def crop_plate_band(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    return image.crop((int(w * 0.10), int(h * 0.04), int(w * 0.88), int(h * 0.58)))


def make_contact_sheet(items, output, crop_output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    tiles = []
    crop_tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)

        crop = crop_plate_band(path)
        crop.thumbnail((thumb_w, thumb_h))
        crop_tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        crop_tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
        crop_draw = ImageDraw.Draw(crop_tile)
        crop_draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=ImageFont.load_default())
        crop_tiles.append(crop_tile)

    cols = min(2, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (226, 222, 214))
    crop_sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        xy = ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h))
        sheet.paste(tile, xy)
        crop_sheet.paste(crop_tiles[idx], xy)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    crop_sheet.save(crop_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_broad_plate_graft_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: connected/sail-like plates")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"broad separated plates {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_sheet = out_dir / f"{args.prefix}-plate-crops.png"
    make_contact_sheet(items, sheet, crop_sheet)
    print(sheet)
    print(crop_sheet)


if __name__ == "__main__":
    main()
