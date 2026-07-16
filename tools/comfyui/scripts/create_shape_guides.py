import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
GUIDE_DIR = ROOT / "ComfyUI" / "input" / "dino_guides"


W, H = 1152, 768
GROUND = 590
BG = (232, 226, 210)
SKY = (210, 224, 225)
BODY = (95, 72, 48)
BODY_DARK = (54, 43, 32)
BODY_LIGHT = (138, 112, 77)


def base_canvas():
    image = Image.new("RGB", (W, H), SKY)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, GROUND, W, H), fill=BG)
    draw.line((0, GROUND, W, GROUND), fill=(168, 153, 123), width=4)
    return image, draw


def ellipse(draw, box, fill=BODY, outline=BODY_DARK, width=5):
    draw.ellipse(box, fill=fill, outline=outline, width=width)


def polygon(draw, points, fill=BODY, outline=BODY_DARK, width=5):
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def line(draw, points, fill=BODY_DARK, width=24):
    draw.line(points, fill=fill, width=width, joint="curve")


STEGOSAURUS_PLATES = [
    # cx, base_y, width, height, lean, far_row
    (270, 423, 32, 48, -8, True),
    (314, 392, 40, 74, -6, False),
    (358, 372, 46, 96, -4, True),
    (410, 354, 54, 122, -2, False),
    (468, 344, 62, 144, 3, True),
    (532, 340, 66, 154, 0, False),
    (596, 346, 62, 142, -2, True),
    (656, 362, 54, 118, 3, False),
    (710, 386, 46, 90, 4, True),
    (758, 414, 38, 66, 5, False),
    (805, 438, 30, 48, 4, True),
]


def stegosaurus_plate_points(cx, base_y, width, height, lean=0):
    return [
        (int(cx - width * 0.46), int(base_y + 2)),
        (int(cx - width * 0.52), int(base_y - height * 0.22)),
        (int(cx + lean - width * 0.42), int(base_y - height * 0.58)),
        (int(cx + lean - width * 0.18), int(base_y - height * 0.88)),
        (int(cx + lean + width * 0.10), int(base_y - height * 0.96)),
        (int(cx + lean + width * 0.32), int(base_y - height * 0.74)),
        (int(cx + width * 0.50), int(base_y - height * 0.32)),
        (int(cx + width * 0.42), int(base_y + 6)),
    ]


def herrerasaurus():
    image, draw = base_canvas()
    ellipse(draw, (388, 398, 708, 498), fill=(105, 78, 52))
    polygon(draw, [(678, 432), (980, 386), (1065, 402), (976, 424), (696, 464)])
    line(draw, [(414, 420), (334, 388), (270, 382)], width=23)
    ellipse(draw, (190, 356, 318, 398), fill=(118, 86, 57))
    polygon(draw, [(305, 378), (112, 362), (172, 392)], fill=(118, 86, 57), outline=BODY_DARK, width=5)
    draw.line((142, 382, 294, 382), fill=BODY_DARK, width=4)
    ellipse(draw, (238, 370, 249, 381), fill=BODY_DARK, outline=BODY_DARK, width=1)
    # Long bent grasping forelimbs distinguish it from tyrannosaurids.
    line(draw, [(450, 432), (396, 504), (336, 552)], width=21)
    line(draw, [(486, 436), (448, 510), (392, 558)], width=18)
    line(draw, [(336, 552), (302, 548)], width=8)
    line(draw, [(336, 552), (315, 575)], width=8)
    line(draw, [(336, 552), (346, 578)], width=7)
    line(draw, [(392, 558), (358, 562)], width=8)
    line(draw, [(392, 558), (372, 582)], width=8)
    line(draw, [(392, 558), (404, 582)], width=7)
    line(draw, [(545, 486), (522, GROUND), (470, 622)], width=25)
    line(draw, [(636, 482), (694, GROUND), (782, 615)], width=25)
    line(draw, [(468, 622), (542, 622)], width=12)
    line(draw, [(776, 615), (850, 615)], width=12)
    return image


def coelophysis():
    image, draw = base_canvas()
    ellipse(draw, (405, 390, 650, 505), fill=(112, 83, 55))
    polygon(draw, [(620, 430), (960, 376), (1040, 388), (960, 406), (640, 460)])
    line(draw, [(420, 420), (320, 330), (250, 330)], width=26)
    ellipse(draw, (190, 300, 315, 355), fill=(122, 90, 60))
    polygon(draw, [(295, 326), (135, 310), (188, 352)], fill=(122, 90, 60), outline=BODY_DARK, width=4)
    draw.line((156, 337, 294, 337), fill=BODY_DARK, width=3)
    ellipse(draw, (238, 316, 250, 328), fill=BODY_DARK, outline=BODY_DARK, width=1)
    # Coelophysis keeps small but visible grasping forelimbs, unlike bird wings.
    line(draw, [(458, 448), (430, 504), (390, 535)], width=15)
    line(draw, [(430, 504), (406, 532)], width=11)
    line(draw, [(390, 535), (366, 538)], width=6)
    line(draw, [(390, 535), (377, 554)], width=6)
    line(draw, [(408, 532), (385, 542)], width=6)
    line(draw, [(535, 492), (520, GROUND), (470, 620)], width=24)
    line(draw, [(600, 490), (655, GROUND), (740, 612)], width=24)
    line(draw, [(468, 620), (545, 618)], width=12)
    line(draw, [(736, 612), (810, 612)], width=12)
    return image


