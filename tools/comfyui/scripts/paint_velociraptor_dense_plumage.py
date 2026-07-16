import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "assets" / "dinosaurs" / "velociraptor-mongoliensis-sickleclaw-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"alpha": 0.72, "density": 1.00, "wing": 0.80},
    "v1b": {"alpha": 0.88, "density": 1.20, "wing": 0.95},
    "v1c": {"alpha": 0.58, "density": 0.82, "wing": 0.65},
}


def scaled(point, sx, sy):
    return (int(point[0] * sx), int(point[1] * sy))


def sky_like(pixel):
    r, g, b = pixel
    return b > 108 and b > r + 14 and b > g + 3


def make_subject_limit(image, rough_union):
    limit = Image.new("L", image.size, 0)
    src = image.convert("RGB")
    src_px = src.load()
    rough_px = rough_union.load()
    limit_px = limit.load()
    for y in range(image.height):
        for x in range(image.width):
            if rough_px[x, y] < 10:
                continue
            if sky_like(src_px[x, y]):
                continue
            limit_px[x, y] = 255
    return limit.filter(ImageFilter.GaussianBlur(radius=0.8))


def make_masks(image, sx, sy):
    size = image.size
    torso = Image.new("L", size, 0)
    neck = Image.new("L", size, 0)
    tail = Image.new("L", size, 0)
    wing = Image.new("L", size, 0)
    draw_torso = ImageDraw.Draw(torso)
    draw_neck = ImageDraw.Draw(neck)
    draw_tail = ImageDraw.Draw(tail)
    draw_wing = ImageDraw.Draw(wing)

    draw_torso.ellipse((int(318 * sx), int(260 * sy), int(735 * sx), int(525 * sy)), fill=235)
    draw_torso.polygon(
        [
            scaled((278, 316), sx, sy),
            scaled((420, 276), sx, sy),
            scaled((700, 314), sx, sy),
            scaled((720, 454), sx, sy),
            scaled((462, 528), sx, sy),
            scaled((292, 438), sx, sy),
        ],
        fill=242,
    )

    draw_neck.polygon(
        [
            scaled((178, 182), sx, sy),
            scaled((318, 208), sx, sy),
            scaled((425, 332), sx, sy),
            scaled((384, 386), sx, sy),
            scaled((260, 330), sx, sy),
            scaled((164, 250), sx, sy),
        ],
        fill=235,
    )

    draw_tail.polygon(
        [
            scaled((645, 342), sx, sy),
            scaled((872, 292), sx, sy),
            scaled((932, 320), sx, sy),
            scaled((706, 408), sx, sy),
        ],
        fill=160,
    )

    draw_wing.polygon(
        [
            scaled((380, 326), sx, sy),
            scaled((570, 340), sx, sy),
            scaled((626, 444), sx, sy),
            scaled((474, 500), sx, sy),
            scaled((382, 424), sx, sy),
        ],
        fill=235,
    )

    radius = max(2, int(2.4 * sx))
    masks = {
        "torso": torso.filter(ImageFilter.GaussianBlur(radius=radius)),
        "neck": neck.filter(ImageFilter.GaussianBlur(radius=radius)),
        "tail": tail.filter(ImageFilter.GaussianBlur(radius=radius)),
        "wing": wing.filter(ImageFilter.GaussianBlur(radius=max(1, int(1.8 * sx)))),
    }
    rough_union = ImageChops.lighter(ImageChops.lighter(masks["torso"], masks["neck"]), ImageChops.lighter(masks["tail"], masks["wing"]))
    subject_limit = make_subject_limit(image, rough_union)
    for key, mask in masks.items():
        masks[key] = ImageChops.multiply(mask, subject_limit)
    return masks


