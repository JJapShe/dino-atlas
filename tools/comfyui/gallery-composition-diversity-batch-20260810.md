# Gallery composition diversity batch 2026-08-10

This is an intake record, not an anatomy approval. One image remains a non-representative `anatomy review` candidate in the ignored local review queue; two images failed independent original-size review and were deleted as rejected. No candidate may replace an approved gallery slot until an original-size anatomy review passes.

## Selection

| Taxon | Existing pair | Similarity | Intended slot | New composition | Intake status |
| --- | --- | ---: | ---: | --- | --- |
| Quetzalcoatlus northropi | S1/S5 | 0.997 direct | 5 | elevated rear-three-quarter banked flight, distant separated Alamosaurus | deleted-rejected; cropped wingtip and membrane continuity gate failed |
| Psittacosaurus mongoliensis | S1/S7 | 0.971 direct | 7 | vertical ground-level rear-three-quarter, tail diagonal, quiet foraging | review-hold; candidate max 0.531 |
| Ankylosaurus magniventris | S1/S5 | 0.783 direct | 5 | elevated rear-three-quarter oxbow scene with distant counter-diagonal herd | deleted-rejected; skull, armor, feet, and club identity gates failed |

The first two Psittacosaurus attempts were rejected before enqueue because their bristles spread onto the torso or rump. After enqueue, the Quetzalcoatlus and Ankylosaurus selections also failed independent original-size anatomy review and were deleted through the exact-filename review gate. Their hashes and rejection reasons remain in `gallery-composition-diversity-batch-20260810.json`; generated-cache and staging pixels were moved to the Windows Recycle Bin after exact SHA-256 validation, and review DB history remains.

## Shared provenance

- Source: OpenAI built-in image generation (`image_gen`), generated 2026-08-10.
- Rights record: generated project assets under applicable OpenAI service terms; original project prompts; no external copyrighted reconstruction, franchise frame, or named-artist style used.
- Seed: provider not exposed.
- Workflow: anatomy-led composition-diversity v1; original-size automated visual intake; manual anatomy approval required.
- Promotion gate: representative `false`; review status `review-hold`; no automatic promotion, deletion, or app integration.
- Composition gate: every selected candidate must remain below 0.58 structural similarity against every approved slot of the same taxon.

## Quetzalcoatlus northropi

```text
Use case: historical-scene
Asset type: Dino Atlas wide gallery candidate, anatomy-review only
Primary request: Create a scientifically cautious, naturalistic reconstruction of one Quetzalcoatlus northropi banking in flight over a broad Late Cretaceous Javelina Formation river floodplain, with two very small distant Alamosaurus silhouettes on a far sandbar only as separated ecological context.
Scene/backdrop: semi-arid river corridor, patchy conifers and low vegetation, broad channel and sandbars, clear atmospheric depth; no modern plants or objects.
Subject: one giant azhdarchid pterosaur, not a dinosaur. Q. northropi is known from fragmentary giant wing material, so use a conservative azhdarchid comparison reconstruction: very long neck, small compact torso, short tail, long low toothless beak, no oversized Pteranodon-style rear crest.
Style/medium: highly detailed natural-history museum paleoart, realistic living animal, original project-owned visual, not styled after any named artist or franchise.
Composition/framing: 16:9 landscape environmental shot, entirely different from a centered frontal underside view. Camera is slightly above and behind the animal in a lateral rear-three-quarter view as it banks across the upper-right third; show the complete silhouette with generous landscape around it. The near and far wings read at different angles and sizes; the distant sauropods remain tiny and physically separate.
Critical anatomy lock: exactly two forelimb wings and exactly two hind legs. Each wing is a forelimb with exactly one enormously elongated fourth finger supporting one continuous main wing membrane. The membrane must remain visibly connected from the elongated finger along the flank to the same-side lower leg/ankle; no cut, gap, floating flap, detached membrane, or membrane passing through a leg. At each wrist show only three short free clawed fingers I–III, not extra hands. One head, one neck, one torso, two wings, two hind legs, one very short tail. Natural joints and continuous shoulder-to-wing anatomy.
Constraints: no touching or attacking dinosaurs; no gore; no text; no watermark; no logo; no duplicate animal parts; no hidden or fused hind legs; no bat ears, dragon horns, teeth, bird feathers, long tail, tail vane, or marine Pteranodon scene.
```

