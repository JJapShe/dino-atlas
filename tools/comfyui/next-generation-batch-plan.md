# Next Generation Batch Plan

Use this queue after reviewing `assets/dinosaurs/generation-route-dashboard-v1.png` and the app review panel.
Every output remains `needs_review` until manually checked against the identity gate and hard rejection rule.

## Priority Queue

### 1. Velociraptor (`velociraptor-mongoliensis`)

- Focus: dark-speckled plumage, toothed snout, modest attached sickle toe
- Why now: highest identity risk: toothed non-bird head, feathers, and attached sickle toe must survive together
- Current primary: `assets/dinosaurs/velociraptor-mongoliensis-imagegen-v63-source-candidate.png`
- Control guide: `assets/dinosaurs/velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png`
- Schedule: `tools/comfyui/lora_training/dromaeosaur_feathered/identity_bodylock_prompt_schedule.json` (7 prompts)
- Visual color: dark graphite and umber plumage with rust face accents
- Visual pattern: fine speckles, barred tail, darker wing/arm feather edges
- Surface texture: short filament feathers over body, tighter scaly feet
- Signature anatomy: toothed narrow snout, folded forelimbs, modest attached second-toe sickle claw
- Avoid similarity: modern bird head, wing-fan arms, oversized detached hook claws
- Prompt addendum: species-specific color: dark graphite and umber plumage with rust face accents; pattern: fine speckles, barred tail, darker wing/arm feather edges; surface texture: short filament feathers over body, tighter scaly feet; signature anatomy: toothed narrow snout, folded forelimbs, modest attached second-toe sickle claw
- Pass setup: foot-local i2i/control over v63, v65, or review-hold v68 | preserve dark speckled plumage and rust face | reduce hook-claw exaggeration
- Hard reject: Reject outputs whose head reads as a modern bird, whose folded arms become wing fans, or whose sickle claw becomes a giant hook/detached crescent even if the color looks good.

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id velociraptor-mongoliensis --source-image 'assets/dinosaurs/velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png' --seed 2026070201 --seed 2026070202 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_velociraptor_mongoliensis_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/dromaeosaur_feathered/identity_bodylock_prompt_schedule.json' --limit 3 --seed-base 2026070220 --prefix next_velociraptor_mongoliensis_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/dromaeosaur_feathered/identity_bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png' --seed 2026070240 --seed 2026070241 --denoise 0.42 --denoise 0.56 --prefix next_velociraptor_mongoliensis_v1_schedule_i2i
```

### 2. Stegosaurus (`stegosaurus-stenops`)

- Focus: ground-relative upward V thagomizer, bony plates, alternating plates
- Why now: signature plates still need stricter two-row topology and four-spike tail verification
- Current primary: `assets/dinosaurs/stegosaurus-stenops-imagegen-v92-source-candidate.png`
- Control guide: `assets/dinosaurs/stegosaurus-stenops-plate-topology-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/stegosaur_plates_tailspikes/plate_topology_prompt_schedule.json` (7 prompts)
- Visual color: muted green-gray body with pale bone, rust, or ochre dorsal plates
- Visual pattern: plates visibly differ from skin; tail base may keep faint bands
- Surface texture: rough keratin/bone plate material, pebbled body hide
- Signature anatomy: alternating dorsal plates, small head, four legs, four upward V tail spikes
- Avoid similarity: skin-like leather plates, connected sail, radial/five-spike tail cluster
- Prompt addendum: species-specific color: muted green-gray body with pale bone, rust, or ochre dorsal plates; pattern: plates visibly differ from skin; tail base may keep faint bands; surface texture: rough keratin/bone plate material, pebbled body hide; signature anatomy: alternating dorsal plates, small head, four legs, four upward V tail spikes
- Pass setup: tail-local i2i/inpaint over v92 or v100 | rounded tail base | exactly four upward spikes | preserve rough rust-red/pale-bone plate material
- Hard reject: Reject if any spike or tail-point lies parallel to the ground, runs along the tail shaft, continues as a straight point beyond the spikes, forms a radial/five-spike cluster, or if plates share skin-like leather texture.

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id stegosaurus-stenops --source-image 'assets/dinosaurs/stegosaurus-stenops-plate-topology-guide-v1.png' --seed 2026070301 --seed 2026070302 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_stegosaurus_stenops_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/stegosaur_plates_tailspikes/plate_topology_prompt_schedule.json' --limit 3 --seed-base 2026070320 --prefix next_stegosaurus_stenops_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/stegosaur_plates_tailspikes/plate_topology_prompt_schedule.json' --source-image 'assets/dinosaurs/stegosaurus-stenops-plate-topology-guide-v1.png' --seed 2026070340 --seed 2026070341 --denoise 0.42 --denoise 0.56 --prefix next_stegosaurus_stenops_v1_schedule_i2i
```

