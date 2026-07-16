# stegosaur_plates_tailspikes LoRA Prep

Purpose: prepare a copyright-safe custom LoRA route for `Stegosaurus stenops` and close stegosaurian body plans. The current public-LoRA, prompt-only, ControlNet, and narrow inpaint routes cannot reliably keep all required cues at once: broad separated dorsal plates, a quadrupedal Stegosaurus body, and a four-spike thagomizer.

## Source Policy

Use only:

- internal AI-generated candidates already produced for this project,
- hand-authored control guides from this project,
- future synthetic outputs generated from the prompt schedule in this folder after human review.

Do not use museum photos, copyrighted paleoart, movie/game stills, or public LoRA outputs with unclear provenance as training images. Museum/science links remain reference anchors only, not training data.

## Seed Roles

- `train_seed`: can be materialized as image/caption pairs for a tiny proof dataset, but still needs review before any real LoRA run.
- `control_reference`: useful for ControlNet, prompt planning, and caption validation, but too guide-like or composited for direct LoRA training.
- `review_hold`: useful as a visual comparison, but excluded because one key feature is weak or the image is too flat/guide-like.
- `reject_reference`: failure case kept to prevent repeating known bad directions; never train on it.

Tracked manifest review sheet:

- `review/stegosaur_seed_manifest_sheet_v16.png`

Use this sheet before materializing seeds. It separates `train_seed`, `control_reference`, `review_hold`, and `reject_reference` items so guide images or known failures are not accidentally copied into a LoRA training folder.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py `
  --manifest tools\comfyui\lora_training\stegosaur_plates_tailspikes\seed_manifest.json `
  --output-dir tools\comfyui\lora_training\stegosaur_plates_tailspikes\materialized_seed
