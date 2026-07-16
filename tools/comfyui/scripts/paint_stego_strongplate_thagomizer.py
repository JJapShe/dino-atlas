import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "assets" / "dinosaurs" / "stegosaurus-stenops-strong-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"scale": 0.925, "xoff": 18, "yoff": 24, "anchor": (1113, 421), "spread": 0.92, "length": 1.0},
    "v1b": {"scale": 0.920, "xoff": 8, "yoff": 28, "anchor": (1112, 421), "spread": 0.82, "length": 0.88},
    "v1c": {"scale": 0.935, "xoff": 0, "yoff": 20, "anchor": (1114, 421), "spread": 0.76, "length": 0.78},
    "v2a": {"scale": 0.950, "xoff": -10, "yoff": 16, "anchor": (1115, 421), "spread": 0.78, "length": 0.72},
}


def average_color(image, box):
    x0, y0, x1, y1 = box
    x0 = max(0, min(image.width - 1, int(x0)))
    x1 = max(x0 + 1, min(image.width, int(x1)))
    y0 = max(0, min(image.height - 1, int(y0)))
    y1 = max(y0 + 1, min(image.height, int(y1)))
    return image.crop((x0, y0, x1, y1)).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def make_subject_mask(size):
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    body = [
        (48, 374),
        (114, 330),
        (215, 305),
        (318, 212),
        (476, 95),
        (612, 74),
        (762, 168),
        (875, 314),
        (1072, 367),
        (1148, 400),
        (1148, 448),
        (1030, 458),
        (872, 458),
        (774, 520),
        (650, 584),
        (505, 590),
        (360, 556),
        (230, 540),
        (110, 498),
        (52, 438),
    ]
    draw.polygon(body, fill=255)
    draw.line([(745, 413), (890, 415), (1025, 421), (1148, 430)], fill=255, width=70)
    draw.line([(122, 398), (72, 402), (48, 420)], fill=255, width=54)

    # Legs and feet.
    draw.line([(196, 500), (205, 578), (190, 630)], fill=255, width=62)
    draw.line([(255, 512), (260, 592), (238, 648)], fill=255, width=48)
    draw.line([(705, 494), (690, 598), (680, 648)], fill=255, width=70)
    draw.line([(786, 492), (820, 590), (850, 642)], fill=255, width=58)
    draw.line([(166, 639), (236, 638)], fill=255, width=26)
    draw.line([(226, 650), (291, 650)], fill=255, width=24)
    draw.line([(660, 650), (724, 650)], fill=255, width=26)
    draw.line([(826, 644), (894, 642)], fill=255, width=24)

    mask = mask.filter(ImageFilter.GaussianBlur(radius=3.0))
    return mask


def inpaint_background(base, mask):
    try:
        import cv2
        import numpy as np
    except Exception:
        return base.filter(ImageFilter.GaussianBlur(radius=18)).convert("RGBA")

    cv_base = cv2.cvtColor(np.array(base.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.point(lambda p: 255 if p > 18 else 0))
    repaired = cv2.inpaint(cv_base, cv_mask, 15, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB)).convert("RGBA")


def paste_subject(base, background, subject_mask, scale, xoff, yoff):
    subject = base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS).convert("RGBA")
    alpha = subject_mask.resize(subject.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=0.8))
    subject.putalpha(alpha)

    canvas = background.copy()
    src_x0 = max(0, -xoff)
    src_y0 = max(0, -yoff)
    dst_x = max(0, xoff)
    dst_y = max(0, yoff)
    width = min(subject.width - src_x0, canvas.width - dst_x)
    height = min(subject.height - src_y0, canvas.height - dst_y)
    if width > 0 and height > 0:
        visible = subject.crop((src_x0, src_y0, src_x0 + width, src_y0 + height))
        canvas.alpha_composite(visible, (dst_x, dst_y))
    return canvas


def point_scale(point, scale):
    return (int(point[0] * scale), int(point[1] * scale))


