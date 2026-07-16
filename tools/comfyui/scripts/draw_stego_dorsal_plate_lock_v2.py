import json
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

WIDTH = 1344
HEIGHT = 832


VARIANTS = {
    "v2a": {
        "seed": 2026062501,
        "plate_scale": 1.00,
        "body_drop": 0,
        "near_boost": 1.0,
        "label": "selected: locked alternating broad plates",
    },
    "v2b": {
        "seed": 2026062502,
        "plate_scale": 0.94,
        "body_drop": 8,
        "near_boost": 0.96,
        "label": "lower body, slightly smaller plates",
    },
    "v2c": {
        "seed": 2026062503,
        "plate_scale": 1.06,
        "body_drop": -2,
        "near_boost": 1.05,
        "label": "taller mid-back plates",
    },
}


NEAR_PLATES = [
    (240, 459, 28, 46, -4),
    (284, 438, 34, 61, -4),
    (334, 413, 42, 78, -3),
    (392, 386, 52, 103, -2),
    (458, 360, 62, 129, -1),
    (532, 342, 74, 158, 0),
    (614, 335, 82, 176, 1),
    (700, 345, 78, 164, 2),
    (780, 371, 66, 132, 3),
    (850, 402, 52, 100, 4),
    (908, 432, 38, 70, 5),
    (954, 458, 28, 48, 5),
]

FAR_PLATES = [
    (262, 468, 24, 38, -2),
    (310, 447, 28, 52, -2),
    (362, 424, 36, 68, -1),
    (424, 397, 44, 90, -1),
    (492, 372, 54, 116, 0),
    (570, 356, 62, 142, 1),
    (656, 356, 64, 146, 2),
    (738, 374, 56, 118, 3),
    (812, 404, 44, 88, 4),
    (874, 434, 34, 62, 5),
    (924, 462, 24, 42, 5),
]


def clamp(value, low, high):
    return max(low, min(high, value))


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def tone(color, factor):
    return tuple(clamp(int(channel * factor), 0, 255) for channel in color)


def scaled(points, scale, dy=0):
    return [(int(round(x * scale)), int(round((y + dy) * scale))) for x, y in points]


def draw_background(draw, rng, scale):
    horizon = int(HEIGHT * 0.61 * scale)
    for y in range(HEIGHT * scale):
        if y < horizon:
            t = y / max(1, horizon)
            color = mix((184, 218, 221), (144, 184, 177), t)
        else:
            t = (y - horizon) / max(1, HEIGHT * scale - horizon)
            color = mix((188, 177, 123), (122, 116, 78), t)
        draw.line((0, y, WIDTH * scale, y), fill=color)

    for _ in range(680):
        x = rng.randrange(0, WIDTH * scale)
        y = rng.randrange(horizon + 6 * scale, HEIGHT * scale)
        length = rng.randrange(7 * scale, 28 * scale)
        lean = rng.randrange(-7 * scale, 8 * scale)
        color = rng.choice([(78, 92, 52), (106, 112, 69), (144, 130, 82), (64, 76, 47)])
        draw.line((x, y, x + lean, y - length), fill=color, width=max(1, scale // 2))


def add_texture(layer, mask, rng, colors, count, scale, alpha=(10, 42)):
    texture = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    bbox = mask.getbbox()
    if not bbox:
        return layer
    pixels = mask.load()
    x0, y0, x1, y1 = bbox
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        if pixels[x, y] < 16:
            continue
        color = rng.choice(colors)
        if rng.random() < 0.16:
            r = rng.uniform(0.4 * scale, 1.8 * scale)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, rng.randrange(*alpha)))
        else:
            draw.point((x, y), fill=(*color, rng.randrange(*alpha)))
    texture.putalpha(ImageChops.multiply(texture.getchannel("A"), mask))
    return Image.alpha_composite(layer, texture)


