# Dino Atlas 슬롯 기반 이미지 생성 CLI Goal Prompt

이 문서 전체를 `C:\Users\USER\Documents\dinosour`에서 실행하는 Codex CLI의 goal objective로 사용한다. 이 문서는 단순 수량 부족 감사용 `dino-image-gap-fill-goal.md`보다 우선하는 슬롯 기반 생성 지침이다.

## 최종 목표

Dino Atlas에 등록된 모든 공룡의 `imageSlots`를 역할이 명확한 최종 이미지로 채운다. 각 종은 대표 이미지에서 확정한 몸 색, 무늬 배치, 피부·깃털 질감과 핵심 해부학을 다른 슬롯에서도 유지해야 한다. 서식지에 따른 색 변화는 종의 기본 팔레트를 바꾸는 방식이 아니라, 배경색·조명·국소적인 흙먼지·진흙·습기·위장 대비를 조정하는 방식으로 적용한다.

기존 이미지를 먼저 선별해 슬롯에 배정하고, 적합한 기존 이미지가 없는 슬롯만 새로 생성한다. 새 이미지 생성, 후보 승격, 종 특징 수정, 앱 갤러리 반영에는 반드시 `dino-atlas-gallery-workflow`를 사용한다. 비트맵을 새로 만들 때는 `imagegen` 워크플로를 사용하고, 선택된 결과만 `.codex/generated_images`에서 `assets/dinosaurs/`로 복사한다. 앱은 `.codex/generated_images`를 직접 참조하면 안 된다.

## 현재 기준선

2026-07-13 감사 결과는 다음과 같다. 실행을 시작할 때 다시 계산하고, 데이터가 달라졌다면 최신 수치를 기준으로 계획을 갱신한다.

- 등록 종: 132종
- 전체 목표 슬롯: 472칸
- 슬롯 분포: 3칸 92종, 4칸 8종, 5칸 29종, 6칸 2종, 7칸 1종
- 등록 샘플: 1,356개
- 현재 사용자 노출 가능 실제 이미지: 786장
- 슬롯 수와 정확히 일치하는 종: 86종
- 슬롯보다 이미지가 많은 종: 41종, 합계 319장 초과
- 슬롯보다 적게 보이는 종: 5종
- 이 중 4종은 실제로 1장씩 부족하고, `Hanssuesia sternbergi`는 정상 `mask-pattern` 이미지를 내부 마스크로 오인해 숨기는 필터 문제다.
- 실제 1장 부족 종: `riojasaurus-incertus`, `dracovenator-regenti`, `monolophosaurus-jiangi`, `cetiosaurus-oxoniensis`
- `herrerasaurus-ischigualastensis`는 사용자용 이미지 수는 충분하지만 활성 `count-level pass` 대표가 없으므로 슬롯 1을 별도 재검수하거나 새로 생성해야 한다.
- 132종 모두 `visualVariationProfiles`와 `generationRouteGuides`가 있다.
- `identityChecklists`가 없는 종: `ceratosaurus-nasicornis`, `scutellosaurus-lawleri`
- 4색 스와치가 없는 종: `wannanosaurus-yansiensis`, `alaskacephale-gangloffi`, `sphaerotholus-goodwini`, `acrotholus-audeti`
- `generatedImageSamples` 안에 이미지 객체가 아닌 문자열이 들어간 곳이 2개 있다: `stegosaurus-stenops` index 0, `velociraptor-mongoliensis` index 1.

따라서 472장을 모두 새로 만들지 않는다. 먼저 786장에서 최종 472칸을 선별하고, 슬롯 역할·해부학·색상 일관성이 부족한 칸만 생성한다.

## 1. 슬롯 계약

모든 종은 `imageSlots` 수만큼 아래 순서의 슬롯을 사용한다. 슬롯이 적은 종은 앞에서부터 필요한 수만 사용한다.

