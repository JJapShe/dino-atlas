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
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_ipadapter_i2i_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def input_name(path):
    return str(path.relative_to(COMFY_INPUT)).replace("\\", "/")


def configure(
    workflow,
    taxon_id,
    reference_image,
    guide_image,
    seed,
    denoise,
    weight,
    weight_type,
    end_at,
    prefix,
    ckpt_name,
    ipadapter_file,
):
    prompt = build_prompt(taxon_id)
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["denoise"] = denoise
    workflow["6"]["inputs"]["text"] = (
        prompt["positivePrompt"]
        + ", preserve the reference image's feathered back, folded arm feather cues, and earth-tone coloration, "
        "clean single long tail only, no extra tail line, clean readable feet, museum reference card render"
    )
    workflow["7"]["inputs"]["text"] = (
        prompt["negativePrompt"]
        + ", extra tail, second tail, tail under the body, duplicate rear limb, extra rear limb, "
        "long curved appendage below the body, detached feather line, tail thread, text, watermark, signature"
    )
    workflow["9"]["inputs"]["filename_prefix"] = (
        f"dino_atlas/{prefix}_{taxon_id}_w{int(weight * 100):02d}_d{int(denoise * 100):02d}"
    )
    workflow["12"]["inputs"]["image"] = input_name(reference_image)
    workflow["15"]["inputs"]["ipadapter_file"] = ipadapter_file
    workflow["17"]["inputs"]["weight"] = weight
    workflow["17"]["inputs"]["weight_type"] = weight_type
    workflow["17"]["inputs"]["end_at"] = end_at
    workflow["18"]["inputs"]["image"] = input_name(guide_image)
    return workflow


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
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 42)), (228, 224, 214))
    for idx, tile in enumerate(tiles):
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + 42)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", default="velociraptor-mongoliensis")
    parser.add_argument("--reference-image", required=True)
    parser.add_argument("--guide-image", default="tools/comfyui/ComfyUI/input/dino_guides/velociraptor-mongoliensis_shape_plumage.png")
    parser.add_argument("--seed", type=int, action="append", default=[])
    parser.add_argument("--denoise", type=float, action="append", default=[])
    parser.add_argument("--weight", type=float, action="append", default=[])
    parser.add_argument("--weight-type", action="append", default=[])
    parser.add_argument("--end-at", type=float, default=0.82)
    parser.add_argument("--ckpt-name", default="RealVisXL_V5.0_fp16.safetensors")
    parser.add_argument("--ipadapter-file", default="ip-adapter-plus_sdxl_vit-h.safetensors")
    parser.add_argument("--prefix", default="ipadapter_i2i")
    args = parser.parse_args()

    reference = Path(args.reference_image)
    if not reference.is_absolute():
        reference = (Path.cwd() / reference).resolve()
    guide = Path(args.guide_image)
    if not guide.is_absolute():
        guide = (Path.cwd() / guide).resolve()

    input_dir = COMFY_INPUT / "dino_ipadapter"
    input_dir.mkdir(parents=True, exist_ok=True)
    input_reference = input_dir / f"{args.prefix}_reference.png"
    input_guide = input_dir / f"{args.prefix}_guide.png"
    shutil.copy2(reference, input_reference)
    shutil.copy2(guide, input_guide)

    seeds = args.seed or [2026067601, 2026067602]
    denoises = args.denoise or [0.58, 0.66]
    weights = args.weight or [0.45, 0.65]
    weight_types = args.weight_type or ["style and composition"]

    results = []
    copied = []
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    for weight_type in weight_types:
        safe_weight_type = weight_type.replace(" ", "_").replace("-", "_")
        for weight in weights:
            for denoise in denoises:
                for seed in seeds:
                    workflow = configure(
                        load_workflow(TEMPLATE),
                        args.taxon_id,
                        input_reference,
                        input_guide,
                        seed,
                        denoise,
                        weight,
                        weight_type,
                        args.end_at,
                        f"{args.prefix}_{safe_weight_type}",
                        args.ckpt_name,
                        args.ipadapter_file,
                    )
                    queued = queue_prompt(workflow, client_id="dino-atlas-ipadapter-i2i")
                    history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                    for image in output_images_from_history(history):
                        item = {
                            "taxonId": args.taxon_id,
                            "referenceImage": str(reference),
                            "guideImage": str(guide),
                            "seed": seed,
                            "denoise": denoise,
                            "weight": weight,
                            "weightType": weight_type,
                            "image": str(image),
                        }
                        results.append(item)
                        dst = EXPERIMENT_OUT / (
                            f"{args.prefix}_{safe_weight_type}_{args.taxon_id}_seed{seed}_w{int(weight * 100):02d}_d{int(denoise * 100):02d}.png"
                        )
                        shutil.copy2(image, dst)
                        copied.append((dst, f"{weight_type} seed {seed} w{weight:.2f} d{denoise:.2f}"))

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
