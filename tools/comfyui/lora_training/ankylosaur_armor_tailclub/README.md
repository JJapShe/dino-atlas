# ankylosaur_armor_tailclub LoRA Prep

Purpose: prepare a copyright-safe custom LoRA/i2i route for `Ankylosaurus magniventris` and close ankylosaurid body-plan work. Public Ankylosaurus LoRAs and prompt-only SDXL passes have not been reliable enough to lock all required cues at once: broad blunt skull, very low squat body, dense low osteoderm rows, four sturdy feet, and a single fused bony tail club.

## Source Policy

Use only:

- internal AI-generated candidates already produced for this project,
- hand-authored control guides created in this repository,
- future synthetic outputs generated from the prompt schedule in this folder after human review.

Do not use museum photos, copyrighted paleoart, movie/game stills, or public LoRA outputs with unclear provenance as training images. External science and museum material remains reference-only for human comparison.

## Seed Roles

- `train_seed`: can be materialized as image/caption pairs for a tiny proof dataset after review.
- `control_reference`: useful for ControlNet, IP-Adapter, depth/line guidance, or prompt planning, but too guide-like for direct LoRA training.
- `review_hold`: useful as a failure/comparison image, but excluded because it contains anatomy artifacts or weak diagnostic cues.
- `reject_reference`: negative gates for automation and human review; never train as positive samples.

## Materialize

```powershell
& tools\comfyui\.venv\Scripts\python.exe tools\comfyui\scripts\prepare_lora_seed_dataset.py --manifest tools\comfyui\lora_training\ankylosaur_armor_tailclub\seed_manifest.json --output-dir tools\comfyui\lora_training\ankylosaur_armor_tailclub\materialized_seed
```

The command writes an ignored local folder with copied `train_seed` images, matching captions, and a contact sheet. Keep the materialized folder out of git.

## Training Gate

Do not train a promoted LoRA from the seed set alone. Before a usable LoRA attempt, expand to at least 40 reviewed synthetic images with:

- full-body side-profile and three-quarter walking views,
- broad blunt skull and very short neck,
- low squat body rather than monitor-lizard, crocodile, turtle, armadillo, or pangolin drift,
- dense low rounded osteoderms on back, flanks, hips, and tail base,
- exactly four sturdy planted legs with reviewable blunt toes,
- one single fused oval bony tail club attached directly to a thick low tail,
- no tall Stegosaurus-like plates, fantasy mace spikes, extra limbs, missing club, detached club, double club, text, logo, or watermark.

## Armor/Tail-Club Control Route

Tracked control files:

- `assets/dinosaurs/ankylosaurus-magniventris-armor-tailclub-guide-v1.png`
- `assets/dinosaurs/ankylosaurus-armor-tailclub-crops-v6.png`
- `assets/dinosaurs/ankylosaurus-review-options-v11.png`
- `armor_tailclub_prompt_schedule.json`

Decision: keep the new armor/tail-club guide as `control_reference`, not as direct training art or final paleoart. It exists to lock the details that still fail intermittently: the broad blunt skull, low squat ankylosaurid mass, rows of low rounded osteoderms, four sturdy feet, and one attached fused oval tail club. Use `armor_tailclub_prompt_schedule.json` for the next ControlNet/depth/line or low-denoise i2i experiment before adding new outputs to the training seed pool.

## Broad-Skull And All-Feet Review Route

Tracked review files:

- `review/anky_broadskull_i2i_v14_review.json`
- `review/anky_lora_i2i_v15_v16_review.json`
- `review/anky_allfeet_lora_i2i_v17_v18_review.json`
- `review/anky_bodylock_osteoderm_lowdenoise_v19_review.json`
- `review/ankylosaurus_p1_v20_review.json`
- `assets/dinosaurs/ankylosaurus-broadskull-i2i-v14-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-broadskull-i2i-v14-crops.png`
- `assets/dinosaurs/ankylosaurus-lora-i2i-v15-v16-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-lora-i2i-v15-v16-crops.png`
- `assets/dinosaurs/ankylosaurus-allfeet-lora-i2i-v17-v18-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-allfeet-lora-i2i-v17-v18-crops.png`
- `assets/dinosaurs/ankylosaurus-bodylock-osteoderm-lowdenoise-v19-rejection-sheet.png`
- `assets/dinosaurs/ankylosaurus-bodylock-osteoderm-lowdenoise-v19-crops.png`
- `assets/dinosaurs/ankylosaurus-p1-v20-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p1-v20-crops.png`

