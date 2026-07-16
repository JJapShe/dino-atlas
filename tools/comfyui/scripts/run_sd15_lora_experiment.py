import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from comfy_client import load_workflow, queue_prompt, wait_for_history


ROOT = Path(__file__).resolve().parents[1]
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"
TEMPLATE = ROOT / "workflow_templates" / "dino_sd15_lora_api.json"
EXPERIMENT_OUT = ROOT / "outputs"


TAXA = {
    "velociraptor-mongoliensis": {
        "lora": "Velociraptor_Dino.safetensors",
        "trigger": "Velociraptor_Dino",
        "positive": (
            "Velociraptor_Dino, naturalistic Velociraptor mongoliensis, small turkey-sized feathered dromaeosaur dinosaur, "
            "full body lateral side view, one animal, long stiff tail, narrow toothed skull, dense downy feathered torso, "
            "folded wing-like feathered arms held close to the ribs, arms folded downward not spread for flight, "
            "large raised sickle claw on second toe, clean natural history paleoart, plain pale background, "
            "earth tone colors, clear feet, no text"
        ),
        "negative": (
            "Jurassic Park, movie monster, giant raptor, human sized, ostrich, emu, naked scaly arms, unfeathered body, "
            "T rex head, tyrannosaur body, smooth naked skin, bald arms, porcupine quills, dorsal spikes, mohawk crest, "
            "pangolin scales, armored scale rows, bird beak, toothless beak, spread wings, flying bird, extra head, extra limbs, "
            "cropped feet, cropped tail, text, labels, watermark, signature, logo, "
            "cartoon, anime, toy, plastic"
        ),
    },
    "ankylosaurus-magniventris": {
        "lora": "Ankylosaurus_Dinosaur.safetensors",
        "trigger": "Ankylosaurus_Dinosaur",
        "positive": (
            "Ankylosaurus_Dinosaur, naturalistic Ankylosaurus magniventris, low wide armored quadruped dinosaur, "
            "full body lateral side view, one animal, flat low back, bony osteoderms across the back, large heavy tail club, "
            "short sturdy legs, clean natural history paleoart, plain pale background, earth tone colors, no text"
        ),
        "negative": (
            "stegosaurus plates, tall dorsal plates, vertical back plates, missing tail club, turtle shell, tortoise shell, "
            "bipedal stance, theropod body, long neck, extra head, extra limbs, cropped feet, cropped tail, text, labels, "
            "watermark, signature, logo, cartoon, anime, toy, plastic"
        ),
    },
}


def configure(workflow, taxon_id, seed, strength, prefix):
    config = TAXA[taxon_id]
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = config["positive"]
    workflow["7"]["inputs"]["text"] = config["negative"]
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{prefix}_{taxon_id}_s{int(strength * 100):02d}"
    workflow["10"]["inputs"]["lora_name"] = config["lora"]
    workflow["10"]["inputs"]["strength_model"] = strength
    workflow["10"]["inputs"]["strength_clip"] = strength
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
    for x0, x1 in [(0, 190), (w - 230, w)]:
        sample = image.crop((max(0, x0), h - 90, min(w, x1), h - 65)).resize((1, 1))
        draw.rectangle((x0, h - 65, x1, h), fill=sample.getpixel((0, 0)))
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
    parser.add_argument("--taxon-id", action="append", choices=sorted(TAXA), required=True)
    parser.add_argument("--seed", action="append", type=int, default=[])
    parser.add_argument("--strength", action="append", type=float, default=[])
    parser.add_argument("--prefix", default="sd15_lora")
    args = parser.parse_args()

    seeds = args.seed or [2026065001, 2026065002]
    strengths = args.strength or [0.65, 0.9]
    results = []
    copied = []
    for taxon_id in args.taxon_id:
        for strength in strengths:
            for seed in seeds:
                workflow = configure(load_workflow(TEMPLATE), taxon_id, seed, strength, args.prefix)
                queued = queue_prompt(workflow, client_id="dino-atlas-sd15-lora")
                history = wait_for_history(queued["prompt_id"], timeout_seconds=900)
                for image in output_images_from_history(history):
                    item = {"taxonId": taxon_id, "seed": seed, "strength": strength, "image": str(image)}
                    results.append(item)
                    dst = EXPERIMENT_OUT / f"{args.prefix}_{taxon_id}_seed{seed}_s{int(strength * 100):02d}.png"
                    shutil.copy2(image, dst)
                    clean_lower_corners(dst)
                    copied.append((dst, f"{taxon_id} seed {seed} strength {strength:.2f}"))

    EXPERIMENT_OUT.mkdir(parents=True, exist_ok=True)
    result_path = EXPERIMENT_OUT / f"{args.prefix}-results.json"
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = EXPERIMENT_OUT / f"{args.prefix}-contact-sheet.png"
    make_contact_sheet(copied, sheet)
    print(json.dumps({"results": str(result_path), "contactSheet": str(sheet), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
