# Theropod Allosaurus Route

This folder tracks the Allosaurus-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `threefinger_bodylock_prompt_schedule.json`: strict guide-conditioned route for preventing T. rex, horned-monster, or two-finger drift.
- `review/`: rejected and comparison sheets from earlier Allosaurus experiments.

## Seed Roles

- `train_seed`: reviewed internal images that may seed a tiny proof dataset.
- `control_reference`: project-owned guides for ControlNet, i2i, or prompt planning; do not train directly from schematic guides.
- `review_hold`: useful comparisons that remain excluded from training because of anatomy risk.
- `reject_reference`: negative gates for automation and human review; never train as positive samples.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\theropod_allosaurus\seed_manifest.json --output-dir tools\comfyui\lora_training\theropod_allosaurus\materialized_seed
```

The command writes an ignored local folder with copied `train_seed` images, matching captions, and a contact sheet. Keep the materialized folder out of git.

## Three-Finger Body-Lock Control Route

Use these project-owned references before promoting another Allosaurus render:

- `assets/dinosaurs/allosaurus-fragilis-threefinger-bodylock-guide-v1.png`
- `assets/dinosaurs/allosaurus-threefinger-bodylock-crops-v10.png`
- `assets/dinosaurs/allosaurus-review-options-v10.png`
- `assets/dinosaurs/allosaurus-p2-v14-v16-review-sheet.png`
- `assets/dinosaurs/allosaurus-p2-v14-v16-crops.png`

The route is designed to preserve these diagnostic cues:

- lower allosaur skull, not a massive T. rex skull
- no horn-like brow bumps or fantasy crest
- medium non-weight-bearing forelimbs, longer than T. rex arms
- exactly three clawed fingers per visible hand
- two strong hind legs with dry three-toed feet
- long single tail fully in frame

Reject otherwise polished outputs if they shrink the arms into T. rex proportions, show two fingers, add horn-like brow spikes, hide the hands, crop the feet/tail, or make the head overly massive and tyrannosaur-like.

## Digit Micro-I2I Review

Tracked review files:

- `review/allosaurus_digit_micro_i2i_v11_review.json`
- `review/allosaurus_p1_v12_v13_review.json`
- `review/allosaurus_p2_v14_v16_review.json`
- `assets/dinosaurs/allosaurus-digit-micro-i2i-v11-review-sheet.png`
- `assets/dinosaurs/allosaurus-digit-micro-i2i-v11-crops.png`
- `assets/dinosaurs/allosaurus-p1-v12-v13-review-sheet.png`
- `assets/dinosaurs/allosaurus-p1-v12-v13-crops.png`
- `assets/dinosaurs/allosaurus-p2-v14-v16-review-sheet.png`
- `assets/dinosaurs/allosaurus-p2-v14-v16-crops.png`

Decision: keep v11 as `review_hold`. It preserves the v4 body, brow, tail, and medium forelimb scale, but it does not clearly improve exact three-finger hand separation and toe readability enough to replace v4 or become a positive seed. Future automation should reject outputs that become prettier by shrinking the arms into T. rex proportions, hiding hands, or drifting into horned monster theropods.

## P1 V12/V13 Source Candidates

Decision: keep `allosaurus-fragilis-imagegen-v13-source-candidate.png` as `review_hold`, not `train_seed`. It improves the smooth-brow full-body read over the v12 retry, but its visible hand can read as four fingers, so it fails the exact three-finger promotion gate. Keep `allosaurus-fragilis-imagegen-v12-source-candidate.png` as `reject_reference`: it has a useful full-body silhouette, but raised brow bumps can read as horns and the digit count is ambiguous. Do not promote either candidate without a crop-level pass for exactly three separated fingers per visible hand and no horn-like brow.

## P2 V14-V16 Three-Finger/Brow Review

Decision: keep `allosaurus-fragilis-imagegen-v15-source-candidate.png` as `review_hold`, not `train_seed`. It has the strongest fresh three-finger hand cue, but the skull mass trends too heavy and Tyrannosaurus-like for representative promotion.

Keep `allosaurus-fragilis-imagegen-v14-source-candidate.png` and `allosaurus-fragilis-imagegen-v16-source-candidate.png` as `reject_reference` examples because their brow/head details drift toward horn-like ornament or unsafe digit ambiguity. Keep v4 as the only current positive seed until smooth brow, lower allosaur skull, medium forelimbs, exactly three fingers, dry feet, and full tail pass together.

## Seed Pool Correction: Older Three-Finger Gate

Decision: demote `allosaurus_reviewable_threefinger_v3` from `train_seed` to `review_hold`. It remains useful as an earlier hand/foot comparison, but the brow and hand clarity are weaker than the selected v4 candidate. Keep only `allosaurus_smoothbrow_threefinger_v4` as the current positive smoke-test seed until a later candidate proves the smooth-brow, medium-arm, exactly three-finger gate more clearly.
