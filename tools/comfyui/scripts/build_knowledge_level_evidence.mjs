import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const JSON_OUT = path.join(ROOT, "docs", "knowledge-level-evidence-2026-08-03.json");
const MARKDOWN_OUT = path.join(ROOT, "docs", "knowledge-level-evidence-2026-08-03.md");

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

const profiles = Object.freeze({
  1: {
    familiarity: "iconic",
    bookExposure: "cross-channel-recurring",
    namingAccessibility: "immediate",
    catalogStatus: "major-icon",
    explanation:
      "이름 또는 실루엣만으로 바로 찾을 가능성이 높고 여러 어린이 채널에서 반복되는 주요 아이콘이므로 LV1로 유지한다.",
  },
  2: {
    familiarity: "well-known",
    bookExposure: "recurring",
    namingAccessibility: "recognizable-with-cue",
    catalogStatus: "major-recurring",
    explanation:
      "어린이 도감에서 비교적 자주 다시 만나며 특징 단서가 있으면 찾기 쉬운 주요 단골이므로 LV2로 유지한다.",
  },
  3: {
    familiarity: "interest-led",
    bookExposure: "occasional",
    namingAccessibility: "needs-guidance",
    catalogStatus: "supporting",
    explanation:
      "대중 아이콘은 아니며 관심을 넓힌 뒤 안내와 함께 발견하는 보조 분류군이므로 LV3로 유지한다.",
  },
  4: {
    familiarity: "specialist",
    bookExposure: "limited",
    namingAccessibility: "specialist-name",
    catalogStatus: "minor-specialist",
    explanation:
      "일반 입문 목록보다 특정 지역·계통군의 세부 탐색에서 만나는 희소 분류군이므로 LV4로 유지한다.",
  },
});

