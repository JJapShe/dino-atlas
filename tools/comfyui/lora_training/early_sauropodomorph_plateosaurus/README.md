# Early Sauropodomorph Plateosaurus Route

This folder tracks the Plateosaurus-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `bodylock_prompt_schedule.json`: guide-conditioned route for preserving the bipedal early-sauropodomorph body plan without reintroducing the six-leg failure mode.
- `review/`: reserved for rejected and comparison sheets from future Plateosaurus experiments.

## No-Six-Leg Body-Lock Control Route

Use these project-owned references before promoting another Plateosaurus render:

- `assets/dinosaurs/plateosaurus-engelhardti-bodylock-guide-v1.png`
- `assets/dinosaurs/plateosaurus-bodylock-crops-v4.png`
- `assets/dinosaurs/plateosaurus-review-options-v12.png`
- `assets/dinosaurs/plateosaurus-p1-v15-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p1-v15-crops.png`
- `assets/dinosaurs/plateosaurus-p2-v16-v18-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p2-v16-v18-crops.png`
- `assets/dinosaurs/plateosaurus-p3-v19-v21-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p3-v19-v21-crops.png`
- `assets/dinosaurs/plateosaurus-p4-v22-v25-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p4-v22-v25-crops.png`

The route is designed to preserve these diagnostic cues:

- low non-predatory herbivore head
- long forward neck and deep early-sauropodomorph torso
- full single tail in frame
- exactly two large weight-bearing hind legs on the ground
- short lifted forelimbs with five-finger hands and a larger thumb-claw cue

Reject otherwise polished outputs if forelimbs touch the ground, overlapping arms read as extra legs, the animal becomes quadrupedal, the hands become huge theropod hooks, the tail is cropped, the feet are hidden, or the head drifts toward a predator, sauropod, or generic lizard.

## Seed Roles

- `train_seed`: only the current v25 dark-speckled color candidate. It is count-level, not final, but it is the safest current positive source that combines no-six-leg body anatomy with gallery-distinct color/pattern.
- `control_reference`: project-owned body-lock guide for ControlNet, depth, line, and i2i conditioning.
- `review_hold`: subtle thumb-tip and body-lock comparisons that preserve useful structure but are not proven positive seeds.
- `reject_reference`: six-leg, ambiguous ControlNet, or identity-drift failures that must stay out of positive training.

## P1 V15 Imagegen Source Hold

`assets/dinosaurs/plateosaurus-engelhardti-imagegen-v15-source-candidate.png` is a prompt-only review hold. It keeps the useful low herbivore head, long neck, full tail, and exactly two grounded hind legs, but it does not decisively solve the far forelimb or five-finger/thumb-claw hand crop. It is superseded by the v20 app-first count-level candidate.

Tracked review files:

- `assets/dinosaurs/plateosaurus-p1-v15-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p1-v15-crops.png`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_p1_v15_review.json`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_seed_manifest_sheet_v2.png`

## P2 V16-V18 Hand-Visibility Review

P2 adds three prompt-only candidates for the lifted-hand problem:

- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v16-source-candidate.png`: best P2 review hold. It improves visible lifted hands and thumb-claw cues while preserving two grounded hind legs, but the claws may be overlong and hook-like.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v17-source-candidate.png`: reject reference. The hands are visible but too human-like, over-digited, and overbuilt for positive training.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v18-source-candidate.png`: silhouette review hold. It keeps a clean two-hind-leg stance and full tail, but the neck trends too long and hand detail is soft.

Tracked review files:

- `assets/dinosaurs/plateosaurus-p2-v16-v18-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p2-v16-v18-crops.png`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_p2_v16_v18_review.json`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_seed_manifest_sheet_v3.png`

## P3 V19-V21 Two-Lifted-Hands Review

P3 adds three prompt-only candidates for the two-visible-forelimb problem:

- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v20-source-candidate.png`: current app-first count-level pass and smoke-test `train_seed`. It shows both short forelimbs lifted off the ground while preserving the low herbivore head, long forward neck, deep torso, full tail, and exactly two grounded hind legs.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v19-source-candidate.png`: hand-detail review hold. It has good hand visibility and no six-leg drift, but the fingers and thumb claws trend long and hook-like.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v21-source-candidate.png`: silhouette review hold. It keeps a clean no-six-leg body and full tail, but the far forelimb remains weaker than v20.

