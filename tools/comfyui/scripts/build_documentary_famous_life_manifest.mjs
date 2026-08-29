import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

const scriptPath = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(scriptPath), "../../..");
const outputJsonPath = path.join(
  repoRoot,
  "tools/comfyui/documentary-famous-life-expansion-20260811.json",
);
const outputMarkdownPath = path.join(
  repoRoot,
  "tools/comfyui/documentary-famous-life-expansion-20260811.md",
);

const defaultSessionPath =
  "C:/Users/USER/.codex/sessions/2026/08/01/rollout-2026-08-01T23-02-43-019fbda2-6313-7010-a45d-5c6c6e3f5169.jsonl";
const defaultPrivateImageRoot =
  "C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169";
const sessionPath = path.resolve(process.argv[2] ?? defaultSessionPath);
const privateImageRoot = path.resolve(process.argv[3] ?? defaultPrivateImageRoot);

const commonLicense =
  "Original project-generated bitmap under the applicable OpenAI service terms. Factual scientific and museum sources supplied anatomy and uncertainty constraints only; no external artwork, published reconstruction, franchise frame, documentary frame, or named-artist style was used as a generation input.";
const commonSourceAttribution =
  "OpenAI built-in image generation from an original Dino Atlas prompt; project-owned generated images were used only where referenceImages records them.";