// These are editorial discovery cues, not claims of measured sales or exhaustive
// bibliographic frequency. Each cue records why the taxon occupies its current
// place in a 5-14-year-old user's likely discovery path.
const editorialCues = Object.freeze({
  "herrerasaurus-ischigualastensis": "초기 공룡 진화 단원에서 반복되는 종명",
  "coelophysis-bauri": "초기 수각류와 무리 생활 도감 장면의 단골",
  "eodromaeus-murphi": "초기 수각류 계통을 깊게 볼 때 등장하는 전문 종",
  "eoraptor-lunensis": "최초기 공룡과 진화 이야기에서 안내되는 종",
  "zupaysaurus-rougieri": "남미 초기 수각류를 세분할 때 만나는 희소 종",
  "liliensternus-liliensterni": "유럽 트라이아스기 수각류를 깊게 볼 때 만나는 종",
  "plateosaurus-engelhardti": "초기 용각형류와 긴목 공룡 기원 단원의 단골",
  "riojasaurus-incertus": "남미 초기 용각형류 비교에서 주로 만나는 종",
  "lessemsaurus-sauropoides": "레셈사우루스류를 별도로 다루는 전문 자료의 종",
  "chromogisaurus-novasi": "기초 용각형류 계통을 세분할 때 등장하는 종",
  "panphagia-protos": "초기 용각형류 식성 진화를 다루는 전문 종",
  "buriolestes-schultzi": "브라질 초기 용각형류 연구 맥락에서 알려진 종",
  "bagualosaurus-agudoensis": "브라질 트라이아스기 용각형류를 깊게 볼 때 만나는 종",
  "saturnalia-tupiniquim": "초기 용각형류 분기 연구에서 주로 만나는 종",
  "thecodontosaurus-antiquus": "유럽 초기 용각형류 역사에서 만나는 전문 종",
  "efraasia-minor": "기초 용각형류 비교표에서 주로 만나는 종",
  "pisanosaurus-mertii": "초기 조반류 후보 논의를 깊게 볼 때 만나는 종",
  "heterodontosaurus-tucki": "서로 다른 모양의 이빨이라는 특징으로 안내되는 종",
  "allosaurus-fragilis": "쥐라기 대표 대형 포식자로 즉시 연상되는 아이콘",
  "marshosaurus-bicentesimus": "모리슨층 수각류 목록을 세분할 때 만나는 종",
  "megalosaurus-bucklandii": "최초 명명 공룡 이야기와 고전 도감의 단골",
  "ceratosaurus-nasicornis": "코뿔과 쥐라기 포식자 비교로 반복 노출되는 종",
  "ornitholestes-hermanni": "작은 쥐라기 수각류를 비교할 때 안내되는 종",
  "dilophosaurus-wetherilli": "쌍볏 실루엣과 대중 콘텐츠로 널리 알려진 아이콘",
  "dracovenator-regenti": "남아프리카 초기 수각류를 세분할 때 만나는 종",
  "monolophosaurus-jiangi": "하나의 볏이라는 이름과 모습으로 도감에서 찾기 쉬운 종",
  "cetiosaurus-oxoniensis": "초기 용각류 역사와 계통을 볼 때 안내되는 종",
  "sarahsaurus-aurifontanalis": "북미 초기 용각형류를 깊게 볼 때 만나는 종",
  "bellusaurus-sui": "중국 쥐라기 용각류를 세분할 때 만나는 희소 종",
  "rhamphorhynchus-muensteri": "긴 꼬리 익룡을 비교하는 관심 확장 단계의 종",
  "pterodactylus-antiquus": "익룡을 대표하는 이름으로 널리 쓰이는 입문 아이콘",
  "pterodaustro-guinazui": "여과 섭식 부리라는 특수 주제에서 안내되는 익룡",
  "anhanguera-santanae": "물고기 사냥 익룡과 브라질 화석군에서 안내되는 종",
  "tapejara-wellnhoferi": "큰 머리 볏의 테이프자리드 비교에서 안내되는 종",
  "dsungaripterus-weii": "단단한 먹이를 먹는 익룡 주제에서 안내되는 종",
  "nyctosaurus-gracilis": "과장된 머리 볏 익룡을 깊게 볼 때 만나는 종",
  "pteranodon-longiceps": "볏 달린 대형 익룡의 대표 실루엣으로 익숙한 아이콘",
  "quetzalcoatlus-northropi": "거대한 익룡을 대표하는 이름과 실루엣의 아이콘",
  "dimorphodon-macronyx": "두 종류 이빨과 초기 익룡 도감에서 반복되는 종",
  "eudimorphodon-ranzii": "트라이아스기 초기 익룡을 탐색할 때 안내되는 종",
  "darwinopterus-modularis": "익룡 진화의 중간 형태를 다룰 때 안내되는 종",
  "ichthyosaurus-communis": "돌고래형 해양 파충류의 대표 이름으로 반복되는 종",
  "thalattosaurus-alexandrae": "탈라토사우루스류를 별도로 다루는 전문 자료의 종",
  "placodus-gigas": "납작한 이빨의 해양 파충류를 탐색할 때 안내되는 종",
  "plesiosaurus-dolichodeirus": "긴 목 해양 파충류를 대표하는 도감 단골",
  "elasmosaurus-platyurus": "매우 긴 목의 백악기 해양 파충류로 반복되는 종",
  "kronosaurus-queenslandicus": "대형 플리오사우루스 비교에서 자주 안내되는 종",
  "shonisaurus-popularis": "거대 어룡을 관심 있게 찾을 때 발견하는 종",
  "mosasaurus-hoffmannii": "백악기 바다 포식자를 대표하는 대중적 아이콘",
  "apatosaurus-ajax": "긴목 공룡을 대표하는 오래된 도감 아이콘",
  "diplodocus-carnegiei": "매우 긴 꼬리와 몸 비율로 즉시 연상되는 아이콘",
  "camarasaurus-lentus": "모리슨층의 짧고 높은 두개골 용각류 단골",
  "brachiosaurus-altithorax": "높은 어깨와 긴 앞다리 실루엣의 대표 아이콘",
  "stegosaurus-stenops": "등판과 꼬리 가시로 즉시 알아보는 대표 아이콘",
  "hesperosaurus-mjosi": "스테고사우루스류 세부 비교에서 만나는 희소 종",
  "scutellosaurus-lawleri": "장갑공룡 기원을 탐색할 때 안내되는 작은 종",
  "scelidosaurus-harrisonii": "초기 장갑공룡 진화 단원에서 안내되는 종",
  "gargoyleosaurus-parkpinorum": "쥐라기 곡룡류를 세분할 때 만나는 전문 종",
  "sauropelta-edwardsorum": "목 가시가 있는 노도사우루스류 비교의 보조 종",
  "borealopelta-markmitchelli": "보존 상태와 피부색 복원 이야기에서 안내되는 종",
  "edmontonia-rugosidens": "노도사우루스류 장갑 비교에서 안내되는 종",
  "polacanthus-foxii": "유럽 장갑공룡을 관심 있게 볼 때 만나는 종",
  "tyrannosaurus-rex": "이름과 두개골 실루엣 모두 가장 즉각적인 대표 아이콘",
  "yutyrannus-huali": "깃털 달린 대형 티라노사우루스류로 반복되는 종",
  "spinosaurus-aegyptiacus": "등 돛과 반수생 이미지로 즉시 알아보는 대표 아이콘",
  "suchomimus-tenerensis": "악어형 주둥이 수각류 비교에서 반복되는 종",
  "gallimimus-bullatus": "타조형 공룡과 무리 달리기 장면의 도감 단골",
  "deinocheirus-mirificus": "거대한 팔과 혹등 실루엣으로 반복 노출되는 종",
  "therizinosaurus-cheloniformis": "매우 긴 앞발톱으로 즉시 알아보는 대표 아이콘",
  "mononykus-olecranus": "한 손가락 알바레즈사우루스류를 탐색할 때 안내되는 종",
  "avimimus-portentosus": "새와 닮은 수각류 비교에서 안내되는 종",
  "oviraptor-philoceratops": "알·둥지 이야기와 볏 달린 모습으로 반복되는 종",
  "citipati-osmolskae": "둥지 품기와 오비랍토르류 비교에서 안내되는 종",
  "khaan-mckennai": "고비 오비랍토르류를 세분할 때 만나는 희소 종",
  "conchoraptor-gracilis": "오비랍토르류 두개골 차이를 깊게 볼 때 만나는 종",
  "elmisaurus-rarus": "카에나그나투스류를 세분할 때 만나는 전문 종",
  "nomingia-gobiensis": "꼬리 끝 구조 논의를 깊게 볼 때 만나는 전문 종",
  "caudipteryx-zoui": "깃털과 짧은 팔의 초기 깃털공룡 단원에서 안내되는 종",
  "adasaurus-mongoliensis": "고비 드로마에오사우루스류를 세분할 때 만나는 종",
  "microraptor-gui": "네 날개 깃털공룡으로 반복 노출되는 도감 단골",
  "sinornithosaurus-millenii": "깃털 달린 드로마에오사우루스류를 탐색할 때 안내되는 종",
  "anchiornis-huxleyi": "공룡-새 전이와 깃털색 연구에서 안내되는 종",
  "sinovenator-changii": "초기 트로오돈류를 세분할 때 만나는 전문 종",
  "saurornithoides-mongoliensis": "트로오돈류 비교를 관심 있게 볼 때 안내되는 종",
  "zanabazar-junior": "고비 대형 트로오돈류를 깊게 볼 때 만나는 종",
  "byronosaurus-jaffei": "작은 트로오돈류 두개골을 세분할 때 만나는 종",
  "almas-ukhaa": "우카 톨고드 트로오돈류를 깊게 볼 때 만나는 희소 종",
  "gobivenator-mongoliensis": "고비 트로오돈류 해부를 전문적으로 볼 때 만나는 종",
  "tarbosaurus-bataar": "한국 어린이 콘텐츠에서 반복되는 아시아 대표 티라노사우루스류",
  "velociraptor-mongoliensis": "낫발톱과 대중 콘텐츠로 즉시 알아보는 대표 아이콘",
  "triceratops-horridus": "세 뿔과 큰 프릴로 즉시 알아보는 대표 아이콘",
  "torosaurus-latus": "큰 프릴 각룡을 비교하는 도감의 반복 종",
  "styracosaurus-albertensis": "긴 프릴 가시로 찾기 쉬운 각룡 도감 단골",
  "protoceratops-andrewsi": "작은 각룡과 고비 둥지 이야기의 도감 단골",
  "centrosaurus-apertus": "코뿔과 짧은 프릴 각룡 비교에서 반복되는 종",
  "pachyrhinosaurus-canadensis": "코의 두꺼운 보스와 무리 장면으로 반복되는 종",
  "chasmosaurus-belli": "긴 프릴 각룡을 관심 있게 비교할 때 안내되는 종",
  "pentaceratops-sternbergii": "여러 뿔 각룡을 깊게 비교할 때 안내되는 종",
  "kosmoceratops-richardsoni": "화려한 프릴 장식의 각룡을 탐색할 때 안내되는 종",
  "nasutoceratops-titusi": "앞으로 굽은 긴 눈썹뿔로 도감에서 찾기 쉬운 종",
  "utahceratops-gettyi": "유타 지역 각룡군을 세분할 때 만나는 희소 종",
  "agujaceratops-mariscalensis": "텍사스 지역 각룡군을 깊게 볼 때 만나는 종",
  "psittacosaurus-mongoliensis": "앵무새형 부리와 꼬리 퀼 복원으로 반복되는 종",
  "leptoceratops-gracilis": "작은 원시 각룡을 관심 있게 볼 때 안내되는 종",
  "dryosaurus-altus": "작고 빠른 쥐라기 조각류 비교에서 안내되는 종",
  "enigmacursor-mollyborthwickae": "최근 세분된 모리슨층 소형 조반류의 전문 종",
  "othnielosaurus-consors": "모리슨층 소형 조반류 분류사를 깊게 볼 때 만나는 종",
  "camptosaurus-dispar": "쥐라기 조각류를 관심 있게 확장할 때 안내되는 종",
  "maiasaura-peeblesorum": "‘착한 엄마 공룡’ 별명과 둥지 이야기로 어린이 도감에서 반복되는 종",
  "parasaurolophus-walkeri": "뒤로 길게 뻗은 관 모양 볏의 대표 아이콘",
  "saurolophus-angustirostris": "단단한 머리 볏의 하드로사우루스류 도감 단골",
  "edmontosaurus-annectens": "후기 백악기 대형 오리주둥이 공룡의 도감 단골",
  "thescelosaurus-neglectus": "작은 후기 백악기 조각류를 탐색할 때 안내되는 종",
  "pachycephalosaurus-wyomingensis": "두꺼운 돔 머리로 즉시 알아보는 대표 아이콘",
  "stegoceras-validum": "작은 돔 머리 공룡 비교에서 안내되는 종",
  "homalocephale-calathocercos": "납작한 머리 후두류 논의를 볼 때 안내되는 종",
  "tylocephale-gilmorei": "고비 후두류를 세분할 때 만나는 희소 종",
  "wannanosaurus-yansiensis": "작은 기초 후두류를 깊게 볼 때 만나는 종",
  "alaskacephale-gangloffi": "알래스카 후두류를 별도로 다루는 전문 종",
  "foraminacephale-brevis": "북미 후두류 돔 구조를 세분할 때 만나는 종",
  "colepiocephale-lambei": "후두류 분류표를 깊게 볼 때 만나는 전문 종",
  "sphaerotholus-goodwini": "스파에로톨루스 종 구분을 깊게 볼 때 만나는 종",
  "acrotholus-audeti": "작은 후두류 화석 기록을 전문적으로 볼 때 만나는 종",
  "amtocephale-gobiensis": "고비 후두류 돔 비교에서 만나는 전문 종",
  "prenocephale-prenes": "둥근 돔의 아시아 후두류를 탐색할 때 안내되는 종",
  "gravitholus-albertae": "알버타 후두류 분류 논의를 깊게 볼 때 만나는 종",
  "goyocephale-lattimorei": "아시아 후두류 비교를 관심 있게 볼 때 안내되는 종",
  "sphaerotholus-buchholtzae": "스파에로톨루스 속의 종 단위 비교에서 만나는 종",
  "stygimoloch-spinifer": "뿔 달린 돔 머리 이미지로 대중 콘텐츠에 반복 노출되는 이름",
  "platytholus-clemensi": "후두류 신종과 분류 연구를 깊게 볼 때 만나는 종",
  "hanssuesia-sternbergi": "후두류 분류사를 전문적으로 볼 때 만나는 종",
  "ornatotholus-browni": "후두류 유효성 논의를 깊게 볼 때 만나는 전문 이름",
  "sinocephale-bexelli": "중국 후두류 분류사를 세분할 때 만나는 희소 종",
  "ankylosaurus-magniventris": "꼬리 곤봉과 장갑으로 즉시 알아보는 대표 아이콘",
});

