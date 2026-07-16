import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "assets" / "dinosaurs" / "stegosaurus-stenops-natural-plates-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


VARIANTS = {
    "v1a": {"scale": 0.92, "xoff": 16, "yoff": 30, "anchor": (1110, 421), "spread": 1.00},
    "v1b": {"scale": 0.91, "xoff": 18, "yoff": 34, "anchor": (1110, 421), "spread": 0.88},
    "v1c": {"scale": 0.93, "xoff": 12, "yoff": 26, "anchor": (1110, 421), "spread": 0.82},
    "v2a": {"scale": 1.00, "xoff": -72, "yoff": 0, "anchor": (1110, 421), "spread": 0.92},
    "v2b": {"scale": 1.00, "xoff": -84, "yoff": 0, "anchor": (1110, 421), "spread": 0.82},
    "v2c": {"scale": 1.00, "xoff": -64, "yoff": 0, "anchor": (1110, 421), "spread": 0.76},
}


def average_color(image, box):
    x0, y0, x1, y1 = box
    x0 = max(0, min(image.width - 1, x0))
    x1 = max(x0 + 1, min(image.width, x1))
    y0 = max(0, min(image.height - 1, y0))
    y1 = max(y0 + 1, min(image.height, y1))
    return image.crop((x0, y0, x1, y1)).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def make_background(base):
    w, h = base.size
    bg = base.resize((int(w * 1.14), int(h * 1.14)), Image.Resampling.BICUBIC)
    left = (bg.width - w) // 2
    top = (bg.height - h) // 2
    bg = bg.crop((left, top, left + w, top + h))
    return bg.filter(ImageFilter.GaussianBlur(radius=9)).convert("RGBA")


def p(point, scale):
    return (int(point[0] * scale), int(point[1] * scale))


def draw_spike(draw, mask_draw, base_a, base_b, tip, fill, scale):
    points = [p(base_a, scale), p(base_b, scale), p(tip, scale)]
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=245)
    ridge = (
        (base_a[0] * 0.55 + base_b[0] * 0.45, base_a[1] * 0.55 + base_b[1] * 0.45),
        (tip[0] * 0.84 + base_a[0] * 0.16, tip[1] * 0.84 + base_a[1] * 0.16),
    )
    shade = (
        (base_a[0] * 0.40 + base_b[0] * 0.60, base_a[1] * 0.40 + base_b[1] * 0.60),
        (tip[0] * 0.72 + base_b[0] * 0.28, tip[1] * 0.72 + base_b[1] * 0.28),
    )
    draw.line([p(ridge[0], scale), p(ridge[1], scale)], fill=(205, 176, 120, 58), width=max(3, int(1.8 * scale)))
    draw.line([p(shade[0], scale), p(shade[1], scale)], fill=(34, 27, 20, 82), width=max(3, int(2.0 * scale)))