```

The command writes an ignored local folder:

`tools/comfyui/lora_training/stegosaur_plates_tailspikes/materialized_seed/`

It contains copied image files, matching `.txt` captions, a materialized manifest, and a contact sheet. Keep that folder out of git; commit only reviewed source assets, manifests, and scripts.

## Training Gate

Do not train a promoted LoRA from the seed set alone. The seed set is for smoke tests and caption validation. Before a usable LoRA attempt, expand to at least 40 reviewed synthetic images with:

- at least 20 side-profile full-body images with broad separated dorsal plates,
- at least 12 images where the four-spike thagomizer is visible and countable,
- multiple plate sizes: smaller near neck and tail base, largest over hips and mid-back,
- visible gaps between plates, not a fused scalloped fan or continuous sail,
- quadrupedal stance with one head and one tail,
- no plant leaves, leaf veins, comb teeth, turtle shells, sauropod neck drift, theropod biped drift, text, logos, or signatures.

Use `synthetic_prompt_schedule.json` as the broad expansion queue and `plate_topology_prompt_schedule.json` when the next pass specifically needs to lock staggered two-row plate anatomy. Treat every output as `needs_review`; only manually accepted images should ever be copied into the tracked seed manifest or materialized for training.

## Current Control Target

The current natural seed target is:

- `assets/dinosaurs/stegosaurus-stenops-imagegen-v92-source-candidate.png`
- current crop gate: `assets/dinosaurs/stegosaurus-p11-v100-v102-crops.png`
- current review sheet: `assets/dinosaurs/stegosaurus-p11-v100-v102-review-sheet.png`
- previous crop gate: `assets/dinosaurs/stegosaurus-p10-v97-v99-crops.png`
- previous review sheet: `assets/dinosaurs/stegosaurus-p10-v97-v99-review-sheet.png`
- previous crop gate: `assets/dinosaurs/stegosaurus-p9-v93-v96-crops.png`
- previous review sheet: `assets/dinosaurs/stegosaurus-p9-v93-v96-review-sheet.png`
- previous crop gate: `assets/dinosaurs/stegosaurus-p8-v90-v92-crops.png`
- previous review sheet: `assets/dinosaurs/stegosaurus-p8-v90-v92-review-sheet.png`
- previous promotion crop gate: `assets/dinosaurs/stegosaurus-p6-v84-v86-crops.png`
- previous promotion review sheet: `assets/dinosaurs/stegosaurus-p6-v84-v86-review-sheet.png`

This is still the current app-first count-level pass because it fixes two review issues at once: the dorsal plates now read as separate rust-red and pale-bone rough bony/keratin structures rather than same-color skin, and the tail is closest to four countable thagomizer spikes rising upward in paired V shapes. P9 clarified that this is not final approval: all four spikes must rise upward relative to the ground or horizon, and any horizontal tail-point or ground-parallel lower spike is a hard reject. P10 further clarified that the problem is ground-relative, not tail-relative: the lower spikes must not run along the tail shaft, and overcorrected five-spike/radial clusters are also rejects. P11 confirmed that whole-body prompting can improve rough plate material but still fails the tail gate through five/radial counts, straight spear drift, or tail-parallel lower points. It is a `train_seed` candidate for smoke testing only; exact alternating row placement, plate bases, far-side thagomizer clarity, tail-spike ground angle, and toe details still need final reference review.

The previous natural seed target remains useful:

- `assets/dinosaurs/stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png`
- crop gate: `assets/dinosaurs/stegosaurus-alternatingplate-fourspike-crops-v6.png`

This was the previous app-scale balance of a natural Stegosaurus body, broad dorsal plates, four planted feet, and a countable four-spike thagomizer. Keep it as a positive smoke-test seed and comparison gate below v86 because v86 has stronger first-card recognition and clearer separated tail spikes.

The clearest plate-topology structure target is:

- `assets/dinosaurs/stegosaurus-stenops-plate-topology-guide-v1.png`
- crop gate: `assets/dinosaurs/stegosaurus-plate-topology-crops-v12.png`
- review sheet: `assets/dinosaurs/stegosaurus-review-options-v46.png`
- generator: `tools/comfyui/scripts/draw_stegosaurus_plate_topology_guide.py`

This guide uses colored near-row and far-row sockets to make the staggered two-row plate arrangement explicit. It is a project-owned diagnostic reference, not final paleoart and not a direct `train_seed`. Use it for ControlNet/depth/line guidance when candidates collapse into a single row, connected sail, or decorative petal plates.

The latest no-label v6-photo plate control target is:

- `assets/dinosaurs/stegosaurus-stenops-plate-silhouette-control-v65.png`
- mask: `assets/dinosaurs/stegosaurus-plate-silhouette-control-mask-v65.png`
- review sheet: `assets/dinosaurs/stegosaurus-plate-silhouette-control-v65-review-sheet.png`
- rejection crops: `assets/dinosaurs/stegosaurus-plate-silhouette-ipcontrol-v65-rejection-crops.png`
- generator: `tools/comfyui/scripts/draw_stegosaurus_plate_silhouette_control_v65.py`

This control source is useful because it keeps the v6 natural body while making the target plate silhouettes clearer than the clean cartoon guide. It is still not a direct `train_seed`: the paired v65 IP-Control run drifted into generic herbivore bodies, comb/fan/neck-frill plate reads, and missing thagomizer evidence. Use it as a negative lesson and control reference only; the next useful step is a Stegosauridae-specific LoRA or a reviewed plate-structure training set.

The older combined structure target remains useful:

- `assets/dinosaurs/stegosaurus-stenops-plate-thagomizer-reference-v1.png`
- contact sheet: `assets/dinosaurs/stegosaurus-plate-thagomizer-reference-sheet-v1.png`
- generator: `tools/comfyui/scripts/draw_stego_plate_thagomizer_reference.py`

This is a project-owned diagnostic reference, not final paleoart and not a direct `train_seed`. It exists to keep both Stegosaurus gates visible in one image: broad separated alternating dorsal plates and exactly four countable thagomizer spikes.

The current body-proportion control target is:

- `assets/dinosaurs/stegosaurus-stenops-lowbody-plate-thagomizer-reference-v1.png`
- contact sheet: `assets/dinosaurs/stegosaurus-lowbody-plate-thagomizer-reference-sheet-v1.png`
- generator command: `tools/comfyui/scripts/draw_stego_plate_thagomizer_reference.py --profile lowbody`

Use this low-body reference when ControlNet starts turning the Stegosaurus into a round shell-backed animal. It is still a guide only, not direct training data.

## Synthetic Schedule Smoke Run

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\run_lora_seed_schedule.py `
  --schedule tools\comfyui\lora_training\stegosaur_plates_tailspikes\synthetic_prompt_schedule.json `
  --limit 4 `
  --seed-base 2026062400 `
  --prefix stegosaur_lora_seed_v1 `
  --ckpt-name RealVisXL_V5.0_fp16.safetensors `
  --steps 32 `
  --cfg 4.6
