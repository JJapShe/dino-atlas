import argparse
import json
import random
from pathlib import Path

from generate_dino_prompt import build_prompt


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "workflow_templates"


def load_template(name):
    return json.loads((TEMPLATES / name).read_text(encoding="utf-8"))


def configure_workflow(workflow, prompt_data, taxon_id, seed=None):
    seed = seed if seed is not None else random.randint(1, 2**48)
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = prompt_data["positivePrompt"]
    workflow["7"]["inputs"]["text"] = prompt_data["negativePrompt"]
    workflow["9"]["inputs"]["filename_prefix"] = f"dino_atlas/{taxon_id}"
    return workflow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", default="tyrannosaurus-rex")
    parser.add_argument("--template", default="dino_sdxl_base_api.json")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    prompt_data = build_prompt(args.taxon_id)
    workflow = configure_workflow(load_template(args.template), prompt_data, args.taxon_id, args.seed)
    output = Path(args.output) if args.output else ROOT / "outputs" / f"{args.taxon_id}.workflow.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
