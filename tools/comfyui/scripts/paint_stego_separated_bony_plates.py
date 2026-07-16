import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-strong-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Tuned against the current 1152x768 strong-plate Stegosaurus. The goal is not
# final art by itself; it is a stricter control target with countable plates.
NEAR_PLATES = [
    # cx, base_y, width, height, lean
    (0.170, 0.512, 0.038, 0.072, -0.006),
    (0.232, 0.478, 0.050, 0.118, -0.006),
    (0.304, 0.435, 0.062, 0.172, -0.004),
    (0.388, 0.405, 0.074, 0.226, -0.001),
    (0.482, 0.390, 0.082, 0.264, 0.001),
    (0.580, 0.397, 0.078, 0.238, 0.002),
    (0.670, 0.425, 0.066, 0.178, 0.003),
    (0.745, 0.468, 0.052, 0.124, 0.004),
    (0.804, 0.506, 0.038, 0.078, 0.004),
]

FAR_PLATES = [
    (0.198, 0.498, 0.032, 0.074, -0.005),
    (0.266, 0.458, 0.040, 0.105, -0.004),
    (0.345, 0.420, 0.050, 0.148, -0.002),
    (0.436, 0.397, 0.056, 0.186, 0.000),
    (0.532, 0.395, 0.058, 0.194, 0.001),
    (0.626, 0.414, 0.052, 0.150, 0.002),
    (0.708, 0.450, 0.040, 0.105, 0.003),
    (0.775, 0.488, 0.030, 0.070, 0.004),
]

VARIANTS = {
    "v1a": {"height": 1.00, "width": 1.00, "yoff": 0, "seed": 2026081601, "plate_alpha": 0.96},
    "v1b": {"height": 0.92, "width": 1.10, "yoff": 5, "seed": 2026081602, "plate_alpha": 0.94},
    "v1c": {"height": 1.08, "width": 0.94, "yoff": -4, "seed": 2026081603, "plate_alpha": 0.97},
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
    return mask.filter(ImageFilter.GaussianBlur(radius=2.2 * scale))


def inpaint_region(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=26)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: int(p * 0.94))
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 21, cv2.INPAINT_TELEA)
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
    top = base_y - height
    shoulder_y = base_y - height * 0.58
    lower_y = base_y - height * 0.18
    shoulder_left = width * (0.42 + asymmetry * 0.04)
    shoulder_right = width * (0.43 - asymmetry * 0.04)
    cap = width * (0.15 + abs(asymmetry) * 0.03)
    return [
        (cx - width * 0.40, base_y + height * 0.015),
        (cx - width * 0.55, lower_y),
        (cx + lean - shoulder_left, shoulder_y),
        (cx + lean - cap, top + height * 0.08),
        (cx + lean, top),
        (cx + lean + cap, top + height * 0.08),
        (cx + lean + shoulder_right, shoulder_y),
        (cx + width * 0.56, lower_y),
        (cx + width * 0.40, base_y + height * 0.015),
    ]


def make_palette(source_large):
    body_mid = average_color(source_large.convert("RGB"), (440 * 4, 310 * 4, 660 * 4, 430 * 4))
    sky_mid = average_color(source_large.convert("RGB"), (420 * 4, 82 * 4, 700 * 4, 180 * 4))
    near_fill = (
        clamp(int(body_mid[0] * 0.58 + 46), 72, 142),
        clamp(int(body_mid[1] * 0.54 + 39), 60, 128),
        clamp(int(body_mid[2] * 0.48 + 30), 46, 106),
    )
    far_fill = tuple(max(34, int(channel * 0.74)) for channel in near_fill)
    shadow = tuple(max(18, int(channel * 0.42)) for channel in near_fill)
    highlight = (
        clamp(int(near_fill[0] * 1.22 + sky_mid[0] * 0.08), 88, 176),
        clamp(int(near_fill[1] * 1.18 + sky_mid[1] * 0.06), 78, 158),
        clamp(int(near_fill[2] * 1.10 + sky_mid[2] * 0.05), 58, 132),
    )
    rim = (
        clamp(int(highlight[0] * 0.74 + sky_mid[0] * 0.14), 78, 178),
        clamp(int(highlight[1] * 0.72 + sky_mid[1] * 0.14), 74, 164),
        clamp(int(highlight[2] * 0.70 + sky_mid[2] * 0.12), 62, 150),
    )
    return {
        "near_fill": near_fill,
        "far_fill": far_fill,
        "shadow": shadow,
        "highlight": highlight,
        "rim": rim,
    }


