# dromaeosaur_feathered LoRA Prep

Purpose: prepare a copyright-safe custom LoRA route for `Velociraptor mongoliensis` and close relatives. The current public-LoRA/inpaint route cannot reliably keep all required cues at once: small feathered dromaeosaur body, folded wing-like forelimbs, long stiff tail, and raised sickle claws.

## Source Policy

Use only:

- internal AI-generated candidates already produced for this project,
- hand-authored control guides from `tools/comfyui/ComfyUI/input/dino_guides/`,
- future synthetic outputs generated from the prompt schedule in this folder after human review.

Do not use museum photos, copyrighted paleoart, movie/game stills, or public LoRA outputs with unclear provenance as training images. Museum/science links remain reference anchors only, not training data.

## Seed Roles

- `train_seed`: can be materialized as image/caption pairs for a first tiny proof dataset.
- `control_reference`: useful for ControlNet or prompt planning, but too guide-like for direct LoRA training.
- `review_hold`: useful as a visual comparison, but excluded because it contains anatomy artifacts, flat style, or weak diagnostic cues.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py
```

The command writes an ignored local folder:

`tools/comfyui/lora_training/dromaeosaur_feathered/materialized_seed/`

It contains copied image files, matching `.txt` captions, a materialized manifest, and a contact sheet. Keep that folder out of git; commit only reviewed source assets, manifests, and scripts.

## Training Gate

Do not train a promoted LoRA from the seed set alone. The seed set is for smoke tests and caption validation. Before a usable LoRA attempt, expand to at least 40 reviewed synthetic images with:

- multiple side-profile walking poses,
- varied Mongolian desert/dune/riverbed backgrounds,
- dense but folded feathers, not flying wings,
- visible two hind legs and long stiff tail,
- at least 12 close or mid shots where the raised sickle claw is readable,
- no text, logo, extra limbs, duplicate tails, or bird-beak drift.

Use `synthetic_prompt_schedule.json` as the broad expansion queue, `identity_bodylock_prompt_schedule.json` when head/forelimb/tail identity collapses, and `foot_topology_prompt_schedule.json` when the main failure is the raised second-toe claw.

## Synthetic Schedule Smoke Run

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\run_lora_seed_schedule.py --limit 6 --prefix dromaeosaur_lora_seed_v1
```

The schedule runner writes ignored review outputs under `tools/comfyui/outputs/`, including a results JSON file and contact sheet. Treat every output as `needs_review`; only manually accepted images should ever be copied into a tracked seed manifest or materialized for training.

### Review Result: `dromaeosaur_lora_seed_v1`

Tracked review files:

- `review/dromaeosaur_lora_seed_v1_review.json`
- `review/dromaeosaur_lora_seed_v1_rejected_contact_sheet.png`

Decision: reject all prompt-only RealVisXL outputs from this run for training. The images repeatedly drift into naked or scaly generic theropods, with weak folded forelimb feathers and no reliable raised sickle-claw cue. This is useful negative evidence: future expansion should use internal plumage guides with ControlNet/IP-Adapter or another feather-aware route, not prompt-only RealVisXL generations.

### Review Result: `dromaeosaur_guided_seed_v1`

Tracked review files:

- `review/dromaeosaur_guided_seed_v1_review.json`
- `review/dromaeosaur_guided_seed_v1_rejected_contact_sheet.png`
- `review/dromaeosaur_guided_feather_inpaint_v1_rejected_contact_sheet.png`

Decision: reject all guide-first outputs from this run for training. IP-Adapter + ControlNet improved pose stability over prompt-only generation, but the surface still reads as striped/scaly generic theropod skin rather than dense dromaeosaur plumage, and the follow-up feather-band inpaint did not fix that. The next route needs stronger project-owned feather references or a feather-aware checkpoint before expanding the LoRA seed pool.

### Review Result: `dromaeosaur_reference_control_v1`

Tracked reference files:

- `references/dromaeosaur_plumage_reference_v1.png`
- `references/dromaeosaur_plumage_reference_v1-sheet.png`
- `references/dromaeosaur_feather_mass_guide_v1.png`

Tracked review files:

- `review/dromaeosaur_reference_control_v1_review.json`
- `review/dromaeosaur_plumage_ref_ipcontrol_v1_rejected_contact_sheet.png`
- `review/dromaeosaur_feathermass_control_v1_rejected_contact_sheet.png`