### 3. Triceratops (`triceratops-horridus`)

- Focus: cool color pattern, skull-attached frill, non-hoofed toes
- Why now: must keep the anti-rhinoceros gate: skull-attached frill, low body, long tail, and non-hoofed toes
- Current primary: `assets/dinosaurs/triceratops-horridus-imagegen-v51-source-candidate.png`
- Control guide: `assets/dinosaurs/triceratops-horridus-skullfrill-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/ceratopsian_triceratops/skullfrill_bodylock_prompt_schedule.json` (7 prompts)
- Visual color: cool slate, teal gray, cream horn tips, restrained rust frill accents
- Visual pattern: mottled face and frill freckles, broken flank spotting
- Surface texture: matte hide with keratin horns and rough frill rim
- Signature anatomy: three horns, skull-attached frill, low ceratopsian body, visible toes
- Avoid similarity: rhinoceros body, shoulder-attached frill, hoof feet, sandy-brown collapse
- Prompt addendum: species-specific color: cool slate, teal gray, cream horn tips, restrained rust frill accents; pattern: mottled face and frill freckles, broken flank spotting; surface texture: matte hide with keratin horns and rough frill rim; signature anatomy: three horns, skull-attached frill, low ceratopsian body, visible toes
- Pass setup: body-lock i2i/control over v51 or v52 | preserve cool mottling | lower rounded torso | prove skull-attached frill and non-hoofed toes
- Hard reject: Reject outputs if the frill attaches to the shoulder/back, the torso reads like a rhinoceros, feet become hoof-like, or the color collapses back to sandy brown.

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id triceratops-horridus --source-image 'assets/dinosaurs/triceratops-horridus-skullfrill-bodylock-guide-v1.png' --seed 2026070401 --seed 2026070402 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_triceratops_horridus_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/ceratopsian_triceratops/skullfrill_bodylock_prompt_schedule.json' --limit 3 --seed-base 2026070420 --prefix next_triceratops_horridus_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/ceratopsian_triceratops/skullfrill_bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/triceratops-horridus-skullfrill-bodylock-guide-v1.png' --seed 2026070440 --seed 2026070441 --denoise 0.42 --denoise 0.56 --prefix next_triceratops_horridus_v1_schedule_i2i
```

### 4. Ankylosaurus (`ankylosaurus-magniventris`)

- Focus: armored skull, color pattern, single attached tail club
- Why now: tail club is present but broad ankylosaur skull/body identity and armor layout still need tightening
- Current primary: `assets/dinosaurs/ankylosaurus-magniventris-imagegen-v40-source-candidate.png`
- Control guide: `assets/dinosaurs/ankylosaurus-magniventris-armor-tailclub-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/ankylosaur_armor_tailclub/armor_tailclub_prompt_schedule.json` (6 prompts)
- Visual color: slate blue, olive gray armor, pale horn and osteoderm highlights
- Visual pattern: irregular armor bands and asymmetrical mottling
- Surface texture: low varied osteoderms, blunt bony skull plates, heavy tail club surface
- Signature anatomy: broad armored skull, cheek horns, four short legs, single attached tail club
- Avoid similarity: smooth lizard/crocodile head, regular tiled shell, missing or split tail club
- Prompt addendum: species-specific color: slate blue, olive gray armor, pale horn and osteoderm highlights; pattern: irregular armor bands and asymmetrical mottling; surface texture: low varied osteoderms, blunt bony skull plates, heavy tail club surface; signature anatomy: broad armored skull, cheek horns, four short legs, single attached tail club
- Pass setup: body-lock i2i/control over v40 with v43 skull-color reference | broad blunt armored skull | varied low osteoderms | one attached club
- Hard reject: Reject outputs if the head reads as a smooth lizard/crocodile, the armor becomes an over-regular tiled shell, the color collapses to plain tan-brown, the tail club is missing/detached/split, or the animal gains extra legs.

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id ankylosaurus-magniventris --source-image 'assets/dinosaurs/ankylosaurus-magniventris-armor-tailclub-guide-v1.png' --seed 2026070501 --seed 2026070502 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_ankylosaurus_magniventris_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/ankylosaur_armor_tailclub/armor_tailclub_prompt_schedule.json' --limit 3 --seed-base 2026070520 --prefix next_ankylosaurus_magniventris_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/ankylosaur_armor_tailclub/armor_tailclub_prompt_schedule.json' --source-image 'assets/dinosaurs/ankylosaurus-magniventris-armor-tailclub-guide-v1.png' --seed 2026070540 --seed 2026070541 --denoise 0.42 --denoise 0.56 --prefix next_ankylosaurus_magniventris_v1_schedule_i2i
```

