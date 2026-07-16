import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "triceratops-horridus-identity-naturalized-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"saturation": 0.48, "contrast": 0.98, "tint": 0.22, "edge": 0.10},
    "v1b": {"saturation": 0.38, "contrast": 0.94, "tint": 0.34, "edge": 0.12},
    "v1c": {"saturation": 0.56, "contrast": 1.00, "tint": 0.16, "edge": 0.08},
    "v2a": {"saturation": 0.30, "contrast": 0.92, "tint": 0.44, "edge": 0.10},
    "v2b": {"saturation": 0.24, "contrast": 0.90, "tint": 0.52, "edge": 0.08},
    "v2c": {"saturation": 0.18, "contrast": 0.88, "tint": 0.60, "edge": 0.06},
}


def scaled(points, sx, sy):
    return [(int(x * sx), int(y * sy)) for x, y in points]


def make_frill_mask(size):
    width, height = size
    sx = width / 1152
    sy = height / 768
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    frill = [
        (132, 72),
        (252, 54),
        (344, 100),
        (384, 196),
        (362, 300),
        (292, 372),
        (206, 380),
        (126, 328),
        (94, 228),
        (104, 132),
    ]
    draw.polygon(scaled(frill, sx, sy), fill=255)

    # Keep the diagnostic horns and skull edge untouched; the pass should only
    # reduce the frill's decorative fan color, not repaint anatomy.
    keep_polys = [
        [(28, 44), (72, 50), (72, 332), (35, 330), (20, 178)],
        [(118, 46), (184, 66), (188, 338), (142, 338), (116, 172)],
        [(0, 280), (132, 256), (190, 344), (84, 420), (0, 398)],
    ]
    for poly in keep_polys:
        draw.polygon(scaled(poly, sx, sy), fill=0)

    return mask.filter(ImageFilter.GaussianBlur(radius=max(2, int(4 * sx))))


def make_frill_color_limit(image):
    source = image.convert("RGB")
    limit = Image.new("L", source.size, 0)
    src_px = source.load()
    limit_px = limit.load()
    for y in range(source.height):
        for x in range(source.width):
            r, g, b = src_px[x, y]
            sky = b > r + 8 and b > g + 2 and b > 112
            cloud = r > 180 and g > 180 and b > 170 and abs(r - g) < 34 and abs(g - b) < 48
            vegetation = g > r + 10 and g > b + 6 and g > 82
            if sky or cloud or vegetation:
                continue
            limit_px[x, y] = 255
    return limit.filter(ImageFilter.GaussianBlur(radius=1.2))


def average_color(image, box):
    x0, y0, x1, y1 = box
    x0 = max(0, min(image.width - 1, int(x0)))
    y0 = max(0, min(image.height - 1, int(y0)))
    x1 = max(x0 + 1, min(image.width, int(x1)))
    y1 = max(y0 + 1, min(image.height, int(y1)))
    return image.crop((x0, y0, x1, y1)).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def blend_colors(a, b, ratio):
    return tuple(int(a[index] * (1 - ratio) + b[index] * ratio) for index in range(3))


def naturalize_frill(source, output, variant_name):
    variant = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    sx = base.width / 1152
    sy = base.height / 768
    mask = ImageChops.multiply(make_frill_mask(base.size), make_frill_color_limit(base))

    muted = ImageEnhance.Color(base).enhance(variant["saturation"])
    muted = ImageEnhance.Contrast(muted).enhance(variant["contrast"])
    body_tone = average_color(base, (500 * sx, 330 * sy, 790 * sx, 470 * sy))
    frill_tone = average_color(base, (190 * sx, 125 * sy, 330 * sx, 290 * sy))
    tint = blend_colors(body_tone, frill_tone, 0.22)

    tint_layer = Image.new("RGB", base.size, tint)
    muted = Image.blend(muted, tint_layer, variant["tint"])

    # Put back a very soft outer rim so the frill remains readable as a shield
    # rather than flattening into the background.
    rim = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(radius=max(1, int(1.8 * sx))))
    rim_layer = Image.new("RGB", base.size, blend_colors(tint, (68, 42, 32), 0.42))
    muted = Image.composite(rim_layer, muted, rim.point(lambda p: int(p * variant["edge"])))

    result = Image.composite(muted, base, mask)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    return output


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
        draw.text((10, thumb_h + 12), label[:58], fill=(42, 39, 35), font=font)
        tiles.append(tile)

    cols = min(2, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def make_crop_sheet(items, output):
    crops = [
        ("head and frill", (0, 35, 430, 430)),
        ("frill color", (90, 45, 405, 390)),
    ]
    thumb_w, thumb_h, label_h = 340, 260, 38
    font = ImageFont.load_default()
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        for crop_label, box in crops:
            crop = image.crop(box)
            crop.thumbnail((thumb_w, thumb_h))
            tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
            tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((10, thumb_h + 10), f"{label} {crop_label}"[:54], fill=(42, 39, 35), font=font)
            tiles.append(tile)

    cols = 2
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
    parser.add_argument("--prefix", default="trike_frill_naturalize_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    items = [(source, "source naturalized candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        naturalize_frill(source, output, variant_name)
        items.append((output, f"frill naturalize {variant_name}"))
        print(output)

    contact = out_dir / f"{args.prefix}-contact-sheet.png"
    crops = out_dir / f"{args.prefix}-head-crops.png"
    make_contact_sheet(items, contact)
    make_crop_sheet(items, crops)
    print(contact)
    print(crops)


if __name__ == "__main__":
    main()