Decision: keep the project-owned references as diagnostic infrastructure, but reject all generated outputs from these runs for training. The paintover reference and feather-mass control guide made the desired feather intent more explicit, yet RealVisXL still filled the animal with stripe/scaly surfaces rather than convincing downy plumage. The next route needs a feather-aware checkpoint/LoRA branch or a stronger direct image-editing step before adding new `train_seed` items.

### Review Result: `velociraptor_sickle_toe_v11`

Tracked review files:

- `review/velociraptor_sickle_toe_v11_review.json`
- `assets/dinosaurs/velociraptor-review-options-v17.png`
- `assets/dinosaurs/velociraptor-prompt-v11-rejection-crops.png`

Decision: reject all stricter whole-body prompt-only sickle-toe outputs for candidate promotion and training. The prompt reduced some oversized-claw risk, but the outputs lost too much feathered dromaeosaur identity, drifted toward smooth generic theropods or bird-like legs, and weakened the folded forelimb cue. Keep `velociraptor-mongoliensis-small-sickle-imagegen-v9.png` first in the app. The next route should use a stronger foot-structure ControlNet/depth/line guide, a feather-aware route, or a custom dromaeosaur LoRA branch that locks toe topology before texture generation.

### Foot Topology Control Route

Tracked control files:

- `assets/dinosaurs/velociraptor-mongoliensis-foot-topology-guide-v1.png`
- `assets/dinosaurs/velociraptor-foot-topology-crops-v12.png`
- `assets/dinosaurs/velociraptor-review-options-v18.png`
- `foot_topology_prompt_schedule.json`

Decision: keep the new foot topology guide as `control_reference`, not as a training image or promoted paleoart. It exists to lock the failed detail from the v10/v11 loops: two long walking toes plus one raised second-toe sickle claw attached to the foot, without floating crescents or oversized bird talons. Use `foot_topology_prompt_schedule.json` for the next ControlNet/depth/line or low-denoise i2i experiment before adding any new outputs to the train seed pool.

### Identity Body-Lock Control Route

Tracked control files:

- `assets/dinosaurs/velociraptor-mongoliensis-identity-bodylock-guide-v1.png`
- `assets/dinosaurs/velociraptor-identity-bodylock-crops-v13.png`
- `assets/dinosaurs/velociraptor-review-options-v19.png`
- `identity_bodylock_prompt_schedule.json`

Decision: keep the identity body-lock guide as `control_reference`, not as direct training art or final paleoart. It exists to lock the full Velociraptor identity bundle before texture polish: narrow toothed non-beak snout, folded feathered forelimbs held close to the ribs, dense body plumage, long stiff balancing tail, two hind legs, and attached raised second-toe sickle claws. Use it before another prompt-only escalation, because the v11 loop reduced some claw risk only by losing dromaeosaur identity.

### Recent Head And Toe Gates

Tracked review files:

- `review/velociraptor_modest_sickle_i2i_v25_review.json`
- `review/velociraptor_less_bird_head_i2i_v27_review.json`
- `review/velociraptor_front_hook_micro_i2i_v28_review.json`
- `review/velociraptor_head_micro_i2i_v29_review.json`
- `review/velociraptor_second_toe_i2i_v30_review.json`
- `assets/dinosaurs/velociraptor-modest-sickle-i2i-v25-review-sheet.png`
- `assets/dinosaurs/velociraptor-less-bird-head-i2i-v27-review-sheet.png`
- `assets/dinosaurs/velociraptor-front-hook-micro-i2i-v28-review-sheet.png`
- `assets/dinosaurs/velociraptor-head-micro-i2i-v29-review-sheet.png`
- `assets/dinosaurs/velociraptor-second-toe-i2i-v30-review-sheet.png`

Decision: keep v25, v27, and v29 as `review_hold` comparisons only. They preserve parts of the current v9 body/head balance, but do not improve enough to replace it. Keep v23, v24, v26, v28, and v30 as `reject_reference` gates. They document routes that either collapse into guide-like art, fail to fix the front-hook/attached second-toe topology, or change too little to count as anatomical progress. Future automation must not treat these as positive samples; use them to reject bird-head drift, flat guide-style output, local foot edits without attached raised second-toe proof, and any candidate whose close crops cannot show two grounded walking toes plus one raised sickle toe.

