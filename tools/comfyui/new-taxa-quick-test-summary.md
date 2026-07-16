# New Taxa Quick Test Summary

Last updated: 2026-07-05

## Scope

Added three taxa to the atlas as a fast stability test for the current image pipeline:

- `spinosaurus-aegyptiacus`
- `parasaurolophus-walkeri`
- `pachycephalosaurus-wyomingensis`

Each taxon now has app data, map placement, review checklist entries, visual variation guidance, generation-route notes, and candidate images in the review board.

## Result

The built-in image generation path produced the current smoke-test representatives:

- `assets/dinosaurs/spinosaurus-aegyptiacus-imagegen-v1-source-candidate.png`
- `assets/dinosaurs/parasaurolophus-walkeri-imagegen-v1-source-candidate.png`
- `assets/dinosaurs/pachycephalosaurus-wyomingensis-imagegen-v1-source-candidate.png`

These are marked `count-level pass`, not final approval. They should be treated as project-owned smoke-test candidates until close reference review checks species-level anatomy.

## Local SDXL Prompt-Only Probe

Two quick ComfyUI prompt-only sweeps were run with the existing `run_sdxl_taxon_sweep.py` path:

```powershell
tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\run_sdxl_taxon_sweep.py --taxon-id spinosaurus-aegyptiacus --taxon-id parasaurolophus-walkeri --taxon-id pachycephalosaurus-wyomingensis --seed 2026070501 --prefix new_taxa_quick_v1 --clean-corners
tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\run_sdxl_taxon_sweep.py --taxon-id spinosaurus-aegyptiacus --taxon-id parasaurolophus-walkeri --taxon-id pachycephalosaurus-wyomingensis --seed 2026070502 --prefix new_taxa_quick_v2 --clean-corners
```

Diagnostic sheets:

- `assets/dinosaurs/new-taxa-quick-v1-contact-sheet.png`
- `assets/dinosaurs/new-taxa-quick-v2-contact-sheet.png`

Findings:

- Spinosaurus: local prompt-only route made plausible theropod bodies but missed or weakened the tall sail.
- Parasaurolophus: first prompt-only run drifted into a goose/ostrich-like animal; stricter retry improved body mass but still missed the tube crest.
- Pachycephalosaurus: local prompt-only route made plausible bipedal ornithischian bodies but did not reliably lock the high dome skull.

## Next Route

For these three taxa, prompt-only local SDXL is useful as a failure probe but not stable enough for first-card candidates. The next ComfyUI route should start with simple body-lock guides:

- Spinosaurus: sail silhouette + theropod stance guide.
- Parasaurolophus: tube-crest skull silhouette + hadrosaur body guide.
- Pachycephalosaurus: high dome skull silhouette + bipedal ornithischian guide.

Until those guides exist, keep the built-in imagegen v1 outputs as the app-first smoke-test candidates and keep local prompt-only sheets as `diagnostic only`.
