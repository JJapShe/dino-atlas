import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history
from generate_dino_prompt import build_prompt


ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = ROOT / "ComfyUI" / "input"
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_inpaint_api.json"
LORA_TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_lora_inpaint_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


MASK_PRESETS = {
    "stego_left_tail_tip": {
        "polygons": [
            [(0, 390), (275, 380), (290, 535), (0, 555)],
        ],
    },
    "stego_left_tail_tip_tight": {
        "polygons": [
            [(0, 370), (155, 384), (172, 545), (0, 555)],
        ],
    },
    "stego_right_tail_tip": {
        "polygons": [
            [(1000, 360), (1152, 335), (1152, 505), (1005, 470)],
        ],
    },
    "stego_right_tail_tip_tight": {
        "polygons": [
            [(1046, 382), (1152, 358), (1152, 482), (1040, 452)],
        ],
    },
    "stego_dorsal_plates": {
        "polygons": [
            [
                (210, 422),
                (238, 338),
                (282, 260),
                (350, 182),
                (452, 118),
                (560, 88),
                (668, 98),
                (762, 154),
                (840, 236),
                (924, 332),
                (952, 408),
                (880, 430),
                (798, 378),
                (710, 326),
                (610, 300),
                (506, 294),
                (410, 316),
                (320, 366),
                (252, 424),
            ],
        ],
    },
    "tail_thread": {
        "polygons": [
        [(850, 446), (1130, 478), (1130, 520), (850, 492)],
        ],
    },
    "tail_thread_tight": {
        "lines": [
            {
                "points": [(820, 431), (895, 428), (970, 417), (1060, 393)],
                "width": 10,
            },
            {
                "points": [(850, 438), (925, 429), (1010, 415)],
                "width": 7,
            },
        ],
    },
    "rear_artifact": {
        "polygons": [
        [(610, 498), (790, 520), (835, 615), (665, 640), (570, 560)],
        ],
    },
    "rear_artifact_tight": {
        "lines": [
            {
                "points": [(635, 536), (675, 580), (748, 606), (835, 603)],
                "width": 34,
            },
        ],
    },
    "tail_and_rear_artifact": {
        "polygons": [
        [(850, 446), (1130, 478), (1130, 520), (850, 492)],
        [(610, 498), (790, 520), (835, 615), (665, 640), (570, 560)],
        ],
    },
    "tail_and_rear_artifact_tight": {
        "lines": [
            {
                "points": [(820, 431), (895, 428), (970, 417), (1060, 393)],
                "width": 10,
            },
            {
                "points": [(850, 438), (925, 429), (1010, 415)],
                "width": 7,
            },
            {
                "points": [(635, 536), (675, 580), (748, 606), (835, 603)],
                "width": 34,
            },
        ],
    },
    "trex_forelimbs_right_side": {
        "polygons": [
            [(700, 340), (875, 345), (900, 520), (700, 535)],
        ],
    },
    "trex_forelimbs_lora_v2": {
        "polygons": [
            [(245, 260), (450, 255), (510, 510), (315, 555), (230, 430)],
        ],
    },
    "trex_tuckedarms_current": {
        "polygons": [
            [(555, 330), (710, 330), (732, 535), (560, 560), (520, 450)],
        ],
    },
    "trex_v3_tinyarms_current": {
        "polygons": [
            [(370, 330), (620, 330), (642, 612), (420, 638), (340, 470)],
        ],
    },
    "trex_v3_twofinger_hands_tight": {
        "polygons": [
            [(420, 385), (598, 392), (612, 630), (428, 638), (392, 505)],
        ],
    },
    "allosaurus_hand_tight": {
        "polygons": [
            [(315, 505), (404, 500), (420, 592), (332, 610), (292, 548)],
        ],
    },
    "allosaurus_hand_foot_tight": {
        "polygons": [
            [(315, 505), (404, 500), (420, 592), (332, 610), (292, 548)],
            [(432, 642), (582, 636), (610, 724), (420, 732)],
            [(628, 648), (760, 650), (770, 724), (620, 732)],
        ],
    },
    "triceratops_head_frill_right": {
        "polygons": [
            [(610, 150), (815, 95), (1048, 165), (1152, 278), (1152, 470), (970, 525), (730, 480), (555, 330)],
        ],
    },
    "triceratops_head_frill_wide_right": {
        "polygons": [
            [(500, 82), (685, 62), (850, 104), (1048, 178), (1138, 292), (1110, 430), (970, 525), (735, 515), (552, 430), (472, 265)],
        ],
    },
    "triceratops_snout_right": {
        "polygons": [
            [(850, 250), (1035, 235), (1145, 292), (1148, 450), (1030, 492), (870, 438), (820, 330)],
        ],
    },
    "triceratops_nasal_horn_top": {
        "polygons": [
            [(875, 235), (980, 225), (1030, 330), (920, 360), (850, 305)],
        ],
    },
    "triceratops_mouth_gap_right": {
        "polygons": [
            [(805, 360), (1148, 350), (1152, 470), (835, 485), (770, 420)],
        ],
    },
    "triceratops_v3_snout_mouth_left": {
        "polygons": [
            [(0, 348), (112, 314), (246, 312), (315, 372), (274, 476), (68, 494), (0, 446)],
        ],
    },
    "triceratops_v3_nasal_horn_left": {
        "polygons": [
            [(16, 374), (96, 346), (145, 378), (126, 426), (38, 438), (0, 408)],
        ],
    },
    "triceratops_v3_nasal_horn_micro_left": {
        "polygons": [
            [(42, 360), (86, 342), (126, 366), (112, 402), (60, 412), (34, 388)],
        ],
    },
    "triceratops_v7_closed_beak_left_tight": {
        "polygons": [
            [(82, 468), (238, 444), (426, 470), (486, 538), (420, 610), (168, 622), (72, 566)],
        ],
    },
    "triceratops_v7_lower_beak_left_micro": {
        "polygons": [
            [(122, 512), (260, 496), (386, 512), (424, 564), (356, 606), (150, 602), (88, 558)],
        ],
    },
    "triceratops_v7_mouth_seam_left_micro": {
        "lines": [
            {
                "points": [(72, 562), (155, 574), (255, 568), (358, 546)],
                "width": 46,
            },
            {
                "points": [(98, 594), (190, 600), (300, 586)],
                "width": 28,
            },
        ],
    },
    "coelophysis_background_keep_body": {
        "background": True,
        "polygons": [
            [(470, 285), (705, 278), (828, 335), (806, 462), (630, 510), (492, 448)],
            [(850, 82), (1048, 88), (1070, 165), (920, 210), (815, 182)],
        ],
        "lines": [
            {
                "points": [(0, 458), (175, 456), (350, 438), (520, 408)],
                "width": 52,
            },
            {
                "points": [(704, 332), (770, 260), (835, 175), (925, 112)],
                "width": 54,
            },
            {
                "points": [(586, 456), (545, 560), (520, 675)],
                "width": 44,
            },
            {
                "points": [(675, 462), (716, 590), (734, 660)],
                "width": 42,
            },
            {
                "points": [(512, 674), (575, 670)],
                "width": 28,
            },
            {
                "points": [(724, 660), (790, 654)],
                "width": 28,
            },
            {
                "points": [(700, 385), (732, 460), (744, 525)],
                "width": 26,
            },
        ],
    },
    "apatosaurus_background_keep_body": {
        "background": True,
        "keep_polygons": [
            [
                (342, 438), (430, 398), (565, 378), (700, 384), (792, 430),
                (806, 504), (740, 562), (602, 586), (464, 560), (350, 514),
            ],
        ],
        "lines": [
            {
                "points": [(12, 382), (115, 384), (220, 398), (320, 430), (410, 465)],
                "width": 48,
            },
            {
                "points": [(735, 468), (875, 456), (1035, 456), (1148, 468)],
                "width": 46,
            },
            {
                "points": [(365, 438), (292, 400), (210, 382), (118, 378), (60, 382)],
                "width": 50,
            },
            {
                "points": [(392, 520), (382, 602), (378, 635)],
                "width": 72,
            },
            {
                "points": [(515, 512), (500, 604), (500, 635)],
                "width": 78,
            },
            {
                "points": [(642, 510), (632, 600), (630, 636)],
                "width": 78,
            },
            {
                "points": [(742, 505), (730, 598), (724, 636)],
                "width": 76,
            },
            {
                "points": [(350, 636), (456, 636)],
                "width": 38,
            },
            {
                "points": [(470, 636), (572, 636)],
                "width": 38,
            },
            {
                "points": [(604, 636), (704, 636)],
                "width": 38,
            },
            {
                "points": [(698, 636), (800, 636)],
                "width": 38,
            },
        ],
    },
    "plateosaurus_forelimbs_left": {
        "polygons": [
            [(330, 430), (500, 420), (535, 600), (365, 635), (305, 540)],
        ],
    },
    "plateosaurus_thumb_claw_tips": {
        "polygons": [
            [(392, 530), (462, 530), (476, 612), (404, 626), (370, 584)],
            [(462, 560), (525, 560), (532, 640), (464, 652), (438, 606)],
        ],
    },
    "velociraptor_plumage_overlay": {
        "polygons": [
            [(125, 185), (250, 165), (420, 245), (730, 260), (1090, 330), (1115, 388), (760, 440), (610, 510), (360, 470), (205, 345), (95, 285)],
        ],
        "lines": [
            {
                "points": [(240, 185), (355, 240), (505, 284), (680, 300), (840, 330), (1025, 360)],
                "width": 58,
            },
            {
                "points": [(420, 355), (525, 430), (640, 465)],
                "width": 92,
            },
        ],
    },
    "velociraptor_feather_bands": {
        "lines": [
            {
                "points": [(150, 205), (260, 190), (405, 250), (555, 285), (760, 305), (1035, 365)],
                "width": 44,
            },
            {
                "points": [(415, 345), (505, 410), (625, 465)],
                "width": 70,
            },
            {
                "points": [(690, 300), (840, 325), (1045, 360)],
                "width": 38,
            },
        ],
    },
    "velociraptor_background_keep_body": {
        "background": True,
        "keep_polygons": [
            [
                (40, 285), (112, 235), (240, 205), (380, 230), (540, 275), (730, 305),
                (1015, 330), (1118, 370), (1110, 438), (900, 450), (725, 470), (625, 565),
                (510, 642), (380, 660), (288, 580), (190, 518), (95, 448), (38, 360),
            ],
        ],
        "lines": [
            {
                "points": [(330, 500), (350, 600), (415, 650)],
                "width": 86,
            },
            {
                "points": [(775, 440), (900, 500), (1005, 522)],
                "width": 74,
            },
        ],
    },
    "velociraptor_sickle_claws": {
        "polygons": [
            [(350, 585), (535, 585), (555, 714), (330, 724)],
            [(760, 610), (948, 612), (970, 732), (742, 732)],
        ],
    },
    "velociraptor_v9_feet_modest_sickle": {
        "polygons": [
            [(548, 652), (892, 640), (934, 878), (550, 910), (480, 770)],
            [(690, 612), (1034, 612), (1070, 878), (696, 910), (635, 742)],
        ],
    },
    "velociraptor_v9_sickle_claw_tips": {
        "polygons": [
            [(575, 675), (760, 660), (820, 792), (646, 836), (548, 760)],
            [(828, 660), (1005, 666), (1022, 798), (842, 842), (764, 748)],
        ],
    },
    "velociraptor_v9_front_hook_reduce_tight": {
        "polygons": [
            [(560, 646), (704, 636), (746, 744), (658, 822), (548, 774), (532, 692)],
        ],
    },
    "velociraptor_head_snout": {
        "polygons": [
            [(88, 120), (305, 118), (372, 236), (318, 342), (132, 350), (58, 252)],
        ],
    },
    "allosaurus_head_jaw_left": {
        "polygons": [
            [(36, 70), (292, 62), (425, 150), (435, 292), (280, 350), (72, 292), (22, 172)],
        ],
    },
    "ankylosaurus_dorsal_spines": {
        "lines": [
            {
                "points": [(210, 402), (330, 376), (500, 360), (690, 366), (845, 396)],
                "width": 58,
            },
            {
                "points": [(285, 384), (470, 352), (665, 355), (805, 382)],
                "width": 34,
            },
        ],
    },
    "ankylosaurus_dorsal_spines_wide": {
        "lines": [
            {
                "points": [(165, 418), (320, 382), (505, 350), (705, 356), (875, 398)],
                "width": 88,
            },
            {
                "points": [(260, 360), (475, 332), (680, 338), (825, 372)],
                "width": 56,
            },
        ],
    },
    "ankylosaurus_osteoderm_band": {
        "lines": [
            {
                "points": [(150, 430), (300, 390), (485, 365), (695, 372), (855, 410)],
                "width": 92,
            },
            {
                "points": [(250, 468), (420, 430), (640, 425), (805, 456)],
                "width": 62,
            },
        ],
    },
    "ankylosaurus_tail_club_left": {
        "polygons": [
            [(0, 318), (210, 322), (250, 470), (174, 548), (0, 540)],
        ],
    },
    "brachiosaurus_v3_outer_tail_reduce": {
        "polygons": [
            [(1160, 520), (1570, 505), (1570, 820), (1135, 800), (1085, 650)],
        ],
    },
    "brachiosaurus_v3_tail_tip_reduce_tight": {
        "polygons": [
            [(1285, 550), (1570, 535), (1570, 790), (1250, 770), (1210, 650)],
        ],
    },
    "brachiosaurus_v3_tail_half_reduce": {
        "polygons": [
            [(910, 470), (1570, 465), (1570, 850), (885, 835), (805, 635)],
        ],
    },
}


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def input_name(path):
    return str(path.relative_to(COMFY_INPUT)).replace("\\", "/")