### Review Result: `velociraptor_identity_bodylock_v31_v32`

Tracked review files:

- `review/velociraptor_identity_v31_v32_review.json`
- `assets/dinosaurs/velociraptor-identity-v31-v32-rejection-sheet.png`
- `assets/dinosaurs/velociraptor-identity-v31-v32-rejection-crops.png`

Decision: reject both the clean body-lock IP-Control route and the low-denoise head/foot i2i route for promotion and training. V31 follows the body-lock guide strongly enough to lose feathered dromaeosaur identity and become a smoother generic theropod. V32 preserves more of the v9 source, but it shrinks or softens the foot evidence and does not prove attached raised second-toe sickle-claw topology. Keep current v9 first; the next useful route needs a curated dromaeosaur/foot mini-LoRA or multi-control workflow that locks foot topology without erasing plumage.

### Review Result: `velociraptor_p1_v36_v38`

Tracked review files:

- `review/velociraptor_p1_v36_v38_review.json`
- `assets/dinosaurs/velociraptor-p1-v36-v38-review-sheet.png`
- `assets/dinosaurs/velociraptor-p1-v36-v38-crops.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v38-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v36-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v37-source-candidate.png`
- `review/dromaeosaur_seed_manifest_sheet_v5.png`

Decision: keep `velociraptor_imagegen_v38_modest_sickle_source_candidate` as `review_hold` only. It is the best new prompt-only route for a subtler attached raised second-toe sickle cue while preserving the toothed snout, feathered body, folded forelimbs, and long tail, but its near-foot crop is not final-proof and the far-foot/hand-claw reads remain risky. Keep `velociraptor_small_sickle_v9` first and keep v38 outside positive LoRA training. Keep v36 and v37 as `reject_reference` examples because both overcorrect the foot target into oversized hook-like claws.

### Review Result: `velociraptor_p2_v39_v41`

Tracked review files:

- `review/velociraptor_p2_v39_v41_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v6.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v39-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v40-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v41-source-candidate.png`
- `assets/dinosaurs/velociraptor-p2-v39-v41-review-sheet.png`
- `assets/dinosaurs/velociraptor-p2-v39-v41-crops.png`

Decision: add v39 and v41 to the app and manifest as `review_hold`, not as `train_seed` and not as representatives. V39 is the best fresh whole-body balance because it keeps a closed toothed non-beak snout, dense feathers, folded forelimbs, and a restrained raised-claw cue, but both feet still do not prove two grounded walking toes plus one attached raised second-toe sickle claw. V41 is useful for foot visibility but risks reading the near raised claw as an oversized front hook. Keep v40 as a `reject_reference` because the open mouth, eye expression, and paired hooks are too dramatic. Keep v9 first until head identity and exact foot topology pass together.

### Review Result: `velociraptor_p3_v42_v44`

Tracked review files:

- `review/velociraptor_p3_v42_v44_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v7.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v42-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v43-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v44-source-candidate.png`
- `assets/dinosaurs/velociraptor-p3-v42-v44-review-sheet.png`
- `assets/dinosaurs/velociraptor-p3-v42-v44-crops.png`

Decision: keep v43 as the best P3 `review_hold`, not as `train_seed` and not as a representative. It has the best new balance of toothy non-beak head, small feathered dromaeosaur body, long stiff tail, and attached modest sickle-claw cue, but the folded forelimb can read wing-like and the feet still do not prove final two-walking-toes plus raised-second-toe topology. Keep v44 as a `review_hold` foot-visibility comparison because the foot area is useful but the near claw can read as an oversized hook. Keep v42 as `reject_reference` because the raised claws are too talon-like. The next route should use v43 only as a localized i2i/ControlNet source with strict rejection for bird-head, wing-arm, detached crescent, or giant-hook drift.

### Review Result: `velociraptor_p4_v45_v47`

Tracked review files:

- `review/velociraptor_p4_v45_v47_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v8.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v45-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v46-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v47-source-candidate.png`
- `assets/dinosaurs/velociraptor-p4-v45-v47-review-sheet.png`
- `assets/dinosaurs/velociraptor-p4-v45-v47-crops.png`

