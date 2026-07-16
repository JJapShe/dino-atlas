import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "tools" / "comfyui" / "outputs" / "app-gallery-samples.json"
AUDIT = ROOT / "tools" / "comfyui" / "anatomy-audit.md"


def taxon_label(taxon_id):
    return taxon_id.split("-", 1)[0].capitalize()


def primary_samples():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    samples = data["samples"]
    primaries = {}
    for taxon_id, items in samples.items():
        if not items:
            continue
        primary = items[0]
        image = primary.get("src") or primary.get("source") or ""
        primaries[taxon_label(taxon_id)] = {
            "taxonId": taxon_id,
            "kind": primary.get("kind", ""),
            "image": image,
            "basename": Path(image).name,
        }
    return primaries


def audit_rows():
    rows = {}
    in_table = False
    for line in AUDIT.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Taxon |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("| ---"):
            continue
        if not line.startswith("| "):
            if rows:
                break
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        rows[parts[0]] = {"status": parts[1], "notes": parts[2]}
    return rows


def main():
    primaries = primary_samples()
    rows = audit_rows()
    problems = []

    for label, primary in primaries.items():
        row = rows.get(label)
        if not row:
            problems.append(f"missing audit row for {label} ({primary['taxonId']})")
            continue
        if row["status"] != primary["kind"]:
            problems.append(
                f"{label}: audit status {row['status']!r} does not match app primary kind {primary['kind']!r}"
            )
        if primary["basename"] and primary["basename"] not in row["notes"]:
            problems.append(
                f"{label}: audit notes do not mention app primary image {primary['basename']!r}"
            )

    stale_dates = re.findall(r"Last updated: (.+)", AUDIT.read_text(encoding="utf-8"))
    result = {
        "checked": len(primaries),
        "problems": problems,
        "lastUpdated": stale_dates[0] if stale_dates else None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
