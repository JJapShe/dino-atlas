import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "velociraptor-mongoliensis-dense-plumage-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v2a": {"alpha": 0.72, "density": 1.00, "wing": 0.88, "crest": 0.70, "claw": 0.76, "seed": 2026081201},
    "v2b": {"alpha": 0.86, "density": 1.18, "wing": 1.04, "crest": 0.84, "claw": 0.86, "seed": 2026081202},
    "v2c": {"alpha": 0.62, "density": 0.86, "wing": 0.72, "crest": 0.58, "claw": 0.68, "seed": 2026081203},
}


def scaled(point, sx, sy):
    return (int(point[0] * sx), int(point[1] * sy))


def sky_like(pixel):
    r, g, b = pixel
    return b > 112 and b > r + 12 and b > g + 2


def sand_like(pixel):
    r, g, b = pixel
    return r > 145 and g > 126 and b > 88 and abs(r - g) < 54 and r > b + 22


def subject_limited_mask(image, rough_mask):
    src = image.convert("RGB")
    src_px = src.load()
    rough_px = rough_mask.load()
    limit = Image.new("L", image.size, 0)
    limit_px = limit.load()
    for y in range(image.height):
        for x in range(image.width):
            if rough_px[x, y] < 12:
                continue
            pixel = src_px[x, y]
            if sky_like(pixel) or sand_like(pixel):
                continue
            limit_px[x, y] = 255
    return limit.filter(ImageFilter.GaussianBlur(radius=0.75))


def make_masks(image, sx, sy):
    size = image.size
    masks = {}
    for key in ("torso", "neck", "tail", "wing", "forearm", "rear_foot"):
        masks[key] = Image.new("L", size, 0)

    draw_torso = ImageDraw.Draw(masks["torso"])
    draw_neck = ImageDraw.Draw(masks["neck"])
    draw_tail = ImageDraw.Draw(masks["tail"])
    draw_wing = ImageDraw.Draw(masks["wing"])
    draw_forearm = ImageDraw.Draw(masks["forearm"])
    draw_rear = ImageDraw.Draw(masks["rear_foot"])

    draw_torso.ellipse((int(315 * sx), int(258 * sy), int(742 * sx), int(528 * sy)), fill=235)
    draw_torso.polygon(
        [
            scaled((276, 316), sx, sy),
            scaled((424, 270), sx, sy),
            scaled((718, 315), sx, sy),
            scaled((724, 448), sx, sy),
            scaled((470, 528), sx, sy),
            scaled((292, 440), sx, sy),
        ],
        fill=245,
    )
    draw_neck.polygon(
        [
            scaled((176, 180), sx, sy),
            scaled((318, 207), sx, sy),
            scaled((430, 335), sx, sy),
            scaled((386, 389), sx, sy),
            scaled((260, 332), sx, sy),
            scaled((166, 252), sx, sy),
        ],
        fill=238,
    )
    draw_tail.polygon(
        [
            scaled((638, 338), sx, sy),
            scaled((900, 287), sx, sy),
            scaled((1004, 304), sx, sy),
            scaled((1050, 320), sx, sy),
            scaled((716, 410), sx, sy),
        ],
        fill=160,
    )
    draw_wing.polygon(
        [
            scaled((374, 320), sx, sy),
            scaled((560, 334), sx, sy),
            scaled((634, 445), sx, sy),
            scaled((476, 508), sx, sy),
            scaled((380, 430), sx, sy),
        ],
        fill=235,
    )
    draw_forearm.polygon(
        [
            scaled((335, 360), sx, sy),
            scaled((418, 390), sx, sy),
            scaled((420, 505), sx, sy),
            scaled((345, 520), sx, sy),
            scaled((310, 438), sx, sy),
        ],
        fill=230,
    )
    draw_rear.polygon(
        [
            scaled((660, 590), sx, sy),
            scaled((794, 592), sx, sy),
            scaled((808, 676), sx, sy),
            scaled((656, 684), sx, sy),
        ],
        fill=240,
    )

    radius = max(2, int(2.1 * sx))
    rough_union = Image.new("L", size, 0)
    for key, mask in masks.items():
        blur = max(1, int((1.8 if key in ("forearm", "rear_foot") else 2.3) * sx))
        masks[key] = mask.filter(ImageFilter.GaussianBlur(radius=blur))
        rough_union = ImageChops.lighter(rough_union, masks[key])

    limit = subject_limited_mask(image, rough_union.filter(ImageFilter.GaussianBlur(radius=radius)))
    for key in masks:
        masks[key] = ImageChops.multiply(masks[key], limit)
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
        if coverage < 28:
            continue
        length = rng.uniform(*length_range) * sx
        jitter = rng.uniform(-0.25, 0.25)
        end = (
            x + int((dx + jitter) * length),
            y + int((dy + rng.uniform(-0.16, 0.16)) * length),
        )
        base = rng.choice(colors)
        alpha = int(base[3] * alpha_scale * (coverage / 255))
        if alpha <= 2:
            continue
        width = max(1, int(rng.choice([0.8, 1.0, 1.25, 1.55]) * sx))
        draw.line((x, y, end[0], end[1]), fill=(base[0], base[1], base[2], alpha), width=width)


