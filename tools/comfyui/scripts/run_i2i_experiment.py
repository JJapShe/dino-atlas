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
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_i2i_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


def configure(workflow, taxon_id, guide_image, seed, denoise, prefix, ckpt_name=None):
    prompt = build_prompt(taxon_id)
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["denoise"] = denoise
    workflow["6"]["inputs"]["text"] = (
        prompt["positivePrompt"]
        + ", naturalistic 3D paleo reconstruction, detailed skin or feather texture, realistic soft shadows, "
        "finished museum-quality educational render, unsigned finished image, no corner marks, "
        "plain clean background, one clear readable animal silhouette"
    )
    workflow["7"]["inputs"]["text"] = (
        prompt["negativePrompt"]
        + ", lower right signature, lower left signature, small artist mark, decorative initials, fake artist name, "
        "printed text on ground, face on tail, eye on tail, flat cartoon, simple vector art, children's drawing, "
        "thick black outline, flat cel shading"
    )
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}_{taxon_id}_d{int(denoise * 100):02d}"
    workflow["12"]["inputs"]["image"] = guide_image
    return workflow


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def make_contact_sheet(paths, output, thumb_w=360, thumb_h=240):
    if not paths:
        return
    rows = []
    for path, label in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + 42), (245, 243, 236))
        x = (thumb_w - image.width) // 2
        tile.paste(image, (x, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 10), label[:52], fill=(31, 31, 28), font=ImageFont.load_default())
        rows.append(tile)
    cols = min(3, len(rows))
    sheet_w = cols * thumb_w
    sheet_h = ((len(rows) + cols - 1) // cols) * (thumb_h + 42)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (228, 224, 214))
    for idx, tile in enumerate(rows):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + 42)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def clean_lower_corners(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    draw = ImageDraw.Draw(image)
    for x0, x1 in [(0, 260), (w - 300, w)]:
        sample_box = (max(0, x0), h - 120, min(w, x1), h - 95)
        sample = image.crop(sample_box).resize((1, 1))
        color = sample.getpixel((0, 0))
        draw.rectangle((x0, h - 90, x1, h), fill=color)
    image.save(path)


def stage_source_image(source_path, taxon_id, prefix):
    source = Path(source_path)
    if not source.is_absolute():
        source = (Path.cwd() / source).resolve()
    staged_dir = COMFY_INPUT / "dino_i2i_sources"
    staged_dir.mkdir(parents=True, exist_ok=True)
    staged = staged_dir / f"{prefix}_{taxon_id}{source.suffix.lower()}"
    shutil.copy2(source, staged)
    return str(staged.relative_to(COMFY_INPUT)).replace("\\", "/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", action="append", required=True)
    parser.add_argument("--seed", type=int, action="append", default=[])
    parser.add_argument("--denoise", type=float, action="append", default=[])
    parser.add_argument("--guide-kind", default="shape")
    parser.add_argument("--source-image", help="Optional local image to use instead of a generated dino guide.")
    parser.add_argument("--prefix", default="i2i_shape")
    parser.add_argument("--ckpt-name")
    args = parser.parse_args()

    seeds = args.seed or [2026064101, 2026064102]
    denoises = args.denoise or [0.58, 0.68, 0.78]
    results = []
    for taxon_id in args.taxon_id:
        guide = (
            stage_source_image(args.source_image, taxon_id, args.prefix)
            if args.source_image
            else f"dino_guides/{taxon_id}_{args.guide_kind}.png"
        )
        for denoise in denoises:
            for seed in seeds:
                workflow = configure(load_workflow(TEMPLATE), taxon_id, guide, seed, denoise, args.prefix, args.ckpt_name)
                queued = queue_prompt(workflow, client_id="dino-atlas-i2i")
                history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                images = output_images_from_history(history)
                for image in images:
                    results.append(
                        {
                            "taxonId": taxon_id,
                            "seed": seed,
                            "denoise": denoise,
                            "image": str(image),
                        }
                    )

    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    copied = []
    for item in results:
        src = Path(item["image"])
        dst = EXPERIMENT_OUT / f"{args.prefix}_{item['taxonId']}_seed{item['seed']}_d{int(item['denoise'] * 100):02d}.png"
        shutil.copy2(src, dst)
        copied.append((dst, f"{item['taxonId']} seed {item['seed']} d{item['denoise']:.2f}"))

    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
