import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP_JS = path.join(ROOT, "app.js");
const ASSET_ROOT = path.join(ROOT, "assets", "dinosaurs");
const OUTPUT_DIR = path.join(ROOT, "tools", "comfyui", "outputs");
const OUTPUT_JSON = path.join(OUTPUT_DIR, "gallery-slot-generation-plan.json");
const OUTPUT_MD = path.join(OUTPUT_DIR, "gallery-slot-generation-plan.md");
const OUTPUT_ASSIGNMENTS = path.join(ROOT, "gallery-slots.js");
const VISUAL_DECISIONS = path.join(ROOT, "tools", "comfyui", "gallery-slot-visual-decisions.json");
const REJECTIONS_JSON = path.join(ROOT, "tools", "comfyui", "gallery-slot-rejections.json");

const SLOT_ROLES = [
  { slot: 1, key: "representative", label: "representative full body", kind: "count-level pass" },
  { slot: 2, key: "color-pattern", label: "color and pattern variant", kind: "review hold" },
  { slot: 3, key: "habitat-ecology", label: "habitat and everyday ecology", kind: "anatomy review" },
  { slot: 4, key: "identity-anatomy", label: "signature anatomy", kind: "anatomy review" },
  { slot: 5, key: "interaction", label: "ecological interaction", kind: "anatomy review" },
  { slot: 6, key: "social-growth-defense", label: "social, growth, or defense", kind: "anatomy review" },
  { slot: 7, key: "alternate-habitat-behavior", label: "alternate habitat or behavior", kind: "anatomy review" },
];
const RICHNESS_MIN_IMAGES = 6;

const COMMON_REJECT = [
  "extra legs or duplicated limbs",
  "fused or missing limbs and hidden feet",
  "extra or missing fingers where digit count is diagnostic",
  "cropped, forked, or malformed tail",
  "modern animal head or generic monitor-lizard/crocodile body",
  "fantasy anatomy, text, logo, watermark, split panel, or excessive blood",
];

const FALLBACK_SWATCHES = {
  "wannanosaurus-yansiensis": ["#30243b", "#555d3d", "#a8c94d", "#e5d5b5"],
  "alaskacephale-gangloffi": ["#2b3a4b", "#a86c45", "#dce3df", "#403b3d"],
  "sphaerotholus-goodwini": ["#45668e", "#c9d4c8", "#d4b37b", "#655064"],
  "acrotholus-audeti": ["#2e5142", "#d8d0b6", "#303336", "#8c7652"],
};

