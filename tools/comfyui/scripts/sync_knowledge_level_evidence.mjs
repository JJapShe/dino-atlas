import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const EVIDENCE_JSON = path.join(ROOT, "docs", "knowledge-level-evidence-2026-08-03.json");
const EVIDENCE_MARKDOWN = path.join(ROOT, "docs", "knowledge-level-evidence-2026-08-03.md");
const AUDIT_MARKDOWN = path.join(ROOT, "docs", "knowledge-level-audit-2026-08-03.md");

function extractLiteral(source, name) {
  const marker = `const ${name} =`;
  const markerAt = source.indexOf(marker);
  if (markerAt < 0) throw new Error(`Missing declaration: ${name}`);

  let start = markerAt + marker.length;
  while (/\s/.test(source[start])) start += 1;
  while (source[start] !== "[" && source[start] !== "{") start += 1;

  const open = source[start];
  const close = open === "[" ? "]" : "}";
  let depth = 0;
  let quote = "";
  let escaped = false;

  for (let index = start; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === '"' || char === "'" || char === "`") {
      quote = char;
      continue;
    }
    if (char === open) depth += 1;
    if (char === close && --depth === 0) return source.slice(start, index + 1);
  }

  throw new Error(`Unterminated declaration: ${name}`);
}

const expectedSignals = {
  1: {
    familiarity: "iconic",
    bookExposure: "cross-channel-recurring",
    namingAccessibility: "immediate",
    catalogStatus: "major-icon",
  },
  2: {
    familiarity: "well-known",
    bookExposure: "recurring",
    namingAccessibility: "recognizable-with-cue",
    catalogStatus: "major-recurring",
  },
  3: {
    familiarity: "interest-led",
    bookExposure: "occasional",
    namingAccessibility: "needs-guidance",
    catalogStatus: "supporting",
  },
  4: {
    familiarity: "specialist",
    bookExposure: "limited",
    namingAccessibility: "specialist-name",
    catalogStatus: "minor-specialist",
  },
};