def draw_strokes(layer, mask, bounds, count, direction, length_range, colors, sx, sy, seed, alpha_scale):
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = [int(v) for v in bounds]
    dx, dy = direction
    for _ in range(count):
        x = rng.randrange(max(0, x0), min(layer.width, x1))
        y = rng.randrange(max(0, y0), min(layer.height, y1))
        coverage = mask.getpixel((x, y))
        if coverage < 32:
            continue
        length = rng.uniform(*length_range) * sx
        jitter = rng.uniform(-0.22, 0.22)
        end = (
            x + int((dx + jitter) * length),
            y + int((dy + rng.uniform(-0.14, 0.14)) * length),
        )
        base = rng.choice(colors)
        alpha = int(base[3] * alpha_scale * (coverage / 255))
        if alpha <= 2:
            continue
        width = max(1, int(rng.choice([0.8, 1.0, 1.2, 1.5]) * sx))
        draw.line((x, y, end[0], end[1]), fill=(base[0], base[1], base[2], alpha), width=width)


def draw_folded_wing(layer, mask, sx, sy, alpha_scale, wing_scale):
    draw = ImageDraw.Draw(layer)
    colors = [
        (52, 35, 24, int(92 * alpha_scale * wing_scale)),
        (92, 54, 31, int(88 * alpha_scale * wing_scale)),
        (172, 112, 62, int(58 * alpha_scale * wing_scale)),
        (224, 185, 116, int(42 * alpha_scale * wing_scale)),
    ]
    for idx in range(13):
        x0 = 394 + idx * 13
        y0 = 342 + (idx % 4) * 5
        x1 = 452 + idx * 8
        y1 = 474 - idx * 2
        points = [scaled((x0, y0), sx, sy), scaled((x1, y1), sx, sy)]
        mid = ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
        if mask.getpixel(mid) < 24:
            continue
        draw.line(points, fill=colors[idx % len(colors)], width=max(1, int(2.2 * sx)))


def paint_dense_plumage(source, output, variant_name):
    spec = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    sx = base.width / 1152
    sy = base.height / 768
    masks = make_masks(base, sx, sy)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

    dark = [
        (45, 29, 20, 58),
        (70, 42, 25, 62),
        (105, 62, 34, 52),
    ]
    warm = [
        (135, 82, 43, 50),
        (174, 111, 62, 42),
        (213, 164, 102, 30),
    ]
    cream = [
        (228, 205, 156, 34),
        (188, 153, 92, 34),
    ]

    density = spec["density"]
    alpha = spec["alpha"]
    draw_strokes(
        layer,
        masks["torso"],
        (292 * sx, 250 * sy, 744 * sx, 530 * sy),
        int(1700 * density),
        (0.62, -0.06),
        (5, 22),
        dark + warm,
        sx,
        sy,
        6101,
        alpha,
    )
    draw_strokes(
        layer,
        masks["neck"],
        (165 * sx, 180 * sy, 430 * sx, 392 * sy),
        int(720 * density),
        (0.42, -0.16),
        (5, 20),
        dark + warm + cream,
        sx,
        sy,
        6102,
        alpha,
    )
    draw_strokes(
        layer,
        masks["tail"],
        (640 * sx, 292 * sy, 940 * sx, 420 * sy),
        int(280 * density),
        (0.72, -0.08),
        (4, 14),
        dark + warm,
        sx,
        sy,
        6103,
        alpha * 0.55,
    )
    draw_strokes(
        layer,
        masks["wing"],
        (370 * sx, 318 * sy, 635 * sx, 505 * sy),
        int(520 * density),
        (0.36, 0.62),
        (6, 24),
        dark + warm + cream,
        sx,
        sy,
        6104,
        alpha,
    )
    draw_folded_wing(layer, masks["wing"], sx, sy, alpha, spec["wing"])

    total_mask = ImageChops.lighter(ImageChops.lighter(masks["torso"], masks["neck"]), ImageChops.lighter(masks["tail"], masks["wing"]))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(0.18, 0.28 * sx)))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), total_mask))
    result = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    return output


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 360, 240
    label_h = 42
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:54], fill=(42, 39, 35), font=ImageFont.load_default())
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
    parser.add_argument("--prefix", default="velo_dense_plumage_local_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    items = [(source, "current sickle-claw candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        paint_dense_plumage(source, output, variant_name)
        items.append((output, f"dense plumage {variant_name}"))
        print(output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