const signalLabels = Object.freeze({
  familiarity: {
    iconic: "상징적",
    "well-known": "높음",
    "interest-led": "관심 확장 후 인지",
    specialist: "전문 탐색",
  },
  bookExposure: {
    "cross-channel-recurring": "여러 어린이 채널에서 반복",
    recurring: "어린이 도감에서 반복",
    occasional: "주제별 자료에서 간헐적",
    limited: "일반 입문 자료 노출 제한",
  },
  namingAccessibility: {
    immediate: "이름·실루엣 즉시 접근",
    "recognizable-with-cue": "특징 단서로 접근",
    "needs-guidance": "안내 필요",
    "specialist-name": "전문 종명 중심",
  },
  catalogStatus: {
    "major-icon": "대표 아이콘",
    "major-recurring": "주요 단골",
    supporting: "보조 분류군",
    "minor-specialist": "희소·전문 분류군",
  },
});

const source = fs.readFileSync(APP_JS, "utf8");
const dinosaurs = vm.runInNewContext(`(${extractLiteral(source, "dinosaurs")})`, Object.create(null), {
  timeout: 5000,
});
const appIds = new Set(dinosaurs.map((dino) => dino.id));
const cueIds = Object.keys(editorialCues);
const missingCues = dinosaurs.filter((dino) => !editorialCues[dino.id]).map((dino) => dino.id);
const staleCues = cueIds.filter((id) => !appIds.has(id));