def plateosaurus():
    image, draw = base_canvas()
    # Early sauropodomorph: deep herbivore torso, hind-limb dominant,
    # long tail, and a low forward neck rather than a vertical sauropod pose.
    # The forelimbs are kept lifted and short so ControlNet does not turn it
    # into a four-equal-pillar sauropod.
    ellipse(draw, (340, 365, 775, 545), fill=(108, 83, 56))
    ellipse(draw, (456, 420, 745, 582), fill=(98, 74, 50))
    polygon(draw, [(720, 454), (1035, 414), (1120, 436), (1020, 464), (735, 496)])
    line(draw, [(386, 418), (314, 372), (235, 352), (170, 352)], width=32)
    ellipse(draw, (96, 328, 184, 370), fill=(119, 92, 62), outline=BODY_DARK, width=5)
    polygon(draw, [(116, 352), (42, 352), (112, 368)], fill=(119, 92, 62), outline=BODY_DARK, width=5)
    draw.line((62, 364, 170, 364), fill=BODY_DARK, width=3)
    ellipse(draw, (134, 342, 145, 353), fill=BODY_DARK, outline=BODY_DARK, width=1)
    # Short functional forelimbs are tucked near the chest; large thumb claws
    # are visible but do not touch the ground.
    line(draw, [(438, 462), (408, 500), (366, 520)], width=15)
    line(draw, [(482, 462), (454, 498), (412, 518)], width=14)
    for base_x, base_y in [(362, 520), (408, 518)]:
        polygon(draw, [(base_x, base_y), (base_x + 34, base_y - 14), (base_x + 20, base_y + 20)], fill=(212, 192, 132), outline=BODY_DARK, width=4)
        line(draw, [(base_x + 6, base_y + 8), (base_x - 16, base_y + 18)], fill=BODY_DARK, width=5)
        line(draw, [(base_x + 14, base_y + 6), (base_x - 2, base_y + 26)], fill=BODY_DARK, width=4)
    # Hind limbs are much heavier than the forelimbs; feet stay broad and
    # planted to force a side-profile, hind-limb-dominant read.
    line(draw, [(565, 500), (520, GROUND), (430, 626)], width=54)
    line(draw, [(690, 492), (744, GROUND), (848, 614)], width=56)
    line(draw, [(426, 626), (548, 626)], width=23)
    line(draw, [(840, 614), (950, 614)], width=23)
    return image


def allosaurus():
    image, draw = base_canvas()
    ellipse(draw, (350, 340, 720, 515), fill=(105, 79, 53))
    polygon(draw, [(675, 400), (1035, 342), (1090, 360), (1015, 392), (702, 462)])
    line(draw, [(390, 395), (280, 332), (205, 338)], width=48)
    ellipse(draw, (105, 294, 300, 362), fill=(114, 85, 57))
    polygon(draw, [(132, 330), (48, 335), (128, 352)], fill=(114, 85, 57), outline=BODY_DARK, width=5)
    polygon(draw, [(148, 302), (185, 282), (224, 304)], fill=(135, 98, 58), outline=BODY_DARK, width=3)
    polygon(draw, [(222, 306), (254, 288), (282, 314)], fill=(135, 98, 58), outline=BODY_DARK, width=3)
    draw.line((72, 340, 250, 344), fill=BODY_DARK, width=5)
    draw.line((78, 351, 242, 352), fill=BODY_DARK, width=2)
    ellipse(draw, (165, 314, 180, 329), fill=BODY_DARK, outline=BODY_DARK, width=1)
    # Three-finger forelimbs, longer than T. rex.
    line(draw, [(420, 430), (370, 502), (335, 530)], width=22)
    for dx in (0, 15, 30):
        line(draw, [(335, 530), (315 + dx, 552)], width=7)
    line(draw, [(585, 492), (535, GROUND), (472, 625)], width=38)
    line(draw, [(675, 490), (724, GROUND), (814, 616)], width=38)
    line(draw, [(468, 625), (552, 625)], width=16)
    line(draw, [(810, 616), (895, 615)], width=16)
    return image


