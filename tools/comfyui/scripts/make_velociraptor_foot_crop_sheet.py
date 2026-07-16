import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "tools" / "comfyui" / "outputs" / "velo_foot_crop_sheet.png"


def make_sheet(items, output):
    crops = [("front", (360, 550, 560, 690)), ("rear", (620, 565, 830, 700))]
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
    parser.add_argument("--item", action="append", required=True, help="label=path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    items = []
    for raw in args.item:
        label, path = raw.split("=", 1)
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        items.append((candidate, label))
    make_sheet(items, Path(args.output).resolve())
    print(Path(args.output).resolve())


if __name__ == "__main__":
    main()
