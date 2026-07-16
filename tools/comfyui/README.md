# Dino Atlas ComfyUI Pipeline

공룡 이미지 생성을 위한 ComfyUI 로컬 자동화 구성입니다. 이 폴더는 앱 코드와 분리되어 있으며, 워크플로우 템플릿과 생성 작업 스크립트만 포함합니다.

## 설치

```powershell
.\tools\comfyui\setup-comfyui.cmd
```

설치 후 ComfyUI 실행:

```powershell
.\tools\comfyui\start-comfyui.cmd
```

기본 서버 주소는 `http://127.0.0.1:8188`입니다.

## 모델 배치

ComfyUI 모델 폴더 기준:

- 체크포인트: `tools/comfyui/ComfyUI/models/checkpoints`
- LoRA: `tools/comfyui/ComfyUI/models/loras`
- VAE: `tools/comfyui/ComfyUI/models/vae`
- ControlNet: `tools/comfyui/ComfyUI/models/controlnet`

라이선스 동의가 필요한 Hugging Face/Civitai 모델은 직접 동의 후 다운로드하세요.

SDXL Base 1.0 다운로드:

```powershell
.\tools\comfyui\download-sdxl-base.cmd
```

Manual download links and target folders are listed in `tools/comfyui/download-links.md`.

## 추천 시작 조합

1. **기본 안정형**: SDXL Base 1.0 + SDXL VAE
2. **프롬프트 이해 강화형**: Stable Diffusion 3.5 Large 또는 Medium
3. **실험형 LoRA**: dinosaur/paleoart LoRA를 낮은 weight로 보조 적용

공룡 앱에서는 과학적 정확도가 중요하므로, LoRA는 처음부터 강하게 쓰지 말고 `0.25-0.55` 정도로 테스트하는 것을 권장합니다.

## 자동화 흐름

```text
dino data -> prompt generator -> workflow api json -> /prompt -> /history/{prompt_id} -> output image -> review queue
```

ComfyUI 공식 서버 API는 `/prompt` 제출, `/history/{prompt_id}` 결과 조회, `/ws` 진행 상태 구독을 지원합니다.

## Workflow 템플릿

- `workflow_templates/dino_sdxl_base_api.json`: SDXL 기본형
- `workflow_templates/dino_sdxl_lora_api.json`: SDXL + LoRA 실험형

종별 workflow 생성:

```powershell
.\tools\comfyui\.venv\Scripts\python.exe .\tools\comfyui\scripts\build_workflow.py --taxon-id tyrannosaurus-rex
```
