import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "ankylosaurus-magniventris-osteoderm-detail-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v2a": {"blend": 0.28, "contrast": 1.08, "texture": 0.55, "edge": 0.10, "seed": 2026062374},
    "v2b": {"blend": 0.34, "contrast": 1.12, "texture": 0.70, "edge": 0.14, "seed": 2026062375},
    "v2c": {"blend": 0.40, "contrast": 1.16, "texture": 0.86, "edge": 0.18, "seed": 2026062376},
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


def club_mask(size, scale):
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    # Fitted to the attached left-side club in the current 1152x768 primary.
    points = [
        (10, 390),
        (28, 362),
        (72, 348),
        (124, 354),
        (160, 382),
        (168, 418),
        (138, 444),
        (88, 456),
        (34, 442),
        (6, 414),
    ]
    draw.polygon([(x * scale, y * scale) for x, y in points], fill=255)
    mask = mask.filter(ImageFilter.MinFilter(max(3, int(3 * scale) | 1)))
    return mask.filter(ImageFilter.GaussianBlur(radius=0.45 * scale))


def make_palette(source_large):
    base = average_color(source_large.convert("RGB"), (18 * 4, 360 * 4, 165 * 4, 445 * 4))
    body = average_color(source_large.convert("RGB"), (380 * 4, 365 * 4, 650 * 4, 460 * 4))
    fill = (
        clamp(int(base[0] * 0.74 + body[0] * 0.18 + 12), 82, 150),
        clamp(int(base[1] * 0.74 + body[1] * 0.18 + 10), 76, 138),
        clamp(int(base[2] * 0.72 + body[2] * 0.14 + 8), 64, 122),
    )
    shadow = tuple(max(24, int(channel * 0.48)) for channel in fill)
    highlight = tuple(clamp(int(channel * 1.23), 96, 178) for channel in fill)
    return {"fill": fill, "shadow": shadow, "highlight": highlight}


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    rng = random.Random(variant["seed"])
    base = Image.open(source).convert("RGB")
    width, height = base.size
    scale = 4
    large = base.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    mask = club_mask(base.size, scale)
    palette = make_palette(large)

    sharpened = large.filter(ImageFilter.UnsharpMask(radius=1.3 * scale, percent=92, threshold=2))
    sharpened = ImageEnhance.Contrast(sharpened).enhance(variant["contrast"])
    sharpened.putalpha(mask.point(lambda p: int(p * variant["blend"])))
    base_with_detail = Image.alpha_composite(large, sharpened)

    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    mask_pix = mask.load()

    x0, y0, x1, y1 = mask.getbbox()

    # Low bony scute texture inside the existing club; no silhouette or color wash.
    for _ in range(int(165 * variant["texture"])):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if mask_pix[x, y] < 96:
            continue
        tone = rng.choice([palette["shadow"], palette["fill"], palette["highlight"], (62, 54, 43)])
        radius = rng.uniform(0.45 * scale, 1.35 * scale)
        alpha = rng.randrange(5, 18)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))

    # A few subtle polygonal facets give the club a bony, fused look without
    # turning it into a spiked mace or a pasted oval.
    for _ in range(9):
        x = rng.randrange(int(35 * scale), int(152 * scale))
        y = rng.randrange(int(358 * scale), int(440 * scale))
        if mask_pix[x, y] < 128:
            continue
        w = rng.uniform(3.5 * scale, 7.0 * scale)
        h = rng.uniform(3.0 * scale, 5.5 * scale)
        pts = [
            (x - w * 0.55, y),
            (x - w * 0.20, y - h * 0.50),
            (x + w * 0.35, y - h * 0.35),
            (x + w * 0.55, y + h * 0.10),
            (x + w * 0.12, y + h * 0.55),
            (x - w * 0.45, y + h * 0.40),
        ]
        draw.polygon(pts, fill=(*palette["highlight"], int(9 * variant["texture"])))
        draw.line(pts + [pts[0]], fill=(*palette["shadow"], int(18 * variant["edge"])), width=max(1, int(0.25 * scale)))

    edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(radius=0.55 * scale))
    edge_layer = Image.new("RGBA", large.size, (*palette["shadow"], 0))
    edge_layer.putalpha(edge.point(lambda p: int(p * variant["edge"])))
    layer = Image.alpha_composite(layer, edge_layer)
    result = Image.alpha_composite(base_with_detail, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")

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


def crop_tail_club(path):
    image = Image.open(path).convert("RGB")
    return image.crop((0, 310, 245, 500))


def make_crop_sheet(items, output):
    thumb_w, thumb_h = 320, 248
    label_h = 38
    tiles = []
    for path, label in items:
        crop = crop_tail_club(path)
        crop.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (244, 241, 235))
        tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 10), label[:48], fill=(38, 35, 31), font=ImageFont.load_default())
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
    parser.add_argument("--prefix", default="anky_tailclub_surface_v2")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    items = [(source, "source: attached tail club")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"club surface texture {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_sheet = out_dir / f"{args.prefix}-tailclub-crops.png"
    make_contact_sheet(items, sheet)
    make_crop_sheet(items, crop_sheet)
    print(sheet)
    print(crop_sheet)


if __name__ == "__main__":
    main()