const HABITATS = {
  "arid-redbed": {
    substrate: "oxidized red and ochre sediment",
    vegetation: "sparse conifers, cycads, ferns, and muted gray-green scrub",
    moisture: "dry to seasonally wet",
    light: "neutral daylight with restrained warm reflected light",
    backgroundPalette: ["#914f38", "#b98a63", "#66705a"],
  },
  "lagarcito-inland-lake": {
    substrate: "pale mineral silt, shallow freshwater channels, and low mud bars",
    vegetation: "sparse low aquatic plants and distant dryland conifers",
    moisture: "shallow perennial inland lake on a semiarid alluvial plain",
    light: "clear neutral daylight with restrained cool freshwater reflection",
    backgroundPalette: ["#6e888b", "#b6a98d", "#68705c"],
  },
  "gobi-arid": {
    substrate: "pale sand, buff rock, and dry wash gravel",
    vegetation: "sparse low gray-green scrub",
    moisture: "arid",
    light: "clear neutral daylight without a global orange cast",
    backgroundPalette: ["#c8aa77", "#8f795d", "#68725c"],
  },
  "djadokhta-semiarid-dune": {
    substrate: "buff to muted red aeolian sand, low dunes, firm interdune silt, and episodic wash gravel",
    vegetation: "very sparse low gray-green non-grass scrub with open ground",
    moisture: "semiarid dune field with rare rain-fed interdune washes",
    light: "clear neutral daylight or cool post-rain light without a global desert-orange cast",
    backgroundPalette: ["#b79a72", "#8a6650", "#64706a"],
  },
  "khulsan-baruungoyot-aeolian-interdune": {
    substrate: "well-sorted red aeolian sandstone, broad dune slopes, firm interdune surfaces, wind ripples, and shallow episodic runoff channels",
    vegetation: "very sparse low gray-green non-grass Mesozoic plants with broad open ground",
    moisture: "arid dune field with interdune deposits and rare post-rain water films; dune-collapse evidence is taphonomic context rather than behavior",
    light: "neutral overcast, restrained dawn, or cool post-rain light with localized red-earth reflection and no global orange cast",
    backgroundPalette: ["#9a654f", "#6f6258", "#6b7464"],
  },
  "wuerho-shallow-delta-lake-margin": {
    substrate: "gray-green and pale yellow sandstone, muted red to reddish-brown mudstone, shallow distributary bars, gravelly splays, and exposed firm lake-margin silt",
    vegetation: "sparse low horsetails, ferns, and restrained non-grass Mesozoic ground plants with broad open shoreline",
    moisture: "inland shallow-lake and delta system with distributary channels, interdistributary bays, alternating exposed bars, and a progressively drier seasonal signal",
    light: "clear neutral daylight, cool overcast, or restrained low-angle light without a global orange cast",
    backgroundPalette: ["#78877d", "#9a6654", "#b8a47f"],
  },
  "conifer-fern-floodplain": {
    substrate: "dark floodplain soil, leaf litter, and shallow water margins",
    vegetation: "conifers, cycads, ferns, and horsetails",
    moisture: "seasonally humid",
    light: "soft neutral daylight with dappled canopy light",
    backgroundPalette: ["#344d3d", "#6f7550", "#6c5b49"],
  },
  "linglongta-volcaniclastic-forest": {
    substrate: "ash-dark volcaniclastic forest floor, tuffaceous ledges, narrow runoff channels, damp clearings, and small palaeolake margins; do not turn the fossil lake bottom into the animal's only living surface",
    vegetation: "ginkgophytes and czekanowskiale foliage, Bennettitales, Nilssoniales, tree and ground ferns, horsetails, and scattered irregular conifers with no grass, flowers, palms, or modern pine plantation",
    moisture: "warm humid seasonal Yanliao forest mosaic near the Linglongta palaeolake system; exact perch, ground use, and flight location remain reconstruction hypotheses",
    light: "neutral broken-cloud daylight, cool dawn, or restrained post-rain sunbreak with natural wet ash and water reflection and no global teal, green, or orange cast",
    backgroundPalette: ["#5d6047", "#4b4559", "#b9823f"],
  },
  "garden-park-felch-point-bar": {
    substrate: "pale coarse arkosic channel sand and gravel, a broad lenticular point bar, adjacent red-brown and greenish-gray overbank mud, shallow scour surfaces, and scattered driftwood",
    vegetation: "open conifers, cycads, ferns, horsetails, and restrained low non-grass ground cover with no flowers or modern grass",
    moisture: "seasonally active moderate-sinuosity stream and shifting point-bar system with damp post-rain sand, shallow channels, and drier floodplain patches",
    light: "neutral daylight, cool blue-hour cloud light, or restrained dawn reflection without a global orange cast",
    backgroundPalette: ["#a18f72", "#66705e", "#3a2f3d"],
  },
  "wessex-seasonal-floodplain": {
    substrate: "muted red and purple oxidized floodplain mud, pale channel gravel, shallow abandoned channels, oxbows, and local sheetflood plant debris",
    vegetation: "scattered conifers, cycads, ferns, horsetails, and low non-grass scrub",
    moisture: "seasonal water supply across a low-relief fluvial, floodplain, and lacustrine mosaic",
    light: "neutral broken-cloud daylight with cool water reflection and no global orange cast",
    backgroundPalette: ["#75554f", "#8b7967", "#4f6657"],
  },
  "khulsangol-alluvial-sheetflood": {
    substrate: "pale alluvial gravel, sandy silt, debris-flow lobes, shallow sheet-flood channels, and low mud bars",
    vegetation: "sparse conifers, cycads, ferns, horsetails, and low non-grass ground cover",
    moisture: "seasonal alluvial debris-flow and sheet-flood plain with alternating wet and dry surfaces",
    light: "neutral broken-cloud daylight with restrained shallow-water reflection and no global orange cast",
    backgroundPalette: ["#8b7967", "#64796c", "#51405f"],
  },
  "knollenmergel-vertisol-sheetflood": {
    substrate: "red-brown vertisol mud, polygonal desiccation cracks, shallow sheet-flood water, low channel bars, and scattered driftwood",
    vegetation: "open low conifers, ferns, horsetails, and sparse non-grass ground cover with localized root-rich patches",
    moisture: "semi-arid monsoonal alluvial plain with strong wet-dry cycles, periodic heavy rain, soil formation, and local sheet floods",
    light: "neutral overcast or post-rain daylight with cool water reflection and restrained warm soil bounce",
    backgroundPalette: ["#75554f", "#384a57", "#66917b"],
  },
  "ischigualasto-cancha-de-bochas-floodplain": {
    substrate: "variegated reddish-brown, greenish-gray, and mottled gray overbank mudstone, calcic paleosol nodules, levee and crevasse-splay silt, and rare high-sinuosity river-channel sand",
    vegetation: "low herbaceous root-halo vegetation, sparse horsetails, and restrained low woody or seed-fern reconstructions with no modern grass, flowers, palms, or dense rainforest",
    moisture: "dry seasonal floodplain with stable meandering to anastomosing channels, episodic overbank flow, and locally wet post-rain surfaces",
    light: "neutral daylight, cool post-rain reflection, or restrained storm-front light without a global orange cast",
    backgroundPalette: ["#76584f", "#66746c", "#355c61"],
  },
  "ischigualasto-la-pena-upper-floodplain": {
    substrate: "greenish-gray and gray fine-grained overbank mud, pale sandy crevasse splays, rare tabular sandstone, shallow low-sinuosity channels, driftwood, and localized root halos",
    vegetation: "open low conifers, sparse horsetails, ferns, and restrained seed-fern reconstructions with no modern grass, flowers, palms, or dense rainforest",
    moisture: "seasonal La Pena floodplain with episodic overbank flow, locally wet post-rain mud, shallow channel water, and broad exposed splay surfaces",
    light: "neutral broken-cloud daylight, cool blue-hour reflection, or restrained post-rain light without a global orange cast",
    backgroundPalette: ["#777a70", "#b2a58c", "#526d67"],
  },
  "santa-maria-alemoa-red-mudstone-floodplain": {
    substrate: "reddish massive Alemoa mudstone, broad distal-to-proximal floodplain surfaces, shallow ephemeral runoff channels, restrained pale sandy splays, driftwood, and local wet red-clay margins",
    vegetation: "open low conifers, sparse horsetails, ferns, and restrained seed-fern reconstructions with no modern grass, flowers, palms, broadleaf forest, or dense rainforest",
    moisture: "seasonal southern Brazil floodplain with alternating dry red mud, brief overbank flow, shallow post-rain pools, and locally damp channel margins",
    light: "neutral daylight, cool blue-hour reflection, warm low-angle context light, or restrained post-rain overcast without a global orange cast",
    backgroundPalette: ["#8b5147", "#304f4b", "#d4a36b"],
  },
  "bristol-rhaetian-limestone-island-archipelago": {
    substrate: "weathered Carboniferous Limestone palaeo-island pavement, low rounded ledges, shallow meteoric runoff channels, rain-fed pools, coastal rubble, and only narrow surface cracks; fossil-bearing fissures remain subsurface burial and depositional conduits rather than open living canyons",
    vegetation: "patchy low conifers, cycads, seed ferns, true ferns, and restrained non-flowering ground cover with no modern grass, flowers, palms, broadleaf forest, or dense rainforest",
    moisture: "small subtropical islands in a shallow Rhaetian sea with aerated rainwater runoff, local freshwater lenses, wet limestone after squalls, tidal shallows, and nearby low islands",
    light: "neutral coastal overcast, cool blue-hour reflection, misty morning, or a restrained sunbreak after rain without a global orange cast",
    backgroundPalette: ["#d8d3c3", "#587f83", "#254b50"],
  },
  "forest-marble-coastal-tidal-mosaic": {
    substrate: "green-grey calcareous mudflat cut by shallow tidal channels, pale lenticular bioclastic and oolitic limestone shoals and channel fills, shell-rich banks, sandy limestone, oyster-rich beds, lignitic driftwood, and locally exposed firmground",
    vegetation: "patchy low coastal swamp vegetation, conifers, ferns, horsetails, seed ferns, and restrained non-flowering ground cover with no modern grass, flowers, palms, broadleaf forest, or dense rainforest",
    moisture: "Bathonian Forest Marble coastal mosaic ranging from intertidal mudflat and tidal channels to shallow marine shoals and local coastal swamp, with brackish pools and a nearby open shallow-sea margin",
    light: "neutral coastal overcast after rain, cool blue-hour reflection, soft morning cloud light, or restrained late-afternoon sunbreak without a global orange cast",
    backgroundPalette: ["#8c948b", "#d4cfbb", "#526f76"],
  },
  "stonesfield-carbonate-island-shallow-shelf": {
    substrate: "low emergent limestone-island surface beside fawn and grey laminated calcareous sand and silt, shell-fragmental and oolitic limestone, pale storm-wash bars, shallow runoff channels, and adjacent high-energy carbonate-shelf water; the fossil bed records reworked terrestrial remains rather than an aquatic dinosaur habitat",
    vegetation: "patchy conifers, cycads, ginkgophytes, seed ferns, true ferns, horsetails, and restrained non-flowering ground cover with no modern grass, flowers, palms, broadleaf forest, or dense rainforest",
    moisture: "Bathonian coastal-island reconstruction beside a high-energy shallow carbonate shelf, with storm runoff and strand material transported or reworked into the Stonesfield Slate depositional setting",
    light: "neutral broken-cloud coastal daylight, cool blue-hour reflection, or restrained post-storm sunbreak without a global orange cast",
    backgroundPalette: ["#9a9486", "#4f7178", "#6a3b49"],
  },
  "los-colorados-seasonal-fluvial-floodplain": {
    substrate: "oxidized red sandstone and siltstone, moderately sinuous sand channels, broad overbank floodplain, shallow ponds, crevasse splays, pebbly bars, and scattered driftwood",
    vegetation: "important but patchy cover of araucarioid conifers, seed ferns, true ferns, horsetails, and low cycad-like plants with no modern grass or flowers",
    moisture: "seasonally humid to subhumid fluvial plain with episodic high precipitation, receding floods, and locally damp overbank surfaces",
    light: "neutral broken-cloud or post-rain daylight with cool shallow-water reflection and restrained red-soil bounce",
    backgroundPalette: ["#7d4f46", "#517375", "#53624d"],
  },
  "morrison-seasonal-alluvial-plain": {
    substrate: "pale sand and gravel bars, red-gray overbank mud, shallow or abandoned channels, and scattered driftwood",
    vegetation: "scattered araucarian conifers, cycads, ferns, horsetails, and low non-grass ground cover",
    moisture: "strongly seasonal semi-arid to tropical wet-dry alluvial plain with fluctuating groundwater",
    light: "neutral broken-cloud daylight with restrained cool channel reflection and no global orange cast",
    backgroundPalette: ["#a18f72", "#6e7770", "#4f604d"],
  },
  "kayenta-silty-fluvial-aeolian-plain": {
    substrate: "reddish-purple siltstone and mud, pale channel sand, flood sheets, interdune sand corridors, and scattered driftwood",
    vegetation: "sparse conifer gallery patches with low cycads, ferns, and horsetails as a restrained reconstruction",
    moisture: "seasonal intermittent to ephemeral fluvial system with flash floods, shallow local channels, and adjacent aeolian sand sheets",
    light: "neutral broken-cloud daylight or cool dawn with restrained water reflection and no global orange cast",
    backgroundPalette: ["#765866", "#a18e74", "#526b64"],
  },
  "shishugou-seasonal-alluvial-wetland": {
    substrate: "dark red calcareous overbank mud, pale low-sinuosity channels, shallow ponds, tuffaceous gray silt, local sheetflood deposits, and scattered silicified wood",
    vegetation: "scattered conifers, cycads, ferns, and horsetails with no modern grass",
    moisture: "warm to hot seasonally wet-dry alluvial, fluvial, and paludal wetland mosaic with episodic floods and local boggy substrates",
    light: "neutral broken-cloud daylight or cool post-rain light with restrained water reflection and no global orange cast",
    backgroundPalette: ["#765247", "#708487", "#53634c"],
  },
  "coastal-lagoon": {
    substrate: "mudflat, pale sediment, and shallow lagoon water",
    vegetation: "coastal conifers, ferns, and low wetland plants",
    moisture: "humid and brackish",
    light: "neutral coastal daylight with controlled water reflection",
    backgroundPalette: ["#607a7a", "#a68a65", "#61715b"],
  },
  "zorzino-carbonate-island": {
    substrate: "low pale limestone and dolomite island surfaces, sheltered freshwater reservoirs, shallow runoff channels, exposed carbonate ledges, and a distant warm intraplatform sea; do not depict the anoxic fossil-basin bottom as a living surface",
    vegetation: "irregular sparse Triassic conifers, cycads, seed ferns, true ferns, and horsetails with no modern grass, flowers, palms, pine plantation, or dense rainforest",
    moisture: "freshwater-bearing ephemeral carbonate islands surrounded by an intraplatform marine basin; exact island use and surface ecology remain regional reconstruction hypotheses",
    light: "neutral broken-cloud daylight, cool dawn, or restrained post-rain sunbreak with natural freshwater and pale-stone reflection and no global teal or orange cast",
    backgroundPalette: ["#8b948a", "#667f7d", "#c8b895"],
  },
  "blue-lias-coastal-lowland": {
    substrate: "rain-darkened low-relief coastal plain, shallow runoff channels, pale limestone gravel, dark mudstone, driftwood, and only a distant marine shelf or low shoreline",
    vegetation: "patchy conifers, ferns, horsetails, cycads, and low non-grass ground cover as restrained reconstruction, with no modern flowers, lawn, palms, or seabird colony",
    moisture: "humid post-rain coastal-lowland mosaic adjacent to the Lower Lias marine depositional setting; exact terrestrial habitat use remains a reconstruction hypothesis",
    light: "neutral broken-cloud daylight, cool dawn, or restrained sunbreak with natural wet-surface reflection and no global teal, green, or orange cast",
    backgroundPalette: ["#596963", "#70818b", "#a89672"],
  },
  "smoky-hill-open-seaway": {
    substrate: "open pale blue-green carbonate-rich Western Interior Seaway water, low swells, suspended chalk mud, and only a very distant low shoreline when needed",
    vegetation: "no foreground vegetation, modern grass, flowers, palms, or seabird colony; distant land cover remains indistinct",
    moisture: "fully marine offshore Smoky Hill Chalk setting far from major terrigenous sediment sources",
    light: "soft overcast marine daylight or restrained sunbreak with natural water reflection and no global teal or orange cast",
    backgroundPalette: ["#67878b", "#aab8b3", "#596d70"],
  },
  "solnhofen-restricted-carbonate-lagoon": {
    substrate: "pale lithographic-limestone shelves, shallow restricted marine channels, carbonate mud, and reef-bounded islands",
    vegetation: "sparse island conifers, cycads, and low coastal vegetation",
    moisture: "warm restricted marine lagoon with clearer surface water and potentially hypersaline, poorly oxygenated bottom water",
    light: "neutral coastal daylight with restrained shallow-water reflection",
    backgroundPalette: ["#6f8582", "#c0aa83", "#5f6f58"],
  },
  "kem-kem-river-delta": {
    substrate: "broad rust-red sandbars, rippled silt, and shallow freshwater-to-brackish channels",
    vegetation: "horsetails, ferns, low early angiosperm scrub, and sparse conifers",
    moisture: "seasonally wet braided river and delta plain",
    light: "clear neutral daylight with controlled water reflection and no global orange cast",
    backgroundPalette: ["#9b694c", "#55747a", "#67705a"],
  },
  "elrhaz-river-system": {
    substrate: "broad buff and rust-red cross-bedded fluvial sandstone, rippled silt, and shallow braided channels",
    vegetation: "sparse low riparian ferns, horsetails, and muted floodplain plants",
    moisture: "seasonally wet sandy river and point-bar system",
    light: "clear neutral daylight with restrained water reflection and no global orange cast",
    backgroundPalette: ["#a66f50", "#587a7d", "#68725d"],
  },
  "nemegt-fluvial-floodplain": {
    substrate: "broad sandy point bars, dark wet silt, shallow meandering channels, and seasonal floodplain pools",
    vegetation: "horsetails, low wetland plants, driftwood, and patches of riparian woodland",
    moisture: "mesic seasonally wet river and floodplain system",
    light: "soft neutral daylight with restrained water reflection and no global desert-orange cast",
    backgroundPalette: ["#a58c69", "#607b74", "#4f604f"],
  },
  "sharon-springs-seaway": {
    substrate: "dark organic-rich black shale, suspended fine sediment, and sparse inoceramid or ammonite shell debris",
    vegetation: "no tropical coral reef; only sparse period-appropriate marine growth when justified",
    moisture: "fully aquatic open Western Interior Seaway with oxygen-poor bottom water",
    light: "cool filtered underwater daylight with localized warm surface light and readable slate-blue body color",
    backgroundPalette: ["#243f4d", "#4f7478", "#34363d"],
  },
  "dinosaur-park-coastal-plain": {
    substrate: "dark wet silt, broad point bars, low-gradient meandering channels, and abandoned channel margins",
    vegetation: "horsetails, ferns, low broad-leaved angiosperm shrubs, and scattered conifers",
    moisture: "humid marine-influenced coastal plain with seasonally active rivers",
    light: "soft broken-cloud daylight with restrained cool water reflection and localized warm sunlight",
    backgroundPalette: ["#566e65", "#84745d", "#4c5845"],
  },
  "dinosaur-park-meander-belt": {
    substrate: "dark wet silt, broad point bars, shallow swales, driftwood, and low-gradient meandering channels",
    vegetation: "horsetails, ferns, low broad-leaved angiosperm shrubs, and scattered conifers",
    moisture: "seasonally active fluvial meander belt upstream of the fluvial-marine transition",
    light: "cool broken-cloud daylight with restrained water reflection and localized warm sunlight",
    backgroundPalette: ["#596d63", "#766d5c", "#4e5c49"],
  },
  "hell-creek-lance-fluvial-forest": {
    substrate: "meandering channels, flood-recession point bars, dark wet silt, oxbow margins, and shallow side channels",
    vegetation: "Pinaceae and cypress-like conifer canopy, ferns, mosses, low herbaceous angiosperms, and sparse cycads",
    moisture: "warm humid fluvial forest and seasonally flooded coastal plain",
    light: "soft broken-cloud daylight with cool water reflection and localized neutral sunlight",
    backgroundPalette: ["#4f6257", "#7c725f", "#556b70"],
  },
  "dorset-humid-island-river": {
    substrate: "gravelly island river terraces, dark wet silt, shallow runoff channels, and low coastal uplands",
    vegetation: "conifers, ferns, horsetails, and low cycadophytes",
    moisture: "humid terrestrial island with seasonally active runoff",
    light: "soft broken-cloud daylight with localized cool water reflection",
    backgroundPalette: ["#53685d", "#7f7460", "#5b6f76"],
  },
  "javelina-riparian-stream-channel": {
    substrate: "broad inland stream-channel sandstone and conglomerate, pale sand and gravel bars, driftwood, and adjacent olive-gray to muted-purple overbank mud",
    vegetation: "riparian Javelinoxylon broadleaf trees, araucariacean conifers, ferns, low angiosperm scrub, and only sparse fan palms away from abandoned-channel lakes",
    moisture: "warm dry subtropical fluvial corridor in a broad inland valley, with localized channel water and no marine setting",
    light: "neutral broken-cloud daylight with restrained warm sediment reflection and readable animal colors",
    backgroundPalette: ["#8b8069", "#66715f", "#6c5f67"],
  },
  "polar-forest": {
    substrate: "cool dark soil, seasonal frost, and damp leaf litter",
    vegetation: "high-latitude conifer and fern woodland",
    moisture: "cool and seasonally wet",
    light: "low-angle neutral daylight with restrained cool ambience",
    backgroundPalette: ["#405264", "#35483f", "#c6cac2"],
  },
  marine: {
    substrate: "open water, suspended sediment, and a distant seafloor or shoreline cue",
    vegetation: "period-appropriate sparse marine vegetation only when justified",
    moisture: "fully aquatic",
    light: "neutral filtered daylight with the animal's body colors still readable",
    backgroundPalette: ["#294c59", "#537b7b", "#9a9b82"],
  },
};

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
  let lineComment = false;
  let blockComment = false;

  for (let index = start; index < source.length; index += 1) {
    const char = source[index];
    const next = source[index + 1];
    if (lineComment) {
      if (char === "\n") lineComment = false;
      continue;
    }
    if (blockComment) {
      if (char === "*" && next === "/") {
        blockComment = false;
        index += 1;
      }
      continue;
    }
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "/" && next === "/") {
      lineComment = true;
      index += 1;
      continue;
    }
    if (char === "/" && next === "*") {
      blockComment = true;
      index += 1;
      continue;
    }
    if (char === '"' || char === "'" || char === "`") {
      quote = char;
      continue;
    }
    if (char === open) depth += 1;
    if (char === close) {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }

  throw new Error(`Unterminated declaration: ${name}`);
}

