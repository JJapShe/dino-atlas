# Reference Checklist

Last updated: 2026-08-08

Use this checklist before promoting any generated dinosaur image above `diagnostic only`.

## Promotion Rule

- Compare the candidate against at least one reliable natural-history source before promotion.
- Do not promote an image because it is visually polished if the body plan or diagnostic traits match the wrong animal.
- Treat AI comparison images as hypotheses, not evidence. Reference sources and fossil-informed reconstructions set the gate.

## Tyrannosaurus rex

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/tyrannosaurus.html
- American Museum of Natural History: https://www.amnh.org/exhibitions/permanent/saurischian-dinosaurs/tyrannosaurus-rex

Must read as:

- massive Late Cretaceous tyrannosaurid theropod, not Allosaurus or a generic three-finger theropod
- very large deep skull, thick neck, robust torso, two powerful hind legs, and long heavy balancing tail
- tiny forelimbs held close to the chest
- exactly two short clawed fingers on each tiny hand when hands are visible
- visible three-toed theropod feet on dry ground for limb-count review

Reject if:

- forelimbs become long, medium-sized, three-fingered, wing-like, or allosaur-like
- hands show a third finger, human-like fingers, or claws hidden enough to block count review
- brow ridges become fantasy horns, decorative knobs, or crest-like spikes
- legs, feet, hands, or tail are cropped or hidden enough to block review
- logo bars, source-like bottom text, captions, or watermarks appear

Temporary app rule:

- Keep `tyrannosaurus-rex-twofinger-hand-i2i-v4.png` first as the current `count-level pass` because it preserves the v3 massive body, calmer jaw, lower brow read, visible tiny chest-held forelimb scale, dry three-toed feet, robust torso, and full heavy tail while making the compact two-finger hand cue slightly cleaner. Keep `tyrannosaurus-twofinger-hand-i2i-crops-v4.png` and `tyrannosaurus-review-options-v7.png` directly below it as the close-review gates, then keep `tyrannosaurus-rex-twofinger-bodylock-guide-v1.png`, `tyrannosaurus-twofinger-bodylock-crops-v8.png`, and `tyrannosaurus-review-options-v8.png` as the next structure-control route for preventing three-finger or allosaur-like arm drift. Keep `tyrannosaurus-rex-smoothbrow-twofinger-imagegen-v3.png`, `tyrannosaurus-smoothbrow-twofinger-crops-v3.png`, `tyrannosaurus-rex-calmjaw-twofinger-comparison-v3.png`, `tyrannosaurus-rex-visiblearms-comparison-v3.png`, `tyrannosaurus-rex-visible-twofinger-imagegen-v2.png`, `tyrannosaurus-rex-broadside-twofinger-comparison-v2.png`, `tyrannosaurus-rex-twofinger-imagegen-v1.png`, `tyrannosaurus-rex-compact-twofinger-inpaint-v1.png`, `tyrannosaurus-rex-tuckedarms-lora-v1.png`, and `tyrannosaurus-rex-lora-v2.png` as comparison gates. Do not treat the new first image as final approval until exact claw shape and skull surface texture are checked against references.

- 2026-07-01 P1 follow-up: keep `tyrannosaurus-p1-v10-v12-review-sheet.png` and `tyrannosaurus-p1-v10-v12-crops.png` as the current prompt-only decision sheets. Treat `tyrannosaurus-rex-imagegen-v12-source-candidate.png` as `review_hold` only: it makes the hand easier to inspect, but the forelimb is larger than the current v4 seed and the two-finger cue is exaggerated enough to risk allosaur-like arm drift. Treat `tyrannosaurus-rex-imagegen-v10-source-candidate.png` and `tyrannosaurus-rex-imagegen-v11-source-candidate.png` as `reject_reference` because the hands read long, ambiguous, or potentially three-pronged. Keep v4 first until a candidate proves tiny-arm scale and exactly two compact fingers together.
- 2026-07-02 P2 v13-v15 follow-up: keep `tyrannosaurus-p2-v13-v15-review-sheet.png` and `tyrannosaurus-p2-v13-v15-crops.png` as the newest tiny-arm/two-finger prompt gate. Treat `tyrannosaurus-rex-imagegen-v15-source-candidate.png` as the best P2 `review_hold` because it preserves tiny tucked forelimb scale better than v14/v12, but do not promote it because the two-finger hand cue remains too soft. Treat `tyrannosaurus-rex-imagegen-v14-source-candidate.png` as `review_hold` only because it has clearer two-finger visibility but larger arm/hand scale. Treat `tyrannosaurus-rex-imagegen-v13-source-candidate.png` as `reject_reference` because the hand can read as three-pronged. Keep v4 first until tiny arms and exactly two compact fingers are proven together.
- 2026-07-02 P3 v16-v18 follow-up: keep `tyrannosaurus-p3-v16-v18-review-sheet.png` and `tyrannosaurus-p3-v16-v18-crops.png` as the latest tiny-arm/two-finger prompt gate. Treat `tyrannosaurus-rex-imagegen-v18-source-candidate.png` as the best P3 `review_hold` because it preserves a massive T. rex body, very small chest-held forelimbs, two hind legs, dry feet, and long tail, but keep it below promotion because the two-finger cue remains too crop-soft. Treat `tyrannosaurus-rex-imagegen-v16-source-candidate.png` as a secondary `review_hold` because the hand overlaps shadow. Treat `tyrannosaurus-rex-imagegen-v17-source-candidate.png` as `reject_reference` because the hand can read as three-pronged and the arm scale creeps larger. Keep v4 first until tiny arms and exactly two compact fingers pass together.

## Triceratops horridus

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/triceratops.html
- American Museum of Natural History: https://www.amnh.org/exhibitions/permanent/ornithischian-dinosaurs/triceratops
- Britannica: https://www.britannica.com/animal/Triceratops

Must read as:

- large quadrupedal ceratopsian dinosaur
- exactly two long brow horns and one shorter nasal horn
- large solid frill attached to the back of the skull, not the shoulders or back
- parrot-like beak, preferably closed mouth for the MVP card
- long tail and dinosaur limbs with visible toes or blunt claws

Reject if:

- the torso, shoulder hump, head mass, or feet read as rhinoceros-like
- feet read as mammal hooves
- the frill reads as a dorsal sail, shoulder sail, or back plate
- extra cheek horns, side horns, spines, or open monster mouth appear
- the image is a close-up that hides the tail, legs, or body plan

Temporary app rule:

- Keep `triceratops-horridus-imagegen-v51-source-candidate.png` first as the current app `count-level pass`, but do not treat it as final approval. It improves gallery-wide color separation with a cool blue-gray, pale-mottled body while keeping the anti-rhino gates: full long tail, closed beak, exactly two brow horns plus one nasal horn, skull-attached frill, four visible dinosaur limbs, and separated non-hoofed toes. Keep `triceratops-p9-v49-v51-review-sheet.png` and `triceratops-p9-v49-v51-crops.png` as the latest close-review gates; the P9 pass keeps v49 and v50 as review holds and demotes v43 to previous familiar anti-rhino comparison. Keep `triceratops-p8-v46-v48-review-sheet.png`, `triceratops-p8-v46-v48-crops.png`, `triceratops-p7-v43-v45-review-sheet.png`, `triceratops-p7-v43-v45-crops.png`, the previous first v41, v44, v45, `triceratops-p6-v40-v42-review-sheet.png`, `triceratops-p6-v40-v42-crops.png`, v42/v40, v22, and `triceratops-horridus-skullfrill-bodylock-guide-v1.png`, `triceratops-skullfrill-bodylock-crops-v10.png`, and `triceratops-review-options-v16.png` as structure-control and comparison gates for preventing rhinoceros drift. Keep the older toe/frill comparisons, schedule+i2i rejection, and closed-beak rhino-risk failures as comparison gates. Do not mark the taxon final until exact non-hoof toe anatomy, beak closure, torso mass, skull/frill proportion, frill rim ornament, and non-sandy natural color pass reference review. Do not promote whole-body i2i if it reopens the mouth or shows teeth, and do not promote prompt-only closed-beak retries if they recover mammal-like rounded torso mass.

