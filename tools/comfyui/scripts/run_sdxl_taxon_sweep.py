import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history
from generate_dino_prompt import build_prompt


ROOT = Path(__file__).resolve().parents[1]
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_base_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


def configure(workflow, taxon_id, seed, prefix, ckpt_name=None, width=None, height=None):
    prompt = build_prompt(taxon_id)
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = prompt["positivePrompt"]
    workflow["7"]["inputs"]["text"] = prompt["negativePrompt"]
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}_{taxon_id}"
    if width:
        workflow["5"]["inputs"]["width"] = width
    if height:
        workflow["5"]["inputs"]["height"] = height
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
    cols = min(2, len(tiles))
    sheet = Image.new("RGB", (cols * thumb_w, ((len(tiles) + cols - 1) // cols) * (thumb_h + 42)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + 42)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", action="append", required=True)
    parser.add_argument("--seed", action="append", type=int, default=[])
    parser.add_argument("--prefix", default="sdxl_sweep")
    parser.add_argument("--ckpt-name")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--clean-corners", action="store_true")
    args = parser.parse_args()

    seeds = args.seed or [2026065301, 2026065302, 2026065303, 2026065304]
    results = []
    copied = []
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    for taxon_id in args.taxon_id:
        for seed in seeds:
            workflow = configure(load_workflow(TEMPLATE), taxon_id, seed, args.prefix, args.ckpt_name, args.width, args.height)
            queued = queue_prompt(workflow, client_id="dino-atlas-sdxl-sweep")
            history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
            for image in output_images_from_history(history):
                item = {"taxonId": taxon_id, "seed": seed, "image": str(image)}
                results.append(item)
                dst = EXPERIMENT_OUT / f"{args.prefix}_{taxon_id}_seed{seed}.png"
                shutil.copy2(image, dst)
                if args.clean_corners:
                    clean_lower_corners(dst)
                copied.append((dst, f"{taxon_id} seed {seed}"))

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