function loadLiteral(source, name) {
  return vm.runInNewContext(`(${extractLiteral(source, name)})`, Object.create(null), {
    timeout: 5000,
  });
}

function normalizePath(value) {
  return String(value || "").replaceAll("\\", "/");
}

function loadJsonIfPresent(file, fallback = {}) {
  if (!fs.existsSync(file)) return fallback;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function visualDecisionFor(decisions, taxon, slot) {
  return decisions?.taxa?.[taxon]?.[String(slot)] || null;
}

function itemText(item) {
  return `${item?.title || ""} ${item?.body || ""} ${item?.variant || ""} ${item?.source || ""} ${item?.src || ""}`.toLowerCase();
}

function itemLabelText(item) {
  return `${item?.title || ""} ${item?.variant || ""} ${item?.source || ""} ${item?.src || ""}`.toLowerCase();
}

function internalSearchText(item) {
  return `${item?.title || ""} ${item?.source || ""} ${item?.src || ""}`.toLowerCase();
}

function isInternalReviewCandidate(item) {
  if (!item || typeof item !== "object") return true;
  if (item.internalOnly) return true;
  if (["diagnostic only", "reject reference", "structure reference", "primary structure reference"].includes(item.kind)) {
    return true;
  }
  const searchable = internalSearchText(item);
  if (/review[- ]?sheet|review[- ]?options|contact[- ]?sheet|crop(?:s| audit| gate)?|guide|manifest|comparison|diagnostic|rejected/.test(searchable)) {
    return true;
  }
  if (/검수\s*(?:시트|보드)|크롭|마스크|가이드|매니페스트|비교\s*시트|진단|탈락/.test(searchable)) {
    return true;
  }
  return /(?:^|[-_/ ])mask(?:-v\d+)?(?:\.png)?(?:$|\s)/.test(searchable);
}

function hasRealImage(item) {
  const relative = normalizePath(item?.src || item?.source);
  return relative.startsWith("assets/dinosaurs/") && fs.existsSync(path.join(ROOT, relative));
}

function roleScore(item, roleKey) {
  const text = itemText(item);
  const labelText = itemLabelText(item);
  const kind = item.kind || "";
  const has = (pattern) => pattern.test(text);
  const hasLabel = (pattern) => pattern.test(labelText);

  if (roleKey === "representative") {
    if (kind === "count-level pass") return 1000;
    if (kind === "primary generated") return 900;
    return kind === "review hold" && has(/full.?body|representative|source-candidate|대표|전신/) ? 120 : -1000;
  }
  if (roleKey === "color-pattern") {
    let score = kind === "review hold" ? 45 : 0;
    if (hasLabel(/pattern|palette|color|plumage|countershade|mottl|stripe|band|rosette|ocelli|saddle|mask-pattern|무늬|색상|배색|변이|변형/)) score += 90;
    if (hasLabel(/ecology|attack|chase|defense|feeding|standoff|생태|공격|추격|방어|섭식|대치/)) score -= 70;
    return score;
  }
  if (roleKey === "habitat-ecology") {
    let score = kind === "anatomy review" ? 30 : kind === "review hold" ? 15 : 0;
    if (hasLabel(/ecology|habitat|forage|browse|river|forest|floodplain|dune|seaway|lagoon|shore|wetland|woodland|roost|rest|trackway|서식|생태|먹이활동|채식|이동|휴식|발자국/)) score += 75;
    if (hasLabel(/attack|bite|chase|defense|standoff|feeding|ambush|pursuit|harass|strike|pack.?hunt|공격|물기|추격|방어|대치|사체|매복|압박|사냥/)) score -= 100;
    return score;
  }
  if (roleKey === "identity-anatomy") {
    let score = kind === "anatomy review" ? 35 : 0;
    if (hasLabel(/anatomy|identity|head|skull|crest|horn|frill|foot|feet|hand|claw|plate|armor|tail|club|dome|wing|flipper|neck|fullbody|구조|머리|두개골|볏|뿔|프릴|발|손|발톱|골판|갑옷|꼬리|돔|전신/)) score += 80;
    if (hasLabel(/ecology|attack|bite|chase|defense|standoff|feeding|ambush|pursuit|harass|strike|escape|생태|공격|물기|추격|방어|대치|사체|매복|도주/)) score -= 110;
    return score;
  }
  if (roleKey === "interaction") {
    let score = kind === "anatomy review" ? 35 : 0;
    if (hasLabel(/attack|bite|chase|defense|standoff|ambush|feeding|pursuit|harass|strike|dodge|escape|hunt|interaction|공격|추격|방어|대치|매복|섭식|도주/)) score += 90;
    return score;
  }
  if (roleKey === "social-growth-defense") {
    let score = kind === "anatomy review" ? 25 : 0;
    if (hasLabel(/group|herd|pair|juvenile|display|social|nest|flock|pack|shield|protect|defense|무리|쌍|새끼|과시|보호|방어/)) score += 90;
    return score;
  }

  let score = kind === "anatomy review" ? 30 : kind === "review hold" ? 20 : 0;
  if (hasLabel(/ecology|habitat|forage|group|herd|display|defense|standoff|river|forest|dune|lagoon|생태|서식|무리|과시|방어/)) score += 55;
  return score;
}

function roleThreshold(roleKey) {
  return {
    representative: 500,
    "color-pattern": 70,
    "habitat-ecology": 55,
    "identity-anatomy": 55,
    interaction: 70,
    "social-growth-defense": 70,
    "alternate-habitat-behavior": 40,
  }[roleKey];
}

function selectCandidate(candidates, usedSources, role, decision) {
  if (decision?.status === "approved") {
    const approvedSource = normalizePath(decision.source);
    const item = candidates.find((candidate) => normalizePath(candidate.src || candidate.source) === approvedSource);
    if (!item || usedSources.has(approvedSource)) {
      return {
        item: null,
        score: null,
        selectedBy: "visual-decision-error",
        decisionError: item ? "approved source is assigned to more than one slot" : "approved source is unavailable",
      };
    }
    usedSources.add(approvedSource);
    return { item, score: null, selectedBy: "visual-decision" };
  }

  const available = candidates.filter((item) => !usedSources.has(normalizePath(item.src)));
  const explicit = available.filter(
    (item) => Number(item.gallerySlot) === role.slot || item.galleryRole === role.key,
  );
  const unassigned = available.filter((item) => !item.gallerySlot && !item.galleryRole);
  const ranked = (explicit.length ? explicit : unassigned)
    .map((item) => ({ item, score: roleScore(item, role.key) }))
    .sort((left, right) => right.score - left.score);
  const best = ranked[0];
  if (!best || (!explicit.length && best.score < roleThreshold(role.key))) return null;
  usedSources.add(normalizePath(best.item.src));
  return { ...best, selectedBy: explicit.length ? "explicit-slot-metadata" : "role-score" };
}

function inferUnregisteredKind(source) {
  const text = source.toLowerCase();
  if (/pattern|palette|color|plumage|mottl|stripe|rosette|ocelli|saddle/.test(text)) return "review hold";
  if (/ecology|attack|chase|defense|standoff|ambush|feeding|pursuit|escape|group|herd|display/.test(text)) return "anatomy review";
  return "review hold";
}

function suggestUnregisteredSource(sources, roleKey) {
  const ranked = sources
    .map((source) => {
      const item = {
        kind: inferUnregisteredKind(source),
        title: path.basename(source, path.extname(source)),
        variant: "",
        source,
        src: source,
      };
      return { source, score: roleScore(item, roleKey) };
    })
    .sort((left, right) => right.score - left.score);
  return ranked[0]?.score >= roleThreshold(roleKey) ? ranked[0] : null;
}

function habitatFor(dino, route) {
  const text = `${dino.era} ${dino.region} ${dino.summary || ""} ${route?.focus || ""} ${route?.pass || ""}`.toLowerCase();
  let key = "conifer-fern-floodplain";
  if (dino.id === "spinosaurus-aegyptiacus") key = "kem-kem-river-delta";
  else if (dino.id === "suchomimus-tenerensis") key = "elrhaz-river-system";
  else if (dino.id === "psittacosaurus-mongoliensis") key = "khulsangol-alluvial-sheetflood";
  else if (dino.id === "liliensternus-liliensterni") key = "knollenmergel-vertisol-sheetflood";
  else if (dino.id === "panphagia-protos") key = "ischigualasto-la-pena-upper-floodplain";
  else if (dino.id === "saturnalia-tupiniquim") key = "santa-maria-alemoa-red-mudstone-floodplain";
  else if (dino.id === "thecodontosaurus-antiquus") key = "bristol-rhaetian-limestone-island-archipelago";
  else if (dino.id === "cetiosaurus-oxoniensis") key = "forest-marble-coastal-tidal-mosaic";
  else if (dino.id === "megalosaurus-bucklandii") key = "stonesfield-carbonate-island-shallow-shelf";
  else if (dino.id === "chromogisaurus-novasi") key = "ischigualasto-cancha-de-bochas-floodplain";
  else if (dino.id === "lessemsaurus-sauropoides") key = "los-colorados-seasonal-fluvial-floodplain";
  else if (dino.id === "ceratosaurus-nasicornis") key = "garden-park-felch-point-bar";
  else if (["gallimimus-bullatus", "therizinosaurus-cheloniformis", "mononykus-olecranus"].includes(dino.id)) key = "nemegt-fluvial-floodplain";
  else if (["oviraptor-philoceratops", "citipati-osmolskae", "khaan-mckennai"].includes(dino.id)) key = "djadokhta-semiarid-dune";
  else if (dino.id === "conchoraptor-gracilis") key = "khulsan-baruungoyot-aeolian-interdune";
  else if (dino.id === "dsungaripterus-weii") key = "wuerho-shallow-delta-lake-margin";
  else if (dino.id === "nyctosaurus-gracilis") key = "smoky-hill-open-seaway";
  else if (dino.id === "dimorphodon-macronyx") key = "blue-lias-coastal-lowland";
  else if (dino.id === "eudimorphodon-ranzii") key = "zorzino-carbonate-island";
  else if (dino.id === "darwinopterus-modularis") key = "linglongta-volcaniclastic-forest";
  else if (dino.id === "velociraptor-mongoliensis") key = "gobi-arid";
  else if (dino.id === "parasaurolophus-walkeri") key = "dinosaur-park-coastal-plain";
  else if (dino.id === "styracosaurus-albertensis") key = "dinosaur-park-meander-belt";
  else if (dino.id === "edmontosaurus-annectens") key = "hell-creek-lance-fluvial-forest";
  else if (["rhamphorhynchus-muensteri", "pterodactylus-antiquus"].includes(dino.id)) key = "solnhofen-restricted-carbonate-lagoon";
  else if (dino.id === "pterodaustro-guinazui") key = "lagarcito-inland-lake";
  else if (dino.id === "scelidosaurus-harrisonii") key = "dorset-humid-island-river";
  else if (dino.id === "polacanthus-foxii") key = "wessex-seasonal-floodplain";
  else if (["camarasaurus-lentus", "apatosaurus-ajax"].includes(dino.id)) key = "morrison-seasonal-alluvial-plain";
  else if (["monolophosaurus-jiangi", "bellusaurus-sui"].includes(dino.id)) key = "shishugou-seasonal-alluvial-wetland";
  else if (dino.id === "dilophosaurus-wetherilli") key = "kayenta-silty-fluvial-aeolian-plain";
  else if (dino.id === "quetzalcoatlus-northropi") key = "javelina-riparian-stream-channel";
  else if (/marine|seaway|ocean|sea |pliosaur|plesiosaur|ichthyosaur|mosasaur|해양|바다|수중/.test(text)) key = "marine";
  else if (/polar|prince creek|alaska|high-latitude|극지|고위도/.test(text)) key = "polar-forest";
  else if (/gobi|djadokhta|nemegt|dune|desert|sandstone|사구|사막|고비/.test(text)) key = "gobi-arid";
  else if (/coast|lagoon|shore|mudflat|lias|해안|석호|갯벌/.test(text)) key = "coastal-lagoon";
  else if (dino.era === "triassic" || /redbed|arid|los colorados|ischigualasto|적색층|반건조/.test(text)) key = "arid-redbed";
  return { key, ...HABITATS[key] };
}

function paletteFor(dino, swatches, profile) {
  const assigned = swatches[dino.id] || FALLBACK_SWATCHES[dino.id];
  return {
    swatches: assigned || ["#66736b", "#3e4a46", "#9fbf8d", "#d8bd79"],
    source: swatches[dino.id] ? "app.js" : FALLBACK_SWATCHES[dino.id] ? "goal fallback" : "generic fallback",
    canonicalColor: profile?.color || "",
    patternTopology: profile?.pattern || "",
    surface: profile?.texture || "",
    allowedVariant: "slot 2 only",
    avoid: profile?.avoid || "",
  };
}

function makePrompt({ dino, role, identity, profile, route, palette, habitat, referenceSource }) {
  const identityLines = [...(identity || []), profile?.anatomy || ""].filter(Boolean).join("; ");
  const action = {
    representative: "one animal in a calm strict full-body side or three-quarter view",
    "color-pattern": "one animal in a calm full-body view showing the approved variant-b palette",
    "habitat-ecology": "the canonical animal performing a normal everyday behavior in its representative habitat",
    "identity-anatomy": "a readable full-body or focused view that clearly shows the taxon's most diagnostic anatomy",
    interaction: "a non-graphic ecological interaction with period- and region-appropriate organisms, with bodies spatially separated",
    "social-growth-defense": "a scientifically restrained social, growth, or defensive behavior scene",
    "alternate-habitat-behavior": "a second plausible microhabitat or behavior scene without redesigning the animal",
  }[role.key];
  return [
    "Use case: scientific-educational",
    "Asset type: dinosaur atlas gallery image",
    `Primary request: ${dino.name}, slot ${role.slot} ${role.label}; ${action}.`,
    `Scene/backdrop: ${dino.period}, ${dino.region}; ${habitat.substrate}; ${habitat.vegetation}; ${habitat.moisture}.`,
    `Subject: ${identityLines}`,
    `Composition/framing: landscape; ${role.slot === 4 ? "diagnostic anatomy must remain readable" : "complete primary body from snout to tail tip when full body is requested"}; visible required limbs and feet.`,
    `Lighting/mood: ${habitat.light}.`,
    `Color palette: preserve ${palette.swatches.join(", ")}; ${palette.canonicalColor}; ${palette.patternTopology}.`,
    `Materials/textures: ${palette.surface}.`,
    `Input images: ${referenceSource ? `Image 1: canonical slot-1 identity, anatomy, color, and marking-placement reference at ${referenceSource}` : "none"}.`,
    `Constraints: ${role.slot === 2 ? "variant-b may shift hues only within the approved profile" : "use canonical-a body color and marking placement"}; habitat color belongs in the background and localized dust, mud, moisture, or reflected light; no text, no labels, no watermark, no split panel.`,
    `Avoid: ${profile?.avoid || ""}; ${route?.reject || ""}; ${COMMON_REJECT.join("; ")}.`,
  ].join("\n");
}

function makePlanItem({ dino, samples, identities, profiles, routes, swatches, unregisteredAssets, decisions, rejectedSources }) {
  const identity = identities[dino.id] || [];
  const profile = profiles[dino.id] || {};
  const route = routes[dino.id] || {};
  const palette = paletteFor(dino, swatches, profile);
  const habitat = habitatFor(dino, route);
  const candidates = (samples[dino.id] || []).filter((item) => (
    !isInternalReviewCandidate(item)
    && hasRealImage(item)
    && !rejectedSources.has(normalizePath(item.src || item.source))
  ));
  const availableUnregisteredAssets = (unregisteredAssets[dino.id] || [])
    .filter((source) => !rejectedSources.has(normalizePath(source)));
  const malformedSamples = (samples[dino.id] || [])
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => !item || typeof item !== "object")
    .map(({ item, index }) => ({ index, value: String(item || "") }));
  const usedSources = new Set();
  const roles = SLOT_ROLES.slice(0, dino.imageSlots);
  const selected = [];

  for (const role of roles) {
    const decision = visualDecisionFor(decisions, dino.id, role.slot);
    const picked = selectCandidate(candidates, usedSources, role, decision);
    selected.push({ role, picked, decision });
  }

  const representative = selected.find(({ role }) => role.slot === 1)?.picked?.item;
  const referenceSource = normalizePath(representative?.src || route.control || "");
  const slots = selected.map(({ role, picked, decision }) => {
    const source = normalizePath(picked?.item?.src || "");
    const suggestedUnregistered = source ? null : suggestUnregisteredSource(availableUnregisteredAssets, role.key);
    const decisionSource = normalizePath(decision?.source || "");
    const approved = decision?.status === "approved" && source && source === decisionSource;
    const status = decision?.status === "approved"
      ? approved ? "approved" : "decision-error"
      : source ? "manual-review" : suggestedUnregistered ? "manual-review-unregistered" : "generate";
    return {
      slot: role.slot,
      role: role.key,
      label: role.label,
      expectedKind: role.kind,
      status,
      currentKind: picked?.item?.kind || "",
      currentSource: source,
      currentTitle: picked?.item?.title || "",
      score: picked?.score ?? null,
      selectedBy: picked?.selectedBy || "",
      decisionStatus: decision?.status || "unreviewed",
      decisionSource,
      decisionReason: decision?.reason || "",
      reviewMethod: decision?.reviewMethod || "",
      decisionError: picked?.decisionError || "",
      suggestedUnregisteredSource: suggestedUnregistered?.source || "",
      suggestedUnregisteredScore: suggestedUnregistered?.score ?? null,
      referenceSource,
      prompt: makePrompt({ dino, role, identity, profile, route, palette, habitat, referenceSource }),
      negativePrompt: [profile.avoid, route.reject, ...COMMON_REJECT].filter(Boolean).join("; "),
      passGate: [...identity, profile.anatomy].filter(Boolean),
      rejectGate: [profile.avoid, route.reject, ...COMMON_REJECT].filter(Boolean),
    };
  });
  const richnessTarget = Math.min(SLOT_ROLES.length, Math.max(RICHNESS_MIN_IMAGES, dino.imageSlots));
  const expansionSelected = [];
  for (const role of SLOT_ROLES.slice(dino.imageSlots, richnessTarget)) {
    expansionSelected.push({ role, picked: selectCandidate(candidates, usedSources, role, null) });
  }
  const expansionSlots = expansionSelected.map(({ role, picked }) => {
    const source = normalizePath(picked?.item?.src || "");
    const suggestedUnregistered = source ? null : suggestUnregisteredSource(availableUnregisteredAssets, role.key);
    const status = source
      ? "candidate-review"
      : suggestedUnregistered
        ? "unregistered-review"
        : "generate";
    return {
      slot: role.slot,
      role: role.key,
      label: role.label,
      expectedKind: role.kind,
      status,
      currentKind: picked?.item?.kind || "",
      currentSource: source,
      currentTitle: picked?.item?.title || "",
      score: picked?.score ?? null,
      selectedBy: picked?.selectedBy || "",
      suggestedUnregisteredSource: suggestedUnregistered?.source || "",
      suggestedUnregisteredScore: suggestedUnregistered?.score ?? null,
      referenceSource,
      prompt: makePrompt({ dino, role, identity, profile, route, palette, habitat, referenceSource }),
      negativePrompt: [profile.avoid, route.reject, ...COMMON_REJECT].filter(Boolean).join("; "),
      passGate: [...identity, profile.anatomy].filter(Boolean),
      rejectGate: [profile.avoid, route.reject, ...COMMON_REJECT].filter(Boolean),
    };
  });

  return {
    taxon: dino.id,
    name: dino.name,
    koreanName: dino.koreanName,
    era: dino.era,
    period: dino.period,
    region: dino.region,
    family: dino.family,
    imageSlots: dino.imageSlots,
    richnessTarget,
    visibleCandidateCount: candidates.length,
    paletteLock: palette,
    habitatProfile: habitat,
    identityChecklistMissing: !identities[dino.id],
    malformedSamples,
    unregisteredSpeciesAssets: availableUnregisteredAssets,
    slots,
    expansionSlots,
  };
}

