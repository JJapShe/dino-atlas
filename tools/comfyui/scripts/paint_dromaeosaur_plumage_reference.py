import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "assets" / "dinosaurs" / "velociraptor-mongoliensis-background-v1.png"
DEFAULT_OUTPUT = (
    ROOT
    / "tools"
    / "comfyui"
    / "lora_training"
    / "dromaeosaur_feathered"
    / "references"
    / "dromaeosaur_plumage_reference_v1.png"
)


def scaled(point, sx, sy):
    return (int(point[0] * sx), int(point[1] * sy))


def make_mask(size, sx, sy):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # Broad body, neck, tail, and folded-arm areas on the current app candidate.
    draw.ellipse((int(315 * sx), int(250 * sy), int(745 * sx), int(535 * sy)), fill=235)
    draw.polygon(
        [
            scaled((190, 185), sx, sy),
            scaled((325, 214), sx, sy),
            scaled((442, 318), sx, sy),
            scaled((402, 382), sx, sy),
            scaled((265, 335), sx, sy),
            scaled((170, 245), sx, sy),
        ],
        fill=225,
    )
    draw.polygon(
        [
            scaled((690, 325), sx, sy),
            scaled((1085, 205), sx, sy),
            scaled((1125, 245), sx, sy),
            scaled((740, 410), sx, sy),
        ],
        fill=210,
    )
    draw.polygon(
        [
            scaled((394, 335), sx, sy),
            scaled((548, 348), sx, sy),
            scaled((590, 456), sx, sy),
            scaled((462, 490), sx, sy),
            scaled((386, 432), sx, sy),
        ],
        fill=240,
    )
    return mask.filter(ImageFilter.GaussianBlur(radius=max(2, int(2.4 * sx))))


def draw_random_feathers(layer, mask, bounds, count, direction, colors, sx, sy, seed):
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = [int(value) for value in bounds]
    dx, dy = direction
    for _ in range(count):
        x = rng.randrange(max(0, x0), min(layer.width, x1))
        y = rng.randrange(max(0, y0), min(layer.height, y1))
        if mask.getpixel((x, y)) < 24:
            continue
        length = rng.uniform(14, 42) * sx
        jitter = rng.uniform(-0.36, 0.36)
        end = (
            x + int((dx + jitter) * length),
            y + int((dy + rng.uniform(-0.18, 0.18)) * length),
        )
        width = max(1, int(rng.choice([1.2, 1.5, 1.8, 2.2]) * sx))
        color = rng.choice(colors)
        draw.line((x, y, end[0], end[1]), fill=color, width=width)
        if rng.random() < 0.18:
            barb = (int((x + end[0]) / 2), int((y + end[1]) / 2))
            draw.line(
                (barb[0], barb[1], barb[0] + int(8 * sx), barb[1] - int(6 * sy)),
                fill=color,
                width=max(1, width - 1),
            )


def draw_folded_wing(layer, sx, sy):
    draw = ImageDraw.Draw(layer)
    quill = (52, 34, 22, 178)
    warm = (151, 92, 48, 168)
    light = (220, 184, 118, 118)
    shadow = (35, 26, 20, 138)

    left_anchor = scaled((392, 337), sx, sy)
    right_anchor = scaled((468, 345), sx, sy)
    for index in range(10):
        offset = index * 10
        start = (left_anchor[0] + int(offset * sx), left_anchor[1] + int((index % 3) * 5 * sy))
        end = scaled((458 + offset * 0.8, 496 - index * 2), sx, sy)
        draw.line((start[0], start[1], end[0], end[1]), fill=shadow if index % 2 else warm, width=max(3, int(3 * sx)))
        draw.line((start[0] + 4, start[1] - 2, end[0] + 3, end[1] - 4), fill=light, width=max(1, int(1.2 * sx)))

    for index in range(8):
        offset = index * 11
        start = (right_anchor[0] + int(offset * sx), right_anchor[1] + int((index % 2) * 6 * sy))
        end = scaled((533 + offset * 0.5, 484 - index * 1.4), sx, sy)
        draw.line((start[0], start[1], end[0], end[1]), fill=quill if index % 2 else warm, width=max(2, int(2.6 * sx)))
        draw.line((start[0] + 3, start[1] - 1, end[0] + 2, end[1] - 3), fill=light, width=max(1, int(1.1 * sx)))


def draw_outline_tufts(layer, sx, sy):
    draw = ImageDraw.Draw(layer)
    dark = (45, 30, 20, 178)
    warm = (134, 78, 43, 164)
    light = (211, 166, 104, 102)

    back_path = [
        (206, 211),
        (268, 224),
        (330, 248),
        (405, 266),
        (510, 286),
        (625, 303),
        (720, 322),
    ]
    for index, (x, y) in enumerate(back_path):
        tip = (x + 16 + (index % 3) * 5, y - 28 - (index % 4) * 5)
        base_a = (x - 9, y + 6)
        base_b = (x + 15, y + 4)
        fill = warm if index % 2 else dark
        draw.polygon([scaled(base_a, sx, sy), scaled(base_b, sx, sy), scaled(tip, sx, sy)], fill=fill)
        draw.line([scaled(((base_a[0] + base_b[0]) / 2, y + 1), sx, sy), scaled(tip, sx, sy)], fill=light, width=max(1, int(1.2 * sx)))


def paint_plumage(source, output):
    base = Image.open(source).convert("RGB")
    sx = base.width / 1152
    sy = base.height / 768
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    mask = make_mask(base.size, sx, sy)

    warm_dark = [
        (49, 31, 20, 86),
        (84, 48, 28, 94),
        (132, 77, 42, 78),
        (182, 124, 72, 58),
    ]
    cream = [
        (222, 196, 142, 72),
        (188, 150, 88, 64),
        (238, 214, 166, 58),
    ]

    draw_random_feathers(layer, mask, (290 * sx, 235 * sy, 760 * sx, 520 * sy), 1100, (0.64, -0.12), warm_dark, sx, sy, 9101)
    draw_random_feathers(layer, mask, (175 * sx, 175 * sy, 430 * sx, 380 * sy), 480, (0.52, -0.18), warm_dark + cream, sx, sy, 9102)
    draw_random_feathers(layer, mask, (330 * sx, 340 * sy, 620 * sx, 520 * sy), 420, (0.36, 0.62), warm_dark + cream, sx, sy, 9104)
    draw_folded_wing(layer, sx, sy)
    draw_outline_tufts(layer, sx, sy)

    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(0.25, 0.45 * sx)))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    result = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    return result


def make_contact_sheet(source, output, sheet_output):
    thumb_w, thumb_h = 440, 294
    items = [(source, "current app candidate"), (output, "project-owned plumage reference")]
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + 44), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label, fill=(42, 39, 35), font=ImageFont.load_default())
        tiles.append(tile)
    sheet = Image.new("RGB", (thumb_w * len(tiles), thumb_h + 44), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    sheet_output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--sheet-output")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    sheet_output = Path(args.sheet_output).resolve() if args.sheet_output else output.with_name(output.stem + "-sheet.png")
    paint_plumage(source, output)
    make_contact_sheet(source, output, sheet_output)
    print(output)
    print(sheet_output)


if __name__ == "__main__":
    main()
