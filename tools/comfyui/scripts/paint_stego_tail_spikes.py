import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def scale_points(points, scale):
    return [(int(x * scale), int(y * scale)) for x, y in points]


def draw_spike(draw, mask_draw, points, fill, outline, scale):
    scaled = scale_points(points, scale)
    draw.polygon(scaled, fill=fill)
    draw.line(scaled + [scaled[0]], fill=outline, width=max(2, int(2.5 * scale)), joint="curve")
    mask_draw.polygon(scaled, fill=255)


def add_texture(overlay, mask, seed, scale):
    rng = random.Random(seed)
    texture = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    w, h = overlay.size
    for _ in range(900):
        x = rng.randrange(0, min(w, int(165 * scale)))
        y = rng.randrange(int(365 * scale), int(555 * scale))
        if mask.getpixel((x, y)) < 16:
            continue
        alpha = rng.randrange(10, 34)
        tone = rng.choice([(38, 31, 24), (142, 122, 82), (82, 66, 45)])
        r = rng.randrange(1, max(2, int(2.5 * scale)))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*tone, alpha))
    texture.putalpha(Image.composite(texture.getchannel("A"), Image.new("L", overlay.size, 0), mask))
    return Image.alpha_composite(overlay, texture)


def make_variant(source, output, variant):
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC).convert("RGBA")
    overlay = Image.new("RGBA", large.size, (0, 0, 0, 0))
    mask = Image.new("L", large.size, 0)
    draw = ImageDraw.Draw(overlay)
    mask_draw = ImageDraw.Draw(mask)

    # The tail points left. Keep all four spikes inside the frame and attach them to the same tail tip.
    variants = {
        "v4a": [
            [(46, 449), (78, 456), (24, 383)],
            [(74, 459), (105, 468), (132, 403)],
            [(43, 478), (78, 488), (9, 534)],
            [(76, 487), (109, 496), (130, 548)],
        ],
        "v4b": [
            [(50, 446), (84, 456), (13, 395)],
            [(80, 454), (111, 466), (118, 385)],
            [(48, 479), (82, 489), (22, 544)],
            [(82, 488), (112, 498), (146, 530)],
        ],
        "v4c": [
            [(42, 450), (76, 457), (4, 414)],
            [(72, 455), (105, 466), (139, 416)],
            [(43, 478), (75, 487), (4, 512)],
            [(75, 486), (106, 497), (137, 548)],
        ],
        "v5a": [
            [(31, 454), (56, 462), (7, 401)],
            [(58, 459), (82, 467), (101, 409)],
            [(31, 476), (57, 485), (6, 528)],
            [(60, 482), (86, 491), (112, 530)],
        ],
        "v5b": [
            [(24, 455), (51, 462), (5, 416)],
            [(54, 458), (79, 465), (88, 396)],
            [(25, 475), (55, 485), (6, 514)],
            [(56, 481), (83, 491), (102, 540)],
        ],
        "v5c": [
            [(36, 452), (62, 459), (14, 389)],
            [(62, 458), (88, 465), (117, 418)],
            [(35, 477), (62, 486), (14, 546)],
            [(64, 482), (90, 491), (124, 520)],
        ],
    }
    fills = [
        (111, 88, 58, 246),
        (121, 98, 64, 244),
        (96, 75, 49, 248),
        (104, 82, 54, 246),
    ]
    outlines = [
        (48, 37, 25, 230),
        (53, 41, 27, 225),
        (42, 32, 22, 235),
        (48, 37, 25, 230),
    ]

    # A small opaque attachment pad makes the spikes look grown from the tail rather than pasted on.
    if variant.startswith("v5"):
        attachment = [(20, 452), (91, 455), (100, 477), (83, 498), (20, 488), (6, 470)]
        attachment_alpha = 238
    else:
        attachment = [(32, 449), (95, 445), (121, 477), (100, 506), (35, 496), (13, 472)]
        attachment_alpha = 222
    draw.polygon(scale_points(attachment, scale), fill=(92, 70, 46, attachment_alpha))
    mask_draw.polygon(scale_points(attachment, scale), fill=210)

    for index, points in enumerate(variants[variant]):
        draw_spike(draw, mask_draw, points, fills[index], outlines[index], scale)

    # Directional highlights and basal shadows tie the shape into the existing tail lighting.
    highlight = Image.new("RGBA", large.size, (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(highlight)
    for points in variants[variant]:
        p0, p1, p2 = points
        mid_base = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        hdraw.line(
            scale_points([(mid_base[0] + 3, mid_base[1] - 3), (p2[0] + 4, p2[1] + 5)], scale),
            fill=(190, 162, 105, 72),
            width=max(1, int(2.1 * scale)),
        )
    shadow = Image.new("RGBA", large.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse(scale_points([(16, 480), (126, 523)], scale), fill=(32, 24, 18, 64))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=3.2 * scale))

    overlay = Image.alpha_composite(shadow, overlay)
    overlay = Image.alpha_composite(overlay, highlight)
    overlay = add_texture(overlay, mask, seed=sum(ord(c) for c in variant), scale=scale)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=0.22 * scale))

    combined = Image.alpha_composite(large, overlay)
    result = combined.resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def average_color(image, box):
    crop = image.crop(box).resize((1, 1), Image.Resampling.BICUBIC)
    return crop.getpixel((0, 0))


