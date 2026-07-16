# Sauropod Brachiosaurus Route

This folder tracks the Brachiosaurus-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `synthetic_prompt_schedule.json`: broad prompt schedule for Brachiosaurus candidate generation.
- `bodylock_prompt_schedule.json`: stricter guide-conditioned route for preventing diplodocid drift.

## High-Shoulder Body-Lock Control Route

Use these project-owned references before promoting another Brachiosaurus render:

- `assets/dinosaurs/brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png`
- `assets/dinosaurs/brachiosaurus-highshoulder-bodylock-crops-v8.png`
- `assets/dinosaurs/brachiosaurus-review-options-v8.png`
- `assets/dinosaurs/brachiosaurus-p1-v9-v11-review-sheet.png`
- `assets/dinosaurs/brachiosaurus-p1-v9-v11-crops.png`
- `tools/comfyui/lora_training/sauropod_brachiosaurus/review/brachiosaurus_p1_v9_v11_review.json`
- `assets/dinosaurs/brachiosaurus-p2-v12-v14-review-sheet.png`
- `assets/dinosaurs/brachiosaurus-p2-v12-v14-crops.png`
- `tools/comfyui/lora_training/sauropod_brachiosaurus/review/brachiosaurus_p2_v12_v14_review.json`
- `assets/dinosaurs/brachiosaurus-p3-v15-v17-review-sheet.png`
- `assets/dinosaurs/brachiosaurus-p3-v15-v17-crops.png`
- `tools/comfyui/lora_training/sauropod_brachiosaurus/review/brachiosaurus_p3_v15_v17_review.json`

The route is designed to preserve these diagnostic cues:

- shoulders visibly higher than hips
- front limbs taller and straighter than hind limbs
- trunk slopes downward from shoulder to hip
- long neck rises forward-up from the shoulder
- small non-predatory sauropod head
- exactly four visible pillar feet on dry ground
- short thick tapering tail, not a diplodocid whip tail

Reject otherwise polished outputs if they recover a low Apatosaurus/Diplodocus body plan, equal-height limbs, cropped feet, hoof-like feet, or a long thin tail.

## Seed Roles

- `train_seed`: the current v16 short-tail candidate, because it keeps the high-shoulder body gate while solving the repeated whip-tail risk more clearly than prior prompt-only outputs.
- `control_reference`: project-owned high-shoulder guide for ControlNet, depth, line, and i2i conditioning.
- `review_hold`: previous v4, v17/v15, v13/v10/v9 prompt-only candidates, and earlier high-shoulder/balanced-neck comparisons that are useful for diagnostics but weaker than v16.
- `reject_reference`: v12/v14/v11 tail-risk, muted-neck, or older naturalistic routes that weaken the Brachiosaurus identity gate.

Decision: keep `brachiosaurus-altithorax-imagegen-v10-source-candidate.png` as `review_hold`, not `train_seed`. It is the strongest fresh prompt-only candidate from the v9-v11 set because it preserves high shoulders, taller forelimbs, a rising neck, a side-profile body, and four visible legs. Keep the tail-reduced v4 image first because v10 still has a long thin tail risk; keep v9 as a secondary review hold and v11 as a `reject_reference` for curling diplodocid-tail drift.

P2 decision: keep `brachiosaurus-altithorax-imagegen-v13-source-candidate.png` as `review_hold`, not `train_seed`. It has the strongest fresh high-shoulder, taller-forelimb, rising-neck, and four-foot read from v12-v14, but the tail remains too long and thin for the Brachiosaurus short-tail gate. Keep v12 and v14 as `reject_reference` examples because they show the recurring failure: attractive high shoulders paired with unsafe diplodocid whip-tail drift. Future work should use a stricter tail-base/short-tail control source or localized tail i2i rather than more whole-body prompt-only retries.

P3 decision: promote `brachiosaurus-altithorax-imagegen-v16-source-candidate.png` as the current app first image and positive seed. It is the first fresh candidate in this route to combine the high-shoulder/taller-forelimb Brachiosaurus silhouette, rising neck, four reviewable feet, and a visibly short thick tapering tail. Keep the previous v4 first candidate as `review_hold` because it remains useful for i2i comparison but has a longer thinner tail than v16. Keep v17 and v15 as review holds: both preserve useful body plans, but v17 is less compact than v16 and v15 retains a longer pointed tail. Do not mark the taxon final until the skull, toes, and tail base pass closer reference review.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\sauropod_brachiosaurus\seed_manifest.json --output-dir tools\comfyui\lora_training\sauropod_brachiosaurus\materialized_seed
```

## Review Route

Promote a future candidate only if it preserves visibly higher shoulders, taller forelimbs, a rising neck, four open feet, and a short thick tail.
