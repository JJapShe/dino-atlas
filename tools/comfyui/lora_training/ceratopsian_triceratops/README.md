# ceratopsian_triceratops LoRA Prep

Purpose: prepare a copyright-safe custom LoRA or reference-conditioned route for `Triceratops horridus`.

The current public LoRA path is not reliable enough for app promotion: global use can exaggerate horns, reopen the mouth, create artifacts, or pull the body back toward a rhinoceros-like mammal. Keep public LoRAs diagnostic only unless a future masked, low-strength pass clearly preserves the body gate.

## Source Policy

Use only:

- internal AI-generated candidates already produced for this project,
- hand-authored project control guides,
- future synthetic outputs generated from schedules in this folder after human review.

Museum/science links remain reference anchors only, not training data.

## Seed Roles

- `train_seed`: reviewed internal images that may seed a tiny proof dataset.
- `control_reference`: project-owned guides for ControlNet, i2i, or prompt planning; do not train directly from schematic guides.
- `review_hold`: useful comparisons that remain excluded from training because of anatomy risk.
- `reject_reference`: negative gates for automation and human review; never train as positive samples.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\ceratopsian_triceratops\seed_manifest.json --output-dir tools\comfyui\lora_training\ceratopsian_triceratops\materialized_seed
```

The command writes an ignored local folder with copied `train_seed` images, matching captions, and a contact sheet. Keep the materialized folder out of git.

## Training Gate

Do not train a promoted LoRA from the seed set alone. Before a useful LoRA attempt, expand to at least 40 reviewed synthetic images with:

- exactly two brow horns plus one shorter nasal horn,
- large solid frill attached to the skull, not shoulders or back,
- closed parrot-like beak,
- low elongated ceratopsian body, long dinosaur tail, four limbs,
- visible non-hoofed toes or blunt claws,
- no rhinoceros torso, mammal hooves, shoulder hump, short tail, text, logos, or artifacts.

## Skull/Frill Body-Lock Route

Tracked control files:

- `assets/dinosaurs/triceratops-horridus-skullfrill-bodylock-guide-v1.png`
- `assets/dinosaurs/triceratops-skullfrill-bodylock-crops-v10.png`
- `assets/dinosaurs/triceratops-review-options-v16.png`
- `skullfrill_bodylock_prompt_schedule.json`

Decision: keep the new skull/frill body-lock guide as `control_reference`, not as a training image or promoted paleoart. It exists to lock the failure points from earlier Triceratops loops: skull-attached frill, exactly three facial horns, low long dinosaur body, long tail, and non-hoofed toes without returning to a rhinoceros-like torso.

## All-Feet And Toe-Claw Review Route

Tracked review files:

- `review/trike_allfeet_lora_i2i_v21_v22_review.json`
- `review/trike_toe_claw_matte_i2i_v23_review.json`
- `review/trike_antirhino_lowdenoise_v24_review.json`
- `review/triceratops_p1_v27_review.json`
- `review/trike_schedule_i2i_v17_review.json`
- `assets/dinosaurs/triceratops-allfeet-lora-i2i-v21-v22-review-sheet.png`
- `assets/dinosaurs/triceratops-allfeet-lora-i2i-v21-v22-crops.png`
- `assets/dinosaurs/triceratops-p1-v27-review-sheet.png`
- `assets/dinosaurs/triceratops-p1-v27-crops.png`
- `assets/dinosaurs/triceratops-toe-claw-matte-i2i-v23-foot-compare.png`
- `assets/dinosaurs/triceratops-toe-claw-matte-i2i-v23-crops.png`
- `assets/dinosaurs/triceratops-antirhino-lowdenoise-v24-rejection-sheet.png`
- `assets/dinosaurs/triceratops-antirhino-lowdenoise-v24-crops.png`

Decision: keep v22 as the current app first candidate, but only as `review_hold` for LoRA prep until a human crop review confirms the anti-rhino body and exact non-hoofed toe gate. Keep v23 as `review_hold` because it preserves v22 and slightly reduces shiny toe-claw highlights, but it does not prove better toe anatomy. Keep v24 as `reject_reference`: low-denoise whole-body RealVisXL i2i can avoid the old rhinoceros torso failure, but it does not beat v22 on feet and weakens the head/eye read. Keep schedule+i2i v17 as `reject_reference` because it reopens the beak and shows teeth. Future automation must not treat visible toes, dramatic horns, or a closed-looking mouth as enough by themselves; it must preserve the low ceratopsian body, long dinosaur tail, skull-attached frill, exactly three facial horns, closed beak, and non-hoofed toes together.

## P1 V26/V27 Closed-Beak Prompt Route

Decision: keep `assets/dinosaurs/triceratops-horridus-imagegen-v27-source-candidate.png` as `review_hold` only. It is the best new prompt-only closed-beak source, with readable three horns, skull-attached frill, long tail, and visible toes, but the torso is still too rounded and the rear legs overlap enough that it should not replace v22. Keep `assets/dinosaurs/triceratops-horridus-imagegen-v26-source-candidate.png` as `reject_reference` because the black mouth gap reopens the beak.

Tracked review files:

- `assets/dinosaurs/triceratops-p1-v27-review-sheet.png`
- `assets/dinosaurs/triceratops-p1-v27-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p1_v27_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v5.png`

## P2 V28/V30 Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v28-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v30-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v29-source-candidate.png`
- `assets/dinosaurs/triceratops-p2-v28-v30-review-sheet.png`
- `assets/dinosaurs/triceratops-p2-v28-v30-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p2_v28_v30_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v6.png`

