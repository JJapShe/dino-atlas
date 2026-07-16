# Dinosaur LoRA Research Notes

Last checked: 2026-06-23

## Short Verdict

There are dinosaur-related LoRAs, but there is not a strong public LoRA that matches all three needs at once:

- scientifically plausible `Velociraptor mongoliensis`
- copyright-safe training provenance
- compatible with the current realistic SDXL / RealVisXL atlas workflow

For the MVP, keep public LoRAs as experiments and use review-gated SDXL/RealVisXL plus hand-authored shape guides for production candidates. For better repeatable quality, train our own clade-level LoRAs from cleared references.

Note: a follow-up Civitai API query on 2026-06-21 returned `503 Service Unavailable` for the main species searches, so public-candidate conclusions still rely on the browser/search checks and locally downloaded files rather than fresh API metadata.

## Local LoRA Inventory

| File | Base | Useful for | Verdict |
| --- | --- | --- | --- |
| `Dinosaur_Generator.safetensors` | SD 1.5 | legacy broad dinosaur prompt support | Useful only in SD 1.5 experiments; not a RealVisXL/SDXL anatomy solution. |
| `Dinosaur_Generator_v2.0-000011.safetensors` | SDXL | broad dinosaur prompt support | Loads, but Velociraptor drifts toward naked/movie raptors and Stegosaurus drifts toward sauropod/theropod bodies without plates. Use only at low strength for diagnostic comparisons. |
| `Realistic_Tyrannosaurus_Rex-000019.safetensors` | SDXL | T. rex | Best local species LoRA so far. Low strength works; high strength overfits/artifacts. |
| `TriceratopsXL0_4.safetensors` | SDXL | Triceratops | Loads, but exaggerates shapes when used globally. Best current use is low-strength masked inpaint over a natural scene. |
| `Velociraptor_Dino.safetensors` | SD 1.5 | Velociraptor experiments | Adds bird/feather cues but also text, bird drift, and odd anatomy. Not production-ready. |
| `Ankylosaurus_Dinosaur.safetensors` | SD 1.5 | Ankylosaurus experiments | Some texture help, weak full-body control. Not production-ready. |
| `dinosaur_practical_fx.safetensors` | SDXL | practical creature texture | Loads in the current SDXL workflow, but drifts toward cinematic bulky theropods. Use only as a low-strength diagnostic comparison. |

## Public Candidates Found

### 2026-06-21 Civitai / Hugging Face re-check

| Target | Result | MVP decision |
| --- | --- | --- |
| `Plateosaurus`, `sauropodomorph`, `Triassic dinosaur` | No useful public species LoRA found. Searches returned no relevant Plateosaurus/sauropodomorph candidates. | Use RealVisXL + shape guide + ControlNet/IP-Adapter. Consider custom early-sauropodomorph LoRA later; the current no-six-leg body-lock route is the preferred next step. |
| `Herrerasaurus`, `Coelophysis` | No useful public species LoRA found. | Same as above: guide-first workflow, not public LoRA-first workflow. Use the new body-lock guide routes before any more generic-LoRA probing. |
| `Allosaurus` | Public LoRAs exist, but the SDXL candidate found is ARK-derived and weakly rated; others are SD1.5/Pony/Illustrious. | Avoid for copyright-safe final assets. Current RealVisXL candidate is safer. |
| `Stegosaurus` | A species LoRA exists, but it is Illustrious-only. | Worth testing only if we add an Illustrious branch; not directly useful in the current SDXL workflow. |
| `Apatosaurus` / `Brachiosaurus` / `Sauropod` | Search results are mostly movie/cartoon/character LoRAs, not neutral paleo reconstruction LoRAs. | Avoid for final assets. Use prompt + ControlNet silhouettes. |
| Generic dinosaur SDXL | `Dinosaur Generator`, `Dinosaur Generator v2.0`, and the SDXL version of `Dinosaur Practical Effects` are the best current public options. | Use at low strength for texture/material help only; do not trust them for diagnostic anatomy. |

Practical implication: for uncommon taxa, a public LoRA will not solve the weird anatomy. The better short-term path is a three-part workflow: strict diagnostic prompt, clean internal silhouette/reference image, then ControlNet/IP-Adapter with low denoise and review filtering.

