import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "herrerasaurus-ischigualastensis-longarms-ipcontrol-v1.png"
DEFAULT_HEAD = ASSET_ROOT / "herrerasaurus-ischigualastensis-closedjaw-refine-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {
        "polygon": [
            (790, 314),
            (842, 234),
            (940, 192),
            (1052, 187),
            (1136, 208),
            (1150, 260),
            (1104, 326),
            (988, 344),
            (846, 332),
        ],
        "feather": 24,
        "color": 0.66,
    },
    "v1b": {
        "polygon": [
            (754, 334),
            (816, 246),
            (930, 192),
            (1060, 186),
            (1142, 210),
            (1152, 276),
            (1098, 342),
            (942, 356),
            (776, 344),
        ],
        "feather": 32,
        "color": 0.58,
    },
    "v1c": {
        "polygon": [
            (848, 326),
            (872, 224),
            (950, 192),
            (1060, 190),
            (1142, 216),
            (1150, 282),
            (1092, 334),
            (960, 338),
            (858, 320),
        ],
        "feather": 22,
        "color": 0.74,
    },
}


def mean_rgb(image, mask):
    stat = ImageStat.Stat(image.convert("RGB"), mask)
    return tuple(stat.mean)


def color_match_patch(patch, source, mask, amount):
    patch_rgb = patch.convert("RGB")
    source_mean = mean_rgb(source, mask)
    patch_mean = mean_rgb(patch_rgb, mask)
    offsets = [source_mean[idx] - patch_mean[idx] for idx in range(3)]
    lut = []
    for channel in range(3):
        offset = offsets[channel] * amount
        lut.extend(max(0, min(255, int(value + offset))) for value in range(256))
    return patch_rgb.point(lut)


def make_variant(source_path, head_path, output, mask_output, variant_name):
    spec = VARIANTS[variant_name]
    source = Image.open(source_path).convert("RGB")
    head = Image.open(head_path).convert("RGB")
    if source.size != head.size:
        head = head.resize(source.size, Image.Resampling.LANCZOS)

    hard_mask = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(hard_mask)
    draw.polygon(spec["polygon"], fill=255)
    mask = hard_mask.filter(ImageFilter.GaussianBlur(radius=spec["feather"]))
    matched_head = color_match_patch(head, source, hard_mask, spec["color"])

    result = Image.composite(matched_head, source, mask)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    mask.save(mask_output)


def crop_head(path):
    image = Image.open(path).convert("RGB")
    return image.crop((760, 150, 1152, 350))


def make_contact_sheet(items, output, crop_output):
    thumb_w, thumb_h = 384, 256
    label_h = 42
    sheets = []
    for crop_fn in (None, crop_head):
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
    parser.add_argument("--head-source", default=str(DEFAULT_HEAD))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="herrera_closedjaw_head_blend_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    head_source = Path(args.head_source).resolve()
    out_dir = Path(args.out_dir).resolve()

    items = [
        (source, "source: long-arm primary"),
        (head_source, "head source: closed-jaw comparison"),
    ]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, head_source, output, mask_output, variant_name)
        items.append((output, f"closed-jaw head blend {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_sheet = out_dir / f"{args.prefix}-head-crops.png"
    make_contact_sheet(items, sheet, crop_sheet)
    print(sheet)
    print(crop_sheet)


if __name__ == "__main__":
    main()