### 5. Plateosaurus (`plateosaurus-engelhardti`)

- Focus: dark speckled color, no-six-leg gate, lifted hands, thumb claw
- Why now: six-leg and forelimb-ground-contact risks are still the main promotion blockers
- Current primary: `assets/dinosaurs/plateosaurus-engelhardti-imagegen-v25-source-candidate.png`
- Control guide: `assets/dinosaurs/plateosaurus-engelhardti-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/bodylock_prompt_schedule.json` (0 prompts)
- Visual color: charcoal green or blue-gray body with burgundy/copper neck hints
- Visual pattern: cream speckles and restrained tail bands
- Surface texture: fine dry scales, not glossy monster skin
- Signature anatomy: two grounded hind legs, lifted compact forelimbs, visible thumb-claw cue
- Avoid similarity: six-leg read, forelimb ground contact, long theropod hook hands
- Prompt addendum: species-specific color: charcoal green or blue-gray body with burgundy/copper neck hints; pattern: cream speckles and restrained tail bands; surface texture: fine dry scales, not glossy monster skin; signature anatomy: two grounded hind legs, lifted compact forelimbs, visible thumb-claw cue
- Pass setup: hand-local i2i/control over v25 with v27 no-six-leg reference | preserve charcoal-green speckles and tail bands | exactly two grounded hind legs | lifted compact hands
- Hard reject: Reject if any forelimb touches the ground, if the silhouette gains extra legs, if hands become long theropod hooks, or if the color collapses back to plain sandy tan.

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id plateosaurus-engelhardti --source-image 'assets/dinosaurs/plateosaurus-engelhardti-bodylock-guide-v1.png' --seed 2026070601 --seed 2026070602 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_plateosaurus_engelhardti_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/bodylock_prompt_schedule.json' --limit 3 --seed-base 2026070620 --prefix next_plateosaurus_engelhardti_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/plateosaurus-engelhardti-bodylock-guide-v1.png' --seed 2026070640 --seed 2026070641 --denoise 0.42 --denoise 0.56 --prefix next_plateosaurus_engelhardti_v1_schedule_i2i
```

### 6. Tyrannosaurus rex (`tyrannosaurus-rex`)

- Focus: tiny arms, exactly two fingers, skull surface
- Why now: continue structure-guided polishing after higher-risk taxa
- Current primary: `assets/dinosaurs/tyrannosaurus-rex-twofinger-hand-i2i-v4.png`
- Control guide: `assets/dinosaurs/tyrannosaurus-rex-twofinger-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/theropod_tyrannosaurus/twofinger_bodylock_prompt_schedule.json` (0 prompts)
- Visual color: charcoal olive, dark gray flank, pale lower jaw
- Visual pattern: subtle dorsal striping and broken tail bands, not a uniform brown body
- Surface texture: coarse pebbled hide with heavier skull scales
- Signature anatomy: massive skull, deep chest, tiny two-finger forelimbs, counterbalancing tail
- Avoid similarity: generic giant lizard, three-finger hand, overly feathered raptor look
- Prompt addendum: species-specific color: charcoal olive, dark gray flank, pale lower jaw; pattern: subtle dorsal striping and broken tail bands, not a uniform brown body; surface texture: coarse pebbled hide with heavier skull scales; signature anatomy: massive skull, deep chest, tiny two-finger forelimbs, counterbalancing tail
- Pass setup: controlnet_twofinger_bodylock_low_denoise | i2i_controlnet | denoise 0.18-0.32 | control 0.5-0.72
- Hard reject: reject if either visible hand shows a third finger or ambiguous three claw tips

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id tyrannosaurus-rex --source-image 'assets/dinosaurs/tyrannosaurus-rex-twofinger-bodylock-guide-v1.png' --seed 2026070701 --seed 2026070702 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_tyrannosaurus_rex_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/theropod_tyrannosaurus/twofinger_bodylock_prompt_schedule.json' --limit 3 --seed-base 2026070720 --prefix next_tyrannosaurus_rex_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/theropod_tyrannosaurus/twofinger_bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/tyrannosaurus-rex-twofinger-bodylock-guide-v1.png' --seed 2026070740 --seed 2026070741 --denoise 0.42 --denoise 0.56 --prefix next_tyrannosaurus_rex_v1_schedule_i2i
```