- 2026-07-01 P1 follow-up: keep `triceratops-p1-v25-review-sheet.png` and `triceratops-p1-v25-crops.png` as the current v22/v25 decision sheets. Treat `triceratops-horridus-imagegen-v25-source-candidate.png` as review_hold only: it improves full-body visibility, frill/tail/feet review, and remains project-owned, but the beak/mouth reads partly open and the heavy body still carries mild rhinoceros risk. Add it to the ceratopsian LoRA manifest as review_hold, not train_seed.
- 2026-07-01 P1 v27 follow-up: keep `triceratops-horridus-imagegen-v27-source-candidate.png`, `triceratops-p1-v27-review-sheet.png`, and `triceratops-p1-v27-crops.png` as closed-beak review_hold evidence only. V27 improves the sealed mouth seam over v25/v26 while keeping skull-attached frill, exactly three facial horns, long tail, and visible feet, but the rounded torso and rear-leg overlap still carry rhinoceros/mammal-body risk. Keep `triceratops-horridus-imagegen-v26-source-candidate.png` as reject_reference because the black mouth gap reopens the beak. Do not promote v27 or train from it unless a later route proves low elongated ceratopsian body, closed beak, non-hoofed toes, long tail, and skull-attached frill together.
- 2026-07-01 P2 v28-v30 follow-up: keep `triceratops-p2-v28-v30-review-sheet.png` and `triceratops-p2-v28-v30-crops.png` as an older anti-rhino prompt gate. Treat `triceratops-horridus-imagegen-v28-source-candidate.png` as `review_hold` only: it is the best new project-owned prompt candidate for three horns, skull-attached frill, closed beak, long tail, and visible toes, but its torso and shoulder mass still carry mild rhinoceros risk. Treat `triceratops-horridus-imagegen-v30-source-candidate.png` as `review_hold` only because the head/frill/tail cues are useful but the rounded torso and decorative frill rim do not beat v22. Treat `triceratops-horridus-imagegen-v29-source-candidate.png` as `reject_reference` because it reinforces round, shoulder-heavy rhino-body drift. Superseded by P6 v41 for the app-first slot.
- 2026-07-02 P3 v31-v33 follow-up: keep `triceratops-p3-v31-v33-review-sheet.png` and `triceratops-p3-v31-v33-crops.png` as an older prompt-only anti-rhino gate. Treat `triceratops-horridus-imagegen-v33-source-candidate.png` as `review_hold` only because it has the best fresh closed-beak, skull-frill, three-horn, long-tail, and visible-toe balance, but the torso is still rounded and shoulder-heavy enough to carry rhinoceros risk. Treat `triceratops-horridus-imagegen-v31-source-candidate.png` and `triceratops-horridus-imagegen-v32-source-candidate.png` as `reject_reference` because their useful head/frill cues are outweighed by round mammal-body drift. Superseded by P6 v41 for the app-first slot.
- 2026-07-02 P4 v34-v36 follow-up: set app `reviewStatus` back to `검수중`; do not leave Triceratops marked as approved. Keep `triceratops-p4-v34-v36-review-sheet.png` and `triceratops-p4-v34-v36-crops.png` as an older anti-rhino prompt gate. Treat `triceratops-horridus-imagegen-v35-source-candidate.png` as the best fresh `review_hold` because it improves the longer body, long tail, closed beak, three-horn read, and visible non-hoofed toes, but the torso/frill ornament still need close review. Treat `triceratops-horridus-imagegen-v34-source-candidate.png` as secondary `review_hold` only, and `triceratops-horridus-imagegen-v36-source-candidate.png` as `reject_reference` because the body returns to rounded mammal-like mass. Superseded by P6 v41 for the app-first slot.
- 2026-07-02 P5 v37-v39 follow-up: keep `triceratops-p5-v37-v39-review-sheet.png` and `triceratops-p5-v37-v39-crops.png` as the previous prompt-only anti-rhino gate. Treat `triceratops-horridus-imagegen-v38-source-candidate.png` as the best P5 `review_hold` because it has the strongest immediate Triceratops read with skull-attached frill, exactly three facial horns, closed beak, long tail, and separated toes, but keep it below promotion because the torso remains rounded/barrel-like and could reinforce mammal-body shortcuts. Treat `triceratops-horridus-imagegen-v39-source-candidate.png` and `triceratops-horridus-imagegen-v37-source-candidate.png` as secondary `review_hold` only. Superseded by P6 v41 for the app-first slot.
- 2026-07-02 P6 v40-v42 follow-up: promote `triceratops-horridus-imagegen-v41-source-candidate.png` to the app-first `count-level pass` because it finally improves the low elongated anti-rhino torso and full long-tail silhouette while retaining closed beak, skull-attached frill, three facial horns, and separated non-hoofed toes. Keep `triceratops-p6-v40-v42-review-sheet.png` and `triceratops-p6-v40-v42-crops.png` as the newest close-review gate. Treat v41 as a project-owned smoke-test `train_seed`, not final approval; keep v42 as a low-body `review_hold`, v40 as a close-framed `review_hold`, and v22 as the previous all-feet comparison hold.
- 2026-07-02 P7 v43-v45 follow-up: promote `triceratops-horridus-imagegen-v43-source-candidate.png` to the app-first `count-level pass` because it improves the familiar Triceratops head/frill/toe read at app scale while preserving the long tail, closed beak, exactly three facial horns, skull-attached frill, four dinosaur limbs, and separated non-hoofed toes. Keep `triceratops-p7-v43-v45-review-sheet.png` and `triceratops-p7-v43-v45-crops.png` as the latest close-review gate. Treat v43 as a project-owned smoke-test `train_seed`, not final approval; keep v41 as the previous low-body hold, v44 as a rounded-body hold, and v45 as a mouth/head-risk hold.
- 2026-07-02 P8 v46-v48 follow-up: keep `triceratops-horridus-imagegen-v43-source-candidate.png` first because fresh v46-v48 did not clearly beat it. Keep `triceratops-p8-v46-v48-review-sheet.png` and `triceratops-p8-v46-v48-crops.png` as the latest close-review gate. Treat `triceratops-horridus-imagegen-v46-source-candidate.png` as a near-duplicate `review_hold`, `triceratops-horridus-imagegen-v48-source-candidate.png` as a silhouette `review_hold`, and `triceratops-horridus-imagegen-v47-source-candidate.png` as a `reject_reference` because its leg/foot read is weaker than v43 and it still carries rounded mammal-mass risk.
- 2026-07-03 P9 v49-v51 follow-up: promote `triceratops-horridus-imagegen-v51-source-candidate.png` to the app-first `count-level pass` because it improves cool non-sandy species color while preserving the familiar Triceratops gates. Keep `triceratops-p9-v49-v51-review-sheet.png` and `triceratops-p9-v49-v51-crops.png` as the latest close-review gate. Treat v51 as a project-owned smoke-test `train_seed`, not final approval; treat `triceratops-horridus-imagegen-v49-source-candidate.png` as a dark-speckle `review_hold`, `triceratops-horridus-imagegen-v50-source-candidate.png` as a rust-frill `review_hold`, and v43 as the previous familiar anti-rhino comparison hold because its tan-gray palette is less distinct.

## Velociraptor mongoliensis

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/velociraptor.html
- American Museum of Natural History: https://www.amnh.org/explore/news-blogs/research-posts/velociraptor-feathers
- Science quill-knob paper: https://www.science.org/doi/10.1126/science.1145076

Must read as:

- small, agile dromaeosaur rather than a giant movie raptor
- long stiff balancing tail
- narrow toothed snout, not a bird beak
- feathering on the body and folded forelimbs, with arm feathers held close to the body rather than spread wings
- two main walking toes plus a raised enlarged sickle claw on the second toe of each foot when the feet are visible

Reject if:

- the body becomes naked, scaly, or tyrannosaur-like
- the arms become large flight wings or the animal reads as a modern bird
- the feet lose the sickle-claw cue, gain extra toes, or become generic bird talons
- guide conditioning creates duplicate legs, floating limbs, a second tail, or a long artifact under the tail

Temporary app rule:

- Keep `velociraptor-mongoliensis-imagegen-v63-source-candidate.png` first as the current `count-level pass` because it improves the gallery color problem with dark charcoal/umber speckled plumage, a rust face mask, pale throat/belly, and narrow tail bands while preserving the toothed non-beak head, compact folded arm cue, full stiff tail, two-hind-leg stance, and visible attached raised second-toe cues. Keep `velociraptor-p8-v60-v63-review-sheet.png` and `velociraptor-p8-v60-v63-crops.png` as the newest color-plus-anatomy gate: v63 is the current smoke-test seed, v56 is the previous safety comparison hold, v60/v62 are hook-risk color holds, and v61 is a wing-risk color hold. Keep `velociraptor-p7-v57-v59-review-sheet.png`, `velociraptor-p7-v57-v59-crops.png`, `velociraptor-p6-v51-v56-review-sheet.png`, `velociraptor-p6-v51-v56-crops.png`, `velociraptor-p5-v48-v50-review-sheet.png`, `velociraptor-p5-v48-v50-crops.png`, `velociraptor-small-sickle-crops-v9.png`, `velociraptor-p4-v45-v47-crops.png`, `velociraptor-mongoliensis-foot-topology-guide-v1.png`, `velociraptor-foot-topology-crops-v12.png`, `velociraptor-mongoliensis-identity-bodylock-guide-v1.png`, `velociraptor-identity-bodylock-crops-v13.png`, and older rejection/comparison gates below it. Do not promote direct foot-only i2i outputs that create floating claws, detached crescents, oversized hook-like talons, black talons, or crowded toe counts. Do not promote color retries that solve plumage by creating hook-claw drift, wing-like forelimbs, or bird-head drift. Do not mark the taxon final until exact toe anatomy, tail feather stiffness, skull/eye proportions, and forelimb feather shape pass reference review.

