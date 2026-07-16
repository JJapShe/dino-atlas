# Multi-Dinosaur Smoke Test Findings

Last tested: 2026-06-21

## Test Outputs

- First pass sheet: `tools/comfyui/outputs/multi-dino-smoke-contact-sheet.png`
- Second pass sheet: `tools/comfyui/outputs/multi-dino-smoke2-contact-sheet.png`
- Targeted correction sheet: `tools/comfyui/outputs/multi-dino-target-contact-sheet.png`

## First Pass

Generated with the shared SDXL Base workflow and taxon-specific prompts:

- `Tyrannosaurus rex`: usable direction. Needs hand-count review for every candidate.
- `Triceratops horridus`: usable direction. Horn/frill silhouette was recognizable.
- `Stegosaurus stenops`: rejected. Dorsal plates were visible, but tail spikes were not clearly shown.
- `Velociraptor mongoliensis`: rejected. Drifted toward an ostrich-like ornithomimid body and lacked strong dromaeosaur/feather/sickle-claw cues.
- `Brachiosaurus altithorax`: improved with taller canvas. Usable direction, but needs side-profile consistency checks.
- `Ankylosaurus magniventris`: rejected. Drifted toward turtle-shell or spiky hybrid forms and did not clearly show the tail club.

## Targeted Corrections

- `Stegosaurus stenops`: improved. Tail spikes became visible enough for a review candidate.
- `Velociraptor mongoliensis`: improved as a feathered animal, but still needs better dromaeosaur proportions and clearer sickle claws.
- `Ankylosaurus magniventris`: improved away from turtle-shell drift, but still not acceptable. It shows tall dorsal spikes instead of the low, broad ankylosaur armor profile and the tail club remains weak.

## Next Prompt Adjustments

For `Velociraptor mongoliensis`:

- Keep: `small feathered dromaeosaurid`, `wing-like feathered arms`, `large raised sickle claw`.
- Add stronger negatives: `ostrich`, `emu`, `ornithomimid`, `long smooth neck`, `toothless bird head`.
- Consider a lower, wider composition and more side-on foot visibility.

For `Ankylosaurus magniventris`:

- Keep: `low wide armored dinosaur`, `large heavy tail club`.
- Add stronger positives: `flat low back`, `rounded osteoderms`, `club at the very end of the tail`.
- Add stronger negatives: `tall dorsal spikes`, `stegosaurus plates`, `ceratopsian horns`, `turtle carapace`.
- Consider a dedicated seed sweep; this taxon is not stable under the current general prompt.

For `Brachiosaurus altithorax`:

- Use a taller canvas such as `1024 x 896`.
- Keep `side profile view`, `front limbs longer than hind limbs`, and `high shoulder profile`.