### 2026-06-21 Stegosaurus LoRA detail check

| Candidate | Base | Link | File / trigger | Notes |
| --- | --- | --- | --- | --- |
| Stegosaurus: "Roof-Lizard" | Illustrious | https://civitai.com/models/1503821 | `StegosaurusDinosaur_IXL.safetensors`; trigger `zzStego` | The most relevant public Stegosaurus hit found so far. It is not installed locally yet, and the API download returned `401 Unauthorized`, so manual browser download is likely required. Because it is Illustrious-trained, test it in a separate Illustrious branch first; only use RealVisXL mixing as a low-confidence experiment. Its Civitai permissions allow commercial image use but disallow derivatives, so do not use it to train another LoRA. |
| Dinosaur Generator v2.0 | SDXL | https://civitai.com/models/386745 | `Dinosaur_Generator_v2.0-000011.safetensors` | Already tested locally. It did not reliably create Stegosaurus thagomizer anatomy and is not a replacement for a species LoRA. |
| Dinosaur Practical Effects | SDXL | https://civitai.com/models/1062304 | `dinosaur_practical_fx.safetensors` locally | Can help practical creature texture, but it is not Stegosaurus- or Herrerasaurus-specific. Treat as a diagnostic texture LoRA, not an anatomy controller. |

### Velociraptor / Dromaeosaur

| Candidate | Base | Link | Notes |
| --- | --- | --- | --- |
| Experimental Velociraptor | SD 1.5 | https://civitai.com/models/123987 | Already downloaded as `Velociraptor_Dino.safetensors`. Not accurate enough for the MVP. |
| deinonychus | SD 1.5 | https://civitai.com/models/248424 | Closer dromaeosaur direction than movie raptors, but still SD 1.5 and not a clean SDXL atlas fit. Useful only as an experiment/i2i pre-pass. |
| Utahraptor | Illustrious | https://civitai.com/models/2603737 | Newer feathered-dromaeosaur-adjacent candidate found in the 2026-06-21 re-check. License and Illustrious compatibility make it experimental, not a final asset source. |
| Velociraptor Pack - Jurassic World | Illustrious / Pony | https://civitai.com/models/873635 | Movie-character/source dependent. Not copyright-safe for final app assets. |
| Velociraptors | Illustrious | https://civitai.com/models/1952989 | More scalie/furry/character-oriented than paleo reconstruction. |
| Deinonychus - ARK Survival Evolved | Illustrious | https://civitai.com/models/1465791 | Has feathered-theropod tags, but game-derived and not copyright-safe for final output. |
| Macrobius dromaeosaur | Illustrious | https://civitai.com/models/1980595 | Character model; not a scientific Velociraptor LoRA. |
| Anthro Feathered Raptor | Illustrious / Pony | https://civitai.com/models/1397480 | Anthro/furry direction; not suitable for natural-history atlas images. |

### Other Species

| Candidate | Base | Link | Notes |
| --- | --- | --- | --- |
| Realistic Tyrannosaurus Rex | SDXL | https://civitai.com/models/1766028 | Useful, already tested and adopted as a T. rex gallery candidate. |
| T-Rex: Tyrant Lizard King | SDXL / SD 1.5 | https://civitai.com/models/192092 | Stronger public T. rex candidate than most. Worth testing as a comparison to the current Realistic T. rex LoRA. |
| Triceratops XL | SDXL | https://civitai.com/models/523521 | Tested; not preferred because shapes became too stylized. |
| Dinosaur Generator | SD 1.5 | https://civitai.com/models/383891 | General dinosaur helper. Already available locally as `Dinosaur_Generator.safetensors`; use only in SD 1.5 experiments and rely on guides for anatomy. |
| Dinosaur Generator v2.0 | SDXL / SD 1.5 | https://civitai.com/models/386745 | General dinosaur helper. Already available locally as `Dinosaur_Generator_v2.0-000011.safetensors`; better as a texture/style booster than a species controller. |
| Dinosaur Practical Effects | SDXL | https://civitai.com/models/1062304 | Local `dinosaur_practical_fx.safetensors` loads in the current workflow, but it is a texture/style helper only. |
| Smol Dinosaurs [SDXL] | SDXL | https://civitai.com/models/242314 | Uses the trigger `ral-smoldino`. Cute/small-dinosaur bias; not useful for realistic atlas anatomy except possibly child-friendly side illustrations. |
| Stegosaurus: "Roof-Lizard" | Illustrious | https://civitai.com/models/1503821 | Species-specific, but not directly compatible with the current SDXL checkpoint. Useful only if we add an Illustrious test branch. |
| Allosaurus (ARK) | SDXL | https://civitai.com/models/622272 | SDXL species-adjacent candidate, but game-derived and weakly rated. Avoid for copyright-safe final app assets. |
| Experimental Ankylosaurus | SD 1.5 | https://civitai.com/models/194220 | Already downloaded; not reliable enough for MVP. |
| Ankylosaurus | Illustrious | https://civitai.com/models/2118196 | Has tail-club tags, but appears anthro/character-leaning and requires an Illustrious workflow. Not a clean MVP source. |