def make_mask(source, output, preset, feather):
    image = Image.open(source).convert("RGB")
    mask_preset = MASK_PRESETS[preset]
    mask = Image.new("L", image.size, 255 if mask_preset.get("background") else 0)
    draw = ImageDraw.Draw(mask)
    keep_fill = 0 if mask_preset.get("background") else 255
    for polygon in mask_preset.get("polygons", []):
        draw.polygon(polygon, fill=255)
    for polygon in mask_preset.get("keep_polygons", []):
        draw.polygon(polygon, fill=keep_fill)
    for stroke in mask_preset.get("lines", []):
        draw.line(stroke["points"], fill=keep_fill, width=stroke["width"], joint="curve")
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
    mask_rgb = Image.merge("RGB", (mask, mask, mask))
    output.parent.mkdir(parents=True, exist_ok=True)
    mask_rgb.save(output)
    return output


EDIT_PROMPTS = {
    "cleanup": {
        "positive": (
            "preserve the existing dinosaur silhouette outside the masked area, "
            "masked area should become clean matching background or a natural continuous body edge only, "
            "remove stray extra tail line, remove duplicate rear limb artifact, no new appendage"
        ),
        "negative": (
            "extra tail, second tail, dangling tail under the body, duplicate rear leg, extra rear limb, "
            "long curved appendage below the body, floating feather line, detached body part, smeared limb"
        ),
    },
    "stego_tail_spikes": {
        "positive": (
            "preserve everything outside the masked area exactly, keep the same tail base and lighting, "
            "masked tail tip becomes the end of a Stegosaurus tail with four long natural thagomizer spikes, "
            "two spikes angling upward and two spikes angling backward, realistic keratin texture, attached to the tail tip"
        ),
        "negative": (
            "second head, face on tail, eye on tail, horned head, duplicate tail, extra animal, detached spikes, "
            "floating spikes, metal spikes, oversized fantasy spikes, text, watermark, signature"
        ),
    },
    "stego_right_tail_spikes_strict": {
        "positive": (
            "preserve everything outside the masked right tail tip exactly, keep the same Stegosaurus body, separated dorsal plates, legs, ground, background, and lighting, "
            "the masked right tail tip becomes one continuous Stegosaurus tail ending in exactly four visible thagomizer spikes, "
            "two spikes angle upward and backward, two spikes angle downward and backward, all four are attached to the tail tip, "
            "natural keratin texture matching the tail color, no smooth tail tip"
        ),
        "negative": (
            "missing tail spikes, smooth tail tip, fewer than four spikes, more than four spikes, tiny hair-like spikes, "
            "detached spikes, floating spikes, transparent overlay, paper spikes, metal spikes, fantasy mace, second tail, "
            "second head, face on tail, eye on tail, horned head, extra animal, changed body, changed dorsal plates, text, watermark, signature"
        ),
    },
    "stego_tail_spikes_refine": {
        "positive": (
            "preserve everything outside the masked tail tip exactly, keep the same body, plates, legs, ground, background, tail base, and lighting, "
            "keep the existing four Stegosaurus thagomizer spikes visible in the masked area, do not remove any spike, "
            "refine the four spikes so they look like opaque natural keratin spikes attached to the tail tip, "
            "match the brown tail skin, same light direction, realistic texture, no transparent overlay look"
        ),
        "negative": (
            "missing tail spikes, removed spikes, fewer than four spikes, smooth tail tip, transparent paper spikes, flat vector spikes, "
            "detached spikes, floating spikes, metal spikes, oversized fantasy spikes, second head, face on tail, eye on tail, "
            "horned head, duplicate tail, extra animal, changed body, changed plates, text, watermark, signature"
        ),
    },
    "stego_dorsal_plates": {
        "positive": (
            "preserve everything outside the masked dorsal plates exactly, keep the same Stegosaurus body, small low head, four legs, tail, thagomizer, ground, background, and lighting, "
            "masked area becomes many separate broad kite-shaped Stegosaurus dorsal plates attached individually along the back, "
            "two staggered alternating rows of opaque bony plates, largest plates over the hips and mid-back, smaller plates near the neck and tail base, "
            "clear gaps of sky visible between individual plates, natural keratin and bony texture matching the body color, "
            "not a single sail and not a row of small spines"
        ),
        "negative": (
            "missing dorsal plates, single smooth sail, continuous back fin, rounded hump fins, soft oval bumps, "
            "five huge triangular mountain plates, roof-like identical triangles, sawblade crest, comb-like needle spines, "
            "bristles, fur, feathers, porcupine quills, tail covered with many small spikes, transparent overlay, pasted paper plates, "
            "flat cartoon plates, detached plates, changed body, changed head, changed legs, changed tail, missing thagomizer, text, watermark, signature"
        ),
    },
    "stego_plate_air_gaps": {
        "positive": (
            "preserve everything outside the narrow masked seams exactly, keep the same Stegosaurus body, existing dorsal plates, head, legs, tail, ground, background, and lighting, "
            "the masked seams become narrow natural open air gaps between adjacent broad Stegosaurus dorsal plates, "
            "show blurred background color through the gaps so each plate reads as a separate opaque bony slab, "
            "add subtle dark bony plate edges on both sides of each gap, keep plate bases attached to the back"
        ),
        "negative": (
            "new plate row, removed plates, missing plates, fused scalloped fan, continuous sail, painted stripes, green plant stems, grass growing from the back, "
            "transparent overlay, paper cutout seams, detached plates, changed body, changed head, changed legs, changed tail, text, watermark, signature"
        ),
    },
    "stego_alternating_plate_bases": {
        "positive": (
            "preserve everything outside the masked dorsal plate base and gap areas exactly, keep the same Stegosaurus body, small low head, four planted feet, tail, four thagomizer spikes, ground, background, and lighting, "
            "masked areas clarify the bases and side edges of separate broad Stegosaurus dorsal plates, "
            "add subtle near-row and far-row overlap cues so the plates read as two staggered alternating rows attached individually along the back, "
            "keep sky-colored open gaps between plates, keep each plate opaque and bony with dark edge thickness, do not change the torso silhouette"
        ),
        "negative": (
            "new full plate row, removed plates, missing plates, single smooth sail, continuous scalloped fan, fused plate wall, identical roof teeth, comb-like spikes, "
            "leaf plates, plant leaves, pasted paper plates, transparent overlay, changed body hump, changed head, changed legs, changed tail, missing thagomizer, extra tail spikes, text, watermark, signature"
        ),
    },
    "trex_two_finger_forelimbs": {
        "positive": (
            "preserve everything outside the masked area exactly, keep the torso, lighting, background, and pose unchanged, "
            "masked area becomes two short Tyrannosaurus rex forelimbs held close to the chest, "
            "each visible hand ends in exactly two small clawed fingers, no third finger, "
            "small compact hands, short arms tucked close to the body, natural skin texture matching the torso"
        ),
        "negative": (
            "three fingers, four fingers, five fingers, extra fingers, human-like hands, long arms, "
            "oversized hands, large hook hands, giant black claws, raptor arms, bird wings, duplicate arms, missing arms, text, watermark, signature"
        ),
    },
    "trex_compact_two_finger_hands": {
        "positive": (
            "preserve everything outside the masked forelimb area exactly, keep the torso, belly, neck, head, legs, tail, ground, background, lighting, and pose unchanged, "
            "masked area becomes very short Tyrannosaurus rex forelimbs tucked close to the ribs, "
            "each visible hand has exactly two compact clawed fingers, two fingers only, paired like a small V shape, "
            "small blunt claws, compact wrists, arms do not hang below the belly, natural skin texture matching the chest"
        ),
        "negative": (
            "three fingers, four fingers, five fingers, extra fingers, third claw, spread hand with three claws, human-like hands, long arms, "
            "arms reaching below the belly, oversized hook claws, raptor arms, bird wings, duplicate arms, missing arms, changed torso, changed neck, text, watermark, signature"
        ),
    },
    "triceratops_head_frill": {
        "positive": (
            "preserve everything outside the masked area exactly, keep the body, legs, tail, ground, background, and lighting unchanged, "
            "masked area becomes a natural Triceratops horridus head and neck with a large solid shield-like frill attached behind the skull, "
            "exactly three horns total: two long brow horns growing above the eyes and one short nasal horn on the snout, "
            "no other horns anywhere, broad rounded shield frill with a smooth rim, closed parrot-like beak, no teeth visible, "
            "same skin color and realistic scale texture as the existing body, anatomically joined to the shoulders"
        ),
        "negative": (
            "rhinoceros head, mammal nose, mammal ears, hooves, missing frill, dorsal sail, frill on the back, "
            "extra horns, four horns, five horns, side horns, cheek horns, jaw horns, tusks, antelope horns, bull horns, unicorn horn, "
            "horn crown, spiked crown, spiky frill rim, split frill, open roaring mouth, sharp teeth, predator skull, "
            "theropod head, skull-only, detached head, second animal, text, watermark, signature"
        ),
    },
    "triceratops_head_frill_strict": {
        "positive": (
            "preserve everything outside the masked area exactly, keep the body, legs, tail, ground, background, and lighting unchanged, "
            "masked area becomes a natural side-profile Triceratops horridus head, short neck, and a large oval shield frill attached immediately behind the skull, "
            "the frill is a skull frill, not a dorsal sail, and it does not grow from the back or shoulder, "
            "exactly three facial horns total: two long brow horns above the eyes and one short nasal horn on the snout, "
            "smooth rounded frill rim with no spikes or saw teeth, closed parrot-like beak, no visible teeth, "
            "same skin color and realistic scale texture as the existing body, anatomically joined to the shoulders"
        ),
        "negative": (
            "rhinoceros head, mammal nose, mammal ears, hooves, missing frill, dorsal sail, shoulder sail, frill growing from the back, "
            "tall hump on the shoulders, extra horns, four horns, five horns, side horns, cheek horns, jaw horns, tusks, antelope horns, bull horns, unicorn horn, "
            "horn crown, spiked crown, spiky frill rim, sawtooth frill rim, scalloped sharp rim, split frill, open roaring mouth, sharp teeth, predator skull, "
            "theropod head, skull-only, detached head, second animal, text, watermark, signature"
        ),
    },
    "triceratops_nasal_horn_closed_beak": {
        "positive": (
            "preserve everything outside the masked area exactly, keep the body, frill, eye, two brow horns, legs, tail, ground, background, and lighting unchanged, "
            "masked snout becomes a natural Triceratops horridus side-profile snout with exactly one short nasal horn on top of the nose, "
            "closed parrot-like beak, no visible teeth, no open mouth, same skin color and realistic scale texture as the existing head"
        ),
        "negative": (
            "missing nasal horn, long rhinoceros horn, extra nasal horns, extra side horns, cheek horns, tusks, antelope horns, bull horns, "
            "open mouth, visible teeth, predator teeth, sharp teeth, mammal nose, rhinoceros head, detached beak, text, watermark, signature"
        ),
    },
    "triceratops_nasal_horn_only": {
        "positive": (
            "preserve everything outside the masked nasal-horn area exactly, keep the closed beak, mouth line, nostril, eye, brow horns, skull frill, body, legs, feet, tail, water, forest, and lighting unchanged, "
            "masked area becomes exactly one short natural Triceratops nasal horn growing from the top of the snout, smaller than the brow horns, "
            "solid keratin horn attached to the skull, side-profile, realistic texture matching the brow horns"
        ),
        "negative": (
            "missing nasal horn, black dash, painted triangle, paper triangle, flat sticker, long rhinoceros horn, extra nasal horns, "
            "extra side horns, cheek horns, open mouth, visible teeth, predator teeth, changed mouth, changed beak, changed frill, "
            "rhinoceros head, mammal nose, detached horn, text, watermark, signature"
        ),
    },
    "triceratops_nasal_horn_micro_blend": {
        "positive": (
            "preserve everything outside the tiny masked nasal horn area exactly, keep the eye, nostril, closed beak, mouth line, two brow horns, skull frill, neck, body, legs, feet, tail, trees, and lighting unchanged, "
            "blend the existing short nasal-horn guide into one small natural Triceratops nasal horn attached to the top of the snout, "
            "short blunt keratin horn, smaller than the brow horns, same light direction, realistic texture integrated with the snout skin"
        ),
        "negative": (
            "changed eye, changed beak, changed mouth, open mouth, visible teeth, changed frill, frill flap, changed brow horns, missing nasal horn, "
            "flat sticker, painted triangle, paper triangle, black outline, detached horn, extra horn, long rhinoceros horn, mammal nose, text, watermark, signature"
        ),
    },
    "triceratops_closed_beak_only": {
        "positive": (
            "preserve everything outside the masked mouth area exactly, keep the nasal horn, two brow horns, eye, nostril, skull frill, body, legs, feet, tail, water, forest, and lighting unchanged, "
            "masked area becomes a closed Triceratops parrot-like beak with only a narrow dark mouth seam, "
            "upper and lower beak meet cleanly, no visible teeth, no open mouth, realistic skin texture matching the head"
        ),
        "negative": (
            "open mouth, visible teeth, sharp teeth, predator teeth, tooth row, monster jaw, lipless jaw, giant mouth gap, "
            "changed nasal horn, missing nasal horn, extra horn, changed brow horns, changed frill, detached beak, "
            "rhinoceros head, mammal nose, text, watermark, signature"
        ),
    },
    "triceratops_v7_closed_beak_preserve_body": {
        "positive": (
            "preserve everything outside the masked mouth and lower beak area exactly, keep the low elongated ceratopsian body, long single tail, four legs, visible non-hoofed toes, skull frill, eye, nostril, nasal horn, and two brow horns unchanged, "
            "masked area becomes a natural closed Triceratops horridus parrot-like beak with the upper and lower beak touching, "
            "only a very thin dark mouth seam remains, no visible teeth, same scale texture and brown skin color as the surrounding snout, anatomically joined to the existing head"
        ),
        "negative": (
            "changed body, round mammal torso, high rhinoceros shoulder hump, changed tail, missing tail, changed feet, hooves, extra legs, changed frill, changed brow horns, changed nasal horn, "
            "open mouth, mouth gap, visible teeth, predator teeth, crocodile jaw, detached beak, oversized lower jaw, mammal lips, rhinoceros head, text, watermark, signature"
        ),
    },
    "triceratops_nonhoof_toes": {
        "positive": (
            "preserve everything outside the small masked foot and toe areas exactly, keep the low elongated Triceratops body, long single tail, four legs, skull-attached frill, eye, closed beak, nasal horn, two brow horns, ground, background, lighting, and pose unchanged, "
            "masked areas become natural Triceratops dinosaur feet with separated blunt non-hoofed toes, "
            "broad dry toes with small blunt claws, toes spread slightly on the ground, realistic wrinkled scale texture matching the legs, no new limbs"
        ),
        "negative": (
            "hooves, rhinoceros feet, horse hooves, cow hooves, elephant feet, mammal feet, single block foot, fused hoof, "
            "extra toes, extra legs, duplicate limbs, changed body, round mammal torso, high rhinoceros shoulder hump, changed tail, changed head, changed frill, changed horns, open mouth, visible teeth, text, watermark, signature"
        ),
    },
    "triceratops_matte_toe_claws": {
        "positive": (
            "preserve everything outside the tiny masked toe-claw highlight areas exactly, keep the low elongated Triceratops body, long single tail, four legs, skull-attached frill, closed beak, three horns, ground, background, lighting, and pose unchanged, "
            "masked areas become small blunt non-hoofed Triceratops toe claws with muted dark keratin color, "
            "matte natural claw tips partly dusty with sand, realistic wrinkled skin texture matching the existing toes, no shiny white nails and no hoof-like caps"
        ),
        "negative": (
            "bright white claws, shiny silver nails, metal claws, horse hooves, rhinoceros hooves, mammal hooves, oversized talons, sharp raptor claws, "
            "extra toes, fused hoof, extra legs, duplicate limbs, changed foot shape, changed body, changed head, changed frill, changed horns, open mouth, visible teeth, text, watermark, signature"
        ),
    },
    "plateosaurus_forelimbs_thumb_claws": {
        "positive": (
            "preserve everything outside the masked forelimb area exactly, keep the torso, neck, head, hind legs, tail, grass, forest, background, and lighting unchanged, "
            "masked area becomes two short Plateosaurus forelimbs held off the ground close to the chest, "
            "five-fingered grasping hands with one large thumb claw visible on each hand, hands not touching the ground, "
            "small functional arms much shorter than the hind legs, natural skin texture matching the body"
        ),
        "negative": (
            "front hands touching the ground, weight-bearing forelimbs, walking on four legs, quadrupedal pose, elephant feet, pillar forelegs, "
            "tiny tyrannosaur arms, missing arms, extra arms, extra legs, giant claws, predator talons, detached hands, text, watermark, signature"
        ),
    },
    "plateosaurus_thumb_claw_tips": {
        "positive": (
            "preserve everything outside the tiny masked hand-tip areas exactly, keep the existing arms, torso, belly, neck, head, hind legs, feet, tail, grass, forest, background, lighting, and pose unchanged, "
            "masked hand tips gain small readable five-fingered grasping Plateosaurus hands with one slightly larger inward thumb claw cue, "
            "hands remain lifted off the ground close to the chest, subtle natural skin texture matching the existing body, no new limbs"
        ),
        "negative": (
            "new arm, new leg, extra leg, duplicate limb, weight-bearing forelimb, front foot touching ground, walking on four legs, quadrupedal pose, "
            "giant predator talons, detached hand, floating claws, long sickle claws, changed torso, changed hind legs, changed tail, changed background, text, watermark, signature"
        ),
    },
    "velociraptor_plumage": {
        "positive": (
            "preserve the existing Velociraptor body silhouette, pose, legs, feet, claws, tail length, head position, ground, background, and lighting, "
            "masked area becomes dense layered downy feathers across the neck, torso, hips, upper tail, and folded wing-like forelimbs, "
            "short folded feathered arms held close against the ribs, natural brown and cream plumage matching the existing colors, "
            "fine feather texture rather than scales, no change to the overall anatomy"
        ),
        "negative": (
            "extra tail, second tail, tail under body, extra rear limb, duplicate leg, extra arms, missing arms, spread wings, flying wings, "
            "large bird wings, eagle wings, crane body, ostrich body, toothless beak, bird beak, porcupine quills, dorsal spikes, mohawk crest, "
            "long dangling feather line, detached feathers, black brush stroke, blurry smear, text, watermark, signature"
        ),
    },
    "velociraptor_feather_bands": {
        "positive": (
            "preserve everything outside the masked feather bands exactly, keep the silhouette, pose, legs, feet, tail length, head, ground, background, and lighting unchanged, "
            "masked bands become short layered natural feathers and soft feather tufts along the neck, back, hips, upper tail, and folded forelimbs, "
            "subtle brown and cream plumage, feather texture integrated into the existing body colors, no new limbs"
        ),
        "negative": (
            "extra tail, second tail, tail under body, extra leg, duplicate limb, detached feather line, long streamer, black brush stroke, "
            "large spread wings, flying wings, eagle wings, dorsal spikes, porcupine quills, mohawk crest, missing arms, missing feet, "
            "changed silhouette, blurry smear, text, watermark, signature"
        ),
    },
    "velociraptor_sickle_claws": {
        "positive": (
            "preserve everything outside the masked foot areas exactly, keep the body, tail, head, feathers, legs, ground, background, and lighting unchanged, "
            "masked areas become natural Velociraptor mongoliensis feet with two walking toes touching the sand and one enlarged sickle-shaped second toe claw held raised off the ground on each foot, "
            "small agile dromaeosaur feet, dark curved claws, realistic scale texture, no change to leg count"
        ),
        "negative": (
            "missing sickle claw, flat ordinary lizard feet, hooves, mammal feet, human feet, bird talons only, oversized monster claws, "
            "extra toes, extra feet, extra legs, duplicate limbs, changed body, changed pose, detached claws, text, watermark, signature"
        ),
    },
    "velociraptor_modest_sickle_toes": {
        "positive": (
            "preserve everything outside the masked foot areas exactly, keep the same Velociraptor body, long stiff tail, toothed snout, folded forelimbs, feather texture, leg count, ground, background, and lighting unchanged, "
            "masked areas become natural Velociraptor mongoliensis feet with two slim walking toes touching the dry sand and one modest raised second-toe sickle claw attached to each foot, "
            "the sickle claws are small dark curved claws, clearly attached to the second toes, raised just off the ground, not oversized, with realistic scale texture matching the existing legs"
        ),
        "negative": (
            "giant hook claw, oversized talon, eagle talon, monster claw, detached crescent, floating claw, black banana-shaped claw, huge sickle, "
            "missing sickle claw, flat ordinary lizard feet, hooves, mammal feet, human feet, extra toes, extra feet, extra legs, duplicate limbs, "
            "changed body, changed tail, changed head, changed feathers, changed pose, text, watermark, signature"
        ),
    },
    "velociraptor_reduce_front_hook": {
        "positive": (
            "preserve everything outside the tiny masked front-foot hook area exactly, keep the same legs, toes, rear foot, body, tail, head, feathers, ground, background, and lighting unchanged, "
            "masked area becomes a smaller natural raised Velociraptor second-toe sickle claw attached to the existing front foot, "
            "shorter dark curved claw, close to the toe, realistic scale, same color and texture as the surrounding foot, no change to the walking toes"
        ),
        "negative": (
            "giant hook claw, oversized talon, eagle talon, monster claw, detached crescent, floating claw, black banana-shaped claw, extra claw in the air, "
            "missing foot, changed toes, extra toes, extra feet, extra legs, duplicate limb, changed leg, changed body, changed ground, text, watermark, signature"
        ),
    },
    "velociraptor_head_snout": {
        "positive": (
            "preserve everything outside the masked head and snout area exactly, keep the neck, body, forelimbs, legs, feet, tail, feathers, sand, background, and lighting unchanged, "
            "masked area becomes a natural Velociraptor mongoliensis side-profile head with a long narrow dromaeosaur snout, small toothy closed mouth line, "
            "forward-facing alert eye, low reptile-like skull, feathered cheek and crown texture matching the neck, no bird beak"
        ),
        "negative": (
            "parrot beak, eagle beak, duck bill, owl head, chicken head, round bird head, mammal muzzle, human face, oversized eye, open roaring mouth, "
            "giant teeth, crocodile head, changed neck, changed body, changed arms, changed legs, changed feet, extra limb, duplicate head, text, watermark, signature"
        ),
    },
    "velociraptor_second_toe_topology": {
        "positive": (
            "preserve everything outside the tight masked toe areas exactly, keep the same Velociraptor body, long stiff tail, toothed snout, folded feathered forelimbs, leg count, ground, background, and lighting unchanged, "
            "masked areas become anatomically anchored Velociraptor feet: two slim walking toes remain grounded, and the raised second-toe sickle claw is attached to its toe joint near the foot, "
            "small dark curved dromaeosaur sickle claw, modest scale, close to the toe, natural skin texture matching the existing foot, no change to the walking toes or ankle"
        ),
        "negative": (
            "floating claw, detached crescent, giant hook claw, oversized talon, eagle talon, monster claw, black banana-shaped claw, extra claw in the air, "
            "missing foot, changed ankle, elongated walking toes, fused toes, extra toes, extra feet, extra legs, duplicate limb, changed body, changed ground, text, watermark, signature"
        ),
    },
    "velociraptor_less_bird_head": {
        "positive": (
            "preserve everything outside the masked head area exactly, keep the neck, feathered body, folded forelimbs, legs, feet, sickle-claw cues, long stiff tail, sand, background, lighting, and pose unchanged, "
            "masked area becomes a natural Velociraptor mongoliensis dromaeosaur head in side profile, low elongated skull, long narrow toothed snout, closed mouth with a fine row of small teeth, "
            "small dark reptile eye set into the skull, subtle brow ridge, feathered cheek and crown texture matching the neck, no bird beak and no round modern bird eye"
        ),
        "negative": (
            "parrot beak, eagle beak, duck bill, chicken head, owl head, round modern bird head, large yellow bird eye, oversized circular eye, cute bird face, "
            "smooth toothless beak, mammal muzzle, crocodile head, giant teeth, open roaring mouth, changed neck, changed body, changed arms, changed legs, changed feet, "
            "missing sickle claws, extra limb, duplicate head, text, watermark, signature"
        ),
    },
    "natural_desert_background": {
        "positive": (
            "preserve the unmasked dinosaur exactly, keep its full silhouette, feathers, colors, head, arms, legs, feet, claws, and tail unchanged, "
            "replace only the masked background and ground with a natural Late Cretaceous Mongolian desert edge, sandy ground, sparse low scrub, distant soft hills, pale blue sky, "
            "realistic ground contact and soft daylight shadows, museum-quality educational paleoart, no new animal"
        ),
        "negative": (
            "changed dinosaur body, changed feather pattern, changed head, changed tail, changed legs, missing feet, extra limb, duplicate tail, "
            "new dinosaur, second animal, giant movie raptor, scaly naked body, spread wings, bird beak, cropped animal, text, watermark, signature"
        ),
    },
    "coelophysis_dry_ground_background": {
        "positive": (
            "preserve the unmasked Coelophysis exactly, keep its full slender silhouette, long neck, narrow head, small forelimbs, two hind legs, feet, claws, and long tail unchanged, "
            "replace only the masked log, branch, water, reeds, and background with a natural Late Triassic North American dry river plain, sandy silty ground, sparse low scrub, scattered small stones, "
            "feet planted on dry ground with realistic ground contact and soft daylight shadows, museum-quality educational paleoart, no new animal"
        ),
        "negative": (
            "changed dinosaur body, changed head, changed tail, changed legs, missing feet, extra limb, duplicate tail, new dinosaur, second animal, "
            "perched on a log, tree branch perch, fallen log, water, pond, wet reflection, reeds behind body, bird beak, cropped animal, text, watermark, signature"
        ),
    },
    "apatosaurus_floodplain_background": {
        "positive": (
            "preserve the unmasked Apatosaurus exactly, keep the low forward neck, small head, massive quadrupedal body, four pillar legs, full tail, feet, body color, and silhouette unchanged, "
            "replace only the masked sky, flat ground, and background with a natural Late Jurassic Morrison Formation floodplain, dry sandy ground with sparse low plants, distant conifer and fern patches, soft blue sky, "
            "realistic ground contact and soft daylight shadows, museum-quality educational paleoart, no new animal"
        ),
        "negative": (
            "changed dinosaur body, changed neck angle, vertical swan neck, high Brachiosaurus neck, changed tail, missing tail, cropped tail, changed legs, missing feet, extra limb, duplicate tail, "
            "new dinosaur, second animal, two-legged sauropod, front legs taller than hind legs, tail dragging on ground, text, watermark, signature"
        ),
    },
    "apatosaurus_floodplain_rich_background": {
        "positive": (
            "preserve the unmasked Apatosaurus exactly, keep the low forward neck, small head, massive quadrupedal body, four pillar legs, full tail, feet, body color, and silhouette unchanged, "
            "replace only the masked sky, flat studio ground, and empty background with a detailed natural Late Jurassic Morrison Formation floodplain scene, "
            "distant conifer tree line and fern patches across the horizon, sparse cycads, sandy mudflat ground with low plants and small stones, soft blue sky with light clouds, "
            "realistic ground contact and soft daylight shadows, museum-quality educational paleoart, no new animal"
        ),
        "negative": (
            "plain studio background, empty pale gradient, blank sky only, flat beige floor, white floor, seamless product render, changed dinosaur body, changed neck angle, vertical swan neck, "
            "high Brachiosaurus neck, changed tail, missing tail, cropped tail, changed legs, missing feet, extra limb, duplicate tail, new dinosaur, second animal, two-legged sauropod, "
            "front legs taller than hind legs, tail dragging on ground, text, watermark, signature"
        ),
    },
    "allosaurus_closed_jaw": {
        "positive": (
            "preserve everything outside the masked head and jaw area exactly, keep the body, forelimbs, legs, tail, grass, background, lighting, and pose unchanged, "
            "masked area becomes a natural Allosaurus fragilis head and upper neck with a long low theropod skull, low brow ridges, "
            "fully closed jaws, upper and lower jaw touching, only a narrow dark mouth line, no visible mouth gap, teeth hidden by the lips, "
            "skin texture and color matching the existing neck and body, anatomically joined to the neck"
        ),
        "negative": (
            "open mouth, parted jaws, visible mouth gap, wide open roaring mouth, oversized gape, monster jaw, exposed teeth, giant teeth, crocodile head, tyrannosaur deep skull, "
            "horned ceratopsian head, bull horns, detached head, second head, changed body, changed forelimbs, changed legs, text, watermark, signature"
        ),
    },
    "allosaurus_digit_cues": {
        "positive": (
            "preserve everything outside the masked hand and foot areas exactly, keep the Allosaurus body, head, tail, legs, grass, background, lighting, and pose unchanged, "
            "masked forelimb area becomes a natural small Allosaurus fragilis hand with exactly three short clawed fingers, "
            "three slim dinosaur fingers only, curved black claws, wrist stays attached to the existing short forelimb, "
            "masked foot areas keep natural theropod feet partly hidden by dry grass with three forward toes and small claws, "
            "same realistic skin texture and color as the surrounding limb, no new limb"
        ),
        "negative": (
            "extra arm, extra leg, duplicate limb, disconnected hand, hanging strings, long dangling fingers, human hand, five fingers, four fingers, "
            "oversized claws, giant hook claws, bird wing, changed torso, changed belly, changed head, changed tail, changed background, text, watermark, signature"
        ),
    },
    "herrerasaurus_closed_jaw": {
        "positive": (
            "preserve everything outside the masked head and jaw area exactly, keep the body, longer grasping forelimbs, legs, tail, ground, background, lighting, and pose unchanged, "
            "masked area becomes a natural Herrerasaurus ischigualastensis head with a long narrow early-saurischian skull, "
            "calm closed jaws or nearly closed jaws, upper and lower jaw touching with only a thin dark mouth seam, "
            "small sharp teeth mostly hidden, no roaring mouth, no oversized gape, skin texture and color matching the existing neck and body"
        ),
        "negative": (
            "wide open mouth, roaring mouth, monster jaw, giant gape, oversized teeth, crocodile head, tyrannosaur deep skull, "
            "round bulky head, bird beak, horned head, detached head, second head, changed body, changed arms, changed legs, text, watermark, signature"
        ),
    },
    "ankylosaurus_low_armor": {
        "positive": (
            "preserve everything outside the masked dorsal ridge exactly, keep the full body, head, legs, tail, tail club, ground, background, lighting, and pose unchanged, "
            "masked dorsal ridge becomes a continuous low Ankylosaurus back with embedded rounded bony osteoderms and low armor knobs, "
            "remove the tall vertical spikes completely and flatten them into short rounded armor scutes that barely rise above the back line, "
            "natural keratin and bone texture matching the existing skin, smooth low armored silhouette, no changed tail club"
        ),
        "negative": (
            "tall dorsal spikes, sharp vertical back spikes, raised stegosaurus plates, sail, spiky mohawk, porcupine quills, "
            "smooth unarmored back, missing armor, changed tail, missing tail club, detached tail club, duplicate animal, "
            "changed head, changed legs, changed body silhouette, text, watermark, signature"
        ),
    },
    "ankylosaurus_osteoderm_detail": {
        "positive": (
            "preserve everything outside the masked armor band exactly, keep the full body outline, head, legs, tail, tail club, ground, background, lighting, and pose unchanged, "
            "masked band becomes natural Ankylosaurus armor with many low rounded bony osteoderms embedded in the skin, "
            "add rows of broad oval and polygonal armor scutes across the back and upper flank, each scute low and blunt, "
            "the back silhouette stays flat and low, no tall spikes, no stegosaurus plates, natural bone-and-keratin texture matching the skin"
        ),
        "negative": (
            "tall dorsal spikes, sharp vertical back spikes, raised stegosaurus plates, triangular plates, sail, spiky mohawk, porcupine quills, "
            "smooth unarmored back, missing armor, turtle shell, tortoise shell, changed body outline, changed tail, missing tail club, detached tail club, "
            "extra leg, duplicate animal, changed head, changed legs, text, watermark, signature"
        ),
    },
    "ankylosaurus_smooth_tail_club": {
        "positive": (
            "preserve everything outside the masked tail-club area exactly, keep the same body, legs, head, tail shaft, ground, background, lighting, and pose unchanged, "
            "masked area becomes the end of an Ankylosaurus tail with a large solid bony tail club, "
            "the tail shaft connects cleanly into a broad rounded oval club, low blunt armored texture, natural bone-and-keratin surface, "
            "no separate spikes, no porcupine quills, no detached overlay, same color and light direction as the tail"
        ),
        "negative": (
            "spiked mace, many spikes on the club, porcupine quills, detached tail club, floating oval, transparent overlay, flat painted circle, "
            "missing tail club, thin tail only, cropped club, second tail, changed body, changed legs, changed head, text, watermark, signature"
        ),
    },
    "ankylosaurus_broad_blunt_skull": {
        "positive": (
            "preserve everything outside the masked head area exactly, keep the squat low armored Ankylosaurus body, low rounded osteoderm rows, four sturdy feet, thick tail, attached single oval tail club, ground, background, lighting, and pose unchanged, "
            "masked area becomes a compact broad blunt Ankylosaurus magniventris armored skull with a very short snout, low wedge-shaped head, small side eye, closed mouth, and rounded bony cheek armor, "
            "the head is short and wide rather than crocodile-like, armored texture matches the existing neck and body, no horns or tall spikes"
        ),
        "negative": (
            "crocodile head, alligator head, long narrow snout, monitor lizard head, snake head, turtle head, horse head, dog head, mammal face, "
            "horns, horn-like skull projections, ceratopsian frill, tall spikes, open mouth, teeth, monster jaw, changed body, changed tail, missing tail club, changed feet, extra legs, text, watermark, signature"
        ),
    },
    "ankylosaurus_sturdy_toes": {
        "positive": (
            "preserve everything outside the masked foot areas exactly, keep the squat low armored Ankylosaurus body, broad blunt skull, armor rows, thick tail, attached single oval tail club, ground, background, lighting, and pose unchanged, "
            "masked areas become short sturdy Ankylosaurus feet planted on the ground with blunt dinosaur toes and small dark claws, "
            "each visible foot stays broad and low, toes are short and weight-bearing, skin texture and color match the surrounding legs"
        ),
        "negative": (
            "extra leg, missing leg, long bird toes, raptor foot, theropod foot, crocodile foot, hoof, horse hoof, mammal paw, dog paw, human toes, "
            "thin dangling toes, detached claws, floating claws, oversized talons, changed body, changed head, changed armor, changed tail club, text, watermark, signature"
        ),
    },
    "brachiosaurus_shorten_tail_tip": {
        "positive": (
            "preserve everything outside the masked outer tail area exactly, keep the same Brachiosaurus body, high shoulders, taller forelimbs, long rising neck, head, four legs, feet, ground, trees, sky, lighting, and pose unchanged, "
            "masked area becomes natural background and the shorter natural tapering end of the same Brachiosaurus tail, "
            "tail ends earlier inside the masked area, thick at the base and tapering gently, no long whip-like tail continuation"
        ),
        "negative": (
            "long whip tail, extremely long thin tail, tail continues to the right edge, missing whole tail, detached tail tip, second tail, duplicate tail, "
            "changed body, changed legs, changed neck, changed head, hidden feet, extra legs, text, watermark, signature"
        ),
    },
}


