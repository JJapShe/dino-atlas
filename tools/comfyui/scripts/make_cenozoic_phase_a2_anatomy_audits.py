from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = ROOT / "assets" / "dinosaurs"
AUDIT_DIR = ASSET_DIR / "anatomy-audit"

MARGIN = 28
GAP = 18
CELL_W = 560
IMAGE_H = 315
LABEL_H = 226
HEADER_H = 108

ROLE_COLORS = {
    "REP CANDIDATE": (59, 132, 96),
    "COLOR REVIEW": (183, 126, 49),
    "ECOLOGY REVIEW": (58, 101, 143),
}

TAXA = {
    "mammut-americanum": {
        "title": "Mammut americanum anatomy audit v1",
        "subtitle": "Three approved assets | level back, low head, two upper tusks, one trunk, four feet",
        "items": [
            {
                "role": "REP CANDIDATE",
                "kind": "count-level pass",
                "source": "mammut-americanum-level-back-upcurved-tusks-representative-imagegen-v1.png",
                "cue": "Full-body right-facing candidate. Check a near-level back, low broad head, exactly two gently upcurved upper tusks, one trunk, four attached legs with broad feet, and one short tail.",
            },
            {
                "role": "COLOR REVIEW",
                "kind": "review hold",
                "source": "mammut-americanum-left-rear-woodland-review-imagegen-v1.png",
                "cue": "Left-facing rear three-quarter review. Recount two tusks, one trunk, four separated legs and feet, and one tail. Coat, color, season, and exact wet woodland remain hypotheses.",
            },
            {
                "role": "ECOLOGY REVIEW",
                "kind": "anatomy review",
                "source": "mammut-americanum-willow-browsing-ecology-imagegen-v1.png",
                "cue": "Non-graphic browsing reconstruction. Keep the whole mastodon readable and audit tusks, trunk, four feet, and tail separately; the pictured plant and individual feeding event are not direct evidence.",
            },
        ],
    },
    "megatherium-americanum": {
        "title": "Megatherium americanum anatomy audit v1",
        "subtitle": "Three approved assets | deep torso, massive pelvis, long forelimbs, claws, thick tail",
        "items": [
            {
                "role": "REP CANDIDATE",
                "kind": "count-level pass",
                "source": "megatherium-americanum-thick-tail-fourlimb-representative-imagegen-v2.png",
                "cue": "Full-body left-facing candidate. Check a small head, deep torso, massive pelvis, two long clawed forelimbs, two weight-bearing hind limbs, and one thick continuous tail. Do not infer exact claw digits.",
            },
            {
                "role": "COLOR REVIEW",
                "kind": "review hold",
                "source": "megatherium-americanum-right-streambank-review-imagegen-v1.png",
                "cue": "Right-facing low-walk review. Recount all four limbs, both foreclaw groups, massive hindquarters, and the full tail; coat, palette, gait phase, and streambank setting remain reconstructed.",
            },
            {
                "role": "ECOLOGY REVIEW",
                "kind": "anatomy review",
                "source": "megatherium-americanum-tripod-browse-ecology-imagegen-v1.png",
                "cue": "Stationary tripod-browse reconstruction. Audit both raised forelimbs, two grounded hind limbs, and the tail support separately. It is not evidence of a permanent upright gait or this exact feeding event.",
            },
        ],
    },
    "arctodus-simus": {
        "title": "Arctodus simus anatomy audit v1",
        "subtitle": "Three approved assets | broad head, moderate muzzle, level shoulders, plantigrade paws",
        "items": [
            {
                "role": "REP CANDIDATE",
                "kind": "count-level pass",
                "source": "arctodus-simus-level-shoulders-plantigrade-representative-imagegen-v2.png",
                "cue": "Full-body right-facing candidate. Check a broad deep head, moderate non-pug muzzle, compact ears, no extreme shoulder hump, four robust plantigrade paws, and one short tail.",
            },
            {
                "role": "COLOR REVIEW",
                "kind": "review hold",
                "source": "arctodus-simus-rear-aspen-gray-review-imagegen-v1.png",
                "cue": "Left-facing rear three-quarter review. Recount four attached legs and plantigrade feet plus one short tail. Gray coat, neck patch, weather, and aspen-edge setting are hypothetical.",
            },
            {
                "role": "ECOLOGY REVIEW",
                "kind": "anatomy review",
                "source": "arctodus-simus-log-berry-foraging-ecology-imagegen-v1.png",
                "cue": "Non-contact foraging scene. Keep all four limbs, paws, head, and tail readable. Berries and a log do not prove diet choice, scavenging, predation, speed, or an exact observed behavior.",
            },
        ],
    },
    "glyptodon-reticulatus": {
        "title": "Glyptodon reticulatus anatomy audit v1",
        "subtitle": "Three approved assets | rigid dome, rosette osteoderms, four legs, ringed non-club tail",
        "items": [
            {
                "role": "REP CANDIDATE",
                "kind": "count-level pass",
                "source": "glyptodon-reticulatus-rigid-carapace-ringed-tail-representative-imagegen-v1.png",
                "cue": "Full-body right-facing candidate. Check a rigid domed carapace with rosette-like osteoderms, small armored head, four stout legs and feet, and one ring-armored tail without an expanded knob or spikes.",
            },
            {
                "role": "COLOR REVIEW",
                "kind": "review hold",
                "source": "glyptodon-reticulatus-four-visible-feet-review-imagegen-v2.png",
                "cue": "Left-facing wetland review chosen for four separated feet. Retain the rigid dome and tapering ring-armored tail, but treat head shape, distal tail fusion, osteoderm geometry, palette, and habitat as unresolved.",
            },
            {
                "role": "ECOLOGY REVIEW",
                "kind": "anatomy review",
                "source": "glyptodon-reticulatus-megatherium-coexistence-ecology-imagegen-v1.png",
                "cue": "Two-taxon, non-contact reconstruction. Audit the foreground Glyptodon and distant Megatherium separately. The frame proves no interaction, shared herd, or exact locality and moment of coexistence.",
            },
        ],
    },
}


