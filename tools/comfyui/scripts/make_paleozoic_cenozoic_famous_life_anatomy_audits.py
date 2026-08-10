import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = ROOT / "assets" / "dinosaurs"
AUDIT_DIR = ASSET_DIR / "anatomy-audit"

MARGIN = 28
GAP = 18
CELL_W = 560
IMAGE_H = 315
LABEL_H = 270
HEADER_H = 126
FOOTER_H = 58

ROLE_COLORS = {
    "REPRESENTATIVE CANDIDATE": (61, 148, 102),
    "COLOR / VIEW REVIEW": (199, 137, 51),
    "ECOLOGY / ANATOMY REVIEW": (70, 121, 172),
}

TAXA = {
    "anomalocaris-canadensis": {
        "audit_version": "v2",
        "title": "Anomalocaris canadensis anatomy audit v2",
        "subtitle": "Renewed gate: unmistakably soft unarmored trunk + thin flexible flaps, paired eyes/appendages, 3-pair + central-blade tail fan",
        "boundary": "Colors, soft-tissue contour, prey choice and swimming moment are reconstructed; hard-prey attack is not established.",
        "items": [
            {
                "role": "REPRESENTATIVE CANDIDATE",
                "kind": "count-level pass",
                "source": "anomalocaris-canadensis-softbody-tailfan-representative-imagegen-v2.png",
                "cue": "S1 left profile. Read two stalked eyes, one segmented frontal-appendage pair, a side-subordinate oral cone, a smooth matte soft trunk, sixteen pairs of thin flexible flaps, feathery dorsal setal blades, and a complete seven-blade tail fan. Reject a lobster-like armored trunk.",
            },
            {
                "role": "COLOR / VIEW REVIEW",
                "kind": "review hold",
                "source": "anomalocaris-canadensis-rightfacing-softflap-indigo-copper-imagegen-v2.png",
                "cue": "S2 right-facing rear-three-quarter comparison. The trunk is matte and unarmored with supple translucent-edged flaps and feathery setal blades; indigo-copper color is hypothetical. Foreshortening lowers count certainty, so this view cannot outrank S1.",
            },
            {
                "role": "ECOLOGY / ANATOMY REVIEW",
                "kind": "anatomy review",
                "source": "anomalocaris-canadensis-softbody-shelf-ecology-imagegen-v2.png",
                "cue": "S3 broad Cambrian shelf scene. The soft unarmored trunk, thin flaps, both frontal appendages and both eyes remain readable; tiny soft prey stay well ahead without contact. Prey, habitat arrangement and pursuit direction are illustrative only.",
            },
        ],
    },
    "dunkleosteus-terrelli": {
        "audit_version": "v2",
        "title": "Dunkleosteus terrelli anatomy audit v2",
        "subtitle": "Renewed gate: articulated armor + cutting jaw plates + exactly one dorsal fin; posterior body remains comparative reconstruction",
        "boundary": "Armor and jaw plates are direct cues; posterior trunk, fins, tail, colors and pictured behavior remain uncertain.",
        "items": [
            {
                "role": "REPRESENTATIVE CANDIDATE",
                "kind": "count-level pass",
                "source": "dunkleosteus-terrelli-single-dorsal-compact-armor-representative-imagegen-v2.png",
                "cue": "S1 right-facing candidate. Check blunt armor, plate seams and joint, blade-like jaw plates without conical teeth, a compact deep trunk, exactly one dorsal fin on the posterior half, a smooth back to the tail base, and one vertical tail.",
            },
            {
                "role": "COLOR / VIEW REVIEW",
                "kind": "review hold",
                "source": "dunkleosteus-terrelli-leftfacing-single-dorsal-copper-pattern-imagegen-v2.png",
                "cue": "S2 left-facing rear-three-quarter comparison. Exactly one large dorsal remains and the back is smooth to the tail base. Copper-gray weathering is invented; rear perspective and near-closed jaw reduce diagnostic clarity.",
            },
            {
                "role": "ECOLOGY / ANATOMY REVIEW",
                "kind": "anatomy review",
                "source": "dunkleosteus-terrelli-single-dorsal-fish-school-ecology-imagegen-v2.png",
                "cue": "S3 wide Devonian shelf scene. The main animal has exactly one dorsal and a smooth rear back; the fish school remains several body lengths away with no bite, capture or species-level association claimed. Small scale keeps this below S1.",
            },
        ],
    },
    "otodus-megalodon": {
        "title": "Otodus megalodon anatomy audit v1",
        "subtitle": "Tooth-led taxon: no complete skeleton; elongated 2025 lamniform body model is a provisional comparison, not a known outline",
        "boundary": "Teeth and some vertebrae are fossil evidence; rostrum, fins, proportions, color and whale encounter remain hypotheses.",
        "items": [
            {
                "role": "REPRESENTATIVE CANDIDATE",
                "kind": "count-level pass",
                "source": "otodus-megalodon-elongated-blunt-rostrum-representative-imagegen-v1.png",
                "cue": "S1 left profile candidate. Read a long streamlined lamniform body, short blunt broad rostrum, five gill slits, long paired pectorals, tall first plus tiny rear dorsal, pelvic and anal fins, and a vertical crescent tail. Reject giant-great-white certainty.",
            },
            {
                "role": "COLOR / VIEW REVIEW",
                "kind": "review hold",
                "source": "otodus-megalodon-rightfacing-slate-bronze-pattern-imagegen-v1.png",
                "cue": "S2 right-facing low-front view. Slate-bronze mottling is wholly speculative, and perspective makes fin proportions harder to compare. It remains a gallery variation, never anatomical confirmation.",
            },
            {
                "role": "ECOLOGY / ANATOMY REVIEW",
                "kind": "anatomy review",
                "source": "otodus-megalodon-neogene-whale-distance-ecology-imagegen-v1.png",
                "cue": "S3 distant shelf-drop scene. Shark and whale remain separated by several body lengths with no contact, bite or kill. Co-occurrence is educational context, not evidence for this individual event or exact body reconstruction.",
            },
        ],
    },
    "coelodonta-antiquitatis": {
        "audit_version": "v2",
        "title": "Coelodonta antiquitatis anatomy audit v2",
        "subtitle": "Renewed gate: high withers, dense coat, four grounded limbs, broad horn faces + narrow side-to-side thickness, small rear horn",
        "boundary": "Mummy and horn evidence lead the body and blade-horn direction; exact horn curve, coat, gait and social scene remain reconstructed.",
        "items": [
            {
                "role": "REPRESENTATIVE CANDIDATE",
                "kind": "count-level pass",
                "source": "coelodonta-antiquitatis-laterally-compressed-bladehorn-representative-imagegen-v2.png",
                "cue": "S1 shallow right-facing side/front candidate. Check exactly two horns: a long blade-like nasal horn with broad lateral faces, narrow side-to-side thickness and transverse bands, plus one much smaller rear horn. Four connected legs and grounded feet remain readable.",
            },
            {
                "role": "COLOR / VIEW REVIEW",
                "kind": "review hold",
                "source": "coelodonta-antiquitatis-leftfacing-tawny-patch-pattern-imagegen-v1.png",
                "cue": "S2 strict left profile with four separate grounded legs and feet. Tawny flank patches are a color hypothesis. The leg-count correction makes it reviewable but does not promote this variant over S1.",
            },
            {
                "role": "ECOLOGY / ANATOMY REVIEW",
                "kind": "anatomy review",
                "source": "coelodonta-antiquitatis-mammoth-steppe-ecology-imagegen-v1.png",
                "cue": "S3 wide grazing scene. Four rhino limbs remain separated while distant mammoths do not overlap. Grazing moment, herd relationship, coat, snow and tracks are illustrative; random tracks must not become a repeated pattern.",
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
    canvas = Image.new("RGB", size, (29, 33, 35))
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


def make_sheet(taxon_id, spec, overwrite=False):
    items = spec["items"]
    width = MARGIN * 2 + len(items) * CELL_W + (len(items) - 1) * GAP
    height = HEADER_H + GAP + IMAGE_H + LABEL_H + FOOTER_H + MARGIN
    sheet = Image.new("RGB", (width, height), (19, 23, 25))
    draw = ImageDraw.Draw(sheet)
    fonts = {
        "title": load_font(28, bold=True),
        "subtitle": load_font(15),
        "role": load_font(16, bold=True),
        "kind": load_font(15, bold=True),
        "filename": load_font(13),
        "body": load_font(15),
        "footer": load_font(14, bold=True),
    }

    draw.rectangle((0, 0, width, HEADER_H), fill=(26, 66, 58))
    draw.text((MARGIN, 16), spec["title"], fill=(245, 242, 232), font=fonts["title"])
    draw_wrapped(
        draw,
        (MARGIN, 60),
        spec["subtitle"],
        fonts["subtitle"],
        (197, 220, 210),
        width - MARGIN * 2,
        max_lines=2,
        line_gap=4,
    )

    for index, item in enumerate(items):
        x = MARGIN + index * (CELL_W + GAP)
        image_y = HEADER_H + GAP
        source = ASSET_DIR / item["source"]
        if not source.exists():
            raise FileNotFoundError(source)
        with Image.open(source) as image:
            sheet.paste(fit_image(image, (CELL_W, IMAGE_H)), (x, image_y))

        label_y = image_y + IMAGE_H
        draw.rectangle((x, label_y, x + CELL_W, label_y + LABEL_H), fill=(31, 35, 37))
        role_color = ROLE_COLORS[item["role"]]
        draw.rectangle((x, label_y, x + 8, label_y + LABEL_H), fill=role_color)
        draw.text((x + 20, label_y + 15), f"S{index + 1}  {item['role']}", fill=(241, 239, 231), font=fonts["role"])
        draw.text((x + 20, label_y + 43), item["kind"], fill=role_color, font=fonts["kind"])
        draw_wrapped(
            draw,
            (x + 20, label_y + 70),
            item["source"],
            fonts["filename"],
            (163, 179, 175),
            CELL_W - 40,
            max_lines=2,
            line_gap=4,
        )
        draw_wrapped(
            draw,
            (x + 20, label_y + 117),
            item["cue"],
            fonts["body"],
            (226, 223, 212),
            CELL_W - 40,
            max_lines=6,
            line_gap=5,
        )

    footer_y = HEADER_H + GAP + IMAGE_H + LABEL_H
    draw.rectangle((0, footer_y, width, footer_y + FOOTER_H), fill=(70, 38, 36))
    footer = (
        "PROMOTION GATE: S1 is the sole count-level representative candidate. "
        "S2 and S3 are prohibited from representative promotion without a separate anatomy review. "
        f"BOUNDARY: {spec['boundary']}"
    )
    draw_wrapped(
        draw,
        (MARGIN, footer_y + 10),
        footer,
        fonts["footer"],
        (248, 224, 211),
        width - MARGIN * 2,
        max_lines=2,
        line_gap=4,
    )

    audit_version = spec.get("audit_version", "v1")
    output = AUDIT_DIR / f"{taxon_id}-anatomy-audit-{audit_version}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing audit sheet: {output}")
    sheet.save(output, optimize=True)
    return output


def main():
    parser = argparse.ArgumentParser(description="Build famous-life anatomy audit sheets.")
    parser.add_argument("--taxon", choices=sorted(TAXA), help="Build only one taxon sheet.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing derived audit sheet.")
    args = parser.parse_args()
    outputs = []
    selected = {args.taxon: TAXA[args.taxon]} if args.taxon else TAXA
    for taxon_id, spec in selected.items():
        output = make_sheet(taxon_id, spec, overwrite=args.overwrite)
        with Image.open(output) as image:
            outputs.append(f"{output.relative_to(ROOT).as_posix()} {image.width}x{image.height}")
    print("\n".join(outputs))


if __name__ == "__main__":
    main()
