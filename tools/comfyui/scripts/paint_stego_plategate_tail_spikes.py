import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-plate-gate-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Coordinates are tuned for the current plate-gate Stegosaurus candidate.
# The goal is a visible four-spike guide attached to the right tail tip without
# touching the improved dorsal plates.
VARIANTS = {
    "v1a": {
        "hub": [(1078, 354), (1109, 352), (1120, 362), (1109, 376), (1078, 374), (1068, 363)],
        "spikes": [
            ((1092, 351), (1107, 355), (1138, 317)),
            ((1106, 357), (1118, 363), (1147, 341)),
            ((1090, 372), (1105, 378), (1134, 414)),
            ((1106, 372), (1119, 378), (1147, 393)),
        ],
        "opacity": 0.92,
        "blur": 0.22,
        "seed": 2026062501,
    },
    "v1b": {
        "hub": [(1082, 356), (1111, 354), (1121, 363), (1110, 375), (1082, 373), (1073, 364)],
        "spikes": [
            ((1095, 354), (1108, 357), (1132, 324)),
            ((1108, 359), (1119, 364), (1140, 346)),
            ((1094, 370), (1107, 375), (1130, 407)),
            ((1108, 370), (1120, 375), (1140, 390)),
        ],
        "opacity": 0.86,
        "blur": 0.30,
        "seed": 2026062502,
    },
    "v1c": {
        "hub": [(1085, 357), (1112, 356), (1120, 364), (1111, 374), (1085, 372), (1077, 364)],
        "spikes": [
            ((1097, 356), (1109, 359), (1128, 329)),
            ((1109, 360), (1119, 365), (1138, 350)),
            ((1097, 369), (1109, 374), (1128, 402)),
            ((1110, 369), (1120, 374), (1138, 388)),
        ],
        "opacity": 0.80,
        "blur": 0.36,
        "seed": 2026062503,
    },
    "v2a": {
        "hub": [(1072, 352), (1108, 350), (1125, 362), (1110, 379), (1072, 377), (1060, 363)],
        "spikes": [
            ((1088, 350), (1105, 354), (1140, 308)),
            ((1105, 356), (1122, 362), (1150, 336)),
            ((1088, 374), (1105, 380), (1138, 426)),
            ((1106, 373), (1123, 379), (1150, 402)),
        ],
        "opacity": 0.98,
        "blur": 0.20,
        "seed": 2026062504,
    },
    "v3a": {
        "hub": [(1068, 349), (1113, 349), (1129, 362), (1112, 382), (1068, 380), (1054, 363)],
        "spikes": [
            ((1084, 348), (1106, 354), (1140, 310)),
            ((1104, 356), (1124, 364), (1150, 336)),
            ((1084, 376), (1107, 384), (1138, 426)),
            ((1104, 374), (1124, 382), (1150, 404)),
        ],
        "opacity": 1.00,
        "blur": 0.16,
        "seed": 2026062505,
    },
    "v3b": {
        "hub": [(1074, 352), (1112, 352), (1125, 363), (1112, 378), (1074, 376), (1062, 364)],
        "spikes": [
            ((1088, 351), (1106, 356), (1133, 320)),
            ((1106, 358), (1122, 365), (1144, 343)),
            ((1088, 374), (1107, 381), (1132, 416)),
            ((1106, 373), (1122, 379), (1144, 399)),
        ],
        "opacity": 0.94,
        "blur": 0.22,
        "seed": 2026062506,
    },
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


def scale_point(point, scale):
    return (int(point[0] * scale), int(point[1] * scale))


def scale_poly(points, scale):
    return [scale_point(point, scale) for point in points]


def color_mix(a, b, ratio):
    return tuple(int(a[i] * (1 - ratio) + b[i] * ratio) for i in range(3))


def draw_variant(source, output, mask_output, variant_name):
    spec = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    tail_color = average_color(base, (1010, 340, 1108, 388))
    ground_shadow = average_color(base, (1020, 405, 1138, 455))
    dark = tuple(max(18, int(channel * 0.45)) for channel in tail_color)
    keratin = (
        clamp(int(tail_color[0] * 0.86 + 34), 62, 178),
        clamp(int(tail_color[1] * 0.80 + 28), 52, 150),
        clamp(int(tail_color[2] * 0.70 + 22), 40, 122),
    )
    highlight = color_mix(keratin, (238, 211, 155), 0.28)
    alpha = spec["opacity"]

    shadow = Image.new("RGBA", large.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        scale_poly([(1065, 382), (1146, 426)], scale),
        fill=(*tuple(max(12, int(c * 0.38)) for c in ground_shadow), int(26 * alpha)),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6 * scale))

    hub_fill = (*color_mix(tail_color, dark, 0.30), int(150 * alpha))
    draw.polygon(scale_poly(spec["hub"], scale), fill=hub_fill)
    mask_draw.polygon(scale_poly(spec["hub"], scale), fill=170)

    for idx, (base_a, base_b, tip) in enumerate(spec["spikes"]):
        spike_color = (
            clamp(keratin[0] + idx * 3 - 4, 48, 184),
            clamp(keratin[1] + idx * 2 - 4, 40, 154),
            clamp(keratin[2] + idx * 2 - 4, 30, 124),
        )
        points = [base_a, base_b, tip]
        draw.polygon(scale_poly(points, scale), fill=(*spike_color, int(225 * alpha)))
        mask_draw.polygon(scale_poly(points, scale), fill=245)

        ridge_start = (
            base_a[0] * 0.55 + base_b[0] * 0.45,
            base_a[1] * 0.55 + base_b[1] * 0.45,
        )
        ridge_end = (
            tip[0] * 0.82 + base_a[0] * 0.18,
            tip[1] * 0.82 + base_a[1] * 0.18,
        )
        shade_start = (
            base_a[0] * 0.34 + base_b[0] * 0.66,
            base_a[1] * 0.34 + base_b[1] * 0.66,
        )
        shade_end = (
            tip[0] * 0.70 + base_b[0] * 0.30,
            tip[1] * 0.70 + base_b[1] * 0.30,
        )
        draw.line(scale_poly([ridge_start, ridge_end], scale), fill=(*highlight, int(62 * alpha)), width=max(2, int(0.72 * scale)))
        draw.line(scale_poly([shade_start, shade_end], scale), fill=(*dark, int(80 * alpha)), width=max(2, int(0.78 * scale)))

    rng = random.Random(spec["seed"])
    texture = Image.new("RGBA", large.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    tones = [dark, keratin, highlight, color_mix(tail_color, keratin, 0.40)]
    for _ in range(1200):
        x = rng.randrange(1058 * scale, min(large.width, 1150 * scale))
        y = rng.randrange(304 * scale, 430 * scale)
        if mask.getpixel((x, y)) < 16:
            continue
        tone = rng.choice(tones)
        dot_alpha = rng.randrange(5, 26)
        if rng.random() < 0.20:
            radius = rng.randrange(1, max(2, int(1.5 * scale)))
            texture_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, dot_alpha))
        else:
            texture_draw.point((x, y), fill=(*tone, dot_alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))

    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=spec["blur"] * scale))
    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=1.25 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))

    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def crop_tail(path):
    image = Image.open(path).convert("RGB")
    return image.crop((850, 250, 1152, 485))


def make_contact_sheet(items, output, crop_output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    tiles = []
    crop_tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(42, 39, 35), font=ImageFont.load_default())
        tiles.append(tile)

        crop = crop_tail(path)
        crop.thumbnail((thumb_w, thumb_h))
        crop_tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        crop_tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
        crop_draw = ImageDraw.Draw(crop_tile)
        crop_draw.text((10, thumb_h + 12), label[:58], fill=(42, 39, 35), font=ImageFont.load_default())
        crop_tiles.append(crop_tile)

    cols = min(2, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    crop_sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
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
    parser.add_argument("--prefix", default="stego_plategate_tailspike_local_v2")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source: plate-gate candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        draw_variant(source, output, mask_output, variant_name)
        items.append((output, f"attached four-spike guide {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_sheet = out_dir / f"{args.prefix}-tail-crops.png"
    make_contact_sheet(items, sheet, crop_sheet)
    print(sheet)
    print(crop_sheet)


if __name__ == "__main__":
    main()
