import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = ROOT / "tools" / "comfyui" / "ComfyUI" / "input" / "dino_guides"
ASSET_DIR = ROOT / "assets" / "dinosaurs"


WIDTH = 1152
HEIGHT = 768


def sc(points, scale):
    return [(int(round(x * scale)), int(round(y * scale))) for x, y in points]


def clamp(value, low, high):
    return max(low, min(high, value))


def polygon_points(cx, base_y, width, height, lean=0, asym=0):
    apex_x = cx + lean + width * asym * 0.08
    return [
        (cx - width * 0.46, base_y + height * 0.02),
        (cx - width * 0.58, base_y - height * 0.16),
        (cx + lean * 0.20 - width * 0.52, base_y - height * 0.48),
        (apex_x - width * 0.25, base_y - height * 0.84),
        (apex_x, base_y - height),
        (apex_x + width * 0.25, base_y - height * 0.84),
        (cx + lean * 0.20 + width * 0.52, base_y - height * 0.48),
        (cx + width * 0.58, base_y - height * 0.16),
        (cx + width * 0.46, base_y + height * 0.02),
    ]


def draw_background(draw, scale):
    for y in range(HEIGHT * scale):
        t = y / (HEIGHT * scale)
        if t < 0.58:
            local = t / 0.58
            color = (
                int(188 * (1 - local) + 155 * local),
                int(215 * (1 - local) + 194 * local),
                int(216 * (1 - local) + 178 * local),
            )
        else:
            local = (t - 0.58) / 0.42
            color = (
                int(184 * (1 - local) + 136 * local),
                int(172 * (1 - local) + 130 * local),
                int(124 * (1 - local) + 91 * local),
            )
        draw.line((0, y, WIDTH * scale, y), fill=color)


def draw_ground(draw, rng, scale):
    horizon = int(HEIGHT * 0.62 * scale)
    draw.rectangle((0, horizon, WIDTH * scale, HEIGHT * scale), fill=(170, 154, 109))
    for _ in range(420):
        x = rng.randrange(0, WIDTH * scale)
        y = rng.randrange(horizon, HEIGHT * scale)
        length = rng.randrange(8 * scale, 28 * scale)
        color = rng.choice([(86, 99, 58), (118, 112, 74), (64, 77, 48), (145, 132, 85)])
        draw.line((x, y, x + rng.randrange(-8 * scale, 8 * scale), y - length), fill=color, width=max(1, scale))


