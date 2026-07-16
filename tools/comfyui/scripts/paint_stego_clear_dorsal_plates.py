import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-bony-plates-lora-control-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Tuned for the 1152x768 side-view Stegosaurus candidates. The goal here is a
# readable inspection target: broad separate plates with large sky gaps.
NEAR_PLATES = [
    # cx, base_y, width, height, lean
    (0.158, 0.515, 0.040, 0.075, -0.006),
    (0.225, 0.482, 0.055, 0.120, -0.005),
    (0.315, 0.440, 0.070, 0.178, -0.002),
    (0.425, 0.405, 0.086, 0.245, 0.000),
    (0.540, 0.395, 0.092, 0.270, 0.002),
    (0.652, 0.420, 0.080, 0.210, 0.003),
    (0.748, 0.465, 0.060, 0.135, 0.004),
    (0.825, 0.503, 0.040, 0.080, 0.005),
]

FAR_PLATES = [
    (0.190, 0.498, 0.043, 0.090, -0.004),
    (0.270, 0.458, 0.055, 0.142, -0.003),
    (0.370, 0.420, 0.068, 0.205, -0.001),
    (0.485, 0.398, 0.078, 0.245, 0.001),
    (0.602, 0.405, 0.074, 0.225, 0.002),
    (0.705, 0.445, 0.058, 0.155, 0.004),
    (0.785, 0.488, 0.042, 0.095, 0.005),
]