def body_shapes(scale, dy):
    body = scaled(
        [
            (238, 488),
            (292, 419),
            (420, 374),
            (574, 356),
            (724, 372),
            (858, 421),
            (940, 489),
            (898, 552),
            (746, 582),
            (544, 583),
            (374, 552),
            (276, 514),
        ],
        scale,
        dy,
    )
    neck = scaled([(298, 435), (190, 404), (162, 446), (304, 476)], scale, dy)
    head = scaled([(176, 396), (96, 402), (46, 432), (64, 462), (126, 478), (190, 454), (215, 414)], scale, dy)
    tail = scaled([(888, 440), (1170, 350), (1238, 364), (930, 505)], scale, dy)
    belly = scaled([(320, 558), (462, 589), (666, 590), (842, 552)], scale, dy)
    return body, neck, head, tail, belly


def draw_body(layer, mask, rng, scale, variant):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    dy = variant["body_drop"]
    outline = (31, 25, 20, 255)
    body_mid = (105, 77, 50, 255)
    body_dark = (69, 52, 38, 255)
    body_light = (150, 115, 74, 170)

    body, neck, head, tail, belly = body_shapes(scale, dy)
    for pts, fill in ((tail, body_dark), (body, body_mid), (neck, body_dark), (head, body_mid)):
        draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
        mask_draw.polygon(pts, fill=255)

    draw.arc((300 * scale, (348 + dy) * scale, 900 * scale, (584 + dy) * scale), 190, 350, fill=body_light, width=max(3, 3 * scale))
    draw.line(belly, fill=(48, 37, 27, 150), width=max(2, 2 * scale), joint="curve")
    draw.ellipse((108 * scale, (420 + dy) * scale, 122 * scale, (434 + dy) * scale), fill=(12, 10, 9, 255))

    legs = [
        ([(322, 527), (380, 538), (362, 700), (306, 700), (286, 726), (386, 726)], (55, 41, 30, 255)),
        ([(468, 542), (522, 540), (514, 702), (452, 702), (430, 728), (534, 728)], (77, 58, 41, 255)),
        ([(678, 537), (738, 532), (748, 702), (680, 702), (658, 728), (766, 728)], (55, 41, 30, 255)),
        ([(810, 516), (870, 510), (886, 702), (824, 702), (802, 728), (904, 728)], (77, 58, 41, 255)),
    ]
    for pts, fill in legs:
        spts = scaled(pts, scale, dy)
        draw.polygon(spts, fill=fill)
        draw.line(spts + [spts[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
        mask_draw.polygon(spts, fill=255)

    hub = scaled([(1152, 354), (1190, 358), (1213, 376), (1188, 398), (1148, 390), (1132, 370)], scale, dy)
    draw.polygon(hub, fill=(91, 64, 42, 255))
    draw.line(hub + [hub[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
    mask_draw.polygon(hub, fill=255)
    spikes = [
        [(1164, 356), (1188, 363), (1232, 294)],
        [(1190, 363), (1212, 376), (1288, 332)],
        [(1161, 388), (1186, 399), (1230, 468)],
        [(1188, 390), (1210, 401), (1284, 444)],
    ]
    for pts in spikes:
        spts = scaled(pts, scale, dy)
        draw.polygon(spts, fill=(153, 96, 54, 255))
        draw.line(spts + [spts[0]], fill=outline, width=max(4, 4 * scale), joint="curve")
        mask_draw.polygon(spts, fill=255)

    return add_texture(
        layer,
        mask,
        rng,
        [(53, 42, 32), (116, 88, 57), (153, 119, 75), (83, 62, 42)],
        6200,
        scale,
    )


def plate_points(cx, base_y, width, height, lean, asym):
    shoulder = height * 0.52
    return [
        (cx - width * 0.46, base_y),
        (cx - width * 0.58, base_y - height * 0.15),
        (cx - width * 0.48 + lean * 0.08, base_y - shoulder),
        (cx - width * 0.22 + lean * 0.36, base_y - height * 0.84),
        (cx + lean + width * asym * 0.07, base_y - height),
        (cx + width * 0.23 + lean * 0.36, base_y - height * 0.84),
        (cx + width * 0.48 + lean * 0.08, base_y - shoulder),
        (cx + width * 0.58, base_y - height * 0.15),
        (cx + width * 0.46, base_y),
    ]


def draw_plate(draw, mask_draw, rng, scale, variant, spec, far=False):
    cx, base_y, width, height, lean = spec
    dy = variant["body_drop"]
    ps = variant["plate_scale"] * (0.86 if far else variant["near_boost"])
    cx *= scale
    base_y = (base_y + dy) * scale
    width *= scale * ps
    height *= scale * ps
    lean *= scale

    points = plate_points(cx, base_y, width, height, lean, rng.uniform(-0.28, 0.28))
    if far:
        fill = (138, 92, 55, 225)
        edge = (82, 55, 36, 230)
        high = (190, 146, 95, 138)
        low = (58, 42, 31, 62)
    else:
        fill = (158, 101, 58, 255)
        edge = (52, 36, 25, 255)
        high = (220, 166, 95, 172)
        low = (60, 43, 30, 80)

    draw.ellipse((cx - width * 0.43, base_y - height * 0.02, cx + width * 0.43, base_y + height * 0.06), fill=low)
    draw.polygon(points, fill=fill)
    mask_draw.polygon(points, fill=230 if far else 255)
    draw.line(points + [points[0]], fill=edge, width=max(2, int(3.0 * scale)), joint="curve")
    draw.line(points[2:7], fill=high, width=max(1, int(1.0 * scale)), joint="curve")

    vein_x = cx + lean * 0.45
    draw.line((vein_x, base_y - height * 0.08, cx + lean, base_y - height * 0.92), fill=(72, 49, 34, 92), width=max(1, int(1.2 * scale)))
    if not far:
        for _ in range(80):
            x = rng.uniform(cx - width * 0.38, cx + width * 0.38)
            y = rng.uniform(base_y - height * 0.88, base_y - height * 0.12)
            if rng.random() < 0.5:
                draw.point((x, y), fill=(236, 188, 112, rng.randrange(45, 115)))
            else:
                draw.point((x, y), fill=(73, 49, 32, rng.randrange(35, 95)))


def draw_plates(layer, mask, rng, scale, variant):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    for spec in FAR_PLATES:
        draw_plate(draw, mask_draw, rng, scale, variant, spec, far=True)
    for spec in NEAR_PLATES:
        draw_plate(draw, mask_draw, rng, scale, variant, spec, far=False)
    return layer


def render_variant(key, output):
    variant = VARIANTS[key]
    scale = 2
    rng = random.Random(variant["seed"])
    canvas = Image.new("RGBA", (WIDTH * scale, HEIGHT * scale), (0, 0, 0, 0))
    bg = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw_background(ImageDraw.Draw(bg), rng, scale)
    canvas = Image.alpha_composite(canvas, bg)

    body_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    body_mask = Image.new("L", canvas.size, 0)
    body_layer = draw_body(body_layer, body_mask, rng, scale, variant)

    plate_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    plate_mask = Image.new("L", canvas.size, 0)
    plate_layer = draw_plates(plate_layer, plate_mask, rng, scale, variant)
    plate_layer = add_texture(
        plate_layer,
        plate_mask,
        rng,
        [(72, 46, 31), (174, 112, 64), (230, 176, 99), (118, 75, 43)],
        5200,
        scale,
        alpha=(8, 32),
    )

    canvas = Image.alpha_composite(canvas, plate_layer)
    canvas = Image.alpha_composite(canvas, body_layer)

    # Re-draw the plate row after the body so the bases remain visibly embedded,
    # while still preserving clear gaps between the individual dorsal plates.
    final_plate_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    final_plate_mask = Image.new("L", canvas.size, 0)
    draw_plates(final_plate_layer, final_plate_mask, rng, scale, variant)
    canvas = Image.alpha_composite(canvas, final_plate_layer)

    image = canvas.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    return output


def crop_plate_strip(source, output):
    image = Image.open(source).convert("RGB")
    crops = [
        ("neck small plates", (190, 250, 410, 505)),
        ("mid-back broad plates", (390, 155, 730, 505)),
        ("hip/tail-base plates", (700, 240, 1005, 515)),
        ("full dorsal row", (170, 140, 1010, 520)),
    ]
    thumb_w = 320
    thumb_h = 210
    label_h = 34
    sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * 2), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (label, box) in enumerate(crops):
        crop = image.crop(box)
        crop.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(crop, ((thumb_w - crop.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(45, 40, 34), font=font)
        sheet.paste(tile, ((idx % 2) * thumb_w, (idx // 2) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def make_contact_sheet(items, output):
    thumb_w = 432
    thumb_h = 268
    label_h = 42
    sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * 2), (232, 228, 218))
    font = ImageFont.load_default()
    for idx, (path, label) in enumerate(items):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 12), label[:64], fill=(45, 40, 34), font=font)
        sheet.paste(tile, ((idx % 2) * thumb_w, (idx // 2) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    outputs = []
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for key, variant in VARIANTS.items():
        path = OUTPUT_ROOT / f"stego_dorsal_plate_lock_v2_{key}.png"
        outputs.append((render_variant(key, path), variant["label"]))

    selected = ASSET_ROOT / "stegosaurus-stenops-dorsal-plate-lock-v2-guide.png"
    selected.parent.mkdir(parents=True, exist_ok=True)
    Image.open(outputs[0][0]).save(selected)

    contact_sheet = REVIEW_ROOT / "stego_dorsal_plate_lock_v2_contact_sheet.png"
    make_contact_sheet(outputs, contact_sheet)
    app_sheet = ASSET_ROOT / "stegosaurus-review-options-v38.png"
    make_contact_sheet(
        [
            (selected, "selected v2 guide: alternating broad plates"),
            (ASSET_ROOT / "stegosaurus-stenops-plate-readable-natural-v1.png", "previous natural: few rounded plates"),
            (ASSET_ROOT / "stegosaurus-stenops-plate-priority-structure-v1.png", "previous structure guide: flatter plates"),
            (ASSET_ROOT / "stegosaurus-stenops-plate-lock-ipcontrol-v1.png", "previous generated: rounded petal drift"),
        ],
        app_sheet,
    )

    crop_sheet = REVIEW_ROOT / "stego_dorsal_plate_lock_v2_plate_crops.png"
    app_crop_sheet = ASSET_ROOT / "stegosaurus-plate-crops-v10.png"
    crop_plate_strip(selected, crop_sheet)
    crop_plate_strip(selected, app_crop_sheet)

    review = {
        "taxonId": "stegosaurus-stenops",
        "round": "stego_dorsal_plate_lock_v2",
        "date": "2026-06-25",
        "objective": "Tighten the Stegosaurus dorsal-plate gate after review that the current first image still does not capture the plates well enough.",
        "referenceGate": {
            "required": [
                "many individual broad bony dorsal plates",
                "two visually staggered rows, with the far row offset behind the near row",
                "largest plates over the mid-back and hips",
                "smaller plates toward the neck and tail base",
                "clear sky/background gaps between individual plates at app-card scale",
                "low quadrupedal Stegosaurus body and four-spike thagomizer",
            ],
            "rejectIf": [
                "few rounded fins",
                "flower-petal or plant-leaf plates",
                "single continuous sail",
                "shell armor ridge",
                "thin tail bristles instead of a clean tail shaft and four tail spikes",
            ],
        },
        "selected": {
            "asset": str(selected.relative_to(ROOT)).replace("\\", "/"),
            "role": "structure reference and next ControlNet source",
            "reason": "The selected guide makes the alternating broad plate row readable before any natural-render polish is attempted.",
        },
        "reviewSheets": {
            "contactSheet": str(contact_sheet.relative_to(ROOT)).replace("\\", "/"),
            "plateCrops": str(crop_sheet.relative_to(ROOT)).replace("\\", "/"),
            "appContactSheet": str(app_sheet.relative_to(ROOT)).replace("\\", "/"),
            "appPlateCrops": str(app_crop_sheet.relative_to(ROOT)).replace("\\", "/"),
        },
        "nextRecommendation": "Use this guide as the control source with low IP-Adapter weight. Do not promote a natural output unless the separate plate silhouettes remain visible at app-card scale.",
    }
    review_path = REVIEW_ROOT / "stego_dorsal_plate_lock_v2_review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected": str(selected), "contactSheet": str(contact_sheet), "plateCrops": str(crop_sheet)}, indent=2))


if __name__ == "__main__":
    main()
