# Dino Atlas Project Rules

- For dinosaur gallery image generation, candidate promotion, species identity cue updates, asset naming, or image path/render audits, use the personal Codex skill `dino-atlas-gallery-workflow`.
- For generated bitmap assets, use the `imagegen` workflow, then copy selected outputs into `assets/dinosaurs/`; never reference files directly from `.codex/generated_images`.
- Keep asset names species-prefixed, cue-specific, and versioned.
- Update `app.js` in the same pass when adding assets: `generatedImageSamples`, and when needed `identityChecklists`, `visualVariationProfiles`, and `generationRouteGuides`.
- Before finishing gallery work, verify `app.js` syntax, all real `assets/dinosaurs/...` paths, local server asset responses when available, and browser render behavior for the affected taxon.
- Brachiosaurus representatives must preserve the high-shouldered body plan and show the rounded top-of-head nasal mound/high-set nostril cue when possible.