def apatosaurus():
    image, draw = base_canvas()
    ellipse(draw, (335, 400, 780, 555), fill=(108, 87, 61))
    polygon(draw, [(730, 478), (1050, 446), (1140, 460), (1060, 480), (745, 508)], fill=(94, 73, 50), outline=BODY_DARK, width=5)
    # Low diplodocid neck carried forward, not the high vertical Brachiosaurus pose.
    line(draw, [(365, 438), (290, 398), (215, 382), (155, 378)], width=38)
    ellipse(draw, (98, 354, 175, 388), fill=(119, 94, 65), outline=BODY_DARK, width=5)
    polygon(draw, [(118, 374), (58, 374), (116, 388)], fill=(119, 94, 65), outline=BODY_DARK, width=5)
    ellipse(draw, (132, 365, 143, 376), fill=BODY_DARK, outline=BODY_DARK, width=1)
    # Low diplodocid proportions: front limbs not taller than hind limbs.
    for x, width in ((410, 30), (505, 32), (642, 34), (740, 34)):
        line(draw, [(x, 518), (x - 5, GROUND)], width=width)
        line(draw, [(x - 30, GROUND), (x + 42, GROUND)], width=16)
    return image


def stegosaurus():
    image, draw = base_canvas()
    ellipse(draw, (300, 340, 785, 560), fill=(102, 78, 52))
    polygon(draw, [(720, 440), (1015, 405), (1080, 430), (1010, 452), (730, 500)])
    polygon(draw, [(340, 420), (210, 405), (150, 430), (225, 465), (350, 480)])
    ellipse(draw, (105, 408, 235, 475), fill=(112, 88, 62))
    # Make the front head unmistakable so the thagomizer is not read as a face.
    ellipse(draw, (126, 428, 140, 442), fill=BODY_DARK, outline=BODY_DARK, width=1)
    polygon(draw, [(1030, 427), (1105, 398), (1088, 428), (1110, 452), (1035, 438)], fill=(122, 92, 56), outline=BODY_DARK, width=4)
    # Four tail spikes at the thagomizer.
    for p1, p2, p3 in [
        ((1010, 416), (1088, 364), (1036, 432)),
        ((1030, 432), (1120, 438), (1035, 456)),
        ((1000, 408), (1050, 344), (1022, 425)),
        ((1015, 448), (1082, 494), (1030, 462)),
    ]:
        polygon(draw, [p1, p2, p3], fill=(164, 134, 82), outline=BODY_DARK, width=4)
    # Alternating rows of many separate, rounded dorsal plates. Keep them
    # individual and varied rather than five giant triangular sails.
    for cx, base_y, plate_w, plate_h, lean, far_row in STEGOSAURUS_PLATES:
        pts = stegosaurus_plate_points(cx, base_y, plate_w, plate_h, lean)
        fill = (142, 105, 66) if far_row else (165, 124, 78)
        outline = (76, 58, 40) if far_row else BODY_DARK
        polygon(draw, pts, fill=fill, outline=outline, width=4)
    for x in (355, 465, 620, 735):
        line(draw, [(x, 520), (x - 20, GROUND)], width=30)
        line(draw, [(x - 10, GROUND), (x + 55, GROUND)], width=16)
    return image


def tyrannosaurus():
    image, draw = base_canvas()
    ellipse(draw, (350, 330, 710, 515), fill=(103, 79, 53))
    polygon(draw, [(660, 390), (1030, 330), (1090, 352), (1015, 385), (690, 460)])
    line(draw, [(385, 390), (255, 330), (170, 340)], width=56)
    ellipse(draw, (95, 285, 285, 370), fill=(112, 84, 57))
    polygon(draw, [(120, 334), (45, 342), (120, 360)], fill=(112, 84, 57), outline=BODY_DARK, width=5)
    draw.arc((70, 320, 230, 380), start=10, end=170, fill=BODY_DARK, width=5)
    ellipse(draw, (155, 310, 170, 325), fill=BODY_DARK, outline=BODY_DARK, width=1)
    # Short forelimbs with exactly two visible fingers.
    line(draw, [(405, 435), (352, 495)], width=22)
    line(draw, [(352, 495), (322, 520)], width=10)
    line(draw, [(352, 495), (365, 530)], width=10)
    line(draw, [(580, 495), (535, GROUND), (480, 625)], width=40)
    line(draw, [(665, 490), (720, GROUND), (800, 617)], width=40)
    line(draw, [(475, 625), (555, 625)], width=18)
    line(draw, [(790, 617), (870, 615)], width=18)
    return image


