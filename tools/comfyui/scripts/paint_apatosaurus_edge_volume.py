import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "apatosaurus-ajax-lowneck-floodplain-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"edge": 0.28, "contrast": 1.07, "shadow": 0.22, "belly": 0.18},
    "v1b": {"edge": 0.20, "contrast": 1.05, "shadow": 0.16, "belly": 0.12},
    "v1c": {"edge": 0.36, "contrast": 1.09, "shadow": 0.28, "belly": 0.22},
    "v2a": {"edge": 0.00, "contrast": 1.03, "shadow": 0.18, "belly": 0.10, "background_cleanup": 0.70},
    "v2b": {"edge": 0.00, "contrast": 1.02, "shadow": 0.14, "belly": 0.08, "background_cleanup": 0.52},
    "v2c": {"edge": 0.08, "contrast": 1.03, "shadow": 0.18, "belly": 0.10, "background_cleanup": 0.62},
}


# Hand-fit to the current 1152x768 Apatosaurus side-profile candidate.
# It is deliberately conservative: the mask is for edge/volume blending only,
# not for changing anatomy.
BODY_POLYGON = [
    (12, 385),
    (64, 366),
    (130, 360),
    (205, 368),
    (290, 396),
    (382, 438),
    (474, 454),
    (590, 430),
    (696, 403),
    (808, 410),
    (936, 444),
    (1080, 450),
    (1142, 466),
    (1128, 478),
    (1022, 470),
    (900, 462),
    (792, 465),
    (718, 476),
    (660, 520),
    (590, 552),
    (492, 558),
    (418, 530),
    (330, 486),
    (238, 452),
    (130, 424),
    (42, 402),
]

LEGS = [
    (184, 446, 286, 603),
    (366, 432, 464, 620),
    (596, 443, 692, 627),
    (740, 434, 828, 618),
]

CONTACT_SHADOWS = [
    (132, 582, 344, 622),
    (330, 596, 498, 632),
    (570, 602, 730, 636),
    (716, 588, 866, 626),
]

BACKGROUND_ARTIFACT_REGIONS = [
    (185, 400, 294, 644),
    (356, 390, 470, 650),
    (548, 398, 688, 650),
    (704, 398, 832, 638),
]


def make_body_mask(size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(BODY_POLYGON, fill=255)
    for box in LEGS:
        draw.rounded_rectangle(box, radius=18, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=1.2))


def make_edge_mask(mask):
    dilated = mask.filter(ImageFilter.MaxFilter(13))
    eroded = mask.filter(ImageFilter.MinFilter(9))
    ring = ImageChops.subtract(dilated, eroded)
    return ring.filter(ImageFilter.GaussianBlur(radius=1.1))


def make_inner_edge_mask(mask):
    eroded = mask.filter(ImageFilter.MinFilter(15))
    inner = ImageChops.subtract(mask, eroded)
    return inner.filter(ImageFilter.GaussianBlur(radius=1.6))


def apply_body_contrast(image, mask, factor):
    enhanced = ImageEnhance.Contrast(image).enhance(factor)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.06)
    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=2.0))
    return Image.composite(enhanced, image, soft_mask)


def make_background_cleanup_mask(size, body_mask):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for box in BACKGROUND_ARTIFACT_REGIONS:
        draw.rounded_rectangle(box, radius=26, fill=255)

    # Do not blur the animal itself; the target is the stale background/mask residue.
    protected_body = body_mask.filter(ImageFilter.MaxFilter(17))
    mask = ImageChops.subtract(mask, protected_body)
    return mask.filter(ImageFilter.GaussianBlur(radius=18))


def apply_background_cleanup(image, body_mask, amount):
    if amount <= 0:
        return image
    cleanup_mask = make_background_cleanup_mask(image.size, body_mask).point(lambda p: int(p * amount))
    smoothed = image.filter(ImageFilter.GaussianBlur(radius=18))
    smoothed = ImageEnhance.Contrast(smoothed).enhance(0.92)
    return Image.composite(smoothed, image, cleanup_mask)


def apply_edge_integration(image, mask, amount):
    edge = make_edge_mask(mask)
    inner = make_inner_edge_mask(mask)
    blur = image.filter(ImageFilter.GaussianBlur(radius=2.2))
    edge_layer = ImageEnhance.Brightness(blur).enhance(0.88)
    edge_layer = ImageEnhance.Contrast(edge_layer).enhance(1.05)
    edge_alpha = edge.point(lambda p: int(p * amount))
    merged = Image.composite(edge_layer, image, edge_alpha)

    # Slightly darken only the inside rim so the body no longer has a pale cutout edge.
    rim_layer = ImageEnhance.Brightness(merged).enhance(0.92)
    inner_alpha = inner.point(lambda p: int(p * amount * 0.65))
    return Image.composite(rim_layer, merged, inner_alpha)


def apply_contact_shadow(image, shadow_strength, belly_strength):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for box in CONTACT_SHADOWS:
        draw.ellipse(box, fill=(24, 18, 12, int(185 * shadow_strength)))
    draw.ellipse((280, 462, 808, 572), fill=(32, 22, 14, int(86 * belly_strength)))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=18))
    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")


def make_variant(source, output, mask_output, variant_name):
    variant = VARIANTS[variant_name]
    image = Image.open(source).convert("RGB")
    mask = make_body_mask(image.size)
    result = apply_background_cleanup(image, mask, variant.get("background_cleanup", 0.0))
    result = apply_body_contrast(result, mask, variant["contrast"])
    if variant["edge"]:
        result = apply_edge_integration(result, mask, variant["edge"])
    result = apply_contact_shadow(result, variant["shadow"], variant["belly"])
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.save(mask_output)


def crop_silhouette(path):
    image = Image.open(path).convert("RGB")
    return image.crop((0, 300, 1152, 650))


def make_contact_sheet(items, output, crop_output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    sheets = []
    for crop_fn in (None, crop_silhouette):
        tiles = []
        for path, label in items:
            image = crop_fn(path) if crop_fn else Image.open(path).convert("RGB")
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
        sheets.append(sheet)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheets[0].save(output)
    sheets[1].save(crop_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="apato_edge_volume_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    items = [(source, "source: current low-neck floodplain")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"edge volume pass {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_sheet = out_dir / f"{args.prefix}-silhouette-crops.png"
    make_contact_sheet(items, sheet, crop_sheet)
    print(sheet)
    print(crop_sheet)


if __name__ == "__main__":
    main()