## Psittacosaurus mongoliensis

```text
Use case: historical-scene
Asset type: Dino Atlas vertical mobile gallery candidate, anatomy-review only
Primary request: A scientifically cautious adult Psittacosaurus mongoliensis foraging in an Early Cretaceous inland Asian floodplain, with a clearly limited genus-level tail-bristle row and a composition unlike a flat side-view catalog portrait.
Scene/backdrop: sandy alluvial channel margin after light rain, low seed ferns and shrubs, sparse conifers in soft dawn haze; no modern lawn grass or flowers.
Subject: one small adult Psittacosaurus. Small head relative to body, closed rounded parrot-like beak, high nostril, short broad rear skull shelf, modest paired pyramidal jugal horns; no large frill, nose horn, brow horns, or macaw-sized head.
Style/medium: highly detailed natural-history museum paleoart, realistic living animal, original project-owned visual, not styled after any named artist or franchise.
Composition/framing: vertical 4:5 portrait. Ground-level rear-three-quarter view. The animal stands bipedally in the lower-right half and bends its neck to nibble a shrub. Its one complete tail leaves the pelvis, curves broadly across the open center, then points toward the upper-left, so the tail is visually separate from the back and its entire dorsal edge is readable. Not a flat lateral standing pose.
Critical limb lock: exactly two short forelimbs held off the ground and visibly separated, exactly two strong hind legs, and exactly one tail continuous from the pelvis. Each hand has four digits with a tiny reduced fourth and no fifth; each hind foot has four toes with toe I shorter than II–IV. No extra limb, fused leg, duplicate foot, or second tail.
Critical bristle lock: the back, shoulders, torso, hips, and tail base must be completely smooth and bristle-free. Leave a clear bare gap after the pelvis. Then place one restrained single row of long, thin cylindrical bristles only on the middle third of the dorsal tail, and stop well before the distal third. No bristle anywhere else. This is comparative Psittacosaurus sp. genus-level context, not confirmed for P. mongoliensis.
Constraints: quiet foraging only; no other animals; no text; no watermark; no logo; no body spines, body feathers, porcupine coat, armor plates, huge frill, facial horns beyond modest jugal horns, theropod teeth, sickle claws, quadrupedal adult stance, five-fingered hands, three-toed feet, or gore.
```

## Ankylosaurus magniventris

```text
Use case: historical-scene
Asset type: Dino Atlas wide gallery candidate, anatomy-review only
Primary request: Create a scientifically grounded, compositionally distinct Late Cretaceous ecology scene with one Ankylosaurus magniventris calmly browsing low floodplain plants while a small group of Edmontosaurus crosses a distant channel, with no contact.
Scene/backdrop: Hell Creek floodplain mosaic, shallow oxbow channel, wet sand, low ferns and flowering shrubs, scattered conifers, broken sunlight after rain; no modern grass lawn.
Subject: foreground Ankylosaurus magniventris as a wide, very low, heavy quadruped about eight metres long, with a broad low skull and one complete tail club. The distant Edmontosaurus are small separated context only.
Style/medium: highly detailed natural-history museum paleoart, realistic living animals, original project-owned visual, not styled after any named artist or franchise.
Composition/framing: 16:9 landscape environmental view from a moderately elevated rear-three-quarter camera. The Ankylosaurus occupies the lower-left half, angled diagonally away toward the center with its head lowered to browse. Its full tail arcs across open wet ground toward the lower-right, leaving clear negative space around the club. The distant hadrosaurs form a small counter-diagonal high in the background. This must not resemble a low eye-level left-facing lateral catalog portrait.
Critical anatomy lock: exactly four weight-bearing legs, all naturally attached and grounded; one broad low body; one broad skull; one continuous tail from pelvis through a stiff handle to exactly one integrated low oval terminal club. No duplicated tail, detached club, two-ball club, paddle tail, or long round mallet.
Armor lock: flat polygonal skull armor; two continuous U-shaped cervical half-rings; four to five transverse rows of varied low oval body osteoderms separated by skin folds. Keep armor low and integrated, not rows of giant glossy bubbles. No huge shoulder spikes and no fused turtle-like pelvic shell.
Constraints: calm browsing and distant coexistence only; no attack; no gore; no text; no watermark; no logo; no extra or fused legs; no elephant feet; no spikes replacing the club; no cropped head, feet, tail, or club.
```