Decision: keep v47 as the best P4 `review_hold`, not as `train_seed` and not as a representative. It has the best closed toothy non-beak head, folded forelimbs, feathered dromaeosaur body, stiff tail, and attached near-foot sickle cue from this pass, but the claw is still slightly large and the far foot does not prove final two-walking-toes plus raised-second-toe topology. Keep v45 as a secondary `review_hold` because its head/body read is useful but the forelimb can still read wing-like. Keep v46 as `reject_reference` because the open mouth and paired hooks risk monster-like/oversized-talon drift. Keep v9 first until head identity, folded non-wing forelimbs, exact foot topology, two hind legs, and a single tail pass together.

### Review Result: `velociraptor_p5_v48_v50`

Tracked review files:

- `review/velociraptor_p5_v48_v50_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v9.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v48-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v49-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v50-source-candidate.png`
- `assets/dinosaurs/velociraptor-p5-v48-v50-review-sheet.png`
- `assets/dinosaurs/velociraptor-p5-v48-v50-crops.png`

Decision: keep v50 as the best P5 `review_hold`, not as `train_seed` and not as a representative. It has the best new head/body/tail balance with a narrow toothy non-beak head, feathered dromaeosaur body, compact folded forelimbs, full stiff tail, and visible feet, but both raised sickle claws remain large, dark, and hook-like instead of modest attached second toes. Keep v48 as a black-hook review hold and v49 as a wing/hidden-foot review hold. Keep v9 first until head identity, folded non-wing forelimbs, exact foot topology, two hind legs, and a single tail pass together. The next useful route is localized low-denoise foot i2i or stronger topology control that preserves v50 head/body/tail while reducing black hook claws.

### Review Result: `velociraptor_p6_v51_v56`

Tracked review files:

- `review/velociraptor_p6_v51_v56_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v10.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v51-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v52-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v53-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v54-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v55-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v56-source-candidate.png`
- `assets/dinosaurs/velociraptor-p6-v51-v56-review-sheet.png`
- `assets/dinosaurs/velociraptor-p6-v51-v56-crops.png`

Decision: promote v56 to the app first slot as the current `count-level pass` and use it as the project-owned smoke-test `train_seed`. V56 improves over v9/v50 by keeping a toothed non-beak head, feathered dromaeosaur body, folded forelimbs, long stiff tail, two hind legs, and visible attached raised second-toe cues without returning to the large black hook-claw drift. It is still not final: exact two-walking-toes plus raised-second-toe topology, folded forelimb feather shape, skull/eye proportions, and tail feather stiffness need close reference review. Keep v9 as the previous first hold, v54/v55 as clearer-claw holds with slightly dramatic claw scale, v53/v51 as subtle-toe holds, and v52/v50 as hook-risk holds.

### Review Result: `velociraptor_p7_v57_v59`

Tracked review files:

- `review/velociraptor_p7_v57_v59_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v11.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v57-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v58-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v59-source-candidate.png`
- `assets/dinosaurs/velociraptor-p7-v57-v59-review-sheet.png`
- `assets/dinosaurs/velociraptor-p7-v57-v59-crops.png`

Decision: keep v56 in the app first slot and keep it as the only current `train_seed`. P7 did not beat v56: v57 has a good feathered body and clearer feet but both raised claws trend curled and hook-like; v58 is a `reject_reference` because the feet become crowded, overbuilt, and unclear in toe count; v59 has a good toothed head and side silhouette but the raised claws are too hook-like for promotion. Use v57/v59 as review holds and v58 as a hard reject gate for crowded toe-count and hook-claw overcorrection. The next useful route should preserve v56 and apply localized foot i2i or stronger dromaeosaur foot topology control rather than another broad prompt-only pass.

### Review Result: `velociraptor_p8_v60_v63`

Tracked review files:

- `review/velociraptor_p8_v60_v63_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v12.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v60-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v61-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v62-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v63-source-candidate.png`
- `assets/dinosaurs/velociraptor-p8-v60-v63-review-sheet.png`
- `assets/dinosaurs/velociraptor-p8-v60-v63-crops.png`