Tracked review files:

- `assets/dinosaurs/plateosaurus-p3-v19-v21-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p3-v19-v21-crops.png`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_p3_v19_v21_review.json`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_seed_manifest_sheet_v4.png`

V20 is not final paleoart approval. It remains a no-six-leg, two-lifted-forelimb review hold below v25; exact five-finger hand topology and the larger thumb-claw still need future localized hand i2i or direct reference review.

## P4 V22-V25 Color-Pattern Review

P4 adds four prompt-only candidates for the species color-separation problem while preserving the no-six-leg gate:

- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v25-source-candidate.png`: current app-first count-level pass and smoke-test `train_seed`. It adds charcoal green-gray skin, cream speckles, and darker tail bands while preserving the low herbivore head, long forward neck, full tail, exactly two grounded hind legs, and short lifted forelimbs.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v23-source-candidate.png`: red-clay color review hold. It has the strongest warm dorsal color and dark flank spots, but the fingers remain longer and more hook-like than v25.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v22-source-candidate.png`: olive/cream mottled color review hold. It is useful as a color direction but keeps long hand-claw risk.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v24-source-candidate.png`: reject reference. It has distinct slate/ochre bands, but the hands lengthen again and hind-leg overlap is less safe for the no-six-leg gate.

Tracked review files:

- `assets/dinosaurs/plateosaurus-p4-v22-v25-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p4-v22-v25-crops.png`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_p4_v22_v25_review.json`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_seed_manifest_sheet_v5.png`

V25 is not final paleoart approval. It is the current color-separated smoke-test source; future hand-local i2i should preserve its dark speckled color, tail bands, two grounded hind legs, full tail, and lifted forelimbs while shortening hook-risk fingers and clarifying the larger thumb-claw cue.

## P5 V26-V28 No-Six-Leg Color Variation Review

P5 adds three prompt-only candidates to test whether the route can preserve color separation while improving the lifted-forelimb/no-six-leg gate:

- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v27-source-candidate.png`: best P5 `review_hold`. It has the safest new two-grounded-hind-leg stance and the shortest lifted forelimbs, plus blue-gray olive speckles and rusty patches, but the hands are partly fused and the thumb-claw cue is weak.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v28-source-candidate.png`: color/silhouette `review_hold`. It adds a useful moss-green, cream-speckled, burgundy-throat palette with dark tail bands and no forelimb ground contact, but the hands lengthen again.
- `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v26-source-candidate.png`: `reject_reference`. It has useful charcoal/copper coloration, speckles, and tail bands, but the lifted fingers become too long and hook-like.

Tracked review files:

- `assets/dinosaurs/plateosaurus-p5-v26-v28-review-sheet.png`
- `assets/dinosaurs/plateosaurus-p5-v26-v28-crops.png`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_p5_v26_v28_review.json`
- `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/review/plateosaurus_seed_manifest_sheet_v6.png`

Decision: keep v25 as the app-first `train_seed`, add v27 and v28 as `review_hold` only, and keep v26 out of positive training as a hook-hand rejection gate. The next useful route is localized hand i2i or body-lock ControlNet over v25 with v27 as the no-six-leg/lifted-hand reference, preserving the dark speckled color and exactly two grounded hind legs while shortening the fingers and clarifying the larger thumb-claw cue.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\early_sauropodomorph_plateosaurus\seed_manifest.json --output-dir tools\comfyui\lora_training\early_sauropodomorph_plateosaurus\materialized_seed
```

## Review Route

Promote a future candidate only if it beats the v25 source on exact hand/thumb-claw anatomy without erasing the dark speckled color, making the forelimbs weight-bearing, weakening the two grounded hind legs, or creating a six-leg read.
