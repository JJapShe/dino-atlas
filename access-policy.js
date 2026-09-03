(function configureDinoAtlasAccessPolicy(global) {
  const freeTaxonIds = [
    "mammuthus-primigenius",
    "smilodon-fatalis",
    "anomalocaris-canadensis",
    "dunkleosteus-terrelli",
    "otodus-megalodon",
    "dimetrodon-grandis",
    "archaeopteryx-lithographica",
    "asteroceras-obtusum",
    "allosaurus-fragilis",
    "dilophosaurus-wetherilli",
    "pterodactylus-antiquus",
    "pteranodon-longiceps",
    "quetzalcoatlus-northropi",
    "mosasaurus-hoffmannii",
    "apatosaurus-ajax",
    "diplodocus-carnegiei",
    "brachiosaurus-altithorax",
    "stegosaurus-stenops",
    "tyrannosaurus-rex",
    "carnotaurus-sastrei",
    "giganotosaurus-carolinii",
    "spinosaurus-aegyptiacus",
    "therizinosaurus-cheloniformis",
    "tarbosaurus-bataar",
    "velociraptor-mongoliensis",
    "triceratops-horridus",
    "iguanodon-bernissartensis",
    "parasaurolophus-walkeri",
    "pachycephalosaurus-wyomingensis",
    "ankylosaurus-magniventris",
  ];

  global.dinoAtlasAccessPolicy = Object.freeze({
    schemaVersion: "dino-atlas-access-v1",
    defaultTier: "subscriber",
    freeTaxonIds: Object.freeze(freeTaxonIds),
    tiers: Object.freeze({
      free: Object.freeze({
        label: "무료 탐험",
        catalogScope: "free",
      }),
      subscriber: Object.freeze({
        label: "전체 도감",
        catalogScope: "all",
      }),
    }),
  });
})(globalThis);