def add_noise(layer, mask, rng, tones, count, scale, alpha_range=(6, 28)):
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    bbox = mask.getbbox()
    if not bbox:
        return layer
    x0, y0, x1, y1 = bbox
    mask_pixels = mask.load()
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if mask_pixels[x, y] < 24:
            continue
        tone = rng.choice(tones)
        alpha = rng.randrange(*alpha_range)
        if rng.random() < 0.25:
            radius = rng.uniform(0.5 * scale, 1.8 * scale)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            draw.point((x, y), fill=(*tone, alpha))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def draw_body(layer, mask, rng, scale, profile="default"):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    outline = (39, 31, 24, 255)
    dark = (62, 47, 35, 255)
    mid = (103, 78, 52, 255)
    light = (142, 111, 73, 255)

    if profile == "lowbody":
        tail = sc([(762, 438), (1020, 374), (1072, 388), (792, 486)], scale)
        body = sc(
            [
                (232, 464),
                (286, 394),
                (410, 352),
                (560, 334),
                (704, 350),
                (822, 408),
                (880, 470),
                (836, 526),
                (700, 552),
                (512, 552),
                (352, 528),
            ],
            scale,
        )
        neck = sc([(292, 414), (176, 386), (154, 430), (302, 462)], scale)
        head = sc([(168, 378), (96, 382), (46, 410), (58, 442), (116, 462), (176, 444), (206, 404)], scale)
        arc_top = (282 * scale, 330 * scale, 848 * scale, 558 * scale)
        arc_bottom = (294 * scale, 380 * scale, 858 * scale, 600 * scale)
        legs = [
            [(318, 502), (374, 512), (360, 646), (304, 646), (286, 672), (378, 672)],
            [(448, 518), (504, 516), (498, 650), (438, 650), (420, 674), (518, 674)],
            [(650, 512), (708, 508), (712, 650), (650, 650), (632, 674), (730, 674)],
            [(770, 494), (826, 490), (838, 650), (780, 650), (762, 674), (858, 674)],
        ]
    else:
        tail = sc([(730, 438), (1014, 348), (1064, 365), (778, 492)], scale)
        body = sc(
            [
                (244, 458),
                (282, 372),
                (380, 326),
                (510, 304),
                (656, 318),
                (770, 370),
                (840, 438),
                (806, 520),
                (674, 556),
                (496, 554),
                (348, 528),
            ],
            scale,
        )
        neck = sc([(278, 406), (170, 372), (152, 426), (290, 468)], scale)
        head = sc([(154, 368), (84, 372), (40, 400), (52, 438), (110, 462), (170, 446), (196, 402)], scale)
        arc_top = (285 * scale, 314 * scale, 810 * scale, 570 * scale)
        arc_bottom = (290 * scale, 365 * scale, 814 * scale, 610 * scale)
        legs = [
            [(322, 500), (382, 514), (366, 646), (308, 646), (292, 672), (386, 672)],
            [(452, 522), (512, 518), (506, 650), (444, 650), (426, 674), (524, 674)],
            [(640, 508), (700, 504), (708, 650), (646, 650), (628, 674), (728, 674)],
            [(752, 484), (810, 478), (828, 648), (768, 648), (750, 674), (850, 674)],
        ]

    for pts, fill in [(tail, (82, 63, 43, 255)), (body, mid), (neck, (88, 67, 45, 255)), (head, (106, 81, 54, 255))]:
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=outline, width=5 * scale, joint="curve")
        mask_draw.polygon(pts, fill=255)

    draw.arc(arc_top, 190, 352, fill=light, width=3 * scale)
    draw.arc(arc_bottom, 12, 176, fill=dark, width=3 * scale)
    draw.ellipse((104 * scale, 398 * scale, 118 * scale, 412 * scale), fill=(20, 17, 14, 255))

    for index, pts in enumerate(legs):
        fill = dark if index in (0, 2) else (75, 56, 39, 255)
        spts = sc(pts, scale)
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=outline, width=4 * scale, joint="curve")
        mask_draw.polygon(spts, fill=255)

    # Four large, countable thagomizer spikes at the tail tip.
    hub = sc([(1002, 349), (1040, 350), (1060, 366), (1040, 384), (1000, 380), (984, 362)], scale)
    draw.polygon(hub, fill=(94, 68, 44, 255))
    draw.line(hub + [hub[0]], fill=outline, width=4 * scale, joint="curve")
    mask_draw.polygon(hub, fill=255)
    spikes = [
        [(1014, 350), (1034, 356), (1075, 292)],
        [(1038, 356), (1058, 366), (1118, 328)],
        [(1010, 376), (1032, 386), (1072, 452)],
        [(1038, 376), (1058, 386), (1120, 426)],
    ]
    for pts in spikes:
        spts = sc(pts, scale)
        draw.polygon(spts, fill=(151, 98, 56, 255))
        draw.line(spts + [spts[0]], fill=outline, width=4 * scale, joint="curve")
        mask_draw.polygon(spts, fill=255)

    return add_noise(
        layer,
        mask,
        rng,
        [(53, 41, 31), (111, 85, 57), (157, 124, 81), (82, 62, 43)],
        3600,
        scale,
    )


