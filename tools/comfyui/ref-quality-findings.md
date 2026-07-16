# Reference Quality Test Findings

Last tested: 2026-06-20

## Selected Default

- Checkpoint: `sd_xl_base_1.0.safetensors`
- VAE: `sdxl_vae.safetensors`
- Canvas: `1152 x 768`
- Sampler: `dpmpp_2m_sde_gpu`
- Scheduler: `sgm_uniform`
- Steps: `38`
- CFG: `4.8`
- Style direction: `clean digital paleoart`, `modern dinosaur encyclopedia quality`, `non-signed image`, `professional natural history reconstruction`
- Benchmark seed: `2026063203`
- Benchmark output: `tools/comfyui/ComfyUI/output/dino_atlas/tyrannosaurus-rex_final_reference_00001_.png`

## Why This Setting

- `dpmpp_2m_sde_gpu` with `sgm_uniform` produced more stable single-animal restoration images than the original `dpmpp_2m`/`karras` baseline.
- `1152 x 768` gave more room for the head, tail, and feet than the original `1024 x 768`.
- `field guide`, `museum`, and `skeleton` in the positive prompt repeatedly pulled outputs toward diagrams, exposed ribs, or skeletal plates.
- `clean digital paleoart` reduced fake signature/text artifacts better than stronger illustration or field-guide wording.
- LoRA tests were not chosen as default:
  - `Dinosaur_Generator.safetensors` produced SDXL shape mismatch errors.
  - `Dinosaur_Generator_v2.0-000011.safetensors` can generate, but had a higher risk of signature-like marks and over-stylization.

## Useful Comparison Sheets

- Color tuning: `tools/comfyui/outputs/color-test2-contact-sheet.png`
- Early reference-quality test: `tools/comfyui/outputs/ref-quality3-contact-sheet.png`
- SDE vs DPM seed sweep: `tools/comfyui/outputs/ref-sweep-contact-sheet.png`
- Final clean digital sweep: `tools/comfyui/outputs/ref-clean-sweep-contact-sheet.png`

## Prompt Notes

For the single-animal restoration workflow, keep the positive prompt focused on:

- `single adult`
- `only one animal`
- `full body lateral side view`
- `entire animal visible with clear margins`
- `intact natural skin`
- `subtle scales`
- `clean empty corners`

Keep these in the negative prompt:

- `text`, `labels`, `signature`, `artist signature`, `bottom right mark`
- `multiple dinosaurs`, `duplicate dinosaur`
- `skeleton`, `exposed bones`, `visible ribs`, `anatomical diagram`
- `cropped body`, `cropped tail`, `cropped feet`

Use a separate ecosystem-scene workflow for images that intentionally include multiple dinosaurs.

## Anatomy Review Gate

Prompting reduces anatomy errors, but does not guarantee correctness. Every generated image should pass a review gate before it is exposed in the app.

For `Tyrannosaurus rex`, the blocking rule is:

- each visible hand must have exactly two fingers
- reject if a visible hand has three or more fingers
- reject if hands are human-like, mangled, or too unclear to verify

Recommended review flow:

1. Generate several candidates with different seeds.
2. Create a review packet:

```powershell
.\tools\comfyui\.venv\Scripts\python.exe .\tools\comfyui\scripts\build_review_packet.py --taxon-id tyrannosaurus-rex --image "dino_atlas\tyrannosaurus-rex_final_reference_00001_.png"
```

3. Send the image plus `visionJudgePrompt` and `reviewChecklist` to a vision-language judge, or show the same packet in the human review UI.
4. Auto-reject clear failures, such as three fingers, exposed ribs, text, signature marks, cropped feet, or duplicate animals.
5. Keep final publication gated by human approval for now.

The review packet is intentionally strict: if the hand count is not visible enough to verify, the image should stay in `needs_review` or be regenerated.