```

The schedule runner writes ignored review outputs under `tools/comfyui/outputs/`, including a results JSON file and contact sheet. Treat every output as `needs_review`; only manually accepted images should ever be copied into this tracked seed manifest or materialized for training.

### Review Result: `stegosaur_lora_seed_v1`

Tracked review files:

- `review/stegosaur_lora_seed_v1_review.json`
- `review/stegosaur_lora_seed_v1_rejected_contact_sheet.png`

Decision: reject all prompt-only RealVisXL outputs from this run for training. The outputs drifted toward theropod or generic dinosaur body plans and did not keep broad separated dorsal plates or a countable four-spike thagomizer. This confirms that the Stegosaurus route needs feature-specific internal guides, reviewed synthetic expansions, or a separate Stegosaurus-compatible LoRA branch rather than more prompt-only retries.

### Review Result: `stego_clearplates_v1`

Tracked review files:

- `review/stego_clearplates_v1_review.json`
- `review/stego_clear_dorsal_plates_angular_v1_contact_sheet.png`
- `review/stego_clearplates_refine_v1_rejected_contact_sheet.png`
- `review/stego_clearplates_ipcontrol_v1_rejected_contact_sheet.png`
- `review/stego_plate_silhouette_angular_v1_rejected_contact_sheet.png`

Decision: keep the local clear-plate paintovers as control/reference material only. They make the broad separated plate target much easier to see, but the plates still read as composited slabs. Refiner passes either preserve that pasted look or fuse the row back into a connected ridge, and IP-Adapter + ControlNet breaks the side-profile Stegosaurus body. Do not add these outputs to `train_seed`; use them only as structure references for a stronger direct image model output, a Stegosaurus-compatible LoRA branch, or future custom LoRA expansion.

### Review Result: `stego_sdxlbase_lora_probe_v1`

Tracked review files:

- `review/stego_sdxlbase_lora_probe_v1_review.json`
- `review/stegosaur_sdxlbase_seed_v1_rejected_contact_sheet.png`
- `review/stego_sdxlbase_dinogenv2_v1_rejected_contact_sheet.png`

Decision: reject all SDXL base and generic Dinosaur Generator v2 probe outputs for both training and app use. Plain SDXL base did not preserve the four-spike thagomizer and often drifted into theropod, rhinoceros, or generic monster shapes. Adding `Dinosaur_Generator_v2.0-000011.safetensors` over SDXL base made the body-plan drift worse and reduced plates to small comb-like spines. This confirms that broad checkpoint switching and generic dinosaur LoRA probing are not the next useful Stegosaurus path.

### Review Result: `stego_combined_reference_generation_v1`

Tracked review files:

- `review/stego_combined_reference_generation_v1_review.json`
- `review/stego_combined_ref_i2i_v1_contact_sheet.png`
- `review/stego_combined_ref_ipcontrol_v1_contact_sheet.png`
- `review/stego_tailref_combined_control_v1_contact_sheet.png`
- `review/stego_tailref_combined_midcontrol_v1_contact_sheet.png`
- `assets/dinosaurs/stegosaurus-review-options-v34.png`

Decision: promote only `assets/dinosaurs/stegosaurus-stenops-plate-thagomizer-ipcontrol-v1.png` to the app as `anatomy review`, not to `train_seed`. The selected low-weight IP-Adapter plus moderate ControlNet pass is the first app-facing Stegosaurus output in this branch with both broad upright plates and a visible four-spike thagomizer. It remains excluded from training promotion because the torso is too rounded, plate bases can still read shell-like, and limb placement needs stricter review.

### Review Result: `stego_lowbody_reference_generation_v1`

Tracked review files:

- `review/stego_lowbody_reference_generation_v1_review.json`
- `review/stego_lowbody_angularref_control_v1_contact_sheet.png`
- `review/stego_lowbody_newref_control_v1_contact_sheet.png`
- `review/stego_lowbody_tailref_control_v1_contact_sheet.png`
- `assets/dinosaurs/stegosaurus-review-options-v35.png`

Decision: promote only `assets/dinosaurs/stegosaurus-stenops-lowbody-plate-thagomizer-ipcontrol-v1.png` to the app as the first `anatomy review` candidate, not to `train_seed`. The selected angular-reference plus low-body ControlNet pass reduces the round shell-like torso while preserving broad dorsal plates and a visible thagomizer. It remains excluded from training promotion because the tail spikes are small, plate separation is imperfect, and hidden legs still need close review.

### Review Result: `stego_lowbody_tailspike_refine_v1`

Tracked review files:

- `review/stego_lowbody_tailspike_refine_v1_review.json`
- `review/stego_lowbody_tailspike_guide_v1_contact_sheet.png`
- `review/stego_lowbody_tailspike_guide_v1_tail_crops.png`
- `review/stego_lowbody_tailspike_refine_v1_contact_sheet.png`
- `review/stego_lowbody_tailspike_refine_v1_tail_crops.png`
- `review/stego_lowbody_tailspike_strict_v1_contact_sheet.png`
- `review/stego_lowbody_tailspike_strict_v1_tail_crops.png`

Decision: no app promotion. The local four-spike overlay aligned to the low-body candidate, but it stayed too translucent/guide-like. Low-denoise refine and stricter tail-tip inpaint preserved the body but did not make the fourth tail spike materially clearer, so the current low-body primary remains the best app-facing Stegosaurus candidate.

### Review Result: `stegosaurus_plate_topology_lowdenoise_v68`

Tracked review files:

- `review/stego_plate_topology_lowdenoise_v68_review.json`
- `review/stegosaur_seed_manifest_sheet_v4.png`
- `assets/dinosaurs/stegosaurus-stenops-plate-topology-lowdenoise-v68.png`
- `assets/dinosaurs/stegosaurus-plate-topology-lowdenoise-v68-review-sheet.png`
- `assets/dinosaurs/stegosaurus-plate-topology-lowdenoise-v68-crops.png`

Decision: add the selected seed `2026070162`, denoise `0.18` output to the app and manifest as `review_hold`, not as the representative candidate and not as `train_seed`. It preserves the v6 body, feet, tail, and visible thagomizer well enough for direct comparison, but it does not prove a stronger staggered two-row plate topology than the current v6 candidate. Keep v6 first until plate placement and four-spike thagomizer evidence are both stronger in the same image.

### Review Result: `stegosaurus_p1_v70_v71`

Tracked review files:

- `review/stegosaurus_p1_v70_v71_review.json`
- `review/stegosaur_seed_manifest_sheet_v7.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v70-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v71-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p1-v70-v71-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p1-v70-v71-crops.png`

Decision: add v70 and v71 to the app and manifest as `review_hold`, not as `train_seed` and not as representatives. V71 gives the strongest new prompt-only staggered plate-overlap cue, but the four-spike thagomizer count is not reliable enough at crop scale. V70 has broad plate surfaces and a more readable tail-spike cue, but the plate bases still read mostly as one row. Keep v6 first until one candidate proves both staggered two-row plates and exactly four thagomizer spikes together.

### Review Result: `stegosaurus_p2_v72_v74`

Tracked review files:

- `review/stegosaurus_p2_v72_v74_review.json`
- `review/stegosaur_seed_manifest_sheet_v8.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v72-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v73-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v74-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p2-v72-v74-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p2-v72-v74-crops.png`

Decision: add v72 and v73 to the app and manifest as `review_hold`, not as `train_seed` and not as representatives. V72 is the best new broad-plate identity candidate: the plates read as rough separated bony slabs with visible gaps, much closer to the requested Stegosaurus plate signal. It still fails promotion because the tail tip can read as more than four thagomizer spikes. V73 has cleaner plate gaps but undercounts the thagomizer. Keep v74 as a `reject_reference`: the tail weapon is large, but the staged tail pose, leg read, and weaker plate count make it unsafe for app promotion or positive training. Keep v6 first until broad separated plates and exactly four tail spikes pass together.

### Review Result: `stegosaurus_p3_v75_v77`

Tracked review files:

- `review/stegosaurus_p3_v75_v77_review.json`
- `review/stegosaur_seed_manifest_sheet_v3.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v75-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v76-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v77-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p3-v75-v77-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p3-v75-v77-crops.png`

Decision: add v77 to the app and manifest as `review_hold`, not as `train_seed` and not as the representative. It has the strongest fresh broad separated plate mass and a good low Stegosaurus body, but the tail tip still overcounts the thagomizer. Keep v75 and v76 as `reject_reference`: both help document the broad-plate target, but v75 clearly overcounts tail spikes and v76 adds leaf-vein plate risk on top of the tail overcount. Keep only v6 as the positive smoke-test seed until broad separated dorsal plates and exactly four thagomizer spikes pass together.

### Review Result: `stegosaurus_p4_v78_v80`

Tracked review files:

- `review/stegosaurus_p4_v78_v80_review.json`
- `review/stegosaur_seed_manifest_sheet_v9.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v78-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v79-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v80-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p4-v78-v80-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p4-v78-v80-crops.png`

Decision: add v79 to the app and manifest as `review_hold`, not as `train_seed` and not as the representative. It is the best new compromise between broad separated plates and a near-four tail read, but the lower thagomizer overlap can still read as an extra spike. Keep v78 and v80 as `reject_reference`: v78 is useful as a broad-plate target but clearly overcounts tail spikes, and v80 has a good side silhouette but can read as an extra lower tail spike. Keep only v6 as the positive smoke-test seed until broad separated dorsal plates and exactly four thagomizer spikes pass together.

### Review Result: `stegosaurus_p5_v81_v83`

Tracked review files:

- `review/stegosaurus_p5_v81_v83_review.json`
- `review/stegosaur_seed_manifest_sheet_v10.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v81-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v82-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v83-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p5-v81-v83-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p5-v81-v83-crops.png`

Decision: add v82 and v83 to the app and manifest as `review_hold`, not as `train_seed` and not as representatives. V82 is the best fresh tail-count-locked candidate because it combines broad separated dorsal plates with the clearest near-four thagomizer read in this pass, but the lower right tail-spike geometry can still be read as overlapping or duplicated. Keep v83 as a secondary hold for body and plate comparison, and keep v81 as `reject_reference` because it clearly overcounts the thagomizer. Keep only v6 as the positive smoke-test seed until broad separated dorsal plates and exactly four thagomizer spikes pass together.

### Review Result: `stegosaurus_p6_v84_v86`

Tracked review files:

- `review/stegosaurus_p6_v84_v86_review.json`
- `review/stegosaur_seed_manifest_sheet_v11.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v84-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v85-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v86-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p6-v84-v86-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p6-v84-v86-crops.png`

Decision: promote v86 to the app as the new `count-level pass` and add it to the manifest as a positive smoke-test `train_seed`. It has the best current combined Stegosaurus read: broad separated dorsal plates, low quadrupedal body, small low head, four visible planted feet, long tail, and exactly four separated thagomizer spikes. Keep v84 as `review_hold` because it has a strong four-spike tail but oversized mid-back plates. Keep v85 as `reject_reference` because the tail weapon can read as only three countable spikes. Keep v6 as a previous positive seed and comparison gate below v86.

### Review Result: `stegosaurus_p7_v87_v89`

Tracked review files:

- `review/stegosaurus_p7_v87_v89_review.json`
- `review/stegosaur_seed_manifest_sheet_v12.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v87-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v88-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v89-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p7-v87-v89-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p7-v87-v89-crops.png`

Decision: keep v86 in the app first slot and keep v86/v6 as the only current positive smoke-test `train_seed` items. P7 did not beat v86: v87 is a `reject_reference` because the tail can read as five thagomizer spikes; v88 is a `review_hold` because the tail is near-four but the plates become larger, rounder, and more leaf/fan-like; v89 is a `review_hold` because the body and tail are stable but plate topology does not improve over v86 and head framing is tighter. The next useful route should be localized plate-row i2i or Stegosauridae-specific LoRA/control work that offsets plate bases while preserving v86's reliable four-spike tail.

### Review Result: `stegosaurus_p8_v90_v92`

Tracked review files:

- `review/stegosaurus_p8_v90_v92_review.json`
- `review/stegosaur_seed_manifest_sheet_v13.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v90-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v91-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v92-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p8-v90-v92-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p8-v90-v92-crops.png`

Decision: promote v92 to the app as the new `count-level pass` and add it to the manifest as the current positive smoke-test `train_seed`. V92 is the best current response to review feedback: dorsal plates are visibly separate rough bony/keratin structures with rust-red centers and pale chipped rims, and the thagomizer is closest to four countable spikes rising upward in paired V shapes. Keep v90 and v91 as `review_hold` only because their plate material is useful but tail angle/count is less safe. Demote v86 to `review_hold` comparison because its body and tail remain useful, but its plates are too close to the skin color and can read leather-like under the new material gate.

### Review Result: `stegosaurus_p9_v93_v96`

Tracked review files:

- `review/stegosaurus_p9_v93_v96_review.json`
- `review/stegosaur_seed_manifest_sheet_v14.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v93-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v94-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v95-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v96-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p9-v93-v96-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p9-v93-v96-crops.png`

Decision: keep v92 first and reject all P9 prompt-only retries from positive training. V93 preserves useful bony plate material but keeps a horizontal tail extension; v94 reduces that flat lower spike but undercounts the thagomizer; v95 reads as upward prongs plus a horizontal tail point; v96 reads as three spikes plus a small side nub. The next route should be tail-local ControlNet or inpaint over the current v92 body, with the tail shaft ending at a rounded thagomizer base and exactly four spikes rising above the ground/horizon.

### Review Result: `stegosaurus_p10_v97_v99`

Tracked review files:

- `review/stegosaurus_p10_v97_v99_review.json`
- `review/stegosaur_seed_manifest_sheet_v15.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v97-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v98-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v99-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p10-v97-v99-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p10-v97-v99-crops.png`

Decision: keep v92 first and reject all P10 prompt-only retries from positive training. V97 and v98 preserve useful body and plate material, but each still leaves a lower thagomizer point that reads too horizontal or tail-parallel. V99 moves the spikes upward more successfully, but can read as five spikes or a radial cluster rather than exactly four. The next useful route is not another whole-body prompt retry; use tail-local ControlNet/inpaint over v92 with a rounded tail base, exactly four countable spikes, and both lower spikes angled upward relative to the ground/horizon.

### Review Result: `stegosaurus_p11_v100_v102`

Tracked review files:

- `review/stegosaurus_p11_v100_v102_review.json`
- `review/stegosaur_seed_manifest_sheet_v16.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v100-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v101-source-candidate.png`
- `assets/dinosaurs/stegosaurus-stenops-imagegen-v102-source-candidate.png`
- `assets/dinosaurs/stegosaurus-p11-v100-v102-review-sheet.png`
- `assets/dinosaurs/stegosaurus-p11-v100-v102-crops.png`

Decision: keep v92 first, add v100 as `review_hold`, and reject v101/v102. V100 is the best P11 evidence for the user's plate-material goal: the dorsal plates read as rough opaque pale-bone/rust keratin rather than body skin. It still cannot be promoted because the thagomizer can read as five spikes or a radial cluster. V101 has a straight tail-spear continuation and does not prove exactly four upward spikes; v102 keeps strong plates but leaves a lower tail point too parallel to the tail or ground. The next useful route remains tail-local ControlNet/inpaint over v92 or v100, preserving the better plate material while forcing a rounded tail base and exactly four upward ground-relative spikes.

### Seed Pool Correction: Partial Feature Seeds

Decision: demote `stegosaurus_angular_plate_v1` and `stegosaurus_tailroom_thagomizer_v1` from `train_seed` to `review_hold`. The angular-plate image has a natural body and broad plates but misses the four-spike thagomizer; the tailroom image has a clearer thagomizer but the dorsal plates read too rounded/decorative. Keep `stegosaurus_imagegen_v92_bony_plate_upward_v_tail` as the current positive smoke-test seed, with `stegosaurus_alternatingplate_fourspike_v6` as an older comparison seed, until a broader reviewed synthetic Stegosaurus set exists.
