# ComfyUI Manual Download Links

Last checked: 2026-06-20

Related LoRA research and current verdicts are tracked in `tools/comfyui/lora-research.md`.

Download files into your Downloads folder first, then move them to the target ComfyUI folder listed below.

## Required For Current MVP

### 1. SDXL Base 1.0 checkpoint

- File: `sd_xl_base_1.0.safetensors`
- Size: about 6.94 GB
- Model page: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- File page: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/sd_xl_base_1.0.safetensors
- Direct download: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors`

### 2. Dinosaur Generator LoRA

- File: `Dinosaur_Generator.safetensors`
- Size: about 36 MB
- Model page: https://civitai.com/models/383891
- Direct download: https://civitai.com/api/download/models/431570
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\loras\Dinosaur_Generator.safetensors`
- Current workflow uses this filename directly.

## Optional Test Candidates

### SD 1.5 fp16 checkpoint

- File: `v1-5-pruned-emaonly-fp16.safetensors`
- Model page: https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive
- Direct download: https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\checkpoints\v1-5-pruned-emaonly-fp16.safetensors`
- Note: downloaded and tested for SD 1.5 species-LoRA experiments. Not selected as the MVP default.

### Triceratops XL LoRA

- File: `TriceratopsXL0_4.safetensors`
- Model page: https://civitai.com/models/523521
- Direct download: https://civitai.com/api/download/models/581641
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\loras\TriceratopsXL0_4.safetensors`
- Note: best immediate species-specific SDXL LoRA candidate found so far. Test only for Triceratops at low-to-medium strength.

### Dinosaur Practical Effects SDXL LoRA

- File: `dinosaur_practical_fx_sdxl_1_0.safetensors`
- Model page: https://civitai.com/models/1062304
- Direct download: https://civitai.com/api/download/models/1213542
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\loras\dinosaur_practical_fx_sdxl_1_0.safetensors`
- Note: separate from the Flux version already downloaded as `dinosaur_practical_fx.safetensors`. Low-priority style experiment only.

### Dinosaur Generator v2.0 LoRA

- File: `Dinosaur_Generator_v2.0-000011.safetensors`
- Size: about 218 MB
- Model page: https://civitai.com/models/386745
- Direct download: https://civitai.com/api/download/models/431713
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\loras\Dinosaur_Generator_v2.0-000011.safetensors`
- Note: good A/B candidate after the MVP workflow is working.

### SDXL VAE

- File: `sdxl_vae.safetensors`
- Model page: https://huggingface.co/stabilityai/sdxl-vae
- File page: https://huggingface.co/stabilityai/sdxl-vae/blob/main/sdxl_vae.safetensors
- Direct download: https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\vae\sdxl_vae.safetensors`
- Note: used by the current MVP workflow for more stable color and brightness.

### SDXL Refiner 1.0

- File: `sd_xl_refiner_1.0.safetensors`
- Model page: https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0
- File page: https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/blob/main/sd_xl_refiner_1.0.safetensors
- Direct download: https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\checkpoints\sd_xl_refiner_1.0.safetensors`
- Note: optional. The current MVP workflow does not use the refiner yet.

### Dinosaur Practical Effects LoRA

- File: `dinosaur_practical_fx.safetensors`
- Size: about 292 MB
- Model page: https://civitai.com/models/1062304
- Direct download: https://civitai.com/api/download/models/1192189
- Put here: `C:\Users\USER\Documents\dinosour\tools\comfyui\ComfyUI\models\loras\dinosaur_practical_fx.safetensors`
- Note: more stylized practical-effect look; test at low LoRA strength only.

## Hold Off For Now

These are SD 1.5 LoRAs, so they need an SD 1.5 checkpoint and a separate workflow. Do not download them for the current SDXL MVP unless you want a separate experiment.

- tekakutli-dinosaurs: https://huggingface.co/lora-library/tekakutli-dinosaurs
- ark-dinosaur-lora: https://huggingface.co/oliverbrown/ark-dinosaur-lora

Species-specific SD 1.5 candidates worth testing only after a separate SD 1.5 workflow exists:

- Experimental Velociraptor: https://civitai.com/models/123987
  - Direct download: https://civitai.com/api/download/models/135283
  - File: `Velociraptor_Dino.safetensors`
  - Local status: downloaded and tested. It adds feather-like cues but drifts too much toward bird silhouettes.
- Experimental Ankylosaurus: https://civitai.com/models/194220
  - Direct download: https://civitai.com/api/download/models/218295
  - File: `Ankylosaurus_Dinosaur.safetensors`
  - Local status: downloaded and tested. Texture improved, but full-body framing and tail club remain unstable.
- Triceratops SD 1.5: https://civitai.com/models/27631
  - Direct download: https://civitai.com/api/download/models/33081
  - File: `triceratops.safetensors`

Illustrious candidates need an Illustrious-compatible checkpoint and separate workflow. They are not recommended for the current realistic SDXL atlas pipeline, but may be useful for anatomy-cue experiments:

- Stegosaurus Dinosaur IXL: https://civitai.com/models/1503821
  - Direct download: https://civitai.com/api/download/models/1701233
  - File: `StegosaurusDinosaur_IXL.safetensors`
- Allosaurus Illustrious: https://civitai.com/models/2297868
  - Direct download: use the model page download button if the API redirects.
  - File: `Allosaurus.safetensors`
  - Note: species-relevant but Illustrious-trained; use only after adding an Illustrious workflow branch.
- Ankylosaurus Illustrious: https://civitai.com/models/2118196
  - Direct download: https://civitai.com/api/download/models/2538790
  - File: `ankyv2.safetensors`
- Dinosaur Expansion for Illustrious: https://civitai.com/models/1286367
  - Direct download: https://civitai.com/api/download/models/1451368
  - File: `Dino_Diffusion.safetensors`

## Notes

- Hugging Face or Civitai may require login or license acceptance before the file starts downloading.
- Civitai direct links may redirect. If a direct link fails, open the model page and use the Download button.
- Keep the filenames exactly as listed above, because the ComfyUI workflow references them by name.

## Local Smoke Test

- `sd_xl_base_1.0.safetensors` generated successfully with the base SDXL workflow.
- `Dinosaur_Generator.safetensors` loaded with shape mismatch errors against the SDXL checkpoint, so it should not be the default LoRA.
- `Dinosaur_Generator_v2.0-000011.safetensors` generated successfully, but may still create signature/text-like artifacts; keep it experimental and review every image.
