import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = ROOT / "assets" / "dinosaurs" / "curated" / "review-decisions.json"
CURATED_MANIFEST = ROOT / "assets" / "dinosaurs" / "curated" / "curated-image-library.json"

VALID_DECISIONS = {"approved", "pending", "rejected", ""}


def rel(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_decisions(data):
    manual = data.get("manualCandidateSelections") or {}
    decisions = data.get("candidateReviewDecisions") or {}
    normalized = {
        "schema": "dino-atlas-review-decisions-v1",
        "exportedAt": data.get("exportedAt"),
        "manualCandidateSelections": {},
        "candidateReviewDecisions": {},
        "taxa": data.get("taxa") or {},
    }

    for taxon, source in manual.items():
        if isinstance(source, str) and source:
            normalized["manualCandidateSelections"][taxon] = source

    for taxon, taxon_decisions in decisions.items():
        if not isinstance(taxon_decisions, dict):
            continue
        clean = {}
        for source, decision in taxon_decisions.items():
            if decision in VALID_DECISIONS and decision:
                clean[source] = decision
        if clean:
            normalized["candidateReviewDecisions"][taxon] = clean

    return normalized


def annotate_item(item, selected_source, taxon_decisions):
    source = item.get("source", "")
    item["selected"] = bool(selected_source and source == selected_source)
    item["decision"] = taxon_decisions.get(source, "")
    return item


def apply_to_manifest(curated, decisions):
    manual = decisions.get("manualCandidateSelections", {})
    all_decisions = decisions.get("candidateReviewDecisions", {})
    summary = {
        "selected": 0,
        "approved": 0,
        "pending": 0,
        "rejected": 0,
    }

    for taxon, taxon_data in curated.get("taxa", {}).items():
        selected_source = manual.get(taxon, "")
        taxon_decisions = all_decisions.get(taxon, {})
        taxon_data["selectedPrimary"] = selected_source
        taxon_data["reviewDecisionCount"] = {
            "approved": 0,
            "pending": 0,
            "rejected": 0,
        }

        for group_name in ("finalCandidates", "referenceItems"):
            for item in taxon_data.get(group_name, []):
                annotate_item(item, selected_source, taxon_decisions)
                if item.get("selected"):
                    summary["selected"] += 1
                decision = item.get("decision")
                if decision in taxon_data["reviewDecisionCount"]:
                    taxon_data["reviewDecisionCount"][decision] += 1
                    summary[decision] += 1

    curated["reviewDecisionSource"] = rel(DEFAULT_INPUT)
    curated["reviewDecisionSummary"] = summary
    return curated, summary


def main():
    parser = argparse.ArgumentParser(
        description="Apply exported Dino Atlas review decisions to the curated image library manifest."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to dino-atlas-review-decisions.json downloaded from the review UI.",
    )
    parser.add_argument(
        "--decisions-out",
        default=str(DEFAULT_INPUT),
        help="Project review-decisions.json path to update.",
    )
    parser.add_argument(
        "--manifest",
        default=str(CURATED_MANIFEST),
        help="Curated image library manifest to annotate.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    decisions_out = Path(args.decisions_out)
    manifest_path = Path(args.manifest)

    decisions = normalize_decisions(load_json(input_path))
    curated = load_json(manifest_path)
    curated, summary = apply_to_manifest(curated, decisions)

    write_json(decisions_out, decisions)
    write_json(manifest_path, curated)

    print(
        json.dumps(
            {
                "decisions": rel(decisions_out),
                "manifest": rel(manifest_path),
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