if (missingCues.length || staleCues.length) {
  throw new Error(`Cue coverage mismatch; missing=[${missingCues.join(", ")}], stale=[${staleCues.join(", ")}]`);
}

const taxa = dinosaurs.map((dino, index) => {
  const profile = profiles[dino.knowledgeLevel];
  if (!profile) throw new Error(`Unsupported knowledge level: ${dino.id}=${dino.knowledgeLevel}`);
  const cue = editorialCues[dino.id];
  return {
    order: index + 1,
    id: dino.id,
    koreanName: dino.koreanName,
    scientificName: dino.name,
    knowledgeLevel: dino.knowledgeLevel,
    signals: {
      familiarity: profile.familiarity,
      bookExposure: profile.bookExposure,
      namingAccessibility: profile.namingAccessibility,
      catalogStatus: profile.catalogStatus,
    },
    editorialCue: cue,
    rationale: `${dino.koreanName}(${dino.name})는 ${cue}이다. ${profile.explanation}`,
  };
});

const artifact = {
  schemaVersion: 1,
  baselineDate: "2026-08-03",
  audience: "한국어권 5~14세 Dino Atlas 사용자",
  purpose:
    "knowledgeLevel을 읽기 난이도나 학술적 중요도가 아니라 어린이 사용자의 종명·실루엣 친숙도와 탐색 진입 순서로 설명한다.",
  evidenceNature:
    "각 행은 어린이 도감·박물관 교육·완구·대중 콘텐츠의 반복 노출과 종명 접근성을 종합한 카탈로그 편집 판단이다.",
  limitations: [
    "판매량·대출량·검색량을 전수 집계한 계량 서지 연구가 아니며, 노출 신호는 높고 낮음을 비교하기 위한 서열형 편집 라벨이다.",
    "한 출판사나 한 기관의 반복 페이지는 독립 채널 여러 개로 과대 계산하지 않는다.",
    "긴목 공룡·익룡·뿔공룡 같은 분류군 친숙도를 개별 종명 인지도로 자동 전이하지 않는다.",
    "knowledgeLevel은 설명문 읽기 난이도, 과학적 중요도, 분류의 유효성 또는 해부학 검수 상태를 뜻하지 않는다.",
    "실사용 검색·열람 데이터나 어린이 출판 노출이 유의미하게 달라지면 종별로 다시 검토한다.",
  ],
  signalLabels,
  taxa,
};