def load_font(size, bold=False):
    candidates = (
        Path("C:/Windows/Fonts/arialbd.ttf") if bold else Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf") if bold else Path("C:/Windows/Fonts/segoeui.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def fit_image(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (30, 34, 35))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def wrap_pixels(draw, text, font, max_width, max_lines):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            line = candidate
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textlength(f"{lines[-1]}...", font=font) > max_width and lines[-1]:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = f"{lines[-1]}..."
    return lines


def draw_wrapped(draw, xy, text, font, fill, max_width, max_lines, line_gap=5):
    x, y = xy
    lines = wrap_pixels(draw, text, font, max_width, max_lines)
    bbox = font.getbbox("Ag")
    line_height = bbox[3] - bbox[1] + line_gap
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_height), line, fill=fill, font=font)


def make_sheet(taxon_id, spec):
    items = spec["items"]
    width = MARGIN * 2 + len(items) * CELL_W + (len(items) - 1) * GAP
    height = HEADER_H + GAP + IMAGE_H + LABEL_H + MARGIN
    sheet = Image.new("RGB", (width, height), (20, 24, 25))
    draw = ImageDraw.Draw(sheet)
    fonts = {
        "title": load_font(28, bold=True),
        "subtitle": load_font(16),
        "role": load_font(18, bold=True),
        "kind": load_font(15, bold=True),
        "filename": load_font(13),
        "body": load_font(16),
    }

    draw.rectangle((0, 0, width, HEADER_H), fill=(24, 66, 56))
    draw.text((MARGIN, 17), spec["title"], fill=(244, 242, 232), font=fonts["title"])
    draw.text((MARGIN, 61), spec["subtitle"], fill=(195, 218, 207), font=fonts["subtitle"])

    for index, item in enumerate(items):
        x = MARGIN + index * (CELL_W + GAP)
        image_y = HEADER_H + GAP
        source = ASSET_DIR / item["source"]
        if not source.exists():
            raise FileNotFoundError(source)
        with Image.open(source) as image:
            sheet.paste(fit_image(image, (CELL_W, IMAGE_H)), (x, image_y))

        label_y = image_y + IMAGE_H
        role_color = ROLE_COLORS[item["role"]]
        draw.rectangle((x, label_y, x + CELL_W, label_y + LABEL_H), fill=(31, 35, 36))
        draw.rectangle((x, label_y, x + 8, label_y + LABEL_H), fill=role_color)
        draw.text((x + 20, label_y + 15), f"S{index + 1}  {item['role']}", fill=(240, 239, 232), font=fonts["role"])
        draw.text((x + 20, label_y + 45), item["kind"], fill=role_color, font=fonts["kind"])
        draw_wrapped(
            draw,
            (x + 20, label_y + 74),
            item["source"],
            fonts["filename"],
            (163, 178, 174),
            CELL_W - 40,
            max_lines=2,
            line_gap=4,
        )
        draw_wrapped(
            draw,
            (x + 20, label_y + 119),
            item["cue"],
            fonts["body"],
            (225, 222, 211),
            CELL_W - 40,
            max_lines=4,
            line_gap=5,
        )

    output = AUDIT_DIR / f"{taxon_id}-anatomy-audit-v1.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    return output


def main():
    outputs = []
    for taxon_id, spec in TAXA.items():
        output = make_sheet(taxon_id, spec)
        with Image.open(output) as image:
            outputs.append(f"{output.relative_to(ROOT).as_posix()} {image.width}x{image.height}")
    print("\n".join(outputs))


if __name__ == "__main__":
    main()
