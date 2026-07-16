import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "herrerasaurus-ischigualastensis-longarms-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"seam_y": 0, "opacity": 0.90, "seed": 2026081507},
    "v1b": {"seam_y": -4, "opacity": 0.86, "seed": 2026081508},
    "v1c": {"seam_y": 4, "opacity": 0.94, "seed": 2026081509},
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


def scaled_points(points, scale, yoff=0):
    return [(x * scale, (y + yoff) * scale) for x, y in points]


def make_palette(base_large, scale):
    lower_jaw = average_color(base_large.convert("RGB"), (970 * scale, 270 * scale, 1075 * scale, 315 * scale))
    neck_shadow = average_color(base_large.convert("RGB"), (860 * scale, 300 * scale, 960 * scale, 352 * scale))
    upper = average_color(base_large.convert("RGB"), (940 * scale, 205 * scale, 1090 * scale, 240 * scale))
    fill = (
        clamp(int(lower_jaw[0] * 0.72 + neck_shadow[0] * 0.18 + 18), 62, 145),
        clamp(int(lower_jaw[1] * 0.74 + neck_shadow[1] * 0.18 + 14), 54, 128),
        clamp(int(lower_jaw[2] * 0.72 + neck_shadow[2] * 0.16 + 10), 40, 105),
    )
    underside = tuple(max(20, int(channel * 0.55)) for channel in fill)
    seam = tuple(max(18, int(channel * 0.36)) for channel in upper)
    highlight = tuple(clamp(int(channel * 1.28), 78, 184) for channel in fill)
    return {"fill": fill, "underside": underside, "seam": seam, "highlight": highlight}


def draw_closed_jaw(source, output, crop_output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    width, height = base.size
    scale = 4
    large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    palette = make_palette(large, scale)
    rng = random.Random(variant["seed"])

    yoff = variant["seam_y"]
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    # Covers only the open mouth gap and teeth, preserving the eye and skull top.
    mouth_patch = [
        (930, 234),
        (965, 244),
        (1010, 250),
        (1072, 252),
        (1134, 247),
        (1140, 270),
        (1102, 290),
        (1044, 298),
        (982, 286),
        (936, 260),
    ]
    lower_shadow = [
        (950, 262),
        (1000, 284),
        (1066, 290),
        (1124, 276),
        (1133, 292),
        (1074, 314),
        (1004, 304),
        (950, 280),
    ]
    patch_points = scaled_points(mouth_patch, scale, yoff)
    shadow_points = scaled_points(lower_shadow, scale, yoff)
    draw.polygon(patch_points, fill=(*palette["fill"], int(238 * variant["opacity"])))
    draw.polygon(shadow_points, fill=(*palette["underside"], int(94 * variant["opacity"])))
    mask_draw.polygon(patch_points, fill=255)

    seam_points = scaled_points(
        [(918, 232), (958, 240), (1005, 245), (1060, 247), (1128, 242)],
        scale,
        yoff,
    )
    draw.line(seam_points, fill=(*palette["seam"], 224), width=max(3, int(1.15 * scale)), joint="curve")
    draw.line(
        scaled_points([(958, 252), (1006, 263), (1070, 263), (1124, 254)], scale, yoff),
        fill=(*palette["highlight"], 42),
        width=max(2, int(0.75 * scale)),
        joint="curve",
    )

    for _ in range(780):
        x = rng.randrange(930 * scale, 1134 * scale)
        y = rng.randrange((235 + yoff) * scale, (302 + yoff) * scale)
        if mask.getpixel((x, y)) < 20:
            continue
        tone = rng.choice([palette["fill"], palette["underside"], palette["highlight"]])
        alpha = rng.randrange(3, 18)
        draw.point((x, y), fill=(*tone, alpha))

    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=1.7 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.12 * scale))
    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")

    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.resize(base.size, Image.Resampling.LANCZOS).save(mask_output)
    result.crop((820, 145, 1152, 390)).save(crop_output)


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    tiles = []
    font = ImageFont.load_default()
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:58], fill=(38, 35, 31), font=font)
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
    parser.add_argument("--prefix", default="herrerasaurus_closed_jaw_local_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source open jaw")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        crop_output = out_dir / f"{args.prefix}_{variant_name}-head-crop.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        draw_closed_jaw(source, output, crop_output, mask_output, variant_name)
        items.append((output, f"local closed jaw guide {variant_name}"))
        print(output)
        print(crop_output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
