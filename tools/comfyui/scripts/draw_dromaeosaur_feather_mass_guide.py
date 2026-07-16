import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = (
    ROOT
    / "tools"
    / "comfyui"
    / "lora_training"
    / "dromaeosaur_feathered"
    / "references"
    / "dromaeosaur_feather_mass_guide_v1.png"
)


def ellipse(draw, box, fill, outline, width=3):
    draw.ellipse(box, fill=fill, outline=outline, width=width)


def polygon(draw, points, fill, outline, width=3):
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def line(draw, points, fill, width=4):
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_guide(output):
    image = Image.new("RGB", (1152, 768), (210, 226, 226))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 620, 1152, 768), fill=(220, 204, 171))

    dark = (48, 39, 31)
    feather = (106, 74, 48)
    feather_dark = (60, 44, 34)
    feather_mid = (142, 94, 56)
    feather_light = (215, 184, 125)
    cream = (222, 207, 166)
    claw = (34, 30, 26)

    # Long stiff dromaeosaur tail.
    polygon(draw, [(640, 382), (1095, 292), (1128, 316), (666, 455)], fill=feather, outline=dark, width=5)
    for x in range(700, 1060, 52):
        line(draw, [(x, 373 - (x - 700) * 0.16), (x + 42, 350 - (x - 700) * 0.15)], fill=feather_light, width=4)

    # Compact feathered torso and hip mass.
    ellipse(draw, (340, 285, 710, 535), fill=feather, outline=dark, width=5)
    ellipse(draw, (510, 345, 760, 555), fill=(92, 64, 44), outline=dark, width=5)
    polygon(draw, [(335, 400), (710, 415), (672, 555), (380, 546)], fill=cream, outline=dark, width=3)

    # Neck and head.
    line(draw, [(342, 332), (288, 285), (240, 248), (198, 232)], fill=feather_dark, width=54)
    line(draw, [(336, 348), (286, 306), (238, 272), (197, 258)], fill=cream, width=28)
    ellipse(draw, (145, 202, 255, 272), fill=feather_mid, outline=dark, width=4)
    polygon(draw, [(145, 236), (82, 248), (150, 260)], fill=feather_mid, outline=dark, width=4)
    draw.ellipse((202, 222, 213, 233), fill=(245, 233, 185), outline=dark, width=2)
    line(draw, [(94, 252), (178, 252)], fill=dark, width=3)

    # Back, neck, and hip feather masses. These are intentionally explicit for ControlNet.
    for index, x in enumerate(range(225, 735, 42)):
        base_y = 286 + int(index * 0.35)
        tip = (x + 24, base_y - 24 - (index % 3) * 5)
        polygon(
            draw,
            [(x - 18, base_y + 10), (x + 36, base_y + 13), tip],
            fill=feather_mid if index % 2 else feather_dark,
            outline=dark,
            width=3,
        )
    for index, x in enumerate(range(365, 705, 38)):
        line(draw, [(x, 310), (x + 52, 455)], fill=feather_light if index % 2 else feather_dark, width=4)
        line(draw, [(x + 16, 304), (x + 70, 430)], fill=(235, 210, 148), width=2)

    # Folded wing-like forelimbs: layered feathers tucked against the ribs.
    shoulder_a = (390, 350)
    shoulder_b = (490, 365)
    for index in range(9):
        start = (shoulder_a[0] + index * 15, shoulder_a[1] + (index % 2) * 6)
        end = (438 + index * 16, 520 - index * 5)
        line(draw, [start, end], fill=feather_dark if index % 2 else feather_mid, width=9)
        line(draw, [(start[0] + 4, start[1] - 3), (end[0] + 3, end[1] - 4)], fill=feather_light, width=3)
    for index in range(7):
        start = (shoulder_b[0] + index * 13, shoulder_b[1] + (index % 2) * 5)
        end = (545 + index * 12, 510 - index * 4)
        line(draw, [start, end], fill=feather_dark if index % 2 else feather_mid, width=8)
        line(draw, [(start[0] + 3, start[1] - 2), (end[0] + 3, end[1] - 4)], fill=feather_light, width=3)

    # Hind legs with raised sickle-claw intent.
    line(draw, [(510, 520), (482, 610), (430, 646)], fill=feather_dark, width=34)
    line(draw, [(625, 512), (680, 608), (774, 640)], fill=feather_dark, width=34)
    line(draw, [(428, 646), (492, 646)], fill=dark, width=13)
    line(draw, [(770, 640), (842, 638)], fill=dark, width=13)
    polygon(draw, [(456, 632), (505, 598), (480, 660)], fill=claw, outline=dark, width=2)
    polygon(draw, [(785, 624), (840, 594), (810, 657)], fill=claw, outline=dark, width=2)
    line(draw, [(458, 642), (420, 654)], fill=claw, width=5)
    line(draw, [(785, 636), (746, 650)], fill=claw, width=5)

    # Small labels outside the animal silhouette help humans, but stay away from the body.
    draw.text((18, 18), "project-owned dromaeosaur feather-mass control guide", fill=(42, 39, 35), font=ImageFont.load_default())

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    draw_guide(output)
    print(output)


if __name__ == "__main__":
    main()