const acceptedSpecs = [
  {
    key: "arthropleura-armata-representative-v1",
    taxonId: "arthropleura-armata",
    taxon: "Arthropleura armata",
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    representativeEligible: true,
    callId: "exec-f7a3f98b-28e8-4d22-881c-766a77006a65",
    projectPath:
      "assets/dinosaurs/arthropleura-armata-diplosegment-stalkedeye-representative-imagegen-v1.png",
    references: [],
    workflow:
      "Fossil-led prompt-to-image followed by original-size antenna, stalked-eye, diplotergite, paired-leg-row, body-continuity, crop, text and watermark review.",
    reviewDecision:
      "Approved as the sole S1 count-level representative. The full body, paired antennae, paired stalked eyes, broad divided tergites, dense successive leg pairs and one terminal end remain readable.",
    claimBoundary:
      "The head cues derive from smaller Arthropleura material and remain genus-level guidance rather than certainty for an adult A. armata head; adult head proportions, color and diet are not established.",
  },
  {
    key: "arthropleura-armata-pattern-v1",
    taxonId: "arthropleura-armata",
    taxon: "Arthropleura armata",
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    representativeEligible: false,
    callId: "exec-99d84761-bbb4-475a-895d-23a06ebb0f31",
    projectPath:
      "assets/dinosaurs/arthropleura-armata-highthreequarter-copper-moss-pattern-imagegen-v1.png",
    references: ["exec-f7a3f98b-28e8-4d22-881c-766a77006a65"],
    workflow:
      "Project-owned S1 identity reference, composition-diversity prompt, then original-size appendage, plate, body-continuity, crop and artifact review.",
    reviewDecision:
      "Accepted only as S2 review hold. The high three-quarter view diversifies direction and color while retaining gross tergite and paired-leg-row continuity.",
    claimBoundary:
      "Perspective, distal leg count, adult head proportions, copper/moss color and every marking location are reconstructed; representative promotion is prohibited without a separate anatomy audit.",
  },
  {
    key: "arthropleura-armata-ecology-v1",
    taxonId: "arthropleura-armata",
    taxon: "Arthropleura armata",
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    representativeEligible: false,
    callId: "exec-300725a2-2ac7-43b1-aae8-361a49f787ee",
    projectPath:
      "assets/dinosaurs/arthropleura-armata-meganeura-floodplain-ecology-imagegen-v1.png",
    references: [
      "exec-f7a3f98b-28e8-4d22-881c-766a77006a65",
      "exec-504155d7-ada5-4116-819f-f602481a1ec2",
    ],
    workflow:
      "Project-owned Arthropleura and Meganeura identity references, wide non-contact ecology prompt, then original-size focal-body, leg-row, background-fauna separation and non-patterned substrate review.",
    reviewDecision:
      "Accepted only as S3 anatomy review. The focal Arthropleura remains readable and the distant griffinfly is spatially separate.",
    claimBoundary:
      "Broad Carboniferous co-occurrence is illustrative; no observed interaction, exact community, track maker, behavior or species-level encounter is asserted, and the distant griffinfly is not count-level evidence.",
  },
  {
    key: "meganeura-monyi-representative-v1",
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    representativeEligible: true,
    callId: "exec-504155d7-ada5-4116-819f-f602481a1ec2",
    projectPath:
      "assets/dinosaurs/meganeura-monyi-fourwing-sixleg-representative-imagegen-v1.png",
    references: [],
    workflow:
      "Fossil-led prompt-to-image followed by original-size four-wing, six-leg, thoracic-attachment, abdomen, crop, text and watermark review.",
    reviewDecision:
      "Approved as the sole S1 count-level representative. Exactly four independently rooted wings and six thoracic legs are readable at original size.",
    claimBoundary:
      "Wing fossils constrain the broad venation direction; complete soft anatomy, exact body proportions, color and the pictured flight/rest pose remain reconstructed.",
  },
  {
    key: "meganeura-monyi-samebody-pattern-v1",
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    representativeEligible: false,
    callId: "exec-d7ce0dda-f6de-4166-a344-037b4d8aaef9",
    projectPath:
      "assets/dinosaurs/meganeura-monyi-petrol-copper-samebody-pattern-imagegen-v1.png",
    references: ["exec-504155d7-ada5-4116-819f-f602481a1ec2"],
    workflow:
      "Targeted same-body edit of the project-owned S1, preserving its composition and anatomy while changing only speculative color and pattern, followed by original-size four-wing, six-leg, attachment, crop and artifact review.",
    reviewDecision:
      "Accepted only as S2 review hold. The complete animal preserves exactly four independently rooted wings, six thoracic legs and the S1 body while supplying a petrol/copper color-pattern variant.",
    claimBoundary:
      "Color, pattern and every marking location are hypothetical. This same-body variant must never replace or outrank the S1 representative without a separate anatomy-promotion audit.",
  },
  {
    key: "meganeura-monyi-ecology-v1",
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    representativeEligible: false,
    callId: "exec-4df05505-79d0-41f7-91bc-67ca54361af1",
    projectPath:
      "assets/dinosaurs/meganeura-monyi-arthropleura-wetland-ecology-imagegen-v1.png",
    references: [
      "exec-504155d7-ada5-4116-819f-f602481a1ec2",
      "exec-f7a3f98b-28e8-4d22-881c-766a77006a65",
    ],
    workflow:
      "Project-owned Meganeura and Arthropleura identity references, wide non-contact ecology prompt, then original-size focal four-wing/six-leg and background-fauna separation review.",
    reviewDecision:
      "Accepted only as S3 anatomy review. The focal griffinfly keeps four wings and six thoracic legs; the distant myriapod remains non-contact context.",
    claimBoundary:
      "Flight, exact spacing, plant community and broad co-occurrence are illustrative. No direct interaction is asserted, and the distant Arthropleura is not count-level evidence.",
  },
  {
    key: "inostrancevia-alexandri-representative-v1",
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    representativeEligible: true,
    callId: "exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa",
    projectPath:
      "assets/dinosaurs/inostrancevia-alexandri-lowskull-saberpair-representative-imagegen-v1.png",
    references: [],
    workflow:
      "Fossil-led prompt-to-image followed by original-size skull, single upper-saber-pair, four-limb, foot, tail-continuity, crop and mammal-drift review.",
    reviewDecision:
      "Approved as the sole S1 count-level representative. The elongate skull, one enlarged upper-canine pair, four connected limbs and one tail are readable.",
    claimBoundary:
      "Skull and saber cues are fossil-led; external soft tissue, skin covering, exact foot appearance, stance, color and behavior remain reconstructed.",
  },
  {
    key: "inostrancevia-alexandri-samebody-pattern-v1",
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    representativeEligible: false,
    callId: "exec-4d3e66e8-4c28-477b-864a-cb098b40744d",
    projectPath:
      "assets/dinosaurs/inostrancevia-alexandri-charcoal-sienna-samebody-pattern-imagegen-v1.png",
    references: ["exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa"],
    workflow:
      "Targeted same-body edit of the project-owned S1, preserving its composition and anatomy while changing only speculative color and pattern, followed by original-size saber-pair, four-limb, four-foot, tail, crop and artifact review.",
    reviewDecision:
      "Accepted only as S2 review hold. The complete animal preserves one enlarged upper-saber pair, four connected limbs, four feet and the S1 body while supplying a charcoal/sienna color-pattern variant.",
    claimBoundary:
      "Color, pattern, skin texture and every marking location are hypothetical. This same-body variant must never replace or outrank the S1 representative without a separate anatomy-promotion audit.",
  },
  {
    key: "inostrancevia-alexandri-ecology-v1",
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    representativeEligible: false,
    callId: "exec-ac631898-538c-4482-920f-ff70d70ada27",
    projectPath:
      "assets/dinosaurs/inostrancevia-alexandri-seasonal-channel-ecology-imagegen-v1.png",
    references: ["exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa"],
    workflow:
      "Project-owned S1 identity reference, wide seasonal-channel ecology prompt, then original-size four-limb, four-foot, tail, saber, crop and habitat-artifact review.",
    reviewDecision:
      "Accepted only as S3 anatomy review. The single animal remains complete and readable in a distinct wide habitat composition.",
    claimBoundary:
      "The exact gait, skin, plants, seasonal channel, weather and behavioral moment are hypothetical; representative promotion is prohibited without a separate anatomy audit.",
  },
  {
    key: "titanoboa-cerrejonensis-representative-v1",
    taxonId: "titanoboa-cerrejonensis",
    taxon: "Titanoboa cerrejonensis",
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    representativeEligible: true,
    callId: "exec-c9a68e46-8771-49ca-802b-e82ff57c5839",
    projectPath:
      "assets/dinosaurs/titanoboa-cerrejonensis-continuous-boid-representative-imagegen-v1.png",
    references: [],
    workflow:
      "Fossil-led prompt-to-image followed by original-size single-head, continuous non-crossing body, one-tail, limbless, crop, modern-snake-copy and artifact review.",
    reviewDecision:
      "Approved as the sole S1 count-level representative. The complete limbless silhouette can be traced continuously from one head through broad curves to one tail.",
    claimBoundary:
      "Vertebrae and limited cranial remains support a giant boid; exact head shape, full-body proportions, muscle profile, scales, color and pattern remain reconstructed.",
  },
  {
    key: "titanoboa-cerrejonensis-pattern-v1",
    taxonId: "titanoboa-cerrejonensis",
    taxon: "Titanoboa cerrejonensis",
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    representativeEligible: false,
    callId: "exec-25d67b5e-6b4a-4277-9250-dcf4284fdbdc",
    projectPath:
      "assets/dinosaurs/titanoboa-cerrejonensis-highoblique-channel-pattern-imagegen-v1.png",
    references: ["exec-c9a68e46-8771-49ca-802b-e82ff57c5839"],
    workflow:
      "Project-owned S1 identity reference, high-oblique color/composition prompt, then original-size head-to-tail continuity, loop, crop and modern-pattern-drift review.",
    reviewDecision:
      "Accepted only as S2 review hold. The oblique channel view remains traceable from one head to one tail and supplies a non-repeating speculative pattern variant.",
    claimBoundary:
      "Perspective, exact proportions, color and markings are hypothetical; the image cannot outrank S1 without a separate anatomy-promotion review.",
  },
  {
    key: "titanoboa-cerrejonensis-ecology-v1",
    taxonId: "titanoboa-cerrejonensis",
    taxon: "Titanoboa cerrejonensis",
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    representativeEligible: false,
    callId: "exec-d27b3439-ecc9-4bd8-963a-15816892b290",
    projectPath:
      "assets/dinosaurs/titanoboa-cerrejonensis-distant-turtle-ecology-imagegen-v1.png",
    references: ["exec-c9a68e46-8771-49ca-802b-e82ff57c5839"],
    workflow:
      "Project-owned S1 identity reference, non-contact Cerrejon ecology prompt, then original-size body-continuity, turtle separation, crop, attack and artifact review.",
    reviewDecision:
      "Accepted only as S3 anatomy review. One traceable Titanoboa and a distant non-diagnostic turtle remain spatially separate with no attack.",
    claimBoundary:
      "The turtle is fauna context only. No prey choice, chase, constriction, exact encounter, body-size relationship or observed behavior is asserted.",
  },
  {
    key: "basilosaurus-isis-representative-v1",
    taxonId: "basilosaurus-isis",
    taxon: "Basilosaurus isis",
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    representativeEligible: true,
    callId: "exec-5ece7103-20eb-45ef-9436-3717c94e3101",
    projectPath:
      "assets/dinosaurs/basilosaurus-isis-longbody-tinyhindlimb-representative-imagegen-v1.png",
    references: ["exec-28f11e33-cab7-4f6b-89d7-09756265ecda"],
    workflow:
      "Targeted edit of a project-generated draft to replace its vertical fish-like tail with a small horizontal fluke, followed by original-size skull, two-foreflipper, paired-tiny-hind-limb, no-dorsal-fin, tail and crop review.",
    reviewDecision:
      "Approved as the sole S1 count-level representative after tail correction. The long archaeocete body, two foreflippers, two tiny pelvic hind limbs and small horizontal fluke are readable.",
    claimBoundary:
      "Skull, elongate axial body and tiny hind limbs are fossil-led; the external horizontal fluke is a conservative comparative reconstruction and exact soft tissues, color and swimming pose remain hypothetical.",
  },
  {
    key: "basilosaurus-isis-pattern-v1",
    taxonId: "basilosaurus-isis",
    taxon: "Basilosaurus isis",
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    representativeEligible: false,
    callId: "exec-52dcc934-c4bc-4d27-a165-a2dc18e554dd",
    projectPath:
      "assets/dinosaurs/basilosaurus-isis-ventral-ascent-petrol-pattern-imagegen-v1.png",
    references: ["exec-5ece7103-20eb-45ef-9436-3717c94e3101"],
    workflow:
      "Project-owned corrected S1 identity reference, ventral-ascent color/composition prompt, then original-size appendage, horizontal-fluke, crop, reptile/fish-drift and artifact review.",
    reviewDecision:
      "Accepted only as S2 review hold. The distinct ascent composition retains the long body, paired foreflippers, tiny paired hind limbs and small horizontal fluke.",
    claimBoundary:
      "Perspective, skin color, mottling, lighting and locomotor moment are hypothetical; representative promotion is prohibited without a separate anatomy audit.",
  },
  {
    key: "basilosaurus-isis-ecology-v1",
    taxonId: "basilosaurus-isis",
    taxon: "Basilosaurus isis",
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    representativeEligible: false,
    callId: "exec-b29639aa-3655-4841-b4dd-56a3814e610a",
    projectPath:
      "assets/dinosaurs/basilosaurus-isis-fishschool-tethys-ecology-imagegen-v1.png",
    references: [
      "exec-60680e54-90d0-49ef-9362-242d2b3b84de",
      "exec-5ece7103-20eb-45ef-9436-3717c94e3101",
    ],
    workflow:
      "Targeted correction of a project-generated ecology draft using corrected S1 as anatomy control, then original-size appendage, small horizontal-fluke, fish-school separation, crop and attack review.",
    reviewDecision:
      "Accepted only as S3 anatomy review after tail repair. The complete whale and distant loose fish school remain separate with no chase or bite.",
    claimBoundary:
      "Fish are non-diagnostic context. Seafloor community, exact place, schooling response, diet event, pursuit and encounter are not established by the image.",
  },
  {
    key: "paraceratherium-transouralicum-representative-v1",
    taxonId: "paraceratherium-transouralicum",
    taxon: "Paraceratherium transouralicum",
    slot: 1,
    role: "representative",
    kind: "count-level pass",
    representativeEligible: true,
    callId: "exec-fd17ae3d-fce7-4a40-bf68-09cba3529697",
    projectPath:
      "assets/dinosaurs/paraceratherium-transouralicum-hornless-longneck-representative-imagegen-v1.png",
    references: [],
    workflow:
      "Fossil-led prompt-to-image followed by original-size hornless-head, neck, four-limb, four-foot, tail, elephant/giraffe/sauropod drift, crop and artifact review.",
    reviewDecision:
      "Approved as the sole S1 count-level representative. The hornless elongated head, long muscular neck, deep body, four sturdy limbs, four feet and one short tail are readable.",
    claimBoundary:
      "Fossils constrain the giant hornless rhinocerotoid body plan; exact mass, proportions, mobile lip, soft tissue, coat, foot visibility, color and pose retain reconstruction uncertainty.",
  },
  {
    key: "paraceratherium-transouralicum-pattern-v1",
    taxonId: "paraceratherium-transouralicum",
    taxon: "Paraceratherium transouralicum",
    slot: 2,
    role: "color-pattern",
    kind: "review hold",
    representativeEligible: false,
    callId: "exec-722f8226-1f3c-46a6-8291-ed8e4612023a",
    projectPath:
      "assets/dinosaurs/paraceratherium-transouralicum-frontthreequarter-fourfoot-pattern-imagegen-v1.png",
    references: ["exec-fd17ae3d-fce7-4a40-bf68-09cba3529697"],
    workflow:
      "Project-owned S1 identity reference, front-three-quarter reroute after a rear-view foot-continuity failure, then original-size four-limb, four-foot, neck, tail, crop and taxon-drift review.",
    reviewDecision:
      "Accepted only as S2 review hold. The front three-quarter view keeps four connected legs and four separated feet readable while diversifying composition and color.",
    claimBoundary:
      "Perspective, exact foot digit visibility, color, pattern and soft tissue are hypothetical; representative promotion is prohibited without a separate anatomy audit.",
  },
  {
    key: "paraceratherium-transouralicum-ecology-v1",
    taxonId: "paraceratherium-transouralicum",
    taxon: "Paraceratherium transouralicum",
    slot: 3,
    role: "habitat-ecology",
    kind: "anatomy review",
    representativeEligible: false,
    callId: "exec-326ad5ef-f82d-4e38-b8fe-59c925226490",
    projectPath:
      "assets/dinosaurs/paraceratherium-transouralicum-high-browse-ecology-imagegen-v1.png",
    references: ["exec-fd17ae3d-fce7-4a40-bf68-09cba3529697"],
    workflow:
      "Project-owned S1 identity reference, wide high-browse ecology prompt, then original-size hornless-head, four-limb, four-foot, branch separation, crop and artifact review.",
    reviewDecision:
      "Accepted only as S3 anatomy review. One complete animal remains readable while browsing from a high branch in a distinct wide setting.",
    claimBoundary:
      "High browsing is a functional ecological reconstruction; exact plant taxon, feeding event, reach, posture, site, season and soft tissue are hypothetical.",
  },
];

