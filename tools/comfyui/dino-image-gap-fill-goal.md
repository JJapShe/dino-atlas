# Dino Atlas 이미지 빈칸 채우기 CLI Goal Prompt

이 문서 전체를 `C:\Users\USER\Documents\dinosour`에서 실행하는 Codex CLI의 goal objective로 사용한다.

## Goal

Dino Atlas에 이미 등록된 공룡들의 사용자 갤러리를 감사하고, 실제 이미지 슬롯 부족만 선별해 해부학적으로 신뢰할 수 있는 이미지로 채운다. 기존 프로젝트 자산을 먼저 재검수해 재사용하고, 적합한 자산이 없을 때만 `imagegen` 또는 현재 ComfyUI 생성 경로로 새 이미지를 만든다. 생성·선별된 자산을 `assets/dinosaurs/`와 `app.js`에 반영하고, 잘못된 빈칸 표시와 후보 숨김 규칙도 함께 고쳐서 모든 등록 종의 갤러리가 실제 상태와 일치하게 한다.

이 작업에서는 반드시 프로젝트 스킬 `dino-atlas-gallery-workflow`를 사용한다. 새 비트맵을 만들 때는 `imagegen` 스킬을 사용하고, 선택된 결과만 `.codex/generated_images`에서 `assets/dinosaurs/`로 복사한다. `.codex/generated_images` 경로를 앱에서 직접 참조하지 않는다.

사용자가 중지하라고 하기 전에는 아래 작업을 종별로 반복한다. 단, 이미 완성된 종을 다시 생성해서 작업량을 부풀리지 않는다.

## 2026-07-13 기준 현재 상태

실행 첫 단계에서 아래 수치를 다시 감사하고, 코드가 바뀌었다면 최신 감사 결과를 기준으로 큐를 갱신한다.

- `dinosaurs`: 132종
- `generatedImageSamples`: 132종
- `visualVariationProfiles`: 132종
- `generationRouteGuides`: 132종
- `identityChecklists`: 130종
- 현재 `app.js`가 참조하는 실제 이미지 경로 누락: 0건
- 모든 종에 최소 한 개 이상의 실제 등록 이미지가 있으므로 132종 전체를 새로 생성하면 안 된다.
- 사용자에게 보이는 실제 이미지 수가 `imageSlots`보다 부족한 진짜 수량 부족은 4종, 각 1장이다.
- `Herrerasaurus ischigualastensis`는 실제 이미지가 충분하지만 `count-level pass` 대표가 0장이다.
- `getGalleryItems()`가 모든 종에 `src` 없는 생성 예정 카드 4개를 무조건 추가하므로 총 528개의 가짜 빈칸이 보인다. 이미지 생성만으로는 이 빈칸이 사라지지 않는다.
- `Hanssuesia sternbergi`의 정상 색상 변형 파일은 이름의 `mask` 때문에 `isInternalReviewCandidate()`에서 내부 마스크로 오인되어 숨겨진다. 이 종은 새 이미지 부족이 아니다.
- 28종은 `anatomy review` 또는 사용자용 참고 역할이 없지만 모두 생태 이미지 자체는 이미 있다. 수량이 충분한 24종은 새 생성보다 기존 생태 이미지의 육안 검수와 역할 정리가 우선이다.

## 빈칸 판정 규칙

다음 조건을 모두 적용해 감사 결과를 만든다.

1. 사용자 갤러리에 실제로 노출되는 `src`가 있고 파일이 존재하는 항목만 실제 이미지로 센다.
2. `diagnostic only`, `reject reference`, `internalOnly`, 퇴역 소스, 검수 시트, 크롭, 마스크, 가이드, 매니페스트는 사용자 이미지 수에서 제외한다.
3. `max(0, dino.imageSlots - userVisibleRealImages.length)`만 실제 수량 부족으로 센다.
4. 대표 역할은 `count-level pass` 1장, 색상·무늬 변형은 `review hold` 1장, 생태·해부 참고는 `anatomy review` 1장을 기본 계약으로 본다.
5. 다중 개체, 포식, 추격, 물보라, 먼지, 가림이 있는 장면은 대표로 자동 승격하지 않고 `anatomy review`로 둔다.
6. 기존 미등록 파일이 해부학·구도·저작권 조건을 통과하면 그것을 먼저 등록하고 새로 생성하지 않는다.
7. 파일명이나 등록 상태만 보고 통과시키지 않는다. 원본 해상도로 직접 보고 머리, 팔다리 수, 손가락·발가락, 꼬리 끝을 각각 크롭 검수한다.

