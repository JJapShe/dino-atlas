# Gallery composition diversity batch 2026-08-11 B4

This is an intake record, not an anatomy approval. Two images remain non-representative `anatomy review` candidates in the ignored local review queue. No candidate may replace an approved gallery slot until an original-size manual anatomy review passes.

## Selection

| Taxon | Existing pair | Similarity | Intended slot | New composition | Intake status |
| --- | --- | ---: | ---: | --- | --- |
| Parasaurolophus walkeri | S1/S2 | 0.579 mirrored | 2 | vertical front-three-quarter head-and-complete-crest dawn portrait | review-hold; candidate max 0.482 |
| Edmontosaurus annectens | S1/S2 | 0.604 direct, recolor risk | 2 | vertical low front-three-quarter gravel-bar approach in depth | review-hold; candidate max 0.493 |

Carnotaurus was also selected for this batch. Three successive attempts were rejected before enqueue because the image generator repeatedly rendered the vestigial forehands as long hooked claws instead of compact reduced four-digit hands. The first Edmontosaurus attempt was rejected because its back became a large hump and its feet became column-like. Exact hashes, prompt records, and reasons remain in the JSON. After exact-path and SHA-256 validation, all generated-cache and staging copies of those four rejected images were moved to the Windows Recycle Bin and never entered the review queue.

## Shared provenance

- Source: OpenAI built-in image generation (`image_gen`), generated 2026-08-11; approved Dino Atlas images and explicitly recorded prior rejected composition references were used only as project-owned inputs.
- Rights record: generated project assets under applicable OpenAI service terms; original project prompts and project-owned inputs only; no external copyrighted reconstruction, franchise frame, or named-artist style used.
- Seed: provider not exposed.
- Workflow: anatomy-led composition-diversity v3; exact input reference paths and hashes; original-size automated and independent visual intake; manual anatomy approval required.
- Promotion gate: representative `false`; review status `review-hold`; no automatic promotion or app integration.
- Composition gate: both retained candidates remain below 0.58 structural similarity against every approved slot of the same taxon.

## Parasaurolophus walkeri

```text
Use case: scientific-educational natural-history paleoart for ages 5-14.
Asset type: Dino Atlas mobile-vertical S2 color-pattern and identity-detail diversity candidate; anatomy-review only.
Input Image 1 is the project-owned approved Parasaurolophus walkeri species-identity reference only. Preserve the diagnostic skull and low tubular crest identity, but create a genuinely new image. Do not mirror, recolor, trace, or reuse the side-profile full-body composition, riverbank layout, pose, camera, or lighting of Image 1.

Primary scene: one calm living adult Parasaurolophus walkeri pausing among low broadleaf plants on a Late Cretaceous floodplain at cool dawn. No other animal.

Composition: vertical 4:5 portrait, close front-right three-quarter head, complete crest, neck, and upper shoulder study. Camera slightly below eye level. The head turns gently toward the viewer while the long tubular crest sweeps diagonally upward and back across open sky. Keep the entire snout tip, jaw, eye, back of skull, and complete crest tip inside frame with generous clearance. Intentionally crop cleanly at the upper shoulder before either forelimb; no partial hand, leg, hip, or tail enters frame. This must read as a deliberate head-and-crest detail, not a cropped catalog body and not a mirrored side view.

Identity lock: exactly one head. One single solid tubular crest attached continuously to the skull, low and long, longer than the head, gently sweeping backward and slightly downward; never hook-shaped, U-shaped, branched, paired, fan-shaped, helmet-like, or disconnected. Long low toothless beak, deep cheek, restrained eye, thick medium-length neck. No horn, frill, teeth, external ear, bird beak, extra crest, duplicate jaw, giant eye, or fantasy ornament.

Color and pattern: muted warm umber face and crest base, cool slate-olive neck, dusty turquoise-gray throat, irregular small ochre flecks and broken maroon cloud patches that vary naturally in size and spacing. Asymmetric, soft-edged markings; no perfect stripes, rings, rows, mirrored bilateral pattern, neon color, or palette-only copy.

Environment and style: softly blurred dawn floodplain plants, pale mist, and distant low trees; realistic living-animal skin and subtle soft tissue; high-detail natural-history museum realism; original project-owned visual, no named-artist or franchise style. No text, watermark, logo, gore, wound, attack, jewelry, harness, modern object, partial limb, extra animal, or cropped crest.
```

## Edmontosaurus annectens

```text
Create a new scientific-educational Edmontosaurus annectens reconstruction. Image 1 is only a reference for the useful vertical 4:5 braided-channel depth, cool sunrise, and diagonal movement; do not copy its faulty hump, dorsal bumps, column feet, pose, or exact pixels. Image 2 is the project-owned approved species-identity and cautious soft-tissue reference. This is an anatomy-review-only S2 color-pattern diversity candidate for ages 5-14, not a representative.

New composition: one complete adult calmly approaching the low ground-level camera at a gentle front-left three-quarter angle across a firm wet gravel bar. The head sits in the upper-left third, the deep torso recedes toward the upper-right, and one continuous tail continues into background depth with the tip fully inside frame. The near forehand is clearly planted in the lower-left foreground, the far forehand is offset farther back with open gravel between them, and both hind feet are separately visible on firm gravel. Do not submerge or hide any foot; water channels remain behind and beside the animal only. Keep the full animal and every extremity in frame.

Head lock: one long low crestless skull, one wide closed toothless beak, one restrained visible eye. No cranial crest, horn, teeth, duck feathers, ear pinna, oversized eye, or fantasy ornament.

Back lock: a naturally level-to-gently-arched hadrosaur back, never a bison hump, camel hump, shoulder dome, or tall sail. Preserve only a VERY THIN, LOW, CONTINUOUS fleshy midline ridge along neck and torso, close to the skin and less than a few centimeters visually. Behind the hips it transitions into one SHORT DENSE WEDGE of TINY tail spines that quickly diminish; no large rounded knobs, no coarse bumps, no tall spikes, no mane, and no quills continuing from the neck.

Count and foot lock: exactly two forelimbs attached at the shoulders and exactly two compact mitten-like forehands. Each forehand is a single padded unit supported by central weight-bearing digits, not spread human fingers and not an elephant stump. Exactly two robust hind legs attached at the hips and exactly two complete hind feet. Each hind foot has exactly three broad wedge-shaped hoof-like toes plus one low heel pad, all clearly connected through one ankle. Exactly one tail. No extra limb, duplicated reflection-foot, fused legs, hidden foot, amputated hand, rhino/elephant column foot, bipedal pose, or cropped extremity.

Color and pattern: deep cool umber back, smoky blue-gray flanks, muted clay-orange face and thin midline, pale olive underside, irregular broken cream flecks and diffuse charcoal patches with natural asymmetry. No perfect rows, rings, zebra bands, mirror symmetry, neon colors, or palette-only copy.

Natural-history museum realism, original project-owned visual, no named-artist/franchise style. No other animal, attack, blood, wound, text, watermark, logo, modern object, mud hiding feet, regular footprint pattern, or extra tail.
```