def draw_plates(layer, mask, rng, scale, profile="default"):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    outline = (35, 27, 21, 255)

    if profile == "lowbody":
        far_specs = [
            (300, 416, 34, 52, -4),
            (366, 382, 44, 78, -3),
            (446, 354, 54, 104, -2),
            (536, 334, 66, 138, -1),
            (632, 340, 66, 136, 1),
            (724, 368, 58, 104, 2),
            (806, 410, 42, 66, 4),
        ]
        near_specs = [
            (254, 444, 30, 40, -4),
            (330, 408, 44, 70, -3),
            (410, 372, 56, 98, -2),
            (502, 348, 70, 128, -1),
            (598, 336, 78, 148, 0),
            (696, 348, 74, 136, 2),
            (786, 384, 58, 96, 3),
            (858, 430, 42, 56, 4),
        ]
    else:
        far_specs = [
            (286, 410, 34, 54, -4),
            (348, 374, 44, 86, -3),
            (424, 340, 56, 120, -2),
            (510, 316, 68, 158, -1),
            (606, 318, 68, 160, 1),
            (696, 346, 58, 120, 2),
            (778, 392, 42, 76, 4),
        ]
        near_specs = [
            (244, 438, 30, 42, -4),
            (316, 398, 44, 76, -3),
            (394, 358, 58, 112, -2),
            (482, 326, 72, 150, -1),
            (574, 304, 82, 182, 0),
            (670, 318, 78, 164, 2),
            (760, 360, 60, 116, 3),
            (834, 418, 42, 64, 4),
        ]

    for specs, fill, line_width in [
        (far_specs, (95, 66, 42, 230), 4),
        (near_specs, (148, 92, 48, 248), 5),
    ]:
        for cx, base_y, plate_w, plate_h, lean in specs:
            pts = sc(polygon_points(cx, base_y, plate_w, plate_h, lean, rng.uniform(-0.18, 0.18)), scale)
            draw.polygon(pts, fill=fill)
            draw.line(pts + [pts[0]], fill=outline, width=line_width * scale, joint="curve")
            draw.line(pts[2:7], fill=(197, 143, 75, 70), width=2 * scale, joint="curve")
            mask_draw.polygon(pts, fill=255)
            # A small socket shadow keeps each plate visibly attached but separate.
            draw.line(
                sc([(cx - plate_w * 0.42, base_y + 2), (cx + plate_w * 0.42, base_y + 2)], scale),
                fill=(23, 18, 14, 190),
                width=4 * scale,
            )

    return add_noise(
        layer,
        mask,
        rng,
        [(66, 45, 31), (121, 78, 42), (182, 121, 61), (40, 31, 25)],
        2600,
        scale,
        alpha_range=(8, 34),
    )


def make_reference(output, profile="default"):
    scale = 4
    rng = random.Random(2026062701)
    image = Image.new("RGB", (WIDTH * scale, HEIGHT * scale), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw_background(draw, scale)
    draw_ground(draw, rng, scale)

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse((250 * scale, 620 * scale, 910 * scale, 706 * scale), fill=(36, 30, 24, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10 * scale))

    plates = Image.new("RGBA", image.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", image.size, 0)
    plates = draw_plates(plates, plate_mask, rng, scale, profile)

    body = Image.new("RGBA", image.size, (0, 0, 0, 0))
    body_mask = Image.new("L", image.size, 0)
    body = draw_body(body, body_mask, rng, scale, profile)

    # Draw far/near plates behind and in front of body by compositing the same
    # clear plate layer before and after body with a body occlusion mask.
    base = Image.alpha_composite(image.convert("RGBA"), shadow)
    base = Image.alpha_composite(base, plates)
    base = Image.alpha_composite(base, body)
    front_alpha = ImageChops.multiply(plates.getchannel("A"), body_mask.filter(ImageFilter.GaussianBlur(radius=0.5 * scale)))
    front_plates = plates.copy()
    front_plates.putalpha(front_alpha.point(lambda value: int(value * 0.34)))
    base = Image.alpha_composite(base, front_plates)

    base = base.filter(ImageFilter.GaussianBlur(radius=0.12 * scale))
    result = base.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


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
    for index, tile in enumerate(tiles):
        sheet.paste(tile, (index * thumb_w, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--guide-output",
        default=str(GUIDE_DIR / "stegosaurus-stenops_plate_thagomizer_reference_v1.png"),
    )
    parser.add_argument(
        "--asset-output",
        default=str(ASSET_DIR / "stegosaurus-stenops-plate-thagomizer-reference-v1.png"),
    )
    parser.add_argument(
        "--sheet-output",
        default=str(ASSET_DIR / "stegosaurus-plate-thagomizer-reference-sheet-v1.png"),
    )
    parser.add_argument("--profile", choices=["default", "lowbody"], default="default")
    args = parser.parse_args()

    guide_output = Path(args.guide_output).resolve()
    asset_output = Path(args.asset_output).resolve()
    sheet_output = Path(args.sheet_output).resolve()
    make_reference(guide_output, args.profile)
    asset_output.parent.mkdir(parents=True, exist_ok=True)
    Image.open(guide_output).save(asset_output)
    sheet_items = []
    for path, label in [
        (ASSET_DIR / "stegosaurus-stenops-angular-plate-ipcontrol-v1.png", "current plate-first candidate"),
        (ASSET_DIR / "stegosaurus-stenops-tailroom-thagomizer-ipcontrol-v1.png", "current thagomizer comparison"),
        (asset_output, "plate + thagomizer reference"),
    ]:
        if path.exists():
            sheet_items.append((path, label))
    make_contact_sheet(sheet_items, sheet_output)
    print(guide_output)
    print(asset_output)
    print(sheet_output)


if __name__ == "__main__":
    main()
