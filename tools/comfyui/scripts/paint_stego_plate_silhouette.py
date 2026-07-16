import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT.parent.parent / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-natural-plates-ipcontrol-v1.png"
DEFAULT_OUTPUT = ROOT / "outputs" / "stego_plate_silhouette_v1.png"
STRUCTURE_REFERENCE = ASSET_ROOT / "stegosaurus-stenops-plate-structure-v1.png"


# Coordinates are normalized against the current 1152x768 Stegosaurus natural
# candidate. Draw two staggered plate rows: far row first, near row last.
PLATES = [
    # cx, base_y, width, height, lean, far_row
    (0.208, 0.532, 0.038, 0.085, -0.010, True),
    (0.238, 0.505, 0.048, 0.122, -0.006, False),
    (0.278, 0.475, 0.052, 0.158, -0.005, True),
    (0.322, 0.447, 0.064, 0.205, -0.002, False),
    (0.372, 0.421, 0.074, 0.240, 0.002, True),
    (0.428, 0.404, 0.082, 0.272, 0.002, False),
    (0.486, 0.397, 0.086, 0.286, 0.000, True),
    (0.545, 0.405, 0.082, 0.258, -0.002, False),
    (0.604, 0.425, 0.072, 0.218, 0.001, True),
    (0.660, 0.456, 0.060, 0.170, 0.004, False),
    (0.710, 0.494, 0.050, 0.128, 0.004, True),
    (0.754, 0.525, 0.040, 0.088, 0.004, False),
]


def scaled_plate_points(cx, base_y, width, height, lean):
    return [
        (cx - width * 0.50, base_y + height * 0.02),
        (cx - width * 0.58, base_y - height * 0.24),
        (cx + lean - width * 0.42, base_y - height * 0.61),
        (cx + lean - width * 0.17, base_y - height * 0.89),
        (cx + lean + width * 0.07, base_y - height * 1.00),
        (cx + lean + width * 0.34, base_y - height * 0.76),
        (cx + width * 0.55, base_y - height * 0.35),
        (cx + width * 0.46, base_y + height * 0.04),
    ]


def to_pixels(spec, width, height, scale):
    cx, base_y, plate_w, plate_h, lean, far_row = spec
    return (
        cx * width * scale,
        base_y * height * scale,
        plate_w * width * scale,
        plate_h * height * scale,
        lean * width * scale,
        far_row,
    )


def old_plate_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)

    # Broadly cover the old single-row fin/plate mass, while keeping the belly,
    # legs, head, and tail shaft outside the inpaint region.
    band = [
        (0.185, 0.512),
        (0.196, 0.392),
        (0.240, 0.300),
        (0.310, 0.235),
        (0.404, 0.158),
        (0.498, 0.122),
        (0.596, 0.155),
        (0.690, 0.250),
        (0.758, 0.368),
        (0.784, 0.484),
        (0.724, 0.508),
        (0.630, 0.455),
        (0.530, 0.425),
        (0.420, 0.430),
        (0.310, 0.455),
        (0.226, 0.498),
    ]
    draw.polygon([(x * width * scale, y * height * scale) for x, y in band], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=2.2 * scale))


def remove_old_plate_mass(image, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=18)).convert("RGBA")
        base = image.convert("RGBA")
        alpha = mask.resize(image.size, Image.Resampling.LANCZOS)
        blurred.putalpha(alpha)
        return Image.alpha_composite(base, blurred).convert("RGB")

    cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.resize(image.size, Image.Resampling.LANCZOS).point(lambda p: 255 if p > 24 else 0))
    repaired = cv2.inpaint(cv_image, cv_mask, 13, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))


def average_color(image, box):
    crop = image.crop(box).resize((1, 1), Image.Resampling.BICUBIC)
    return crop.getpixel((0, 0))


