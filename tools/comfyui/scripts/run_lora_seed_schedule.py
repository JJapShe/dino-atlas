import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history


ROOT = Path(__file__).resolve().parents[1]
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_base_api.json"
DEFAULT_SCHEDULE = ROOT / "lora_training" / "dromaeosaur_feathered" / "synthetic_prompt_schedule.json"
EXPERIMENT_OUT = ROOT / "outputs"


EXTRA_NEGATIVE = (
    "low quality, deformed anatomy, bad legs, missing legs, extra toes, extra claws, extra tail, "
    "tail split, tail artifact, cropped feet, cropped tail, hidden feet, giant monster, Jurassic Park style, "
    "smooth naked scales, plastic toy, modern bird body, ostrich body, eagle wings, spread wings"
)


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def configure(workflow, positive, negative, seed, prefix, ckpt_name, width, height, steps, cfg):
    workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["steps"] = steps
    workflow["3"]["inputs"]["cfg"] = cfg
    workflow["5"]["inputs"]["width"] = width
    workflow["5"]["inputs"]["height"] = height
    workflow["6"]["inputs"]["text"] = positive
    workflow["7"]["inputs"]["text"] = negative
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}"
    return workflow


def selected_prompts(schedule, ids, limit):
    prompts = schedule["prompts"]
    if ids:
        wanted = set(ids)
        prompts = [prompt for prompt in prompts if prompt["id"] in wanted]
        missing = sorted(wanted - {prompt["id"] for prompt in prompts})
        if missing:
            raise ValueError(f"Prompt id(s) not found in schedule: {', '.join(missing)}")
    if limit:
        prompts = prompts[:limit]
    return prompts


def make_prompt(schedule, prompt):
    positive = f"{schedule['basePositive']}, {prompt['variation']}"
    negative = f"{schedule['baseNegative']}, {EXTRA_NEGATIVE}"
    return positive, negative


def make_contact_sheet(items, output, title, thumb_w=360, thumb_h=240):
    label_h = 64
    header_h = 62
    cols = min(3, max(1, len(items)))
    rows = max(1, (len(items) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * thumb_w, header_h + rows * (thumb_h + label_h)), (228, 224, 214))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, sheet.width, header_h), fill=(22, 55, 42))
    draw.text((14, 12), title, fill=(245, 243, 236), font=font)
    draw.text((14, 36), "Synthetic candidates for review only; not training-approved until manually gated.", fill=(220, 225, 214), font=font)

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image = Image.open(item["path"]).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        tile_draw = ImageDraw.Draw(tile)
        tile_draw.text((8, thumb_h + 8), f"{item['promptId']} seed {item['seed']}", fill=(135, 64, 48), font=font)
        tile_draw.text((8, thumb_h + 30), item["variation"][:58], fill=(42, 39, 35), font=font)
        x = (idx % cols) * thumb_w
        y = header_h + (idx // cols) * (thumb_h + label_h)
        sheet.paste(tile, (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", default=str(DEFAULT_SCHEDULE))
    parser.add_argument("--prompt-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed-base", type=int, default=2026062800)
    parser.add_argument("--ckpt-name", default="RealVisXL_V5.0_fp16.safetensors")
    parser.add_argument("--width", type=int, default=1152)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--steps", type=int, default=32)
    parser.add_argument("--cfg", type=float, default=4.6)
    parser.add_argument("--prefix", default="dromaeosaur_lora_seed_v1")
    args = parser.parse_args()

    schedule_path = Path(args.schedule)
    if not schedule_path.is_absolute():
        schedule_path = (Path.cwd() / schedule_path).resolve()
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    prompts = selected_prompts(schedule, args.prompt_id, args.limit)

    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    results = []
    sheet_items = []
    for index, prompt in enumerate(prompts, start=1):
        seed = args.seed_base + index
        positive, negative = make_prompt(schedule, prompt)
        workflow = configure(
            load_workflow(TEMPLATE),
            positive,
            negative,
            seed,
            f"{args.prefix}_{prompt['id']}",
            args.ckpt_name,
            args.width,
            args.height,
            args.steps,
            args.cfg,
        )
        queued = queue_prompt(workflow, client_id="dino-atlas-lora-seed-schedule")
        history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
        for image in output_images_from_history(history):
            dst = EXPERIMENT_OUT / f"{args.prefix}_{prompt['id']}_seed{seed}.png"
            shutil.copy2(image, dst)
            item = {
                "datasetId": schedule["datasetId"],
                "trigger": schedule["trigger"],
                "promptId": prompt["id"],
                "variation": prompt["variation"],
                "seed": seed,
                "ckptName": args.ckpt_name,
                "positive": positive,
                "negative": negative,
                "image": str(dst),
                "decision": "needs_review",
            }
            results.append(item)
            sheet_items.append({"path": dst, "promptId": prompt["id"], "variation": prompt["variation"], "seed": seed})

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sheet_path = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(sheet_items, sheet_path, f"{schedule['datasetId']} synthetic seed candidates")
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet_path), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
