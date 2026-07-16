# Small Theropod Coelophysis Route

This folder tracks the Coelophysis-specific generation path for copyright-safe atlas candidates.

## Current Routes

- `bodylock_prompt_schedule.json`: guide-conditioned route for preserving the small early-theropod body plan without turning forelimbs into extra legs.
- `review/`: reserved for rejected and comparison sheets from future Coelophysis experiments.

## Seed Roles

- `train_seed`: reviewed internal images that may seed a tiny proof dataset.
- `control_reference`: project-owned guides for ControlNet, i2i, or prompt planning; do not train directly from schematic guides.
- `review_hold`: useful comparisons that remain excluded from training because of anatomy risk.
- `reject_reference`: negative gates for automation and human review; never train as positive samples.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\small_theropod_coelophysis\seed_manifest.json --output-dir tools\comfyui\lora_training\small_theropod_coelophysis\materialized_seed
```

The command writes an ignored local folder with copied `train_seed` images, matching captions, and a contact sheet. Keep the materialized folder out of git.

## Body-Lock Control Route

Use these project-owned references before promoting another Coelophysis render:

- `assets/dinosaurs/coelophysis-bauri-bodylock-guide-v1.png`
- `assets/dinosaurs/coelophysis-bodylock-crops-v4.png`
- `assets/dinosaurs/coelophysis-review-options-v8.png`
- `assets/dinosaurs/coelophysis-p2-v6-v8-review-sheet.png`
- `assets/dinosaurs/coelophysis-p2-v6-v8-crops.png`

The route is designed to preserve these diagnostic cues:

- narrow lightly toothed head and long S-curved neck
- slim lightly built early-theropod torso
- very long single balancing tail fully in frame
- exactly two long hind legs with dry three-toed feet
- two short folded three-finger forelimbs held off the ground

Reject otherwise polished outputs if the forelimbs touch the ground, read as extra legs, become huge dangling hooks, lose the full tail, hide the feet, become bird-beaked or feathered, or drift toward bulky raptor, T. rex, Allosaurus, lizard, or sauropodomorph proportions.

## Slender-Neck Small-Hand Review Route

Tracked review files:

- `assets/dinosaurs/coelophysis-slenderneck-smallhands-crops-v3.png`
- `assets/dinosaurs/coelophysis-bodylock-crops-v4.png`
- `assets/dinosaurs/coelophysis-review-options-v8.png`
- `assets/dinosaurs/coelophysis-forelimb-reference-sheet-v1.png`
- `assets/dinosaurs/coelophysis-p1-v5-review-sheet.png`
- `assets/dinosaurs/coelophysis-p1-v5-crops.png`
- `assets/dinosaurs/coelophysis-p2-v6-v8-review-sheet.png`
- `assets/dinosaurs/coelophysis-p2-v6-v8-crops.png`
- `review/coelophysis_p1_v5_review.json`
- `review/coelophysis_p2_v6_v8_review.json`

Decision: keep `coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png` as the current app first candidate and a cautious `train_seed`, with the previous compact-hand v2 as a supporting seed. Keep the open-feet v3 comparison as `review_hold` and the open-limb v2 route as `reject_reference` because longer forelimb hands can drift into hook-like or extra-limb reads. Future automation must reject outputs where the small forelimbs touch the ground, become extra legs, hide the feet, lose the full tail, or drift toward bird, bulky raptor, T. rex, Allosaurus, lizard, or sauropodomorph body plans.

## P1 V5 Source Candidate

Decision: keep `coelophysis-bauri-imagegen-v5-source-candidate.png` as `review_hold`, not `train_seed`. It improves the visible small forelimb read while keeping those forelimbs off the ground, plus two hind legs, dry feet, a long S-curved neck, and a full tail. Keep v3 first because v5 reads slightly heavier in the head and torso, and exact hand/toe anatomy remains close-review only.

## P2 V6-V8 No-Extra-Leg Review

Decision: keep `coelophysis-bauri-imagegen-v6-source-candidate.png` and `coelophysis-bauri-imagegen-v8-source-candidate.png` as `review_hold`, not `train_seed`. V6 is the best new gracile silhouette and V8 has the cleanest no-extra-leg read, but neither clearly beats v3 on exact small-hand and toe anatomy.

Keep `coelophysis-bauri-imagegen-v7-source-candidate.png` as `reject_reference` because the body/head read heavier and the forelimb hands become longer and more hook-like. The current v3 candidate remains the only positive seed.

## Seed Pool Correction: Older Compact-Hand Gate

Decision: demote `coelophysis_compacthands_v2` from `train_seed` to `review_hold`. It remains a useful dry-ground and compact-hand comparison, but it is less gracile and less Coelophysis-like than the selected v3 candidate, with weaker exact hand and rear-foot reads. Keep only `coelophysis_slenderneck_smallhands_v3` as the current positive smoke-test seed until a later candidate proves small hands, long S-neck, feet, and full tail together.
