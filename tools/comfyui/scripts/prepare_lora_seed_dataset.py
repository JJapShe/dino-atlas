import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "seed_manifest.json"
DEFAULT_OUTPUT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "materialized_seed"


def safe_stem(value):
    return "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value).strip("_")


def load_manifest(path):
    return json.loads(path.read_text(encoding="utf-8"))


def selected_items(manifest, roles):
    wanted = set(roles)
    return [item for item in manifest["items"] if item.get("role") in wanted]


def write_contact_sheet(rows, output):
    if not rows:
        return
    thumb_w, thumb_h, label_h = 320, 214, 64
    cols = min(2, len(rows))
    sheet_rows = (len(rows) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, sheet_rows * (thumb_h + label_h)), (235, 231, 220))
    font = ImageFont.load_default()
    for idx, row in enumerate(rows):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (246, 244, 235))
        image = Image.open(row["path"]).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        tile.paste(image, ((thumb_w - image.width) // 2, (thumb_h - image.height) // 2))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), row["id"][:50], fill=(120, 58, 45), font=font)
        draw.text((8, thumb_h + 28), row["role"][:50], fill=(40, 37, 32), font=font)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(tile, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def materialize(manifest_path, output_dir, roles):
    manifest = load_manifest(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    missing = []

    for item in selected_items(manifest, roles):
        source = ROOT / item["source"]
        if not source.exists():
            missing.append(item["source"])
            continue
        stem = safe_stem(item["id"])
        image_out = output_dir / f"{stem}{source.suffix.lower()}"
        caption_out = output_dir / f"{stem}.txt"
        shutil.copy2(source, image_out)
        caption_out.write_text(item["caption"].strip() + "\n", encoding="utf-8")
        copied.append(
            {
                "id": item["id"],
                "role": item["role"],
                "source": item["source"],
                "image": str(image_out.relative_to(ROOT)).replace("\\", "/"),
                "caption": str(caption_out.relative_to(ROOT)).replace("\\", "/"),
                "path": image_out,
            }
        )

    summary = {
        "datasetId": manifest["datasetId"],
        "trigger": manifest["trigger"],
        "roles": roles,
        "count": len(copied),
        "missing": missing,
        "items": [
            {key: value for key, value in row.items() if key != "path"}
            for row in copied
        ],
    }
    summary_path = output_dir / "materialized_manifest.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_contact_sheet(copied, output_dir / "materialized_contact_sheet.png")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Materialize reviewed LoRA seed images and captions.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--role",
        action="append",
        default=[],
        help="Manifest role to include. Defaults to train_seed. Repeat for multiple roles.",
    )
    args = parser.parse_args()
    roles = args.role or ["train_seed"]
    summary = materialize(Path(args.manifest).resolve(), Path(args.output_dir).resolve(), roles)
    print(json.dumps({key: summary[key] for key in ("datasetId", "trigger", "roles", "count", "missing")}, indent=2))


if __name__ == "__main__":
    main()