Decision: keep v18 as the previous app first candidate and as `review_hold` for LoRA prep until human crop review confirms that it reads as a broad low ankylosaurid rather than a crocodile, monitor lizard, pangolin, turtle, armadillo, or generic armored fantasy reptile. Keep v14 as `review_hold` because it preserves the v5 body and club while slightly improving the skull. Keep v15, v16, and v19 as `reject_reference`: armor texture, foot clarity, or tail-club preservation alone is not enough unless skull breadth, low armored mass, rounded osteoderm rows, four feet, and a single attached tail club improve together. The v19 low-denoise whole-body route preserved the club but often lengthened the body/snout toward a lizard read, so it should guide rejection rather than promotion. Future automation must reject any candidate whose tail club is present but whose body plan is not recognizably Ankylosaurus.

## P1 V20 Source Candidate

Decision: keep `ankylosaurus-magniventris-imagegen-v20-source-candidate.png` as `review_hold`, not `train_seed`. It is project-owned, copyright-safe, and useful for comparison because it keeps four visible planted legs, dense low rounded osteoderms, a thick low tail, and one attached oval tail club. Do not promote it until close review confirms that the skull is broad/blunt enough and the body does not read as a generic armored lizard. Use `assets/dinosaurs/ankylosaurus-p1-v20-review-sheet.png` and `assets/dinosaurs/ankylosaurus-p1-v20-crops.png` before any future LoRA or representative-image use.

## P2 V21/V23 Armor And Tail-Club Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v21-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v22-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v23-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p2-v21-v23-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p2-v21-v23-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p2_v21_v23_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v5.png`

Decision: keep v22 and v23 as `review_hold`, not as representatives or positive LoRA seeds. V22 is the best new prompt-only balance of broad blunt skull, low rounded armor rows, four planted feet, and one attached oval tail club, but it still carries mild long-body and long-tail lizard drift risk. V23 gives the lowest, broadest new armor-body read and a clean club, but the body/tail proportions can read monitor-lizard-like. Keep v21 as `review_hold` only because the armor and club are useful but the skull-side projections can read as horns or fantasy spikes. Keep v18 first until a candidate proves compact ankylosaurid proportions, broad skull, low osteoderms, four sturdy feet, and one attached club together.

## P3 V24/V26 Compact-Skull Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v24-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v25-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v26-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p3-v24-v26-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p3-v24-v26-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p3_v24_v26_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v6.png`

Decision: keep v25 as the best P3 `review_hold`, not as a final representative or positive LoRA seed. It improves the combined read of compact head, low rounded armor rows, four grounded feet, and a single attached oval club, but the skull can still read slightly long and the rear legs need close separation review. Keep v24 as a tail-club/body comparison with long-snout and long-body lizard risk. Keep v26 as a low-armor/blunt-head comparison with rear-foot ambiguity. The next route should use v25 only as a copyright-safe i2i/ControlNet review source, with rejection if it weakens the non-lizard body plan, broad blunt skull, four sturdy feet, rounded low osteoderms, or attached tail club.

## P4 V27/V29 Compact Armor/Tail-Club Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v27-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v28-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v29-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p4-v27-v29-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p4-v27-v29-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p4_v27_v29_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v7.png`

Decision: add v28 to the app and manifest as the best P4 `review_hold`, not as a final representative or positive LoRA seed. V28 improves the tank-like low armored body, dense rounded osteoderms, grounded feet, and one attached oval club, but head side knobs and long-tail tendency still need close review. Keep v27 as secondary armor/club evidence because it stretches toward lizard proportions. Keep v29 as `reject_reference`: its blunt-head and armor cues are useful, but the body and tail become too long. Continue toward low-denoise compact-body i2i or a curated ankylosaur LoRA branch before any approval.

## P5 V30/V32 Compact Tank Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v30-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v31-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v32-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p5-v30-v32-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p5-v30-v32-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p5_v30_v32_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v8.png`

Decision: promote v32 to the app first slot as a `count-level pass`, but keep it only as `review_hold` in the LoRA manifest. V32 gives the strongest immediate Ankylosaurus read so far with a low tank-like armored body, dense rounded osteoderm rows, four sturdy planted feet, and one attached oval club. It is not final because the cheek knob can still read horn-like and the tail remains longer than ideal. Keep v31 as a horn-risk hold and v30 as a compact armor hold with lizard-head risk. Do not train from these until broad blunt skull, compact body, four sturdy feet, low rounded armor, and single attached club all pass together.