- 2026-07-01 P0 follow-up: keep `velociraptor-p0-wide-review-v35.png` as the current decision sheet for v9/v30/v33/v34/v35. Treat `velociraptor-mongoliensis-imagegen-v35-source-candidate.png` as a review-hold source candidate, not a final pass: it preserves the small feathered dromaeosaur body better than the v33/v34 i2i routes, but the raised second-toe sickle claw is still not final-proof on both feet. Treat v33 low-denoise identity i2i and v34 foot-topology i2i as diagnostic failures because they either weaken the head/forelimb read or lose the sickle-claw cue.
- 2026-07-01 P1 v36-v38 follow-up: keep `velociraptor-p1-v36-v38-review-sheet.png` and `velociraptor-p1-v36-v38-crops.png` as the current prompt-only claw-size gate. Treat `velociraptor-mongoliensis-imagegen-v38-source-candidate.png` as `review_hold` only: it is the best new attempt at a subtler attached near-foot sickle cue while preserving the toothy snout, feathered body, folded forelimbs, and long tail, but it does not prove final two-walking-toes plus raised-second-toe topology. Treat `velociraptor-mongoliensis-imagegen-v36-source-candidate.png` and `velociraptor-mongoliensis-imagegen-v37-source-candidate.png` as reject references because they overcorrect into oversized hook-like claws. Keep `velociraptor-mongoliensis-small-sickle-imagegen-v9.png` first until a crop gate proves both feet and head identity together.
- 2026-07-02 P2 v39-v41 follow-up: keep `velociraptor-p2-v39-v41-review-sheet.png` and `velociraptor-p2-v39-v41-crops.png` as the latest closed-snout plus foot-topology gate. Treat `velociraptor-mongoliensis-imagegen-v39-source-candidate.png` as `review_hold` only because it has the best fresh whole-body balance and reduces bird-beak/open-mouth drift, but both feet still do not prove two grounded walking toes plus one attached raised second-toe sickle claw. Treat `velociraptor-mongoliensis-imagegen-v41-source-candidate.png` as `review_hold` only because the foot area is useful but the near claw can read as an oversized front hook. Treat `velociraptor-mongoliensis-imagegen-v40-source-candidate.png` as `reject_reference` because the open mouth and paired hooks are too dramatic. Keep v9 first until head identity and exact foot topology pass together.
- 2026-07-02 P3 v42-v44 follow-up: keep `velociraptor-p3-v42-v44-review-sheet.png` and `velociraptor-p3-v42-v44-crops.png` as the newest toothed-head/attached-sickle prompt gate. Treat `velociraptor-mongoliensis-imagegen-v43-source-candidate.png` as the best P3 `review_hold` because it balances toothy non-beak head, small feathered body, stiff tail, and attached modest sickle-claw cue, but keep it below promotion because the folded forelimb can read wing-like and the feet still do not prove final two-walking-toes plus raised-second-toe topology. Treat `velociraptor-mongoliensis-imagegen-v44-source-candidate.png` as `review_hold` only because the foot area is useful but the near claw can read as an oversized hook. Treat `velociraptor-mongoliensis-imagegen-v42-source-candidate.png` as `reject_reference` because the raised claws look too talon-like. Keep v9 first until head identity, folded non-wing forelimbs, and exact foot topology pass together.
- 2026-07-02 P4 v45-v47 follow-up: keep `velociraptor-p4-v45-v47-review-sheet.png` and `velociraptor-p4-v45-v47-crops.png` as the newest closed-head/attached-sickle prompt gate. Treat `velociraptor-mongoliensis-imagegen-v47-source-candidate.png` as the best P4 `review_hold` because it keeps a closed toothy non-beak snout, folded forelimbs, feathered dromaeosaur body, stiff tail, and attached near-foot sickle cue, but keep it below promotion because the claw is still slightly large and the far-foot topology does not prove two walking toes plus one attached raised second toe. Treat `velociraptor-mongoliensis-imagegen-v45-source-candidate.png` as a secondary `review_hold` because its head/body read is useful but the forelimb crop can still read wing-like. Treat `velociraptor-mongoliensis-imagegen-v46-source-candidate.png` as `reject_reference` because its open mouth and paired hooks risk monster-like/oversized-talon drift. Keep v9 first until head identity, folded non-wing forelimbs, two hind legs, single tail, and exact foot topology pass together.
- 2026-07-02 P5 v48-v50 follow-up: keep `velociraptor-p5-v48-v50-review-sheet.png` and `velociraptor-p5-v48-v50-crops.png` as the newest subtle-sickle prompt gate. Treat `velociraptor-mongoliensis-imagegen-v50-source-candidate.png` as the best P5 `review_hold` because it has the strongest new head/body/tail balance, but keep it below promotion and outside positive LoRA training because both raised claws remain large, dark, and hook-like. Treat `velociraptor-mongoliensis-imagegen-v48-source-candidate.png` as a black-hook `review_hold` and `velociraptor-mongoliensis-imagegen-v49-source-candidate.png` as a wing/hidden-foot `review_hold`. Keep v9 first until head identity, folded non-wing forelimbs, two hind legs, single tail, and exact foot topology pass together.
- 2026-07-02 P6 v51-v56 follow-up: promote `velociraptor-mongoliensis-imagegen-v56-source-candidate.png` to the app-first `count-level pass` because it gives the best current balance of toothed non-beak head, feathered body, folded forelimbs, full stiff tail, two visible hind legs, and attached raised second-toe cues without the black-hook drift that blocks v50/v52. Keep `velociraptor-p6-v51-v56-review-sheet.png` and `velociraptor-p6-v51-v56-crops.png` as the newest close-review gate. Treat v56 as a project-owned smoke-test `train_seed`, not final approval; keep v9 as the previous first hold, v54/v55 as clearer-claw holds, v53/v51 as subtle-toe holds, and v52/v50 as hook-risk holds.
- 2026-07-02 P7 v57-v59 follow-up: keep `velociraptor-mongoliensis-imagegen-v56-source-candidate.png` first. Add `velociraptor-p7-v57-v59-review-sheet.png` and `velociraptor-p7-v57-v59-crops.png` as the latest close-review gate. Treat `velociraptor-mongoliensis-imagegen-v57-source-candidate.png` as a review hold because it has useful body/foot visibility but curled hook-like raised claws. Treat `velociraptor-mongoliensis-imagegen-v59-source-candidate.png` as a head/silhouette review hold because the feet still overcorrect into hook-risk claws. Treat `velociraptor-mongoliensis-imagegen-v58-source-candidate.png` as a `reject_reference` because the feet become crowded, overbuilt, and unclear in toe count. Future work should preserve v56 and use localized foot i2i or stronger topology control rather than promoting another broad prompt-only output.
- 2026-07-03 P8 v60-v63 follow-up: promote `velociraptor-mongoliensis-imagegen-v63-source-candidate.png` to the app-first `count-level pass` and add `velociraptor-p8-v60-v63-review-sheet.png` plus `velociraptor-p8-v60-v63-crops.png` as the latest color-plus-anatomy gate. Treat v63 as a project-owned smoke-test `train_seed`, not final approval. Treat `velociraptor-mongoliensis-imagegen-v60-source-candidate.png` and `velociraptor-mongoliensis-imagegen-v62-source-candidate.png` as hook-risk color holds because their plumage is useful but the feet overbuild into dramatic claws. Treat `velociraptor-mongoliensis-imagegen-v61-source-candidate.png` as a wing-risk color hold because the rust/barred color is useful but the folded forelimb reads too wing-fan-like. Demote v56 to previous comparison hold because its anatomy remains useful but its plain brown plumage is less distinct than v63. Future work should use foot-local i2i or foot-topology ControlNet over v63 to preserve the new color while reducing hook-claw exaggeration.

## Stegosaurus stenops

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/stegosaurus.html

Must read as:

- heavy quadrupedal stegosaur with a small low head and long tail
- many separate broad bony dorsal plates embedded along the back, not decorative leaves or soft fins
- vertical plates alternating on either side of the spine, with the largest plates over the mid-back and hips
- clear sky/background gaps between individual plates at atlas-card scale
- tail tip with a four-spike thagomizer when the tail end is visible

Reject if:

- the plates read as plant leaves, leaf veins, a comb, a continuous sail, or paper/cardboard overlays
- the plates are separated only by obvious vertical slit edits and read as tall panels rather than broad bony plates
- the plates read as turtle-shell armor segments, pasted rocks, or ankylosaur-like back armor instead of upright bony dorsal plates
- the plate row is reduced to a few huge triangular mountains or many tiny needle spines
- tail-shaft bristles replace the four larger thagomizer spikes
- the body becomes a generic long-necked sauropodomorph, horned ceratopsian, ankylosaur, or two-legged theropod
- the prompt-only image loses the plates entirely, even if the scene is visually polished

Temporary app rule:

- Keep `stegosaurus-stenops-imagegen-v92-source-candidate.png` first as the current `count-level pass` because it improves two user-reviewed weaknesses: dorsal plates now read as separate rough rust-red/pale-bone bony or keratin structures rather than same-color skin, and the thagomizer remains the closest current four-spike upward-V read. Keep `stegosaurus-p10-v97-v99-crops.png` and `stegosaurus-p10-v97-v99-review-sheet.png` directly below it as the latest close-review gate: P10 clarified that the thagomizer must rise upward relative to the ground/horizon, not merely point away from the tail shaft, and the two lower spikes must not lie sideways along the tail. Treat v97-v99 as reject references only because v97/v98 preserve useful plate material but keep lower tail-parallel or horizontal-point risks, while v99 overcorrects into a five-spike/radial-cluster read. Keep `stegosaurus-p9-v93-v96-crops.png`, `stegosaurus-p9-v93-v96-review-sheet.png`, `stegosaurus-p8-v90-v92-crops.png`, `stegosaurus-p8-v90-v92-review-sheet.png`, previous v86, `stegosaurus-p7-v87-v89-crops.png`, `stegosaurus-p7-v87-v89-review-sheet.png`, `stegosaurus-p6-v84-v86-crops.png`, `stegosaurus-p6-v84-v86-review-sheet.png`, the previous `stegosaurus-stenops-alternatingplate-fourspike-imagegen-v6.png`, `stegosaurus-alternatingplate-fourspike-crops-v6.png`, `stegosaurus-stenops-plate-topology-guide-v1.png`, `stegosaurus-plate-topology-crops-v12.png`, and `stegosaurus-review-options-v46.png` as structure-control and comparison gates before any future naturalized candidate is promoted. Keep older comparison gates for tail overcount, undercount, leaf-like plates, and connected sails. Do not mark the taxon final until exact alternating two-row plate placement, rough non-skin plate material, ground-relative upward V four-spike thagomizer anatomy, and toe detail are verified against references.