def gradient_plate(size, points, fill, highlight, shadow, mask_value, scale, rng):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=mask_value)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = int(min(xs)), int(max(xs))
    y0, y1 = int(min(ys)), int(max(ys))
    pix = layer.load()
    mask_pix = mask.load()
    span_y = max(1, y1 - y0)
    span_x = max(1, x1 - x0)
    for y in range(max(0, y0), min(size[1], y1 + 1)):
        vertical = (y - y0) / span_y
        for x in range(max(0, x0), min(size[0], x1 + 1)):
            alpha = mask_pix[x, y]
            if not alpha:
                continue
            horizontal = (x - x0) / span_x
            light = max(0.0, 1.0 - vertical) * 0.32 + max(0.0, 1.0 - horizontal) * 0.11
            shade = vertical * 0.38 + horizontal * 0.08
            noise = rng.uniform(-0.045, 0.045)
            channels = []
            for idx, base in enumerate(fill):
                value = base * (1.0 - shade) + shadow[idx] * shade + highlight[idx] * light
                channels.append(clamp(int(value * (1.0 + noise)), 0, 255))
            pix[x, y] = (*channels, alpha)

    texture = Image.new("RGBA", size, (0, 0, 0, 0))
    tex_draw = ImageDraw.Draw(texture)
    for _ in range(240):
        x = rng.randrange(max(0, x0), min(size[0], x1 + 1))
        y = rng.randrange(max(0, y0), min(size[1], y1 + 1))
        if mask_pix[x, y] < 24:
            continue
        tone = rng.choice([fill, highlight, shadow])
        alpha = rng.randrange(8, 28)
        radius = rng.randrange(1, max(2, int(1.8 * scale)))
        tex_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture), mask


def draw_back_socket(layer, size, scale, palette):
    draw = ImageDraw.Draw(layer)
    width, height = size
    points = [
        (0.132, 0.528),
        (0.198, 0.493),
        (0.292, 0.450),
        (0.398, 0.415),
        (0.510, 0.399),
        (0.620, 0.418),
        (0.724, 0.466),
        (0.844, 0.523),
    ]
    scaled_points = [(x * width * scale, y * height * scale) for x, y in points]
    draw.line(scaled_points, fill=(*palette["shadow"], 152), width=max(7, int(2.4 * scale)), joint="curve")
    draw.line(scaled_points, fill=(*palette["highlight"], 38), width=max(3, int(0.8 * scale)), joint="curve")


def draw_plate(layer, total_mask, spec, size, scale, variant, palette, far_row, rng):
    cx, base_y, plate_w, plate_h, lean = scaled(spec, size, scale, variant)
    asymmetry = rng.uniform(-0.32, 0.32)
    points = plate_points(cx, base_y, plate_w, plate_h, lean, asymmetry)
    fill = palette["far_fill"] if far_row else palette["near_fill"]
    alpha = int((184 if far_row else 232) * variant["plate_alpha"])
    plate_layer, plate_mask = gradient_plate(layer.size, points, fill, palette["highlight"], palette["shadow"], alpha, scale, rng)
    draw = ImageDraw.Draw(plate_layer)

    base_shadow = (
        cx - plate_w * 0.50,
        base_y - plate_h * 0.035,
        cx + plate_w * 0.50,
        base_y + plate_h * 0.120,
    )
    shadow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.ellipse(base_shadow, fill=(14, 12, 10, 52 if not far_row else 34))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=1.3 * scale))
    layer.alpha_composite(shadow_layer)

    edge = (*palette["shadow"], 214 if not far_row else 166)
    rim = (*palette["rim"], 68 if not far_row else 42)
    draw.line(points + [points[0]], fill=edge, width=max(3, int(1.05 * scale)), joint="curve")
    draw.line(points[2:7], fill=rim, width=max(2, int(0.75 * scale)), joint="curve")

    # Subtle pitted/scute texture only; avoid branching marks that read as leaves.
    for _ in range(6 if not far_row else 4):
        px = rng.uniform(cx - plate_w * 0.24, cx + plate_w * 0.24)
        py = rng.uniform(base_y - plate_h * 0.76, base_y - plate_h * 0.22)
        r = rng.uniform(0.8 * scale, 2.4 * scale)
        draw.ellipse((px - r, py - r, px + r, py + r), fill=(*palette["shadow"], 18))

    layer.alpha_composite(plate_layer)
    total_mask.paste(ImageChops.lighter(total_mask, plate_mask))


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
    draw_back_socket(plate_layer, base.size, scale, palette)
    for spec in FAR_PLATES:
        draw_plate(plate_layer, plate_mask, spec, base.size, scale, variant, palette, True, rng)
    for spec in NEAR_PLATES:
        draw_plate(plate_layer, plate_mask, spec, base.size, scale, variant, palette, False, rng)

    soft_alpha = plate_layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.20 * scale))
    plate_layer.putalpha(soft_alpha)
    result = Image.alpha_composite(cleaned, plate_layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
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
    parser.add_argument("--prefix", default="stego_separated_bony_plates_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: current connected/sail-like plates")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"separate bony plate lock {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
