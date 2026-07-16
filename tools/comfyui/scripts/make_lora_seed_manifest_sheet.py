import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "seed_manifest.json"
DEFAULT_OUTPUT = ROOT / "tools" / "comfyui" / "lora_training" / "stegosaur_plates_tailspikes" / "review" / "stegosaur_seed_manifest_sheet_v2.png"

ROLE_COLORS = {
    "train_seed": (45, 111, 76),
    "control_reference": (68, 92, 138),
    "review_hold": (143, 100, 52),
    "reject_reference": (144, 68, 64),
}


def wrap_text(text, max_chars, max_lines):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    return lines[:max_lines]


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (246, 244, 235))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def draw_item(item, thumb_size, label_h):
    tile = Image.new("RGB", (thumb_size[0], thumb_size[1] + label_h), (246, 244, 235))
    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()
    source = ROOT / item["source"]
    if source.exists():
        tile.paste(fit(Image.open(source), thumb_size), (0, 0))
    else:
        draw.rectangle((0, 0, thumb_size[0], thumb_size[1]), fill=(222, 216, 205))
        draw.text((12, 12), "missing source", fill=(120, 58, 45), font=font)

    color = ROLE_COLORS.get(item.get("role"), (90, 90, 84))
    draw.rectangle((0, thumb_size[1], thumb_size[0], thumb_size[1] + 8), fill=color)
    draw.text((8, thumb_size[1] + 14), item["id"][:56], fill=(38, 35, 31), font=font)
    draw.text((8, thumb_size[1] + 32), item.get("role", "")[:44], fill=color, font=font)
    summary = "; ".join(item.get("strengths", [])[:1] + item.get("risks", [])[:1])
    for idx, line in enumerate(wrap_text(summary, 58, 2)):
        draw.text((8, thumb_size[1] + 52 + idx * 15), line, fill=(72, 66, 58), font=font)
    return tile


def make_sheet(manifest, output):
    items = manifest["items"]
    order = ["train_seed", "control_reference", "review_hold", "reject_reference"]
    grouped = {role: [item for item in items if item.get("role") == role] for role in order}

    thumb = (320, 214)
    label_h = 92
    cols = 3
    gap = 14
    header_h = 112
    role_header_h = 34
    content_w = cols * thumb[0] + (cols + 1) * gap

    section_heights = []
    for role in order:
        count = len(grouped[role])
        rows = max(1, (count + cols - 1) // cols)
        section_heights.append(role_header_h + rows * (thumb[1] + label_h + gap) + gap)
    sheet_h = header_h + sum(section_heights) + gap
    sheet = Image.new("RGB", (content_w, sheet_h), (232, 228, 218))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    draw.rectangle((0, 0, content_w, header_h), fill=(27, 60, 47))
    draw.text((18, 18), f"{manifest['datasetId']} seed manifest review", fill=(248, 246, 238), font=font)
    draw.text((18, 42), f"trigger: {manifest['trigger']} / items: {len(items)}", fill=(220, 228, 216), font=font)
    draw.text(
        (18, 68),
        "Only train_seed items may be materialized for smoke tests; control/reject items are gates, not training data.",
        fill=(190, 207, 190),
        font=font,
    )

    y = header_h
    for role in order:
        role_items = grouped[role]
        color = ROLE_COLORS.get(role, (90, 90, 84))
        draw.rectangle((0, y, content_w, y + role_header_h), fill=color)
        draw.text((18, y + 10), f"{role} ({len(role_items)})", fill=(250, 248, 239), font=font)
        y += role_header_h + gap
        for idx, item in enumerate(role_items):
            x = gap + (idx % cols) * (thumb[0] + gap)
            tile_y = y + (idx // cols) * (thumb[1] + label_h + gap)
            sheet.paste(draw_item(item, thumb, label_h), (x, tile_y))
        rows = max(1, (len(role_items) + cols - 1) // cols)
        y += rows * (thumb[1] + label_h + gap) + gap

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    make_sheet(manifest, Path(args.output))
    print(args.output)


if __name__ == "__main__":
    main()