- 2026-07-01 v69 follow-up: keep `stegosaurus-plate-row-i2i-v69-review-sheet.png` and `stegosaurus-plate-row-i2i-v69-crops.png` as the current custom-mask plate-row evidence. Treat `stegosaurus-stenops-plate-row-i2i-v69.png` as review_hold only: it preserves the v6 body, feet, tail, and four-spike thagomizer and slightly hardens plate edges, but it does not prove stronger alternating two-row plate topology than v6. Add it to the stegosaur LoRA manifest as review_hold, not train_seed.
- 2026-07-01 P1 v70/v71 follow-up: keep `stegosaurus-stenops-imagegen-v71-source-candidate.png`, `stegosaurus-stenops-imagegen-v70-source-candidate.png`, `stegosaurus-p1-v70-v71-review-sheet.png`, and `stegosaurus-p1-v70-v71-crops.png` as review_hold evidence only. V71 gives the best new prompt-only staggered plate-overlap cue, but its thagomizer can collapse to an ambiguous count at crop scale. V70 gives broader plate surfaces and a more readable thagomizer cue, but plate bases still read mostly as a single row. Keep v6 first and do not train from either v70 or v71 until one candidate proves both alternating two-row plate topology and exactly four tail spikes together.
- 2026-07-01 P2 v72-v74 follow-up: keep `stegosaurus-p2-v72-v74-review-sheet.png` and `stegosaurus-p2-v72-v74-crops.png` as the current broad-plate identity gate. Treat `stegosaurus-stenops-imagegen-v72-source-candidate.png` as a `review_hold` plate-target candidate: it has the strongest new rough, separated, broad bony plate read, but the tail tip can overcount the thagomizer and therefore cannot replace v6. Treat `stegosaurus-stenops-imagegen-v73-source-candidate.png` as `review_hold` only because the plate gaps are useful but the tail reads closer to three spikes. Treat `stegosaurus-stenops-imagegen-v74-source-candidate.png` as a reject reference because the tail weapon is too staged and the leg/plate read is weaker for a representative. Keep v6 first until broad separated dorsal plates and exactly four tail spikes pass together.
- 2026-07-01 P3 v75-v77 follow-up: keep `stegosaurus-p3-v75-v77-review-sheet.png` and `stegosaurus-p3-v75-v77-crops.png` as the latest broad-plate plus thagomizer crop gate. Treat `stegosaurus-stenops-imagegen-v77-source-candidate.png` as `review_hold` only because it has the strongest fresh broad separated plate mass and a good low Stegosaurus body, but the tail still overcounts the thagomizer. Treat `stegosaurus-stenops-imagegen-v75-source-candidate.png` and `stegosaurus-stenops-imagegen-v76-source-candidate.png` as `reject_reference` because they reinforce tail-spike overcount; v76 also risks leaf-vein plate surfaces. Keep v6 first until broad separated dorsal plates and exactly four tail spikes pass together.
- 2026-07-02 P4 v78-v80 follow-up: keep `stegosaurus-p4-v78-v80-review-sheet.png` and `stegosaurus-p4-v78-v80-crops.png` as the latest broad-plate plus thagomizer crop gate. Treat `stegosaurus-stenops-imagegen-v79-source-candidate.png` as `review_hold` only because it is the best new compromise between broad separated plates and a near-four tail read, but the lower thagomizer overlap can still read as an extra spike. Treat `stegosaurus-stenops-imagegen-v78-source-candidate.png` and `stegosaurus-stenops-imagegen-v80-source-candidate.png` as `reject_reference`: v78 is a strong plate target but clearly overcounts the thagomizer, and v80 has a useful silhouette but can read as an extra lower tail spike. Keep v6 first until broad separated dorsal plates and exactly four tail spikes pass together.
- 2026-07-02 P5 v81-v83 follow-up: keep `stegosaurus-p5-v81-v83-review-sheet.png` and `stegosaurus-p5-v81-v83-crops.png` as the latest tail-count-locked crop gate. Treat `stegosaurus-stenops-imagegen-v82-source-candidate.png` as the best fresh `review_hold`: it has broad separated plates and the clearest near-four thagomizer read from the new prompt, but the lower right tail-spike geometry can still be read as overlapping or duplicated. Treat `stegosaurus-stenops-imagegen-v83-source-candidate.png` as `review_hold` only because it preserves a useful side body and plate read but still has lower-spike overlap risk. Treat `stegosaurus-stenops-imagegen-v81-source-candidate.png` as `reject_reference` because it clearly overcounts the thagomizer. Keep v6 first until broad separated dorsal plates and exactly four tail spikes pass together.
- 2026-07-02 P6 v84-v86 follow-up: promote `stegosaurus-stenops-imagegen-v86-source-candidate.png` to the app `count-level pass` and keep `stegosaurus-p6-v84-v86-review-sheet.png` plus `stegosaurus-p6-v84-v86-crops.png` as the newest broad-plate/four-spike gate. V86 has the best current combined read of broad separated plates, low quadrupedal body, four planted feet, and exactly four separated thagomizer spikes. Treat `stegosaurus-stenops-imagegen-v84-source-candidate.png` as `review_hold` because the four-spike tail is useful but mid-back plates are oversized. Treat `stegosaurus-stenops-imagegen-v85-source-candidate.png` as `reject_reference` because the tail can read as only three countable spikes. Keep v6 as a previous comparison seed below v86.
- 2026-07-02 P7 v87-v89 follow-up: keep `stegosaurus-stenops-imagegen-v86-source-candidate.png` first and add `stegosaurus-p7-v87-v89-review-sheet.png` plus `stegosaurus-p7-v87-v89-crops.png` as the latest close-review gate. Treat `stegosaurus-stenops-imagegen-v88-source-candidate.png` as `review_hold` because the tail is near-four but the plates become rounder and more leaf/fan-like. Treat `stegosaurus-stenops-imagegen-v89-source-candidate.png` as `review_hold` because the body and tail are stable but plate topology does not beat v86. Treat `stegosaurus-stenops-imagegen-v87-source-candidate.png` as `reject_reference` because the tail can read as five thagomizer spikes. Future work should preserve v86's tail and use localized plate-row i2i or Stegosauridae-specific LoRA/control work for the alternating plate bases.
- 2026-07-03 P8 v90-v92 follow-up: promote `stegosaurus-stenops-imagegen-v92-source-candidate.png` to the app-first `count-level pass` and add `stegosaurus-p8-v90-v92-review-sheet.png` plus `stegosaurus-p8-v90-v92-crops.png` as the latest close-review gate. Treat v92 as the current project-owned smoke-test `train_seed`, not final approval. Treat `stegosaurus-stenops-imagegen-v90-source-candidate.png` as `review_hold` because its plate material is strong but one thagomizer spike is too lateral for the upward V gate. Treat `stegosaurus-stenops-imagegen-v91-source-candidate.png` as `review_hold` because the plate material and upward direction are useful but the tail can read as only three visible spikes. Demote v86 to previous comparison hold because its plates are too close to skin color and can read leather-like under the new material gate.
- 2026-07-03 P9 v93-v96 follow-up: keep `stegosaurus-stenops-imagegen-v92-source-candidate.png` first, but add `stegosaurus-p9-v93-v96-review-sheet.png` and `stegosaurus-p9-v93-v96-crops.png` as the latest strict tail-angle gate. Treat `stegosaurus-stenops-imagegen-v93-source-candidate.png`, `stegosaurus-stenops-imagegen-v94-source-candidate.png`, `stegosaurus-stenops-imagegen-v95-source-candidate.png`, and `stegosaurus-stenops-imagegen-v96-source-candidate.png` as `reject_reference` only: v93 keeps a ground-parallel lower tail extension, v94 undercounts the thagomizer, v95 reads as upward prongs plus a horizontal tail point, and v96 reads as three spikes plus a small side nub. The next useful route is tail-local ControlNet/inpaint over v92 with a rounded tail base and exactly four spikes all rising above the ground/horizon.
- 2026-07-03 P10 v97-v99 follow-up: keep `stegosaurus-stenops-imagegen-v92-source-candidate.png` first, but add `stegosaurus-p10-v97-v99-review-sheet.png` and `stegosaurus-p10-v97-v99-crops.png` as the latest strict ground-relative upward-V gate. Treat `stegosaurus-stenops-imagegen-v97-source-candidate.png`, `stegosaurus-stenops-imagegen-v98-source-candidate.png`, and `stegosaurus-stenops-imagegen-v99-source-candidate.png` as `reject_reference` only: v97/v98 still leave lower thagomizer points too close to the ground or tail shaft, while v99 improves the upward direction but can read as five/radial spikes. The next useful route is tail-local ControlNet/inpaint over v92 with a rounded tail base, exactly four countable spikes, and both lower spikes angled upward relative to the ground/horizon.

## Plateosaurus engelhardti

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/plateosaurus.html
- Palaeontologia Electronica manus study: https://palaeo-electronica.org/content/2014/692-plateo-hand

Must read as:

- early sauropodomorph herbivore, not a giant true sauropod or carnivorous theropod
- hind-limb-dominant bipedal or near-bipedal stance with two large weight-bearing hind legs
- moderately long low-forward neck, small herbivore head, closed or toothless-looking mouth
- short forelimbs held off the ground near the chest
- grasping hands with a large thumb-claw cue, but not huge predator talons

Reject if:

- forelimbs become weight-bearing front legs or make the animal read as a four-legged sauropod
- narrow forelimb edits create an extra-leg or six-leg read
- the head becomes toothy, predator-like, or too large for an early sauropodomorph
- hands are hidden so completely that the thumb-claw cue cannot be reviewed
- the body becomes rear-view, cropped, or too obscured to verify tail and hind-limb count

Temporary app rule:

