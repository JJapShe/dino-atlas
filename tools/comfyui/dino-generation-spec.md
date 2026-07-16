# Dino Image Generation Spec

## 목표

저작권 리스크가 낮고, 재현 가능한 공룡 교육용 이미지를 생성합니다.

## LLM 역할

LLM은 이미지를 직접 만들지 않고 다음 JSON을 생성합니다.

```json
{
  "taxonId": "tyrannosaurus-rex",
  "positivePrompt": "scientifically plausible full body paleoart of Tyrannosaurus rex...",
  "negativePrompt": "text, watermark, logo, movie monster, fantasy dragon...",
  "visualTraits": [
    "large deep skull",
    "short two-fingered forelimbs",
    "long balancing tail"
  ],
  "reviewChecklist": [
    "bipedal theropod posture",
    "two-fingered forelimbs",
    "no text or watermark"
  ]
}
```

## 기본 프롬프트 템플릿

```text
Scientifically plausible educational paleoart of {scientificName},
full body side view, {period}, {region} environment,
{visualTraits},
natural history museum reconstruction, accurate anatomy, neutral lighting,
no text, no logo, no watermark
```

## Color Tuning Default

Current recommended MVP setting after local smoke tests:

- Checkpoint: `sd_xl_base_1.0.safetensors`
- VAE: `sdxl_vae.safetensors`
- Canvas: `1152 x 768`
- Sampler: `dpmpp_2m_sde_gpu`
- Scheduler: `sgm_uniform`
- Steps: `38`
- CFG: `4.8`
- Positive style terms: `clean digital paleoart`, `modern dinosaur encyclopedia quality`, `non-signed image`, `professional natural history reconstruction`, `single adult`, `full body lateral side view`
- Positive color terms: `clean daylight`, `balanced white balance`, `realistic earth tones`, `natural contrast`
- Negative artifact terms: `text`, `signature`, `bottom right mark`, `multiple dinosaurs`, `skeleton`, `exposed bones`, `visible ribs`, `anatomical diagram`, `sepia`, `washed out colors`, `color cast`
- Benchmark seed: `2026063203` produced the current best Tyrannosaurus rex reference candidate during local tests.
- Avoid positive terms such as `field guide`, `museum`, or `skeleton` for the single-animal restoration workflow; those terms pulled the output toward diagrams or exposed-bone reconstructions during local tests.

## Negative Prompt

```text
movie monster, fantasy dragon, kaiju, toy, plastic, cartoon, anime,
incorrect limb count, extra head, extra tail, text, labels, watermark, logo,
blurry, cropped body, human rider, saddle
```

## ComfyUI API 노드 치환 방식

워크플로우 API JSON에서 다음 노드를 변수화합니다.

- checkpoint loader: `ckpt_name`
- positive CLIPTextEncode: `text`
- negative CLIPTextEncode: `text`
- KSampler: `seed`, `steps`, `cfg`, `sampler_name`, `scheduler`
- EmptyLatentImage: `width`, `height`, `batch_size`
- SaveImage: `filename_prefix`

## 저장 메타데이터

```json
{
  "taxonId": "tyrannosaurus-rex",
  "workflowVersion": "dino-sdxl-v0.1",
  "model": "sd_xl_base_1.0.safetensors",
  "lora": [],
  "seed": 123456789,
  "width": 1024,
  "height": 768,
  "status": "queued"
}
```
