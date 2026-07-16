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
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_controlnet_api.json"
LORA_TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_lora_controlnet_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


def make_canny_like(source, output):
    image = Image.open(source).convert("L")
    image = image.filter(ImageFilter.FIND_EDGES)
    image = image.point(lambda p: 255 if p > 22 else 0)
    image = image.filter(ImageFilter.MaxFilter(3))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output)


def configure(
    workflow,
    taxon_id,
    control_name,
    seed,
    strength,
    end_percent,
    prefix,
    ckpt_name=None,
    lora_name=None,
    lora_strength=None,
    clip_strength=None,
):
    prompt = build_prompt(taxon_id)
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    if lora_name:
        workflow["10"]["inputs"]["lora_name"] = lora_name
        workflow["10"]["inputs"]["strength_model"] = lora_strength
        workflow["10"]["inputs"]["strength_clip"] = clip_strength
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = (
        prompt["positivePrompt"]
        + ", naturalistic side-view paleoart, detailed body texture, realistic dinosaur anatomy, "
        "wide side-view composition, full body visible, entire tail and head fully inside the frame, "
        "animal fits comfortably in frame with ground contact visible, clean pale background, no diagram style"
    )
    workflow["7"]["inputs"]["text"] = (
        prompt["negativePrompt"]
        + ", flat vector art, simple icon, silhouette-only, paper cutout, line drawing, black outline, "
        "bird silhouette, flying pose, spread wings, close crop, cropped tail, cropped head, cropped feet, "
        "animal cut off by image edge"
    )
    workflow["9"]["inputs"]["filename_prefix"] = (
        f"dino_atlas/{prefix}_{taxon_id}_s{int(strength * 100):02d}_e{int(end_percent * 100):02d}"
        + (f"_l{int((lora_strength or 0) * 100):02d}" if lora_name else "")
    )
    workflow["12"]["inputs"]["image"] = control_name
    workflow["16"]["inputs"]["strength"] = strength
    workflow["16"]["inputs"]["end_percent"] = end_percent
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
    parser.add_argument("--taxon-id", default="velociraptor-mongoliensis")
    parser.add_argument("--source-image", required=True)
    parser.add_argument("--seed", type=int, action="append", default=[])
    parser.add_argument("--strength", type=float, action="append", default=[])
    parser.add_argument("--end-percent", type=float, action="append", default=[])
    parser.add_argument("--prefix", default="controlnet")
    parser.add_argument("--ckpt-name")
    parser.add_argument("--lora-name")
    parser.add_argument("--lora-strength", type=float, default=0.12)
    parser.add_argument("--clip-strength", type=float)
    parser.add_argument("--clean-corners", action="store_true")
    args = parser.parse_args()

    seeds = args.seed or [2026065701, 2026065702]
    strengths = args.strength or [0.45, 0.68]
    end_percents = args.end_percent or [0.56, 0.72]

    input_dir = COMFY_INPUT / "dino_control"
    source = Path(args.source_image)
    control_path = input_dir / f"{args.taxon_id}_canny.png"
    make_canny_like(source, control_path)
    control_name = f"dino_control/{control_path.name}"

    results = []
    copied = []
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    template = LORA_TEMPLATE if args.lora_name else TEMPLATE
    clip_strength = args.clip_strength if args.clip_strength is not None else min(args.lora_strength, 0.1)
    for seed in seeds:
        for strength in strengths:
            for end_percent in end_percents:
                workflow = configure(
                    load_workflow(template),
                    args.taxon_id,
                    control_name,
                    seed,
                    strength,
                    end_percent,
                    args.prefix,
                    args.ckpt_name,
                    args.lora_name,
                    args.lora_strength,
                    clip_strength,
                )
                queued = queue_prompt(workflow, client_id="dino-atlas-controlnet")
                history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                for image in output_images_from_history(history):
                    item = {
                        "taxonId": args.taxon_id,
                        "seed": seed,
                        "strength": strength,
                        "endPercent": end_percent,
                        "controlImage": str(control_path),
                        "lora": args.lora_name,
                        "loraStrength": args.lora_strength if args.lora_name else None,
                        "clipStrength": clip_strength if args.lora_name else None,
                        "image": str(image),
                    }
                    results.append(item)
                    dst = (
                        EXPERIMENT_OUT
                        / (
                            f"{args.prefix}_{args.taxon_id}_seed{seed}_s{int(strength * 100):02d}_e{int(end_percent * 100):02d}"
                            + (f"_l{int(args.lora_strength * 100):02d}" if args.lora_name else "")
                            + ".png"
                        )
                    )
                    shutil.copy2(image, dst)
                    if args.clean_corners:
                        clean_lower_corners(dst)
                    copied.append((dst, f"seed {seed} s{strength:.2f} e{end_percent:.2f}"))

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "controlImage": str(control_path), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