def draw_thagomizer(canvas, anchor, spread, length, variant_name):
    scale = 4
    large = canvas.resize((canvas.width * scale, canvas.height * scale), Image.Resampling.BICUBIC)
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    ax, ay = anchor

    tail_color = average_color(canvas.convert("RGB"), (ax - 92, ay - 20, ax - 14, ay + 20))
    base_fill = (
        max(40, int(tail_color[0] * 0.58)),
        max(32, int(tail_color[1] * 0.55)),
        max(24, int(tail_color[2] * 0.50)),
        224,
    )
    spike_fill = (
        min(176, int(tail_color[0] * 0.88 + 34)),
        min(146, int(tail_color[1] * 0.82 + 24)),
        min(108, int(tail_color[2] * 0.74 + 16)),
        238,
    )

    def p(dx, dy):
        return (ax + dx * spread, ay + dy * spread)

    pad = [p(-55, -13), p(15, -11), p(40, 4), p(22, 24), p(-50, 21), p(-70, 2)]
    draw.polygon([point_scale(point, scale) for point in pad], fill=base_fill)
    mask_draw.polygon([point_scale(point, scale) for point in pad], fill=214)

    # Side-view thagomizer: four spikes read as paired upper/lower diagonals.
    raw_spikes = [
        (p(-32, -8), p(-10, -2), p(44 * length, -66 * length)),
        (p(-4, -8), p(18, -1), p(78 * length, -42 * length)),
        (p(-34, 9), p(-11, 17), p(40 * length, 52 * length)),
        (p(-4, 12), p(20, 20), p(80 * length, 32 * length)),
    ]
    for idx, points in enumerate(raw_spikes):
        fill = (
            max(48, min(184, spike_fill[0] + idx * 3 - 6)),
            max(40, min(154, spike_fill[1] + idx * 2 - 5)),
            max(28, min(112, spike_fill[2] + idx * 2 - 5)),
            spike_fill[3] - idx * 4,
        )
        poly = [point_scale(point, scale) for point in points]
        draw.polygon(poly, fill=fill)
        mask_draw.polygon(poly, fill=244)
        base_a, base_b, tip = points
        ridge = [
            (base_a[0] * 0.58 + base_b[0] * 0.42, base_a[1] * 0.58 + base_b[1] * 0.42),
            (tip[0] * 0.84 + base_a[0] * 0.16, tip[1] * 0.84 + base_a[1] * 0.16),
        ]
        shade = [
            (base_a[0] * 0.35 + base_b[0] * 0.65, base_a[1] * 0.35 + base_b[1] * 0.65),
            (tip[0] * 0.72 + base_b[0] * 0.28, tip[1] * 0.72 + base_b[1] * 0.28),
        ]
        draw.line([point_scale(point, scale) for point in ridge], fill=(204, 174, 118, 56), width=7)
        draw.line([point_scale(point, scale) for point in shade], fill=(31, 24, 18, 78), width=8)

    rng = random.Random(sum(ord(char) for char in variant_name) + 9300)
    texture = Image.new("RGBA", large.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    for _ in range(1500):
        x = rng.randrange(max(0, int((ax - 88) * scale)), min(large.width, int((ax + 96) * scale)))
        y = rng.randrange(max(0, int((ay - 86) * scale)), min(large.height, int((ay + 86) * scale)))
        if mask.getpixel((x, y)) < 18:
            continue
        tone = rng.choice([(48, 37, 27), (112, 88, 58), (156, 128, 84), (82, 63, 42), (190, 160, 108)])
        alpha = rng.randrange(4, 22)
        if rng.random() < 0.16:
            radius = rng.randrange(1, 3)
            texture_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            texture_draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))

    shadow = Image.new("RGBA", large.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        [point_scale((ax - 82, ay + 28), scale), point_scale((ax + 92, ay + 66), scale)],
        fill=(28, 22, 17, 44),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=14))

    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.72))
    soft = mask.filter(ImageFilter.GaussianBlur(radius=2.6))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), soft))

    result = Image.alpha_composite(large, layer).resize(canvas.size, Image.Resampling.LANCZOS).convert("RGB")
    return result, mask.resize(canvas.size, Image.Resampling.LANCZOS)


def make_variant(source, output, mask_output, variant_name):
    spec = VARIANTS[variant_name]
    base = Image.open(source).convert("RGB")
    subject_mask = make_subject_mask(base.size)
    background = inpaint_background(base, subject_mask)
    canvas = paste_subject(base, background, subject_mask, spec["scale"], spec["xoff"], spec["yoff"])
    anchor = (
        int(spec["xoff"] + spec["anchor"][0] * spec["scale"]),
        int(spec["yoff"] + spec["anchor"][1] * spec["scale"]),
    )
    result, spike_mask = draw_thagomizer(canvas, anchor, spec["spread"], spec["length"], variant_name)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    spike_mask.save(mask_output)


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
    cols = min(3, len(tiles))
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
    parser.add_argument("--prefix", default="stego_strongplate_thagomizer_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [(source, "strong plate candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        make_variant(source, output, mask_output, variant_name)
        items.append((output, f"reframed thagomizer {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