감사 결과는 재실행 가능한 스크립트 또는 명확한 명령으로 남기고 `tools/comfyui/outputs/gallery-image-gap-audit.json`에 저장한다. 최소 필드는 `taxon`, `imageSlots`, `visibleRealCount`, `deficit`, `representativeCount`, `variantCount`, `anatomyReviewCount`, `missingPaths`, `unregisteredSpeciesAssets`이다.

## 우선순위 큐

### P0. 가짜 빈칸과 숨김 버그 수정

- `getGalleryItems(dino)`에서 실제 이미지 뒤에 생성 예정 카드 4개를 무조건 붙이지 않는다.
- 실제 부족 수량만큼만 계획 카드를 만들거나, 생성 작업이 끝난 뒤 부족 수량이 0이면 계획 카드를 전혀 렌더링하지 않는다.
- 상세 갤러리의 카운터와 점도 실제 노출 이미지 수를 기준으로 맞춘다.
- `isInternalReviewCandidate()`의 광범위한 `mask` 매칭을 고쳐 `hanssuesia-sternbergi-indigo-ochre-mask-pattern-imagegen-v2.png` 같은 정상적인 face-mask pattern 이미지를 숨기지 않게 한다.
- 실제 편집용 `*-mask-vN.png`, 검수 시트, 크롭, 가이드 파일은 계속 숨겨야 한다. `mask-pattern`은 사용자 이미지로 허용하고 단순 문자열 포함만으로 숨기지 않는다.
- 후보만/대표/참고 탭에서 연 확대 이미지의 이전·다음 이동 범위가 현재 카테고리 안에만 머무는 기존 동작을 보존한다.

### P1. 진짜 수량 부족 4종

각 종은 현재 사용자 노출 이미지가 4장이고 `imageSlots`가 5이므로 1장만 추가한다. 우선 아래 미등록 자산을 원본으로 직접 검사한다. 통과 자산이 있으면 `anatomy review`로 등록하고 생성하지 않는다. 모두 탈락할 때만 해당 종의 생성 프롬프트로 2~3개 후보를 만들고 가장 좋은 1장만 프로젝트 자산으로 복사한다.

1. `riojasaurus-incertus`
   - 미등록 검사 후보:
     - `assets/dinosaurs/riojasaurus-incertus-storm-slope-blueblack-lime-ladder-ecology-imagegen-v1.png`
     - `assets/dinosaurs/riojasaurus-incertus-zupaysaurus-juvenile-shield-defense-ecology-imagegen-v1.png`
     - `assets/dinosaurs/riojasaurus-incertus-zupaysaurus-tail-guard-defense-ecology-imagegen-v1.png`
   - 통과 핵심: 깊고 튼튼한 몸, 앞으로 뻗은 긴 목, 작은 초식 머리, 네 발 접지, 앞다리가 뒷다리보다 짧지만 체중을 지탱함, 길고 두꺼운 꼬리.
   - 탈락: 작은 이족보행 몸, 후기 기둥다리 용각류, 수직 기린목, 수각류 이빨, 숨은 발, 여분 다리, 잘린 꼬리.

2. `dracovenator-regenti`
   - 미등록 검사 후보:
     - `assets/dinosaurs/dracovenator-regenti-aardonyx-arroyo-bite-pressure-ecology-imagegen-v1.png`
     - `assets/dinosaurs/dracovenator-regenti-aardonyx-redbed-carcass-feeding-ecology-imagegen-v1.png`
     - `assets/dinosaurs/dracovenator-regenti-heterodontosaurus-attack-ecology-imagegen-v1.png`
     - `assets/dinosaurs/dracovenator-regenti-heterodontosaurus-sandstone-gully-bite-ecology-imagegen-v1.png`
     - `assets/dinosaurs/dracovenator-regenti-massospondylus-fern-gully-carcass-feeding-ecology-imagegen-v1.png`
     - `assets/dinosaurs/dracovenator-regenti-massospondylus-wet-gully-bite-ecology-imagegen-v1.png`
   - 통과 핵심: 길고 낮고 좁은 머리, 은은한 낮은 볏/능선, 중간보다 긴 세 손가락 앞다리, 정확히 두 뒷다리, 세 발가락 접지 발, 긴 균형 꼬리.
   - 탈락: 딜로포사우루스식 높은 쌍 부채 볏, 영화식 목주름, 케라토사우루스 코뿔, 티라노사우루스식 작은 팔, 낫발톱, 여분 팔다리, 과한 유혈.

