import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "assets" / "dinosaurs" / "triceratops-identity-crops-v1.png"


CROPS = [
    ("full body", (0, 90, 1152, 705)),
    ("head + skull frill", (0, 70, 430, 475)),
    ("three horns + beak", (0, 100, 315, 405)),
    ("front and rear feet", (210, 500, 830, 735)),
    ("tail + hip", (640, 320, 1152, 610)),
]


def crop_to_tile(image, box, size):
    crop = image.crop(box)
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (239, 235, 226))
    tile.paste(crop, ((size[0] - crop.width) // 2, (size[1] - crop.height) // 2))
    return tile


def make_sheet(items, output):
    tile_w, image_h, label_h = 300, 206, 48
    font = ImageFont.load_default()
    tiles = []

    for label, path in items:
        image = Image.open(path).convert("RGB")
        scale_x = image.width / 1152
        scale_y = image.height / 768
        for crop_label, box in CROPS:
            scaled = (
                int(box[0] * scale_x),
                int(box[1] * scale_y),
                int(box[2] * scale_x),
                int(box[3] * scale_y),
            )
            tile = Image.new("RGB", (tile_w, image_h + label_h), (247, 244, 237))
            tile.paste(crop_to_tile(image, scaled, (tile_w, image_h)), (0, 0))
            draw = ImageDraw.Draw(tile)
            draw.rectangle((0, image_h, tile_w, image_h + label_h), fill=(247, 244, 237))
            draw.text((10, image_h + 8), label[:44], fill=(42, 38, 32), font=font)
            draw.text((10, image_h + 26), crop_label[:44], fill=(91, 82, 68), font=font)
            tiles.append(tile)

    cols = 5
    gap = 10
    header_h = 66
    rows = (len(tiles) + cols - 1) // cols
    sheet_w = cols * tile_w + (cols + 1) * gap
    sheet_h = header_h + rows * (image_h + label_h + gap) + gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (225, 220, 210))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet_w, header_h), fill=(78, 65, 51))
    draw.text((20, 18), "Triceratops identity review crops", fill=(248, 246, 239), font=font)
    draw.text((20, 40), "Check three horns, skull-attached frill, beak, non-hoofed feet, long tail, and non-rhino body.", fill=(230, 224, 214), font=font)

    for idx, tile in enumerate(tiles):
        x = gap + (idx % cols) * (tile_w + gap)
        y = header_h + gap + (idx // cols) * (image_h + label_h + gap)
        sheet.paste(tile, (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--item", action="append", required=True, help="label=path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    items = []
    for raw in args.item:
        label, path = raw.split("=", 1)
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        items.append((label, candidate))
    make_sheet(items, Path(args.output).resolve())
    print(Path(args.output).resolve())


if __name__ == "__main__":
    main()