def draw_gap_separators(draw, specs, width, height, scale, alpha=96):
    ordered = sorted(specs, key=lambda item: item[0])
    for left, right in zip(ordered, ordered[1:]):
        lx, lb, lw, lh, _, _ = left
        rx, rb, rw, rh, _, _ = right
        gap_x = ((lx + rx) * 0.5) * width * scale
        top_y = (min(lb - lh * 0.82, rb - rh * 0.82) * height * scale)
        base_y = ((lb + rb) * 0.5 * height * scale)
        wiggle = (rx - lx) * width * scale * 0.08
        points = [
            (gap_x - wiggle, top_y + 5 * scale),
            (gap_x + wiggle * 0.35, (top_y + base_y) * 0.50),
            (gap_x, base_y - 3 * scale),
        ]
        draw.line(points, fill=(72, 92, 58, alpha), width=max(3, int(2.1 * scale)), joint="curve")


def draw_plate_layer(image, seed=2026069201, cleanup_strength=0.0):
    rng = random.Random(seed)
    width, height = image.size
    scale = 4
    large_source = image.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")

    cleanup_mask = old_plate_mask(image.size, scale)
    if cleanup_strength > 0:
        cleaned_small = remove_old_plate_mass(image, cleanup_mask).convert("RGBA")
        source_small = image.convert("RGBA")
        cleanup_alpha = cleanup_mask.resize(image.size, Image.Resampling.LANCZOS).point(
            lambda p: int(p * max(0.0, min(1.0, cleanup_strength)))
        )
        cleaned_small.putalpha(cleanup_alpha)
        cleaned = Image.alpha_composite(source_small, cleaned_small).resize(
            (width * scale, height * scale), Image.Resampling.LANCZOS
        ).convert("RGBA")
    else:
        cleaned = large_source.copy()

    layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", cleaned.size, 0)
    gap_layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(plate_mask)
    gap_draw = ImageDraw.Draw(gap_layer)
    shadow_draw = ImageDraw.Draw(shadow)

    body_mid = average_color(large_source.convert("RGB"), (420 * scale, 330 * scale, 610 * scale, 395 * scale))
    body_dark = tuple(max(20, int(channel * 0.58)) for channel in body_mid)
    body_warm = (
        min(180, int(body_mid[0] * 0.86 + 42)),
        min(145, int(body_mid[1] * 0.82 + 32)),
        min(108, int(body_mid[2] * 0.76 + 24)),
    )

    bounded_cleanup = max(0.0, min(1.0, cleanup_strength))
    if cleanup_strength < 0.85:
        gap_alpha = int(104 - bounded_cleanup * 46)
        draw_gap_separators(gap_draw, PLATES, width, height, scale, alpha=gap_alpha)
        gap_layer = gap_layer.filter(ImageFilter.GaussianBlur(radius=0.9 * scale))

    fill_alpha = 0.46 + bounded_cleanup * 0.32
    line_alpha = 0.82 + bounded_cleanup * 0.18

    for spec in sorted(PLATES, key=lambda item: item[-1], reverse=True):
        cx, base_y, plate_w, plate_h, lean, far_row = to_pixels(spec, width, height, scale)
        points = scaled_plate_points(cx, base_y, plate_w, plate_h, lean)

        if far_row:
            fill = (
                max(54, body_warm[0] - 34),
                max(45, body_warm[1] - 30),
                max(34, body_warm[2] - 24),
                int(172 * fill_alpha),
            )
            outline = (*body_dark, int(168 * line_alpha))
            ridge = (88, 70, 52, int(98 * line_alpha))
            highlight = (164, 132, 92, int(62 * line_alpha))
        else:
            fill = (body_warm[0], body_warm[1], body_warm[2], int(186 * fill_alpha))
            outline = (*body_dark, int(188 * line_alpha))
            ridge = (78, 59, 43, int(116 * line_alpha))
            highlight = (196, 160, 112, int(84 * line_alpha))

        base_box = (
            cx - plate_w * 0.56,
            base_y - plate_h * 0.08,
            cx + plate_w * 0.56,
            base_y + plate_h * 0.14,
        )
        shadow_draw.ellipse(base_box, fill=(20, 16, 12, int((58 if not far_row else 38) * line_alpha)))
        draw.polygon(points, fill=fill)
        draw.line(points + [points[0]], fill=outline, width=max(3, int(1.25 * scale)), joint="curve")
        mask_draw.polygon(points, fill=255)

        center_top = (cx + lean * 0.40, base_y - plate_h * 0.84)
        center_base = (cx + lean * 0.10, base_y - plate_h * 0.03)
        draw.line([center_base, center_top], fill=ridge, width=max(2, int(0.9 * scale)))
        for frac in (0.22, 0.38, 0.54, 0.70):
            left = (cx - plate_w * (0.42 - frac * 0.17), base_y - plate_h * frac)
            right = (cx + plate_w * (0.43 - frac * 0.16), base_y - plate_h * frac)
            rib_mid = (cx + lean * 0.24, base_y - plate_h * (frac + 0.10))
            draw.line([left, rib_mid], fill=(66, 50, 38, 68), width=max(1, int(0.7 * scale)))
            draw.line([right, rib_mid], fill=(66, 50, 38, 62), width=max(1, int(0.7 * scale)))

        draw.line(points[1:5], fill=highlight, width=max(2, int(0.95 * scale)), joint="curve")

    texture = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    tex_draw = ImageDraw.Draw(texture)
    for _ in range(4200):
        x = rng.randrange(int(width * 0.18 * scale), int(width * 0.80 * scale))
        y = rng.randrange(int(height * 0.08 * scale), int(height * 0.54 * scale))
        if plate_mask.getpixel((x, y)) < 20:
            continue
        tone = rng.choice([(45, 34, 26), (115, 90, 62), (168, 134, 92), (82, 62, 43)])
        alpha = rng.randrange(4, 24)
        if rng.random() < 0.18:
            radius = rng.randrange(1, max(2, int(2.3 * scale)))
            tex_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            tex_draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), plate_mask))

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=2.0 * scale))
    cleaned = Image.alpha_composite(cleaned, gap_layer)
    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.12 * scale))
    soft_mask = plate_mask.filter(ImageFilter.GaussianBlur(radius=0.42 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))

    composite = Image.alpha_composite(cleaned, layer)
    result = composite.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    return result, cleanup_mask.resize((width, height), Image.Resampling.LANCZOS), plate_mask.resize(
        (width, height), Image.Resampling.LANCZOS
    )


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 384, 256
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + 44), (244, 241, 233))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:62], fill=(38, 33, 28), font=ImageFont.load_default())
        tiles.append(tile)

    cols = min(3, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 44)), (226, 220, 209))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + 44)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--cleanup-mask-output")
    parser.add_argument("--plate-mask-output")
    parser.add_argument("--sheet-output")
    parser.add_argument("--seed", type=int, default=2026069201)
    parser.add_argument(
        "--cleanup-strength",
        type=float,
        default=0.0,
        help="Blend old-plate removal before repainting. Keep 0 for texture-preserving emphasis.",
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    cleanup_mask_output = (
        Path(args.cleanup_mask_output).resolve()
        if args.cleanup_mask_output
        else output.with_name(output.stem + "-cleanup-mask.png")
    )
    plate_mask_output = (
        Path(args.plate_mask_output).resolve() if args.plate_mask_output else output.with_name(output.stem + "-mask.png")
    )
    sheet_output = Path(args.sheet_output).resolve() if args.sheet_output else output.with_name(output.stem + "-sheet.png")

    output.parent.mkdir(parents=True, exist_ok=True)
    cleanup_mask_output.parent.mkdir(parents=True, exist_ok=True)
    plate_mask_output.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(source).convert("RGB")
    corrected, cleanup_mask, plate_mask = draw_plate_layer(image, seed=args.seed, cleanup_strength=args.cleanup_strength)
    corrected.save(output)
    cleanup_mask.save(cleanup_mask_output)
    plate_mask.save(plate_mask_output)

    items = [(source, "current natural candidate")]
    if STRUCTURE_REFERENCE.exists():
        items.append((STRUCTURE_REFERENCE, "old structure reference"))
    items.append((output, "plate silhouette paintover v1"))
    make_contact_sheet(items, sheet_output)

    print(output)
    print(cleanup_mask_output)
    print(plate_mask_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
