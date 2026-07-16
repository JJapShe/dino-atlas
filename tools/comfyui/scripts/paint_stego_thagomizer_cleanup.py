import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_DIR / "stegosaurus-stenops-dorsal-plate-lock-v2-thagomizer-v1.png"
DEFAULT_OUTPUT = ASSET_DIR / "stegosaurus-stenops-thagomizer-softclean-v1.png"
DEFAULT_SHEET = ASSET_DIR / "stegosaurus-thagomizer-softclean-crops-v1.png"


def scaled(points, sx, sy):
    return [(int(x * sx), int(y * sy)) for x, y in points]


def average_color(image, box):
    return image.crop(box).resize((1, 1), Image.Resampling.BICUBIC).getpixel((0, 0))


def blend(a, b, ratio):
    return tuple(int(a[i] * (1 - ratio) + b[i] * ratio) for i in range(3))


def draw_spike(layer, mask, points, fill, outline, seed):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    draw.polygon(points, fill=(*fill, 230))
    draw.line(points + [points[0]], fill=(*outline, 210), width=2)
    mask_draw.polygon(points, fill=255)

    rng = random.Random(seed)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    texture_mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(texture_mask).polygon(points, fill=210)
    pix = texture_mask.load()
    for _ in range(90):
        x = rng.randrange(min(xs), max(xs) + 1)
        y = rng.randrange(min(ys), max(ys) + 1)
        if pix[x, y] < 32:
            continue
        tone = blend(fill, rng.choice([(36, 30, 24), (190, 174, 146), (93, 74, 55)]), rng.uniform(0.12, 0.32))
        texture_draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(*tone, rng.randrange(14, 36)))
    texture.putalpha(texture_mask.filter(ImageFilter.GaussianBlur(0.4)))
    layer.alpha_composite(texture)


def clean_tail_strings(image, sx, sy):
    cleanup = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(cleanup)
    lines = [
        [(1016, 360), (1040, 430)],
        [(1060, 370), (1085, 492)],
        [(1104, 368), (1134, 472)],
    ]
    for line in lines:
        draw.line(scaled(line, sx, sy), fill=210, width=max(3, int(4 * sx)))
    cleanup = cleanup.filter(ImageFilter.GaussianBlur(max(1, int(1.2 * sx))))
    softened = image.filter(ImageFilter.GaussianBlur(max(2, int(3.2 * sx))))
    return Image.composite(softened, image, cleanup)


def make_candidate(source, output):
    base = Image.open(source).convert("RGB")
    sx = base.width / 1152
    sy = base.height / 768
    cleaned = clean_tail_strings(base, sx, sy)
    output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.save(output)
    return output


def make_rejected_overlay_candidate(source, output):
    base = Image.open(source).convert("RGB")
    sx = base.width / 1152
    sy = base.height / 768
    cleaned = clean_tail_strings(base, sx, sy).convert("RGBA")
    layer = Image.new("RGBA", cleaned.size, (0, 0, 0, 0))
    mask = Image.new("L", cleaned.size, 0)

    tail_tone = average_color(base, (930 * sx, 282 * sy, 1062 * sx, 350 * sy))
    dark = blend(tail_tone, (28, 23, 20), 0.45)
    light = blend(tail_tone, (194, 176, 148), 0.18)
    outline = blend(tail_tone, (25, 20, 18), 0.58)

    # Four attached, opaque thagomizer spikes. They are deliberately narrow in
    # side view, but wide enough to avoid the previous wire-like artifact read.
    spikes = [
        [(1051, 332), (1108, 240), (1084, 348)],
        [(1092, 350), (1146, 275), (1116, 377)],
        [(1038, 358), (1098, 420), (1064, 382)],
        [(1084, 376), (1140, 436), (1102, 400)],
    ]
    fills = [dark, dark, light, light]
    for idx, spike in enumerate(spikes):
        draw_spike(layer, mask, scaled(spike, sx, sy), fills[idx], outline, 2026063600 + idx)

    # Small attachment pad so the spikes read as growing from the tail tip.
    draw = ImageDraw.Draw(layer)
    pad = scaled([(1018, 336), (1074, 322), (1112, 356), (1074, 392), (1020, 382)], sx, sy)
    draw.polygon(pad, fill=(*blend(tail_tone, light, 0.12), 190))
    draw.line(pad + [pad[0]], fill=(*outline, 150), width=max(1, int(1.5 * sx)))
    ImageDraw.Draw(mask).polygon(pad, fill=180)

    layer = layer.filter(ImageFilter.GaussianBlur(0.18 * sx))
    mask = mask.filter(ImageFilter.GaussianBlur(max(1, int(1.0 * sx))))
    result = Image.alpha_composite(cleaned, layer).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    return output


def make_crop_sheet(items, output):
    crops = [
        ("full body", (0, 90, 1152, 640)),
        ("dorsal plates", (205, 125, 855, 370)),
        ("tail thagomizer", (835, 205, 1152, 515)),
        ("rear leg + tail base", (670, 310, 1020, 650)),
    ]
    tile_w, image_h, label_h = 330, 220, 42
    font = ImageFont.load_default()
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        sx = image.width / 1152
        sy = image.height / 768
        for crop_label, box in crops:
            scaled_box = tuple(int(value * (sx if index % 2 == 0 else sy)) for index, value in enumerate(box))
            crop = image.crop(scaled_box)
            crop.thumbnail((tile_w, image_h), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (tile_w, image_h + label_h), (247, 244, 237))
            tile.paste(crop, ((tile_w - crop.width) // 2, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((10, image_h + 8), f"{label} {crop_label}"[:58], fill=(42, 38, 32), font=font)
            tiles.append(tile)

    cols = 4
    gap = 10
    header_h = 66
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w + (cols + 1) * gap, header_h + rows * (image_h + label_h + gap) + gap), (225, 220, 210))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, header_h), fill=(70, 70, 56))
    draw.text((20, 18), "Stegosaurus plate and thagomizer review crops", fill=(248, 246, 239), font=font)
    draw.text((20, 40), "Check separated dorsal plates, low quadruped body, and four attached tail spikes.", fill=(226, 224, 210), font=font)
    for idx, tile in enumerate(tiles):
        x = gap + (idx % cols) * (tile_w + gap)
        y = header_h + gap + (idx // cols) * (image_h + label_h + gap)
        sheet.paste(tile, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--sheet-output", default=str(DEFAULT_SHEET))
    parser.add_argument("--overlay-output")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    make_candidate(source, output)
    items = [(source, "previous"), (output, "soft-clean")]
    if args.overlay_output:
        overlay_output = Path(args.overlay_output).resolve()
        make_rejected_overlay_candidate(source, overlay_output)
        items.append((overlay_output, "rejected overlay"))
    make_crop_sheet(items, sheet_output)
    print(output)
    print(sheet_output)


if __name__ == "__main__":
    main()