| 슬롯 | 역할 | 기본 구성 | 앱 분류 |
|---|---|---|---|
| 1 | 대표 전신 | 한 개체, 머리부터 꼬리 끝까지 전신, 팔다리와 발이 모두 판독 가능 | `count-level pass` |
| 2 | 색상·무늬 변형 | 같은 몸 비율과 무늬 토폴로지, 승인 팔레트 안의 제한된 변형 | `review hold` |
| 3 | 대표 서식지·일상 생태 | 시대와 지역에 맞는 서식지, 먹이활동·이동·휴식 중 하나 | `anatomy review` 또는 판독성이 높으면 `review hold` |
| 4 | 종 고유 구조 | 머리, 손·발, 볏, 프릴, 골판, 갑옷, 꼬리 구조 등 가장 중요한 특징 | 사용자용 `anatomy review` |
| 5 | 생태 상호작용 | 같은 시대·지역의 다른 생물과 추격·방어·무리·경계 행동 | `anatomy review` |
| 6 | 사회·성장·방어 변형 | 무리, 새끼 보호, 과시, 방어, 두 번째 생태 행동 중 과학적으로 무리 없는 장면 | `anatomy review` |
| 7 | 대체 미세서식지·행동 | 계절·시간대·미세서식지 또는 두 번째 해부학 강조 장면 | `anatomy review` |

슬롯 1~3은 모든 종의 고정 핵심이다. 슬롯 4 이상은 해당 종에서 가장 교육적인 특징을 우선한다. 근거가 약한 성적 이형, 털색, 집단 사냥, 육아 행동을 사실처럼 단정하지 않는다. 색상과 무늬는 화석으로 확정된 사실이 아니라 앱의 일관된 복원 아트 디렉션이라는 점을 설명 데이터에 유지한다.

## 2. 명시적 슬롯 데이터

최종 사용자용 `generatedImageSamples[id]` 항목에는 다음 필드를 추가한다.

```js
{
  gallerySlot: 1,
  galleryRole: "representative",
  phenotype: "canonical-a",
  habitatKey: "formation-or-biome-key",
  kind: "count-level pass",
  title: "...",
  body: "...",
  source: "assets/dinosaurs/...png",
  src: "assets/dinosaurs/...png",
}
```

규칙:

- 한 종에서 같은 `gallerySlot`을 두 이미지가 차지하면 안 된다.
- `gallerySlot`은 1부터 `imageSlots`까지만 허용한다.
- 최종 갤러리는 `gallerySlot`이 지정된 항목만 슬롯 순서대로 보여준다.
- 초과 후보, 탈락 근거, 검수 시트는 `gallerySlot`을 주지 않고 검수 페이지에만 남긴다.
- 슬롯 1은 정확히 한 장만 활성 대표로 둔다. 이전 대표 후보는 `review hold` 또는 내부 검수 항목으로 내린다.
- `getGalleryItems()`는 모든 종에 빈 계획 카드 4개를 무조건 붙이지 않는다. 실제 미배정 슬롯만 역할명이 있는 플레이스홀더로 표시하고, 완료된 종에는 빈 카드가 없어야 한다.
- 후보만/대표/참고 탭에서 이미지를 확대했을 때 이전·다음 이동은 현재 카테고리 안에서만 유지한다.

## 3. 생성 계획 파일

이미지를 생성하기 전에 `tools/comfyui/outputs/gallery-slot-generation-plan.json`과 같은 내용의 Markdown 요약을 만든다.

각 종의 계획에는 최소한 다음 정보가 있어야 한다.

