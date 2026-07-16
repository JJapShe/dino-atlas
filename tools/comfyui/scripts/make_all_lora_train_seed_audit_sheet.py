import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LORA_ROOT = ROOT / "tools" / "comfyui" / "lora_training"
DEFAULT_OUTPUT = DEFAULT_LORA_ROOT / "review" / "all_lora_train_seed_audit_sheet_v1.png"


def wrap_text(text, max_chars, max_lines):
    words = str(text or "").split()
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


def load_train_seeds(lora_root):
    rows = []
    for manifest_path in sorted(lora_root.glob("*/seed_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("items", []):
            if item.get("role") != "train_seed":
                continue
            rows.append(
                {
                    "dataset": manifest["datasetId"],
                    "trigger": manifest["trigger"],
                    "id": item["id"],
                    "source": item["source"],
                    "strengths": item.get("strengths", []),
                    "risks": item.get("risks", []),
                }
            )
    return rows


def draw_tile(row, thumb_size, label_h):
    tile = Image.new("RGB", (thumb_size[0], thumb_size[1] + label_h), (246, 244, 235))
    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()
    source = ROOT / row["source"]
    if source.exists():
        with Image.open(source) as image:
            tile.paste(fit(image, thumb_size), (0, 0))
    else:
        draw.rectangle((0, 0, thumb_size[0], thumb_size[1]), fill=(222, 216, 205))
        draw.text((12, 12), "missing source", fill=(130, 48, 44), font=font)

    y = thumb_size[1]
    draw.rectangle((0, y, thumb_size[0], y + 8), fill=(43, 111, 76))
    y += 14
    draw.text((8, y), row["dataset"][:58], fill=(38, 35, 31), font=font)
    y += 16
    draw.text((8, y), row["id"][:58], fill=(38, 35, 31), font=font)
    y += 18
    strength = row["strengths"][0] if row["strengths"] else ""
    risk = row["risks"][0] if row["risks"] else ""
    for line in wrap_text(f"ok: {strength}", 58, 2):
        draw.text((8, y), line, fill=(50, 84, 61), font=font)
        y += 14
    for line in wrap_text(f"risk: {risk}", 58, 3):
        draw.text((8, y), line, fill=(121, 63, 46), font=font)
        y += 14
    return tile


def make_sheet(rows, output):
    thumb = (320, 214)
    label_h = 112
    cols = 3
    gap = 14
    header_h = 92
    content_w = cols * thumb[0] + (cols + 1) * gap
    rows_count = max(1, (len(rows) + cols - 1) // cols)
    sheet_h = header_h + rows_count * (thumb[1] + label_h + gap) + gap
    sheet = Image.new("RGB", (content_w, sheet_h), (232, 228, 218))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    draw.rectangle((0, 0, content_w, header_h), fill=(27, 60, 47))
    draw.text((18, 18), "All LoRA train_seed audit", fill=(248, 246, 238), font=font)
    draw.text((18, 42), f"train_seed items: {len(rows)}", fill=(220, 228, 216), font=font)
    draw.text(
        (18, 66),
        "Positive seeds only. Demote any card whose risks contradict required anatomy.",
        fill=(190, 207, 190),
        font=font,
    )

    y0 = header_h + gap
    for idx, row in enumerate(rows):
        x = gap + (idx % cols) * (thumb[0] + gap)
        y = y0 + (idx // cols) * (thumb[1] + label_h + gap)
        sheet.paste(draw_tile(row, thumb, label_h), (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lora-root", default=str(DEFAULT_LORA_ROOT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    rows = load_train_seeds(Path(args.lora_root))
    make_sheet(rows, Path(args.output))
    print(args.output)


if __name__ == "__main__":
    main()
