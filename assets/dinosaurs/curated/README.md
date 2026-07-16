# Curated Dinosaur Image Library

This folder is generated from the app gallery data.

- `final-candidates/`: copied representative images only (`primary generated`, `primary structure reference`, `count-level pass`).
- `reference-library/`: copied per-taxon review material, anatomy/crop sheets, structure guides, review holds, diagnostics, and reject references.
- `curated-image-library.json`: manifest for both folders.
- `review-decisions.json`: project-persisted manual review selections and decisions.

The source files under `assets/dinosaurs/` are not moved, so existing app links stay stable.

## Regenerate Folders

```powershell
& 'C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\comfyui\scripts\organize_dinosaur_image_library.py
```

## Apply Review Page Decisions

1. Open the app review page.
2. Mark candidates as selected, approved, pending, or rejected.
3. Click `검수 데이터 내보내기`.
4. Apply the downloaded JSON:

```powershell
& 'C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\comfyui\scripts\apply_review_decisions.py --input "$env:USERPROFILE\Downloads\dino-atlas-review-decisions.json"
```

The command updates `review-decisions.json` and annotates `curated-image-library.json` with `selected`, `decision`, `selectedPrimary`, and decision counts.
