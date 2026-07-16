import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent.parent / "assets" / "dinosaurs" / "stegosaurus-stenops-platefirst-tailclean-v1.png"
DEFAULT_OUTPUT = ROOT / "outputs" / "stego_plate_corrected_v1.png"


# Coordinates are normalized against the current 1152x768 Stegosaurus side-view
# candidate. The alternating row is represented through overlap, color, and
# staggered base positions; the near row is drawn last.
PLATES = [
    # cx, base_y, width, height, lean, far_row
    (0.226, 0.515, 0.035, 0.090, -0.010, True),
    (0.265, 0.494, 0.044, 0.120, -0.006, False),
    (0.306, 0.470, 0.052, 0.155, -0.004, True),
    (0.355, 0.440, 0.064, 0.205, -0.002, False),
    (0.412, 0.420, 0.074, 0.235, 0.002, True),
    (0.472, 0.405, 0.080, 0.252, 0.000, False),
    (0.535, 0.415, 0.076, 0.230, -0.002, True),
    (0.596, 0.440, 0.066, 0.190, 0.003, False),
    (0.650, 0.472, 0.056, 0.150, 0.004, True),
    (0.696, 0.505, 0.046, 0.112, 0.004, False),
    (0.735, 0.535, 0.036, 0.078, 0.003, True),
]


def scaled_plate_points(cx, base_y, width, height, lean):
    return [
        (cx - width * 0.48, base_y + height * 0.03),
        (cx - width * 0.56, base_y - height * 0.20),
        (cx + lean - width * 0.42, base_y - height * 0.58),
        (cx + lean - width * 0.18, base_y - height * 0.88),
        (cx + lean + width * 0.08, base_y - height * 0.98),
        (cx + lean + width * 0.32, base_y - height * 0.74),
        (cx + width * 0.52, base_y - height * 0.34),
        (cx + width * 0.43, base_y + height * 0.04),
    ]


def to_pixels(spec, width, height, scale):
    cx, base_y, plate_w, plate_h, lean, far_row = spec
    return (
        cx * width * scale,
        base_y * height * scale,
        plate_w * width * scale,
        plate_h * height * scale,
        lean * width * scale,
        far_row,
    )


def draw_plate_layer(image):
    width, height = image.size
    scale = 3
    canvas = image.resize((width * scale, height * scale), Image.Resampling.LANCZOS).convert("RGBA")
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(layer)
    shadow_draw = ImageDraw.Draw(shadow)
    mask_draw = ImageDraw.Draw(mask)

    ordered = sorted(PLATES, key=lambda item: item[-1], reverse=True)
    for spec in ordered:
        cx, base_y, plate_w, plate_h, lean, far_row = to_pixels(spec, width, height, scale)
        points = scaled_plate_points(cx, base_y, plate_w, plate_h, lean)
        fill = (116, 86, 58, 238) if far_row else (143, 101, 66, 246)
        outline = (56, 43, 34, 242) if far_row else (47, 35, 27, 250)
        highlight = (184, 142, 96, 108) if not far_row else (154, 116, 80, 82)

        base_box = (
            cx - plate_w * 0.50,
            base_y - plate_h * 0.10,
            cx + plate_w * 0.52,
            base_y + plate_h * 0.13,
        )
        shadow_draw.ellipse(base_box, fill=(26, 20, 15, 95))
        draw.polygon(points, fill=fill, outline=outline)
        draw.line(points + [points[0]], fill=outline, width=max(3, int(1.4 * scale)), joint="curve")
        mask_draw.polygon(points, fill=255)

        center_top = (cx + lean * 0.40, base_y - plate_h * 0.83)
        center_base = (cx, base_y - plate_h * 0.04)
        draw.line([center_base, center_top], fill=(71, 51, 38, 128), width=max(2, int(1.0 * scale)))
        for frac in (0.22, 0.40, 0.58, 0.74):
            left = (cx - plate_w * (0.42 - frac * 0.18), base_y - plate_h * frac)
            right = (cx + plate_w * (0.42 - frac * 0.16), base_y - plate_h * frac)
            rib_mid = (cx + lean * 0.25, base_y - plate_h * (frac + 0.12))
            draw.line([left, rib_mid], fill=(65, 48, 37, 78), width=max(1, int(0.8 * scale)))
            draw.line([right, rib_mid], fill=(65, 48, 37, 72), width=max(1, int(0.8 * scale)))

        edge_highlight = [
            points[1],
            points[2],
            points[3],
            points[4],
        ]
        draw.line(edge_highlight, fill=highlight, width=max(2, int(1.0 * scale)), joint="curve")

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=2.2 * scale))
    layer = Image.alpha_composite(shadow, layer)
    composite = Image.alpha_composite(canvas, layer)
    return (
        composite.resize((width, height), Image.Resampling.LANCZOS).convert("RGB"),
        mask.resize((width, height), Image.Resampling.LANCZOS),
    )


def make_contact_sheet(items, output):
    thumb_w, thumb_h = 440, 294
    tiles = []
    for path, label in items:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + 44), (244, 241, 233))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 12), label[:64], fill=(38, 33, 28), font=ImageFont.load_default())
        tiles.append(tile)

    sheet = Image.new("RGB", (thumb_w * len(tiles), thumb_h + 44), (226, 220, 209))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--mask-output")
    parser.add_argument("--sheet-output")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    mask_output = Path(args.mask_output).resolve() if args.mask_output else output.with_name(output.stem + "-mask.png")
    sheet_output = Path(args.sheet_output).resolve() if args.sheet_output else output.with_name(output.stem + "-sheet.png")

    output.parent.mkdir(parents=True, exist_ok=True)
    mask_output.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(source).convert("RGB")
    corrected, mask = draw_plate_layer(image)
    corrected.save(output)
    mask.save(mask_output)
    make_contact_sheet([(source, "previous rounded-plate candidate"), (output, "plate-corrected paintover")], sheet_output)
    print(output)
    print(mask_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