### 7. Allosaurus (`allosaurus-fragilis`)

- Focus: low skull, medium arms, three fingers
- Why now: continue structure-guided polishing after higher-risk taxa
- Current primary: `assets/dinosaurs/allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png`
- Control guide: `assets/dinosaurs/allosaurus-fragilis-threefinger-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/theropod_allosaurus/threefinger_bodylock_prompt_schedule.json` (0 prompts)
- Visual color: muted ochre, ash gray, and olive flank contrast
- Visual pattern: low-contrast striping over hips and tail, light brow ridges
- Surface texture: pebbled theropod skin with rough cranial ridges
- Signature anatomy: long low skull, medium three-finger arms, balanced hind legs
- Avoid similarity: T. rex two-finger hands, oversized fantasy jaw, tiny forelimb proportions
- Prompt addendum: species-specific color: muted ochre, ash gray, and olive flank contrast; pattern: low-contrast striping over hips and tail, light brow ridges; surface texture: pebbled theropod skin with rough cranial ridges; signature anatomy: long low skull, medium three-finger arms, balanced hind legs
- Pass setup: controlnet_threefinger_bodylock_low_denoise | i2i_controlnet | denoise 0.2-0.34 | control 0.52-0.76
- Hard reject: reject if either visible hand loses the third finger or reads as two-fingered

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id allosaurus-fragilis --source-image 'assets/dinosaurs/allosaurus-fragilis-threefinger-bodylock-guide-v1.png' --seed 2026070801 --seed 2026070802 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_allosaurus_fragilis_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/theropod_allosaurus/threefinger_bodylock_prompt_schedule.json' --limit 3 --seed-base 2026070820 --prefix next_allosaurus_fragilis_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/theropod_allosaurus/threefinger_bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/allosaurus-fragilis-threefinger-bodylock-guide-v1.png' --seed 2026070840 --seed 2026070841 --denoise 0.42 --denoise 0.56 --prefix next_allosaurus_fragilis_v1_schedule_i2i
```

### 8. Herrerasaurus (`herrerasaurus-ischigualastensis`)

- Focus: compact hands, three main digits, two hind legs
- Why now: continue structure-guided polishing after higher-risk taxa
- Current primary: `assets/dinosaurs/herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png`
- Control guide: `assets/dinosaurs/herrerasaurus-ischigualastensis-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/early_saurischian_herrerasaurus/bodylock_prompt_schedule.json` (0 prompts)
- Visual color: earth red, charcoal brown, and muted cream underside
- Visual pattern: broken flank bars and tail bands
- Surface texture: dry early-theropod scales with compact hand detail
- Signature anatomy: lean early dinosaur body, three main hand digits, long tail, two hind legs
- Avoid similarity: tiny T. rex arms, four-legged stance, generic crocodile/lizard read
- Prompt addendum: species-specific color: earth red, charcoal brown, and muted cream underside; pattern: broken flank bars and tail bands; surface texture: dry early-theropod scales with compact hand detail; signature anatomy: lean early dinosaur body, three main hand digits, long tail, two hind legs
- Pass setup: controlnet_compact_hand_bodylock_low_denoise | i2i_controlnet | denoise 0.18-0.32 | control 0.5-0.74
- Hard reject: reject if arms shrink into tiny T. rex proportions

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id herrerasaurus-ischigualastensis --source-image 'assets/dinosaurs/herrerasaurus-ischigualastensis-bodylock-guide-v1.png' --seed 2026070901 --seed 2026070902 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_herrerasaurus_ischigualastensis_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/early_saurischian_herrerasaurus/bodylock_prompt_schedule.json' --limit 3 --seed-base 2026070920 --prefix next_herrerasaurus_ischigualastensis_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/early_saurischian_herrerasaurus/bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/herrerasaurus-ischigualastensis-bodylock-guide-v1.png' --seed 2026070940 --seed 2026070941 --denoise 0.42 --denoise 0.56 --prefix next_herrerasaurus_ischigualastensis_v1_schedule_i2i
```

