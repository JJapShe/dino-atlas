# Theropod Tyrannosaurus Route

This folder tracks the Tyrannosaurus-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `twofinger_bodylock_prompt_schedule.json`: strict guide-conditioned route for preventing three-finger or allosaur-like arm drift.

## Seed Roles

- `train_seed`: reviewed internal images that may seed a tiny proof dataset.
- `control_reference`: project-owned guides for ControlNet, i2i, or prompt planning; do not train directly from schematic guides.
- `review_hold`: useful comparisons that remain excluded from training because of anatomy risk.
- `reject_reference`: negative gates for automation and human review; never train as positive samples.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\theropod_tyrannosaurus\seed_manifest.json --output-dir tools\comfyui\lora_training\theropod_tyrannosaurus\materialized_seed
```

The command writes an ignored local folder with copied `train_seed` images, matching captions, and a contact sheet. Keep the materialized folder out of git.

## Two-Finger Body-Lock Control Route

Use these project-owned references before promoting another Tyrannosaurus render:

- `assets/dinosaurs/tyrannosaurus-rex-twofinger-bodylock-guide-v1.png`
- `assets/dinosaurs/tyrannosaurus-twofinger-bodylock-crops-v8.png`
- `assets/dinosaurs/tyrannosaurus-review-options-v8.png`
- `assets/dinosaurs/tyrannosaurus-p1-v10-v12-review-sheet.png`
- `assets/dinosaurs/tyrannosaurus-p1-v10-v12-crops.png`
- `tools/comfyui/lora_training/theropod_tyrannosaurus/review/tyrannosaurus_p1_v10_v12_review.json`
- `assets/dinosaurs/tyrannosaurus-p2-v13-v15-review-sheet.png`
- `assets/dinosaurs/tyrannosaurus-p2-v13-v15-crops.png`
- `tools/comfyui/lora_training/theropod_tyrannosaurus/review/tyrannosaurus_p2_v13_v15_review.json`
- `assets/dinosaurs/tyrannosaurus-p3-v16-v18-review-sheet.png`
- `assets/dinosaurs/tyrannosaurus-p3-v16-v18-crops.png`
- `tools/comfyui/lora_training/theropod_tyrannosaurus/review/tyrannosaurus_p3_v16_v18_review.json`
- `tools/comfyui/lora_training/theropod_tyrannosaurus/review/tyrannosaurus_seed_manifest_sheet_v4.png`

The route is designed to preserve these diagnostic cues:

- massive deep skull with smooth low brow, no horns or crest
- robust torso and long heavy balancing tail
- exactly two strong hind legs with dry three-toed feet
- tiny forelimbs held close to the chest
- exactly two short clawed fingers per visible hand

Reject otherwise polished outputs if they enlarge the arms, add a third finger, hide the hands entirely, create allosaur-like medium forelimbs, add horn-like brow bumps, crop the feet/tail, or introduce logo/text artifacts.

## V4-Source ControlNet Rejection

Tracked review files:

- `review/trex_v4source_controlnet_v9_review.json`
- `assets/dinosaurs/tyrannosaurus-controlnet-v9-rejection-sheet.png`
- `assets/dinosaurs/tyrannosaurus-controlnet-v9-rejection-crops.png`

Decision: keep the v9 ControlNet output as `reject_reference`. It looks dramatic, but it enlarges the arms toward Allosaurus-like proportions and weakens the exact two-finger hand gate. Future automation should favor local low-denoise hand masking or style-preserving i2i over whole-body ControlNet from the natural v4 source unless the two-finger cue and tiny arm scale remain crop-proven.

## Seed Pool Correction: Older Hand Gate

Decision: demote `tyrannosaurus_smoothbrow_twofinger_v3` from `train_seed` to `review_hold`. It remains a useful body/skull source for comparison, but the hand cue is weaker than the v4 local hand repair. Keep only `tyrannosaurus_twofinger_hand_i2i_v4` as the current positive smoke-test seed until a later candidate proves tiny-arm scale and exactly two visible fingers more clearly.

## Prompt-Only V10-V12 Review

Decision: keep `tyrannosaurus-rex-imagegen-v12-source-candidate.png` as `review_hold`, not `train_seed`. It is the most useful fresh prompt-only comparison because the hand is easier to inspect, but the forelimb is larger than the current v4 seed and the two-finger cue is exaggerated enough to risk allosaur-like drift. Keep `tyrannosaurus-rex-imagegen-v10-source-candidate.png` and `tyrannosaurus-rex-imagegen-v11-source-candidate.png` as `reject_reference` because the hands read long, ambiguous, or potentially three-pronged. Do not promote a T. rex candidate solely because the fingers are more visible; tiny-arm scale and exactly two compact fingers must pass together.

## Prompt-Only V13-V15 Review

Decision: keep `tyrannosaurus-rex-imagegen-v15-source-candidate.png` as the best P2 `review_hold`, not `train_seed`. It preserves tiny tucked forelimb scale better than the other new prompt-only outputs, but the exact two-finger cue is still too soft in crop review. Keep `tyrannosaurus-rex-imagegen-v14-source-candidate.png` as a `review_hold` hand-visibility comparison because the two-finger cue is clearer, but the arm and hand scale grow too large. Keep `tyrannosaurus-rex-imagegen-v13-source-candidate.png` as `reject_reference` because the hand can read as three-pronged or too claw-heavy. Use v15 only as a copyright-safe localized hand i2i or ControlNet source, and reject any result that gains finger readability by enlarging the arm or adding a third digit.

## Prompt-Only V16-V18 Review

Decision: keep `tyrannosaurus-rex-imagegen-v18-source-candidate.png` as the best P3 `review_hold`, not `train_seed`. It has the best fresh balance of massive T. rex body, very small chest-held forelimbs, two strong hind legs, dry feet, and long tail, but the exact two-finger hand cue remains too small and crop-soft for representative promotion. Keep `tyrannosaurus-rex-imagegen-v16-source-candidate.png` as a secondary `review_hold` because it preserves tiny arm scale but the hand overlaps shadow. Keep `tyrannosaurus-rex-imagegen-v17-source-candidate.png` as `reject_reference` because the hand can read as three-pronged and the arm scale creeps larger. Keep v4 first until tiny-arm scale and exactly two compact fingers are proven together in crop review.