const newEvidence = {
  "meganeuropsis-permiana": {
    editorialCue: "네 장의 거대한 날개와 긴 마디 배로 알아보는 페름기의 초대형 그리핀플라이",
    rationale:
      "메가뉴롭시스는 가장 큰 곤충 후보와 약 71 cm 날개폭 이야기로 선사 생물 도감에서 메가네우라와 함께 소개된다. 이름만으로 즉시 아는 스타보다는 거대 날개곤충 단서와 함께 구별하는 주요 단골이므로 LV2로 수록한다.",
  },
  "helicoprion-davisii": {
    editorialCue: "아래턱 안으로 말려 들어가는 나선 이빨로 알아보는 페름기의 기묘한 연골어류",
    rationale:
      "헬리코프리온은 나선 치열이라는 강한 시각 단서로 어린이 고생물 도감과 다큐멘터리에 반복되지만, 외부 톱날이라는 오래된 오류를 바로잡는 설명이 필요하다. 형태 단서와 함께 알아보는 주요 단골로 LV2를 적용한다.",
  },
  "titanomyrma-lubei": {
    editorialCue: "5 cm가 넘는 날개 달린 여왕개미로 알아보는 에오세의 거대 곤충",
    rationale:
      "타이타노미르마는 벌새 크기 비교로 대중 과학 기사에 등장하지만 공룡·빙하기 동물만큼 널리 알려지지는 않았다. 거대 개미라는 이야기와 네 날개·여섯 다리 단서를 알고 찾아보는 탐험가 단계이므로 LV3로 수록한다.",
  },
  "gastornis-gigantea": {
    editorialCue: "곧고 깊은 큰 부리와 굵은 다리로 알아보는 에오세의 거대한 초식성 날지 못하는 새",
    rationale:
      "가스토르니스는 디아트리마라는 옛 이름과 함께 어린이 선사 생물 책·박물관에 자주 등장하며 포식자에서 초식성으로 바뀐 복원 이야기도 교육 가치가 높다. 이름과 실루엣에 약간의 설명이 필요한 주요 단골로 LV2를 적용한다.",
  },
  "opabinia-regalis": {
    editorialCue: "머리 위에 모인 눈 다섯 개와 빗살 가시가 난 긴 코끝으로 알아보는 캄브리아기 기묘한 동물",
    rationale:
      "오파비니아(Opabinia regalis)는 눈 다섯 개와 긴 집게 코라는 독특한 모습으로 캄브리아기 생물을 다루는 어린이 도감·박물관 콘텐츠에서 반복된다. 이름만으로 즉시 아는 최상위 스타보다는 형태 단서와 함께 알아보는 주요 단골이므로 5~14세용 LV2로 수록한다.",
  },
  "tiktaalik-roseae": {
    editorialCue: "납작한 머리와 위쪽 눈, 손가락 없이 튼튼한 지느러미로 구별하는 물고기와 네발동물 사이의 대표 생물",
    rationale:
      "틱타알릭(Tiktaalik roseae)은 물고기에서 네발동물로 이어지는 진화 이야기에 자주 등장하고 납작한 머리·목·튼튼한 지느러미라는 단서가 뚜렷하다. 어린이 과학책과 박물관에서 반복되지만 이름만으로는 단서가 필요한 주요 단골이므로 LV2로 수록한다.",
  },
  "jaekelopterus-rhenaniae": {
    editorialCue: "거대한 앞 집게와 수영 패들, 넓은 꼬리판으로 알아보는 데본기의 거대 바다전갈",
    rationale:
      "야이켈롭테루스(Jaekelopterus rhenaniae)는 가장 거대한 절지동물 후보와 거대 바다전갈 이야기로 어린이 선사 생물 도감과 다큐멘터리에 반복된다. 실루엣은 강하지만 이름과 정확한 최대 크기에는 설명이 필요해 주요 단골인 LV2로 수록한다.",
  },
  "megaloceros-giganteus": {
    editorialCue: "좌우로 넓게 펼쳐진 거대한 손바닥 모양 뿔과 큰 사슴형 몸으로 알아보는 빙하기 큰뿔사슴",
    rationale:
      "메갈로케로스(Megaloceros giganteus)는 거대한 손바닥 모양 뿔과 빙하기 큰뿔사슴이라는 이야기로 어린이 선사 생물 도감과 다큐멘터리에서 자주 소개된다. 이름·별칭과 실루엣을 즉시 연결하기 쉬운 대표 신생대 생물이므로 5~14세용 LV1로 수록한다.",
  },
  "macrauchenia-patachonica": {
    editorialCue: "긴 목과 작은 머리, 짧은 코 연조직과 세 발가락 발로 구별하는 남아메리카의 독특한 초식 포유류",
    rationale:
      "마크라우케니아(Macrauchenia patachonica)는 긴 목, 작은 머리와 세 발가락 발을 지닌 남아메리카 고유 초식 포유류다. 다큐멘터리와 어린이 고생물 도감에 반복되지만 이름만으로는 바로 찾기보다 형태 단서가 필요한 주요 단골이므로 LV2로 수록한다.",
  },
  "varanus-priscus": {
    editorialCue: "낮고 굵은 왕도마뱀형 몸과 매우 긴 꼬리로 알아보는 플라이스토세 오스트레일리아의 메갈라니아",
    rationale:
      "메갈라니아(Varanus priscus)는 거대한 왕도마뱀이라는 직관적인 이름과 낮고 긴 몸, 매우 긴 꼬리로 어린이 선사 생물 콘텐츠에서 쉽게 알아볼 수 있다. 오스트레일리아 거대동물 다큐멘터리와 도감에서 반복되는 대표 파충류이므로 LV1로 수록한다.",
  },
  "arthropleura-armata": {
    editorialCue: "납작하고 넓은 방패형 몸마디와 몸 양옆으로 길게 이어지는 많은 다리로 알아보는 석탄기 거대 육상 절지동물",
    rationale:
      "아르트로플레우라(Arthropleura armata)는 납작하고 넓은 몸마디, 몸 양옆으로 이어지는 많은 다리, 석탄기 숲의 거대 육상 절지동물이라는 이야기로 어린이 선사 생물 도감과 다큐멘터리에서 반복되는 대표 생물이다. 5~14세 사용자가 이름이나 실루엣으로 바로 찾을 가능성이 높고 여러 어린이 채널에서 반복되는 주요 아이콘이므로 LV1로 수록한다.",
  },
  "meganeura-monyi": {
    editorialCue: "가슴에서 뻗는 두 쌍의 큰 날개와 긴 배를 지닌 잠자리형 석탄기 거대 곤충",
    rationale:
      "메가네우라(Meganeura monyi)는 현대 잠자리를 닮았지만 훨씬 큰 몸, 가슴에서 뻗는 두 쌍의 날개와 긴 배로 알아보는 석탄기 거대 곤충이다. 거대 곤충을 다루는 어린이 도감과 다큐멘터리에서 이름과 모습이 함께 반복되어 5~14세 사용자가 즉시 연결하기 쉬운 주요 아이콘이므로 LV1로 수록한다.",
  },
  "inostrancevia-alexandri": {
    editorialCue: "낮고 긴 머리와 위턱에서 아래로 뻗은 한 쌍의 긴 검치로 구별하는 페름기 고르고놉스류",
    rationale:
      "이노스트란체비아(Inostrancevia alexandri)는 낮고 긴 머리와 위턱의 한 쌍 긴 검치, 포유류형 몸으로 구별하는 페름기 고르고놉스류다. 대멸종 전후를 다룬 어린이 고생물 도감과 다큐멘터리에 반복되지만 이름만으로 바로 찾기보다는 검치와 시대 단서가 필요한 주요 단골이므로 LV2로 수록한다.",
  },
  "titanoboa-cerrejonensis": {
    editorialCue: "다리와 지느러미 없이 굵고 긴 한 줄의 몸으로 이어지는 팔레오세 초대형 보아뱀",
    rationale:
      "티타노보아(Titanoboa cerrejonensis)는 다리나 지느러미가 없는 굵고 긴 뱀의 몸과 팔레오세 열대 습지의 초대형 포식자라는 이야기로 어린이 선사 생물 콘텐츠에서 즉시 알아보는 대표 파충류다. 이름과 거대한 뱀 실루엣이 여러 도감·박물관·다큐멘터리 채널에서 반복되므로 LV1로 수록한다.",
  },
  "basilosaurus-isis": {
    editorialCue: "유난히 길게 늘어난 고래형 몸과 앞지느러미, 매우 작아진 뒷다리로 구별하는 에오세 고래",
    rationale:
      "바실로사우루스(Basilosaurus isis)는 유난히 길게 늘어난 고래형 몸, 앞지느러미와 매우 작아진 뒷다리로 구별하는 에오세 초기 고래다. 고래의 진화와 고대 바다를 다룬 어린이 도감·박물관·다큐멘터리에 반복되지만 뱀장어나 해양 파충류와 구별할 형태 단서가 필요한 주요 단골이므로 LV2로 수록한다.",
  },
  "paraceratherium-transouralicum": {
    editorialCue: "뿔 없는 코뿔소형 머리와 긴 목, 높은 어깨와 기둥 같은 다리로 구별하는 올리고세 거대 포유류",
    rationale:
      "파라케라테리움(Paraceratherium transouralicum)은 뿔 없는 코뿔소형 머리, 긴 목과 높은 어깨, 기둥 같은 다리로 구별하는 올리고세 거대 포유류다. 가장 큰 육상 포유류 이야기로 어린이 도감과 다큐멘터리에 반복되지만 이름과 모습을 잇는 특징 안내가 필요한 주요 단골이므로 LV2로 수록한다.",
  },
  "anomalocaris-canadensis": {
    editorialCue: "한 쌍의 가시 달린 앞부속지와 둥근 입, 몸 양옆의 헤엄엽과 꼬리부채로 알아보는 캄브리아기 포식자",
    rationale:
      "아노말로카리스(Anomalocaris canadensis)는 한 쌍의 가시 달린 앞부속지, 둥근 입, 몸 양옆의 헤엄엽과 꼬리부채로 알아보는 캄브리아기 대표 포식자다. 캄브리아기 폭발을 소개하는 어린이 도감·박물관·다큐멘터리에서 이름과 실루엣이 반복되는 주요 아이콘이므로 LV1로 수록한다.",
  },
  "dunkleosteus-terrelli": {
    editorialCue: "두꺼운 머리 갑옷과 이빨 대신 맞물리는 날카로운 턱판으로 알아보는 데본기 대형 판피어",
    rationale:
      "둔클레오스테우스(Dunkleosteus terrelli)는 두꺼운 머리와 어깨 갑옷, 이빨 대신 맞물리는 날카로운 턱판으로 알아보는 데본기 대표 판피어다. 고생대 바다 포식자를 다루는 어린이 도감·박물관·다큐멘터리에서 이름과 얼굴 실루엣이 널리 반복되는 주요 아이콘이므로 LV1로 수록한다.",
  },
  "otodus-megalodon": {
    editorialCue: "손바닥만 한 삼각형 톱니 이빨과 거대한 상어형 몸으로 알아보는 신생대 바다의 포식자",
    rationale:
      "메갈로돈(Otodus megalodon)은 매우 큰 삼각형 톱니 이빨과 거대한 상어형 몸으로 어린이 선사 생물 콘텐츠에서 즉시 알아보는 신생대 바다의 대표 포식자다. 이름과 이빨 실루엣이 도감·박물관·다큐멘터리 등 여러 채널에서 반복되는 주요 아이콘이므로 LV1로 수록한다.",
  },
  "coelodonta-antiquitatis": {
    editorialCue: "앞으로 길게 뻗은 납작한 앞뿔과 짧은 뒤뿔, 두꺼운 털과 높은 어깨로 구별하는 빙하기 코뿔소",
    rationale:
      "털코뿔소(Coelodonta antiquitatis)는 앞으로 길게 뻗은 납작한 앞뿔과 짧은 뒤뿔, 두꺼운 털과 높은 어깨로 구별하는 빙하기 코뿔소다. 매머드 스텝을 다루는 어린이 도감과 다큐멘터리에 반복되지만 현생 코뿔소와 구별할 뿔·털 단서가 필요한 주요 단골이므로 LV2로 수록한다.",
  },
  "nipponites-mirabilis": {
    editorialCue: "한 개의 관이 여러 평면에서 구불구불 이어지는 엉킨 모양의 후기 백악기 암모나이트",
    rationale:
      "니포니테스(엉킨 암모나이트)(Nipponites mirabilis)는 이형 암모나이트의 독특한 구불구불한 패각으로 과학관과 화석 입문 자료에 등장한다. 이름과 구조를 함께 설명해야 알아볼 수 있는 흥미 유도형 생물이므로 5~14세용 LV3로 수록한다.",
  },
  "diplomoceras-maximum": {
    editorialCue: "두 긴 축과 넓은 U자 굴곡이 종이클립처럼 이어지는 거대 후기 백악기 암모나이트",
    rationale:
      "디플로모세라스(클립 암모나이트)(Diplomoceras maximum)는 종이클립을 닮은 큰 이형 암모나이트로 고생물 화석 콘텐츠에서 독특한 예시로 쓰인다. 보통 암모나이트보다 전문적인 이름과 형태 설명이 필요하므로 LV3로 수록한다.",
  },
  "megateuthis-elliptica": {
    editorialCue: "몸 안쪽의 긴 로스트룸과 열 개의 갈고리 팔 단서로 살펴보는 중기 쥐라기 거대 벨렘나이트",
    rationale:
      "메가테우티스(거대 벨렘나이트)(Megateuthis elliptica)는 거대 벨렘나이트 연구로 알려졌지만 연체부와 크기의 비교복원 경계를 함께 배워야 한다. 어린이 도감의 기본 단골보다는 관심이 생긴 사용자를 위한 LV3로 수록한다.",
  },
  "duvalia-dilatata": {
    editorialCue: "좌우로 납작하고 위아래로 깊은 내부 로스트룸이 특징인 전기 백악기 벨렘나이트",
    rationale:
      "듀발리아(납작 로스트룸 벨렘나이트)(Duvalia dilatata)는 납작한 로스트룸이라는 세부 화석 형질로 구별하는 벨렘나이트다. 비교적 전문적인 구조 관찰이 필요한 생물이므로 5~14세용 탐험 단계인 LV3로 수록한다.",
  },
};

