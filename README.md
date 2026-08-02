# Dino Atlas MVP

5~14세 사용자를 위한 공룡 계통도 기반 도감 MVP입니다.

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
- 도감: 카드형 공룡 목록, 검색/식성/도감 친숙도 LV 필터/정렬
- 상세: 생성 후보, 라이선스 확인 비교군, 시대 장면, 검수 컷을 넘겨보는 스와이프 갤러리
- 검수: 더미 이미지 슬롯과 ComfyUI 자동화 단계

## 도감 친숙도 LV

- `LV1 스타`: 대부분의 아이가 이름이나 모습으로 알아볼 대표 종
- `LV2 도감 단골`: 어린이 도감·전시·콘텐츠에서 자주 만나는 종
- `LV3 탐험가`: 공룡을 관심 있게 찾아보면 만나게 되는 종
- `LV4 연구자`: 전문 도감이나 특정 분류군 탐구에서 주로 만나는 종

이 값은 종의 **친숙도와 발견 순서**를 나타냅니다. 설명문의 읽기 난이도, 학술적 중요도, 생존 시기와는 별개이며 퀴즈 난이도로 직접 사용하지 않습니다. 세부 판정 기준과 표본 종은 [`docs/knowledge-level-rubric.md`](docs/knowledge-level-rubric.md)에 기록합니다.

## ComfyUI 자동화

ComfyUI 로컬 설치와 공룡 이미지 생성 자동화 초안은 `tools/comfyui`에 있습니다.

- 설치/실행: `tools/comfyui/README.md`
- 모델 후보: `tools/comfyui/model-candidates.md`
- 생성 사양: `tools/comfyui/dino-generation-spec.md`
- 워크플로우 템플릿: `tools/comfyui/workflow_templates`