def triceratops():
    image, draw = base_canvas()
    # Ceratopsian guide: low dinosaur body, long tail, skull-attached frill, and toes instead of hooves.
    ellipse(draw, (395, 378, 825, 532), fill=(116, 91, 63))
    polygon(draw, [(795, 430), (1035, 382), (1110, 404), (1020, 438), (812, 486)], fill=(93, 72, 49), outline=BODY_DARK, width=5)
    polygon(draw, [(395, 430), (342, 405), (312, 440), (350, 486), (405, 486)], fill=(108, 83, 58), outline=BODY_DARK, width=5)

    # The frill is drawn as a tall shield directly behind the skull, not as a shoulder hump.
    ellipse(draw, (165, 305, 335, 505), fill=(131, 105, 76), outline=BODY_DARK, width=6)
    polygon(draw, [(205, 392), (72, 398), (38, 434), (92, 468), (218, 452)], fill=(124, 96, 68), outline=BODY_DARK, width=5)
    polygon(draw, [(78, 427), (22, 436), (76, 452)], fill=(124, 96, 68), outline=BODY_DARK, width=5)
    ellipse(draw, (116, 408, 128, 420), fill=BODY_DARK, outline=BODY_DARK, width=1)

    # Two brow horns plus one short nasal horn. Keep them tied to the skull, not a rhino-style nose horn pair.
    for horn in [
        [(132, 392), (50, 276), (160, 382)],
        [(190, 388), (178, 268), (220, 384)],
        [(88, 398), (56, 332), (118, 402)],
    ]:
        polygon(draw, horn, fill=(218, 199, 146), outline=BODY_DARK, width=4)

    leg_specs = [
        (440, 512, 402, GROUND - 14, 350, GROUND + 28),
        (540, 520, 535, GROUND - 8, 495, GROUND + 30),
        (665, 512, 694, GROUND - 8, 656, GROUND + 30),
        (775, 500, 820, GROUND - 12, 784, GROUND + 28),
    ]
    for hip_x, hip_y, ankle_x, ankle_y, foot_x, foot_y in leg_specs:
        line(draw, [(hip_x, hip_y), (ankle_x, ankle_y)], width=34)
        polygon(
            draw,
            [(ankle_x - 20, ankle_y - 2), (foot_x + 70, foot_y - 6), (foot_x + 82, foot_y + 10), (foot_x - 8, foot_y + 12)],
            fill=(75, 58, 40),
            outline=BODY_DARK,
            width=4,
        )
        for toe_x in (foot_x + 56, foot_x + 72, foot_x + 88):
            polygon(draw, [(toe_x, foot_y - 4), (toe_x + 18, foot_y + 2), (toe_x, foot_y + 8)], fill=(218, 199, 146), outline=BODY_DARK, width=2)
    return image


def triceratops_precision_guide():
    image, draw = base_canvas()
    # Stricter ceratopsian control guide for LoRA/ControlNet passes. The goal is
    # to lock four limbs, a long dinosaur tail, and a skull-attached frill without
    # the shoulder hump / hoof read that made earlier renders look like rhinos.
    body_fill = (118, 94, 67)
    dark = BODY_DARK
    horn = (222, 206, 154)

    # Low, long dinosaur torso with no high mammal shoulder hump.
    ellipse(draw, (340, 372, 795, 535), fill=body_fill, outline=dark, width=5)
    polygon(
        draw,
        [(760, 430), (1075, 372), (1128, 392), (1032, 438), (780, 485)],
        fill=(91, 72, 51),
        outline=dark,
        width=5,
    )

    # Neck bridge keeps the frill attached to the skull rather than floating as a sail.
    polygon(draw, [(332, 430), (385, 392), (432, 418), (408, 488), (350, 493)], fill=body_fill, outline=dark, width=5)

    # Solid frill behind skull, kept forward and low so it does not become a back sail.
    ellipse(draw, (172, 300, 365, 504), fill=(132, 106, 78), outline=dark, width=7)
    draw.arc((195, 330, 338, 478), start=102, end=258, fill=(96, 76, 56), width=5)

    # Closed beaked skull in side view.
    polygon(
        draw,
        [(208, 398), (74, 402), (38, 432), (80, 462), (218, 454), (288, 430)],
        fill=(126, 98, 70),
        outline=dark,
        width=5,
    )
    polygon(draw, [(82, 426), (20, 438), (80, 452)], fill=(126, 98, 70), outline=dark, width=5)
    ellipse(draw, (118, 410, 132, 424), fill=dark, outline=dark, width=1)
    draw.line((48, 446, 204, 448), fill=dark, width=4)

    # Exactly two brow horns plus one short nasal horn.
    polygon(draw, [(130, 394), (46, 274), (168, 384)], fill=horn, outline=dark, width=4)
    polygon(draw, [(190, 390), (168, 270), (224, 384)], fill=horn, outline=dark, width=4)
    polygon(draw, [(84, 402), (52, 338), (118, 405)], fill=horn, outline=dark, width=4)

    # Four separated dinosaur limbs only. Each foot has small toe triangles to
    # discourage hoof-like blocks while preserving a coarse ControlNet silhouette.
    leg_specs = [
        ((402, 506), (365, 574), (330, 620), 34),
        ((510, 514), (502, 582), (472, 624), 36),
        ((648, 512), (682, 582), (650, 624), 38),
        ((752, 500), (818, 570), (788, 616), 36),
    ]
    for hip, ankle, foot, width in leg_specs:
        line(draw, [hip, ankle], width=width)
        polygon(
            draw,
            [(ankle[0] - 22, ankle[1] - 4), (foot[0] + 74, foot[1] - 6), (foot[0] + 86, foot[1] + 10), (foot[0] - 12, foot[1] + 12)],
            fill=(74, 58, 42),
            outline=dark,
            width=4,
        )
        for toe_x in (foot[0] + 54, foot[0] + 70, foot[0] + 86):
            polygon(draw, [(toe_x, foot[1] - 6), (toe_x + 18, foot[1] + 1), (toe_x, foot[1] + 8)], fill=horn, outline=dark, width=2)

    return image