```json
{
  "taxon": "species-id",
  "imageSlots": 5,
  "paletteLock": {
    "swatches": ["#...", "#...", "#...", "#..."],
    "canonicalColor": "visualVariationProfiles.color",
    "patternTopology": "visualVariationProfiles.pattern",
    "surface": "visualVariationProfiles.texture",
    "allowedVariant": "slot 2 only",
    "avoid": "visualVariationProfiles.avoid"
  },
  "habitatProfile": {
    "period": "...",
    "region": "...",
    "formationOrBiome": "...",
    "substrate": "...",
    "vegetation": "...",
    "moisture": "...",
    "light": "...",
    "backgroundPalette": ["#...", "#...", "#..."]
  },
  "slots": [
    {
      "slot": 1,
      "role": "representative",
      "status": "reuse | generate | manual-review",
      "currentSource": "assets/dinosaurs/...png",
      "referenceSource": "assets/dinosaurs/...png",
      "prompt": "...",
      "negativePrompt": "...",
      "passGate": ["..."],
      "rejectGate": ["..."]
    }
  ]
}
```

계획을 만든 뒤에는 `reuse` 대상부터 원본 크기로 확인한다. 파일명과 설명만 보고 슬롯을 채우지 않는다.

## 4. 종별 팔레트 잠금

각 종의 슬롯 1을 `canonical-a` 개체로 본다. 슬롯 3~7은 가능하면 대표 이미지를 참조 이미지로 사용해 같은 개체의 색과 무늬 배치를 유지한다.

팔레트 우선순위:

1. `taxonPaletteSwatches[id]`의 4색
2. `visualVariationProfiles[id].color`
3. `visualVariationProfiles[id].pattern`
4. `visualVariationProfiles[id].texture`
5. `generationRouteGuides[id].pass`와 `reject`

색상 규칙:

- 슬롯 1, 3, 4, 5, 6, 7은 같은 기본 몸색, 배색 위치, 얼굴 포인트, 꼬리 무늬 토폴로지를 유지한다.
- 슬롯 2만 승인된 두 번째 표현형 `variant-b`를 허용한다. 색상 이동은 기존 4색 스와치 또는 프로필에 명시된 대체색 안에서 제한하고, 무늬가 찍히는 위치와 크기는 같은 종으로 읽히게 유지한다.
- 서식지 때문에 몸 전체가 갈색·초록색·파란색 필터로 덮이지 않게 한다.
- 흙먼지, 진흙, 물기, 수초 그림자는 발과 하부 몸통에 국소적으로만 적용한다.
- 시간대 조명은 배경과 외곽광에 주로 적용하고, 몸의 기준색을 알아볼 수 있게 중성광을 남긴다.
- 인접한 계통의 공룡이 모두 갈색 몸+점박이 옆구리+고리 꼬리 조합으로 수렴하지 않게 한다.
- 배경과 동물 사이에는 썸네일에서도 실루엣이 읽히는 명도·색상 대비를 확보한다.

4색 스와치가 없는 네 종은 생성 전에 프로필에 맞는 고유 스와치를 추가한다. 시작 후보는 다음과 같으며, 인접 분류군과 중복되면 조정한다.

- `wannanosaurus-yansiensis`: blackberry, olive, lime shoulder fleck, cream belly
- `alaskacephale-gangloffi`: midnight blue-gray, copper flank panel, frost belly, dark tail tip
- `sphaerotholus-goodwini`: cobalt body, opal dome, warm sand belly, muted dark accent
- `acrotholus-audeti`: bottle green, ivory dome, dark fern bar, muted earth underside

## 5. 서식지 색 적용

서식지는 `period`, `region`, 종 설명, `generationRouteGuides.focus/pass`, 기존 생태 이미지명과 지층 정보를 함께 사용해 정한다. 지역명만으로 현대 풍경을 복사하지 않는다.

