import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "assets" / "dinosaurs" / "stegosaurus-stenops-platefirst-tailclean-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {
        "anchor": (1066, 407),
        "spikes": [
            ((1050, 396), (1070, 403), (1110, 344)),
            ((1068, 402), (1088, 408), (1132, 373)),
            ((1052, 416), (1074, 422), (1120, 470)),
            ((1071, 414), (1092, 420), (1138, 436)),
        ],
    },
    "v1b": {
        "anchor": (1060, 408),
        "spikes": [
            ((1046, 398), (1065, 403), (1098, 352)),
            ((1064, 403), (1083, 408), (1124, 382)),
            ((1048, 416), (1069, 421), (1114, 462)),
            ((1068, 413), (1088, 418), (1131, 431)),
        ],
    },
    "v1c": {
        "anchor": (1058, 410),
        "spikes": [
            ((1044, 400), (1062, 405), (1092, 360)),
            ((1062, 405), (1081, 410), (1117, 389)),
            ((1045, 417), (1066, 422), (1104, 455)),
            ((1066, 414), (1086, 419), (1124, 428)),
        ],
    },
    "v2a": {
        "anchor": (1080, 404),
        "pad": [(1052, 393), (1096, 396), (1120, 406), (1097, 420), (1055, 416), (1046, 404)],
        "pad_alpha": 166,
        "shadow_alpha": 24,
        "spikes": [
            ((1064, 394), (1078, 398), (1108, 352)),
            ((1080, 398), (1095, 402), (1137, 378)),
            ((1065, 410), (1081, 414), (1112, 458)),
            ((1081, 410), (1097, 414), (1139, 431)),
        ],
    },
    "v2b": {
        "anchor": (1084, 405),
        "pad": [(1056, 395), (1098, 397), (1117, 407), (1098, 419), (1058, 416), (1050, 405)],
        "pad_alpha": 152,
        "shadow_alpha": 18,
        "spikes": [
            ((1068, 396), (1082, 400), (1106, 360)),
            ((1084, 400), (1098, 404), (1132, 383)),
            ((1068, 410), (1084, 414), (1107, 449)),
            ((1084, 410), (1100, 414), (1134, 429)),
        ],
    },
    "v2c": {
        "anchor": (1077, 405),
        "pad": [(1050, 394), (1093, 397), (1113, 407), (1093, 419), (1053, 416), (1044, 405)],
        "pad_alpha": 142,
        "shadow_alpha": 14,
        "spikes": [
            ((1061, 396), (1076, 400), (1096, 364)),
            ((1078, 400), (1093, 404), (1125, 386)),
            ((1062, 410), (1078, 414), (1100, 445)),
            ((1079, 410), (1095, 414), (1127, 427)),
        ],
    },
}


def average_color(image, box):
    return image.crop(box).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def scaled(point, scale):
    return (int(point[0] * scale), int(point[1] * scale))


def poly(points, scale):
    return [scaled(point, scale) for point in points]


def draw_spikes(source, output, mask_output, variant_name):
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC)
    canvas = large.convert("RGBA")
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    variant = VARIANTS[variant_name]
    anchor_x, anchor_y = variant["anchor"]

    tail_color = average_color(base, (970, 382, 1095, 438))
    pad_alpha = variant.get("pad_alpha", 224)
    pad_color = (
        max(42, int(tail_color[0] * 0.64)),
        max(34, int(tail_color[1] * 0.60)),
        max(24, int(tail_color[2] * 0.54)),
        pad_alpha,
    )
    spike_color = (
        min(174, int(tail_color[0] * 0.84 + 32)),
        min(142, int(tail_color[1] * 0.78 + 24)),
        min(104, int(tail_color[2] * 0.72 + 18)),
        238,
    )

    pad = variant.get(
        "pad",
        [
            (anchor_x - 46, anchor_y - 18),
            (anchor_x + 36, anchor_y - 14),
            (anchor_x + 76, anchor_y + 2),
            (anchor_x + 54, anchor_y + 25),
            (anchor_x - 34, anchor_y + 24),
            (anchor_x - 58, anchor_y + 4),
        ],
    )
    draw.polygon(poly(pad, scale), fill=pad_color)
    mask_draw.polygon(poly(pad, scale), fill=210)

    for idx, points in enumerate(variant["spikes"]):
        tint = (
            max(48, min(184, spike_color[0] + idx * 3 - 7)),
            max(40, min(152, spike_color[1] + idx * 2 - 6)),
            max(28, min(110, spike_color[2] + idx * 2 - 5)),
            spike_color[3] - idx * 4,
        )
        draw.polygon(poly(points, scale), fill=tint)
        mask_draw.polygon(poly(points, scale), fill=245)
        base_a, base_b, tip = points
        ridge = [
            (base_a[0] * 0.58 + base_b[0] * 0.42, base_a[1] * 0.58 + base_b[1] * 0.42),
            (tip[0] * 0.84 + base_a[0] * 0.16, tip[1] * 0.84 + base_a[1] * 0.16),
        ]
        shade = [
            (base_a[0] * 0.35 + base_b[0] * 0.65, base_a[1] * 0.35 + base_b[1] * 0.65),
            (tip[0] * 0.72 + base_b[0] * 0.28, tip[1] * 0.72 + base_b[1] * 0.28),
        ]
        draw.line(poly(ridge, scale), fill=(206, 172, 114, 54), width=7)
        draw.line(poly(shade, scale), fill=(32, 25, 19, 78), width=8)

    rng = random.Random(sum(ord(char) for char in variant_name) + 2400)
    texture = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    for _ in range(1200):
        x = rng.randrange(max(0, int((anchor_x - 92) * scale)), min(large.width, int((anchor_x + 110) * scale)))
        y = rng.randrange(max(0, int((anchor_y - 92) * scale)), min(large.height, int((anchor_y + 86) * scale)))
        if mask.getpixel((x, y)) < 18:
            continue
        tone = rng.choice([(48, 37, 27), (116, 90, 58), (156, 128, 84), (82, 63, 42)])
        alpha = rng.randrange(5, 24)
        if rng.random() < 0.18:
            radius = rng.randrange(1, 3)
            texture_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            texture_draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_alpha = variant.get("shadow_alpha", 58)
    shadow_draw.ellipse(poly([(anchor_x - 74, anchor_y + 24), (anchor_x + 98, anchor_y + 64)], scale), fill=(28, 22, 17, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))

    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.85))
    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=3.1))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))

    result = Image.alpha_composite(canvas, layer)
    result = result.resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 420, 280
    label_h = 42
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label, fill=(42, 39, 35), font=ImageFont.load_default())
        tiles.append(tile)
    sheet = Image.new("RGB", (len(tiles) * thumb_w, thumb_h + label_h), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_right_tailspike_local_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    items = [(source, "current plate-first candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        draw_spikes(source, output, mask_output, variant_name)
        items.append((output, f"right thagomizer {variant_name}"))
        print(output)
        print(mask_output)
    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
