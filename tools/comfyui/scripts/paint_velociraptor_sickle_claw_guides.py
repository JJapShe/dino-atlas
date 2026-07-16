import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "assets" / "dinosaurs" / "velociraptor-mongoliensis-background-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {
        "left": [((420, 613), (447, 615), (430, 568)), ((452, 612), (478, 614), (476, 650))],
        "right": [((682, 633), (706, 631), (704, 588)), ((712, 631), (742, 633), (748, 664))],
    },
    "v1b": {
        "left": [((414, 615), (442, 616), (421, 576)), ((450, 614), (476, 616), (472, 646))],
        "right": [((674, 634), (700, 632), (694, 594)), ((710, 632), (738, 634), (742, 660))],
    },
    "v2a": {
        "left": [((422, 612), (452, 614), (438, 560)), ((456, 612), (484, 616), (484, 654))],
        "right": [((680, 632), (710, 630), (714, 578)), ((714, 632), (746, 635), (756, 668))],
    },
    "rear_only_v1a": {
        "right": [((680, 632), (708, 630), (704, 586)), ((716, 632), (748, 635), (754, 666))],
    },
    "rear_only_v1b": {
        "right": [((674, 633), (704, 631), (690, 592)), ((712, 633), (744, 635), (748, 660))],
    },
}


def average_color(image, box):
    x0, y0, x1, y1 = box
    x0 = max(0, min(image.width - 1, x0))
    x1 = max(x0 + 1, min(image.width, x1))
    y0 = max(0, min(image.height - 1, y0))
    y1 = max(y0 + 1, min(image.height, y1))
    return image.crop((x0, y0, x1, y1)).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def scale_point(point, scale):
    return (int(point[0] * scale), int(point[1] * scale))


def bezier(p0, p1, p2, t):
    mt = 1.0 - t
    return (
        mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
        mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1],
    )


def draw_claw(draw, mask_draw, base_a, base_b, tip, fill, scale):
    base_center = ((base_a[0] + base_b[0]) * 0.5, (base_a[1] + base_b[1]) * 0.5)
    dx = tip[0] - base_center[0]
    dy = tip[1] - base_center[1]
    length = max(1.0, (dx * dx + dy * dy) ** 0.5)
    normal = (-dy / length, dx / length)
    curve_sign = -1 if tip[1] < base_center[1] else 1
    control = (
        base_center[0] + dx * 0.48 + normal[0] * 12 * curve_sign,
        base_center[1] + dy * 0.48 + normal[1] * 12 * curve_sign,
    )

    left = []
    right = []
    for step in range(9):
        t = step / 8
        point = bezier(base_center, control, tip, t)
        next_point = bezier(base_center, control, tip, min(1.0, t + 0.06))
        tangent = (next_point[0] - point[0], next_point[1] - point[1])
        tangent_len = max(1.0, (tangent[0] * tangent[0] + tangent[1] * tangent[1]) ** 0.5)
        n = (-tangent[1] / tangent_len, tangent[0] / tangent_len)
        width = (9.5 * (1 - t) + 1.4 * t)
        left.append((point[0] + n[0] * width, point[1] + n[1] * width))
        right.append((point[0] - n[0] * width, point[1] - n[1] * width))

    points = [scale_point(point, scale) for point in left + list(reversed(right))]
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=245)

    ridge = [bezier(base_center, control, tip, t / 5) for t in range(1, 5)]
    draw.line([scale_point(point, scale) for point in ridge], fill=(190, 176, 142, 62), width=max(1, int(1.2 * scale)))


def draw_guides(source, output, mask_output, variant_name):
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    variant = VARIANTS[variant_name]

    foot_color = average_color(base, (390, 590, 735, 658))
    claw_fill = (
        max(24, int(foot_color[0] * 0.38)),
        max(20, int(foot_color[1] * 0.34)),
        max(18, int(foot_color[2] * 0.30)),
        232,
    )

    for foot_name in ("left", "right"):
        for idx, (base_a, base_b, tip) in enumerate(variant.get(foot_name, [])):
            alpha = max(190, claw_fill[3] - idx * 22)
            fill = (claw_fill[0], claw_fill[1], claw_fill[2], alpha)
            draw_claw(draw, mask_draw, base_a, base_b, tip, fill, scale)

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.34 * scale))
    edge = mask.filter(ImageFilter.GaussianBlur(radius=0.55 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge))
    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)

    # The inpaint mask should include the existing toes plus the guide claws.
    inpaint_mask = Image.new("L", base.size, 0)
    mdraw = ImageDraw.Draw(inpaint_mask)
    if "left" in variant:
        mdraw.polygon([(376, 588), (535, 588), (548, 666), (388, 666)], fill=255)
    if "right" in variant:
        mdraw.polygon([(648, 600), (790, 596), (806, 682), (650, 682)], fill=255)
    inpaint_mask = inpaint_mask.filter(ImageFilter.GaussianBlur(radius=2.0))
    Image.merge("RGB", (inpaint_mask, inpaint_mask, inpaint_mask)).save(mask_output)


def make_crop_sheet(paths, output):
    crops = [("front foot", (360, 550, 560, 690)), ("rear foot", (620, 565, 830, 700))]
    tile_w, tile_h = 320, 224
    label_h = 40
    tiles = []
    for path, label in paths:
        image = Image.open(path).convert("RGB")
        for crop_label, box in crops:
            crop = image.crop(box)
            crop.thumbnail((tile_w, tile_h))
            tile = Image.new("RGB", (tile_w, tile_h + label_h), (245, 243, 236))
            tile.paste(crop, ((tile_w - crop.width) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((10, tile_h + 10), f"{label} {crop_label}"[:48], fill=(42, 39, 35), font=ImageFont.load_default())
            tiles.append(tile)
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * (tile_h + label_h)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * tile_w, (idx // cols) * (tile_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="velo_sickle_guides_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = [(source, "source")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        draw_guides(source, output, mask_output, variant_name)
        paths.append((output, variant_name))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-crop-sheet.png"
    make_crop_sheet(paths, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