const appSource = fs.readFileSync(APP_JS, "utf8");
const dinosaurs = vm.runInNewContext(`(${extractLiteral(appSource, "dinosaurs")})`, Object.create(null), {
  timeout: 5000,
});
const evidence = JSON.parse(fs.readFileSync(EVIDENCE_JSON, "utf8"));
const existingById = new Map(evidence.taxa.map((row) => [row.id, row]));
const appIds = new Set(dinosaurs.map((dino) => dino.id));

for (const id of existingById.keys()) {
  if (!appIds.has(id)) throw new Error(`Evidence id is no longer in app.js: ${id}`);
}
for (const id of Object.keys(newEvidence)) {
  if (!appIds.has(id)) throw new Error(`New evidence id is not in app.js: ${id}`);
}

evidence.baselineDate = "2026-08-11";
evidence.taxa = dinosaurs.map((dino, index) => {
  const existing = existingById.get(dino.id);
  if (existing && !newEvidence[dino.id]) return { ...existing, order: index + 1 };

  const addition = newEvidence[dino.id];
  if (!addition) throw new Error(`Missing evidence definition: ${dino.id}`);
  if (!expectedSignals[dino.knowledgeLevel]) {
    throw new Error(`No signal mapping for new ${dino.id}=LV${dino.knowledgeLevel}`);
  }
  return {
    order: index + 1,
    id: dino.id,
    koreanName: dino.koreanName,
    scientificName: dino.name,
    knowledgeLevel: dino.knowledgeLevel,
    signals: { ...expectedSignals[dino.knowledgeLevel] },
    editorialCue: addition.editorialCue,
    rationale: addition.rationale,
  };
});