function buildUnregisteredAssets(dinosaurs, samples) {
  const files = fs.readdirSync(ASSET_ROOT, { withFileTypes: true }).filter((entry) => entry.isFile()).map((entry) => entry.name);
  const registered = new Set(
    Object.values(samples)
      .flat()
      .filter((item) => item && typeof item === "object")
      .map((item) => path.basename(normalizePath(item.src || item.source)))
      .filter(Boolean),
  );
  return Object.fromEntries(
    dinosaurs.map((dino) => [
      dino.id,
      files.filter((name) => name.startsWith(`${dino.id}-`) && !registered.has(name)).map((name) => `assets/dinosaurs/${name}`),
    ]),
  );
}

function writeMarkdown(plan) {
  const lines = [
    "# Dino Atlas Gallery Slot Generation Plan",
    "",
    `Generated: ${plan.generatedAt}`,
    "",
    "## Summary",
    "",
    `- Taxa: ${plan.summary.taxa}`,
    `- Target slots: ${plan.summary.targetSlots}`,
    `- Richness target slots (minimum ${RICHNESS_MIN_IMAGES} per taxon): ${plan.summary.richnessTargetSlots}`,
    `- Taxa already publishing at least ${RICHNESS_MIN_IMAGES} slots: ${plan.summary.taxaAtPublishedTarget}`,
    `- Expansion slots ready for candidate review: ${plan.summary.expansionCandidateReviewSlots}`,
    `- Expansion slots with unregistered suggestions: ${plan.summary.expansionUnregisteredReviewSlots}`,
    `- Expansion slots requiring generation: ${plan.summary.expansionGenerateSlots}`,
    `- Visually approved slots: ${plan.summary.approvedSlots}`,
    `- Slots pending visual review: ${plan.summary.pendingVisualReview}`,
    `- Visual decision errors: ${plan.summary.visualDecisionErrors}`,
    `- Slots with selected registered candidates: ${plan.summary.selectedRegistered}`,
    `- Slots with suggested unregistered candidates: ${plan.summary.unregisteredReviewSlots}`,
    `- Slots requiring generation: ${plan.summary.generateSlots}`,
    `- Taxa with generation slots: ${plan.summary.taxaWithGenerateSlots}`,
    `- Missing real asset paths: ${plan.summary.missingAssetPaths}`,
    `- Missing identity checklists: ${plan.summary.missingIdentityChecklists}`,
    `- Malformed sample values: ${plan.summary.malformedSampleValues}`,
    "",
    "## Generation Queue",
    "",
    "| Taxon | Slot | Role | Registered candidate | Suggested unregistered candidate |",
    "|---|---:|---|---|---|",
  ];
  for (const taxon of plan.taxa) {
    for (const slot of taxon.slots.filter((item) => item.status !== "approved")) {
      lines.push(`| ${taxon.taxon} | ${slot.slot} | ${slot.role} | ${slot.currentSource || "none"} | ${slot.suggestedUnregisteredSource || "none"} |`);
    }
  }
  lines.push("", `## ${RICHNESS_MIN_IMAGES}-Image Richness Expansion Queue`, "");
  lines.push(
    "| Taxon | Current slots | Target | Slot | Role | Status | Registered candidate | Suggested unregistered candidate |",
    "|---|---:|---:|---:|---|---|---|---|",
  );
  for (const taxon of plan.taxa) {
    for (const slot of taxon.expansionSlots) {
      lines.push(`| ${taxon.taxon} | ${taxon.imageSlots} | ${taxon.richnessTarget} | ${slot.slot} | ${slot.role} | ${slot.status} | ${slot.currentSource || "none"} | ${slot.suggestedUnregisteredSource || "none"} |`);
    }
  }
  lines.push("", "## Data Hygiene", "");
  for (const taxon of plan.taxa.filter((item) => item.identityChecklistMissing || item.malformedSamples.length)) {
    lines.push(`- ${taxon.taxon}: identityMissing=${taxon.identityChecklistMissing}; malformedSamples=${taxon.malformedSamples.length}`);
  }
  lines.push("");
  fs.writeFileSync(OUTPUT_MD, `${lines.join("\n")}\n`, "utf8");
}

