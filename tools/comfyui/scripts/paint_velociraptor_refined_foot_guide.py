import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "velociraptor-mongoliensis-refined-plumage-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Coordinates are tuned to the current refined-plumage Velociraptor candidate.
# Keep the sickle-claw cue modest; oversized hooks read as fantasy talons.
VARIANTS = {
    "v1a": {
        "front": {
            "toe_base": (430, 624),
            "walking": [((404, 626), (450, 626), (464, 615)), ((428, 629), (484, 631), (498, 622))],
            "sickle": ((434, 623), (447, 622), (438, 592), (424, 604)),
        },
        "rear": {
            "toe_base": (708, 636),
            "walking": [((683, 641), (728, 638), (738, 626)), ((710, 640), (758, 640), (770, 630))],
            "sickle": ((707, 633), (720, 631), (716, 600), (704, 611)),
        },
        "opacity": 0.86,
        "blur": 0.18,
        "seed": 2026062601,
    },
    "v1b": {
        "front": {
            "toe_base": (428, 625),
            "walking": [((402, 626), (448, 627), (462, 616)), ((430, 630), (480, 632), (494, 624))],
            "sickle": ((430, 623), (443, 622), (432, 597), (421, 608)),
        },
        "rear": {
            "toe_base": (707, 636),
            "walking": [((682, 640), (728, 638), (740, 628)), ((710, 641), (754, 642), (766, 632))],
            "sickle": ((704, 633), (717, 632), (710, 605), (700, 615)),
        },
        "opacity": 0.78,
        "blur": 0.24,
        "seed": 2026062602,
    },
    "rear_focus_v1": {
        "rear": {
            "toe_base": (708, 636),
            "walking": [((682, 641), (730, 638), (740, 627)), ((710, 640), (758, 640), (770, 630))],
            "sickle": ((706, 633), (721, 631), (716, 597), (702, 611)),
        },
        "opacity": 0.90,
        "blur": 0.16,
        "seed": 2026062603,
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


def color_mix(a, b, ratio):
    return tuple(int(a[i] * (1 - ratio) + b[i] * ratio) for i in range(3))


def bezier(p0, p1, p2, t):
    mt = 1.0 - t
    return (
        mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
        mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1],
    )


def draw_curved_claw(draw, mask_draw, base_a, base_b, tip, hook, fill, highlight, scale):
    base_center = ((base_a[0] + base_b[0]) * 0.5, (base_a[1] + base_b[1]) * 0.5)
    left = []
    right = []
    for step in range(9):
        t = step / 8
        point = bezier(base_center, hook, tip, t)
        next_point = bezier(base_center, hook, tip, min(1.0, t + 0.08))
        tangent = (next_point[0] - point[0], next_point[1] - point[1])
        length = max(1.0, (tangent[0] * tangent[0] + tangent[1] * tangent[1]) ** 0.5)
        normal = (-tangent[1] / length, tangent[0] / length)
        width = 5.2 * (1 - t) + 1.0 * t
        left.append((point[0] + normal[0] * width, point[1] + normal[1] * width))
        right.append((point[0] - normal[0] * width, point[1] - normal[1] * width))
    points = [scale_point(point, scale) for point in left + list(reversed(right))]
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=245)
    ridge = [bezier(base_center, hook, tip, t / 5) for t in range(1, 5)]
    draw.line([scale_point(point, scale) for point in ridge], fill=highlight, width=max(1, int(0.82 * scale)))