3. `monolophosaurus-jiangi`
   - 미등록 검사 후보:
     - `assets/dinosaurs/monolophosaurus-jiangi-bellusaurus-moonlit-reedbend-ambush-ecology-imagegen-v2.png`
     - `assets/dinosaurs/monolophosaurus-jiangi-bellusaurus-open-pursuit-ecology-imagegen-v1.png`
     - `assets/dinosaurs/monolophosaurus-jiangi-bellusaurus-reed-ambush-ecology-imagegen-v1.png`
   - 통과 핵심: 정중선 하나의 머리 볏, 길고 낮은 두개골, 중간 크기 세 손가락 앞다리, 정확히 두 뒷다리, 보이는 세 발가락 발, 긴 균형 꼬리.
   - 탈락: 쌍으로 갈라진 딜로포사우루스 볏, 코뿔 하나로 축소된 케라토사우루스 머리, 알로사우루스식 무거운 눈두덩과 체구, 작은 티라노사우루스 팔, 여분 팔다리, 잘린 꼬리.

4. `cetiosaurus-oxoniensis`
   - 미등록 검사 후보:
     - `assets/dinosaurs/cetiosaurus-oxoniensis-megalosaurus-bite-repel-defense-ecology-imagegen-v1.png`
     - `assets/dinosaurs/cetiosaurus-oxoniensis-megalosaurus-quarry-tail-barrier-defense-ecology-imagegen-v1.png`
     - `assets/dinosaurs/cetiosaurus-oxoniensis-megalosaurus-tail-guard-defense-ecology-imagegen-v1.png`
   - 통과 핵심: 크고 튼튼한 초기 용각류, 중간 길이의 두껍고 앞으로 향한 목, 작은 초식 머리, 깊은 몸통, 네 발 접지와 보이는 발, 낮게 유지되는 길고 무거운 꼬리.
   - 탈락: 브라키오사우루스식 높은 어깨와 기린 자세, 디플로도쿠스식 초장형 채찍 꼬리, 카마라사우루스식 각진 머리, 티타노사우루스 갑옷, 이족보행, 여분 다리, 잘린 꼬리.

### P2. 대표가 없는 Herrerasaurus

- 대상: `herrerasaurus-ischigualastensis`
- 현재 실제 이미지와 참고 자료는 충분하지만 `count-level pass`가 0장이다.
- 기존 `imagegen-v4`, `imagegen-v6`, `balancedhands-imagegen-v2`를 원본 및 머리·손·발·꼬리 크롭으로 다시 확인한다.
- 기존 후보가 모두 대표 기준을 만족하지 못하면 `assets/dinosaurs/herrerasaurus-ischigualastensis-bodylock-guide-v1.png`와 현재 route/profile을 기준으로 새 전신 후보 2~3장을 생성한다.
- 대표 통과 핵심: 가늘고 긴 초기 공룡 몸, 길고 낮은 머리, 티라노사우루스보다 긴 두 앞다리, 각 손에 세 주요 손가락, 정확히 두 뒷다리, 보이는 발, 잘리지 않은 긴 꼬리.
- 탈락: 티라노사우루스식 작은 팔, 네발 자세, 악어·왕도마뱀 같은 몸, 여분 팔다리·손가락, 가려진 손, 잘린 꼬리.
- 색상은 흙빛 붉은색과 차콜 갈색, 낮은 채도의 크림색 배를 사용하고 끊어진 옆구리·꼬리 띠를 허용한다.
- 새 후보를 이름만으로 자동 대표 승격하지 않는다. 모든 해부학 조건을 직접 통과한 한 장만 `count-level pass`로 등록하고 나머지는 `review hold` 또는 미등록으로 둔다.

### P3. 생성 없이 역할과 메타데이터 정리

- 다음 24종은 이미지 수가 이미 충분하고 생태 이미지도 있으므로 새로 생성하지 않는다. 가장 판독성이 좋은 기존 생태 이미지 한 장을 직접 확인한 뒤, 다중 개체/행동 참고 성격에 맞게 `anatomy review`로 정리한다.

