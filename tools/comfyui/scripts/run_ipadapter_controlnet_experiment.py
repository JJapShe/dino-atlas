import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history
from generate_dino_prompt import build_prompt


ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = ROOT / "ComfyUI" / "input"
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_ipadapter_controlnet_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def input_name(path):
    return str(path.relative_to(COMFY_INPUT)).replace("\\", "/")


def make_line_control(source, output):
    image = Image.open(source).convert("RGB")
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 255 if p > 18 else 0)
    edges = edges.filter(ImageFilter.MaxFilter(3))
    output.parent.mkdir(parents=True, exist_ok=True)
    edges.convert("RGB").save(output)
    return output


def configure(
    workflow,
    taxon_id,
    reference_image,
    control_image,
    seed,
    ip_weight,
    ip_weight_type,
    control_strength,
    control_end,
    prefix,
    ckpt_name,
    ipadapter_file,
    lora_name=None,
    lora_strength=None,
    clip_strength=None,
):
    prompt = build_prompt(taxon_id)
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    if lora_name:
        workflow["20"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["4", 0],
                "clip": ["4", 1],
                "lora_name": lora_name,
                "strength_model": lora_strength,
                "strength_clip": clip_strength,
            },
        }
        workflow["6"]["inputs"]["clip"] = ["20", 1]
        workflow["7"]["inputs"]["clip"] = ["20", 1]
        workflow["17"]["inputs"]["model"] = ["20", 0]
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = (
        prompt["positivePrompt"]
        + ", use the reference image only for natural color palette, skin texture, lighting, and habitat mood, "
        "follow the control guide for the full body silhouette and pose, clean readable legs and feet, "
        "single coherent tail, no extra appendages"
    )
    workflow["7"]["inputs"]["text"] = (
        prompt["negativePrompt"]
        + ", extra tail, second tail, tail under body, duplicate rear limb, extra rear limb, "
        "long curved appendage below body, detached body line, tail thread, black brush stroke under tail, "
        "printed text, watermark, signature"
    )
    workflow["9"]["inputs"]["filename_prefix"] = (
        f"dino_atlas/{prefix}_{taxon_id}_iw{int(ip_weight * 100):02d}_cs{int(control_strength * 100):02d}"
        + (f"_l{int((lora_strength or 0) * 100):02d}" if lora_name else "")
    )
    workflow["12"]["inputs"]["image"] = input_name(reference_image)
    workflow["15"]["inputs"]["ipadapter_file"] = ipadapter_file
    workflow["16"]["inputs"]["strength"] = control_strength
    workflow["16"]["inputs"]["end_percent"] = control_end
    workflow["17"]["inputs"]["weight"] = ip_weight
    workflow["17"]["inputs"]["weight_type"] = ip_weight_type
    workflow["18"]["inputs"]["image"] = input_name(control_image)
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
    parser.add_argument("--control-source", default="tools/comfyui/ComfyUI/input/dino_guides/velociraptor-mongoliensis_shape_plumage.png")
    parser.add_argument("--seed", type=int, action="append", default=[])
    parser.add_argument("--ip-weight", type=float, action="append", default=[])
    parser.add_argument("--ip-weight-type", action="append", default=[])
    parser.add_argument("--control-strength", type=float, action="append", default=[])
    parser.add_argument("--control-end", type=float, default=0.68)
    parser.add_argument("--ckpt-name", default="RealVisXL_V5.0_fp16.safetensors")
    parser.add_argument("--ipadapter-file", default="ip-adapter-plus_sdxl_vit-h.safetensors")
    parser.add_argument("--lora-name")
    parser.add_argument("--lora-strength", type=float, default=0.14)
    parser.add_argument("--clip-strength", type=float)
    parser.add_argument("--prefix", default="ipadapter_controlnet")
    args = parser.parse_args()

    reference = Path(args.reference_image)
    if not reference.is_absolute():
        reference = (Path.cwd() / reference).resolve()
    control_source = Path(args.control_source)
    if not control_source.is_absolute():
        control_source = (Path.cwd() / control_source).resolve()

    input_dir = COMFY_INPUT / "dino_ipadapter"
    input_dir.mkdir(parents=True, exist_ok=True)
    input_reference = input_dir / f"{args.prefix}_reference.png"
    input_control = input_dir / f"{args.prefix}_control.png"
    shutil.copy2(reference, input_reference)
    make_line_control(control_source, input_control)

    seeds = args.seed or [2026067901, 2026067902]
    ip_weights = args.ip_weight or [0.35, 0.5]
    ip_weight_types = args.ip_weight_type or ["style transfer"]
    control_strengths = args.control_strength or [0.45, 0.6]

    results = []
    copied = []
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_control, EXPERIMENT_OUT / f"{args.prefix}_control.png")
    clip_strength = args.clip_strength if args.clip_strength is not None else min(args.lora_strength, 0.1)
    for ip_weight_type in ip_weight_types:
        safe_weight_type = ip_weight_type.replace(" ", "_").replace("-", "_")
        for ip_weight in ip_weights:
            for control_strength in control_strengths:
                for seed in seeds:
                    workflow = configure(
                        load_workflow(TEMPLATE),
                        args.taxon_id,
                        input_reference,
                        input_control,
                        seed,
                        ip_weight,
                        ip_weight_type,
                        control_strength,
                        args.control_end,
                        f"{args.prefix}_{safe_weight_type}",
                        args.ckpt_name,
                        args.ipadapter_file,
                        args.lora_name,
                        args.lora_strength,
                        clip_strength,
                    )
                    queued = queue_prompt(workflow, client_id="dino-atlas-ipadapter-controlnet")
                    history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                    for image in output_images_from_history(history):
                        item = {
                            "taxonId": args.taxon_id,
                            "referenceImage": str(reference),
                            "controlSource": str(control_source),
                            "seed": seed,
                            "ipWeight": ip_weight,
                            "ipWeightType": ip_weight_type,
                            "controlStrength": control_strength,
                            "lora": args.lora_name,
                            "loraStrength": args.lora_strength if args.lora_name else None,
                            "clipStrength": clip_strength if args.lora_name else None,
                            "image": str(image),
                        }
                        results.append(item)
                        dst = EXPERIMENT_OUT / (
                            f"{args.prefix}_{safe_weight_type}_{args.taxon_id}_seed{seed}_iw{int(ip_weight * 100):02d}_cs{int(control_strength * 100):02d}.png"
                            if not args.lora_name
                            else f"{args.prefix}_{safe_weight_type}_{args.taxon_id}_seed{seed}_iw{int(ip_weight * 100):02d}_cs{int(control_strength * 100):02d}_l{int(args.lora_strength * 100):02d}.png"
                        )
                        shutil.copy2(image, dst)
                        copied.append((dst, f"{ip_weight_type} seed {seed} iw{ip_weight:.2f} cs{control_strength:.2f}"))

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