def draw_walking_toe(draw, mask_draw, base, mid, tip, fill, highlight, scale):
    p0 = base
    p1 = mid
    p2 = tip
    left = []
    right = []
    for step in range(7):
        t = step / 6
        point = bezier(p0, p1, p2, t)
        next_point = bezier(p0, p1, p2, min(1.0, t + 0.09))
        tangent = (next_point[0] - point[0], next_point[1] - point[1])
        length = max(1.0, (tangent[0] * tangent[0] + tangent[1] * tangent[1]) ** 0.5)
        normal = (-tangent[1] / length, tangent[0] / length)
        width = 4.3 * (1 - t) + 1.4 * t
        left.append((point[0] + normal[0] * width, point[1] + normal[1] * width))
        right.append((point[0] - normal[0] * width, point[1] - normal[1] * width))
    toe = [scale_point(point, scale) for point in left + list(reversed(right))]
    draw.polygon(toe, fill=fill)
    mask_draw.polygon(toe, fill=210)
    claw = [
        (tip[0] - 1.5, tip[1] - 3.0),
        (tip[0] + 12.0, tip[1] - 1.5),
        (tip[0] + 2.0, tip[1] + 4.0),
    ]
    draw.polygon([scale_point(point, scale) for point in claw], fill=(24, 20, 18, fill[3]))
    mask_draw.polygon([scale_point(point, scale) for point in claw], fill=230)
    draw.line([scale_point(p0, scale), scale_point(p2, scale)], fill=highlight, width=max(1, int(0.45 * scale)))


def draw_foot(draw, mask_draw, foot, palette, alpha, scale):
    toe_fill = (*palette["toe"], int(54 * alpha))
    toe_high = (*palette["highlight"], int(24 * alpha))
    claw_fill = (*palette["claw"], int(220 * alpha))
    claw_high = (*palette["highlight"], int(58 * alpha))
    base = foot["toe_base"]
    for mid, tip, claw_tip in foot["walking"]:
        del claw_tip
        draw_walking_toe(draw, mask_draw, base, mid, tip, toe_fill, toe_high, scale)

    base_a, base_b, tip, hook = foot["sickle"]
    draw_curved_claw(draw, mask_draw, base_a, base_b, tip, hook, claw_fill, claw_high, scale)


def draw_variant(source, output, mask_output, variant_name):
    spec = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    foot_color = average_color(base, (388, 590, 782, 656))
    palette = {
        "toe": color_mix(foot_color, (42, 31, 24), 0.36),
        "claw": tuple(max(16, int(channel * 0.30)) for channel in foot_color),
        "highlight": color_mix(foot_color, (236, 218, 171), 0.48),
    }

    for foot_name in ("front", "rear"):
        if foot_name in spec:
            draw_foot(draw, mask_draw, spec[foot_name], palette, spec["opacity"], scale)

    rng = random.Random(spec["seed"])
    texture = Image.new("RGBA", large.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    tones = [palette["toe"], palette["claw"], palette["highlight"]]
    bbox = mask.getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        for _ in range(500):
            x = rng.randrange(x0, x1)
            y = rng.randrange(y0, y1)
            if mask.getpixel((x, y)) < 16:
                continue
            tone = rng.choice(tones)
            texture_draw.point((x, y), fill=(*tone, rng.randrange(8, 28)))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=spec["blur"] * scale))
    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=1.0 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft_mask))

    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)

    inpaint = Image.new("L", base.size, 0)
    inpaint_draw = ImageDraw.Draw(inpaint)
    if "front" in spec:
        inpaint_draw.polygon([(382, 592), (522, 588), (532, 666), (392, 666)], fill=255)
    if "rear" in spec:
        inpaint_draw.polygon([(662, 598), (792, 594), (804, 680), (666, 680)], fill=255)
    inpaint = inpaint.filter(ImageFilter.GaussianBlur(radius=2.0))
    Image.merge("RGB", (inpaint, inpaint, inpaint)).save(mask_output)


def make_crop_sheet(items, output):
    crops = [("front foot", (360, 550, 560, 690)), ("rear foot", (620, 565, 830, 700))]
    tile_w, tile_h = 340, 232
    label_h = 42
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        for crop_label, box in crops:
            crop = image.crop(box)
            crop.thumbnail((tile_w, tile_h))
            tile = Image.new("RGB", (tile_w, tile_h + label_h), (245, 243, 236))
            tile.paste(crop, ((tile_w - crop.width) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((10, tile_h + 12), f"{label} {crop_label}"[:54], fill=(42, 39, 35), font=ImageFont.load_default())
            tiles.append(tile)

    cols = 4
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
    parser.add_argument("--prefix", default="velo_refined_foot_guide_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "source")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        draw_variant(source, output, mask_output, variant_name)
        items.append((output, variant_name))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-crop-sheet.png"
    make_crop_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