`eodromaeus-murphi`, `eoraptor-lunensis`, `zupaysaurus-rougieri`, `liliensternus-liliensterni`, `lessemsaurus-sauropoides`, `chromogisaurus-novasi`, `panphagia-protos`, `buriolestes-schultzi`, `bagualosaurus-agudoensis`, `saturnalia-tupiniquim`, `thecodontosaurus-antiquus`, `efraasia-minor`, `pisanosaurus-mertii`, `heterodontosaurus-tucki`, `marshosaurus-bicentesimus`, `megalosaurus-bucklandii`, `ornitholestes-hermanni`, `bellusaurus-sui`, `rhamphorhynchus-muensteri`, `pterodactylus-antiquus`, `dimorphodon-macronyx`, `ichthyosaurus-communis`, `plesiosaurus-dolichodeirus`, `othnielosaurus-consors`.

- `ceratosaurus-nasicornis`와 `scutellosaurus-lawleri`에는 현재 profile/route는 있으나 `identityChecklists`가 없다. 기존 대표 이미지, 프로필, route의 핵심 해부학 조건과 탈락 조건을 사용해 체크리스트를 추가한다. 이 두 종은 이미지 생성 대상이 아니다.

## 새 이미지 생성 공통 프롬프트

새 생성이 필요한 경우 아래 공통 문장을 사용하고 각 종별 핵심 문장을 뒤에 붙인다. 사용자 갤러리용 결과에는 글자, 화살표, 분할 패널, 라벨, 워터마크를 넣지 않는다.

```text
scientific-educational dinosaur atlas gallery image, one clearly readable named taxon, period-appropriate habitat, landscape composition, complete full body visible from snout to tail tip, every limb and grounded foot readable, realistic natural history reconstruction, restrained species-specific color and pattern, natural daylight, enough negative space around the extremities, no text, no labels, no watermark, no split panel, no fantasy anatomy
```

종별 추가 프롬프트:

```text
Herrerasaurus ischigualastensis, Late Triassic Ischigualasto setting, slender early saurischian body, long low skull, two proportionally long forelimbs, three main clawed fingers on each hand, exactly two powerful hind legs, long balancing tail, earthy rust and charcoal body with a muted cream underside and broken flank bands

Riojasaurus incertus, Late Triassic Los Colorados setting, large robust basal sauropodomorph, deep torso, small herbivorous head on a long forward-reaching neck, stable quadrupedal stance, shorter weight-bearing forelimbs, exactly four grounded legs with visible feet, long thick tail, blue-gray or moss-olive hide with sienna flank accents

Dracovenator regenti, Early Jurassic Upper Elliot setting, slender medium theropod, long low narrow skull with only a subtle low cranial ridge, medium-long three-fingered arms, exactly two hind legs, visible three-toed feet, complete balancing tail, charcoal slate and warm ochre pattern

Monolophosaurus jiangi, Middle Jurassic Shishugou setting, slender medium theropod, one single midline cranial crest, long low skull, medium three-fingered forelimbs, exactly two hind legs, visible three-toed feet, complete balancing tail, saffron and slate species pattern

Cetiosaurus oxoniensis, Middle Jurassic Oxfordshire setting, robust early sauropod, small herbivorous head, moderately long thick neck carried forward, deep body, level shoulders, exactly four sturdy grounded legs with visible feet, long heavy tapering tail carried low, blue-gray and muted copper pattern
```

공통 네거티브 프롬프트:

```text
extra legs, six limbs, duplicated limbs, missing limbs, fused feet, hidden feet, extra fingers, detached claws, cropped tail, forked tail, modern animal head, generic monitor lizard, crocodile body, fantasy spikes, oversized horns, incorrect crest, text, logo, watermark, infographic, contact sheet, split image, excessive blood, exposed organs
```

각 종의 `visualVariationProfiles[id].avoid`와 `generationRouteGuides[id].reject`를 공통 네거티브 뒤에 반드시 추가한다.

## 종별 처리 루프