- Keep `plateosaurus-engelhardti-imagegen-v25-source-candidate.png` first as the current `count-level pass` because it improves gallery-wide color separation with charcoal green-gray skin, cream speckles, and darker tail bands while preserving the low herbivore head, long forward neck, deep torso, full tail, exactly two large grounded hind legs, and lifted forelimbs. Keep `plateosaurus-p4-v22-v25-review-sheet.png` and `plateosaurus-p4-v22-v25-crops.png` directly below it as the latest close-review gates. Keep `plateosaurus-engelhardti-imagegen-v20-source-candidate.png` as the previous anatomy-first hold, `plateosaurus-engelhardti-imagegen-v23-source-candidate.png` as a red-clay color hold with hook-risk fingers, `plateosaurus-engelhardti-imagegen-v22-source-candidate.png` as an olive/cream color hold with long-hand risk, and `plateosaurus-engelhardti-imagegen-v24-source-candidate.png` as a hook-hand/leg-overlap reject. Keep `plateosaurus-p3-v19-v21-review-sheet.png`, `plateosaurus-p3-v19-v21-crops.png`, `plateosaurus-engelhardti-singleforelimb-smallhand-imagegen-v3.png`, `plateosaurus-engelhardti-imagegen-v19-source-candidate.png`, `plateosaurus-engelhardti-imagegen-v21-source-candidate.png`, `plateosaurus-engelhardti-bodylock-guide-v1.png`, `plateosaurus-bodylock-crops-v4.png`, and `plateosaurus-review-options-v12.png` as the structure-control route for preventing forelimb-ground-contact or six-leg drift. Keep older hand/thumb, tripod, and six-leg rejection gates as comparisons. Do not promote a Plateosaurus edit if it weakens the two large hind legs, ground contact, erases v25's dark speckled color, or creates any six-leg read. Do not mark the taxon final until exact two lifted forelimbs, five-finger hand topology, and the larger thumb-claw cue can be checked against references.
- 2026-07-01 P1 v15 follow-up: add `plateosaurus-engelhardti-imagegen-v15-source-candidate.png`, `plateosaurus-p1-v15-review-sheet.png`, and `plateosaurus-p1-v15-crops.png` as review_hold evidence only. V15 keeps a usable low herbivore head, long neck, full tail, and exactly two grounded hind legs, but the lifted hand/thumb-claw crop is still too soft and the far forelimb is not decisive. Keep v3 first and do not use v15 as a positive LoRA train_seed until a later crop gate proves better five-finger/thumb-claw anatomy without forelimb ground contact.
- 2026-07-02 P2 v16-v18 hand-visibility follow-up: add `plateosaurus-engelhardti-imagegen-v16-source-candidate.png`, `plateosaurus-engelhardti-imagegen-v17-source-candidate.png`, `plateosaurus-engelhardti-imagegen-v18-source-candidate.png`, `plateosaurus-p2-v16-v18-review-sheet.png`, and `plateosaurus-p2-v16-v18-crops.png`. V16 is the best P2 review_hold because it improves visible lifted hands and thumb-claw cues while preserving the two-grounded-hind-leg gate, but the claws may be overlong and hook-like. V17 is a reject_reference for human-like/over-digited hand overbuild. V18 is a silhouette review_hold only because its hand detail is soft and the neck trends too long. Superseded by P3 v20 for the app-first slot.
- 2026-07-02 P3 v19-v21 two-lifted-hands follow-up: promote `plateosaurus-engelhardti-imagegen-v20-source-candidate.png` to the app-first `count-level pass` and current smoke-test `train_seed` because it shows both short lifted forelimbs while keeping exactly two grounded hind legs and avoiding six-leg drift. Keep `plateosaurus-p3-v19-v21-review-sheet.png` and `plateosaurus-p3-v19-v21-crops.png` as the latest close-review gates. Treat v3 as the previous app-first hold, v19 as a hand-detail hold with long/hook-like finger risk, and v21 as a silhouette hold with weaker far-forelimb detail. Do not mark final until exact five-finger hand topology and the larger thumb-claw cue pass close reference review.
- 2026-07-03 P4 v22-v25 color-pattern follow-up: promote `plateosaurus-engelhardti-imagegen-v25-source-candidate.png` to the app-first `count-level pass` and current smoke-test `train_seed` because it adds dark charcoal-green speckling and tail bands while preserving the no-six-leg body gate. Keep `plateosaurus-p4-v22-v25-review-sheet.png` and `plateosaurus-p4-v22-v25-crops.png` as the latest close-review gates. Treat v20 as the previous anatomy-first hold, v23 as a red-clay color hold with hook-risk fingers, v22 as an olive/cream color hold with long-hand risk, and v24 as a hook-hand/leg-overlap reject. Future hand-local i2i must preserve v25's dark speckled color while shortening fingers and clarifying the larger thumb-claw cue.

## Ankylosaurus magniventris

Reference anchors:

- PBDB taxon record and project-owned structure guides
- Use ankylosaurid skeletal/reconstruction references before promotion

Must read as:

- broad, low, heavily armored ankylosaurid quadruped
- compact low skull and short neck integrated into a squat body
- bony osteoderms or armor texture across the back and flanks
- four sturdy limbs under the body, not a sprawled lizard posture
- a single tail with an attached bony club at the tip

Reject if:

- the body reads as a crocodile, monitor lizard, pangolin, turtle, or generic low reptile
- the tail club is missing, detached, too soft, or reads as a leaf/paddle
- tall Stegosaurus-like dorsal plates or large side spikes replace low osteoderms
- the animal becomes bipedal, long-necked, or theropod-like
- the image is too diagram-like to serve as natural representative art

Temporary app rule:

- Keep `ankylosaurus-magniventris-imagegen-v40-source-candidate.png` first as the current app `count-level pass`, but do not treat it as final approval. It improves over v38 by solving two app-scale issues together: the older candidate's sandy-brown palette blended into the rest of the gallery, and the head still read too smooth/lizard-like. V40 adds a red-ochre/burnt-umber natural pattern, compact armored skull, cheek horns, rear skull-corner horn cues, low rounded armor rows, four visible feet, and one attached oval tail club. Keep `ankylosaurus-p8-v39-v41-review-sheet.png` and `ankylosaurus-p8-v39-v41-crops.png` directly below as the current close-review gates; keep v38 as the previous compact-body hold, v39 as a dark-olive skull-armor hold, v41 as a blue-gray skull-horn hold with possible horn-size overemphasis, v34/v37/v36/v33/v35/v32 as older comparison holds, v18 as the older all-feet weak-LoRA comparison, and `ankylosaurus-magniventris-armor-tailclub-guide-v1.png`, `ankylosaurus-armor-tailclub-crops-v6.png`, and `ankylosaurus-review-options-v11.png` as the structure-control route. Do not treat tail-club presence alone as a pass; reject any candidate that reads as crocodile, monitor lizard, pangolin, turtle, armadillo, generic low reptile, fantasy spike creature, or Stegosaurus-like plate-backed animal. Do not mark the taxon final until skull proportions, skull horn size, toe details, compact tail proportions, tail-club attachment, armor-row layout, and natural-but-distinct color pattern are checked against references.
- 2026-07-01 P2 v21-v23 follow-up: keep `ankylosaurus-p2-v21-v23-review-sheet.png` and `ankylosaurus-p2-v21-v23-crops.png` as the current armor/tail-club prompt gate. Treat `ankylosaurus-magniventris-imagegen-v22-source-candidate.png` as the best new `review_hold` source candidate because it balances broad skull, low armor rows, four planted feet, and one attached oval club, but it still carries mild long-body lizard risk. Treat `ankylosaurus-magniventris-imagegen-v23-source-candidate.png` as `review_hold` only because it has the lowest broad armor body and clean club but can read monitor-lizard-like in body/tail length. Treat `ankylosaurus-magniventris-imagegen-v21-source-candidate.png` as `review_hold` only because its armor and club are useful but skull-side projections can read as horns. Keep v18 first until compact ankylosaurid proportions, broad skull, low osteoderms, four sturdy feet, and one attached club pass together.
- 2026-07-02 P3 v24-v26 follow-up: add `ankylosaurus-p3-v24-v26-review-sheet.png` and `ankylosaurus-p3-v24-v26-crops.png` as the newest compact-skull/armor/tail-club prompt gate. Treat `ankylosaurus-magniventris-imagegen-v25-source-candidate.png` as the best P3 `review_hold` because it improves the combined compact-head, low rounded osteoderm, four-grounded-feet, and attached single-club read, but keep it below final approval because skull length and rear-leg separation still need close review. Treat `ankylosaurus-magniventris-imagegen-v24-source-candidate.png` as a clean tail-club hold with long-snout/long-body lizard risk. Treat `ankylosaurus-magniventris-imagegen-v26-source-candidate.png` as a low-armor/blunt-head hold with rear-foot ambiguity. Keep v18 first and keep all P3 outputs outside positive LoRA training until non-lizard proportions, broad blunt skull, rounded low armor, four sturdy feet, and one attached tail club pass together.
- 2026-07-02 P4 v27-v29 follow-up: add `ankylosaurus-p4-v27-v29-review-sheet.png` and `ankylosaurus-p4-v27-v29-crops.png` as the latest compact armor/tail-club prompt gate. Treat `ankylosaurus-magniventris-imagegen-v28-source-candidate.png` as the best P4 `review_hold` because it improves the tank-like low body, dense rounded osteoderms, grounded feet, and one attached oval club, but keep it below final approval because head side knobs and long-tail tendency still need close review. Treat `ankylosaurus-magniventris-imagegen-v27-source-candidate.png` as secondary armor/club `review_hold` only. Treat `ankylosaurus-magniventris-imagegen-v29-source-candidate.png` as `reject_reference` because the body and tail become too long and drift toward generic armored lizard proportions. Keep v18 first until compact ankylosaurid proportions, broad blunt skull, rounded low armor, four sturdy feet, and one attached tail club pass together.
- 2026-07-02 P5 v30-v32 follow-up: promote `ankylosaurus-magniventris-imagegen-v32-source-candidate.png` to the app-first `count-level pass` because it gives the strongest immediate Ankylosaurus read so far: lower tank-like body, dense rounded osteoderms, four sturdy planted feet, and one attached oval club. Keep `ankylosaurus-p5-v30-v32-review-sheet.png` and `ankylosaurus-p5-v30-v32-crops.png` directly below it. Treat v32 as `review_hold` only for LoRA because the cheek knob can still read horn-like and the tail is still longer than ideal. Treat v31 and v30 as secondary review holds only. Do not mark final until broad blunt skull, compact body, low rounded armor, four sturdy feet, and one attached club pass together against references.
- 2026-07-02 P6 v33-v35 follow-up: promote `ankylosaurus-magniventris-imagegen-v34-source-candidate.png` to the app-first `count-level pass` because it improves the blunt-skull, compact armored body, four planted feet, and attached club balance over v32. Keep `ankylosaurus-p6-v33-v35-review-sheet.png` and `ankylosaurus-p6-v33-v35-crops.png` as the newest close-review gate. Treat v34 as the current project-owned smoke-test `train_seed`, not final approval; treat v33 and v35 as `review_hold` comparisons, and demote v32 to previous `review_hold` because of horn-like cheek and long-tail risk. Do not mark final until broad blunt skull, compact body, low rounded armor, four sturdy feet, and one attached club pass together against references.
- 2026-07-02 P7 v36-v38 follow-up: promote `ankylosaurus-magniventris-imagegen-v38-source-candidate.png` to the app-first `count-level pass` because it improves the compact tank-like body over v34 while preserving the broad blunt skull, low rounded armor rows, four visible feet, and one attached oval club. Keep `ankylosaurus-p7-v36-v38-review-sheet.png` and `ankylosaurus-p7-v36-v38-crops.png` as the newest close-review gate. Treat v38 as the current project-owned smoke-test `train_seed`, not final approval; treat v34 as the previous app-first hold, v37 as a compact-body hold, and v36 as a longer-tail hold. Do not mark final until broad blunt skull, compact body, low rounded armor, four sturdy feet, tail-club attachment, and exact toes pass together against references.
- 2026-07-02 P8 v39-v41 follow-up: promote `ankylosaurus-magniventris-imagegen-v40-source-candidate.png` to the app-first `count-level pass` because it improves color/pattern variety and the armored-head identity over v38. Keep `ankylosaurus-p8-v39-v41-review-sheet.png` and `ankylosaurus-p8-v39-v41-crops.png` as the newest close-review gate. Treat v40 as the current project-owned smoke-test `train_seed`, not final approval; treat v38 as the previous compact-body hold, v39 as a dark-olive skull-armor hold, and v41 as a blue-gray skull-horn hold with possible horn-size/head-shape overemphasis. Do not mark final until broad blunt armored skull, compact body, low rounded armor, four sturdy feet, tail-club attachment, exact toes, and natural-but-distinct color pattern pass together against references.