Decision: promote v63 to the app first slot and use it as the current positive smoke-test `train_seed`. V63 improves the gallery-wide color separation problem with dark charcoal/umber speckled plumage, a small rust face mask, pale throat/belly, and narrow pale tail bands while preserving the narrow toothed non-beak snout, compact folded forelimbs, two hind legs, and long stiff tail. Its foot anatomy remains count-level, not final, but it does not worsen the v56 toe gate at app scale. Keep v56 as the previous safety comparison hold. Keep v60 and v62 as hook-risk color holds, and keep v61 as a wing-risk color hold. The next useful route should be foot-local i2i or foot-topology ControlNet over v63, preserving the new color pattern while reducing hook-claw exaggeration.

### Review Result: `velociraptor_p9_v64_v66`

Tracked review files:

- `review/velociraptor_p9_v64_v66_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v13.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v64-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v65-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v66-source-candidate.png`
- `assets/dinosaurs/velociraptor-p9-v64-v66-review-sheet.png`
- `assets/dinosaurs/velociraptor-p9-v64-v66-crops.png`

Decision: keep v63 as the current app first slot and only add v65 as a `review_hold`. V65 is the best P9 candidate for a less bird-like toothed head, long stiff tail, and distinct dark speckled/rust-face color, but its raised sickle claw is still too large and hook-like for promotion. Keep v64 and v66 as `reject_reference` examples: v64 overbuilds the near raised claw and risks wing-fan forelimbs, while v66 has useful color contrast but long hand-like forelimb fingers and oversized raised claws. The next useful route remains localized foot i2i or foot-topology ControlNet over v63 or v65, with automatic rejection for modern-bird head, wing-fan arms, long hands, detached crescent claws, giant hooks, or crowded toe counts.

### Review Result: `velociraptor_p10_v67_v69`

Tracked review files:

- `review/velociraptor_p10_v67_v69_review.json`
- `review/dromaeosaur_seed_manifest_sheet_v14.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v67-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v68-source-candidate.png`
- `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v69-source-candidate.png`
- `assets/dinosaurs/velociraptor-p10-v67-v69-review-sheet.png`
- `assets/dinosaurs/velociraptor-p10-v67-v69-crops.png`

Decision: keep v63 as the current app first slot and only add v68/v69 as `review_hold` color/head references. V68 is the best P10 balance of dark speckled plumage, rust face, toothed non-beak head, folded arms, barred tail, and less-overbuilt feet, but its raised second-toe sickle claw is still too large for promotion. V69 is a secondary color/head hold with a similar hook-claw risk. Keep v67 as `reject_reference` because the forelimb reads wing-fan-like and both raised claws become oversized hooks. The next useful route is still foot-local i2i or foot-topology ControlNet over v63, v65, or v68; do not promote any prettier render unless close crops prove two grounded walking toes plus one modest attached raised second-toe claw.

### Legacy Plumage And Rear-Foot Cleanup Gate

Tracked review files:

- `review/velo_refined_plumage_sickle_v1_review.json`
- `review/velo_rear_sickle_cleanup_v1_review.json`
- `assets/dinosaurs/velociraptor-mongoliensis-plumage-sickle-refined-v1.png`
- `assets/dinosaurs/velociraptor-mongoliensis-rearfoot-cleanup-v1.png`

Decision: keep both legacy cleanup outputs as `reject_reference` items, not app representatives and not positive LoRA seeds. The earlier coarse gate overvalued feather mass and local rear-foot cleanup; direct identity review shows that both still read too bird-like in the head and do not prove the attached raised second-toe sickle claw. These images are useful only as negative gates for future automation: a candidate must keep a narrow toothed non-beak snout, dense folded plumage, long stiff tail, two hind legs, and a readable raised second-toe claw together.

### Seed Pool Correction: Bird-Head Drift

Decision: demote `velociraptor_background_v1`, `velociraptor_featherband_v3`, and `velociraptor_ipadapter_clean_v2` from `train_seed` to `reject_reference`. They preserve some body, tail, or feather-band cues, but their head silhouettes read too modern-bird-like and their raised second-toe claw evidence is weak. The current positive smoke-test seed is now `velociraptor_imagegen_v63_dark_speckled_plumage_seed`; v56 is the previous app-first hold, v9 remains an older hold, and v50 remains useful only as a local foot-edit source because it reinforces black hook-claw drift.
