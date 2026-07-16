# Model And LoRA Candidates

조사일: 2026-06-20

## 우선 추천

### SDXL Base 1.0

- Source: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- License: OpenRAIL++
- 용도: 앱 MVP의 기본 생성 모델
- 이유: ComfyUI 호환성이 좋고, RTX 4080 16GB에서 다루기 현실적입니다.
- 주의: 공룡 종별 해부학 정확도는 프롬프트/검수/참고 특징 데이터로 보완해야 합니다.

### Stable Diffusion 3.5 Large 또는 Medium

- Source: https://huggingface.co/stabilityai/stable-diffusion-3.5-large
- License: Stability Community License
- 용도: 프롬프트 이해력과 품질 테스트
- 이유: 복잡한 자연어 프롬프트를 더 잘 따라갈 가능성이 있습니다.
- 주의: 라이선스 조건과 VRAM/속도를 확인해야 합니다.

## 보조 LoRA 후보

### tekakutli-dinosaurs

- Source: https://huggingface.co/lora-library/tekakutli-dinosaurs
- License: CreativeML OpenRAIL-M
- Base: SD 1.5 계열
- 용도: 공룡 형태 실험
- 주의: 오래된 SD 1.5 계열이고 다운로드/품질 검증 자료가 적습니다.

### ark-dinosaur-lora

- Source: https://huggingface.co/oliverbrown/ark-dinosaur-lora
- Base: SD 1.5
- Trigger: `arkdino`
- 용도: 도감/필드 스케치 스타일 실험
- 주의: ARK dossier 스타일에 특화되어 있어 교육용 사실 복원 이미지에는 직접 사용보다 스타일 실험용으로 제한하는 편이 좋습니다.

## Civitai 조사 메모

### Dinosaur Generator

- Source: https://civitai.com/models/383891
- Type: LoRA
- Base: SDXL 1.0
- File: `Dinosaur_Generator.safetensors`
- Size: about 36 MB
- API metadata: NSFW false, `allowNoCredit=true`, commercial image use listed in API metadata
- 용도: SDXL 기본 워크플로우에서 공룡 형태 보조
- 권장 weight: `0.25-0.45`

### Dinosaur Generator v2.0

- Source: https://civitai.com/models/386745
- Type: LoRA
- Base: SDXL 1.0
- File: `Dinosaur_Generator_v2.0-000011.safetensors`
- Size: about 218 MB
- API metadata: NSFW false, `allowNoCredit=true`
- 용도: SDXL 공룡 형태 보조
- 권장 weight: `0.25-0.5`

### Dinosaur Practical Effects

- Source: https://civitai.com/models/1062304
- Type: LoRA
- Base: Flux.1 D, also appears positioned for Flux/SDXL usage
- Trigger word: `dinosaur`
- File: `dinosaur_practical_fx.safetensors`
- Size: about 292 MB
- API metadata: NSFW false, `allowNoCredit=true`
- 용도: 실사/실물 모형 느낌 실험
- 주의: 영화/실물특수효과 스타일에 치우칠 수 있어 교육용 복원에는 낮은 weight로만 테스트합니다.

## Civitai 운영 메모

- Civitai에는 dinosaur 키워드 모델/LoRA가 있으나, 과학적 복원용으로 바로 신뢰할 후보는 제한적입니다.
- Civitai 다운로드는 모델별 라이선스, NSFW 여부, commercial use 허용 여부, trigger word를 반드시 확인해야 합니다.
- Civitai API 후보 조회 예:

```text
https://civitai.com/api/v1/models?query=dinosaur&limit=20&nsfw=false
```

## 추천 운영 방침

1. 기본은 SDXL 또는 SD3.5 계열 범용 모델로 생성합니다.
2. 공룡 특화 LoRA는 `0.25-0.55` 낮은 weight로만 실험합니다.
3. 특정 영화, 게임, 작가 스타일을 프롬프트에 넣지 않습니다.
4. 종별 특징은 앱 DB의 `visualTraits`에서 가져옵니다.
5. 모든 결과물은 검수 큐를 거친 뒤 공개합니다.