def draw_soft_spike(layer, mask, base_a, base_b, tip, fill, shadow_side=1):
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)
    poly = [base_a, base_b, tip]
    draw.polygon(poly, fill=fill)
    mask_draw.polygon(poly, fill=255)

    highlight = (
        (base_a[0] * 0.55 + base_b[0] * 0.45, base_a[1] * 0.55 + base_b[1] * 0.45),
        (tip[0] * 0.82 + base_a[0] * 0.18, tip[1] * 0.82 + base_a[1] * 0.18),
    )
    shadow = (
        (base_a[0] * 0.45 + base_b[0] * 0.55, base_a[1] * 0.45 + base_b[1] * 0.55),
        (tip[0] * 0.76 + base_b[0] * 0.24, tip[1] * 0.76 + base_b[1] * 0.24),
    )
    draw.line(highlight, fill=(192, 164, 112, 70), width=5)
    draw.line(shadow, fill=(43, 32, 22, 95), width=5 + shadow_side)


def make_margin_variant(source, output, variant):
    base = Image.open(source).convert("RGB")
    w, h = base.size

    # Use the source itself as a soft background extension so the shifted animal does not
    # reveal hard blank margins. This gives the thagomizer room inside the frame.
    bg = base.resize((int(w * 1.12), int(h * 1.12)), Image.Resampling.BICUBIC)
    bg = bg.crop(((bg.width - w) // 2, (bg.height - h) // 2, (bg.width + w) // 2, (bg.height + h) // 2))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=9))

    scale = 0.9 if variant != "v6c" else 0.92
    shifted = base.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS).convert("RGBA")
    xoff = 78 if variant != "v6c" else 58
    yoff = int((h - shifted.height) * 0.55)

    canvas = bg.convert("RGBA")
    canvas.alpha_composite(shifted, (xoff, yoff))

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    # New tail-tip area after the source image is scaled and shifted.
    anchor_x = xoff + int(23 * scale)
    anchor_y = yoff + int(462 * scale)
    tail_color = average_color(canvas.convert("RGB"), (anchor_x + 38, anchor_y - 18, anchor_x + 92, anchor_y + 22))
    base_color = (max(48, tail_color[0] - 16), max(38, tail_color[1] - 18), max(26, tail_color[2] - 18), 236)
    spike_color = (max(64, tail_color[0] + 8), max(52, tail_color[1] + 2), max(36, tail_color[2] - 4), 246)

    pad = [
        (anchor_x - 6, anchor_y - 14),
        (anchor_x + 56, anchor_y - 8),
        (anchor_x + 65, anchor_y + 13),
        (anchor_x + 39, anchor_y + 28),
        (anchor_x - 8, anchor_y + 16),
        (anchor_x - 20, anchor_y + 1),
    ]
    draw.polygon(pad, fill=base_color)
    mask_draw.polygon(pad, fill=230)

    if variant == "v6a":
        spikes = [
            ((anchor_x + 3, anchor_y - 9), (anchor_x + 21, anchor_y - 3), (anchor_x - 48, anchor_y - 64)),
            ((anchor_x + 25, anchor_y - 8), (anchor_x + 43, anchor_y - 1), (anchor_x + 9, anchor_y - 72)),
            ((anchor_x + 0, anchor_y + 9), (anchor_x + 20, anchor_y + 17), (anchor_x - 61, anchor_y + 44)),
            ((anchor_x + 24, anchor_y + 13), (anchor_x + 44, anchor_y + 20), (anchor_x + 4, anchor_y + 72)),
        ]
    elif variant == "v6b":
        spikes = [
            ((anchor_x + 2, anchor_y - 9), (anchor_x + 20, anchor_y - 2), (anchor_x - 58, anchor_y - 48)),
            ((anchor_x + 24, anchor_y - 9), (anchor_x + 42, anchor_y - 2), (anchor_x + 20, anchor_y - 78)),
            ((anchor_x - 1, anchor_y + 8), (anchor_x + 19, anchor_y + 17), (anchor_x - 55, anchor_y + 55)),
            ((anchor_x + 23, anchor_y + 12), (anchor_x + 42, anchor_y + 20), (anchor_x + 34, anchor_y + 80)),
        ]
    else:
        spikes = [
            ((anchor_x + 6, anchor_y - 8), (anchor_x + 24, anchor_y - 2), (anchor_x - 39, anchor_y - 62)),
            ((anchor_x + 29, anchor_y - 7), (anchor_x + 47, anchor_y), (anchor_x + 1, anchor_y - 73)),
            ((anchor_x + 5, anchor_y + 10), (anchor_x + 25, anchor_y + 17), (anchor_x - 44, anchor_y + 49)),
            ((anchor_x + 29, anchor_y + 13), (anchor_x + 49, anchor_y + 20), (anchor_x + 10, anchor_y + 66)),
        ]

    for idx, (base_a, base_b, tip) in enumerate(spikes):
        tint = (
            min(180, spike_color[0] + idx * 4),
            min(150, spike_color[1] + idx * 3),
            min(105, spike_color[2] + idx * 2),
            spike_color[3],
        )
        draw_soft_spike(layer, mask, base_a, base_b, tip, tint, shadow_side=idx % 2)

    rng = random.Random(sum(ord(c) for c in variant) + 600)
    tex = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tex)
    for _ in range(520):
        x = rng.randrange(max(0, anchor_x - 72), min(canvas.width, anchor_x + 74))
        y = rng.randrange(max(0, anchor_y - 84), min(canvas.height, anchor_y + 92))
        if mask.getpixel((x, y)) < 16:
            continue
        tone = rng.choice([(48, 38, 28), (137, 112, 74), (96, 75, 48), (188, 160, 106)])
        alpha = rng.randrange(10, 28)
        tdraw.point((x, y), fill=(*tone, alpha))
    tex.putalpha(ImageChops.multiply(tex.getchannel("A"), mask))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse((anchor_x - 64, anchor_y + 34, anchor_x + 86, anchor_y + 70), fill=(34, 27, 20, 56))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))

    layer = Image.alpha_composite(shadow, layer)
    layer = Image.alpha_composite(layer, tex)
    edge_mask = mask.filter(ImageFilter.GaussianBlur(radius=0.55))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge_mask))
    result = Image.alpha_composite(canvas, layer).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def make_in_frame_soft_variant(source, output, variant):
    base = Image.open(source).convert("RGB")
    canvas = base.convert("RGBA")
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    anchor_x, anchor_y = 52, 467
    tail_color = average_color(base, (75, 438, 155, 488))
    pad_color = (max(52, tail_color[0] - 12), max(42, tail_color[1] - 14), max(30, tail_color[2] - 16), 210)
    spike_color = (max(76, tail_color[0] + 5), max(58, tail_color[1] - 2), max(40, tail_color[2] - 8), 220)

    pad = [
        (anchor_x - 26, anchor_y - 14),
        (anchor_x + 44, anchor_y - 8),
        (anchor_x + 62, anchor_y + 9),
        (anchor_x + 35, anchor_y + 27),
        (anchor_x - 28, anchor_y + 17),
        (anchor_x - 42, anchor_y + 1),
    ]
    draw.polygon(pad, fill=pad_color)
    mask_draw.polygon(pad, fill=190)

    if variant == "v7a":
        spikes = [
            ((31, 454), (49, 462), (7, 411)),
            ((54, 456), (72, 464), (91, 405)),
            ((29, 475), (49, 483), (7, 512)),
            ((55, 477), (75, 486), (99, 526)),
        ]
    elif variant == "v7b":
        spikes = [
            ((35, 454), (53, 462), (12, 421)),
            ((58, 456), (76, 464), (86, 413)),
            ((34, 476), (53, 483), (13, 503)),
            ((59, 478), (78, 486), (93, 519)),
        ]
    else:
        spikes = [
            ((30, 452), (49, 461), (6, 430)),
            ((55, 456), (73, 464), (104, 422)),
            ((29, 476), (49, 484), (4, 500)),
            ((55, 479), (76, 487), (110, 510)),
        ]

    for idx, (base_a, base_b, tip) in enumerate(spikes):
        fill = (
            min(168, spike_color[0] + idx * 4),
            min(138, spike_color[1] + idx * 3),
            min(96, spike_color[2] + idx * 2),
            spike_color[3],
        )
        draw_soft_spike(layer, mask, base_a, base_b, tip, fill, shadow_side=idx % 2)

    rng = random.Random(sum(ord(c) for c in variant) + 700)
    tex = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tex)
    for _ in range(430):
        x = rng.randrange(0, 125)
        y = rng.randrange(392, 548)
        if mask.getpixel((x, y)) < 16:
            continue
        tone = rng.choice([(55, 42, 30), (132, 108, 72), (88, 68, 44), (184, 152, 98)])
        tdraw.point((x, y), fill=(*tone, rng.randrange(8, 24)))
    tex.putalpha(ImageChops.multiply(tex.getchannel("A"), mask))

    layer = Image.alpha_composite(layer, tex)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.42))
    edge_mask = mask.filter(ImageFilter.GaussianBlur(radius=0.7))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge_mask))
    result = Image.alpha_composite(canvas, layer).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def make_low_profile_natural_variant(source, output, variant):
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC)
    canvas = large.convert("RGBA")
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    def p(point):
        return (int(point[0] * scale), int(point[1] * scale))

    def poly(points):
        return [p(point) for point in points]

    anchor_x, anchor_y = 58, 468
    tail_color = average_color(base, (72, 446, 155, 486))
    dark_tail = (
        max(46, int(tail_color[0] * 0.62)),
        max(36, int(tail_color[1] * 0.58)),
        max(26, int(tail_color[2] * 0.52)),
        214,
    )
    spike_base = (
        min(158, int(tail_color[0] * 0.82 + 34)),
        min(130, int(tail_color[1] * 0.78 + 22)),
        min(92, int(tail_color[2] * 0.70 + 14)),
        224,
    )
    shadow_color = (28, 22, 17, 80)

    if variant == "v10a":
        pad = [(16, 454), (82, 449), (111, 466), (94, 491), (23, 489), (1, 470)]
        spikes = [
            [(25, 456), (44, 461), (4, 415)],
            [(50, 453), (70, 458), (78, 402)],
            [(23, 475), (45, 481), (3, 512)],
            [(51, 476), (73, 482), (92, 526)],
        ]
    elif variant == "v10b":
        pad = [(20, 456), (87, 451), (110, 468), (91, 489), (24, 487), (5, 470)]
        spikes = [
            [(28, 457), (47, 462), (5, 427)],
            [(52, 454), (72, 459), (88, 410)],
            [(27, 474), (48, 480), (7, 503)],
            [(53, 476), (75, 482), (100, 515)],
        ]
    else:
        pad = [(18, 456), (82, 451), (105, 466), (91, 487), (25, 489), (2, 472)]
        spikes = [
            [(25, 457), (43, 462), (0, 433)],
            [(49, 454), (69, 459), (70, 414)],
            [(24, 475), (44, 481), (0, 499)],
            [(51, 477), (72, 483), (86, 518)],
        ]

    # Soft basal pad first, with no hard outline. It tucks the spikes into the tail tip.
    draw.polygon(poly(pad), fill=dark_tail)
    mask_draw.polygon(poly(pad), fill=210)

    for idx, points in enumerate(spikes):
        tint = (
            max(55, min(170, spike_base[0] + idx * 3 - 8)),
            max(45, min(138, spike_base[1] + idx * 2 - 8)),
            max(32, min(98, spike_base[2] + idx * 2 - 6)),
            max(0, spike_base[3] - idx * 4),
        )
        draw.polygon(poly(points), fill=tint)
        mask_draw.polygon(poly(points), fill=232)
        base_a, base_b, tip = points
        highlight = [
            ((base_a[0] * 0.62 + base_b[0] * 0.38), (base_a[1] * 0.62 + base_b[1] * 0.38)),
            ((tip[0] * 0.82 + base_a[0] * 0.18), (tip[1] * 0.82 + base_a[1] * 0.18)),
        ]
        shade = [
            ((base_a[0] * 0.38 + base_b[0] * 0.62), (base_a[1] * 0.38 + base_b[1] * 0.62)),
            ((tip[0] * 0.76 + base_b[0] * 0.24), (tip[1] * 0.76 + base_b[1] * 0.24)),
        ]
        draw.line([p(point) for point in highlight], fill=(197, 165, 110, 48), width=max(2, int(1.5 * scale)))
        draw.line([p(point) for point in shade], fill=(34, 27, 20, 64), width=max(2, int(1.7 * scale)))

    # A very soft contact shadow under the low spikes reduces the pasted look.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse(poly([(3, 486), (111, 529)]), fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=4.8 * scale))
    layer = Image.alpha_composite(shadow, layer)

    rng = random.Random(sum(ord(char) for char in variant) + 1000)
    tex = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tex)
    for _ in range(900):
        x = rng.randrange(0, int(118 * scale))
        y = rng.randrange(int(390 * scale), int(538 * scale))
        if mask.getpixel((x, y)) < 18:
            continue
        tone = rng.choice([(56, 43, 30), (112, 88, 58), (155, 128, 84), (72, 56, 38)])
        alpha = rng.randrange(5, 22)
        tdraw.point((x, y), fill=(*tone, alpha))
    tex.putalpha(ImageChops.multiply(tex.getchannel("A"), mask))
    layer = Image.alpha_composite(layer, tex)

    # Blur the overlay slightly and multiply by a soft mask to avoid vector-sharp edges.
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.28 * scale))
    edge_mask = mask.filter(ImageFilter.GaussianBlur(radius=0.72 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge_mask))

    result = Image.alpha_composite(canvas, layer)
    result = result.resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def make_mid_profile_natural_variant(source, output, variant):
    base = Image.open(source).convert("RGB")
    scale = 4
    large = base.resize((base.width * scale, base.height * scale), Image.Resampling.BICUBIC)
    canvas = large.convert("RGBA")
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(layer)
    mask_draw = ImageDraw.Draw(mask)

    def p(point):
        return (int(point[0] * scale), int(point[1] * scale))

    def poly(points):
        return [p(point) for point in points]

    tail_color = average_color(base, (70, 442, 150, 486))
    base_pad = (
        max(45, int(tail_color[0] * 0.66)),
        max(35, int(tail_color[1] * 0.62)),
        max(25, int(tail_color[2] * 0.56)),
        226,
    )
    spike_fill = (
        min(166, int(tail_color[0] * 0.86 + 34)),
        min(136, int(tail_color[1] * 0.80 + 24)),
        min(98, int(tail_color[2] * 0.72 + 18)),
        232,
    )

    if variant == "v11a":
        pad = [(16, 452), (86, 447), (113, 466), (96, 494), (20, 492), (0, 471)]
        spikes = [
            [(25, 455), (47, 461), (0, 407)],
            [(53, 452), (75, 458), (93, 394)],
            [(23, 476), (47, 483), (0, 518)],
            [(54, 477), (77, 484), (104, 536)],
        ]
    elif variant == "v11b":
        pad = [(19, 454), (88, 449), (112, 467), (94, 492), (22, 491), (2, 471)]
        spikes = [
            [(28, 456), (49, 462), (2, 417)],
            [(54, 453), (76, 459), (84, 397)],
            [(26, 475), (48, 482), (2, 509)],
            [(55, 477), (77, 484), (97, 528)],
        ]
    else:
        pad = [(15, 454), (83, 450), (110, 466), (96, 490), (20, 492), (0, 473)]
        spikes = [
            [(24, 456), (45, 462), (0, 423)],
            [(50, 453), (73, 459), (72, 401)],
            [(23, 476), (45, 483), (0, 503)],
            [(51, 478), (75, 484), (86, 526)],
        ]

    draw.polygon(poly(pad), fill=base_pad)
    mask_draw.polygon(poly(pad), fill=222)

    for idx, points in enumerate(spikes):
        tint = (
            max(50, min(176, spike_fill[0] + idx * 4 - 5)),
            max(42, min(144, spike_fill[1] + idx * 3 - 6)),
            max(30, min(104, spike_fill[2] + idx * 2 - 6)),
            spike_fill[3] - idx * 3,
        )
        draw.polygon(poly(points), fill=tint)
        mask_draw.polygon(poly(points), fill=245)
        base_a, base_b, tip = points
        ridge = [
            ((base_a[0] * 0.6 + base_b[0] * 0.4), (base_a[1] * 0.6 + base_b[1] * 0.4)),
            ((tip[0] * 0.84 + base_a[0] * 0.16), (tip[1] * 0.84 + base_a[1] * 0.16)),
        ]
        lower = [
            ((base_a[0] * 0.35 + base_b[0] * 0.65), (base_a[1] * 0.35 + base_b[1] * 0.65)),
            ((tip[0] * 0.74 + base_b[0] * 0.26), (tip[1] * 0.74 + base_b[1] * 0.26)),
        ]
        draw.line([p(point) for point in ridge], fill=(202, 169, 112, 58), width=max(2, int(1.7 * scale)))
        draw.line([p(point) for point in lower], fill=(33, 26, 20, 76), width=max(2, int(1.9 * scale)))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse(poly([(0, 486), (126, 536)]), fill=(28, 22, 17, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5.4 * scale))
    layer = Image.alpha_composite(shadow, layer)

    rng = random.Random(sum(ord(char) for char in variant) + 1100)
    tex = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tex)
    for _ in range(1200):
        x = rng.randrange(0, int(128 * scale))
        y = rng.randrange(int(388 * scale), int(548 * scale))
        if mask.getpixel((x, y)) < 18:
            continue
        tone = rng.choice([(50, 39, 29), (118, 92, 60), (156, 128, 84), (82, 63, 41)])
        alpha = rng.randrange(5, 24)
        if rng.random() < 0.18:
            radius = rng.randrange(1, 3)
            tdraw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*tone, alpha))
        else:
            tdraw.point((x, y), fill=(*tone, alpha))
    tex.putalpha(ImageChops.multiply(tex.getchannel("A"), mask))
    layer = Image.alpha_composite(layer, tex)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.22 * scale))
    edge_mask = mask.filter(ImageFilter.GaussianBlur(radius=0.58 * scale))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge_mask))

    result = Image.alpha_composite(canvas, layer)
    result = result.resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def make_reframed_thagomizer_variant(source, output, variant):
    import cv2
    import numpy as np

    base = Image.open(source).convert("RGB")
    w, h = base.size

    # Remove the original animal from the background, then paste a slightly
    # smaller copy back in with room for the thagomizer inside the frame.
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(
        [
            (0, 408), (82, 384), (250, 315), (392, 168), (700, 160),
            (815, 315), (1000, 335), (1145, 360), (1152, 528),
            (980, 565), (780, 540), (635, 610), (475, 640), (310, 570),
            (145, 532), (0, 520),
        ],
        fill=255,
    )
    draw.rectangle((250, 510, 820, 646), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=6))
    cv_base = cv2.cvtColor(np.array(base), cv2.COLOR_RGB2BGR)
    cv_mask = np.array(mask.point(lambda p: 255 if p > 16 else 0))
    bg = cv2.inpaint(cv_base, cv_mask, 13, cv2.INPAINT_TELEA)
    canvas = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert("RGBA")

    if variant == "v12a":
        scale, xoff, yoff = 0.93, 58, 20
        anchor_dx = 0
    elif variant == "v12b":
        scale, xoff, yoff = 0.92, 70, 24
        anchor_dx = -4
    else:
        scale, xoff, yoff = 0.94, 48, 18
        anchor_dx = 3

    subject = base.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS).convert("RGBA")
    subject_mask = mask.resize(subject.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=1.2))
    subject.putalpha(subject_mask)
    canvas.alpha_composite(subject, (xoff, yoff))

    scale4 = 4
    large = canvas.resize((w * scale4, h * scale4), Image.Resampling.BICUBIC)
    layer = Image.new("RGBA", large.size, (0, 0, 0, 0))
    spike_mask = Image.new("L", large.size, 0)
    ldraw = ImageDraw.Draw(layer)
    mdraw = ImageDraw.Draw(spike_mask)

    def p(point):
        return (int(point[0] * scale4), int(point[1] * scale4))

    def poly(points):
        return [p(point) for point in points]

    anchor_x = int(xoff + 58 * scale) + anchor_dx
    anchor_y = int(yoff + 468 * scale)
    tail_color = average_color(large.convert("RGB"), (
        int((anchor_x + 20) * scale4), int((anchor_y - 14) * scale4),
        int((anchor_x + 92) * scale4), int((anchor_y + 20) * scale4),
    ))
    base_pad = (
        max(42, int(tail_color[0] * 0.64)),
        max(32, int(tail_color[1] * 0.58)),
        max(24, int(tail_color[2] * 0.52)),
        230,
    )
    spike_fill = (
        min(164, int(tail_color[0] * 0.82 + 32)),
        min(134, int(tail_color[1] * 0.78 + 22)),
        min(96, int(tail_color[2] * 0.72 + 16)),
        238,
    )

    pad = [
        (anchor_x - 32, anchor_y - 13),
        (anchor_x + 48, anchor_y - 9),
        (anchor_x + 72, anchor_y + 10),
        (anchor_x + 45, anchor_y + 30),
        (anchor_x - 34, anchor_y + 19),
        (anchor_x - 50, anchor_y + 1),
    ]
    if variant == "v12b":
        spikes = [
            [(anchor_x - 24, anchor_y - 8), (anchor_x - 2, anchor_y - 2), (anchor_x - 76, anchor_y - 56)],
            [(anchor_x + 7, anchor_y - 8), (anchor_x + 30, anchor_y - 1), (anchor_x + 3, anchor_y - 74)],
            [(anchor_x - 25, anchor_y + 10), (anchor_x - 2, anchor_y + 18), (anchor_x - 82, anchor_y + 47)],
            [(anchor_x + 6, anchor_y + 12), (anchor_x + 30, anchor_y + 20), (anchor_x + 18, anchor_y + 72)],
        ]
    else:
        spikes = [
            [(anchor_x - 22, anchor_y - 8), (anchor_x + 1, anchor_y - 2), (anchor_x - 68, anchor_y - 48)],
            [(anchor_x + 9, anchor_y - 8), (anchor_x + 32, anchor_y - 1), (anchor_x + 12, anchor_y - 66)],
            [(anchor_x - 23, anchor_y + 10), (anchor_x + 1, anchor_y + 18), (anchor_x - 72, anchor_y + 40)],
            [(anchor_x + 8, anchor_y + 12), (anchor_x + 32, anchor_y + 20), (anchor_x + 24, anchor_y + 62)],
        ]

    ldraw.polygon(poly(pad), fill=base_pad)
    mdraw.polygon(poly(pad), fill=220)
    for idx, points in enumerate(spikes):
        fill = (
            max(48, min(174, spike_fill[0] + idx * 4 - 5)),
            max(40, min(142, spike_fill[1] + idx * 3 - 5)),
            max(28, min(102, spike_fill[2] + idx * 2 - 5)),
            spike_fill[3] - idx * 4,
        )
        ldraw.polygon(poly(points), fill=fill)
        mdraw.polygon(poly(points), fill=245)
        base_a, base_b, tip = points
        ridge = [
            (base_a[0] * 0.58 + base_b[0] * 0.42, base_a[1] * 0.58 + base_b[1] * 0.42),
            (tip[0] * 0.84 + base_a[0] * 0.16, tip[1] * 0.84 + base_a[1] * 0.16),
        ]
        shade = [
            (base_a[0] * 0.35 + base_b[0] * 0.65, base_a[1] * 0.35 + base_b[1] * 0.65),
            (tip[0] * 0.72 + base_b[0] * 0.28, tip[1] * 0.72 + base_b[1] * 0.28),
        ]
        ldraw.line([p(point) for point in ridge], fill=(202, 169, 112, 54), width=7)
        ldraw.line([p(point) for point in shade], fill=(31, 24, 18, 74), width=8)

    rng = random.Random(sum(ord(char) for char in variant) + 1200)
    tex = Image.new("RGBA", large.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tex)
    for _ in range(1600):
        x = rng.randrange(max(0, int((anchor_x - 92) * scale4)), min(large.width, int((anchor_x + 98) * scale4)))
        y = rng.randrange(max(0, int((anchor_y - 88) * scale4)), min(large.height, int((anchor_y + 92) * scale4)))
        if spike_mask.getpixel((x, y)) < 18:
            continue
        tone = rng.choice([(48, 38, 28), (118, 92, 60), (156, 128, 84), (82, 63, 41), (190, 158, 104)])
        alpha = rng.randrange(4, 22)
        if rng.random() < 0.14:
            r = rng.randrange(1, 3)
            tdraw.ellipse((x - r, y - r, x + r, y + r), fill=(*tone, alpha))
        else:
            tdraw.point((x, y), fill=(*tone, alpha))
    tex.putalpha(ImageChops.multiply(tex.getchannel("A"), spike_mask))
    layer = Image.alpha_composite(layer, tex)

    contact_shadow = Image.new("RGBA", large.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(contact_shadow)
    sdraw.ellipse(poly([(anchor_x - 86, anchor_y + 32), (anchor_x + 84, anchor_y + 70)]), fill=(28, 22, 17, 52))
    contact_shadow = contact_shadow.filter(ImageFilter.GaussianBlur(radius=17))
    layer = Image.alpha_composite(contact_shadow, layer)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.85))
    edge = spike_mask.filter(ImageFilter.GaussianBlur(radius=3.2))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), edge))
    result = Image.alpha_composite(large, layer).resize(base.size, Image.Resampling.LANCZOS).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--out-dir", default="tools/comfyui/outputs")
    parser.add_argument("--prefix", default="stego_tailspike_local_v4")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    source = Path(args.source)
    for variant in ("v4a", "v4b", "v4c", "v5a", "v5b", "v5c"):
        make_variant(source, out_dir / f"{args.prefix}_{variant}.png", variant)
        print(out_dir / f"{args.prefix}_{variant}.png")
    for variant in ("v6a", "v6b", "v6c"):
        make_margin_variant(source, out_dir / f"{args.prefix}_{variant}.png", variant)
        print(out_dir / f"{args.prefix}_{variant}.png")
    for variant in ("v7a", "v7b", "v7c"):
        make_in_frame_soft_variant(source, out_dir / f"{args.prefix}_{variant}.png", variant)
        print(out_dir / f"{args.prefix}_{variant}.png")
    for variant in ("v10a", "v10b", "v10c"):
        make_low_profile_natural_variant(source, out_dir / f"{args.prefix}_{variant}.png", variant)
        print(out_dir / f"{args.prefix}_{variant}.png")
    for variant in ("v11a", "v11b", "v11c"):
        make_mid_profile_natural_variant(source, out_dir / f"{args.prefix}_{variant}.png", variant)
        print(out_dir / f"{args.prefix}_{variant}.png")
    for variant in ("v12a", "v12b", "v12c"):
        make_reframed_thagomizer_variant(source, out_dir / f"{args.prefix}_{variant}.png", variant)
        print(out_dir / f"{args.prefix}_{variant}.png")


if __name__ == "__main__":
    main()