## Herrerasaurus ischigualastensis

Reference anchors:

- UCMP Berkeley: https://ucmp.berkeley.edu/diapsids/herrerasaurus.html
- Britannica: https://www.britannica.com/animal/Herrerasaurus-ischigualastensis
- Sereno and Novas skeletal reconstruction: https://www.science.org/doi/10.1126/science.258.5085.1137

Must read as:

- lightly built early saurischian predator in a bipedal stance
- long balancing tail and horizontal body
- long, narrow carnivorous skull rather than a deep tyrannosaur skull
- grasping forelimbs visibly longer than tiny Tyrannosaurus-style arms, with clawed hands below the chest
- hand read should emphasize three main clawed digits with any fourth/fifth digits tiny and vestigial; reject both two-finger T. rex hands and five equally long human-like fingers
- two large hind legs only; forelimbs must not be mistaken for extra weight-bearing legs

Reject if:

- the forelimbs shrink into tiny tucked two-finger tyrannosaur arms
- the hands show many equally long dangling fingers, human-like hands, or oversized hook claws
- the mouth is a wide roaring gape with oversized exposed teeth instead of a calmer narrow early-theropod head
- the neck becomes a long swan-like sauropodomorph neck
- the animal gains extra legs, duplicate arms, a second tail, or a dangling tail-like artifact
- the body becomes bulky, quadrupedal, or sauropodomorph-like

Temporary app rule:

- Keep `herrerasaurus-ischigualastensis-compacthands-imagegen-v2.png` first as the current `count-level pass` because it improves the closed-head, dry side-profile, full tail, two-hind-leg stance, and compact folded-hand read over the previous strict compact candidate. Keep `herrerasaurus-compacthands-crops-v2.png` directly below it as the close-review gate, then keep `herrerasaurus-ischigualastensis-bodylock-guide-v1.png`, `herrerasaurus-bodylock-crops-v3.png`, and `herrerasaurus-review-options-v8.png` as the next structure-control route for preventing T. rex arm shrinkage, long dangling hook-hand drift, or bulky large-theropod drift while locking the closed narrow head, compact folded hands, two hind legs, dry feet, and full tail. Keep `herrerasaurus-ischigualastensis-balancedhands-imagegen-v2.png`, `herrerasaurus-ischigualastensis-strict-imagegen-alt-v1.png`, `herrerasaurus-ischigualastensis-strict-imagegen-v1.png`, `herrerasaurus-ischigualastensis-closedjaw-headblend-v1.png`, and `herrerasaurus-ischigualastensis-longarms-ipcontrol-v1.png` as comparison gates. Do not treat the new first image as final approval until the three-main-clawed-digit hand read, tiny vestigial outer digits, and toe anatomy are checked against references.

- 2026-07-01 P1 follow-up: keep `herrerasaurus-p1-v4-review-sheet.png` and `herrerasaurus-p1-v4-crops.png` as the current v2/v4 decision sheets. Treat `herrerasaurus-ischigualastensis-imagegen-v4-source-candidate.png` as `review_hold` only: it improves the project-owned Triassic floodplain scene and keeps the narrow closed head, full body, long tail, and two hind legs, but the visible hand can read as too many equal long fingers. Keep v2 first until a candidate proves the compact folded forelimbs, three-main-digit hand target with tiny vestigial outer digits, dry three-toed feet, and non-bulky early-saurischian body together.
- 2026-07-02 P2 v5-v7 follow-up: keep `herrerasaurus-p2-v5-v7-review-sheet.png` and `herrerasaurus-p2-v5-v7-crops.png` as the newest compact-hand prompt gate. Treat `herrerasaurus-ischigualastensis-imagegen-v6-source-candidate.png` as the best P2 `review_hold` because it preserves compact folded forelimbs, a narrow closed head, full tail, and exactly two grounded hind legs, but do not promote it because the exact three-main-digit topology remains soft. Treat `herrerasaurus-ischigualastensis-imagegen-v5-source-candidate.png` and `herrerasaurus-ischigualastensis-imagegen-v7-source-candidate.png` as `reject_reference` because their hands drift into long dangling hooks or too many/equal long fingers. Keep v2 first.

## Coelophysis bauri

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/coelophysis.html
- American Museum of Natural History: https://www.amnh.org/exhibitions/permanent/saurischian-dinosaurs/coelophysis
- Britannica: https://www.britannica.com/animal/Coelophysis

Must read as:

- small, lightly built early theropod in a bipedal stance
- long slender neck, narrow head, long balancing tail, and long hind legs
- small grasping forelimbs held below the chest
- feet on dry ground for the MVP atlas scene, not perched on a branch or log

Reject if:

- the body becomes bulky, quadrupedal, bird-beaked, or sauropodomorph-like
- the scene reads as perched on a log, branch, or wet reed bank rather than walking on ground
- tail, head, feet, or forelimbs are cropped or hidden enough to block limb-count review
- extra limbs, duplicate tail, or background shadows read as anatomy

Temporary app rule:

- Keep `coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png` first because it improves the gracile small-theropod body, long S-curved neck, narrow head, open dry-ground scene, full tail, two-hind-leg stance, and small tucked forelimb-hand read over the previous compact-hand candidate. Keep `coelophysis-slenderneck-smallhands-crops-v3.png` directly below it as the close-review gate, then keep `coelophysis-bauri-bodylock-guide-v1.png`, `coelophysis-bodylock-crops-v4.png`, and `coelophysis-review-options-v8.png` as the next structure-control route for preventing forelimbs from reading as extra legs while locking the S-neck, slim body, full tail, two hind legs, and dry three-toed feet. Keep `coelophysis-bauri-slenderneck-openfeet-imagegen-v3.png`, `coelophysis-bauri-compacthands-imagegen-v2.png`, `coelophysis-bauri-openlimbs-imagegen-v2.png`, `coelophysis-bauri-strict-imagegen-v1.png`, `coelophysis-bauri-dryground-bgreplace-v1.png`, `coelophysis-bauri.png`, and `coelophysis-bauri-forelimb-reference-guide-v1.png` as comparison gates until a small-theropod LoRA or i2i route can reproduce the same full-body read with cleaner finger and toe anatomy.

- 2026-07-01 P1 follow-up: keep `coelophysis-p1-v5-review-sheet.png` and `coelophysis-p1-v5-crops.png` as the current v3/v5 decision sheets. Treat `coelophysis-bauri-imagegen-v5-source-candidate.png` as `review_hold` only: it makes the small folded forelimbs more visible while keeping them off the ground and preserves two hind legs, dry feet, S-curved neck, and full tail, but the head and torso read slightly heavier than v3. Keep v3 first until a candidate proves the visible small hands, gracile body, exact foot anatomy, full tail, and no-extra-leg read together.
- 2026-07-02 P2 v6-v8 follow-up: keep `coelophysis-p2-v6-v8-review-sheet.png` and `coelophysis-p2-v6-v8-crops.png` as the newest no-extra-leg prompt gate. Treat `coelophysis-bauri-imagegen-v6-source-candidate.png` as the best new `review_hold` for gracile silhouette and visible tucked forelimbs, but keep it below v3 because hand digits can still lengthen. Treat `coelophysis-bauri-imagegen-v8-source-candidate.png` as a secondary `review_hold` because it keeps a clean two-leg/no-extra-leg read but hand/toe detail remains soft. Treat `coelophysis-bauri-imagegen-v7-source-candidate.png` as `reject_reference` because the body/head read heavier and forelimb hands become longer and more hook-like. Keep v3 first.

## Allosaurus fragilis

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/allosaurus.html
- Cleveland-Lloyd Dinosaur Quarry: https://www.blm.gov/visit/cleveland-lloyd-dinosaur-quarry

Must read as:

- large Jurassic theropod predator, not a Tyrannosaurus rex
- long balancing tail and horizontal side-profile body
- low elongated skull with modest brow ridges or lacrimal hornlets, not a massive deep tyrannosaur skull
- longer three-fingered forelimbs held off the ground near the chest
- two powerful hind legs with visible three-toed theropod feet on open ground

Reject if:

- the skull becomes deep, blocky, and T. rex-like, or the brow ridges become fantasy horns
- the forelimbs shrink into tiny two-finger tyrannosaur arms
- hands, feet, or tail are hidden enough to block count-level review
- forelimbs touch the ground or read as extra weight-bearing legs
- the animal gains extra legs, duplicate arms, duplicate tails, feathers, wings, or a bird beak

Temporary app rule:

