import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history
from generate_dino_prompt import build_prompt


ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = ROOT / "ComfyUI" / "input"
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
DEFAULT_TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_refiner_i2i_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


def configure(workflow, taxon_id, input_name, seed, denoise, prefix, polish=False):
    prompt = build_prompt(taxon_id)
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["denoise"] = denoise
    workflow["6"]["inputs"]["text"] = (
        prompt["positivePrompt"]
        + ", preserve the exact full-body silhouette and pose from the input image, "
        "add subtle natural skin or feather texture, soft realistic light, refined educational paleoart"
        + (", more dimensional body volume, not flat vector art, realistic material detail" if polish else "")
    )
    workflow["7"]["inputs"]["text"] = (
        prompt["negativePrompt"]
        + ", changed silhouette, changed pose, new horns, missing diagnostic feature, extra diagnostic feature, "
        "overpainted background, text, signature, watermark, logo, flat cartoon, simple vector art, thick black outline"
    )
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}_{taxon_id}_d{int(denoise * 100):02d}"
    workflow["12"]["inputs"]["image"] = input_name
    return workflow


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def clean_lower_corners(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    draw = ImageDraw.Draw(image)
    for x0, x1 in [(0, 260), (w - 300, w)]:
        sample = image.crop((max(0, x0), h - 120, min(w, x1), h - 95)).resize((1, 1))
        draw.rectangle((x0, h - 90, x1, h), fill=sample.getpixel((0, 0)))
    image.save(path)


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
    cols = min(3, len(tiles))
    sheet = Image.new("RGB", (cols * thumb_w, ((len(tiles) + cols - 1) // cols) * (thumb_h + 42)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + 42)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--item", action="append", required=True, help="taxon_id=path")
    parser.add_argument("--seed", type=int, default=2026065501)
    parser.add_argument("--denoise", type=float, action="append", default=[])
    parser.add_argument("--prefix", default="refiner_pass")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    parser.add_argument("--polish", action="store_true")
    args = parser.parse_args()

    denoises = args.denoise or [0.28]
    input_dir = COMFY_INPUT / "dino_refine"
    input_dir.mkdir(parents=True, exist_ok=True)
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    results = []
    copied = []
    for raw_item in args.item:
        taxon_id, raw_path = raw_item.split("=", 1)
        source = Path(raw_path).resolve()
        staged = input_dir / f"{taxon_id}{source.suffix.lower()}"
        shutil.copy2(source, staged)
        input_name = f"dino_refine/{staged.name}"
        for denoise in denoises:
            workflow = configure(load_workflow(args.template), taxon_id, input_name, args.seed, denoise, args.prefix, args.polish)
            queued = queue_prompt(workflow, client_id="dino-atlas-refiner-pass")
            history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
            for image in output_images_from_history(history):
                results.append({"taxonId": taxon_id, "seed": args.seed, "denoise": denoise, "image": str(image)})
                dst = EXPERIMENT_OUT / f"{args.prefix}_{taxon_id}_seed{args.seed}_d{int(denoise * 100):02d}.png"
                shutil.copy2(image, dst)
                clean_lower_corners(dst)
                copied.append((dst, f"{taxon_id} refiner d{denoise:.2f}"))

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