def brachiosaurus():
    image, draw = base_canvas()
    # High withers, tall forelimbs, and a shorter tail separate Brachiosaurus from low diplodocids.
    ellipse(draw, (380, 350, 720, 535), fill=(112, 88, 60))
    ellipse(draw, (355, 340, 555, 535), fill=(119, 94, 64))
    polygon(draw, [(690, 445), (955, 412), (1035, 432), (955, 458), (700, 488)], fill=(96, 74, 50), outline=BODY_DARK, width=5)
    line(draw, [(430, 380), (365, 230), (335, 112)], width=58)
    ellipse(draw, (288, 72, 392, 132), fill=(120, 94, 64), outline=BODY_DARK, width=5)
    polygon(draw, [(306, 100), (235, 102), (300, 122)], fill=(120, 94, 64), outline=BODY_DARK, width=5)
    ellipse(draw, (326, 91, 338, 103), fill=BODY_DARK, outline=BODY_DARK, width=1)
    for x in (430, 520):
        line(draw, [(x, 505), (x - 5, GROUND)], width=42)
        line(draw, [(x - 34, GROUND), (x + 54, GROUND)], width=20)
    for x in (620, 700):
        line(draw, [(x, 505), (x + 12, GROUND - 12)], width=32)
        line(draw, [(x - 18, GROUND - 12), (x + 52, GROUND - 12)], width=16)
    return image


def velociraptor():
    image, draw = base_canvas()
    ellipse(draw, (410, 370, 680, 505), fill=(105, 76, 51))
    polygon(draw, [(620, 420), (930, 360), (990, 376), (918, 407), (650, 465)])
    line(draw, [(455, 405), (355, 355), (295, 360)], width=34)
    ellipse(draw, (250, 320, 370, 390), fill=(112, 82, 56))
    polygon(draw, [(330, 352), (220, 330), (255, 375)], fill=(112, 82, 56), outline=BODY_DARK, width=5)
    # Feathered forelimbs held close to the torso; avoid a flying-bird silhouette.
    polygon(draw, [(500, 425), (452, 525), (565, 495), (592, 442)], fill=(84, 66, 47), outline=BODY_DARK, width=5)
    polygon(draw, [(548, 428), (548, 548), (650, 500), (625, 442)], fill=(79, 62, 44), outline=BODY_DARK, width=5)
    for offset in range(0, 6):
        draw.line((458 + offset * 12, 515 - offset * 5, 552 + offset * 7, 492 - offset * 5), fill=(168, 145, 99), width=4)
        draw.line((552 + offset * 12, 540 - offset * 8, 650, 502 - offset * 5), fill=(168, 145, 99), width=4)
    for x in range(420, 675, 36):
        draw.arc((x, 374, x + 38, 430), start=185, end=340, fill=(163, 132, 83), width=3)
    # Legs and sickle claw cue.
    line(draw, [(555, 485), (535, 585), (480, 620)], width=28)
    line(draw, [(610, 485), (645, 585), (735, 615)], width=28)
    polygon(draw, [(728, 608), (790, 580), (755, 625)], fill=(210, 194, 137), outline=BODY_DARK, width=4)
    polygon(draw, [(474, 610), (530, 590), (500, 626)], fill=(210, 194, 137), outline=BODY_DARK, width=4)
    # Feather texture hints.
    for x in range(430, 670, 28):
        draw.line((x, 390, x + 38, 465), fill=(146, 116, 78), width=4)
    return image