const rejectedSpecs = [
  {
    taxonId: "arthropleura-armata",
    taxon: "Arthropleura armata",
    intendedRole: "S1 representative",
    callId: "exec-e9d46802-2c2c-472c-aef0-fe71e3741efe",
    references: [],
    reason:
      "Superseded after the 2024 head evidence review: the prompt and output used an obsolete plain rounded head/no-large-eye boundary and did not preserve the paired stalked-eye plus diplotergite two-successive-leg-pair gate required by the corrected S1 route.",
    disposition:
      "Never copied; replaced by exec-f7a3f98b after a fossil-led identity correction.",
  },
  {
    taxonId: "arthropleura-armata",
    taxon: "Arthropleura armata",
    intendedRole: "S2 color-pattern",
    callId: "exec-970907d4-ea26-4f2c-878c-ef150165754c",
    references: ["exec-e9d46802-2c2c-472c-aef0-fe71e3741efe"],
    reason:
      "Inherited the rejected first S1's obsolete plain-head identity boundary, so it could not remain in the gallery after the stalked-eye and diplotergite correction.",
    disposition:
      "Never copied; regenerated from corrected S1 as exec-99d84761.",
  },
  {
    taxonId: "arthropleura-armata",
    taxon: "Arthropleura armata",
    intendedRole: "S3 habitat-ecology",
    callId: "exec-09769592-eabd-4ffb-bd8f-2e96bbabb0ee",
    references: ["exec-e9d46802-2c2c-472c-aef0-fe71e3741efe"],
    reason:
      "Inherited the rejected first S1's obsolete head and trunk/leg identity boundary; broad ecology value did not override the focal-animal identity gate.",
    disposition:
      "Never copied; regenerated from corrected identities as exec-300725a2.",
  },
  {
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    intendedRole: "S1 representative",
    callId: "exec-9dc10616-169f-405c-91e3-76e7cdc43d9e",
    references: [],
    reason:
      "Failed the original-size appendage gate: four independently connected wing roots and exactly six separately connected thoracic legs were not all reliably countable.",
    disposition:
      "Never copied; a stricter count-layout route followed.",
  },
  {
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    intendedRole: "S1 representative",
    callId: "exec-48c4dad6-d5b8-4238-8614-0616929b31d2",
    references: [],
    reason:
      "The second whole-body attempt still did not make the required four wing attachments and six thoracic legs unambiguous at original size.",
    disposition:
      "Never copied; replaced by the accepted stricter S1 exec-504155d7.",
  },
  {
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    intendedRole: "S2 color-pattern",
    callId: "exec-86d9ecf5-88c5-40d7-bdd3-933ff196f046",
    references: ["exec-504155d7-ada5-4116-819f-f602481a1ec2"],
    reason:
      "The low ventral flight attempt failed exact six-leg readability; overlapping or accessory leg-like forms made count-level use unsafe.",
    disposition:
      "Never copied; additional correction routes were tested.",
  },
  {
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    intendedRole: "S2 color-pattern",
    callId: "exec-ac000020-80f6-4be9-8771-c4a137d86b4a",
    references: ["exec-504155d7-ada5-4116-819f-f602481a1ec2"],
    reason:
      "Original-size review found seven leg-like appendages rather than exactly six thoracic legs.",
    disposition:
      "Never copied; used only as the private edit base for exec-c7fabaa3.",
  },
  {
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    intendedRole: "S2 color-pattern repair",
    callId: "exec-c7fabaa3-d3b8-4bb9-951f-518fa018b079",
    references: [
      "exec-ac000020-80f6-4be9-8771-c4a137d86b4a",
      "exec-504155d7-ada5-4116-819f-f602481a1ec2",
    ],
    reason:
      "The targeted seventh-leg repair still did not yield six fully separate, unambiguous thoracic legs without attachment/fusion uncertainty.",
    disposition:
      "Never copied; the free-pose route was abandoned in favor of accepted same-body S2 edit exec-d7ce0dda.",
  },
  {
    taxonId: "meganeura-monyi",
    taxon: "Meganeura monyi",
    intendedRole: "S2 color-pattern",
    callId: "exec-efe5d7d9-e81d-466d-a22b-fb9a3867e26b",
    references: ["exec-504155d7-ada5-4116-819f-f602481a1ec2"],
    formerProjectPath:
      "assets/dinosaurs/meganeura-monyi-dorsal-wingbase-petrol-copper-structure-imagegen-v1.png",
    reason:
      "The cropped dorsal close-up was useful for four wing-root structure and color only, but it showed no legs and omitted wing tips/body extent, so it violated the fixed same-body full-body S2 color-pattern contract.",
    disposition:
      "Temporarily copied and classified as structure reference, then superseded and removed from runtime by accepted same-body S2 exec-d7ce0dda.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    intendedRole: "S1 representative",
    callId: "exec-08daa434-e18c-49a8-8a7a-00c903794523",
    references: [],
    reason:
      "The first side-profile attempt did not keep the saber pair, all four connected limbs/feet and complete tail sufficiently unambiguous for the count-level identity gate.",
    disposition:
      "Never copied; replaced by the stricter S1 exec-a6c3a903.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    intendedRole: "S2 color-pattern",
    callId: "exec-7ed9e867-2522-48fe-9ded-c3db55a4d9fe",
    references: ["exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa"],
    reason:
      "The rear three-quarter route did not make all four connected feet and their five-digit groups reliably readable; no color variant may bypass the limb/foot gate.",
    disposition:
      "Never copied; another full-body route was tested.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    intendedRole: "S2 color-pattern",
    callId: "exec-603f66bd-f8ad-433d-81b0-658d447eba33",
    references: ["exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa"],
    reason:
      "The elevated full-body attempt again failed the four separate pentadactyl-foot readability requirement through occlusion, fusion or uncertain toe counts.",
    disposition:
      "Never copied; a flatter count-layout route was tested.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    intendedRole: "S2 color-pattern",
    callId: "exec-ea848bd8-b0c1-444b-941a-21f567a73ef7",
    references: ["exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa"],
    reason:
      "Even with separated ground patches, all four five-toed feet were not simultaneously trustworthy at original size.",
    disposition:
      "Never copied; the free-pose route was abandoned in favor of accepted same-body S2 edit exec-4d3e66e8.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    taxon: "Inostrancevia alexandri",
    intendedRole: "S2 color-pattern",
    callId: "exec-094c6e07-7d24-4ae9-92ea-c996eb41382e",
    references: ["exec-a6c3a903-b9fa-4ca8-a0ad-07d8f25a13fa"],
    formerProjectPath:
      "assets/dinosaurs/inostrancevia-alexandri-headneck-saberpair-color-structure-imagegen-v1.png",
    reason:
      "The cropped head-neck close-up was useful for color, texture and the upper saber pair only, but it contained no limbs, feet or full body, so it violated the fixed same-body full-body S2 color-pattern contract.",
    disposition:
      "Temporarily copied and classified as structure reference, then superseded and removed from runtime by accepted same-body S2 exec-4d3e66e8.",
  },
  {
    taxonId: "titanoboa-cerrejonensis",
    taxon: "Titanoboa cerrejonensis",
    intendedRole: "S1 representative",
    callId: "exec-54a3dfb1-d26c-4695-8565-8d8e713ad5e6",
    references: [],
    reason:
      "The first bank-and-water route did not keep the entire head-to-tail body path continuously traceable through every bend at original size.",
    disposition:
      "Never copied; replaced by the stricter continuous-body S1 exec-c9a68e46.",
  },
  {
    taxonId: "titanoboa-cerrejonensis",
    taxon: "Titanoboa cerrejonensis",
    intendedRole: "S3 habitat-ecology",
    callId: "exec-4626d0c5-fafa-4c35-8f45-48a73c424557",
    references: ["exec-c9a68e46-8771-49ca-802b-e82ff57c5839"],
    reason:
      "The first ecology route did not keep both full snake-body continuity and distant non-contact turtle separation unambiguous enough for the ecology gate.",
    disposition:
      "Never copied; replaced by the accepted regenerated ecology scene exec-d27b3439.",
  },
  {
    taxonId: "basilosaurus-isis",
    taxon: "Basilosaurus isis",
    intendedRole: "S1 representative",
    callId: "exec-28f11e33-cab7-4f6b-89d7-09756265ecda",
    references: [],
    reason:
      "The otherwise useful first whole-body draft ended in a vertical fish-like caudal fin rather than a small horizontal archaeocete fluke.",
    disposition:
      "Never copied; retained only as the private edit base for accepted corrected S1 exec-5ece7103.",
  },
  {
    taxonId: "basilosaurus-isis",
    taxon: "Basilosaurus isis",
    intendedRole: "S3 habitat-ecology",
    callId: "exec-60680e54-90d0-49ef-9362-242d2b3b84de",
    references: ["exec-5ece7103-20eb-45ef-9436-3717c94e3101"],
    reason:
      "The first wide ecology draft repeated a caudal-fluke orientation/continuity error, so its fish-school composition could not override the tail anatomy gate.",
    disposition:
      "Never copied; retained only as the private edit base for accepted corrected S3 exec-b29639aa.",
  },
  {
    taxonId: "paraceratherium-transouralicum",
    taxon: "Paraceratherium transouralicum",
    intendedRole: "S2 color-pattern",
    callId: "exec-8e0a9271-8d79-42ca-a776-4b50cf488a04",
    references: ["exec-fd17ae3d-fce7-4a40-bf68-09cba3529697"],
    reason:
      "The rear three-quarter look-back route hid or fused a far limb/foot, producing an unreliable four-leg/four-foot read.",
    disposition:
      "Never copied; rerouted to the accepted front-three-quarter S2 exec-722f8226.",
  },
];

