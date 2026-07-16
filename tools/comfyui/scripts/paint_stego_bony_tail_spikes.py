import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-bony-plates-lora-control-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Coordinates are tuned to the current right-facing bony-plate Stegosaurus.
# Keep the hub small: the previous generic tail script created a blocky pad.
VARIANTS = {
    "v1a": {
        "hub": [(1048, 397), (1088, 399), (1110, 411), (1087, 425), (1049, 421), (1038, 409)],
        "spikes": [
            ((1070, 396), (1085, 401), (1122, 357)),
            ((1088, 401), (1103, 407), (1140, 383)),
            ((1070, 419), (1086, 424), (1120, 461)),
            ((1089, 416), (1105, 421), (1142, 433)),
        ],
        "opacity": 0.84,
        "blur": 0.34,
        "seed": 2026080901,
    },
    "v1b": {
        "hub": [(1053, 399), (1090, 401), (1108, 411), (1089, 422), (1055, 419), (1044, 409)],
        "spikes": [
            ((1074, 398), (1087, 402), (1113, 365)),
            ((1088, 402), (1101, 406), (1130, 389)),
            ((1075, 416), (1088, 420), (1110, 450)),
            ((1089, 414), (1102, 419), (1130, 429)),
        ],
        "opacity": 0.76,
        "blur": 0.46,
        "seed": 2026080902,
    },
    "v1c": {
        "hub": [(1058, 400), (1092, 402), (1109, 411), (1092, 421), (1059, 418), (1049, 409)],
        "spikes": [
            ((1077, 398), (1089, 402), (1110, 370)),
            ((1090, 402), (1102, 406), (1126, 391)),
            ((1078, 415), (1090, 419), (1108, 445)),
            ((1090, 414), (1103, 418), (1128, 427)),
        ],
        "opacity": 0.68,
        "blur": 0.54,
        "seed": 2026080903,
    },
    "v2a": {
        "hub": [(1058, 397), (1097, 400), (1117, 411), (1098, 424), (1059, 421), (1048, 408)],
        "spikes": [
            ((1078, 396), (1093, 401), (1132, 350)),
            ((1096, 401), (1111, 407), (1150, 379)),
            ((1079, 419), (1095, 424), (1125, 468)),
            ((1097, 416), (1113, 422), (1150, 438)),
        ],
        "opacity": 1.00,
        "blur": 0.26,
        "seed": 2026080906,
    },
    "v2b": {
        "hub": [(1061, 398), (1098, 401), (1114, 411), (1098, 421), (1061, 419), (1052, 408)],
        "spikes": [
            ((1080, 397), (1094, 401), (1125, 358)),
            ((1096, 402), (1110, 407), (1140, 384)),
            ((1081, 417), (1095, 421), (1118, 458)),
            ((1097, 415), (1111, 420), (1140, 432)),
        ],
        "opacity": 0.92,
        "blur": 0.34,
        "seed": 2026080907,
    },
    "v2c": {
        "hub": [(1064, 399), (1098, 401), (1112, 411), (1098, 420), (1065, 418), (1056, 408)],
        "spikes": [
            ((1083, 398), (1095, 402), (1118, 365)),
            ((1097, 402), (1109, 407), (1134, 389)),
            ((1083, 416), (1096, 420), (1113, 449)),
            ((1098, 414), (1110, 419), (1134, 428)),
        ],
        "opacity": 0.86,
        "blur": 0.42,
        "seed": 2026080908,
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

    tail_color = average_color(base, (985, 383, 1108, 438))
    ground_shadow = average_color(base, (1010, 470, 1125, 520))
    highlight = color_mix(tail_color, (230, 194, 132), 0.30)
    dark = tuple(max(18, int(channel * 0.44)) for channel in tail_color)
    keratin = (
        clamp(int(tail_color[0] * 0.82 + 34), 58, 170),
        clamp(int(tail_color[1] * 0.76 + 28), 48, 145),
        clamp(int(tail_color[2] * 0.68 + 20), 36, 116),
    )
    alpha = spec["opacity"]

    shadow = Image.new("RGBA", large.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        scale_poly([(1037, 423), (1143, 467)], scale),
        fill=(*tuple(max(12, int(c * 0.36)) for c in ground_shadow), int(34 * alpha)),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=7 * scale))

    hub_fill = (*color_mix(tail_color, dark, 0.36), int(130 * alpha))
    draw.polygon(scale_poly(spec["hub"], scale), fill=hub_fill)
    mask_draw.polygon(scale_poly(spec["hub"], scale), fill=160)
    draw.line(scale_poly(spec["hub"] + [spec["hub"][0]], scale), fill=(*dark, int(84 * alpha)), width=max(2, int(0.7 * scale)))

    for idx, (base_a, base_b, tip) in enumerate(spec["spikes"]):
        spike_color = (
            clamp(keratin[0] + idx * 3 - 4, 45, 178),
            clamp(keratin[1] + idx * 2 - 4, 38, 150),
            clamp(keratin[2] + idx * 2 - 3, 28, 118),
        )
        points = scale_poly([base_a, base_b, tip], scale)
        draw.polygon(points, fill=(*spike_color, int(214 * alpha)))
        mask_draw.polygon(points, fill=235)
        ridge_start = (
            base_a[0] * 0.58 + base_b[0] * 0.42,
            base_a[1] * 0.58 + base_b[1] * 0.42,
        )
        ridge_end = (
            tip[0] * 0.82 + base_a[0] * 0.18,
            tip[1] * 0.82 + base_a[1] * 0.18,
        )
        shade_start = (
            base_a[0] * 0.35 + base_b[0] * 0.65,
            base_a[1] * 0.35 + base_b[1] * 0.65,
        )
        shade_end = (
            tip[0] * 0.70 + base_b[0] * 0.30,
            tip[1] * 0.70 + base_b[1] * 0.30,
        )
        draw.line(
            scale_poly([ridge_start, ridge_end], scale),
            fill=(*highlight, int(54 * alpha)),
            width=max(2, int(0.70 * scale)),
        )
        draw.line(
            scale_poly([shade_start, shade_end], scale),
            fill=(*dark, int(72 * alpha)),
            width=max(2, int(0.76 * scale)),
        )

    rng = random.Random(spec["seed"])
    texture = Image.new("RGBA", large.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    tones = [dark, keratin, highlight, color_mix(tail_color, keratin, 0.45)]
    for _ in range(1050):
        x = rng.randrange(1030 * scale, min(large.width, 1148 * scale))
        y = rng.randrange(345 * scale, 468 * scale)
        if mask.getpixel((x, y)) < 16:
            continue
        tone = rng.choice(tones)
        dot_alpha = rng.randrange(4, 22)
        if rng.random() < 0.18:
            radius = rng.randrange(1, max(2, int(1.6 * scale)))
            texture_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, dot_alpha))
        else:
            texture_draw.point((x, y), fill=(*tone, dot_alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))

    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=spec["blur"] * scale))
    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=1.55 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))

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
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(42, 39, 35), font=ImageFont.load_default())
        tiles.append(tile)

    cols = min(2, len(tiles))
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
    parser.add_argument("--prefix", default="stego_bony_tailspike_local_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "current bony-plate candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        draw_variant(source, output, mask_output, variant_name)
        items.append((output, f"small four-spike thagomizer {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