### 9. Coelophysis (`coelophysis-bauri`)

- Focus: slender S-neck, small hands, reviewable feet
- Why now: continue structure-guided polishing after higher-risk taxa
- Current primary: `assets/dinosaurs/coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png`
- Control guide: `assets/dinosaurs/coelophysis-bauri-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/small_theropod_coelophysis/bodylock_prompt_schedule.json` (0 prompts)
- Visual color: sand gray, cool olive, and dark dorsal line
- Visual pattern: thin flank striping, small speckles, lightly banded tail
- Surface texture: dry fine scales on a very slender body
- Signature anatomy: slender S-neck, narrow head, small hands, two long hind legs
- Avoid similarity: forelimbs touching ground, extra leg illusion, bulky raptor body
- Prompt addendum: species-specific color: sand gray, cool olive, and dark dorsal line; pattern: thin flank striping, small speckles, lightly banded tail; surface texture: dry fine scales on a very slender body; signature anatomy: slender S-neck, narrow head, small hands, two long hind legs
- Pass setup: controlnet_bodylock_low_denoise | i2i_controlnet | denoise 0.18-0.32 | control 0.48-0.72
- Hard reject: reject if either forelimb touches the ground or reads as a third/fourth leg

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id coelophysis-bauri --source-image 'assets/dinosaurs/coelophysis-bauri-bodylock-guide-v1.png' --seed 2026071001 --seed 2026071002 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_coelophysis_bauri_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/small_theropod_coelophysis/bodylock_prompt_schedule.json' --limit 3 --seed-base 2026071020 --prefix next_coelophysis_bauri_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/small_theropod_coelophysis/bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/coelophysis-bauri-bodylock-guide-v1.png' --seed 2026071040 --seed 2026071041 --denoise 0.42 --denoise 0.56 --prefix next_coelophysis_bauri_v1_schedule_i2i
```

### 10. Apatosaurus (`apatosaurus-ajax`)

- Focus: low neck, similar-height legs, full horizontal tail
- Why now: continue structure-guided polishing after higher-risk taxa
- Current primary: `assets/dinosaurs/apatosaurus-ajax-imagegen-v3-source-candidate.png`
- Control guide: `assets/dinosaurs/apatosaurus-ajax-lowneck-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/sauropod_apatosaurus/bodylock_prompt_schedule.json` (0 prompts)
- Visual color: cool gray, olive, and dust-blue body with pale underside
- Visual pattern: very subtle flank mottling and tail gradients
- Surface texture: heavy matte sauropod hide with broad wrinkles
- Signature anatomy: low long neck, level back, pillar legs, long horizontal whip tail
- Avoid similarity: high-shouldered Brachiosaurus silhouette, vertical neck, short tail
- Prompt addendum: species-specific color: cool gray, olive, and dust-blue body with pale underside; pattern: very subtle flank mottling and tail gradients; surface texture: heavy matte sauropod hide with broad wrinkles; signature anatomy: low long neck, level back, pillar legs, long horizontal whip tail
- Pass setup: controlnet_lowneck_bodylock_low_denoise | i2i_controlnet | denoise 0.2-0.34 | control 0.55-0.78
- Hard reject: reject if the silhouette drifts toward high-shouldered Brachiosaurus

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id apatosaurus-ajax --source-image 'assets/dinosaurs/apatosaurus-ajax-lowneck-bodylock-guide-v1.png' --seed 2026071101 --seed 2026071102 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_apatosaurus_ajax_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/sauropod_apatosaurus/bodylock_prompt_schedule.json' --limit 3 --seed-base 2026071120 --prefix next_apatosaurus_ajax_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/sauropod_apatosaurus/bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/apatosaurus-ajax-lowneck-bodylock-guide-v1.png' --seed 2026071140 --seed 2026071141 --denoise 0.42 --denoise 0.56 --prefix next_apatosaurus_ajax_v1_schedule_i2i
```

