# Dino Atlas MVP

공룡 계통도 기반 도감 MVP입니다. 현재 버전은 이미지 생성 파이프라인을 연결하지 않고 더미 이미지 슬롯만 표시합니다.

## 구성

- `index.html`: 정적 앱 진입점
- `styles.css`: 다크모드 UI 스타일
- `app.js`: 더미 공룡 데이터, 계통도/도감/검수 화면 렌더링

## 실행

브라우저에서 `index.html`을 열면 바로 실행됩니다.

```powershell
Start-Process .\index.html
```

## MVP 화면

- 계통도: 트라이아스기/쥐라기/백악기 3단 지도형 계통 트리, 확대/축소/이동 지원
- 도감: 카드형 공룡 목록, 검색/식성/공룡지식 LV 필터/정렬
- 상세: 생성 후보, 라이선스 확인 비교군, 시대 장면, 검수 컷을 넘겨보는 스와이프 갤러리
- 검수: 더미 이미지 슬롯과 ComfyUI 자동화 단계

## 공룡지식 LV

- `LV1`: 유명 공룡
- `LV2`: 익숙한 도감
- `LV3`: 탐험 단계
- `LV4`: 매니아

이 필드는 이후 퀴즈 난이도와 학습 진행도에 연결할 수 있습니다.

## ComfyUI 자동화

ComfyUI 로컬 설치와 공룡 이미지 생성 자동화 초안은 `tools/comfyui`에 있습니다.

- 설치/실행: `tools/comfyui/README.md`
- 모델 후보: `tools/comfyui/model-candidates.md`
- 생성 사양: `tools/comfyui/dino-generation-spec.md`
- 워크플로우 템플릿: `tools/comfyui/workflow_templates`