VARIANTS = {
    "v2a": {"height": 1.00, "width": 1.00, "yoff": 0, "opacity": 0.98, "seed": 2026081301},
    "v2b": {"height": 0.92, "width": 1.10, "yoff": 5, "opacity": 0.96, "seed": 2026081302},
    "v2c": {"height": 1.08, "width": 0.94, "yoff": -5, "opacity": 0.98, "seed": 2026081303},
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
        (0.105, 0.540),
        (0.126, 0.445),
        (0.188, 0.330),
        (0.285, 0.225),
        (0.395, 0.118),
        (0.515, 0.078),
        (0.630, 0.110),
        (0.730, 0.248),
        (0.812, 0.405),
        (0.862, 0.532),
        (0.802, 0.562),
        (0.710, 0.510),
        (0.612, 0.470),
        (0.500, 0.458),
        (0.388, 0.466),
        (0.282, 0.492),
        (0.190, 0.525),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=2.4 * scale))


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
    repaired = cv2.inpaint(cv_image, cv_mask, 19, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def make_palette(source_large):
    body_mid = average_color(source_large.convert("RGB"), (430 * 4, 305 * 4, 640 * 4, 430 * 4))
    sky_mid = average_color(source_large.convert("RGB"), (430 * 4, 80 * 4, 680 * 4, 190 * 4))
    body_dark = tuple(max(18, int(channel * 0.42)) for channel in body_mid)
    near_fill = (
        clamp(int(body_mid[0] * 0.52 + 58), 76, 138),
        clamp(int(body_mid[1] * 0.48 + 48), 66, 124),
        clamp(int(body_mid[2] * 0.40 + 34), 48, 98),
    )
    far_fill = tuple(max(38, int(channel * 0.72)) for channel in near_fill)
    edge = tuple(max(18, int(channel * 0.45)) for channel in near_fill)
    high = tuple(clamp(int(channel * 1.26), 92, 172) for channel in near_fill)
    cool_rim = (
        clamp(int(sky_mid[0] * 0.34 + high[0] * 0.62), 72, 180),
        clamp(int(sky_mid[1] * 0.34 + high[1] * 0.62), 72, 170),
        clamp(int(sky_mid[2] * 0.30 + high[2] * 0.60), 64, 150),
    )
    return {
        "body_dark": body_dark,
        "near_fill": near_fill,
        "far_fill": far_fill,
        "edge": edge,
        "high": high,
        "cool_rim": cool_rim,
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
    top = base_y - height
    shoulder_y = base_y - height * 0.62
    cap = width * (0.18 + abs(asymmetry) * 0.03)
    left_push = width * (0.05 + asymmetry * 0.04)
    right_push = width * (0.04 - asymmetry * 0.04)
    return [
        (cx - width * 0.44, base_y + height * 0.018),
        (cx - width * 0.55, base_y - height * 0.18),
        (cx + lean - width * 0.49 - left_push, shoulder_y),
        (cx + lean - cap, top + height * 0.075),
        (cx + lean, top),
        (cx + lean + cap, top + height * 0.075),
        (cx + lean + width * 0.50 + right_push, shoulder_y),
        (cx + width * 0.56, base_y - height * 0.18),
        (cx + width * 0.43, base_y + height * 0.018),
    ]


def draw_back_socket(layer, size, scale, palette):
    draw = ImageDraw.Draw(layer)
    width, height = size
    points = [
        (0.122, 0.520),
        (0.190, 0.493),
        (0.285, 0.452),
        (0.395, 0.415),
        (0.510, 0.400),
        (0.624, 0.420),
        (0.728, 0.468),
        (0.846, 0.522),
    ]
    pixel_points = [(x * width * scale, y * height * scale) for x, y in points]
    draw.line(pixel_points, fill=(*palette["body_dark"], 142), width=max(7, int(2.4 * scale)), joint="curve")
    draw.line(pixel_points, fill=(*palette["high"], 34), width=max(3, int(0.8 * scale)), joint="curve")


def draw_plate(draw, mask_draw, spec, size, scale, variant, palette, far_row, rng):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale, variant)
    asymmetry = rng.uniform(-0.38, 0.38)
    points = plate_points(cx, base_y, plate_w, plate_h, lean, asymmetry)
    if far_row:
        fill = (*palette["far_fill"], int(218 * variant["opacity"]))
        edge = (*palette["edge"], int(178 * variant["opacity"]))
        high = (*palette["cool_rim"], int(38 * variant["opacity"]))
        shadow = 38
    else:
        fill = (*palette["near_fill"], int(242 * variant["opacity"]))
        edge = (*palette["edge"], int(224 * variant["opacity"]))
        high = (*palette["cool_rim"], int(56 * variant["opacity"]))
        shadow = 58

    draw.ellipse(
        (
            cx - plate_w * 0.48,
            base_y - plate_h * 0.020,
            cx + plate_w * 0.48,
            base_y + plate_h * 0.110,
        ),
        fill=(15, 13, 11, shadow),
    )
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=255)

    # A subtle lower shade makes each plate read as a flat object with thickness.
    lower = [
        points[8],
        points[0],
        points[1],
        (cx + lean - plate_w * 0.32, base_y - plate_h * 0.36),
        (cx + lean + plate_w * 0.36, base_y - plate_h * 0.34),
        points[7],
    ]
    draw.polygon(lower, fill=(*palette["edge"], 30 if not far_row else 22))
    draw.line(points + [points[0]], fill=edge, width=max(4, int(1.25 * scale)), joint="curve")
    draw.line(points[2:7], fill=high, width=max(2, int(0.75 * scale)), joint="curve")

    # Keep surfaces blunt and pitted: no branching leaf-vein marks.
    for _ in range(4 if not far_row else 3):
        x = rng.uniform(cx - plate_w * 0.28, cx + plate_w * 0.28)
        y = rng.uniform(base_y - plate_h * 0.80, base_y - plate_h * 0.25)
        radius = rng.uniform(0.8 * scale, 2.2 * scale)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*palette["edge"], 20))


def add_plate_texture(layer, plate_mask, size, scale, seed, palette):
    rng = random.Random(seed)
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    width, height = size
    tones = [palette["edge"], palette["near_fill"], palette["far_fill"], palette["high"]]
    for _ in range(4200):
        x = rng.randrange(int(width * 0.12 * scale), int(width * 0.85 * scale))
        y = rng.randrange(int(height * 0.06 * scale), int(height * 0.54 * scale))
        if plate_mask.getpixel((x, y)) < 24:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(3, 22)
        if rng.random() < 0.22:
            radius = rng.randrange(1, max(2, int(2.0 * scale)))
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

    draw_back_socket(layer, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(draw, mask_draw, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(draw, mask_draw, spec, base.size, scale, variant, palette, False, rng)

    layer = add_plate_texture(layer, plate_mask, base.size, scale, variant["seed"], palette)
    soft_mask = plate_mask.filter(ImageFilter.GaussianBlur(radius=0.8 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.08 * scale))

    result = Image.alpha_composite(cleaned, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
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
    parser.add_argument("--prefix", default="stego_clear_dorsal_plates_v2")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: rejected comb-like plates")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"clear broad alternating plates {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