def draw_folded_wing(layer, mask, sx, sy, alpha_scale, wing_scale):
    draw = ImageDraw.Draw(layer)
    colors = [
        (45, 30, 21, int(108 * alpha_scale * wing_scale)),
        (88, 50, 29, int(102 * alpha_scale * wing_scale)),
        (148, 88, 48, int(78 * alpha_scale * wing_scale)),
        (226, 190, 126, int(54 * alpha_scale * wing_scale)),
    ]
    for idx in range(16):
        x0 = 382 + idx * 12
        y0 = 336 + (idx % 5) * 5
        x1 = 432 + idx * 8
        y1 = 486 - idx * 2
        p0 = scaled((x0, y0), sx, sy)
        p1 = scaled((x1, y1), sx, sy)
        mid = ((p0[0] + p1[0]) // 2, (p0[1] + p1[1]) // 2)
        if mask.getpixel(mid) < 22:
            continue
        draw.line([p0, p1], fill=colors[idx % len(colors)], width=max(1, int(2.25 * sx)))
        if idx % 3 == 0:
            draw.line(
                [p0, scaled((x1 + 18, y1 - 4), sx, sy)],
                fill=(240, 210, 152, int(24 * alpha_scale * wing_scale)),
                width=max(1, int(0.85 * sx)),
            )


def draw_neck_crest(layer, mask, sx, sy, alpha_scale, crest_scale):
    draw = ImageDraw.Draw(layer)
    for idx in range(18):
        x = 208 + idx * 13
        y = 187 + idx * 6
        p0 = scaled((x, y), sx, sy)
        p1 = scaled((x + 14, y - 18 - (idx % 3) * 4), sx, sy)
        if mask.getpixel(p0) < 24:
            continue
        draw.line(
            [p0, p1],
            fill=(72, 42, 25, int(78 * alpha_scale * crest_scale)),
            width=max(1, int(1.35 * sx)),
        )


def draw_sickle_claw(layer, mask, sx, sy, alpha_scale):
    draw = ImageDraw.Draw(layer)
    # Rear foot second-toe claw cue. Keep it modest; oversized claws read as fantasy.
    claw_points = [
        scaled((704, 628), sx, sy),
        scaled((724, 626), sx, sy),
        scaled((724, 574), sx, sy),
        scaled((710, 586), sx, sy),
    ]
    if mask.getpixel(scaled((715, 626), sx, sy)) < 18:
        return
    draw.polygon(claw_points, fill=(30, 24, 20, int(188 * alpha_scale)))
    draw.line(
        [scaled((716, 625), sx, sy), scaled((722, 579), sx, sy)],
        fill=(218, 202, 160, int(52 * alpha_scale)),
        width=max(1, int(1.0 * sx)),
    )
    toe_points = [
        scaled((682, 636), sx, sy),
        scaled((722, 632), sx, sy),
        scaled((724, 644), sx, sy),
        scaled((684, 650), sx, sy),
    ]
    draw.polygon(toe_points, fill=(52, 38, 28, int(72 * alpha_scale)))


def paint(source, output, variant_name):
    spec = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    sx = base.width / 1152
    sy = base.height / 768
    masks = make_masks(base, sx, sy)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

    dark = [(42, 28, 20, 64), (65, 39, 25, 70), (98, 58, 32, 58)]
    warm = [(132, 78, 42, 54), (172, 110, 62, 46), (214, 166, 104, 34)]
    cream = [(230, 207, 160, 38), (188, 153, 92, 36), (246, 226, 180, 25)]

    density = spec["density"]
    alpha = spec["alpha"]
    seed = spec["seed"]
    draw_strokes(layer, masks["torso"], (290 * sx, 250 * sy, 748 * sx, 535 * sy), int(2100 * density), (0.56, -0.04), (5, 24), dark + warm, sx, sy, seed + 1, alpha)
    draw_strokes(layer, masks["neck"], (165 * sx, 175 * sy, 438 * sx, 398 * sy), int(900 * density), (0.38, -0.18), (5, 21), dark + warm + cream, sx, sy, seed + 2, alpha)
    draw_strokes(layer, masks["tail"], (638 * sx, 286 * sy, 1054 * sx, 424 * sy), int(520 * density), (0.78, -0.05), (4, 17), dark + warm, sx, sy, seed + 3, alpha * 0.62)
    draw_strokes(layer, masks["wing"], (368 * sx, 315 * sy, 646 * sx, 512 * sy), int(760 * density), (0.32, 0.66), (7, 28), dark + warm + cream, sx, sy, seed + 4, alpha)
    draw_strokes(layer, masks["forearm"], (305 * sx, 350 * sy, 430 * sx, 526 * sy), int(360 * density), (0.18, 0.78), (6, 22), dark + cream, sx, sy, seed + 5, alpha)
    draw_folded_wing(layer, masks["wing"], sx, sy, alpha, spec["wing"])
    draw_neck_crest(layer, masks["neck"], sx, sy, alpha, spec["crest"])
    draw_sickle_claw(layer, masks["rear_foot"], sx, sy, spec["claw"])

    total_mask = Image.new("L", base.size, 0)
    for key in ("torso", "neck", "tail", "wing", "forearm", "rear_foot"):
        total_mask = ImageChops.lighter(total_mask, masks[key])
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(0.16, 0.24 * sx)))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), total_mask))
    result = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    return output


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


def make_crop_sheet(items, output):
    crops = [
        ("wing/body", (280, 230, 660, 548)),
        ("rear foot", (625, 555, 820, 700)),
    ]
    tile_w, tile_h, label_h = 360, 260, 38
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        for crop_label, box in crops:
            crop = image.crop(box)
            crop.thumbnail((tile_w, tile_h))
            tile = Image.new("RGB", (tile_w, tile_h + label_h), (245, 243, 236))
            tile.paste(crop, ((tile_w - crop.width) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((10, tile_h + 10), f"{label} {crop_label}"[:54], fill=(42, 39, 35), font=ImageFont.load_default())
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
    parser.add_argument("--prefix", default="velo_plumage_sickle_v2")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "current dense plumage v1")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        paint(source, output, variant_name)
        items.append((output, f"plumage + sickle {variant_name}"))
        print(output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crops = out_dir / f"{args.prefix}-crop-sheet.png"
    make_contact_sheet(items, sheet)
    make_crop_sheet(items, crops)
    print(sheet)
    print(crops)


if __name__ == "__main__":
    main()