### 11. Brachiosaurus (`brachiosaurus-altithorax`)

- Focus: high shoulders, taller forelimbs, short thick tail
- Why now: continue structure-guided polishing after higher-risk taxa
- Current primary: `assets/dinosaurs/brachiosaurus-altithorax-imagegen-v16-source-candidate.png`
- Control guide: `assets/dinosaurs/brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png`
- Schedule: `tools/comfyui/lora_training/sauropod_brachiosaurus/bodylock_prompt_schedule.json` (0 prompts)
- Visual color: warm gray, moss green, and light tan underside
- Visual pattern: soft vertical neck mottling and shoulder patches
- Surface texture: thick folded hide on high shoulders and neck
- Signature anatomy: tall forelimbs, high shoulders, upright neck, shorter thick tail
- Avoid similarity: low Diplodocus/Apatosaurus body plan, equal leg height, whip tail
- Prompt addendum: species-specific color: warm gray, moss green, and light tan underside; pattern: soft vertical neck mottling and shoulder patches; surface texture: thick folded hide on high shoulders and neck; signature anatomy: tall forelimbs, high shoulders, upright neck, shorter thick tail
- Pass setup: controlnet_bodylock_low_denoise | i2i_controlnet | denoise 0.22-0.34 | control 0.55-0.75
- Hard reject: reject if the silhouette drifts toward low-shouldered Apatosaurus or Diplodocus

ControlNet probe:

```powershell
python tools/comfyui/scripts/run_controlnet_experiment.py --taxon-id brachiosaurus-altithorax --source-image 'assets/dinosaurs/brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png' --seed 2026071201 --seed 2026071202 --strength 0.45 --strength 0.62 --end-percent 0.56 --end-percent 0.72 --prefix next_brachiosaurus_altithorax_v1_controlnet --clean-corners
```

Schedule prompt probe:

```powershell
python tools/comfyui/scripts/run_lora_seed_schedule.py --schedule 'tools/comfyui/lora_training/sauropod_brachiosaurus/bodylock_prompt_schedule.json' --limit 3 --seed-base 2026071220 --prefix next_brachiosaurus_altithorax_v1_schedule
```

Low-denoise i2i probe:

```powershell
python tools/comfyui/scripts/run_schedule_i2i_experiment.py --schedule 'tools/comfyui/lora_training/sauropod_brachiosaurus/bodylock_prompt_schedule.json' --source-image 'assets/dinosaurs/brachiosaurus-altithorax-highshoulder-bodylock-guide-v1.png' --seed 2026071240 --seed 2026071241 --denoise 0.42 --denoise 0.56 --prefix next_brachiosaurus_altithorax_v1_schedule_i2i
```
