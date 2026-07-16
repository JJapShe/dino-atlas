import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_MANIFEST = ROOT / "tools" / "comfyui" / "outputs" / "app-gallery-samples.json"
CURATED_ROOT = ROOT / "assets" / "dinosaurs" / "curated"
FINAL_ROOT = CURATED_ROOT / "final-candidates"
REFERENCE_ROOT = CURATED_ROOT / "reference-library"
OUT_MANIFEST = CURATED_ROOT / "curated-image-library.json"

FINAL_KINDS = {
    "primary generated",
    "primary structure reference",
    "count-level pass",
}

REFERENCE_KINDS = {
    "review hold",
    "anatomy review",
    "structure reference",
    "diagnostic only",
    "reject reference",
}


def safe_name(path, index):
    source = Path(path)
    stem = source.stem.lower()
    cleaned = "".join(char if char.isalnum() or char in "-_" else "-" for char in stem)
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return f"{index:03d}-{cleaned}{source.suffix.lower() or '.png'}"


def copy_item(item, taxon, target_root, index):
    source_rel = item.get("src") or item.get("source")
    if not source_rel:
        return None

    source_path = ROOT / source_rel
    if not source_path.exists():
        return {
            "taxon": taxon,
            "source": source_rel,
            "missing": True,
        }

    target_dir = target_root / taxon
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / safe_name(source_rel, index)
    shutil.copy2(source_path, target_path)

    return {
        "taxon": taxon,
        "kind": item.get("kind", ""),
        "title": item.get("title", ""),
        "source": source_rel,
        "curated": str(target_path.relative_to(ROOT)).replace("\\", "/"),
    }


def main():
    data = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    samples = data.get("samples", {})
    if CURATED_ROOT.exists():
        shutil.rmtree(CURATED_ROOT)
    manifest = {
        "schema": "dino-atlas-curated-image-library-v1",
        "sourceManifest": str(SOURCE_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "policy": {
            "finalCandidates": sorted(FINAL_KINDS),
            "referenceLibrary": sorted(REFERENCE_KINDS),
            "mode": "copy-only; source files are not moved so existing app links remain stable",
        },
        "taxa": {},
        "missing": [],
    }

    for taxon, items in samples.items():
        final_items = []
        reference_items = []
        final_index = 1
        reference_index = 1
        for item in items:
            kind = item.get("kind", "")
            if kind in FINAL_KINDS:
                copied = copy_item(item, taxon, FINAL_ROOT, final_index)
                final_index += 1
                if copied and copied.get("missing"):
                    manifest["missing"].append(copied)
                elif copied:
                    final_items.append(copied)
            elif kind in REFERENCE_KINDS:
                copied = copy_item(item, taxon, REFERENCE_ROOT, reference_index)
                reference_index += 1
                if copied and copied.get("missing"):
                    manifest["missing"].append(copied)
                elif copied:
                    reference_items.append(copied)

        manifest["taxa"][taxon] = {
            "finalFolder": str((FINAL_ROOT / taxon).relative_to(ROOT)).replace("\\", "/"),
            "referenceFolder": str((REFERENCE_ROOT / taxon).relative_to(ROOT)).replace("\\", "/"),
            "finalCandidates": final_items,
            "referenceItems": reference_items,
        }

    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "manifest": str(OUT_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
                "taxa": len(manifest["taxa"]),
                "finalCandidates": sum(len(item["finalCandidates"]) for item in manifest["taxa"].values()),
                "referenceItems": sum(len(item["referenceItems"]) for item in manifest["taxa"].values()),
                "missing": len(manifest["missing"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