- Keep `allosaurus-fragilis-smoothbrow-threefinger-imagegen-v4.png` first because it lowers the allosaur brow silhouette while preserving the side profile, medium non-weight-bearing forelimbs, open dry feet, two-hind-leg read, and full tail. Keep `allosaurus-smoothbrow-threefinger-crops-v4.png` directly below it as the close-review gate, then keep `allosaurus-fragilis-threefinger-bodylock-guide-v1.png`, `allosaurus-threefinger-bodylock-crops-v10.png`, and `allosaurus-review-options-v10.png` as the next structure-control route for preventing T. rex, two-finger, or horned-brow drift. Keep `allosaurus-fragilis-lowhorn-threefinger-comparison-v4.png`, `allosaurus-fragilis-ridgehand-comparison-v4.png`, `allosaurus-fragilis-lowbrow-threefinger-imagegen-v3.png`, `allosaurus-lowbrow-threefinger-crops-v3.png`, `allosaurus-fragilis-reviewable-threefinger-imagegen-v3.png`, `allosaurus-fragilis-mediumarm-threefinger-imagegen-v3.png`, `allosaurus-fragilis-compacthands-imagegen-v2.png`, and older strict/open-feet/hand-cue candidates as comparison gates. Do not treat the new first image as final approval until exact three-finger hand anatomy, claw length, and toe anatomy are checked against references.

- 2026-07-01 P1 follow-up: keep `allosaurus-p1-v12-v13-review-sheet.png` and `allosaurus-p1-v12-v13-crops.png` as the current source-candidate decision sheets. Treat `allosaurus-fragilis-imagegen-v13-source-candidate.png` as `review_hold` only: it improves the smooth-brow full-body read over the v12 retry, but the visible hand can read as four fingers. Treat `allosaurus-fragilis-imagegen-v12-source-candidate.png` as `reject_reference` because the brow bumps can read as horns and the hand digit count remains ambiguous. Keep v4 first until a candidate proves the lower Allosaurus skull, medium non-weight-bearing arms, exactly three visible fingers, dry three-toed feet, and full tail together.
- 2026-07-02 P2 v14-v16 follow-up: keep `allosaurus-p2-v14-v16-review-sheet.png` and `allosaurus-p2-v14-v16-crops.png` as the newest three-finger/brow prompt gate. Treat `allosaurus-fragilis-imagegen-v15-source-candidate.png` as the best P2 `review_hold` because it has the clearest fresh three-finger cue and lower brow than v14/v16, but do not promote it because the skull mass trends heavy/Tyrannosaurus-like. Treat `allosaurus-fragilis-imagegen-v14-source-candidate.png` and `allosaurus-fragilis-imagegen-v16-source-candidate.png` as `reject_reference` because brow/head detail drifts toward horn-like ornament or unsafe digit ambiguity. Keep v4 first.

## Apatosaurus ajax

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/apatosaurus.html
- Carnegie Museum of Natural History: https://carnegiemnh.org/dippy-vs-apatosaurus/

Must read as:

- massive quadrupedal diplodocid sauropod, not a biped or theropod
- low forward-reaching neck near shoulder height, with a small herbivore head
- very long horizontal tail held off the ground and fully in frame
- deep heavy torso with robust hips and exactly four visible pillar-like legs
- feet and ground contact visible for limb-count review

Reject if:

- the animal becomes high-shouldered or giraffe-necked like Brachiosaurus
- legs, feet, head, or tail are hidden by hills, water, foreground plants, fog, or crop
- the body becomes a flat guide/card silhouette instead of natural paleoart
- extra legs, missing legs, duplicate tail, dragged tail, armor, spikes, hooves, or predator teeth appear

Temporary app rule:

- Keep `apatosaurus-ajax-smallhead-imagegen-v2.png` first because it improves the small blunt head, low forward neck, full horizontal tail, four-visible-leg read, and reviewable open feet over the previous low-neck imagegen candidate. Keep `apatosaurus-smallhead-crops-v2.png` directly below it as the close-review gate, then keep `apatosaurus-ajax-lowneck-bodylock-guide-v1.png`, `apatosaurus-lowneck-bodylock-crops-v3.png`, and `apatosaurus-review-options-v6.png` as the next structure-control route for preventing Brachiosaurus/high-neck drift. Keep `apatosaurus-ajax-openfeet-imagegen-v2.png`, `apatosaurus-ajax-lowneck-imagegen-v1.png`, `apatosaurus-ajax-edge-volume-v1.png`, and the low-neck i2i/floodplain candidates as comparison gates until a stronger sauropod LoRA or i2i route can reproduce the same low-neck open-feet anatomy with tighter skull and foot detail.

- 2026-07-01 P1 follow-up: promote `apatosaurus-ajax-imagegen-v3-source-candidate.png` to the current count-level pass and keep `apatosaurus-p1-v3-v5-review-sheet.png` plus `apatosaurus-p1-v3-v5-crops.png` as the current v2/v3/v4/v5 decision sheets. V3 improves the low-neck Apatosaurus read with an almost horizontal forward neck, low non-Brachiosaurus shoulder profile, very long fully framed horizontal tail, and exactly four visible pillar legs. Keep v2, v4, and v5 as `review_hold`: v2 remains useful for skull/foot comparison, v4 is close but head/neck read heavier, and v5 has more tail-tip bend plus rear-foot overlap risk. Do not mark final until exact foot shape and species-level skull proportions pass close reference review.

## Brachiosaurus altithorax

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/dino-directory/brachiosaurus.html
- Field Museum: https://www.fieldmuseum.org/blog/first-brachiosaurus

Must read as:

- massive quadrupedal sauropod, not a biped or theropod
- front limbs visibly longer/taller than the hind limbs, creating high shoulders and a trunk line that descends from shoulders toward hips
- very long neck rising high above the shoulders, with a small herbivore head
- small head with a rounded fleshy nasal mound on top and high-set external nostril cue; avoid a flat generic sauropod skull
- shorter, less whip-like tail than a diplodocid
- full body visible enough to review tail, all feet, and ground contact

Reject if:

- the animal reads as Apatosaurus/Diplodocus with low shoulders, equal-height limbs, or a low forward neck
- rear-view or frontal-view pose hides the shoulder-to-hip slope or prevents independent limb counting
- feet, tail tip, or head are cropped or hidden enough to block anatomy review
- the head becomes flat, crocodile-like, toothy, predator-like, loses the rounded nasal mound, moves the nostril low and forward, or gains duplicate facial openings
- the animal rears up, becomes bipedal, or loses quadrupedal ground contact
- a new slot repeats an existing composition key, camera family, and spatial signature without adding independent anatomy or ecology information

Temporary app rule:

- Keep `brachiosaurus-altithorax-nasal-mound-fullbody-imagegen-v18.png` as the sole representative and positive full-body anatomy control. The approved six-role gallery is: S1 v18 front-three-quarter representative; S2 `brachiosaurus-altithorax-nasal-mound-slate-moss-rearthreequarter-pattern-imagegen-v2.png`; S3 dedicated vertical `brachiosaurus-altithorax-tailclear-canopy-window-habitat-ecology-imagegen-v2.png`; S4 head-only `brachiosaurus-altithorax-nasal-mound-head-reference-imagegen-v19.png`; S5 `brachiosaurus-altithorax-tailclear-conifer-browse-longlens-ecology-imagegen-v2.png`; and S6 `brachiosaurus-altithorax-two-individual-spacing-size-variation-imagegen-v2.png`. S4 does not imply a full-body, limb-count, shoulder, or tail pass. S6 must not be described as a family, parent-young pair, herd, protection scene, or observed growth sequence. Treat v16 as `review_hold`, not a positive training seed, because it lacks the current rounded nasal-mound and high-nostril gate. The six composition keys, camera families, and spatial signatures must remain unique.

- 2026-07-01 P1 follow-up: keep `brachiosaurus-p1-v9-v11-review-sheet.png` and `brachiosaurus-p1-v9-v11-crops.png` as the current prompt-only decision sheets. Treat `brachiosaurus-altithorax-imagegen-v10-source-candidate.png` as `review_hold` only: it is the strongest fresh source because the high shoulder, taller forelimbs, rising neck, side-profile body, and four-leg count read clearly, but the tail remains long and thin enough to need tail-base and diplodocid-drift review. Keep v4 first, keep v9 as a secondary review hold, and keep v11 as a reject reference for curling long-tail drift.
- 2026-07-02 P2 v12-v14 follow-up: keep `brachiosaurus-p2-v12-v14-review-sheet.png` and `brachiosaurus-p2-v12-v14-crops.png` as the latest high-shoulder versus short-tail decision sheets. Treat `brachiosaurus-altithorax-imagegen-v13-source-candidate.png` as `review_hold` only because it preserves a clear high-shoulder, taller-forelimb, rising-neck, four-foot read, but still has a long thin diplodocid-tail risk. Treat `brachiosaurus-altithorax-imagegen-v12-source-candidate.png` and `brachiosaurus-altithorax-imagegen-v14-source-candidate.png` as `reject_reference` because they document the same failure more strongly: strong shoulders but unsafe long whip-tail reads. Keep v4 first until a candidate proves high shoulders, taller forelimbs, rising neck, four open feet, and a short thick tail together.
- 2026-07-02 P3 v15-v17 historical note, superseded on 2026-08-03: v16 was temporarily promoted because it paired a compact tail with the high-shoulder/taller-forelimb body plan and four reviewable feet. Keep the P3 sheets, v4, v17, and v15 only as comparison records; v16 is no longer a count-level pass or positive train seed because it misses the current nasal-mound/high-nostril gate.
- 2026-08-03 closure supersedes the temporary v16 promotion: v18 is the only `count-level pass` and train seed. S2, S3, S5, and S6 passed independent original-size full-body review; S4 passed only as a close head-detail role. Full provenance, file hashes, role boundaries, and composition signatures are recorded in `tools/comfyui/brachiosaurus-gallery-closure-20260803.json`.

## Mammuthus primigenius

Reference anchors:

- Natural History Museum: https://www.nhm.ac.uk/discover/were-all-mammoths-woolly.html
- Larramendi 2016 proboscidean body-shape study: https://doi.org/10.4202/app.00136.2014
- Willerslev et al. 2014 mammoth-steppe vegetation study: https://doi.org/10.1038/nature12921

Must read as:

- Cenozoic elephantid with a high shoulder, back descending toward the hips, domed head, tiny ears, short tail, and dense coat
- one trunk, exactly two separate spiralling upper tusks, four connected columnar limbs, and four broad padded feet

Reject if:

