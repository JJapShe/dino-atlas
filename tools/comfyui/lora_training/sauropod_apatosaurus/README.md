# Sauropod Apatosaurus Route

This folder tracks the Apatosaurus-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `bodylock_prompt_schedule.json`: strict guide-conditioned route for preventing Brachiosaurus or generic sauropod drift.
- `review/`: rejected and comparison sheets from earlier low-neck and edge-volume experiments.

## Low-Neck Body-Lock Control Route

Use these project-owned references before promoting another Apatosaurus render:

- `assets/dinosaurs/apatosaurus-ajax-lowneck-bodylock-guide-v1.png`
- `assets/dinosaurs/apatosaurus-lowneck-bodylock-crops-v3.png`
- `assets/dinosaurs/apatosaurus-review-options-v6.png`
- `assets/dinosaurs/apatosaurus-p1-v3-v5-review-sheet.png`
- `assets/dinosaurs/apatosaurus-p1-v3-v5-crops.png`
- `tools/comfyui/lora_training/sauropod_apatosaurus/review/apatosaurus_p1_v3_v5_review.json`

The route is designed to preserve these diagnostic cues:

- low forward-reaching neck held near horizontal
- small blunt non-predatory head
- deep heavy torso without a Brachiosaurus shoulder peak
- front and rear pillar limbs of similar height
- exactly four visible broad sauropod feet on dry ground
- long single horizontal tail fully in frame

Reject otherwise polished outputs if they recover high shoulders, front limbs taller than hind limbs, vertical necks, hidden feet, or cropped/duplicated tails.

## Seed Roles

- `train_seed`: only the current v3 prompt-only candidate, because it is the best low-neck, low-shoulder, full-tail, and four-foot compromise.
- `control_reference`: project-owned low-neck guide for ControlNet, depth, line, and i2i conditioning.
- `review_hold`: previous v2, v4/v5, older low-neck, open-foot, and edge-volume passes that are useful comparisons but still carry foot, head, tail-tip, or flat-body risks.
- `reject_reference`: high-neck or residue-amplifying routes that must not be treated as positive Apatosaurus examples.

Decision: promote `apatosaurus-ajax-imagegen-v3-source-candidate.png` to the current count-level `train_seed`. It improves the low-neck Apatosaurus read over v2 with an almost horizontal forward neck, low non-Brachiosaurus shoulders, a long fully framed horizontal tail, and exactly four visible pillar legs. Keep `apatosaurus-ajax-smallhead-imagegen-v2.png`, `apatosaurus-ajax-imagegen-v4-source-candidate.png`, and `apatosaurus-ajax-imagegen-v5-source-candidate.png` as `review_hold`; v4 is close but slightly heavier in the head/neck, and v5 carries more tail-tip bend and rear-foot overlap risk.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\sauropod_apatosaurus\seed_manifest.json --output-dir tools\comfyui\lora_training\sauropod_apatosaurus\materialized_seed
```

## Review Route

Promote a future candidate only if it keeps the low forward neck, similar-height pillar limbs, four open feet, and full horizontal tail while improving body volume.