| 서식지 | 배경 방향 | 동물 색 보정 | 피할 것 |
|---|---|---|---|
| 건조 적색층·반건조 범람원 | 산화철 적갈색, 회녹색 관목, 옅은 먼지 | 차가운 청회색·차콜 또는 올리브 기준색을 유지하고 따뜻한 포인트만 허용 | 전신 주황색 필터, 현대 사막 도마뱀 복제 |
| 침엽수·양치식물 범람원 | 짙은 녹색, 젖은 갈색, 회청색 물그림자 | 프로필의 올리브·차콜·크림을 유지하고 얼룩무늬 대비를 약간 높임 | 몸과 배경이 모두 같은 녹색, 현대 잔디밭 |
| 해안·석호·갯벌 | 청회색 물, 황토 퇴적층, 탁한 녹색 식생 | 옅은 배색과 젖은 피부 반사를 허용하되 몸의 기준색을 유지 | 전신 파란색 수중 필터, 현대 열대 해변 |
| 고위도·극지 숲 | 낮은 채도의 청회색, 짙은 침엽수, 서리빛 지면 | 차콜·구리·크림 등 프로필 대비를 유지하고 몸 전체 백색화 금지 | 북극곰식 순백색 자동 적용 |
| 고비형 사구·건조 관목지 | 옅은 모래, 회갈색 암석, 드문 회녹색 식생 | 프로필의 자주·청록·황토 포인트를 살리고 그림자 쪽만 저채도화 | 모든 종을 모래색으로 통일 |
| 해양 | 어두운 등과 밝은 배의 카운터셰이딩, 탁한 청록·회청색 물 | 프로필에 있는 반점·띠만 유지하고 수면광은 외곽에 적용 | 돌고래·상어·현대 바다도마뱀 해부학 드리프트 |

트라이아스기·쥐라기 장면은 현대 꽃밭과 잔디 평원을 기본값으로 쓰지 않는다. 백악기 속씨식물도 해당 지층과 지역 맥락이 없으면 과장하지 않는다. 배경은 교육적으로 그럴듯해야 하지만, 동물 해부학을 가리거나 흐리게 만들 정도로 복잡하면 안 된다.

## 6. 슬롯별 생성 프롬프트 템플릿

아래 템플릿에 해당 종의 실제 데이터를 채운다. 대괄호를 남긴 채 생성하지 않는다.

```text
USE CASE: scientific-educational dinosaur atlas gallery image
SLOT: [slot number] / [gallery role]
TAXON: [scientific name], [period], [region or formation]

IDENTITY LOCK:
[identityChecklists entries]
[visualVariationProfiles.anatomy]

CANONICAL PHENOTYPE LOCK:
Use the same individual identity as [slot 1 reference path].
Preserve these four palette anchors: [taxonPaletteSwatches].
Preserve body base color: [visualVariationProfiles.color].
Preserve marking topology and placement: [visualVariationProfiles.pattern].
Preserve surface material: [visualVariationProfiles.texture].
Only slot 2 may use the approved variant-b palette; all other slots use canonical-a.

HABITAT:
[formation or plausible biome], [substrate], [vegetation], [moisture], [time-neutral natural light].
Use habitat color in the background and localized dust, mud, moisture, or reflected light without replacing the animal's canonical body colors.

COMPOSITION:
[slot-specific action and camera angle].
Keep the primary taxon readable at thumbnail scale.
For a full-body slot, show the complete animal from snout to tail tip with every required limb and foot visible.
For an interaction slot, keep the animals spatially separated enough to count limbs and identify both taxa.

SCIENTIFIC AND DISPLAY CONSTRAINTS:
realistic natural-history reconstruction, landscape composition, no text, no label, no watermark, no split panel, no modern animal substitution, no fantasy anatomy, no excessive blood.
```

공통 네거티브 프롬프트:

```text
extra legs, six limbs, duplicated limbs, fused limbs, missing legs, hidden feet, extra fingers, missing fingers, detached claws, cropped tail, forked tail, malformed skull, wrong crest, wrong horn count, wrong plate count, wrong tail weapon, modern bird head, rhinoceros head, monitor lizard body, crocodile body, fantasy spikes, generic dragon, identical brown spotted skin across taxa, ringed tail by default, global color cast, text, logo, watermark, infographic, contact sheet, split image, excessive blood, exposed organs
```

여기에 반드시 `visualVariationProfiles[id].avoid`와 `generationRouteGuides[id].reject`를 추가한다.

## 7. 일관성 생성 경로