def configure(
    workflow,
    taxon_id,
    source_image,
    mask_image,
    seed,
    denoise,
    prefix,
    ckpt_name,
    edit_mode,
    lora_name=None,
    lora_strength=None,
    clip_strength=None,
):
    prompt = build_prompt(taxon_id)
    edit_prompt = EDIT_PROMPTS[edit_mode]
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    if lora_name:
        workflow["10"]["inputs"]["lora_name"] = lora_name
        workflow["10"]["inputs"]["strength_model"] = lora_strength
        workflow["10"]["inputs"]["strength_clip"] = clip_strength
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["denoise"] = denoise
    workflow["6"]["inputs"]["text"] = (
        prompt["positivePrompt"]
        + ", "
        + edit_prompt["positive"]
    )
    workflow["7"]["inputs"]["text"] = (
        prompt["negativePrompt"]
        + ", "
        + edit_prompt["negative"]
        + ", text, watermark, signature"
    )
    strength_suffix = f"_s{int(lora_strength * 100):02d}" if lora_name else ""
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}_{taxon_id}{strength_suffix}_d{int(denoise * 100):02d}"
    workflow["12"]["inputs"]["image"] = input_name(source_image)
    workflow["13"]["inputs"]["image"] = input_name(mask_image)
    return workflow