## Rejected-before-enqueue prompt records

These prompt blocks preserve the exact provider-revised text for deleted attempts whose pixels never entered the review queue.

### Psittacosaurus body-bristle drift attempt

```text
Use case: historical-scene
Asset type: Dino Atlas portrait gallery candidate for mobile, anatomy-review only
Primary request: Create a scientifically cautious Psittacosaurus scene that demonstrates the genus-level tail-bristle evidence without copying the existing left-facing lateral standing portrait. Show one adult Psittacosaurus mongoliensis walking slowly and lowering its beak toward low vegetation in an Early Cretaceous inland Asian floodplain.
Scene/backdrop: sandy alluvial ground after light rain, scattered low ferns and shrubs, sparse conifers far behind, soft dawn light; no modern grass lawn or flowers.
Subject: one small adult Psittacosaurus mongoliensis. Small head relative to body, closed rounded parrot-like beak, high nostril, short wide rear skull shelf, modest paired pyramidal jugal horns; no large ceratopsian frill or facial horns.
Style/medium: highly detailed natural-history museum paleoart, realistic living animal, original project-owned visual, not styled after any named artist or franchise.
Composition/framing: vertical 4:5 portrait for mobile. Low rear-three-quarter view, animal moving diagonally away from lower-left toward upper-right with its head turned down toward a shrub. Show the full body and complete tail. The tail forms a strong diagonal through the frame and is the clearest feature; this must not be a flat lateral catalog pose.
Critical anatomy lock: adult biped with exactly two short forelimbs held off the ground, exactly two strong hind legs, and one tail continuous from the pelvis. Each visible hand has four digits, with a very small reduced fourth digit and no fifth. Each hind foot has four toes, with toe I shorter than II–IV. No extra limb, fused leg, duplicated foot, or second tail.
Tail-bristle evidence boundary: include one restrained single row of long, narrow cylindrical bristles only along the dorsal base-to-middle portion of the tail, corresponding to the genus-level Psittacosaurus sp. soft-tissue specimen. Do not cover the whole body or full tail in feathers. This bristle row is comparative genus-level context, not a confirmed diagnostic trait of P. mongoliensis.
Constraints: natural quiet foraging only; no other animal; no text; no watermark; no logo; no oversized macaw head; no huge frill; no nasal or brow horn; no theropod teeth or sickle claws; no quadrupedal adult stance; no five-fingered hands; no three-toed feet; no gore.
```

### Psittacosaurus targeted tail-bristle edit attempt

```text
Use case: precise-object-edit
Input images: Image 1 is the edit target, a vertical rear-three-quarter Psittacosaurus foraging scene.
Primary request: Correct only the tail-bristle placement and limb readability while preserving the vertical 4:5 composition, camera angle, animal identity, body proportions, quiet foraging pose, lighting, color pattern, and floodplain background.
Tail-bristle correction: remove every bristle, spike, quill, or feather from the back, shoulders, torso, hip, and final distal half of the tail. Keep exactly one restrained single row of long, narrow, round cylindrical bristles on the dorsal base-to-middle section of the one tail only, beginning just behind the pelvis and ending well before the distal tail. The bristles must not become armor plates, porcupine spines, a sail, or full-body feathering. This remains comparative genus-level Psittacosaurus sp. context, not a confirmed diagnostic trait of P. mongoliensis.
Limb correction: the adult remains bipedal with exactly two short forelimbs held off the ground, both naturally attached and distinguishable, and exactly two strong hind legs. Each hand has four digits with a tiny reduced fourth and no fifth; each foot has four toes with toe I shorter than II–IV. Preserve one continuous tail and one head.
Head lock: small head relative to body, closed rounded parrot-like beak, high nostril, short rear skull shelf, modest paired jugal horns; no large frill or other facial horns.
Constraints: do not change the scene or framing; no extra limb, fused leg, duplicated foot, second tail, quadrupedal stance, body quills, text, watermark, logo, or gore.
```
