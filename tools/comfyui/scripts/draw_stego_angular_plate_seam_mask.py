import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-angular-plate-ipcontrol-v1.png"
DEFAULT_OUTPUT = ROOT / "tools" / "comfyui" / "outputs" / "stego_angular_plate_seam_mask_v1.png"
DEFAULT_SHEET = ROOT / "tools" / "comfyui" / "outputs" / "stego_angular_plate_seam_mask_v1-sheet.png"


# Coordinates target the current angular-plate candidate. White areas are
# inpainted into open air/background gaps between fused dorsal plates.
SEAMS = [
    # x, top_y, base_y, top_w, base_w, lean
    (0.262, 0.360, 0.455, 0.006, 0.012, -0.006),
    (0.310, 0.292, 0.430, 0.007, 0.014, -0.005),
    (0.365, 0.232, 0.405, 0.008, 0.016, -0.004),
    (0.428, 0.182, 0.382, 0.009, 0.018, -0.002),
    (0.497, 0.144, 0.366, 0.010, 0.019, 0.000),
    (0.568, 0.156, 0.368, 0.010, 0.019, 0.001),
    (0.638, 0.204, 0.392, 0.009, 0.017, 0.003),
    (0.704, 0.272, 0.426, 0.008, 0.015, 0.004),
    (0.760, 0.348, 0.456, 0.007, 0.013, 0.005),
]


def seam_polygon(seam, size, scale, width_scale):
    image_w, image_h = size
    x, top_y, base_y, top_w, base_w, lean = seam
    x_top = (x + lean * 0.20) * image_w * scale
    x_mid = (x + lean * 0.62) * image_w * scale
    x_base = (x + lean) * image_w * scale
    y_top = top_y * image_h * scale
    y_mid = (top_y * 0.42 + base_y * 0.58) * image_h * scale
    y_base = base_y * image_h * scale
    top_px = top_w * width_scale * image_w * scale
    base_px = base_w * width_scale * image_w * scale
    mid_px = (top_px * 0.55 + base_px * 0.45)
    return [
        (x_top - top_px * 0.50, y_top),
        (x_top + top_px * 0.50, y_top),
        (x_mid + mid_px * 0.52, y_mid),
        (x_base + base_px * 0.50, y_base),
        (x_base - base_px * 0.50, y_base),
        (x_mid - mid_px * 0.52, y_mid),
    ]


def make_mask(source, output, width_scale):
    source_image = Image.open(source).convert("RGB")
    width, height = source_image.size
    scale = 4
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    for seam in SEAMS:
        draw.polygon(seam_polygon(seam, source_image.size, scale, width_scale), fill=255)
    mask = mask.resize(source_image.size, Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    mask.convert("RGB").save(output)
    return output


def make_sheet(source, mask, output):
    source_image = Image.open(source).convert("RGB")
    mask_image = Image.open(mask).convert("L")
    overlay = source_image.convert("RGBA")
    red = Image.new("RGBA", source_image.size, (210, 40, 28, 0))
    red.putalpha(mask_image.point(lambda p: int(p * 0.72)))
    overlay = Image.alpha_composite(overlay, red).convert("RGB")

    thumb_w, thumb_h, label_h = 384, 256, 38
    tiles = []
    for image, label in [(source_image, "source angular plate candidate"), (mask_image.convert("RGB"), "seam mask"), (overlay, "masked seam overlay")]:
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(38, 35, 31), font=ImageFont.load_default())
        tiles.append(tile)
    sheet = Image.new("RGB", (thumb_w * len(tiles), thumb_h + label_h), (226, 222, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--sheet-output", default=str(DEFAULT_SHEET))
    parser.add_argument("--width-scale", type=float, default=1.0)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    make_mask(source, output, args.width_scale)
    make_sheet(source, output, sheet_output)
    print(output)
    print(sheet_output)


if __name__ == "__main__":
    main()