def make_contact_sheet(paths, output, thumb_w=384, thumb_h=256):
    tiles = []
    for path, label in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + 42), (245, 243, 236))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 10), label[:58], fill=(31, 31, 28), font=ImageFont.load_default())
        tiles.append(tile)
    cols = min(2, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 42)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + 42)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", default="velociraptor-mongoliensis")
    parser.add_argument("--source-image", required=True)
    parser.add_argument("--mask-preset", action="append", choices=sorted(MASK_PRESETS), default=[])
    parser.add_argument("--mask-image", help="Optional explicit mask image. White is edited, black is preserved.")
    parser.add_argument("--seed", type=int, action="append", default=[])
    parser.add_argument("--denoise", type=float, action="append", default=[])
    parser.add_argument("--feather", type=float, default=4.0)
    parser.add_argument("--ckpt-name", default="RealVisXL_V5.0_fp16.safetensors")
    parser.add_argument("--prefix", default="inpaint")
    parser.add_argument("--edit-mode", choices=sorted(EDIT_PROMPTS), default="cleanup")
    parser.add_argument("--lora-name")
    parser.add_argument("--lora-strength", type=float)
    parser.add_argument("--clip-strength", type=float)
    args = parser.parse_args()

    source = Path(args.source_image)
    if not source.is_absolute():
        source = (Path.cwd() / source).resolve()
    custom_mask = None
    if args.mask_image:
        custom_mask = Path(args.mask_image)
        if not custom_mask.is_absolute():
            custom_mask = (Path.cwd() / custom_mask).resolve()

    input_dir = COMFY_INPUT / "dino_inpaint"
    input_dir.mkdir(parents=True, exist_ok=True)
    input_source = input_dir / f"{args.prefix}_source.png"
    shutil.copy2(source, input_source)

    seeds = args.seed or [2026067201, 2026067202]
    denoises = args.denoise or [0.34, 0.46, 0.58]
    presets = args.mask_preset or (["custom"] if custom_mask else ["tail_thread"])
    template = LORA_TEMPLATE if args.lora_name else TEMPLATE
    lora_strength = args.lora_strength if args.lora_strength is not None else 0.16
    clip_strength = args.clip_strength if args.clip_strength is not None else min(lora_strength, 0.1)

    results = []
    copied = []
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)

    for preset in presets:
        mask_image = input_dir / f"{args.prefix}_{preset}_mask.png"
        if preset == "custom":
            if not custom_mask:
                raise ValueError("--mask-image is required when using the custom mask preset")
            shutil.copy2(custom_mask, mask_image)
        else:
            make_mask(input_source, mask_image, preset, args.feather)
        shutil.copy2(mask_image, EXPERIMENT_OUT / f"{args.prefix}_{preset}_mask.png")
        for denoise in denoises:
            for seed in seeds:
                workflow = configure(
                    load_workflow(template),
                    args.taxon_id,
                    input_source,
                    mask_image,
                    seed,
                    denoise,
                    f"{args.prefix}_{preset}",
                    args.ckpt_name,
                    args.edit_mode,
                    args.lora_name,
                    lora_strength,
                    clip_strength,
                )
                queued = queue_prompt(workflow, client_id="dino-atlas-inpaint")
                history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                for image in output_images_from_history(history):
                    item = {
                        "taxonId": args.taxon_id,
                        "sourceImage": str(source),
                        "maskPreset": preset,
                        "seed": seed,
                        "denoise": denoise,
                        "lora": args.lora_name,
                        "loraStrength": lora_strength if args.lora_name else None,
                        "clipStrength": clip_strength if args.lora_name else None,
                        "image": str(image),
                    }
                    results.append(item)
                    strength_suffix = f"_s{int(lora_strength * 100):02d}" if args.lora_name else ""
                    dst = EXPERIMENT_OUT / (
                        f"{args.prefix}_{preset}_{args.taxon_id}_seed{seed}{strength_suffix}_d{int(denoise * 100):02d}.png"
                    )
                    shutil.copy2(image, dst)
                    copied.append((dst, f"{preset} seed {seed} d{denoise:.2f}"))

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