1. `app.js`의 해당 `dinosaurs[]`, `generatedImageSamples`, `identityChecklists`, `visualVariationProfiles`, `generationRouteGuides`를 읽는다.
2. 같은 종 접두사의 등록·미등록 자산을 모두 나열한다.
3. 기존 미등록 자산을 원본 크기로 보고 머리, 앞다리/손, 뒷다리/발, 꼬리, 종 고유 구조를 각각 확인한다.
4. 통과 자산이 있으면 새 생성 없이 안정적인 종 접두사 파일명을 유지해 등록한다.
5. 통과 자산이 없으면 종별 프롬프트로 2~3개만 생성한다. 한 번에 많은 종을 병렬 생성하지 않는다.
6. 선택 결과만 `assets/dinosaurs/`에 복사하고 `<species-id>-<specific-cue>-imagegen-vN.png` 또는 `<species-id>-<specific-cue>-ecology-imagegen-vN.png`로 이름을 붙인다. 기존 파일을 덮어쓰지 않는다.
7. 새 사용자용 참고 이미지는 `anatomy review`, 색상 변형은 `review hold`, 엄격히 통과한 대표만 `count-level pass`로 등록한다.
8. `app.js`의 제목·설명에 실제로 확인한 특징과 남은 위험을 기록한다. 파일명만 보고 설명을 만들지 않는다.
9. 필요하면 `visualVariationProfiles`와 `generationRouteGuides`의 누락된 avoid/pass 조건을 함께 보강한다.
10. `tools/comfyui/dino-recursive-expansion-queue.md`에 종별 결과, 사용/탈락 파일, 검수 이유를 짧게 남긴다.
11. 브라우저 자산이나 `app.js`가 바뀌면 `index.html`의 캐시 키를 한 번 갱신한다.
12. 한 종을 검증까지 끝낸 뒤 다음 종으로 이동한다.

## 검증

각 종 처리 후와 최종 완료 전에 다음을 모두 수행한다.

- `node --check app.js`
- `app.js`의 모든 실제 `assets/dinosaurs/...` 참조를 검사하고 누락 0건 확인
- 새 이미지의 파일 존재와 0이 아닌 크기 확인
- 로컬 서버가 있으면 새 자산 HTTP 200 확인
- 대상 공룡 카드의 대표 이미지가 0이 아닌 크기로 렌더링되는지 확인
- 상세 갤러리의 실제 이미지 수가 `imageSlots` 이상인지 확인
- 후보만/대표/참고 탭의 항목 수와 확대 이전·다음 이동 범위 확인
- 대표 카드가 `count-level pass`를 사용하고 다중 개체 장면을 대표로 잘못 사용하지 않는지 확인
- 대상 종의 머리, 팔다리 수, 손가락/발가락, 꼬리 끝을 원본 또는 확대 화면으로 재확인
- 데스크톱과 모바일에서 이미지, 텍스트, 계통도 노드 겹침이 없는지 확인
- `git diff --check`

## 단계별 커밋

현재 작업 트리에 기존 변경이 많을 수 있으므로 다른 변경을 되돌리거나 함께 커밋하지 않는다. 이번 작업 파일만 경로 지정해서 스테이징한다.

- 커밋 1: 감사 스크립트/감사 JSON, 가짜 빈칸 렌더링 수정, Hanssuesia mask 오탐 수정
- 커밋 2: 진짜 수량 부족 4종의 재사용 또는 생성 이미지와 앱 등록
- 커밋 3: Herrerasaurus 대표 후보와 대표 게이트 반영
- 커밋 4: 24종 역할 정리, 2종 identity checklist, 최종 검증 및 큐 문서

Git 인덱스 잠금 또는 권한 오류가 나면 작업을 되돌리지 말고 오류를 정확히 기록한 뒤 검증을 계속한다.

## 완료 조건

아래를 모두 충족하기 전에는 goal을 완료로 표시하지 않는다.

- 최신 감사에서 등록 132종 모두 `visibleRealCount >= imageSlots`
- 모든 종에 실제 사용자용 이미지가 있고 누락 경로 0건
- `Herrerasaurus ischigualastensis`에 직접 검수된 `count-level pass` 대표 1장 이상
- 모든 종에 대표, 색상/무늬 변형, 생태/해부 참고 역할이 각각 최소 1장
- `ceratosaurus-nasicornis`, `scutellosaurus-lawleri` identity checklist 존재
- Hanssuesia의 정상 mask-pattern 변형이 사용자 갤러리와 검수 탭에서 보임
- 완성된 종에 `src` 없는 가짜 계획 카드가 남지 않음
- 카테고리별 확대 탐색 범위가 유지됨
- `app.js` 문법, 실제 경로, HTTP, 브라우저 데스크톱/모바일 검증 통과
- 각 단계의 변경과 검증 결과가 큐 문서 및 가능한 범위의 분리 커밋으로 남음

최종 보고에는 생성한 이미지 수, 재사용한 기존 이미지 수, 생성하지 않고 역할만 정리한 종 수, 탈락 후보와 이유, 남은 수동 검수 항목, 검증 결과, 커밋 해시를 간결하게 정리한다.