### Hugging Face

| Candidate | Link | Notes |
| --- | --- | --- |
| tekakutli-dinosaurs | https://huggingface.co/lora-library/tekakutli-dinosaurs | Old/general LoRA; not a strong fit for SDXL atlas output. |
| ark-dinosaur-lora | https://huggingface.co/oliverbrown/ark-dinosaur-lora | ARK/game-derived direction; not recommended for copyright-safe final assets. |

## Copyright-Safety Rule

Avoid final app assets generated from LoRAs that are clearly trained on:

- Jurassic Park / Jurassic World screenshots, game models, or named characters
- ARK / Pixar / TV / anime / mascot character material
- modern paleoartist work unless explicit permission or a compatible license exists

These can be used for local anatomy experiments, but not as production asset sources for a copyright-safe dinosaur atlas.

## Recommended Production Path

1. Keep SDXL / RealVisXL plus hand-authored shape guides as the MVP reference-card pipeline.
2. Use IP-Adapter and ControlNet only to transfer approved internal style and pose cues, not copyrighted source identity.
3. Train custom clade-level LoRAs from cleared references:
   - `dromaeosaur_feathered`
   - `tyrannosaur_bodyplan`
   - `ceratopsian_frill_horns`
   - `ankylosaur_armor_tailclub`
   - `stegosaur_plates_tailspikes`
   - `sauropod_highshoulder_longneck`
4. Dataset target per clade:
   - 30 to 80 cleared images or generated/commissioned derivatives
   - captions with diagnostic traits, not only species names
   - multiple poses and lighting setups
   - exclude logos, signatures, museum labels, toy/game/movie styling
5. Use the LoRA at low to medium strength and keep a human review gate for anatomy.

### dromaeosaur_feathered seed dataset

The first project-owned seed manifest now lives at:

- `tools/comfyui/lora_training/dromaeosaur_feathered/seed_manifest.json`
- `tools/comfyui/lora_training/dromaeosaur_feathered/synthetic_prompt_schedule.json`
- materializer: `tools/comfyui/scripts/prepare_lora_seed_dataset.py`

The manifest now includes the current v9 app candidate plus earlier reviewed internal Velociraptor outputs as `train_seed` smoke-test material, and separates guide-like or artifact-prone images into `control_reference` / `review_hold` roles. This is not enough to train a production LoRA; it is the reproducible starting set for caption validation and for expanding toward a 40+ image synthetic, copyright-safe dromaeosaur dataset.

### stegosaur_plates_tailspikes seed dataset

The first project-owned Stegosaurus/stegosaurian seed manifest now lives at:

- `tools/comfyui/lora_training/stegosaur_plates_tailspikes/seed_manifest.json`
- `tools/comfyui/lora_training/stegosaur_plates_tailspikes/synthetic_prompt_schedule.json`
- materializer: `tools/comfyui/scripts/prepare_lora_seed_dataset.py`

The manifest separates the current best feature examples into `train_seed`, `control_reference`, `review_hold`, and `reject_reference` roles. The training target is narrow on purpose: broad separated angular dorsal plates plus a countable four-spike thagomizer. The initial prompt-only smoke run is tracked under `tools/comfyui/lora_training/stegosaur_plates_tailspikes/review/` and was rejected for training because RealVisXL drifted into generic/theropod body plans without reliable Stegosaurus plates.