## P6 V33/V35 Blunt-Skull Armor-Tailclub Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v33-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v34-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v35-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p6-v33-v35-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p6-v33-v35-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p6_v33_v35_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v9.png`

Decision: promote v34 to the app first slot as a `count-level pass` and add it as the current project-owned smoke-test `train_seed`. V34 improves over v32 with a broader blunt skull read, lower compact tank-like body, visible planted feet, rounded armor rows, and one attached oval tail club. It is still not a final approval because the tail remains longer than ideal and exact skull, toe, and armor-row topology need reference review. Keep v33 and v35 as `review_hold` comparisons; v33 has useful compact body/club evidence but a longer tail, while v35 has strong broad armor but a slightly longer head and tighter framing.

## P7 V36/V38 Compact-Tank Tailclub Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v36-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v37-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v38-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p7-v36-v38-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p7-v36-v38-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p7_v36_v38_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v10.png`

Decision: promote v38 to the app first slot as the current `count-level pass` and use it as the project-owned compact-body smoke-test `train_seed`. V38 improves over v34 with a shorter, rounder tank-like body while keeping a broad blunt skull, dense low rounded osteoderm rows, four sturdy visible feet, and one attached oval tail club. It is still not a final approval because exact skull shape, toe detail, armor-row topology, and tail-club attachment need close reference review. Keep v34 as the previous app-first hold, v37 as a compact-body hold with tighter framing/heavier head, and v36 as a longer-tail hold.

## P8 V39/V41 Color And Armored-Skull Prompt Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v39-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v40-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v41-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p8-v39-v41-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p8-v39-v41-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p8_v39_v41_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v11.png`

Decision: promote v40 to the app first slot as the current `count-level pass` and use it as the project-owned color-and-armored-skull smoke-test `train_seed`. V40 addresses two current gallery weaknesses at once: it breaks the repeated sandy-brown palette with a red-ochre and burnt-umber natural pattern, and it gives a stronger Ankylosaurus head read with a compact armored skull, fused cranial-plate texture, cheek horns, and rear skull-corner horn cues. It keeps the low rounded osteoderm rows, four visible feet, and one attached oval tail club. It is still not final approval because skull horn size, exact cranial armor layout, toe detail, color naturalism, and tail-club attachment need close reference review. Keep v38 as the previous compact-body `review_hold`, v39 as a dark-olive skull-armor `review_hold`, and v41 as a blue-gray skull-horn `review_hold` with possible horn-size/head-shape overemphasis.

## P9 V42/V44 Armored-Skull Color Variation Route

Tracked review files:

- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v42-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v43-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v44-source-candidate.png`
- `assets/dinosaurs/ankylosaurus-p9-v42-v44-review-sheet.png`
- `assets/dinosaurs/ankylosaurus-p9-v42-v44-crops.png`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaurus_p9_v42_v44_review.json`
- `tools/comfyui/lora_training/ankylosaur_armor_tailclub/review/ankylosaur_seed_manifest_sheet_v12.png`

Decision: keep v40 as the app first slot and current `train_seed`, then add v43, v42, and v44 as `review_hold` items only. P9 directly targets the user-visible lizard-head issue: v43 has the strongest new short blunt helmet-like skull, cheek horns, rear skull-corner horn cues, darker color separation, four legs, and one attached tail club. V42 adds a cool slate-blue armor palette and v44 adds a charcoal/russet flank pattern. Do not promote any of them yet because their dorsal osteoderm rows can read as too regular, tiled, or plate-like. The next useful route is body-lock i2i/ControlNet using v40 for the body balance, v43 for skull/color cues, and the armor-tailclub guide for structure, with strict rejection for smooth lizard/crocodile heads, over-regular shell grids, fantasy spikes, missing/doubled clubs, or six-legged outputs.

## Seed Pool Correction: Lizard-Drift Risk

Decision: demote `ankylosaurus_clearfeet_singleclub_v4` from `train_seed` to `review_hold`. It remains a useful open-foot and single-club comparison, but direct review shows its longer body and snout can drift toward a generic armored lizard read. Keep `ankylosaurus_imagegen_v40_armored_skull_color` and `ankylosaurus_broadskull_singleclub_v5` as the current positive smoke-test seeds, with v40 preferred for the project-owned app representative route and v5 retained as the older broad-skull/single-club comparison. Keep v38 and v34 as previous first-image review holds, v39/v41 as color-and-skull review holds. Do not treat any positive seed as final until broad blunt armored skull, very short neck, low squat armored body, rounded osteoderm rows, four sturdy feet, one attached fused tail club, and natural-but-distinct color pattern pass together against references.
