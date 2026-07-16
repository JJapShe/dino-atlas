import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "assets" / "dinosaurs" / "velociraptor-p0-wide-review-v35.png"

CROPS = [
    ("full body", (0.00, 0.06, 1.00, 0.92), (340, 210)),
    ("head/snout", (0.00, 0.10, 0.30, 0.42), (300, 210)),
    ("folded forelimb", (0.22, 0.34, 0.45, 0.70), (260, 210)),
    ("both feet", (0.30, 0.60, 0.58, 0.90), (300, 210)),
    ("sickle-toe area", (0.34, 0.64, 0.50, 0.88), (240, 210)),
]


def crop_tile(image, box_norm, size):
    w, h = image.size
    box = (
        int(box_norm[0] * w),
        int(box_norm[1] * h),
        int(box_norm[2] * w),
        int(box_norm[3] * h),
    )
    crop = image.crop(box)
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, (244, 241, 233))
    tile.paste(crop, ((size[0] - crop.width) // 2, (size[1] - crop.height) // 2))
    return tile


def make_sheet(items, output):
    font = ImageFont.load_default()
    label_h = 48
    gap = 10
    header_h = 74
    row_h = max(size[1] for _, _, size in CROPS) + label_h
    col_widths = [size[0] for _, _, size in CROPS]
    sheet_w = sum(col_widths) + gap * (len(col_widths) + 1)
    sheet_h = header_h + gap + len(items) * (row_h + gap)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (225, 220, 210))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet_w, header_h), fill=(62, 66, 82))
    draw.text((18, 18), "Velociraptor P0 wide candidate anatomy review", fill=(248, 246, 239), font=font)
    draw.text(
        (18, 42),
        "Gate: toothed non-beak snout, folded forelimbs, two hind legs, attached modest raised second-toe sickle claw.",
        fill=(224, 225, 232),
        font=font,
    )

    x = gap
    for crop_label, _, size in CROPS:
        draw.text((x + 6, header_h - 18), crop_label, fill=(248, 246, 239), font=font)
        x += size[0] + gap

    for row, (label, path) in enumerate(items):
        image = Image.open(path).convert("RGB")
        x = gap
        y = header_h + gap + row * (row_h + gap)
        for crop_label, box, size in CROPS:
            tile = Image.new("RGB", (size[0], row_h), (247, 244, 237))
            tile.paste(crop_tile(image, box, size), (0, 0))
            tile_draw = ImageDraw.Draw(tile)
            tile_draw.rectangle((0, size[1], size[0], row_h), fill=(247, 244, 237))
            tile_draw.text((8, size[1] + 8), label[:42], fill=(42, 38, 32), font=font)
            tile_draw.text((8, size[1] + 26), crop_label, fill=(91, 82, 68), font=font)
            sheet.paste(tile, (x, y))
            x += size[0] + gap

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