The current combined control target is `assets/dinosaurs/stegosaurus-stenops-plate-thagomizer-reference-v1.png`, generated by `tools/comfyui/scripts/draw_stego_plate_thagomizer_reference.py`. It is useful because it puts both required gates in one project-owned image: broad separated alternating plates and exactly four countable tail spikes. The newer plate-topology control target, `assets/dinosaurs/stegosaurus-stenops-plate-topology-guide-v1.png`, is now the better route when the specific failure is near/far row collapse: it marks staggered plate sockets and should be used with `tools/comfyui/lora_training/stegosaur_plates_tailspikes/plate_topology_prompt_schedule.json`.

This is not enough to train a production LoRA. Use it only for caption validation, control/reference routing, and as the start of a reviewed 40+ image synthetic expansion focused on plate and tail-spike anatomy.

## Download / Test Priority

1. `dinosaur_practical_fx.safetensors` from https://civitai.com/models/1062304
   - Already tested in the current SDXL / RealVisXL pipeline.
   - Helps creature material texture, but does not enforce species anatomy and can push small/early theropods toward bulky cinematic predators.
2. `Trex_Dinosaur_XL.safetensors` from https://civitai.com/models/192092
   - Worth testing specifically for two-finger `Tyrannosaurus rex` shots.
   - Use with strict hand/arm negative prompts and manual review.
3. `deinonychus.safetensors` from https://civitai.com/models/248424
   - Optional SD 1.5 experiment for dromaeosaur silhouette or i2i pre-pass.
   - Not recommended as the final SDXL workflow anchor.
4. `BastionExa_Utahraptor.safetensors` from https://civitai.com/models/2603737
   - Optional Illustrious branch experiment for feathered raptor cues.
   - Avoid as a final-source LoRA until licensing/training provenance and style drift are acceptable.
5. `StegosaurusDinosaur_IXL.safetensors` from https://civitai.com/models/1503821
   - Best public Stegosaurus-specific candidate found so far.
   - Put it in `tools/comfyui/ComfyUI/models/loras/`.
   - Test with trigger `zzStego` and low-to-medium strength (`0.25`, `0.45`, `0.65`) in an Illustrious-compatible workflow. Treat RealVisXL mixing as experimental because the LoRA was not trained for that checkpoint family.
   - Review specifically for four tail spikes, two staggered dorsal plate rows, quadrupedal body, and no head horns.
6. `Allosaurus.safetensors` from https://civitai.com/models/2297868
   - Most relevant public Allosaurus species hit found in the latest Civitai re-check.
   - It is Illustrious-trained, not SDXL/RealVisXL, so use only in a separate Illustrious branch or as anatomy-cue reference material.
   - Review for generic theropod drift and avoid it as a final-source LoRA until provenance/style behavior is checked.

## Follow-up Test Notes

- `Dinosaur_Generator_v2.0-000011.safetensors` was tested on Stegosaurus, Ankylosaurus, and Velociraptor over RealVisXL at low strengths (`0.22`, `0.36`). It improved texture but weakened species identity:
  - Stegosaurus drifted into generic quadruped/theropod-like forms without reliable plates or thagomizer.
  - Ankylosaurus gained nice armor texture but still lost the tail club.
  - Velociraptor drifted toward naked movie-raptor proportions.
- `Velociraptor` public LoRA options still did not produce an app-quality SDXL result. The best current public-tool route is IP-Adapter with a feathered internal reference plus clean ControlNet silhouette, followed by narrow feather-band inpaint over the back, upper tail, and folded forelimbs, then background-only inpaint to improve the scene without sacrificing the existing feather silhouette.
  - a later reference-gated sickle-claw retry showed the same limit: narrow foot inpaint was too subtle to improve the raised claw cue, while stronger plumage/sickle-claw ControlNet broke body proportion and leg/tail stability. Keep the current background-inpaint candidate first and treat new attempts as comparison-only until a custom cleared dromaeosaur LoRA is available.
  - the next route is now materialized as the `dromaeosaur_feathered` seed dataset and prompt schedules under `tools/comfyui/lora_training/dromaeosaur_feathered/`. The current whole-body control route is `velociraptor-mongoliensis-identity-bodylock-guide-v1.png` plus `identity_bodylock_prompt_schedule.json`; the focused foot route remains `velociraptor-mongoliensis-foot-topology-guide-v1.png` plus `foot_topology_prompt_schedule.json`. Expand with reviewed synthetic images rather than repeating the same narrow inpaint loop.