def velociraptor_feathered_guide():
    image, draw = base_canvas()
    draw.rectangle((0, GROUND - 4, W, GROUND + 8), fill=BG)

    feather_base = (92, 72, 52)
    feather_dark = (56, 45, 36)
    feather_warm = (145, 104, 64)
    feather_light = (178, 150, 102)

    # Long stiff tail, kept narrow so it reads as a dromaeosaur rather than a bulky tyrannosaur.
    polygon(
        draw,
        [(620, 420), (950, 354), (1038, 366), (955, 398), (642, 466)],
        fill=(92, 66, 45),
        outline=(68, 52, 40),
        width=3,
    )
    for idx, x in enumerate(range(650, 945, 34)):
        y = 447 - idx * 5
        draw.line((x, y, x + 58, y - 20), fill=(126, 92, 59), width=5)

    # Compact feathered body and hips.
    ellipse(draw, (390, 356, 695, 515), fill=feather_base, outline=feather_dark, width=4)
    ellipse(draw, (420, 375, 660, 506), fill=(111, 82, 56), outline=(74, 55, 40), width=2)

    # Low neck and narrow toothed snout; avoid an ostrich neck or bird beak.
    line(draw, [(430, 410), (342, 355), (282, 362)], fill=(86, 66, 49), width=34)
    ellipse(draw, (245, 325, 370, 392), fill=(105, 76, 53), outline=feather_dark, width=4)
    polygon(draw, [(328, 351), (218, 329), (253, 376)], fill=(104, 75, 53), outline=feather_dark, width=4)
    draw.line((246, 366, 336, 365), fill=(43, 34, 28), width=3)
    for tooth_x in range(258, 326, 13):
        draw.line((tooth_x, 365, tooth_x + 3, 374), fill=(226, 214, 170), width=2)
    ellipse(draw, (296, 345, 309, 358), fill=(36, 29, 24), outline=(36, 29, 24), width=1)

    # Folded feathered arms hanging against the torso, not open wings.
    polygon(draw, [(475, 415), (448, 508), (548, 492), (586, 440)], fill=(67, 53, 43), outline=(45, 37, 31), width=4)
    polygon(draw, [(548, 415), (548, 526), (646, 496), (635, 432)], fill=(63, 50, 41), outline=(45, 37, 31), width=4)
    for offset in range(0, 7):
        draw.line((456 + offset * 12, 500 - offset * 6, 548 + offset * 4, 488 - offset * 7), fill=feather_light, width=4)
        draw.line((552 + offset * 12, 516 - offset * 7, 646, 496 - offset * 5), fill=feather_light, width=4)

    # Layered body plumage: short overlapping marks, not scales or dorsal spines.
    for row, y in enumerate(range(388, 494, 20)):
        start = 418 + (row % 2) * 14
        for x in range(start, 650, 42):
            draw.arc((x, y, x + 36, y + 26), start=195, end=335, fill=feather_warm, width=3)
    for x in range(270, 370, 18):
        draw.line((x, 338, x + 36, 365), fill=(158, 121, 77), width=4)

    # Lean legs, feet, and explicit sickle-claw cue.
    line(draw, [(535, 492), (520, 580), (474, 620)], fill=feather_dark, width=26)
    line(draw, [(612, 490), (648, 582), (742, 614)], fill=feather_dark, width=26)
    line(draw, [(472, 620), (528, 620)], fill=feather_dark, width=13)
    line(draw, [(735, 614), (796, 612)], fill=feather_dark, width=13)
    polygon(draw, [(492, 610), (535, 585), (510, 628)], fill=(219, 203, 145), outline=feather_dark, width=3)
    polygon(draw, [(748, 603), (798, 575), (772, 622)], fill=(219, 203, 145), outline=feather_dark, width=3)

    # Soft downy outline around hips and back without upright quills.
    for x in range(402, 680, 24):
        wave = math.sin(x * 0.05) * 5
        draw.arc((x, 350 + wave, x + 42, 384 + wave), start=195, end=335, fill=(126, 96, 68), width=3)
    for x in range(430, 690, 28):
        draw.arc((x, 496, x + 34, 526), start=20, end=170, fill=(128, 99, 70), width=3)

    return image.filter(ImageFilter.GaussianBlur(radius=0.25))


def velociraptor_plumage_guide():
    image, draw = base_canvas()
    draw.rectangle((0, GROUND - 4, W, GROUND + 8), fill=BG)

    dark = (55, 43, 32)
    mid = (103, 76, 52)
    warm = (140, 104, 66)
    light = (186, 154, 98)

    # Clean small dromaeosaur silhouette.
    polygon(draw, [(620, 425), (948, 360), (1030, 370), (950, 395), (638, 464)], fill=(88, 64, 45), outline=dark, width=3)
    ellipse(draw, (392, 360, 684, 514), fill=mid, outline=dark, width=3)
    line(draw, [(430, 410), (348, 360), (292, 362)], fill=(92, 68, 48), width=30)
    ellipse(draw, (248, 328, 372, 390), fill=(108, 80, 56), outline=dark, width=3)
    polygon(draw, [(330, 352), (224, 334), (256, 374)], fill=(108, 80, 56), outline=dark, width=3)
    draw.line((246, 364, 334, 365), fill=(42, 34, 27), width=3)
    for tooth_x in range(260, 326, 14):
        draw.line((tooth_x, 365, tooth_x + 2, 372), fill=(225, 214, 173), width=2)
    ellipse(draw, (298, 345, 310, 357), fill=(35, 28, 23), outline=(35, 28, 23), width=1)

    # Folded feathered forelimbs as compact patches against the body.
    polygon(draw, [(492, 420), (456, 500), (550, 492), (580, 438)], fill=(69, 53, 41), outline=(45, 35, 28), width=3)
    polygon(draw, [(548, 418), (552, 512), (634, 492), (624, 436)], fill=(63, 49, 39), outline=(45, 35, 28), width=3)
    for offset in range(0, 6):
        draw.line((466 + offset * 13, 492 - offset * 6, 548 + offset * 6, 486 - offset * 5), fill=light, width=4)
        draw.line((558 + offset * 12, 504 - offset * 7, 634, 492 - offset * 5), fill=light, width=4)

    # Legs and sickle claws, kept visually separate from the arm patches.
    line(draw, [(536, 492), (520, 582), (474, 620)], fill=dark, width=24)
    line(draw, [(612, 490), (650, 582), (742, 614)], fill=dark, width=24)
    line(draw, [(472, 620), (528, 620)], fill=dark, width=12)
    line(draw, [(735, 614), (796, 612)], fill=dark, width=12)
    polygon(draw, [(492, 610), (536, 586), (510, 628)], fill=(218, 202, 145), outline=dark, width=3)
    polygon(draw, [(748, 604), (798, 578), (772, 623)], fill=(218, 202, 145), outline=dark, width=3)

    # Plumage texture stays inside the body silhouette.
    for row, y in enumerate(range(386, 494, 18)):
        start = 420 + (row % 2) * 13
        for x in range(start, 650, 42):
            draw.arc((x, y, x + 38, y + 26), start=200, end=340, fill=warm, width=3)
    for x in range(402, 674, 24):
        wave = math.sin(x * 0.05) * 5
        draw.arc((x, 354 + wave, x + 38, 384 + wave), start=205, end=330, fill=(128, 95, 64), width=3)
    # Leave the tail smooth; texture marks here tend to become stray tail-like artifacts.
    for x in range(270, 365, 20):
        draw.line((x, 340, x + 28, 362), fill=(154, 112, 70), width=3)

    return image.filter(ImageFilter.GaussianBlur(radius=0.4))