- 슬롯 1이 이미 통과한 종은 그것을 모든 후속 슬롯의 주 참조 이미지로 사용한다.
- `imagegen`을 사용할 때는 가능한 한 대표 이미지 파일을 참조 이미지로 전달하고, 프롬프트에 같은 개체·같은 무늬 위치를 명시한다.
- ComfyUI를 사용할 때는 현재 종의 `generationRouteGuides.control`을 우선하고, 대표 이미지를 색·재질 참조로 함께 사용한다.
- 색상·서식지 변형은 낮은 변화량부터 시작한다. 권장 탐색 범위는 img2img denoise 0.28~0.45, 색·참조 조건 0.60~0.80, 구조 제어 0.45~0.70이다. 종별 route가 더 엄격한 값을 지정하면 route를 우선한다.
- 새로운 행동 포즈는 denoise를 높이기 전에 ControlNet 또는 포즈/실루엣 가이드를 사용한다.
- 손·발·꼬리 무기·볏 같은 국소 오류는 전신 재생성보다 저노이즈 인페인트를 우선한다.
- 한 슬롯당 처음에는 2~3개 후보만 만든다. 해부학이 틀린 상태에서 색만 바꾼 대량 변형을 만들지 않는다.

## 8. 실행 순서

1. 현재 `app.js`와 실제 자산을 감사해 132종 x 슬롯 계획을 만든다.
2. `generatedImageSamples`의 두 문자열 항목을 이미지 목록에서 제거하고 해당 문장은 체크리스트/route의 해부학 메모로 보존한다.
3. Hanssuesia의 `mask-pattern` 오탐을 수정한다. 실제 편집용 `*-mask-vN.png`는 계속 내부 항목으로 숨긴다.
4. 누락된 identity checklist 2개와 스와치 4세트를 먼저 보완한다.
5. 현재 786개 사용자 노출 후보를 원본으로 확인하고, 각 종의 1~N 슬롯에 최종 472장을 배정한다.
6. 41종의 초과 이미지 319장은 삭제하지 않는다. 슬롯을 주지 않고 검수/비교 후보로 남긴다.
7. 기존 이미지로 역할이 충족되지 않는 슬롯만 `generate` 상태로 둔다.
8. `generate` 슬롯을 한 종씩 처리한다. 한 종의 모든 슬롯 검증이 끝난 뒤 다음 종으로 이동한다.
9. 선택된 새 이미지만 `assets/dinosaurs/`에 복사하고 종 접두사, 특징, 역할, 버전을 포함한 이름을 사용한다.
10. `app.js`의 `generatedImageSamples`, 필요 시 `identityChecklists`, `visualVariationProfiles`, `generationRouteGuides`, 스와치와 캐시 키를 같은 패스에서 갱신한다.
11. `tools/comfyui/dino-recursive-expansion-queue.md`에 슬롯별 재사용·생성·탈락 결과를 기록한다.
12. 각 종을 검증하고 단계별 커밋을 만든다.

## 9. 육안 통과 게이트

모든 최종 슬롯 이미지는 원본 크기에서 다음을 통과해야 한다.

- 종 고유 머리 형태, 볏·뿔·프릴·갑옷·골판·꼬리 무기 수와 배치
- 정확한 팔다리 수
- 손가락과 발가락이 중요한 종은 필요한 수와 방향
- 머리부터 꼬리 끝까지 잘리지 않은 실루엣
- 대표 이미지와 동일한 canonical-a 몸색 및 무늬 위치, 또는 슬롯 2의 명시적 variant-b
- 서식지에 맞는 배경과 국소 색 반응
- 배경과 동물의 썸네일 판독성
- 다중 개체 장면에서 종 혼합, 팔다리 융합, 먹이·포식자 역할 반전이 없음
- 과도한 유혈, 현대 동물 복제, 판타지 장식, 텍스트·워터마크가 없음

특히 다음 기존 사용자 지적을 하드 게이트로 유지한다.

