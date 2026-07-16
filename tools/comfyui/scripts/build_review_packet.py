import argparse
import json
from pathlib import Path

from generate_dino_prompt import build_prompt


ROOT = Path(__file__).resolve().parents[1]
COMFY_OUTPUT = ROOT / "ComfyUI" / "output"


def build_review_packet(taxon_id, image_path):
    prompt_data = build_prompt(taxon_id)
    image = Path(image_path)
    if not image.is_absolute():
        image = (COMFY_OUTPUT / image).resolve()

    return {
        "taxonId": taxon_id,
        "imagePath": str(image),
        "decision": "needs_review",
        "blockingRules": prompt_data["anatomyRules"].get("rejectIf", []),
        "requiredTraits": prompt_data["anatomyRules"].get("mustHave", []),
        "reviewChecklist": prompt_data["reviewChecklist"],
        "visionJudgePrompt": (
            "You are reviewing a dinosaur reconstruction for educational use. "
            "Return strict JSON with keys: approved, reasons, visibleIssues, confidence. "
            "Reject the image if any blocking rule is visible or if the anatomy cannot be verified. "
            "For Tyrannosaurus rex, each visible hand must have exactly two fingers; "
            "three or more fingers on a visible hand is an automatic rejection."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxon-id", default="tyrannosaurus-rex")
    parser.add_argument("--image", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    packet = build_review_packet(args.taxon_id, args.image)
    output = Path(args.output) if args.output else ROOT / "outputs" / f"{args.taxon_id}.review_packet.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