def ankylosaurus():
    image, draw = base_canvas()
    ellipse(draw, (255, 355, 820, 545), fill=(92, 82, 58))
    polygon(draw, [(235, 430), (135, 418), (95, 455), (155, 500), (255, 485)])
    polygon(draw, [(770, 450), (995, 505), (1030, 535), (775, 505)])
    ellipse(draw, (975, 475, 1125, 575), fill=(122, 101, 64))
    # Low rounded armor knobs embedded on the body, not vertical stegosaur plates.
    for x in range(300, 800, 54):
        ellipse(draw, (x, 360, x + 42, 400), fill=(137, 118, 74), width=3)
    for x in range(280, 790, 54):
        ellipse(draw, (x, 410, x + 38, 445), fill=(128, 108, 70), width=3)
    for x in range(325, 760, 70):
        ellipse(draw, (x, 326, x + 28, 354), fill=(128, 108, 70), width=3)
    for x in (335, 465, 610, 745):
        line(draw, [(x, 510), (x - 12, GROUND)], width=36)
        line(draw, [(x - 30, GROUND), (x + 40, GROUND)], width=18)
    return image


def make_soft_guide(image, taxon_id):
    """Turn the simple shape guide into a softer textured i2i guide."""
    source = image.convert("RGB")
    mask = Image.new("L", source.size, 0)
    mask_pixels = mask.load()
    source_pixels = source.load()
    for y in range(source.height):
        for x in range(source.width):
            r, g, b = source_pixels[x, y]
            is_subject = r < 190 and g < 175 and b < 155
            is_ground_line = abs(r - 168) < 12 and abs(g - 153) < 12 and abs(b - 123) < 12
            if is_subject and not is_ground_line:
                mask_pixels[x, y] = 255

    mask = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius=3.2))
    mask_pixels = mask.load()
    output, draw = base_canvas()
    # Remove the hard horizon line from the soft guide so it does not become a cartoon baseline.
    draw.rectangle((0, GROUND - 4, W, GROUND + 10), fill=BG)
    output_pixels = output.load()
    seed = sum(ord(char) for char in taxon_id)
    for y in range(output.height):
        for x in range(output.width):
            alpha = mask_pixels[x, y] / 255
            if alpha <= 0:
                continue
            wave = math.sin((x + seed) * 0.006) * 9 + math.cos((y + seed) * 0.009) * 6
            noise = math.sin((x * 0.021 + y * 0.017 + seed) * 0.33) * 4
            shade = 1.0 + (GROUND - y) * 0.00045
            r = int((106 + wave + noise) * shade)
            g = int((83 + wave * 0.55 + noise * 0.35) * shade)
            b = int((58 + wave * 0.28 + noise * 0.22) * shade)
            if "velociraptor" in taxon_id:
                r += 18
                g += 12
                b += 4
            if "brachiosaurus" in taxon_id:
                r += 10
                g += 8
                b += 4
            if "triceratops" in taxon_id:
                r += 8
                g += 5
            if "ankylosaurus" in taxon_id:
                r -= 8
                g += 3
                b += 3
            subject = (max(25, min(185, r)), max(25, min(160, g)), max(20, min(125, b)))
            bg = output_pixels[x, y]
            output_pixels[x, y] = tuple(int(bg[i] * (1 - alpha) + subject[i] * alpha) for i in range(3))

    # Preserve diagnostic features as soft value cues instead of hard black outlines.
    detail = Image.new("RGBA", source.size, (0, 0, 0, 0))
    detail_draw = ImageDraw.Draw(detail)
    if "stegosaurus" in taxon_id:
        for cx, base_y, plate_w, plate_h, lean, far_row in STEGOSAURUS_PLATES:
            pts = stegosaurus_plate_points(cx, base_y, plate_w, plate_h, lean)
            fill = (140, 105, 70, 110) if far_row else (172, 128, 76, 135)
            detail_draw.polygon(pts, fill=fill)
        for pts in [
            [(1010, 416), (1088, 364), (1036, 432)],
            [(1030, 432), (1120, 438), (1035, 456)],
            [(1000, 408), (1050, 344), (1022, 425)],
            [(1015, 448), (1082, 494), (1030, 462)],
        ]:
            detail_draw.polygon(pts, fill=(170, 138, 86, 135))
    if "ankylosaurus" in taxon_id:
        for x in range(300, 800, 54):
            detail_draw.ellipse((x, 360, x + 42, 400), fill=(145, 126, 82, 150))
        for x in range(280, 790, 54):
            detail_draw.ellipse((x, 410, x + 38, 445), fill=(135, 116, 76, 135))
        detail_draw.ellipse((975, 475, 1125, 575), fill=(125, 104, 68, 150))
    if "triceratops" in taxon_id:
        for horn in [
            [(118, 355), (40, 250), (145, 340)],
            [(190, 350), (160, 230), (220, 348)],
            [(88, 412), (20, 395), (92, 432)],
        ]:
            detail_draw.polygon(horn, fill=(214, 195, 145, 165))
    if "velociraptor" in taxon_id:
        for offset in range(0, 6):
            detail_draw.line((402 + offset * 22, 555 - offset * 8, 552 + offset * 10, 502 - offset * 8), fill=(184, 159, 108, 140), width=8)
            detail_draw.line((528 + offset * 20, 575 - offset * 12, 664, 505 - offset * 8), fill=(184, 159, 108, 140), width=8)
    output = Image.alpha_composite(output.convert("RGBA"), detail).convert("RGB")
    return output.filter(ImageFilter.GaussianBlur(radius=0.45))


