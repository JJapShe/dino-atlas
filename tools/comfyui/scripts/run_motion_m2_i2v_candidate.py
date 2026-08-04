import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
COMFY_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = COMFY_DIR / "workflow_templates" / "dino_wan22_ti2v_5b_i2v_api.json"

sys.path.insert(0, str(SCRIPT_DIR))
from comfy_client import queue_prompt, wait_for_history  # noqa: E402


POSITIVE_PROMPT = """Scientific-educational image-to-video. Use the attached approved Oviraptor philoceratops still as the exact identity, anatomy, composition, lighting, and background reference. Exactly one full-body Oviraptor philoceratops: low restrained midline crest, comparatively elongate and deep toothless rostrum, closed beak, compact robust feathered torso, charcoal-gray dorsal plumage, rust throat and neck, pale belly, exactly two forelimbs with three visible fingers on each hand, exactly two hind limbs with stable feet, and one short feathered tail.

The head, entire feathered neck, both sides of the neck root, shoulder girdle, and upper chest remain one continuous living structure in every frame. The cervical column bends smoothly across several points with natural soft-tissue and feather continuity; never rotate from a single hinge. Perform one clear but controlled alert glance: smoothly raise the head about five degrees and turn about four degrees toward the camera, with a subtle distributed S-curve through the neck and slight compression and release of the throat and upper-chest feathers, then return to the starting pose. One subtle blink is allowed. Keep the torso, arms, all fingers, legs, feet, tail, ground shadow, camera, crop, background, lighting, exposure, and color stable. Static camera, no zoom, no cut, source-matched first and last frame."""


NEGATIVE_PROMPT = """decapitation, severed neck, detached head, floating head, neck stump, background visible through neck attachment, cutout puppet, paper-doll rotation, rigid head-and-neck plate, single hinge pivot, neck collar seam, halo, double contour, transparent gap, clean-plate ghost, discontinuous feathers, sliding feather texture, rubber neck, stretched neck, broken neck, abrupt cervical kink, flicker, morphing, identity drift, crest drift, beak warping, eye drift, duplicate eye, extra head, teeth, open mouth, tongue, tall broad Citipati-like crest, short rectangular Citipati-like skull, modern parrot, owl, cassowary, ostrich, long swan neck, gracile Avimimus-like body, extra or missing limbs, fused limbs, extra or missing fingers, one-claw hand, sickle claw, duplicate tail, missing tail, wing flapping, arm motion, tail motion, walking, foot sliding, body translation, camera motion, pan, zoom, crop change, background change, lighting shift, exposure shift, color shift, text, watermark, logo, signature, low quality, blurry, compression artifacts"""


def load_template() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def configure_workflow(args: argparse.Namespace) -> dict:
    workflow = load_template()
    workflow["4"]["inputs"]["text"] = args.positive_prompt
    workflow["5"]["inputs"]["text"] = args.negative_prompt
    workflow["6"]["inputs"]["image"] = args.input_name
    workflow["7"]["inputs"].update(
        {
            "width": args.width,
            "height": args.height,
            "length": args.frames,
            "batch_size": 1,
        }
    )
    workflow["9"]["inputs"].update(
        {
            "seed": args.seed,
            "steps": args.steps,
            "cfg": args.cfg,
            "sampler_name": args.sampler,
            "scheduler": args.scheduler,
            "denoise": args.denoise,
        }
    )
    workflow["11"]["inputs"]["fps"] = args.fps
    workflow["12"]["inputs"]["filename_prefix"] = args.output_prefix
    return workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Queue a deterministic Wan2.2 TI2V 5B Oviraptor I2V review candidate."
    )
    parser.add_argument("--input-name", required=True, help="Path relative to ComfyUI/input")
    parser.add_argument("--output-prefix", required=True, help="Path relative to ComfyUI/output")
    parser.add_argument("--seed", type=int, default=240804041)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--frames", type=int, default=81)
    parser.add_argument("--fps", type=float, default=24)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--cfg", type=float, default=5)
    parser.add_argument("--sampler", default="uni_pc")
    parser.add_argument("--scheduler", default="simple")
    parser.add_argument("--denoise", type=float, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--positive-prompt", default=POSITIVE_PROMPT)
    parser.add_argument("--negative-prompt", default=NEGATIVE_PROMPT)
    parser.add_argument("--record", type=Path, required=True)
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.width % 32 or args.height % 32:
        raise SystemExit("Wan2.2 width and height must be divisible by 32")
    if args.frames < 1 or (args.frames - 1) % 4:
        raise SystemExit("Wan2.2 frame count must be 4n+1")
    if not 0 < args.denoise <= 1:
        raise SystemExit("denoise must be in (0, 1]")


def main() -> None:
    args = parse_args()
    validate_args(args)
    workflow = configure_workflow(args)
    queued = queue_prompt(workflow, client_id="dino-atlas-motion-m2-i2v")
    prompt_id = queued["prompt_id"]
    history = wait_for_history(prompt_id, timeout_seconds=args.timeout_seconds)
    record = {
        "schemaVersion": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "status": history.get("status"),
        "promptId": prompt_id,
        "queueResponse": queued,
        "workflow": workflow,
        "history": history,
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
