import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
APP_JS = ROOT / "app.js"
MANIFEST = ROOT / "tools" / "comfyui" / "outputs" / "app-gallery-samples.json"
ASSET_DIR = ROOT / "assets" / "dinosaurs"
AUDIT_DIR = ASSET_DIR / "anatomy-audit"
FULL_AUDIT = ASSET_DIR / "all-gallery-anatomy-audit-v1.png"

RANK = {
    "primary generated": 0,
    "primary structure reference": 0,
    "count-level pass": 0,
    "review hold": 1,
    "anatomy review": 2,
    "structure reference": 3,
    "diagnostic only": 4,
}


def load_audit_font(size=14):
    for candidate in (
        Path("C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/malgunbd.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def parse_samples():
    text = APP_JS.read_text(encoding="utf-8")
    start = text.index("const generatedImageSamples = {")
    end = text.index("const anatomyCandidateRank", start)
    section = text[start:end]
    samples = {}
    current_taxon = None
    current = None

    for raw_line in section.splitlines():
        line = raw_line.strip()
        taxon_match = re.match(r'"([^"]+)": \[', line)
        if taxon_match:
            current_taxon = taxon_match.group(1)
            samples.setdefault(current_taxon, [])
            continue
        if line == "{":
            current = {}
            continue
        if current is None:
            continue
        for key in ("kind", "title", "body", "source", "variant", "src"):
            match = re.match(rf'{key}: "(.*)",?$', line)
            if match:
                current[key] = match.group(1)
        if line == "},":
            if current.get("src") or current.get("source"):
                samples[current_taxon].append(current)
            current = None

    return {taxon: sorted(items, key=image_rank) for taxon, items in samples.items()}


def image_rank(item):
    return RANK.get(item.get("kind"), 4)


def flatten(samples):
    return [
        {"taxon": taxon, **item, "image": item.get("src") or item.get("source")}
        for taxon, items in samples.items()
        for item in items
    ]


def write_manifest(samples):
    missing = []
    for items in samples.values():
        for item in items:
            image = item.get("src") or item.get("source")
            if image and not (ROOT / image).exists():
                missing.append(image)

    manifest = {
        "taxa": len(samples),
        "images": sum(len(items) for items in samples.values()),
        "missing": sorted(missing),
        "rankOrder": list(RANK),
        "samples": samples,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def draw_wrapped_text(draw, xy, text, font, fill, max_chars, max_lines=2):
    x, y = xy
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 18), line, fill=fill, font=font)


def make_sheet(items, output, title, cols=5, thumb_w=280, thumb_h=188):
    label_h = 74
    header_h = 64
    rows = max(1, (len(items) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * thumb_w, header_h + rows * (thumb_h + label_h)), (232, 228, 218))
    draw = ImageDraw.Draw(sheet)
    font = load_audit_font()
    draw.rectangle((0, 0, sheet.width, header_h), fill=(22, 55, 42))
    draw.text((16, 14), title, fill=(245, 243, 236), font=font)
    draw.text(
        (16, 36),
        f"{len(items)} connected images; sorted by anatomy gate rank.",
        fill=(220, 225, 214),
        font=font,
    )

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image_path = ROOT / item["image"]
        if image_path.exists():
            image = Image.open(image_path).convert("RGB")
            image.thumbnail((thumb_w, thumb_h))
            tile.paste(image, ((thumb_w - image.width) // 2, 0))
        tile_draw = ImageDraw.Draw(tile)
        tile_draw.text(
            (8, thumb_h + 8),
            f"{item.get('taxon', '')} | {item.get('kind', '')}"[:52],
            fill=(135, 64, 48),
            font=font,
        )
        draw_wrapped_text(
            tile_draw,
            (8, thumb_h + 30),
            item.get("title", ""),
            font,
            (42, 39, 35),
            max_chars=42,
        )
        x = (idx % cols) * thumb_w
        y = header_h + (idx // cols) * (thumb_h + label_h)
        sheet.paste(tile, (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def write_audit_sheets(samples, taxon_ids=None):
    entries = flatten(samples)
    if taxon_ids:
        entries = [entry for entry in entries if entry["taxon"] in taxon_ids]

    selected_taxa = taxon_ids or sorted(samples)
    for taxon in selected_taxa:
        taxon_items = [entry for entry in flatten(samples) if entry["taxon"] == taxon]
        if not taxon_items:
            continue
        make_sheet(
            taxon_items,
            AUDIT_DIR / f"{taxon}-anatomy-audit-v1.png",
            f"{taxon} anatomy audit v1",
            cols=2,
            thumb_w=420,
            thumb_h=280,
        )

    if not taxon_ids:
        make_sheet(entries, FULL_AUDIT, "all connected gallery anatomy audit v1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", action="append", help="Only regenerate audit sheet(s) for selected taxa.")
    args = parser.parse_args()

    samples = parse_samples()
    manifest = write_manifest(samples)
    write_audit_sheets(samples, args.taxon_id)
    print(json.dumps({"taxa": manifest["taxa"], "images": manifest["images"], "missing": manifest["missing"]}, indent=2))


if __name__ == "__main__":
    main()