const unresolved = Object.keys(newEvidence).filter((id) => !evidence.taxa.some((row) => row.id === id));
if (unresolved.length) throw new Error(`New evidence rows were not emitted: ${unresolved.join(", ")}`);

fs.writeFileSync(EVIDENCE_JSON, `${JSON.stringify(evidence, null, 2)}\n`, "utf8");

const labels = evidence.signalLabels;
const distribution = { 1: 0, 2: 0, 3: 0, 4: 0 };
for (const row of evidence.taxa) distribution[row.knowledgeLevel] += 1;

const markdown = [
  `# ${evidence.taxa.length}개 분류군 지식 레벨 근거표`,
  "",
  `- 기준일: ${evidence.baselineDate}`,
  `- 대상: ${evidence.audience}`,
  `- 행 수: ${evidence.taxa.length}개 분류군`,
  "- 기준 문서: [도감 친숙도 LV 판정 기준](knowledge-level-rubric.md)",
  "- 기계 판독본: [`knowledge-level-evidence-2026-08-03.json`](knowledge-level-evidence-2026-08-03.json)",
  "",
  "## 읽는 법과 한계",
  "",
  evidence.purpose,
  "",
  evidence.evidenceNature,
  "",
  ...evidence.limitations.map((limitation) => `- ${limitation}`),
  "",
  "아래 표의 신호는 정확한 판매량이나 출현 횟수가 아니라 서로 비교하기 위한 서열형 편집 판단이다. 각 행은 `app.js`의 현재 ID와 LV를 고정된 기준선으로 기록하며, 자동 검증기가 누락·중복·레벨 불일치를 검사한다.",
  "",
  "## 종별 근거",
  "",
  "| # | 분류군 | 학명 / ID | LV | 친숙도 | 어린이 자료 노출 | 이름 접근성 | 도감 지위 | 편집 근거 |",
  "| ---: | --- | --- | :---: | --- | --- | --- | --- | --- |",
  ...evidence.taxa.map((row) => {
    const signal = row.signals;
    return (
      `| ${row.order} | ${row.koreanName} | *${row.scientificName}*<br><code>${row.id}</code> | ` +
      `LV${row.knowledgeLevel} | ${labels.familiarity[signal.familiarity]} | ` +
      `${labels.bookExposure[signal.bookExposure]} | ${labels.namingAccessibility[signal.namingAccessibility]} | ` +
      `${labels.catalogStatus[signal.catalogStatus]} | ${row.rationale} |`
    );
  }),
  "",
  "## 현재 분포",
  "",
  `- LV1: ${distribution[1]}종`,
  `- LV2: ${distribution[2]}종`,
  `- LV3: ${distribution[3]}종`,
  `- LV4: ${distribution[4]}종`,
  "",
  "이 표는 현재 기준선을 설명하는 감사 산출물이다. 새 출판·교육 노출이나 실사용 데이터가 들어오면 근거 행을 먼저 수정하고, 그 뒤 `app.js`의 레벨을 변경한다.",
  "",
].join("\n");

fs.writeFileSync(EVIDENCE_MARKDOWN, markdown, "utf8");

let audit = fs.readFileSync(AUDIT_MARKDOWN, "utf8");
for (const level of [1, 2, 3, 4]) {
  const names = dinosaurs
    .filter((dino) => dino.knowledgeLevel === level)
    .map((dino) => dino.koreanName)
    .join(", ");
  const snapshotLine = `- LV${level} ${distribution[level]}종: ${names}.`;
  const pattern = new RegExp(`^- LV${level} \\d+종: .+$`, "m");
  if (!pattern.test(audit)) throw new Error(`Missing LV${level} snapshot line in audit`);
  audit = audit.replace(pattern, snapshotLine);
}
fs.writeFileSync(AUDIT_MARKDOWN, audit, "utf8");

console.log(
  JSON.stringify(
    {
      taxa: evidence.taxa.length,
      baselineRowsPreserved: [...existingById.keys()].filter((id) => !newEvidence[id]).length,
      managedAdditionRows: Object.keys(newEvidence).length,
      distribution,
    },
    null,
    2,
  ),
);
