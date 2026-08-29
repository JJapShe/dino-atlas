# Dino Asset Review

공개 앱과 분리된 로컬 이미지 검수 서버다. 검수 대기 이미지는 Git에서 제외된 `pending/`에 보관하고, 상태와 처리 이력은 로컬 SQLite에 기록한다. 통과 자산만 `assets/dinosaurs/`로 이동하며, `app.js` 등록은 해부학 검토 뒤 별도 단계로 남긴다.

## 시작

저장소 루트에서 다음 명령을 실행한다.

```powershell
.\tools\dino-review\start-dino-review.ps1
```

런처는 SQLite를 지원하는 Node 24를 확인하고 `127.0.0.1:8792`에 서버를 띄운 뒤 인증된 검수 페이지를 연다. 접근 키는 `tools/dino-review/data/review-key`에 로컬로 저장되며 Git에 포함되지 않는다. `start-dino-atlas.ps1`을 실행하면 Atlas와 같은 검수 서버를 시작하고 두 화면을 함께 연다. 키가 없는 `http://127.0.0.1:8792/` 직접 접속은 의도적으로 HTTP 403을 반환한다.

다른 포트나 직접 정한 키가 필요하면 실행 전에 `DINO_REVIEW_PORT`, `DINO_REVIEW_KEY`를 설정한다. 키는 URL-safe 문자 16~128자로 제한된다.

## 후보 넣기

후보는 PNG 한 장과 `candidate.json` 한 장으로 구성된다. 직접 폴더를 만들기보다 enqueue 도구를 사용한다.

출처와 라이선스/권리 근거는 확인한 실제 기록을 그대로 입력한다. 생성 자산이면 제공자·도구/모델·버전·생성일과 적용 약관 또는 라이선스 근거까지 연결해 남기며, 예시용 문구를 권리 확인 없이 복사해 넣으면 안 된다.

```powershell
$node = 'C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$sourceRecord = Read-Host '정확한 출처 또는 생성 기록'
$licenseBasis = Read-Host '확인한 라이선스 또는 소유권 근거'
& $node .\tools\dino-review\enqueue.js `
  --candidate-id brachiosaurus-altithorax-high-shouldered-riverbank-v2 `
  --image C:\path\to\brachiosaurus-altithorax-high-shouldered-riverbank-imagegen-v2.png `
  --species-id brachiosaurus-altithorax `
  --kind 'count-level pass' `
  --source $sourceRecord `
  --license $licenseBasis `
  --prompt-file C:\path\to\prompt.txt `
  --seed 260810001 `
  --workflow 'imagegen anatomy-led v2' `
  --anatomy-status passed `
  --representative `
  --reviewer 'reviewer name' `
  --reviewed-at '2026-08-10T06:00:00.000Z' `
  --anatomy-notes '높은 어깨와 둥근 비강 융기, 높은 콧구멍 확인'
```

필수 메타데이터가 덜 채워진 후보도 대기함에는 넣을 수 있지만, 검수 화면에 누락 사유가 표시되고 승격은 차단된다. 수동 manifest 형식은 `candidate.example.json`을 참고한다.

승격 가능한 kind와 해부학 조건은 다음과 같다.

| kind | 대표 여부 | 허용 anatomy status |
| --- | --- | --- |
| `count-level pass` | `true` | `passed` |
| `review hold` | `false` | `passed`, `review-hold`, `reference-only`, `not-applicable` |
| `anatomy review` | `false` | 위와 같음 |
| `structure reference` | `false` | 위와 같음 |
| `ecosystem scene review` | `false` | 위와 같음 |

모든 kind에서 출처, 라이선스, 전체 프롬프트, 시드, 워크플로, 검토자와 ISO 검토 시각이 필요하다. 대표 이미지는 해부학 검증 전 `passed`로 기록하지 않는다.

## 검수 흐름

1. 기본 `검수 대기` 범위에서 후보를 선택한다.
2. `통과`, `보류`, `반려`와 메모를 저장한다.
3. 통과 후보는 모든 메타데이터와 해부학 gate가 맞을 때만 `자산 승격`이 활성화된다.
4. 반려 후보는 사유를 저장하고 정확한 파일명을 다시 입력해야 `완전 탈락 삭제`가 실행된다.

`앱 등록 대기` 범위에는 파일 승격은 끝났지만 `app.js` 등록이 남은 자산이 표시된다. 손상된 manifest나 PNG도 검수창의 `미분류/오류` 범위에 읽기 전용 카드로 남아 조용히 사라지지 않는다.

승격은 원본을 `assets/dinosaurs/<targetFilename>`으로 무덮어쓰기 이동하고, `promotions/<candidateId>.json`에 SHA-256, 크기, 검수 결과와 provenance를 남긴다. 상태는 `promoted-awaiting-app-integration`이다. 이후 갤러리 워크플로에 따라 `app.js`의 `generatedImageSamples`와 필요한 identity/checklist/profile/route 자료를 갱신하고 문법·경로·렌더 검증을 끝내야 공개 자산이 된다.

완전 탈락은 후보 PNG와 manifest만 삭제한다. 후보 ID, 파일명, SHA-256, 사유와 이벤트 이력은 SQLite에 남지만 이미지 자체는 복구되지 않는다.

## 저장 위치

- `pending/<candidate-id>/`: Git에서 제외된 검수 대기 PNG와 manifest
- `data/review.sqlite`: Git에서 제외된 SQLite DB; WAL/SHM 포함
- `promotions/<candidate-id>.json`: Git으로 추적하는 승격 감사 기록
- `assets/dinosaurs/`: 승격된 프로젝트 자산

DB는 이미지 원본을 BLOB으로 중복 저장하지 않는다. 대신 경로, 파일 상태, 크기, 수정 시각, 필요 시 계산한 SHA-256, 종·용도, 출처, 라이선스, 프롬프트·시드·워크플로, 해부학 검토, 검수 상태를 색인한다. 주요 테이블은 `metadata`, `reviews`, `review_events`, `candidates`, `candidate_events`, `asset_inventory`, `inventory_sync_runs`, `asset_app_registrations`다. 기존 `data/reviews.json`은 DB 최초 생성 때 한 번 가져온다.

서버는 숫자형 loopback 주소에만 바인딩하고 loopback Host만 허용한다. 브라우저가 `Origin`을 보낸 요청은 same-origin인지 확인하며, 모든 화면·API·미디어 접근에는 로컬 키가 필요하다. 변경 API는 키 헤더와 `application/json`도 요구한다. 다른 프로세스가 포트를 차지했거나 저장된 키로 health 검증이 되지 않으면 런처는 그 프로세스를 종료하지 않고 명확한 충돌 오류로 멈춘다.