Decision: keep v28 and v30 as `review_hold`, not as representatives or positive LoRA seeds. V28 is the best new project-owned prompt candidate because it keeps the three facial horns, skull-attached frill, closed beak, long tail, and visible toes together, but its torso and shoulder mass still carry mild rhinoceros risk. V30 has similar head/frill/tail strength but a more decorative frill rim and rounded torso. Keep v29 as `reject_reference`: it preserves useful head cues but reinforces the round, shoulder-heavy rhino-body failure mode. This older P2 decision was superseded by the P6 v41 promotion after a later candidate proved a lower elongated torso and longer tail.

## P3 V31/V33 Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v31-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v32-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v33-source-candidate.png`
- `assets/dinosaurs/triceratops-p3-v31-v33-review-sheet.png`
- `assets/dinosaurs/triceratops-p3-v31-v33-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p3_v31_v33_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v7.png`

Decision: add v33 to the app and manifest as `review_hold`, not as a representative or positive LoRA seed. V33 is the best fresh P3 comparison because it keeps a closed beak, skull-attached frill, exactly three facial horns, long tail, and visible toes, but its torso remains rounded and shoulder-heavy enough to carry rhinoceros risk. Keep v31 and v32 as `reject_reference` examples: both preserve useful head/frill cues, but they reinforce the round mammal-body failure mode. Prompt-only retries are not solving the anti-rhino torso gate; the next useful route should use the skull-frill body-lock guide with local body-shape/i2i control or a curated ceratopsian LoRA branch.

## P4 V34/V36 Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v34-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v35-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v36-source-candidate.png`
- `assets/dinosaurs/triceratops-p4-v34-v36-review-sheet.png`
- `assets/dinosaurs/triceratops-p4-v34-v36-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p4_v34_v36_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v8.png`

Decision: set the app taxon status back to `검수중`; Triceratops must not remain marked approved while the current first candidate still has anti-rhino and toe review risk. Add v35 to the app and manifest as `review_hold`, not as a representative or positive LoRA seed. V35 is the best fresh P4 compromise because it improves the longer body, long tail, closed beak, exactly three facial horns, and visible non-hoofed toes. Keep v34 as a secondary `review_hold` because its skull/frill identity is useful but the torso remains high and rounded. Keep v36 as `reject_reference` because the body returns to a rounded mammal-like mass. Continue with skull-frill body-lock i2i or a curated ceratopsian LoRA branch before any approval.

## P5 V37/V39 Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v37-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v38-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v39-source-candidate.png`
- `assets/dinosaurs/triceratops-p5-v37-v39-review-sheet.png`
- `assets/dinosaurs/triceratops-p5-v37-v39-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p5_v37_v39_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v9.png`

Decision: add v38, v39, and v37 to the app and manifest as `review_hold`, not as representatives or positive LoRA seeds. V38 is the best fresh P5 comparison because it has the strongest immediate Triceratops read: skull-attached frill, exactly three facial horns, closed beak, long tail, and separated toes. Keep it below v22 because the torso remains rounded/barrel-like enough to reinforce mammal-body shortcuts. V39 has strong head/frill identity but a heavier barrel body; v37 has useful tail and foot visibility but the water-edge scene and body volume are weaker. This P5 decision was superseded by the P6 v41 promotion after v41 improved the low elongated torso and full long-tail silhouette.

## P6 V40/V42 Low-Body Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v40-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v41-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v42-source-candidate.png`
- `assets/dinosaurs/triceratops-p6-v40-v42-review-sheet.png`
- `assets/dinosaurs/triceratops-p6-v40-v42-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p6_v40_v42_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v10.png`

Decision: promote v41 to the app first slot as a `count-level pass` and add it as a project-owned smoke-test `train_seed`. V41 gives the strongest current anti-rhino body read with a lower elongated torso than v22/v38, a full long tail, closed beak, skull-attached frill, exactly three facial horns, four visible dinosaur limbs, and separated non-hoofed toes. It is not final approval because skull/frill proportions, exact toe anatomy, and forelimb posture still need reference review. Keep v42 as a low-body `review_hold` and v40 as a close-framed head/feet `review_hold`. This P6 decision was superseded by the P7 v43 promotion after v43 improved the app-scale skull/frill/toe read while preserving the anti-rhino gates.