// Immutable file facts captured from the last canonical manifest before the
// standing complete-reject deletion policy was applied. The source JSON's
// SHA-256 was 875ed47d5e12da64bb29c38f8808267ec08817ca06af1c6e9e30870e282c89fa.
// These facts keep deleted generator inputs auditable without retaining pixels.
const rejectedPreDeletionFacts = {
  "exec-e9d46802-2c2c-472c-aef0-fe71e3741efe": { sha256: "6c878f5e64cd5a924bb7f9fe63e3bb9fb5aaf713eca763633451d5bb71c2bbfd", bytes: 2744874, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-970907d4-ea26-4f2c-878c-ef150165754c": { sha256: "2df03f704697e347785f3d944eeed512f5ec030e0ad1d0e1352d87a317920f7e", bytes: 2546124, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-09769592-eabd-4ffb-bd8f-2e96bbabb0ee": { sha256: "aace26d442ea27141f6cee7df00d3f22fd5c3d00cd3bdd250680d40fe30d6dce", bytes: 2428491, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-9dc10616-169f-405c-91e3-76e7cdc43d9e": { sha256: "6447fe6dda1d4340019419d4fa64a3382d49e8bda120412998bed64d857f3284", bytes: 2698662, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-48c4dad6-d5b8-4238-8614-0616929b31d2": { sha256: "2aa531366d4c6eb442f60ec30e5a20b7394c90c94a4ccee096d43f006b6d87d4", bytes: 2985416, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-86d9ecf5-88c5-40d7-bdd3-933ff196f046": { sha256: "f7a876d4cc56cd248a48722693c47a4713322391955eaf491a586c042b6c5673", bytes: 2575660, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-ac000020-80f6-4be9-8771-c4a137d86b4a": { sha256: "c02c587a3289dab9162fb4ad86ddc636569283156c801f6f246183b8cdc2ac89", bytes: 2051105, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-c7fabaa3-d3b8-4bb9-951f-518fa018b079": { sha256: "719f8ca16e0131fecc3a44d75ea8129519bb4b4d0f7d21c297851dfd275feeb8", bytes: 1976068, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-efe5d7d9-e81d-466d-a22b-fb9a3867e26b": { sha256: "fd346eb1fd8630b1343bee0c57e26c67548c6e4be626215349e94eff08ad5c4a", bytes: 2665670, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-08daa434-e18c-49a8-8a7a-00c903794523": { sha256: "26970f79262ae7f363e23338c1d87ed37ab01fdf101c9e34526dc4805eece44b", bytes: 2839676, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-7ed9e867-2522-48fe-9ded-c3db55a4d9fe": { sha256: "1b64c240e5756d9f222c24e090d1f6bba91ca0d01fc8df98a70048e8316bf3fb", bytes: 2961257, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-603f66bd-f8ad-433d-81b0-658d447eba33": { sha256: "ba8dfe95da32548dddfd46572eecdeb6fa947f0f25471c611f4c10c4b0f67842", bytes: 2954229, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-ea848bd8-b0c1-444b-941a-21f567a73ef7": { sha256: "66bb61819ab4ca34d4cb0f80d1cb79de96c0184f7cb02a2e0cf0bf2e62bc6a1e", bytes: 2532879, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-094c6e07-7d24-4ae9-92ea-c996eb41382e": { sha256: "045a0df604f61284cde7a249a6ff219c0c2da4c2036a3fa11566e42b4980bd98", bytes: 2632999, width: 1122, height: 1402, dimensions: "1122x1402" },
  "exec-54a3dfb1-d26c-4695-8565-8d8e713ad5e6": { sha256: "b0f6556d5cc0d3b348543f2f4b8e6c19a5bc14cf19a1c618b60a91d920099f85", bytes: 2970529, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-4626d0c5-fafa-4c35-8f45-48a73c424557": { sha256: "37f475e35393b08371389e8b2f21c647714c5969800858ad16488842facf8a4c", bytes: 2689982, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-28f11e33-cab7-4f6b-89d7-09756265ecda": { sha256: "5c68f42bcf5baf13ebda34b6568b04e95a9d17eb3c2bca63d02031e30e5aa7f0", bytes: 1791124, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-60680e54-90d0-49ef-9362-242d2b3b84de": { sha256: "5d3f80d33d711fb00821d82261938bde188bcd28733ab65257e202169ad01f85", bytes: 2264156, width: 1672, height: 941, dimensions: "1672x941" },
  "exec-8e0a9271-8d79-42ca-a776-4b50cf488a04": { sha256: "3d9d06b441bf6f25b84df97b14271bcddad9f68b83309def69c58d58a67c4bc2", bytes: 3022117, width: 1122, height: 1402, dimensions: "1122x1402" },
};

const researchSources = [
  {
    taxonId: "arthropleura-armata",
    citation:
      "Lheritier et al. 2024. The head of the largest arthropod, Arthropleura, and its phylogenetic significance. Science Advances 10:eadp6362.",
    url: "https://doi.org/10.1126/sciadv.adp6362",
    use:
      "Head, stalked-eye, antenna and mixed centipede/millipede affinity constraints; adult A. armata head extrapolation remains explicit.",
    rightsUse: "Factual and analytical reference only; no paper figure was supplied to the generator.",
  },
  {
    taxonId: "arthropleura-armata",
    citation: "Natural History Museum. Largest-ever millipede head revealed.",
    url: "https://www.nhm.ac.uk/discover/news/2024/october/largest-ever-millipede-head-revealed.html",
    use: "Museum cross-check for the newly described head and uncertainty boundary.",
    rightsUse: "Educational facts only; no museum image was supplied to the generator.",
  },
  {
    taxonId: "arthropleura-armata",
    citation: "Natural History Museum. World's largest terrestrial arthropod was a car-sized millipede.",
    url: "https://www.nhm.ac.uk/discover/news/2021/december/worlds-largest-terrestrial-arthropod-was-car-sized-millipede.html",
    use: "Size and Carboniferous terrestrial occurrence context.",
    rightsUse: "Educational facts only; no museum image was supplied to the generator.",
  },
  {
    taxonId: "meganeura-monyi",
    citation: "Museum national d'Histoire naturelle. Meganeura monyi, libellule geante.",
    url: "https://www.mnhn.fr/fr/meganeura-monyi-libellule-geante",
    use: "Museum-level identity, Commentry occurrence and giant wing-span context.",
    rightsUse: "Educational facts only; no museum image was supplied to the generator.",
  },
  {
    taxonId: "meganeura-monyi",
    citation: "Wootton et al. 2024. Integrative and Comparative Biology 64(2):598-614.",
    url: "https://academic.oup.com/icb/article/64/2/598/7687824",
    use: "Comparative griffinfly wing structure, venation and flight-boundary context.",
    rightsUse: "Factual and analytical reference only; no article figure was supplied to the generator.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    citation:
      "Kammerer et al. 2023, Current Biology, and Ivakhnenko 2008, Paleontological Journal, as recorded in the Dino Atlas taxon source list.",
    url: null,
    use: "Gorgonopsian skull, enlarged upper-canine pair, limb posture and extinction-interval context.",
    rightsUse: "Factual and analytical reference only; no publication figure was supplied to the generator.",
  },
  {
    taxonId: "inostrancevia-alexandri",
    citation: "Netflix Tudum. Life on Our Planet: What did prehistoric animals look like?",
    url: "https://www.netflix.com/tudum/articles/life-on-our-planet-what-did-dinosaurs-look-like",
    use: "Documentary-audience exposure rationale only, not an anatomical authority.",
    rightsUse: "Textual exposure check only; no documentary still or frame was supplied to the generator.",
  },
  {
    taxonId: "titanoboa-cerrejonensis",
    citation: "Head et al. 2009. Giant boid snake from the Palaeocene neotropics. Nature 457:715-717.",
    url: "https://www.nature.com/articles/nature07671",
    use: "Vertebral evidence, giant size estimate and Paleocene Cerrejon setting.",
    rightsUse: "Factual and analytical reference only; no article figure was supplied to the generator.",
  },
  {
    taxonId: "titanoboa-cerrejonensis",
    citation: "Smithsonian Institution. Titanoboa: Monster Snake.",
    url: "https://www.si.edu/exhibitions/titanoboa-monster-snake-event-event-exhib-4820",
    use: "Museum-level public identity and documentary-recognition cross-check.",
    rightsUse: "Educational facts only; no exhibit image was supplied to the generator.",
  },
  {
    taxonId: "titanoboa-cerrejonensis",
    citation: "Florida Museum. Titanoboa.",
    url: "https://www.floridamuseum.ufl.edu/science/titanoboa/",
    use: "Cerrejon fossil and rainforest context cross-check.",
    rightsUse: "Educational facts only; no museum image was supplied to the generator.",
  },
  {
    taxonId: "basilosaurus-isis",
    citation: "University of Michigan Museum of Paleontology. Basilosaurus isis.",
    url: "https://lsa.umich.edu/paleontology/resources/beyond-exhibits/basilosaurus-isis.html",
    use: "Species-level archaeocete skeleton, elongate body and reduced hind-limb context.",
    rightsUse: "Educational facts only; no museum image was supplied to the generator.",
  },
  {
    taxonId: "basilosaurus-isis",
    citation: "PBS NOVA. This massive skeleton belongs to an ancient whale.",
    url: "https://www.pbs.org/video/this-massive-skeleton-belongs-to-an-ancient-whale-xta0ta/",
    use: "Documentary-audience exposure and broad ancient-whale identity context.",
    rightsUse: "Textual exposure check only; no video frame was supplied to the generator.",
  },
  {
    taxonId: "paraceratherium-transouralicum",
    citation:
      "Deng et al. 2021. An Oligocene giant rhino provides insights into Paraceratherium evolution. Communications Biology 4:639.",
    url: "https://www.nature.com/articles/s42003-021-02170-6",
    use: "Paraceratheriid relationships, giant hornless rhinocerotoid anatomy and distribution.",
    rightsUse: "Factual and analytical reference only; no article figure was supplied to the generator.",
  },
  {
    taxonId: "paraceratherium-transouralicum",
    citation: "Natural History Museum. Why were prehistoric animals so big?",
    url: "https://www.nhm.ac.uk/discover/why-were-dinosaurs-so-big.html",
    use: "Museum educational cross-check for Paraceratherium as a giant land mammal.",
    rightsUse: "Educational facts only; no museum image was supplied to the generator.",
  },
];

const evidenceBoundaries = {
  "arthropleura-armata": {
    fossilLed:
      "Broad divided tergites, repeated diplotergites and dense leg series are fossil-led; the head cue comes from smaller Arthropleura material.",
    reconstructed:
      "Adult head proportions, exact leg visibility, soft tissue, color, pattern, gait and every living habitat moment are reconstructed.",
    promotionBoundary:
      "Only S1 is representative eligible. S2 is review hold and S3 is anatomy review.",
  },
  "meganeura-monyi": {
    fossilLed:
      "Four wings and giant archaic griffinfly venation are fossil-led; six thoracic legs follow insect anatomy.",
    reconstructed:
      "Complete body proportions, soft anatomy, coloration, wing membrane appearance, flight pose and ecology are reconstructed.",
    promotionBoundary:
      "Only S1 is representative eligible. The full-body same-body S2 is review hold and S3 is anatomy review.",
  },
  "inostrancevia-alexandri": {
    fossilLed:
      "The elongate gorgonopsian skull, differentiated teeth and one enlarged upper-canine pair are fossil-led.",
    reconstructed:
      "Skin covering, lips, external soft tissue, exact stance, feet, tail volume, color and habitat moment are reconstructed.",
    promotionBoundary:
      "Only S1 is representative eligible. The full-body same-body S2 is review hold and S3 is anatomy review.",
  },
  "titanoboa-cerrejonensis": {
    fossilLed:
      "Giant vertebrae and limited cranial material support a very large Paleocene boid.",
    reconstructed:
      "Complete head and body outline, exact proportions, scales, color, pattern, water pose and animal interactions are reconstructed.",
    promotionBoundary:
      "Only S1 is representative eligible. S2 is review hold and S3 is anatomy review.",
  },
  "basilosaurus-isis": {
    fossilLed:
      "The long skull, heterodont dentition, exceptionally elongate vertebral column, forelimbs and tiny external hind limbs are fossil-led.",
    reconstructed:
      "The external fluke is conservative comparative reconstruction; skin, color, exact appendage contours, swimming pose and fish response are hypothetical.",
    promotionBoundary:
      "Only corrected S1 is representative eligible. S2 is review hold and corrected S3 is anatomy review.",
  },
  "paraceratherium-transouralicum": {
    fossilLed:
      "Skull and postcranial fossils support a giant hornless rhinocerotoid with long neck and robust weight-bearing limbs.",
    reconstructed:
      "Exact mass, proportions, lip, coat, foot appearance, color, gait, browsing pose and vegetation are reconstructed.",
    promotionBoundary:
      "Only S1 is representative eligible. S2 is review hold and S3 is anatomy review.",
  },
};

function toPortablePath(value) {
  return value.replaceAll("\\", "/");
}

function privatePathFor(callId) {
  return path.join(privateImageRoot, `${callId}.png`);
}

function fileFacts(filePath) {
  const bytes = fs.readFileSync(filePath);
  const pngSignature = "89504e470d0a1a0a";
  if (bytes.length < 24 || bytes.subarray(0, 8).toString("hex") !== pngSignature) {
    throw new Error(`Not a valid PNG: ${filePath}`);
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  return {
    sha256: createHash("sha256").update(bytes).digest("hex"),
    bytes: bytes.length,
    width,
    height,
    dimensions: `${width}x${height}`,
  };
}

async function loadGenerationEvents(callIds) {
  const wanted = new Set(callIds);
  const events = new Map();
  const input = fs.createReadStream(sessionPath);
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line.includes('"type":"image_generation_end"')) continue;
    const callIdMarker = '"call_id":"';
    const callIdStart = line.indexOf(callIdMarker);
    if (callIdStart < 0) continue;
    const valueStart = callIdStart + callIdMarker.length;
    const valueEnd = line.indexOf('"', valueStart);
    if (valueEnd < 0 || !wanted.has(line.slice(valueStart, valueEnd))) continue;
    const row = JSON.parse(line);
    const payload = row.payload ?? {};
    if (!wanted.has(payload.call_id)) continue;
    if (payload.status !== "completed") {
      throw new Error(`Generation did not complete: ${payload.call_id}`);
    }
    if (typeof payload.revised_prompt !== "string" || !payload.revised_prompt.trim()) {
      throw new Error(`Missing revised_prompt: ${payload.call_id}`);
    }
    if (events.has(payload.call_id)) {
      throw new Error(`Duplicate generation event: ${payload.call_id}`);
    }
    events.set(payload.call_id, {
      generatedAt: row.timestamp,
      revisedPrompt: payload.revised_prompt,
    });
  }
  const missing = [...wanted].filter((callId) => !events.has(callId));
  if (missing.length) {
    throw new Error(`Generation events missing from session log: ${missing.join(", ")}`);
  }
  return events;
}

function referencePaths(callIds) {
  return callIds.map((callId) => toPortablePath(privatePathFor(callId)));
}

function referenceImageRecords(callIds) {
  const acceptedCallIds = new Set(acceptedSpecs.map((spec) => spec.callId));
  return callIds.map((callId) => {
    const privatePath = privatePathFor(callId);
    if (acceptedCallIds.has(callId)) {
      const facts = fileFacts(privatePath);
      return {
        callId,
        privateGeneratedOriginalPath: toPortablePath(privatePath),
        pixelStatus: "retained-approved-private-original",
        factScope: "current retained PNG",
        ...facts,
      };
    }
    const facts = rejectedPreDeletionFacts[callId];
    if (!facts) {
      throw new Error(`Reference call has no auditable file facts: ${callId}`);
    }
    return {
      callId,
      privateGeneratedOriginalPath: toPortablePath(privatePath),
      pixelStatus: "deleted-rejected-private-original",
      factScope: "embedded pre-deletion PNG facts",
      ...facts,
    };
  });
}

function acceptedRecord(spec, events) {
  const event = events.get(spec.callId);
  const privatePath = privatePathFor(spec.callId);
  const projectPath = path.join(repoRoot, spec.projectPath);
  const privateFacts = fileFacts(privatePath);
  const projectFacts = fileFacts(projectPath);
  if (
    privateFacts.sha256 !== projectFacts.sha256 ||
    privateFacts.bytes !== projectFacts.bytes ||
    privateFacts.dimensions !== projectFacts.dimensions
  ) {
    throw new Error(`Approved copy diverges from generated original: ${spec.key}`);
  }
  return {
    taxonId: spec.taxonId,
    taxon: spec.taxon,
    gallerySlot: spec.slot,
    galleryRole: spec.role,
    kind: spec.kind,
    status: "approved",
    representativeEligible: spec.representativeEligible,
    generatedAt: event.generatedAt,
    generator: "OpenAI built-in image generation",
    workflow: spec.workflow,
    seed: "service-assigned, not exposed",
    callId: spec.callId,
    privateGeneratedOriginalPath: toPortablePath(privatePath),
    approvedProjectPath: spec.projectPath,
    referenceImages: referencePaths(spec.references),
    referenceImageRecords: referenceImageRecords(spec.references),
    sourceAttribution: commonSourceAttribution,
    license: commonLicense,
    sha256: projectFacts.sha256,
    bytes: projectFacts.bytes,
    width: projectFacts.width,
    height: projectFacts.height,
    dimensions: projectFacts.dimensions,
    prompt: [event.revisedPrompt],
    review: {
      reviewedAt: "2026-08-11",
      method:
        "Original-size independent anatomy review plus integration-owner role and evidence-boundary review.",
      decision: spec.reviewDecision,
      claimBoundary: spec.claimBoundary,
      representativePromotionAllowed: spec.representativeEligible,
    },
  };
}

function rejectedRecord(spec, events) {
  const event = events.get(spec.callId);
  const privatePath = privatePathFor(spec.callId);
  const facts = rejectedPreDeletionFacts[spec.callId];
  if (!facts) {
    throw new Error(`Rejected source is missing embedded pre-deletion facts: ${spec.callId}`);
  }
  if (fs.existsSync(privatePath)) {
    throw new Error(`Rejected source pixels must be deleted: ${privatePath}`);
  }
  return {
    taxonId: spec.taxonId,
    taxon: spec.taxon,
    intendedRole: spec.intendedRole,
    status: spec.formerProjectPath
      ? "rejected-superseded-source-deleted"
      : "rejected-source-deleted",
    callId: spec.callId,
    generatedAt: event.generatedAt,
    privateGeneratedOriginalPath: toPortablePath(privatePath),
    copiedToProjectBeforeRejection: Boolean(spec.formerProjectPath),
    formerProjectPath: spec.formerProjectPath ?? null,
    projectCopyPresent: false,
    referencedByApp: false,
    sourceFileExpectedPresent: false,
    sourceFilePresentAtBuild: false,
    retainedInPrivateGenerationCache: false,
    pixelsRetained: false,
    referenceImages: referencePaths(spec.references),
    referenceImageRecords: referenceImageRecords(spec.references),
    generator: "OpenAI built-in image generation",
    workflow:
      "Anatomy-led generation or project-generated-reference edit followed by original-size rejection review.",
    seed: "service-assigned, not exposed",
    sourceAttribution: commonSourceAttribution,
    license: commonLicense,
    fileFactScope: "embedded pre-deletion source PNG metadata; source path verified absent",
    preDeletionFileFacts: { ...facts },
    sha256: facts.sha256,
    bytes: facts.bytes,
    width: facts.width,
    height: facts.height,
    dimensions: facts.dimensions,
    prompt: [event.revisedPrompt],
    rejectionReason: spec.reason,
    preDeletionDisposition: spec.disposition,
    deletionDisposition:
      "Rejected source PNG removed from the private generation cache under the standing complete-reject policy; the builder verifies that the exact path is absent and never performs deletion itself.",
    recoverability:
      "The PNG is not retained in git or the project. It may remain recoverable from the Windows Recycle Bin until that bin is emptied; after purge, only the exact prompt, call ID, lineage and embedded pre-deletion file facts remain.",
  };
}

function markdownFor(manifest) {
  const approvedRows = Object.entries(manifest.records)
    .map(
      ([key, record]) =>
        `| ${key} | S${record.gallerySlot} | ${record.kind} | ${record.representativeEligible ? "yes" : "no"} | ${record.dimensions} | \`${record.sha256.slice(0, 12)}...\` |`,
    )
    .join("\n");
  const rejectedRows = manifest.rejectedAttempts
    .map(
      (record) =>
        `| ${record.taxon} | ${record.intendedRole} | \`${record.callId}\` | \`${record.preDeletionFileFacts.sha256.slice(0, 12)}...\` / ${record.preDeletionFileFacts.dimensions} | ${record.rejectionReason.replaceAll("|", "\\|")} |`,
    )
    .join("\n");
  const deletedPathRows = manifest.rejectedAttempts
    .map((record) => `- \`${record.privateGeneratedOriginalPath}\``)
    .join("\n");
  const sourceRows = manifest.researchSources
    .map((source) => {
      const citation = source.url ? `[${source.citation}](${source.url})` : source.citation;
      return `| ${source.taxonId} | ${citation} | ${source.use.replaceAll("|", "\\|")} |`;
    })
    .join("\n");
  return `# Documentary-famous Paleozoic/Cenozoic expansion provenance

- Batch: \`${manifest.batchId}\`
- Audience: ${manifest.audience}
- Taxa: ${manifest.rollup.taxa}
- Approved project assets: ${manifest.rollup.approvedAssets}
- Representative S1 assets: ${manifest.rollup.representativeAssets}
- Review/reference S2/S3 assets: ${manifest.rollup.nonRepresentativeAssets}
- Rejected or superseded attempts: ${manifest.rollup.rejectedAttempts}
- Rejected source PNGs verified deleted: ${manifest.rollup.rejectedSourcePngsDeleted}
- Rejected source pixels retained: ${manifest.rollup.rejectedPixelsRetained}

The JSON companion is canonical for exact revised prompts, call IDs, source lineage, seed availability, SHA-256 values, byte counts, PNG dimensions, source/licence boundaries, and review decisions. The app may reference only approved \`assets/dinosaurs/...\` paths; private \`.codex/generated_images\` paths are provenance-only.

## Approved records

| Record | Slot | Kind | Representative eligible | Dimensions | SHA-256 |
| --- | ---: | --- | --- | --- | --- |
${approvedRows}

S1 remains the basic full-body side or near-side identity view for every added taxon. Every S2 now satisfies the fixed same-body full-body color-pattern contract and remains review hold. Every S2/S3 is barred from representative promotion without a separate anatomy audit.

## Rights and evidence boundary

All accepted and rejected bitmaps were generated from original project prompts with OpenAI built-in image generation. No external artwork, documentary frame, published reconstruction, franchise frame, or named-artist style was supplied. Scientific papers and museum pages were used only for factual anatomy, occurrence, scale and uncertainty constraints. Colors, patterns, most soft tissue, exact poses and pictured moments remain reconstructions as detailed in the JSON evidence boundaries. Accepted private originals remain available for audit; rejected source pixels do not.

## Rejected attempts

Seventeen failed attempts were never copied into the project. Two cropped S2 structure references were briefly copied before the same-body contract review, then removed from runtime and superseded by full-body variants. Under the standing complete-reject policy, all nineteen rejected source PNGs were moved out of the private generation cache and are verified absent. Their exact prompts, call IDs, lineages, and pre-deletion SHA-256/byte/dimension facts remain. The deleted PNGs may be recoverable from the Windows Recycle Bin until it is emptied; after purge, the embedded metadata is the only retained evidence.

| Taxon | Intended role | Call ID | Pre-deletion SHA / dimensions | Rejection reason |
| --- | --- | --- | --- | --- |
${rejectedRows}

## Deleted rejected-source paths

The builder requires every path below to remain absent and performs no deletion itself.

${deletedPathRows}

## Research sources

| Taxon | Source | Use |
| --- | --- | --- |
${sourceRows}

## Rebuild and verification

Run with the bundled Node runtime:

\`\`\`powershell
& 'C:\\Users\\USER\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe' tools/comfyui/scripts/build_documentary_famous_life_manifest.mjs
\`\`\`

The builder streams the current rollout log instead of loading its multi-gigabyte JSONL into memory. It requires exactly ${manifest.rollup.approvedAssets + manifest.rollup.rejectedAttempts} completed image-generation events, preserves each event's exact \`revised_prompt\`, validates all retained accepted private PNGs, and refuses to write if any approved project copy differs from its generated original in SHA-256, byte count or dimensions. It also refuses to write while any rejected source PNG remains, validates complete coverage of the embedded pre-deletion facts, and attaches those facts to every deleted rejected input-reference lineage.
`;
}

const allSpecs = [...acceptedSpecs, ...rejectedSpecs];
const allCallIds = allSpecs.map((spec) => spec.callId);
if (new Set(allCallIds).size !== allCallIds.length) {
  throw new Error("Call IDs must be unique across accepted and rejected records.");
}
if (acceptedSpecs.length !== 18 || rejectedSpecs.length !== 19) {
  throw new Error("Expected exactly 18 accepted records and 19 rejected attempts.");
}
const rejectedCallIds = rejectedSpecs.map((spec) => spec.callId).sort();
const embeddedRejectedCallIds = Object.keys(rejectedPreDeletionFacts).sort();
if (JSON.stringify(rejectedCallIds) !== JSON.stringify(embeddedRejectedCallIds)) {
  throw new Error("Rejected specs and embedded pre-deletion file facts do not match exactly.");
}
for (const [callId, facts] of Object.entries(rejectedPreDeletionFacts)) {
  if (!/^[0-9a-f]{64}$/.test(facts.sha256)) {
    throw new Error(`Invalid embedded SHA-256 for rejected source: ${callId}`);
  }
  if (
    !Number.isInteger(facts.bytes) ||
    !Number.isInteger(facts.width) ||
    !Number.isInteger(facts.height) ||
    facts.dimensions !== `${facts.width}x${facts.height}`
  ) {
    throw new Error(`Invalid embedded pre-deletion dimensions or byte count: ${callId}`);
  }
}
const rejectedSourcePaths = rejectedSpecs.map((spec) => privatePathFor(spec.callId));
const presentRejectedSources = rejectedSourcePaths.filter((sourcePath) => fs.existsSync(sourcePath));
if (presentRejectedSources.length) {
  throw new Error(
    `Complete-reject deletion required for ${presentRejectedSources.length} source PNG(s):\n${presentRejectedSources.join("\n")}`,
  );
}
const taxonIds = new Set(acceptedSpecs.map((spec) => spec.taxonId));
if (taxonIds.size !== 6) {
  throw new Error("Expected exactly six accepted taxa.");
}
for (const taxonId of taxonIds) {
  const records = acceptedSpecs.filter((spec) => spec.taxonId === taxonId);
  if (records.length !== 3 || records.filter((record) => record.representativeEligible).length !== 1) {
    throw new Error(`Taxon does not have three records and one representative: ${taxonId}`);
  }
}

const appSource = fs.readFileSync(path.join(repoRoot, "app.js"), "utf8");
for (const spec of acceptedSpecs) {
  const promptRecordLink =
    `tools/comfyui/documentary-famous-life-expansion-20260811.json#records/${spec.key}`;
  if (!appSource.includes(promptRecordLink)) {
    throw new Error(`app.js is missing provenance record link: ${spec.key}`);
  }
  if (!appSource.includes(spec.projectPath)) {
    throw new Error(`app.js is missing approved asset path: ${spec.projectPath}`);
  }
}
for (const spec of rejectedSpecs.filter((record) => record.formerProjectPath)) {
  if (appSource.includes(spec.formerProjectPath)) {
    throw new Error(`app.js still references superseded asset: ${spec.formerProjectPath}`);
  }
  if (fs.existsSync(path.join(repoRoot, spec.formerProjectPath))) {
    throw new Error(`Superseded project copy still exists: ${spec.formerProjectPath}`);
  }
}

const events = await loadGenerationEvents(allCallIds);
const records = Object.fromEntries(
  acceptedSpecs.map((spec) => [spec.key, acceptedRecord(spec, events)]),
);
const rejectedAttempts = rejectedSpecs.map((spec) => rejectedRecord(spec, events));
const referenceLineageRecords = [...Object.values(records), ...rejectedAttempts].flatMap(
  (record) => record.referenceImageRecords,
);
const deletedRejectedReferenceRecords = referenceLineageRecords.filter(
  (record) => record.pixelStatus === "deleted-rejected-private-original",
);
const manifest = {
  schemaVersion: 1,
  batchId: "2026-08-11-documentary-famous-life-expansion-v1",
  createdAt: "2026-08-11T08:28:08.000Z",
  audience: "Korean Dino Atlas users ages 5-14",
  scope: [
    "Arthropleura armata three-image Paleozoic gallery",
    "Meganeura monyi three-image Paleozoic gallery",
    "Inostrancevia alexandri three-image Paleozoic gallery",
    "Titanoboa cerrejonensis three-image Cenozoic gallery",
    "Basilosaurus isis three-image Cenozoic gallery",
    "Paraceratherium transouralicum three-image Cenozoic gallery",
  ],
  rollup: {
    taxa: taxonIds.size,
    approvedAssets: acceptedSpecs.length,
    representativeAssets: acceptedSpecs.filter((spec) => spec.representativeEligible).length,
    nonRepresentativeAssets: acceptedSpecs.filter((spec) => !spec.representativeEligible).length,
    rejectedAttempts: rejectedSpecs.length,
    rejectedSourcePngsDeleted: rejectedSpecs.length,
    rejectedPixelsRetained: 0,
    generationEvents: events.size,
  },
  promptEncoding:
    "Each prompt array preserves the exact nonblank revised_prompt returned by the completed image_generation_end event for that call ID.",
  copyrightSafety: {
    externalArtworkUsed: false,
    externalImagesUsedAsGenerationInput: false,
    projectGeneratedReferencesOnly:
      "Where referenceImages is nonempty, only project-owned generated images were supplied for identity control, targeted anatomy repair, or composition lineage.",
    licenseRecord: commonLicense,
    rejectedOriginalPolicy:
      "Seventeen failed attempts were never copied. Two cropped S2 structure references were temporarily copied, then removed from assets/dinosaurs and app metadata when superseded. All nineteen rejected/superseded source PNGs were moved from the private generation cache to the Windows Recycle Bin under the standing complete-reject policy; zero rejected pixels are retained at their original paths. Exact prompts, call IDs, lineages and pre-deletion SHA-256/byte/dimension facts remain as metadata-only audit evidence.",
    rejectedDeletionRecoverability:
      "Deleted source PNGs may remain recoverable from the Windows Recycle Bin until it is emptied. They are not recoverable from git or project assets; after Recycle Bin purge, only the recorded metadata remains.",
    appPathPolicy:
      "Runtime and app metadata may reference approved assets/dinosaurs paths only; private .codex/generated_images paths are provenance-only.",
  },
  rejectedSourceDeletion: {
    policy: "complete rejects retain no source pixels",
    deletionPerformedByBuilder: false,
    deletionMethod: "moved to Windows Recycle Bin after exact-path and accepted-set disjointness validation",
    sourcePathsExpectedPresent: false,
    sourcePathsVerifiedAbsent: true,
    pixelsRetained: false,
    recoverability:
      "Potentially recoverable from the Windows Recycle Bin until it is emptied; not retained in git or project assets.",
    preDeletionEvidenceSource: {
      path: "tools/comfyui/documentary-famous-life-expansion-20260811.json",
      sha256: "875ed47d5e12da64bb29c38f8808267ec08817ca06af1c6e9e30870e282c89fa",
      scope: "canonical manifest immediately before rejected-source deletion",
    },
    deletedSourcePaths: rejectedSourcePaths.map(toPortablePath),
  },
  researchSources,
  evidenceBoundaries,
  records,
  rejectedAttempts,
  validation: {
    generatedFromSessionLog: toPortablePath(sessionPath),
    privateImageRoot: toPortablePath(privateImageRoot),
    exactRevisedPromptsFound: events.size,
    acceptedProjectCopiesHashMatched: acceptedSpecs.length,
    acceptedProjectCopiesByteMatched: acceptedSpecs.length,
    acceptedProjectCopiesDimensionMatched: acceptedSpecs.length,
    appRecordLinksMatched: acceptedSpecs.length,
    appApprovedAssetPathsMatched: acceptedSpecs.length,
    rejectedPrivateOriginalsExpected: 0,
    rejectedPrivateOriginalsFound: 0,
    rejectedPrivateOriginalsAbsent: rejectedSpecs.length,
    rejectedPreDeletionFactsEmbedded: Object.keys(rejectedPreDeletionFacts).length,
    inputReferenceRecordsHashed: referenceLineageRecords.length,
    deletedRejectedInputReferenceRecordsHashed: deletedRejectedReferenceRecords.length,
    rejectedPixelsRetained: 0,
  },
};

fs.writeFileSync(outputJsonPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
fs.writeFileSync(outputMarkdownPath, markdownFor(manifest), "utf8");

console.log(
  JSON.stringify(
    {
      outputJsonPath: toPortablePath(outputJsonPath),
      outputMarkdownPath: toPortablePath(outputMarkdownPath),
      ...manifest.rollup,
      acceptedBytes: Object.values(records).reduce((sum, record) => sum + record.bytes, 0),
      rejectedPreDeletionBytes: rejectedAttempts.reduce((sum, record) => sum + record.bytes, 0),
      inputReferenceRecordsHashed: referenceLineageRecords.length,
      deletedRejectedInputReferenceRecordsHashed: deletedRejectedReferenceRecords.length,
    },
    null,
    2,
  ),
);