- it becomes a dinosaur, mastodon, modern-elephant clone, flat-backed low-shouldered animal, fan-eared animal, naked elephant, long-tailed animal, or camel-humped animal
- tusks, trunk, limbs, feet, tail, or crop are duplicated, missing, fused, crossed, malformed, or hidden enough to block review

Evidence boundary:

- The broad cold-dry mammoth-steppe and core silhouette are evidence-led. Exact coat color, hair placement, sex, age, weather, movement, local plants, and the pictured adult-calf relationship or maternal behavior remain reconstruction hypotheses.

Promotion rule:

- S1 is the sole `count-level pass` representative. S2 remains a color-pattern `review hold`; S3 remains a multi-animal habitat `anatomy review`. S2 and S3 cannot replace or outrank S1 without a separate anatomy-promotion review.

## Smilodon fatalis

Reference anchors:

- Florida Museum of Natural History: https://www.floridamuseum.ufl.edu/florida-vertebrate-fossils/species/smilodon-fatalis/
- Meachen-Samuels & Van Valkenburgh 2010 forelimb-strength study: https://doi.org/10.1371/journal.pone.0011412
- La Brea Tar Pits tiger/coat reconstruction boundary: https://tarpits.org/stories/smilodon-saber-tooths-and-tigersoh-my

Must read as:

- Cenozoic machairodont felid with a deep chest, thick neck, powerful shoulders and forelimbs, sturdy feline hind limbs, four connected feline paws, and one short complete tail
- exactly one elongated upper canine pair, two sabers total, without elongated lower canines

Reject if:

- it becomes a tiger, lion, bear, hyena, wolf, or cheetah clone; gains a long or tufted tail, mane, default tiger stripes, or repeated modern-cat rosettes
- it shows more or fewer than two elongated upper sabers, lower-jaw sabers, crossed or lip-piercing canines, non-feline feet, extra or fused limbs, or cropped head, paws, or tail

Evidence boundary:

- Robust forelimbs are fossil-led, but exact prey restraint, kill pose, sociality, coat color or pattern, lip coverage, weather, vegetation, and the S3 cat-bovid encounter remain hypotheses. S3 establishes no attack, contact, capture, or pack hunt.

Promotion rule:

- S1 is the sole `count-level pass` representative. S2 remains a coat-pattern `review hold`; S3 remains a non-contact habitat `anatomy review`. S2 and S3 cannot replace or outrank S1 without a separate anatomy-promotion review.

## Mammut americanum

Reference anchors:

- National Park Service species overview: https://www.nps.gov/articles/000/mammut_americanum.htm
- National Park Service mammoth-or-mastodon comparison: https://www.nps.gov/articles/mammoth-or-mastodon.htm
- Natural History Museum reconstruction notes: https://www.nhm.ac.uk/discover/the-making-of-an-american-mastodon.html
- Larramendi 2016 proboscidean body-shape study: https://doi.org/10.4202/app.00136.2014

Must read as:

- a stocky North American mastodon with a comparatively near-level back and shoulders, a lower and broader head than the woolly-mammoth direction, modest ears, one trunk, and a short complete tail
- exactly two separate upper tusks with gentle upward curvature, exactly four attached columnar limbs, and four broad feet; woodland browsing is a broad ecological direction rather than a claim about the pictured individual

Reject if:

- it becomes a high-shouldered, strongly rear-sloping, domed-headed woolly mammoth; a fan-eared modern elephant clone; or a fantasy proboscidean with spiral mammoth tusks, lower-jaw tusks, extra trunks, or a long tufted tail
- tusks, trunk, limbs, feet, or tail are duplicated, fused, missing, crossed, malformed, or hidden enough to prevent a confident count

Evidence boundary:

- The near-level mastodon body plan and a browsing association with wooded habitats are evidence-led. Exact hair density, color, sex, age, tusk curvature, gait, season, weather, named plant, and the S3 willow-feeding moment remain reconstructions.

Promotion rule:

- S1 is the only `count-level pass` representative candidate in this intake. S2 remains `review hold`; S3 remains `anatomy review`. None is a final anatomy-certified representative, and S2 or S3 cannot replace or outrank S1 without a separate promotion review.

## Megatherium americanum

Reference anchors:

- Natural History Museum overview: https://www.nhm.ac.uk/discover/what-was-megatherium.html
- Bargo 2001 skull, bite-force, and diet study: https://www.app.pan.pl/article/item/app46-173.html
- CONICET museum overview: https://www.conicet.gov.ar/a-mosasaurus-and-a-megatherium-were-presented-at-the-macns-202-anniversary/

Must read as:

- a huge deep-bodied terrestrial sloth with a relatively small head, massive pelvis and hindquarters, two long robust forelimbs bearing large curved claws, two weight-bearing hind limbs, and one thick muscular tail
- a primarily quadrupedal animal for which a stationary hind-limb-and-tail tripod may be shown only as a conservative reconstruction; it must not be forced into a permanent upright stance or a running bipedal gait

Reject if:

- it becomes a bear, giant anteater, gorilla, Therizinosaurus, or generic furry monster; loses the massive pelvis and thick tail; gains a narrow whiplike tail; or uses its forelimbs as an extra pair of hind legs
- limbs, feet, claw groups, or tail are duplicated, fused, missing, disconnected, or cropped; do not claim a precise living digit formula when the generated hand is not clear enough to support it

Evidence boundary:

- The massive body, strong hindquarters, large foreclaws, and heavy tail are skeleton-led. Fur, color, external ear and nose form, exact claw sheath, gait phase, plant, weather, tail-ground contact, and feeding action are reconstructed. S3 is a conservative stationary tripod-browse visualization, not evidence for a permanent upright gait or this exact event.

Promotion rule:

- S1 is the only `count-level pass` representative candidate in this intake. S2 remains `review hold`; S3 remains `anatomy review`. Exact manus and pedal anatomy still require a dedicated source comparison before any final representative promotion.

## Arctodus simus

Reference anchors:

- Schubert et al. Florida occurrence and range record: https://doi.org/10.1666/09-113.1
- Figueirido et al. body-proportion and ecomorphology review: https://doi.org/10.1080/02724630903416027
- Figueirido et al. elbow-joint and locomotor review: https://doi.org/10.1007/s10914-017-9413-x
- North American short-faced-bear diet study: https://www.nature.com/articles/s41598-017-18116-0

Must read as:

- a very large tremarctine bear with a high broad cranium, short nasals, and a deep broad rostrum; the muzzle must project as a real bear muzzle rather than collapsing into a bulldog-flat face
- a relatively compact, short-backed trunk with the hips close behind the ribcage, a readable underside, and no independent rounded grizzly shoulder hump; retain one short tail
- exactly four attached robust limbs and compact plantigrade, five-toed bear paws when the digits are readable; relatively tall proportions must remain weight-bearing and bear-like rather than becoming digitigrade, cheetah-like pursuit stilts

Reject if:

- it becomes a modern brown- or grizzly-bear long low barrel with a rounded shoulder hump, or is overcorrected into a bulldog-faced fantasy bear, polar-bear muzzle, hyena, dog, cat, or cheetah-like sprinting specialist
- it gains a sagging pear-shaped belly, long tail, digitigrade feet, hoof-like toes, feline paws, hand-like spread digits, or thin racing stilts
- limbs, paws, toes, head, or tail are duplicated, fused, disconnected, missing, or obscured enough to block review

Evidence boundary:

- The short-faced impression is constrained by a deep broad rostrum and short nasal region, not an extremely flattened muzzle. The compact-back, robust-limb and plantigrade-bear direction is fossil-led, while published scaling cautions against cheetah-like pursuit legs. Exact trunk contour, muzzle soft tissue, coat, color, shoulder contour, speed, sociality, hunting, scavenging, and dietary emphasis remain debated or reconstructed. S3's exposed roots, tubers, grubs and log investigation establish no preferred food or observed foraging sequence.

Promotion rule:

- `arctodus-simus-compact-back-deep-rostrum-representative-imagegen-v3.png` is the only `count-level pass` representative candidate in the corrected set. `arctodus-simus-aspen-gray-compact-back-review-imagegen-v2.png` remains `review hold`, and `arctodus-simus-root-foraging-compact-back-ecology-imagegen-v2.png` remains `anatomy review`; S2 and S3 are prohibited from representative promotion. The former three modern-brown-bear-like runtime images are superseded and rejected rather than retained as positive controls.

## Glyptodon reticulatus

Reference anchors:

- Recent Glyptodon systematic revision: https://link.springer.com/article/10.1186/s13358-023-00280-8
- Ancient-DNA placement within armadillos: https://doi.org/10.1016/j.cub.2016.01.039
- Comparative glyptodont tail-weaponry anatomy: https://doi.org/10.1002/ar.24093
- Museum national d'Histoire naturelle overview: https://www.mnhn.fr/fr/glyptodonte

Must read as:

- a large glyptodont with one rigid high-domed carapace built from many irregular rosette-like osteoderms, a small armored head, exactly four short stout legs and feet, and one armored tail carried in successive osteoderm rings
- the tail must taper without an expanded Doedicurus-like knob or spikes; its distal fusion details remain a review boundary. The rigid carapace must not become a flexible modern-armadillo band series, turtle shell, or ankylosaur armor

Reject if:

- it becomes a tortoise, ankylosaur, Doedicurus with a clubbed or spiked tail, fantasy tank, or enlarged modern armadillo with fully flexible bands
- legs, feet, armor, head, or tail are duplicated, fused, missing, floating, or hidden enough to create a three-legged read; regular tiled texture alone cannot substitute for reviewable osteoderm rosettes

Evidence boundary:

- `Glyptodon reticulatus` is used here following recent revision, while historical `G. clavipes` assignments and species boundaries have changed. Visible gates are therefore conservative and mostly genus-level. Exact osteoderm geometry, soft tissue, hair, color, habitat, posture, and the S3 shared frame with Megatherium remain reconstructions; the scene proves no encounter, herd, or exact locality and moment of coexistence.

Promotion rule:

- S1 is the only `count-level pass` representative candidate in this intake. S2 remains `review hold`; S3 remains a two-taxon `anatomy review`. Species-level osteoderm comparison and a separate promotion decision are required before final representative certification.
