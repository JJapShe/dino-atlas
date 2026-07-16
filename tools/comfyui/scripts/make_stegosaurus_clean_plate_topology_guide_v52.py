from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUT = ASSET_ROOT / "stegosaurus-stenops-plate-topology-guide-clean-v52.png"


def draw_leg(draw, x, y, foot_shift=0):
    skin = (100, 70, 45)
    outline = (26, 22, 18)
    draw.polygon(
        [
            (x - 30, y),
            (x + 22, y + 2),
            (x + 12, y + 155),
            (x - 34, y + 155),
        ],
        fill=skin,
        outline=outline,
    )
    draw.polygon(
        [
            (x - 42 + foot_shift, y + 155),
            (x + 42 + foot_shift, y + 158),
            (x + 58 + foot_shift, y + 184),
            (x - 62 + foot_shift, y + 184),
        ],
        fill=(84, 59, 39),
        outline=outline,
    )
    for toe in range(4):
        tx = x - 34 + foot_shift + toe * 24
        draw.polygon([(tx, y + 184), (tx + 18, y + 184), (tx + 12, y + 202)], fill=(67, 48, 34), outline=outline)


def draw_plate(draw, cx, base_y, width, height, color):
    outline = (31, 25, 18)
    points = [
        (cx - width // 2, base_y),
        (cx - width // 2 + 8, base_y - height + 34),
        (cx, base_y - height),
        (cx + width // 2 - 8, base_y - height + 34),
        (cx + width // 2, base_y),
    ]
    draw.polygon(points, fill=color, outline=outline)
    draw.line((cx, base_y - height + 34, cx, base_y - 10), fill=(145, 95, 52), width=2)


def main():
    w, h = 1152, 768
    image = Image.new("RGB", (w, h), (197, 221, 219))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 590, w, h), fill=(210, 194, 144))
    for x in range(15, w, 38):
        draw.line((x, 610, x - 18, 650), fill=(142, 126, 88), width=2)

    skin = (103, 72, 45)
    outline = (26, 22, 18)

    # Body, neck, head, and tail are intentionally simple because this is a
    # ControlNet structure guide, not final app art.
    draw.polygon(
        [
            (205, 386),
            (275, 335),
            (455, 326),
            (680, 334),
            (840, 385),
            (805, 535),
            (660, 574),
            (385, 572),
            (244, 535),
        ],
        fill=skin,
        outline=outline,
    )
    draw.polygon([(206, 392), (83, 384), (38, 432), (129, 488), (229, 465)], fill=skin, outline=outline)
    draw.polygon([(38, 432), (0, 454), (0, 414)], fill=skin, outline=outline)
    draw.ellipse((84, 414, 98, 428), fill=(0, 0, 0))
    draw.line((38, 456, 110, 452), fill=outline, width=2)
    draw.polygon([(805, 394), (960, 340), (1136, 282), (987, 415), (842, 458)], fill=(70, 49, 32), outline=outline)
    draw.polygon([(980, 386), (1148, 284), (1026, 414)], fill=(91, 61, 37), outline=outline)
    draw.line((984, 399, 1146, 510), fill=(91, 61, 37), width=3)

    for args in [(300, 508, 4), (455, 526, -8), (640, 525, 4), (785, 504, -18)]:
        draw_leg(draw, *args)

    far_color = (122, 79, 45)
    near_color = (182, 113, 56)
    far = [
        (228, 360, 34, 96),
        (328, 331, 48, 128),
        (468, 325, 62, 170),
        (618, 322, 58, 170),
        (752, 360, 48, 124),
        (842, 440, 34, 82),
    ]
    near = [
        (282, 378, 38, 88),
        (394, 338, 54, 126),
        (538, 322, 68, 178),
        (678, 337, 58, 150),
        (786, 409, 44, 105),
        (882, 492, 32, 75),
    ]
    for plate in far:
        draw_plate(draw, *plate, far_color)
    for plate in near:
        draw_plate(draw, *plate, near_color)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