- `TriceratopsXL0_4.safetensors` remains useful only at low strength for diagnostic horn/frill readability. New tests showed that:
  - prompt-only LoRA can make the frill and brow horns clearer than the older app scene, but it may overgenerate horns, open the mouth too widely, and create lower-corner artifacts.
  - shape-guide ControlNet can misread the frill as a dorsal sail or spined fan.
  - LoRA+i2i over simple guides can become too flat/cartoon-like.
  - LoRA-source ControlNet can drift toward toothy monster heads.
  - low-strength LoRA inpaint on only the head/frill mask is the least disruptive route so far. It still needs review for horn count and frill edge, but it preserves the natural body/background better than global LoRA.
  - LoRA+ControlNet over the hard guide was tested again and still failed: the animal either lost the frill or collapsed into close-up/theropod-like heads.
  - a wider head/frill inpaint mask and a clearer internally drawn skull/frill guide were tested next. The mask preserved the natural scene but still made the frill read as a shoulder sail, while revised-guide ControlNet collapsed into close-up monster heads. Keep TriceratopsXL constrained to low-strength masked inpaint until a better cleared ceratopsian LoRA or guide-conditioned workflow is available.
  - a later reference-gated retry with a separated skull-frill guide reduced the pure rhinoceros read, but still failed candidate promotion: ControlNet absorbed the frill into a body hump, snout inpaint did not reliably add the short nasal horn, and even `0.06` LoRA snout inpaint reintroduced open-mouth/teeth drift. Do not treat the current TriceratopsXL route as suitable for app images.
  - a Civitai API re-check for SDXL Triceratops/Ceratopsian LoRAs found no better public option than the already-local `TriceratopsXL0_4.safetensors`; `ceratopsian` returned no SDXL LoRA hits. A narrow nasal-horn mask with `0.08` TriceratopsXL still failed to add the horn. The next useful route is probably custom LoRA training or a stronger reference-conditioned workflow, not more public-LoRA search.
