# Early Saurischian Herrerasaurus Route

This folder tracks the Herrerasaurus-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `bodylock_prompt_schedule.json`: guide-conditioned route for preserving the compact-hand early-saurischian body plan without drifting into T. rex arms, oversized dangling claws, or bulky large-theropod anatomy.
- `review/`: rejected and comparison sheets from earlier Herrerasaurus experiments.

## Seed Roles

- `train_seed`: reviewed internal images that may seed a tiny proof dataset.
- `control_reference`: project-owned guides for ControlNet, i2i, or prompt planning; do not train directly from schematic guides.
- `review_hold`: useful comparisons that remain excluded from training because of anatomy risk.
- `reject_reference`: negative gates for automation and human review; never train as positive samples.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\early_saurischian_herrerasaurus\seed_manifest.json --output-dir tools\comfyui\lora_training\early_saurischian_herrerasaurus\materialized_seed
```

The command writes an ignored local folder with copied `train_seed` images, matching captions, and a contact sheet. Keep the materialized folder out of git.

## Compact-Hand Body-Lock Control Route

Use these project-owned references before promoting another Herrerasaurus render:

- `assets/dinosaurs/herrerasaurus-ischigualastensis-bodylock-guide-v1.png`
- `assets/dinosaurs/herrerasaurus-bodylock-crops-v3.png`
- `assets/dinosaurs/herrerasaurus-review-options-v8.png`
- `assets/dinosaurs/herrerasaurus-p2-v5-v7-review-sheet.png`
- `assets/dinosaurs/herrerasaurus-p2-v5-v7-crops.png`

The route is designed to preserve these diagnostic cues:

- closed narrow carnivorous head, not a massive T. rex skull
- slim horizontal early-saurischian torso
- full single tail in frame
- exactly two hind legs with dry three-toed theropod feet
- compact folded forelimbs longer than T. rex arms but not dangling
- three main clawed hand digits, with any outer digits tiny and vestigial

Reject otherwise polished outputs if arms shrink into T. rex proportions, hands become long dangling hooks, four or five equal long fingers dominate the hand, forelimbs touch the ground, the mouth becomes a wide monster gape, the body becomes bulky Allosaurus/T. rex-like, feet or tail are hidden, or source-like text/logos appear.

## Compact-Hand Review Route

Tracked review files:

- `assets/dinosaurs/herrerasaurus-compacthands-crops-v2.png`
- `assets/dinosaurs/herrerasaurus-bodylock-crops-v3.png`
- `assets/dinosaurs/herrerasaurus-review-options-v8.png`
- `assets/dinosaurs/herrerasaurus-p1-v4-review-sheet.png`
- `assets/dinosaurs/herrerasaurus-p1-v4-crops.png`
- `assets/dinosaurs/herrerasaurus-p2-v5-v7-review-sheet.png`
- `assets/dinosaurs/herrerasaurus-p2-v5-v7-crops.png`
- `review/herrera_closedjaw_head_blend_v1_review.json`
- `review/herrerasaurus_p1_v4_review.json`
- `review/herrerasaurus_p2_v5_v7_review.json`

Decision: keep `herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png` as the current app first candidate and a cautious `train_seed`, but keep the balanced-hands and closed-jaw head-blend outputs as `review_hold` until hand anatomy is rechecked. Keep the long-arm IP-Control route as `reject_reference` because it risks long dangling hook hands and weaker species identity. Future automation must not treat a prettier Herrerasaurus as a pass if it shrinks the arms into T. rex proportions, creates four/five equal long fingers, hides feet or tail, or bulks the body toward Allosaurus/T. rex.

## P1 V4 Source Candidate

Decision: keep `herrerasaurus-ischigualastensis-imagegen-v4-source-candidate.png` as `review_hold`, not `train_seed`. It improves the project-owned Triassic floodplain scene and preserves a narrow closed head, full side-profile body, long tail, and two hind legs, but the visible hand can read as too many equal long fingers. Do not promote it until crop review proves the three-main-digit plus tiny vestigial outer-digit hand target without forelimb-ground-contact or bulky large-theropod drift.

## P2 V5-V7 Compact-Hand Review

Decision: keep `herrerasaurus-ischigualastensis-imagegen-v6-source-candidate.png` as the best P2 `review_hold`, not `train_seed`. It improves the compact folded forelimb read while preserving the narrow closed head, light body, full tail, and two grounded hind legs, but exact three-main-digit topology is still too soft for promotion.

Keep `herrerasaurus-ischigualastensis-imagegen-v5-source-candidate.png` and `herrerasaurus-ischigualastensis-imagegen-v7-source-candidate.png` as `reject_reference` examples because their visible hands drift into long dangling hook claws or too many/equal long fingers. The current v2 candidate remains the only positive seed.

## Seed Pool Correction: Older Compact-Hand Gate

Decision: demote `herrerasaurus_strict_compact_v1` from `train_seed` to `review_hold`. It remains a useful closed-head and compact-forelimb comparison, but the smaller scene scale and dangling hand claws are weaker than the v2 first candidate. Keep only `herrerasaurus_compacthands_v2` as the current positive smoke-test seed until a later candidate proves the compact three-main-digit hand target more clearly.