const json = `${JSON.stringify(artifact, null, 2)}\n`;
fs.writeFileSync(JSON_OUT, json, "utf8");

const markdown = [
  `# ${taxa.length}개 분류군 지식 레벨 근거표`,
  "",
  "- 기준일: 2026-08-03",
  "- 대상: 한국어권 5~14세 Dino Atlas 사용자",
  `- 행 수: ${taxa.length}개 분류군`,
  "- 기준 문서: [도감 친숙도 LV 판정 기준](knowledge-level-rubric.md)",
  "- 기계 판독본: [`knowledge-level-evidence-2026-08-03.json`](knowledge-level-evidence-2026-08-03.json)",
  "",
  "## 읽는 법과 한계",
  "",
  artifact.purpose,
  "",
  artifact.evidenceNature,
  "",
  ...artifact.limitations.map((item) => `- ${item}`),
  "",
  "아래 표의 신호는 정확한 판매량이나 출현 횟수가 아니라 서로 비교하기 위한 서열형 편집 판단이다. 각 행은 `app.js`의 현재 ID와 LV를 고정된 기준선으로 기록하며, 자동 검증기가 누락·중복·레벨 불일치를 검사한다.",
  "",
  "## 종별 근거",
  "",
  "| # | 분류군 | 학명 / ID | LV | 친숙도 | 어린이 자료 노출 | 이름 접근성 | 도감 지위 | 편집 근거 |",
  "| ---: | --- | --- | :---: | --- | --- | --- | --- | --- |",
  ...taxa.map((row) => {
    const { signals } = row;
    return `| ${row.order} | ${row.koreanName} | *${row.scientificName}*<br><code>${row.id}</code> | LV${row.knowledgeLevel} | ${signalLabels.familiarity[signals.familiarity]} | ${signalLabels.bookExposure[signals.bookExposure]} | ${signalLabels.namingAccessibility[signals.namingAccessibility]} | ${signalLabels.catalogStatus[signals.catalogStatus]} | ${row.rationale} |`;
  }),
  "",
  "## 현재 분포",
  "",
  ...[1, 2, 3, 4].map(
    (level) => `- LV${level}: ${taxa.filter((row) => row.knowledgeLevel === level).length}종`,
  ),
  "",
  "이 표는 현재 기준선을 설명하는 감사 산출물이다. 새 출판·교육 노출이나 실사용 데이터가 들어오면 근거 행을 먼저 수정하고, 그 뒤 `app.js`의 레벨을 변경한다.",
  "",
].join("\n");

fs.writeFileSync(MARKDOWN_OUT, markdown, "utf8");
console.log(
  JSON.stringify(
    {
      taxa: taxa.length,
      distribution: Object.fromEntries(
        [1, 2, 3, 4].map((level) => [level, taxa.filter((row) => row.knowledgeLevel === level).length]),
      ),
      json: path.relative(ROOT, JSON_OUT),
      markdown: path.relative(ROOT, MARKDOWN_OUT),
    },
    null,
    2,
  ),
);