- Ankylosaurus: 짧고 넓은 장갑 머리, 머리 골갑과 뺨뿔, 낮고 넓은 몸, 정확히 네 다리, 하나의 연결된 꼬리 곤봉
- Triceratops: 코뿔소 몸이 아니라 각룡류 두개골과 연결된 프릴, 두 눈썹뿔과 하나의 코뿔, 정확히 네 다리
- Velociraptor: 현대 새 머리 금지, 이빨 있는 좁은 주둥이, 정확히 두 뒷다리, 각 발의 연결된 둘째 발가락 낫발톱
- Stegosaurus: 피부와 다른 색·질감의 두 줄 교대 골판, 정확히 네 다리, 좌우 두 개씩 총 네 꼬리가시, 지면 기준 위로 솟는 V 방향
- Brachiosaurus: 높은 어깨와 긴 앞다리, 짧은 뒷다리, 둥근 정수리 비강 융기와 높은 콧구멍 단서

## 10. 검증과 커밋

각 단계 후 다음을 실행한다.

- `node --check app.js`
- 모든 실제 `assets/dinosaurs/...` 참조의 파일 존재 확인, 누락 0건
- 슬롯 계획의 중복 `gallerySlot` 0건
- 모든 종에서 슬롯 번호가 1부터 `imageSlots`까지 정확히 한 번씩 존재
- 슬롯 1 대표가 정확히 한 장이고, 다중 개체 장면이 대표가 아님
- 슬롯 2 외에는 canonical-a 팔레트와 무늬 토폴로지 유지
- 로컬 서버 자산 HTTP 200
- 카드, 상세 갤러리, 검수 탭 이미지의 0이 아닌 렌더 크기
- 후보만/대표/참고 확대 탐색이 현재 카테고리에 한정됨
- 데스크톱과 모바일에서 이미지·텍스트·계통도 겹침 없음
- `git diff --check`

커밋은 이번 작업 파일만 경로 지정해 다음 단위로 나눈다.

1. 슬롯 감사·계획 파일·데이터 정리
2. 팔레트 잠금·서식지 프로필·앱 슬롯 렌더링
3. 종별 10~20개 슬롯 완료 단위
4. 최종 132종 슬롯 검증과 문서 정리

기존 작업 트리의 다른 변경은 되돌리거나 함께 커밋하지 않는다. Git 잠금이나 권한 오류가 나면 이미지·앱 작업을 되돌리지 말고 오류를 기록한 뒤 검증을 계속한다.

## 완료 조건

다음을 모두 만족하기 전에는 goal을 완료로 표시하지 않는다.

- 최신 등록 종 전체의 슬롯 수 합계와 최종 `gallerySlot` 이미지 수가 일치
- 모든 종에서 `gallerySlot` 1부터 `imageSlots`까지 중복·누락 없이 존재
- 모든 슬롯 이미지 파일이 실제로 존재하고 앱과 로컬 서버에서 렌더링됨
- 각 종의 슬롯 1, 3~N은 canonical-a 색·무늬·질감을 유지하고 슬롯 2만 승인된 variant-b를 사용
- 모든 이미지가 종별 anatomy/avoid/pass/reject 게이트를 통과
- 서식지 색이 배경과 국소 반응에 적용되고 전신 단색 필터로 종 고유색을 지우지 않음
- 초과 후보는 삭제 없이 검수 페이지에 남고 최종 갤러리에는 슬롯 수만큼만 표시
- 2개 누락 identity checklist, 4개 누락 스와치, 2개 문자열 샘플, Hanssuesia mask 오탐이 해결됨
- 카테고리별 확대 탐색, 데스크톱·모바일 레이아웃, 문법·경로·HTTP 검증 통과

최종 보고에는 재사용 슬롯 수, 새 생성 슬롯 수, 인페인트 수정 수, 탈락 후보 수와 주요 이유, 종별 팔레트 잠금 위반 수정 수, 남은 수동 검수 항목, 검증 결과와 커밋 해시를 정리한다.