def draw_tail_spikes(canvas, anchor, spread, variant_name):
    scale = 4
    large = canvas.resize((canvas.width * scale, canvas.height * scale), Image.Resampling.BICUBIC)
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    ax, ay = anchor

    tail_color = average_color(canvas.convert("RGB"), (ax - 90, ay - 18, ax - 18, ay + 18))
    pad_fill = (
        max(42, int(tail_color[0] * 0.62)),
        max(34, int(tail_color[1] * 0.58)),
        max(24, int(tail_color[2] * 0.54)),
        226,
    )
    spike_fill = (
        min(178, int(tail_color[0] * 0.88 + 36)),
        min(148, int(tail_color[1] * 0.82 + 26)),
        min(108, int(tail_color[2] * 0.74 + 18)),
        238,
    )

    pad = [
        (ax - 50, ay - 12),
        (ax + 18, ay - 10),
        (ax + 42, ay + 5),
        (ax + 24, ay + 24),
        (ax - 44, ay + 20),
        (ax - 62, ay + 2),
    ]
    draw.polygon([p(point, scale) for point in pad], fill=pad_fill)
    mask_draw.polygon([p(point, scale) for point in pad], fill=215)

    def s(dx, dy):
        return ax + dx * spread, ay + dy * spread

    spikes = [
        (s(-28, -8), s(-8, -2), s(42, -66)),
        (s(0, -8), s(20, -1), s(74, -40)),
        (s(-29, 9), s(-8, 17), s(40, 50)),
        (s(0, 12), s(22, 20), s(78, 30)),
    ]
    for idx, (base_a, base_b, tip) in enumerate(spikes):
        fill = (
            max(50, min(184, spike_fill[0] + idx * 3 - 5)),
            max(42, min(154, spike_fill[1] + idx * 3 - 5)),
            max(30, min(112, spike_fill[2] + idx * 2 - 4)),
            spike_fill[3] - idx * 4,
        )
        draw_spike(draw, mask_draw, base_a, base_b, tip, fill, scale)

    rng = random.Random(sum(ord(char) for char in variant_name) + 7400)
    texture = Image.new("RGBA", large.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    for _ in range(1400):
        x = rng.randrange(max(0, int((ax - 80) * scale)), min(large.width, int((ax + 95) * scale)))
        y = rng.randrange(max(0, int((ay - 80) * scale)), min(large.height, int((ay + 82) * scale)))
        if mask.getpixel((x, y)) < 18:
            continue
        tone = rng.choice([(48, 38, 28), (112, 88, 58), (158, 130, 86), (82, 64, 42), (190, 160, 108)])
        alpha = rng.randrange(4, 23)
        if rng.random() < 0.15:
            r = rng.randrange(1, 3)
            texture_draw.ellipse((x - r, y - r, x + r, y + r), fill=(*tone, alpha))
        else:
            texture_draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))

    shadow = Image.new("RGBA", large.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        [p((ax - 70, ay + 30), scale), p((ax + 92, ay + 66), scale)],
        fill=(28, 22, 17, 46),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=12))

    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, texture)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.72))
    edge = mask.filter(ImageFilter.GaussianBlur(radius=2.6))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge))
    return Image.alpha_composite(large, layer).resize(canvas.size, Image.Resampling.LANCZOS).convert("RGB")


def composite_shift(canvas, image, xoff, yoff):
    if xoff >= 0 and yoff >= 0:
        canvas.alpha_composite(image.convert("RGBA"), (xoff, yoff))
        return

    src_x0 = max(0, -xoff)
    src_y0 = max(0, -yoff)
    dst_x = max(0, xoff)
    dst_y = max(0, yoff)
    width = min(image.width - src_x0, canvas.width - dst_x)
    height = min(image.height - src_y0, canvas.height - dst_y)
    if width <= 0 or height <= 0:
        return
    visible = image.crop((src_x0, src_y0, src_x0 + width, src_y0 + height)).convert("RGBA")
    canvas.alpha_composite(visible, (dst_x, dst_y))


def make_variant(source, output, variant_name):
    base = Image.open(source).convert("RGB")
    spec = VARIANTS[variant_name]
    bg = make_background(base)
    scaled = base.resize((int(base.width * spec["scale"]), int(base.height * spec["scale"])), Image.Resampling.LANCZOS)
    canvas = bg.copy()
    composite_shift(canvas, scaled, spec["xoff"], spec["yoff"])
    ax = int(spec["xoff"] + spec["anchor"][0] * spec["scale"])
    ay = int(spec["yoff"] + spec["anchor"][1] * spec["scale"])
    result = draw_tail_spikes(canvas, (ax, ay), spec["spread"], variant_name)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


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
    sheet = Image.new("RGB", (len(tiles) * thumb_w, thumb_h + label_h), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_right_tail_margin_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    items = [(source, "current natural plate candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        make_variant(source, output, variant_name)
        items.append((output, f"tail margin {variant_name}"))
        print(output)
    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(items, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
