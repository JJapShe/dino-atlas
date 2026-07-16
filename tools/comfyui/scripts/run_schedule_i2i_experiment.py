import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history


ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = ROOT / "ComfyUI" / "input"
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
TEMPLATE = ROOT / "workflow_templates" / "dino_sdxl_i2i_api.json"
EXPERIMENT_OUT = ROOT / "outputs"

EXTRA_POSITIVE = (
    "naturalistic museum-quality educational paleoart, full body readable side silhouette, "
    "diagnostic anatomy preserved, realistic soft daylight, no diagram labels, unsigned finished image"
)

EXTRA_NEGATIVE = (
    "text, labels, logo, watermark, signature, diagram annotation, source guide text, corner marks, "
    "flat vector art, simple icon, cartoon mascot, naked generic theropod, smooth scaly movie raptor, "
    "hidden feet, cropped tail, cropped head, extra legs, duplicate tail"
)


def output_images_from_history(history):
    images = []
    for node in history.get("outputs", {}).values():
        for image in node.get("images", []):
            images.append(COMFY_OUTPUT / image["subfolder"] / image["filename"])
    return images


def selected_prompts(schedule, ids, limit):
    prompts = schedule.get("prompts", [])
    if ids:
        wanted = set(ids)
        prompts = [prompt for prompt in prompts if prompt["id"] in wanted]
        missing = sorted(wanted - {prompt["id"] for prompt in prompts})
        if missing:
            raise ValueError(f"Prompt id(s) not found in schedule: {', '.join(missing)}")
    if limit:
        prompts = prompts[:limit]
    return prompts


def stage_source_image(source_path, prefix):
    source = Path(source_path)
    if not source.is_absolute():
        source = (Path.cwd() / source).resolve()
    staged_dir = COMFY_INPUT / "dino_schedule_i2i_sources"
    staged_dir.mkdir(parents=True, exist_ok=True)
    staged = staged_dir / f"{prefix}{source.suffix.lower()}"
    shutil.copy2(source, staged)
    return str(staged.relative_to(COMFY_INPUT)).replace("\\", "/")


def make_prompt(schedule, prompt):
    positive = f"{schedule['basePositive']}, {prompt['variation']}, {EXTRA_POSITIVE}"
    negative = f"{schedule['baseNegative']}, {EXTRA_NEGATIVE}"
    return positive, negative


def configure(workflow, positive, negative, source_name, seed, denoise, prefix, ckpt_name=None):
    if ckpt_name:
        workflow["4"]["inputs"]["ckpt_name"] = ckpt_name
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["denoise"] = denoise
    workflow["6"]["inputs"]["text"] = positive
    workflow["7"]["inputs"]["text"] = negative
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}_d{int(denoise * 100):02d}"
    workflow["12"]["inputs"]["image"] = source_name
    return workflow


def clean_lower_corners(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    draw = ImageDraw.Draw(image)
    for x0, x1 in [(0, 260), (w - 300, w)]:
        sample_box = (max(0, x0), h - 120, min(w, x1), h - 95)
        sample = image.crop(sample_box).resize((1, 1))
        draw.rectangle((x0, h - 90, x1, h), fill=sample.getpixel((0, 0)))
    image.save(path)


def make_contact_sheet(items, output, thumb_w=384, thumb_h=256):
    if not items:
        return
    label_h = 54
    cols = min(2, len(items))
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    font = ImageFont.load_default()
    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image = Image.open(item["path"]).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        tile.paste(image, ((thumb_w - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 8), f"{item['promptId']} seed {item['seed']} d{item['denoise']:.2f}", fill=(31, 31, 28), font=font)
        draw.text((10, thumb_h + 29), item["variation"][:58], fill=(91, 84, 74), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--source-image", required=True)
    parser.add_argument("--prompt-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed", action="append", type=int, default=[])
    parser.add_argument("--denoise", action="append", type=float, default=[])
    parser.add_argument("--prefix", default="schedule_i2i")
    parser.add_argument("--ckpt-name")
    parser.add_argument("--clean-corners", action="store_true")
    args = parser.parse_args()

    schedule_path = Path(args.schedule)
    if not schedule_path.is_absolute():
        schedule_path = (Path.cwd() / schedule_path).resolve()
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    prompts = selected_prompts(schedule, args.prompt_id, args.limit)
    seeds = args.seed or [2026072401, 2026072402]
    denoises = args.denoise or [0.52, 0.62]
    source_name = stage_source_image(args.source_image, args.prefix)

    results = []
    sheet_items = []
    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    for prompt in prompts:
        positive, negative = make_prompt(schedule, prompt)
        for denoise in denoises:
            for seed in seeds:
                workflow = configure(
                    load_workflow(TEMPLATE),
                    positive,
                    negative,
                    source_name,
                    seed,
                    denoise,
                    f"{args.prefix}_{prompt['id']}_seed{seed}",
                    args.ckpt_name,
                )
                queued = queue_prompt(workflow, client_id="dino-atlas-schedule-i2i")
                history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                for image in output_images_from_history(history):
                    dst = EXPERIMENT_OUT / f"{args.prefix}_{prompt['id']}_seed{seed}_d{int(denoise * 100):02d}.png"
                    shutil.copy2(image, dst)
                    if args.clean_corners:
                        clean_lower_corners(dst)
                    item = {
                        "datasetId": schedule["datasetId"],
                        "trigger": schedule["trigger"],
                        "promptId": prompt["id"],
                        "variation": prompt["variation"],
                        "seed": seed,
                        "denoise": denoise,
                        "ckptName": args.ckpt_name,
                        "sourceImage": args.source_image,
                        "positive": positive,
                        "negative": negative,
                        "image": str(dst),
                        "decision": "needs_review",
                    }
                    results.append(item)
                    sheet_items.append(
                        {
                            "path": dst,
                            "promptId": prompt["id"],
                            "variation": prompt["variation"],
                            "seed": seed,
                            "denoise": denoise,
                        }
                    )

    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sheet_path = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(sheet_items, sheet_path)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet_path), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