function writeAssignments(plan) {
  const assignments = Object.fromEntries(
    plan.taxa.map((taxon) => [
      taxon.taxon,
      taxon.slots
        .filter((slot) => slot.status === "approved" && slot.currentSource)
        .map((slot) => ({
          source: slot.currentSource,
          gallerySlot: slot.slot,
          galleryRole: slot.role,
          phenotype: slot.slot === 2 ? "variant-b" : "canonical-a",
          habitatKey: taxon.habitatProfile.key,
          expectedKind: slot.expectedKind,
        })),
    ]),
  );
  const body = [
    "// Generated by tools/comfyui/scripts/build_gallery_slot_plan.mjs.",
    "// Existing candidates remain in generatedImageSamples; only assigned sources enter the final gallery.",
    `window.gallerySlotAssignments = ${JSON.stringify(assignments, null, 2)};`,
    "",
  ].join("\n");
  fs.writeFileSync(OUTPUT_ASSIGNMENTS, body, "utf8");
}

function main() {
  const source = fs.readFileSync(APP_JS, "utf8");
  const dinosaurs = loadLiteral(source, "dinosaurs");
  const samples = loadLiteral(source, "generatedImageSamples");
  const identities = loadLiteral(source, "identityChecklists");
  const profiles = loadLiteral(source, "visualVariationProfiles");
  const routes = loadLiteral(source, "generationRouteGuides");
  const swatches = loadLiteral(source, "taxonPaletteSwatches");
  const decisions = loadJsonIfPresent(VISUAL_DECISIONS, { taxa: {}, rejectedSources: {} });
  const rejectionManifest = loadJsonIfPresent(REJECTIONS_JSON, { rejectedSources: {} });
  const rejectedSources = new Set([
    ...Object.keys(decisions.rejectedSources || {}),
    ...Object.keys(rejectionManifest.rejectedSources || {}),
  ].map(normalizePath));
  const unregisteredAssets = buildUnregisteredAssets(dinosaurs, samples);
  const taxa = dinosaurs.map((dino) => makePlanItem({
    dino,
    samples,
    identities,
    profiles,
    routes,
    swatches,
    unregisteredAssets,
    decisions,
    rejectedSources,
  }));
  const selectedRegistered = taxa.flatMap((taxon) => taxon.slots).filter((slot) => slot.currentSource).length;
  const approvedSlots = taxa.flatMap((taxon) => taxon.slots).filter((slot) => slot.status === "approved").length;
  const pendingVisualReview = taxa.flatMap((taxon) => taxon.slots).filter((slot) => !["approved", "decision-error"].includes(slot.status)).length;
  const visualDecisionErrors = taxa.flatMap((taxon) => taxon.slots).filter((slot) => slot.status === "decision-error").length;
  const generateSlots = taxa.flatMap((taxon) => taxon.slots).filter((slot) => slot.status === "generate").length;
  const unregisteredReviewSlots = taxa.flatMap((taxon) => taxon.slots).filter((slot) => slot.status === "manual-review-unregistered").length;
  const expansionSlots = taxa.flatMap((taxon) => taxon.expansionSlots);
  const missingPaths = Object.values(samples)
    .flat()
    .filter((item) => item && typeof item === "object")
    .map((item) => normalizePath(item.src || item.source))
    .filter((relative) => relative.startsWith("assets/dinosaurs/") && !fs.existsSync(path.join(ROOT, relative)));
  const plan = {
    schemaVersion: 2,
    generatedAt: new Date().toISOString(),
    source: "app.js",
    goal: "tools/comfyui/dino-slot-aware-image-generation-goal.md",
    summary: {
      taxa: taxa.length,
      targetSlots: taxa.reduce((total, taxon) => total + taxon.imageSlots, 0),
      richnessTargetSlots: taxa.reduce((total, taxon) => total + taxon.richnessTarget, 0),
      taxaAtPublishedTarget: taxa.filter((taxon) => taxon.imageSlots >= RICHNESS_MIN_IMAGES).length,
      taxaWithEnoughVisibleCandidates: taxa.filter((taxon) => taxon.visibleCandidateCount >= RICHNESS_MIN_IMAGES).length,
      expansionCandidateReviewSlots: expansionSlots.filter((slot) => slot.status === "candidate-review").length,
      expansionUnregisteredReviewSlots: expansionSlots.filter((slot) => slot.status === "unregistered-review").length,
      expansionGenerateSlots: expansionSlots.filter((slot) => slot.status === "generate").length,
      taxaWithExpansionGeneration: taxa.filter((taxon) => taxon.expansionSlots.some((slot) => slot.status === "generate")).length,
      approvedSlots,
      pendingVisualReview,
      visualDecisionErrors,
      selectedRegistered,
      unregisteredReviewSlots,
      generateSlots,
      taxaWithGenerateSlots: taxa.filter((taxon) => taxon.slots.some((slot) => slot.status === "generate")).length,
      missingAssetPaths: new Set(missingPaths).size,
      missingIdentityChecklists: taxa.filter((taxon) => taxon.identityChecklistMissing).length,
      malformedSampleValues: taxa.reduce((total, taxon) => total + taxon.malformedSamples.length, 0),
      unregisteredSpeciesAssets: taxa.reduce((total, taxon) => total + taxon.unregisteredSpeciesAssets.length, 0),
      rejectedSources: rejectedSources.size,
    },
    taxa,
  };

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(OUTPUT_JSON, `${JSON.stringify(plan, null, 2)}\n`, "utf8");
  writeMarkdown(plan);
  writeAssignments(plan);
  console.log(JSON.stringify(plan.summary, null, 2));
}

main();