- `Dinosaur Practical Effects` now exists locally as an SDXL-loadable file and was tested in the IP-Adapter + ControlNet path. It should remain a low-strength texture comparison because it does not supply reliable species anatomy.
- The same login redirect behavior also affected direct API downloads for `Trex_Dinosaur_XL.safetensors`. The failed download wrote a small Civitai login HTML page with a `.safetensors` extension; those invalid files were removed from `ComfyUI/models/loras/`.
- `Realistic_Tyrannosaurus_Rex-000019.safetensors` was retested for the two-finger problem. Higher-strength variants improved the T. rex body read but generated black bars, logo-like marks, and copyright-style text, so they should be treated only as diagnostic shape sources. A LoRA-to-ControlNet scene regeneration path is more useful for app comparison images than accepting the raw LoRA output.
- A later tucked-arm low-strength pass produced one useful comparison candidate, `assets/dinosaurs/tyrannosaurus-rex-tuckedarms-lora-v1.png`. It is not promoted over `tyrannosaurus-rex-lora-v2.png` because the arm length/open-mouth read still needs review, but it is worth keeping as a two-finger forelimb comparison. The current next route is now `tyrannosaurus-rex-twofinger-bodylock-guide-v1.png`, `tyrannosaurus-twofinger-bodylock-crops-v8.png`, and `tyrannosaurus-review-options-v8.png`, with `tools/comfyui/lora_training/theropod_tyrannosaurus/twofinger_bodylock_prompt_schedule.json` defining the guide-conditioned i2i/IP-Control path.
- Herrerasaurus was rechecked against Civitai tags/query results. No usable `Herrerasaurus ischigualastensis` LoRA was found; tag results were either unrelated generic detail/style LoRAs or character/model-family LoRAs. A low-strength `Dinosaur_Generator_v2.0-000011.safetensors` + revised slender ControlNet guide improved agility and texture slightly, but the best improvement came from the guide shape itself, not the LoRA. A later IP-Adapter + ControlNet LoRA test confirmed the same pattern: `dinosaur_practical_fx.safetensors` made texture more cinematic but pushed the animal toward bulky large-theropod anatomy, while `Dinosaur_Generator_v2.0` still risked long-neck/large-head drift and signature-like artifacts. The current first app image is the compact-hand imagegen v2 candidate, while `herrerasaurus-ischigualastensis-bodylock-guide-v1.png`, `herrerasaurus-bodylock-crops-v3.png`, and `herrerasaurus-review-options-v8.png` now define the next compact-hand structure-conditioned route. For this taxon, use guide-conditioned i2i/IP-Control plus a style reference before spending more time on public LoRA search.
- Coelophysis was retested with a revised dry-ground guide and low-strength `Dinosaur_Generator_v2.0-000011.safetensors`. The generic LoRA helped color/texture slightly but made the small forelimbs less reliable. For small Triassic theropods, prefer a hand-authored silhouette guide and use the generic LoRA only as a comparison, not the first-choice route. The current next route is now `coelophysis-bauri-bodylock-guide-v1.png`, `coelophysis-bodylock-crops-v4.png`, and `coelophysis-review-options-v8.png`, with `tools/comfyui/lora_training/small_theropod_coelophysis/bodylock_prompt_schedule.json` defining the guide-conditioned i2i/IP-Control path.
- Allosaurus public LoRAs remain unattractive for the current copyright-safe MVP. The latest Civitai re-check found an Illustrious species LoRA (`https://civitai.com/models/2297868`), but it is not compatible with the current RealVisXL path without a separate Illustrious workflow; the SDXL `Allosaurus (Ark)` candidate is game-derived and weakly rated. The current first app image is the smooth-brow three-finger v4 candidate, while `allosaurus-fragilis-threefinger-bodylock-guide-v1.png`, `allosaurus-threefinger-bodylock-crops-v10.png`, and `allosaurus-review-options-v10.png` now define the next structure-conditioned route. The useful short-term path is guide-conditioned i2i/IP-Control plus a style reference, not more public LoRA search.
- Apatosaurus low-neck tests reinforced the same rule for sauropods: public LoRA is not the bottleneck. ControlNet over a simple guide often flipped the animal into rear-view or high-neck poses, while i2i over the guide gave the clearest low diplodocid silhouette but too flat a render. The current first app image is the small-head v2 candidate, while `apatosaurus-ajax-lowneck-bodylock-guide-v1.png`, `apatosaurus-lowneck-bodylock-crops-v3.png`, and `apatosaurus-review-options-v6.png` now define the next structure-conditioned route. Use guide-conditioned i2i/IP-Control plus a style reference before spending more time on public sauropod LoRA search.
- Brachiosaurus/sauropod re-checks returned mostly cartoon, character, anthro, Pony/Illustrious, or IP-derived LoRAs such as Dinosaucers/Land Before Time style models. These are not suitable as final-source LoRAs for a copyright-safe natural-history atlas. The current best app image is the tail-reduced i2i v4 candidate, while `brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png`, `brachiosaurus-highshoulder-bodylock-crops-v8.png`, and `brachiosaurus-review-options-v8.png` define the next structure-conditioned route. The better short-term sauropod path is guide-conditioned i2i/IP-Control plus a style reference, not more public LoRA search.
- Ankylosaurus remains better served by targeted SDXL inpaint than by the public SD1.5/Illustrious LoRA options. The local SD1.5 Ankylosaurus LoRA can preserve a flat guide silhouette, but it is not an app-quality natural scene path. The best current MVP step was a RealVisXL dorsal-ridge inpaint that reduced tall stegosaur-like spikes while preserving the visible tail club and background.
- Stegosaurus thagomizer tests show that prompt-only SDXL, ordinary RealVisXL ControlNet, and narrow inpaint all tend to omit or erase the four tail spikes. Local geometry overlays are useful as comparison/reference slides: v11b is less graphic and v5b is more diagnostic, but neither is final-quality. A later strict high-strength ControlNet/IP-Adapter pass over `stegosaurus-stenops_shape_v2.png` finally preserved a readable four-spike thagomizer, but the body and plates became too flat/guide-like for primary use. A 2026-06-22 broad-plate retry confirmed the same bottleneck from the plate side: local grafting reads as pasted shell/rock armor, low-strength ControlNet erases the plates, and higher-strength `Dinosaur_Generator_v2.0-000011.safetensors` loses the Stegosaurus body plan entirely. A 2026-06-23 seam-only inpaint pass over the best angular-plate candidate was less destructive but did not open convincing plate gaps; a prompt-only RealVisXL recheck still drifted into turtle, bird, hump-backed, or generic bipedal forms, and low-strength `Dinosaur_Generator_v2.0-000011.safetensors` again drifted toward sauropod/theropod bodies. Production-quality Stegosaurus images likely require a cleared stegosaurian/thagomizer LoRA or a small generated training set focused specifically on plate and tail-spike anatomy.
  - A later clear-plate guide/refiner/IP-Control loop confirmed the same failure in a more controlled way: local guide outputs can make the broad separated plate silhouette obvious, but RealVisXL either preserves the pasted guide look, fuses the plates back into a connected ridge, or rotates/breaks the body under ControlNet. The public `StegosaurusDinosaur_IXL.safetensors` file is still not present in the local LoRA folder or checked download locations, so an Illustrious comparison branch remains untested.
  - A follow-up plain SDXL base and SDXL base + `Dinosaur_Generator_v2.0-000011.safetensors` probe also failed. The base checkpoint still missed the four-spike thagomizer and drifted into theropod/rhinoceros/monster forms, while the generic LoRA pushed Stegosaurus toward bipedal theropods or long-necked animals with only small comb spines. Do not spend more time on broad checkpoint/generic-LoRA Stegosaurus probes.
  - A combined plate/thagomizer reference pass finally produced an app-facing anatomy-review candidate with both broad upright plates and a visible four-spike thagomizer: `assets/dinosaurs/stegosaurus-stenops-plate-thagomizer-ipcontrol-v1.png`. This is useful for MVP comparison, but it is still a `review_hold` result because the torso reads too rounded/shell-like and limb placement needs review. Treat it as evidence that the combined reference is useful for ControlNet, not as proof that the current RealVisXL route can produce final Stegosaurus art without a focused LoRA or reviewed synthetic expansion.
  - A low-body variant of the combined reference reduced that shell-like torso drift. The current first app candidate is now `assets/dinosaurs/stegosaurus-stenops-lowbody-plate-thagomizer-ipcontrol-v1.png`, generated with the angular-plate candidate as a low-weight style source and the low-body guide as ControlNet. It is still `review_hold`, not train-ready, because tail-spike count, plate separation, and hidden legs need review.
  - A narrow tail-tip refinement loop over the low-body candidate did not beat the current primary. Local four-spike guides aligned correctly, but low-denoise refine and strict inpaint did not make the fourth spike materially clearer. Future Stegosaurus work should use a stronger reference-conditioned tail target or focused LoRA/synthetic seeds, not another same-mask tail-tip inpaint retry.
  - The current v6 app candidate has the best natural balance so far, but exact two-row plate placement remains the weak point. `stegosaurus-stenops-plate-topology-guide-v1.png`, `stegosaurus-plate-topology-crops-v12.png`, and `stegosaurus-review-options-v46.png` now define the next ControlNet/i2i route for locking staggered near/far plates before texture polish.
- Plateosaurus was rechecked with targeted Civitai and Hugging Face searches for `Plateosaurus`, `sauropodomorph`, and Triassic dinosaur LoRAs. No useful public species or clade LoRA was found. A stricter herbivore/sauropodomorph prompt moved prompt-only RealVisXL outputs away from toothy predator forms, but did not produce a stronger primary image than the current ControlNet candidate. A revised early-sauropodomorph guide reduced predator drift more than any public LoRA route, though the best output still needs review for head and forelimb proportions. The current first app image is the single-forelimb small-hand v3 candidate, while `plateosaurus-engelhardti-bodylock-guide-v1.png`, `plateosaurus-bodylock-crops-v4.png`, and `plateosaurus-review-options-v12.png` now define the next no-six-leg structure-conditioned route. For this taxon, use guide-first generation or train a small custom early-sauropodomorph LoRA from cleared material.
