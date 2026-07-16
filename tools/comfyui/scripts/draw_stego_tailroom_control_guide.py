import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
ASSET_DIR = ROOT / "assets" / "dinosaurs"


def sc(points, scale):
    return [(int(round(x * scale)), int(round(y * scale))) for x, y in points]


def plate_points(cx, base_y, width, height, lean=0):
    top_x = cx + lean
    return [
        (cx - width * 0.56, base_y),
        (cx - width * 0.65, base_y - height * 0.16),
        (cx + lean * 0.15 - width * 0.50, base_y - height * 0.46),
        (top_x - width * 0.24, base_y - height * 0.86),
        (top_x, base_y - height),
        (top_x + width * 0.24, base_y - height * 0.86),
        (cx + lean * 0.15 + width * 0.50, base_y - height * 0.46),
        (cx + width * 0.65, base_y - height * 0.16),
        (cx + width * 0.56, base_y),
    ]


def draw_background(draw, width, height, scale):
    draw.rectangle((0, 0, width * scale, int(height * 0.62) * scale), fill=(205, 225, 222))
    draw.rectangle((0, int(height * 0.62) * scale, width * scale, height * scale), fill=(185, 173, 128))


def draw_body(image, scale):
    draw = ImageDraw.Draw(image)
    outline = (30, 25, 20, 255)
    body_fill = (100, 78, 52, 255)
    dark = (64, 48, 34, 255)

    tail = [(770, 410), (1022, 356), (1044, 376), (808, 462)]
    body = [
        (220, 444),
        (258, 366),
        (352, 322),
        (480, 302),
        (626, 306),
        (758, 346),
        (836, 414),
        (806, 496),
        (684, 540),
        (502, 550),
        (350, 526),
        (248, 482),
    ]
    neck = [(248, 394), (158, 370), (136, 418), (256, 456)]
    head = [(132, 365), (74, 371), (40, 402), (58, 438), (116, 458), (166, 441), (174, 394)]

    for pts, fill in [
        (tail, (78, 61, 43, 255)),
        (neck, (84, 65, 44, 255)),
        (head, (98, 77, 53, 255)),
        (body, body_fill),
    ]:
        spts = sc(pts, scale)
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=outline, width=max(3, 5 * scale), joint="curve")

    legs = [
        [(296, 494), (356, 506), (340, 646), (282, 646), (270, 672), (358, 672)],
        [(444, 518), (504, 512), (496, 650), (434, 650), (420, 674), (514, 674)],
        [(650, 500), (708, 492), (716, 648), (654, 648), (640, 672), (730, 672)],
        [(766, 472), (818, 468), (834, 646), (776, 646), (762, 672), (852, 672)],
    ]
    for idx, pts in enumerate(legs):
        fill = dark if idx in (0, 2) else (76, 57, 38, 255)
        spts = sc(pts, scale)
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=outline, width=max(2, 4 * scale), joint="curve")

    draw.ellipse((100 * scale, 398 * scale, 114 * scale, 412 * scale), fill=(18, 15, 12, 255))

    # Large in-frame thagomizer: four spikes, separated from the image edge.
    hub = [(1008, 352), (1040, 350), (1055, 362), (1040, 378), (1008, 376), (996, 363)]
    spikes = [
        [(1020, 350), (1038, 356), (1084, 302)],
        [(1039, 358), (1054, 365), (1104, 334)],
        [(1020, 374), (1038, 382), (1080, 438)],
        [(1040, 373), (1055, 380), (1106, 414)],
    ]
    draw.polygon(sc(hub, scale), fill=(92, 65, 42, 255))
    draw.line(sc(hub + [hub[0]], scale), fill=outline, width=max(2, 4 * scale), joint="curve")
    for pts in spikes:
        spts = sc(pts, scale)
        draw.polygon(spts, fill=(143, 96, 58, 255))
        draw.line(spts + [spts[0]], fill=outline, width=max(2, 4 * scale), joint="curve")


def draw_plate_rows(image, scale):
    draw = ImageDraw.Draw(image)
    outline = (28, 23, 18, 255)
    far = (92, 67, 45, 255)
    near = (151, 94, 48, 255)

    far_specs = [
        (286, 404, 34, 54, -4),
        (348, 368, 44, 82, -4),
        (420, 338, 54, 114, -2),
        (500, 320, 64, 148, -1),
        (590, 318, 66, 156, 1),
        (680, 342, 56, 118, 3),
        (760, 386, 42, 76, 4),
        (824, 426, 28, 46, 5),
    ]
    near_specs = [
        (246, 432, 28, 40, -5),
        (314, 392, 42, 72, -4),
        (386, 356, 56, 106, -2),
        (466, 326, 68, 142, -1),
        (552, 306, 78, 174, 0),
        (642, 314, 74, 162, 2),
        (728, 350, 62, 120, 3),
        (800, 398, 46, 78, 4),
    ]

    for specs, fill, width in [(far_specs, far, 4), (near_specs, near, 5)]:
        for cx, base_y, plate_w, plate_h, lean in specs:
            pts = plate_points(cx, base_y, plate_w, plate_h, lean)
            spts = sc(pts, scale)
            draw.polygon(spts, fill=fill)
            draw.line(spts + [spts[0]], fill=outline, width=max(2, width * scale), joint="curve")
            draw.line(
                sc([(cx - plate_w * 0.50, base_y + 1), (cx + plate_w * 0.50, base_y + 1)], scale),
                fill=(20, 16, 13, 255),
                width=max(2, 4 * scale),
            )


def make_guide(output):
    width, height = 1152, 768
    scale = 3
    image = Image.new("RGBA", (width * scale, height * scale), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw_background(draw, width, height, scale)
    draw_plate_rows(image, scale)
    draw_body(image, scale)
    draw_plate_rows(image, scale)
    image = image.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


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
    sheet = Image.new("RGB", (thumb_w * len(tiles), thumb_h + label_h), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, (idx * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--guide-output",
        default=str(GUIDE_DIR / "stegosaurus-stenops_tailroom_control_v1.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "stegosaurus-stenops-tailroom-control-guide-v1.png"),
    )
    parser.add_argument("--sheet-output", default=str(ASSET_DIR / "stegosaurus-tailroom-control-sheet-v1.png"))
    args = parser.parse_args()

    guide_output = Path(args.guide_output).resolve()
    asset_output = Path(args.asset_output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    make_guide(guide_output)
    asset_output.parent.mkdir(parents=True, exist_ok=True)
    Image.open(guide_output).save(asset_output)
    make_contact_sheet([(asset_output, "tail-room thagomizer control guide")], sheet_output)
    print(guide_output)
    print(asset_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