## P7 V43/V45 Familiar Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v43-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v44-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v45-source-candidate.png`
- `assets/dinosaurs/triceratops-p7-v43-v45-review-sheet.png`
- `assets/dinosaurs/triceratops-p7-v43-v45-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p7_v43_v45_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v11.png`

Decision: promote v43 to the app first slot as a `count-level pass` and add it as a project-owned smoke-test `train_seed`. V43 gives the strongest familiar app-scale Triceratops read while preserving the anti-rhino gates: long tail, closed beak, skull-attached frill, exactly three facial horns, four visible dinosaur limbs, and separated non-hoofed toes. It is not final approval because torso mass, skull/frill proportions, exact toe anatomy, and forelimb posture still need reference review. Keep v41 as the previous low-body `review_hold`, v44 as a rounded-body `review_hold`, and v45 as a mouth/head-risk `review_hold`.

## P8 V46/V48 Familiar Anti-Rhino Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v46-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v47-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v48-source-candidate.png`
- `assets/dinosaurs/triceratops-p8-v46-v48-review-sheet.png`
- `assets/dinosaurs/triceratops-p8-v46-v48-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p8_v46_v48_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v12.png`

Decision: keep v43 in the app first slot as the `count-level pass`. The P8 prompt pass did not produce a clear replacement: v46 is a near-duplicate-style `review_hold` with useful familiar skull/frill/tail/toe cues, but its rounded torso and foot detail do not clearly improve v43; v48 is a `review_hold` with a good full silhouette and long tail, but toe separation and body mass still need closer review; v47 is a `reject_reference` because the leg/foot read is weaker than v43 and the body still carries rounded mammal-mass risk. Do not add v46/v48 as positive LoRA seeds unless a later reference review proves they beat v43 on low elongated body, skull-attached frill, closed beak, long tail, and non-hoofed toes together.

## P9 V49/V51 Color/Frill Pattern Prompt Route

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v49-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v50-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v51-source-candidate.png`
- `assets/dinosaurs/triceratops-p9-v49-v51-review-sheet.png`
- `assets/dinosaurs/triceratops-p9-v49-v51-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p9_v49_v51_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v13.png`

Decision: promote v51 to the app first slot as the current `count-level pass` and add it as the project-owned smoke-test `train_seed`. V51 improves the gallery-wide color problem with a cool blue-gray body and pale mottling while preserving the anti-rhino gates: long tail, closed beak, skull-attached frill, exactly three facial horns, four visible dinosaur limbs, and separated non-hoofed toes. Keep v49 and v50 as `review_hold` color variants: v49 has useful dark speckling but rougher head/frill contrast, and v50 has a useful rust frill accent but less body-color separation. Demote v43 to previous comparison hold because its anti-rhino identity remains useful but its tan-gray palette is less distinct from other taxa.

## P10 V52/V54 Color Variation Body-Lock Review

Tracked review files:

- `assets/dinosaurs/triceratops-horridus-imagegen-v52-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v53-source-candidate.png`
- `assets/dinosaurs/triceratops-horridus-imagegen-v54-source-candidate.png`
- `assets/dinosaurs/triceratops-p10-v52-v54-review-sheet.png`
- `assets/dinosaurs/triceratops-p10-v52-v54-crops.png`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/triceratops_p10_v52_v54_review.json`
- `tools/comfyui/lora_training/ceratopsian_triceratops/review/ceratopsian_seed_manifest_sheet_v14.png`

Decision: keep v51 as the current `count-level pass`. Add v52, v53, and v54 as `review_hold` color references only. V52 gives the most useful cool blue mottling with visible toes; v53 gives the strongest teal body, cream flank marks, and rust frill accent; v54 gives a darker freckled cool-gray pattern. None should enter positive LoRA training yet because their rounded/high torso and skull/frill attachment still carry rhinoceros-body or shoulder-frill risk. The next route should use the skull-frill body-lock guide or low-denoise i2i over v51/v52 to preserve the cool palette while lowering the torso, proving the frill attaches to the skull, and keeping separated non-hoofed toes.

## Seed Pool Correction: Open-Mouth Drift

Decision: demote `triceratops_lowbody_toe_frame_v7` from `train_seed` to `review_hold`. It is still useful as an anti-rhino body and toe-frame comparison, but direct review shows the mouth is more open than the v9 representative. Keep `triceratops_imagegen_v51_cool_color_frill` and `triceratops_lowbody_closedbeak_v9` as the current positive smoke-test seeds, with v51 preferred for the project-owned app representative route and v9 retained as the older body/beak gate. Keep v43, the previous v41 seed, P9 v49/v50, and P8 v46/v48 as `review_hold`; keep P8 v47 as `reject_reference`. Do not treat any positive seed as final until low body, long tail, skull-attached frill, exactly three horns, closed beak, non-hoofed toes, and non-sandy natural color pass together against references.