GUIDES = {
    "herrerasaurus-ischigualastensis": herrerasaurus,
    "coelophysis-bauri": coelophysis,
    "plateosaurus-engelhardti": plateosaurus,
    "allosaurus-fragilis": allosaurus,
    "apatosaurus-ajax": apatosaurus,
    "tyrannosaurus-rex": tyrannosaurus,
    "triceratops-horridus": triceratops,
    "stegosaurus-stenops": stegosaurus,
    "velociraptor-mongoliensis": velociraptor,
    "brachiosaurus-altithorax": brachiosaurus,
    "ankylosaurus-magniventris": ankylosaurus,
}


def save_guides(taxon_ids):
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for taxon_id in taxon_ids:
        image = GUIDES[taxon_id]().filter(ImageFilter.GaussianBlur(radius=0.6))
        output = GUIDE_DIR / f"{taxon_id}_shape.png"
        image.save(output)
        outputs.append(output)
        soft = make_soft_guide(image, taxon_id)
        soft_output = GUIDE_DIR / f"{taxon_id}_shape_soft.png"
        soft.save(soft_output)
        outputs.append(soft_output)
        sd15_output = GUIDE_DIR / f"{taxon_id}_shape_sd15.png"
        image.resize((768, 512), Image.Resampling.LANCZOS).save(sd15_output)
        outputs.append(sd15_output)
        soft_sd15_output = GUIDE_DIR / f"{taxon_id}_shape_soft_sd15.png"
        soft.resize((768, 512), Image.Resampling.LANCZOS).save(soft_sd15_output)
        outputs.append(soft_sd15_output)
        if taxon_id == "velociraptor-mongoliensis":
            feathered = velociraptor_feathered_guide()
            feathered_output = GUIDE_DIR / f"{taxon_id}_shape_feathered.png"
            feathered.save(feathered_output)
            outputs.append(feathered_output)
            feathered_sd15_output = GUIDE_DIR / f"{taxon_id}_shape_feathered_sd15.png"
            feathered.resize((768, 512), Image.Resampling.LANCZOS).save(feathered_sd15_output)
            outputs.append(feathered_sd15_output)
            plumage = velociraptor_plumage_guide()
            plumage_output = GUIDE_DIR / f"{taxon_id}_shape_plumage.png"
            plumage.save(plumage_output)
            outputs.append(plumage_output)
            plumage_sd15_output = GUIDE_DIR / f"{taxon_id}_shape_plumage_sd15.png"
            plumage.resize((768, 512), Image.Resampling.LANCZOS).save(plumage_sd15_output)
            outputs.append(plumage_sd15_output)
        if taxon_id == "triceratops-horridus":
            precision = triceratops_precision_guide().filter(ImageFilter.GaussianBlur(radius=0.45))
            precision_output = GUIDE_DIR / f"{taxon_id}_shape_v3.png"
            precision.save(precision_output)
            outputs.append(precision_output)
            precision_soft = make_soft_guide(precision, taxon_id)
            precision_soft_output = GUIDE_DIR / f"{taxon_id}_shape_v3_soft.png"
            precision_soft.save(precision_soft_output)
            outputs.append(precision_soft_output)
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", action="append", choices=sorted(GUIDES))
    args = parser.parse_args()
    taxon_ids = args.taxon_id or sorted(GUIDES)
    for output in save_guides(taxon_ids):
        print(output)


if __name__ == "__main__":
    main()
