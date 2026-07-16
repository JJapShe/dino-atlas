from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SOURCE = ASSET_ROOT / "stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png"
MASK_OUT = OUTPUT_ROOT / "stegosaurus_plate_base_offset_mask_v59.png"
SHEET_OUT = OUTPUT_ROOT / "stegosaurus_plate_base_offset_mask_v59-sheet.png"


# Normalized polygons for the current v6 side-profile image. They target only
# small sky gaps and plate-base edge zones so the torso, legs, tail, and overall
# plate silhouettes remain locked during inpaint.
BASE_PATCHES = [
    [(0.142, 0.476), (0.188, 0.450), (0.218, 0.470), (0.206, 0.515), (0.154, 0.512)],
    [(0.208, 0.432), (0.258, 0.404), (0.286, 0.424), (0.272, 0.468), (0.218, 0.466)],
    [(0.286, 0.378), (0.344, 0.344), (0.374, 0.368), (0.354, 0.414), (0.294, 0.410)],
    [(0.382, 0.336), (0.448, 0.304), (0.478, 0.334), (0.452, 0.382), (0.386, 0.374)],
    [(0.494, 0.314), (0.568, 0.282), (0.604, 0.316), (0.572, 0.368), (0.498, 0.354)],
    [(0.616, 0.328), (0.690, 0.300), (0.724, 0.334), (0.692, 0.382), (0.620, 0.370)],
    [(0.724, 0.386), (0.790, 0.358), (0.820, 0.390), (0.790, 0.438), (0.728, 0.424)],
    [(0.824, 0.466), (0.880, 0.440), (0.904, 0.472), (0.876, 0.520), (0.824, 0.502)],
]

GAP_STROKES = [
    ((0.190, 0.432), (0.178, 0.512), 7),
    ((0.258, 0.390), (0.246, 0.466), 8),
    ((0.338, 0.344), (0.326, 0.414), 9),
    ((0.438, 0.300), (0.424, 0.384), 9),
    ((0.566, 0.286), (0.544, 0.366), 10),
    ((0.690, 0.310), (0.666, 0.386), 9),
    ((0.806, 0.376), (0.780, 0.450), 8),
    ((0.894, 0.456), (0.860, 0.522), 7),
]


def scaled(points, size, scale):
    width, height = size
    return [(x * width * scale, y * height * scale) for x, y in points]


def make_mask(source, output):
    image = Image.open(source).convert("RGB")
    scale = 4
    mask = Image.new("L", (image.width * scale, image.height * scale), 0)
    draw = ImageDraw.Draw(mask)

    for patch in BASE_PATCHES:
        draw.polygon(scaled(patch, image.size, scale), fill=255)

    for (x0, y0), (x1, y1), width in GAP_STROKES:
        draw.line(
            (
                x0 * image.width * scale,
                y0 * image.height * scale,
                x1 * image.width * scale,
                y1 * image.height * scale,
            ),
            fill=255,
            width=width * scale,
        )

    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.4 * scale))
    mask = mask.resize(image.size, Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    mask.convert("RGB").save(output)
    return output


def make_sheet(source, mask, output):
    image = Image.open(source).convert("RGB")
    mask_image = Image.open(mask).convert("L")
    overlay = image.convert("RGBA")
    red = Image.new("RGBA", image.size, (216, 44, 30, 0))
    red.putalpha(mask_image.point(lambda p: int(p * 0.62)))
    overlay = Image.alpha_composite(overlay, red).convert("RGB")

    items = [
        (image, "current v6 source"),
        (mask_image.convert("RGB"), "v59 base/gap mask"),
        (overlay, "masked plate-base overlay"),
    ]
    thumb_w, thumb_h, label_h = 430, 242, 38
    sheet = Image.new("RGB", (thumb_w * len(items), thumb_h + label_h), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (item, label) in enumerate(items):
        item = item.copy()
        item.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(item, ((thumb_w - item.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(43, 39, 34), font=font)
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    mask = make_mask(SOURCE, MASK_OUT)
    make_sheet(SOURCE, mask, SHEET_OUT)
    print(mask)
    print(SHEET_OUT)


if __name__ == "__main__":
    main()
