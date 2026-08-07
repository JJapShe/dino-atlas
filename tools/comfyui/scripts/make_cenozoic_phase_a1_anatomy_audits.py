from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = ROOT / "assets" / "dinosaurs"
AUDIT_DIR = ASSET_DIR / "anatomy-audit"

MARGIN = 28
GAP = 18
CELL_W = 560
IMAGE_H = 315
LABEL_H = 212
HEADER_H = 108

ROLE_COLORS = {
    "REPRESENTATIVE": (59, 132, 96),
    "COLOR REVIEW": (183, 126, 49),
    "ECOLOGY REVIEW": (58, 101, 143),
}

TAXA = {
    "mammuthus-primigenius": {
        "title": "Mammuthus primigenius anatomy audit v1",
        "subtitle": "Three approved assets | high shoulder, sloping back, two upper tusks, four padded feet",
        "items": [
            {
                "role": "REPRESENTATIVE",
                "kind": "count-level pass",
                "source": "mammuthus-primigenius-high-shoulder-spiral-tusks-representative-imagegen-v1.png",
                "cue": "Full-body left profile. Check high forequarters, descending back, domed head, exactly two spiral upper tusks, one trunk, short tail, and four connected legs with broad feet.",
            },
            {
                "role": "COLOR REVIEW",
                "kind": "review hold",
                "source": "mammuthus-primigenius-right-facing-charcoal-coat-review-imagegen-v2.png",
                "cue": "Right-facing walking variation. Confirm charcoal-brown coat remains hypothetical while two upper tusks, one trunk, shoulder slope, short tail, and four feet remain readable.",
            },
            {
                "role": "ECOLOGY REVIEW",
                "kind": "anatomy review",
                "source": "mammuthus-primigenius-mother-calf-foraging-ecology-imagegen-v1.png",
                "cue": "Adult and calf forage without contact overlap. Audit both bodies separately, the adult's two upper tusks, four limbs per animal, trunk-to-plant contact, and vegetated steppe-tundra setting.",
            },
        ],
    },
    "smilodon-fatalis": {
        "title": "Smilodon fatalis anatomy audit v1",
        "subtitle": "Three approved assets | paired upper sabers, robust forequarters, feline paws, short tail",
        "items": [
            {
                "role": "REPRESENTATIVE",
                "kind": "count-level pass",
                "source": "smilodon-fatalis-robust-forequarters-two-canines-representative-imagegen-v1.png",
                "cue": "Full-body left profile. Check one pair of elongated upper canine sabers, deep feline head, powerful neck and forequarters, four connected legs with feline paws, and a short tail.",
            },
            {
                "role": "COLOR REVIEW",
                "kind": "review hold",
                "source": "smilodon-fatalis-right-facing-gray-mottle-review-imagegen-v2.png",
                "cue": "Right-facing gray-brown variation. Coat color and mottling are hypothetical; retain paired upper sabers, broad chest, robust forelimbs, four paws, and a short tail without tiger or lion drift.",
            },
            {
                "role": "ECOLOGY REVIEW",
                "kind": "anatomy review",
                "source": "smilodon-fatalis-dry-wash-distant-bovids-ecology-imagegen-v1.png",
                "cue": "Wide non-contact habitat scene. Keep the complete cat readable with paired upper sabers, four limbs, feline paws, and short tail; distant bovids indicate attention only, not a proven hunt.",
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
        "footer": load_font(13),
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
        draw.rectangle((x, label_y, x + CELL_W, label_y + LABEL_H), fill=(31, 35, 36))
        role_color = ROLE_COLORS[item["role"]]
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
            max_lines=3,
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
