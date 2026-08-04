import argparse
import hashlib
import json
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parents[2]

sys.path.insert(0, str(SCRIPT_DIR))
from comfy_client import queue_prompt, wait_for_history  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise SystemExit(f"Expected PNG input, got unsupported file: {path}")
        chunk_length = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR" or chunk_length < 8:
            raise SystemExit(f"Invalid PNG IHDR: {path}")
        return struct.unpack(">II", handle.read(8))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_DIR / path


def select_candidate(spec: dict, candidate_id: str) -> dict:
    matches = [item for item in spec.get("candidates", []) if item.get("id") == candidate_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one candidate named {candidate_id!r}; found {len(matches)}")
    return matches[0]


def validate(spec_path: Path, spec: dict, candidate: dict) -> tuple[Path, Path, dict]:
    settings = {**spec.get("settings", {}), **candidate.get("settings", {})}
    required_settings = (
        "width",
        "height",
        "frames",
        "fps",
        "steps",
        "cfg",
        "sampler",
        "scheduler",
        "shift",
        "denoise",
    )
    missing_settings = [key for key in required_settings if key not in settings]
    if missing_settings:
        raise SystemExit(f"Missing settings: {', '.join(missing_settings)}")
    if settings["width"] % 32 or settings["height"] % 32:
        raise SystemExit("Wan2.2 width and height must be divisible by 32")
    if settings["frames"] < 1 or (settings["frames"] - 1) % 4:
        raise SystemExit("Wan2.2 frame count must be 4n+1")
    if not 0 < settings["denoise"] <= 1:
        raise SystemExit("denoise must be in (0, 1]")
    effective_duration = settings["frames"] / settings["fps"]
    if "durationSeconds" in settings and abs(settings["durationSeconds"] - effective_duration) > 0.000001:
        raise SystemExit(
            f"durationSeconds {settings['durationSeconds']} does not match frames/fps {effective_duration}"
        )
    if not candidate.get("positivePrompt") or not candidate.get("negativePrompt"):
        raise SystemExit("Each candidate must provide species-specific positive and negative prompts")

    comfy_root = Path(spec["comfyUiRoot"])
    input_path = comfy_root / "input" / Path(candidate["inputName"])
    if not input_path.is_file():
        raise SystemExit(f"ComfyUI input does not exist: {input_path}")
    source_hash = sha256_file(input_path)
    if source_hash != candidate["sourcePosterSha256"]:
        raise SystemExit(
            f"Input hash mismatch for {input_path}: expected {candidate['sourcePosterSha256']}, got {source_hash}"
        )
    source_width, source_height = png_dimensions(input_path)
    source_ratio = source_width / source_height
    output_ratio = settings["width"] / settings["height"]
    relative_ratio_delta = abs(source_ratio - output_ratio) / output_ratio
    if relative_ratio_delta > 0.01:
        raise SystemExit(
            f"Input aspect ratio {source_width}x{source_height} does not match output "
            f"{settings['width']}x{settings['height']} within 1%; refusing implicit crop"
        )

    template_path = resolve_repo_path(spec["workflowTemplate"])
    if not template_path.is_file():
        raise SystemExit(f"Workflow template does not exist: {template_path}")
    if spec_path.resolve() == template_path.resolve():
        raise SystemExit("Spec and workflow template must be different files")
    return input_path, template_path, settings


def configure_workflow(template_path: Path, spec: dict, candidate: dict, settings: dict) -> dict:
    workflow = load_json(template_path)
    common_negative = spec.get("commonNegativePrompt", "").strip()
    species_negative = candidate["negativePrompt"].strip()
    negative_prompt = ", ".join(value for value in (common_negative, species_negative) if value)
    workflow["4"]["inputs"]["text"] = candidate["positivePrompt"].strip()
    workflow["5"]["inputs"]["text"] = negative_prompt
    workflow["6"]["inputs"]["image"] = candidate["inputName"]
    workflow["7"]["inputs"].update(
        {
            "width": settings["width"],
            "height": settings["height"],
            "length": settings["frames"],
            "batch_size": 1,
        }
    )
    workflow["8"]["inputs"]["shift"] = settings["shift"]
    workflow["9"]["inputs"].update(
        {
            "seed": candidate["seed"],
            "steps": settings["steps"],
            "cfg": settings["cfg"],
            "sampler_name": settings["sampler"],
            "scheduler": settings["scheduler"],
            "denoise": settings["denoise"],
        }
    )
    workflow["11"]["inputs"]["fps"] = settings["fps"]
    workflow["12"]["inputs"]["filename_prefix"] = candidate["outputPrefix"]
    return workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Queue one spec-controlled Wan2.2 TI2V 5B long-motion review candidate."
    )
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec_path = args.spec.resolve()
    spec = load_json(spec_path)
    candidate = select_candidate(spec, args.candidate)
    input_path, template_path, settings = validate(spec_path, spec, candidate)
    workflow = configure_workflow(template_path, spec, candidate, settings)
    queued_at = datetime.now(timezone.utc)
    queued = queue_prompt(workflow, client_id="dino-atlas-motion-m2-i2v-long")
    prompt_id = queued["prompt_id"]
    print(
        json.dumps(
            {
                "queued": candidate["id"],
                "promptId": prompt_id,
                "frames": settings["frames"],
                "fps": settings["fps"],
                "durationSeconds": settings["frames"] / settings["fps"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    history = wait_for_history(prompt_id, timeout_seconds=args.timeout_seconds)
    completed_at = datetime.now(timezone.utc)
    record = {
        "schemaVersion": 2,
        "candidateId": candidate["id"],
        "taxonId": candidate["taxonId"],
        "queuedAt": queued_at.isoformat(),
        "completedAt": completed_at.isoformat(),
        "elapsedSeconds": round((completed_at - queued_at).total_seconds(), 3),
        "status": history.get("status"),
        "promptId": prompt_id,
        "queueResponse": queued,
        "provenance": {
            "spec": str(spec_path),
            "specSha256": sha256_file(spec_path),
            "template": str(template_path),
            "templateSha256": sha256_file(template_path),
            "runner": str(Path(__file__).resolve()),
            "runnerSha256": sha256_file(Path(__file__).resolve()),
            "comfyInput": str(input_path),
            "comfyInputSha256": sha256_file(input_path),
            "comfyInputWidth": png_dimensions(input_path)[0],
            "comfyInputHeight": png_dimensions(input_path)[1],
            "outputAspectWidth": settings["width"],
            "outputAspectHeight": settings["height"],
            "sourcePoster": candidate["sourcePoster"],
            "sourcePosterSha256": candidate["sourcePosterSha256"],
            "sourceLicense": candidate["sourceLicense"],
            "sourceReviewStatus": candidate["sourceReviewStatus"],
        },
        "runConfig": {
            **settings,
            "effectiveDurationSeconds": settings["frames"] / settings["fps"],
            "seed": candidate["seed"],
            "inputName": candidate["inputName"],
            "outputPrefix": candidate["outputPrefix"],
            "positivePrompt": workflow["4"]["inputs"]["text"],
            "negativePrompt": workflow["5"]["inputs"]["text"],
        },
        "workflow": workflow,
        "history": history,
    }
    record_path = resolve_repo_path(candidate["record"])
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "completed": candidate["id"],
                "promptId": prompt_id,
                "elapsedSeconds": record["elapsedSeconds"],
                "record": str(record_path),
                "status": record["status"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
