// Controlled biological micro-motion pilots. M1 is deliberately isolated from
// the M0 environment-only lane and from every representative/gallery image
// path. Motion may never upgrade the source still's anatomy verdict.
window.motionM1SampleCatalog = {
  schemaVersion: 1,
  policy: {
    tier: "M1",
    scope: "controlled biological micro-motion over an approved fixed still",
    representativePromotion: "prohibited",
    galleryPromotion: "prohibited",
    autoplay: "prohibited",
    locomotion: "prohibited in M1",
    allowedMotion: ["natural blink", "sub-degree rigid head-and-neck tilt"],
    publicRequires: ["frameAnatomy", "motionPlausibility", "backgroundIntegrity", "responsive", "publication"],
    accessibility: "explicit click-to-play, muted, playsinline, poster fallback, reduced-motion and save-data aware",
  },
  samples: [
    {
      id: "oviraptor-philoceratops-blink-headtilt-biological-m1-v1",
      title: "오비랍토르 눈깜빡임과 고개 미세 움직임",
      taxonId: "oviraptor-philoceratops",
      scientificName: "Oviraptor philoceratops",
      tier: "M1",
      motionClass: "biological-micro",
      sceneRole: "solo",
      sceneRoleLabel: "단독 개체",
      motionLabel: "자연스러운 두 번의 눈깜빡임 · 약 0.8°의 머리·목 기울임",
      lockedParts: "몸통·팔·손가락·다리·발·꼬리·지면·배경·카메라 고정",
      description: "승인된 오비랍토르 대표 정지화면에서 눈 주변과 머리·목 덩어리만 제한적으로 움직이는 5초짜리 제어형 2D 시험입니다. 걷기·공격·먹이활동 같은 행동을 재현하지 않으며, 생물학적 움직임의 자연스러움만 별도로 검토합니다.",
      poster: "assets/dinosaurs/oviraptor-philoceratops-robust-lowcrest-rostrum-representative-imagegen-v3.png",
      src: "assets/motion/m1/oviraptor-philoceratops-blink-headtilt-biological-m1-v1.mp4",
      provenance: {
        metadataRecord: "tools/comfyui/motion-m1-pilot-batch-20260803.json#/samples/oviraptor-philoceratops-blink-headtilt-biological-m1-v1",
        sourceLicense: "project-owned generated still and project-generated motion-only overlay",
        workflow: "OpenAI image edit limited to a closed-eye patch, then deterministic local FFmpeg masked compositing",
      },
      representativeEligible: false,
      galleryEligible: false,
      review: {
        anatomy: { status: "poster-inherited", note: "The S1 still-image anatomy verdict is inherited; motion is not anatomy evidence." },
        frameAnatomy: { status: "supported", note: "Eight full-frame and head-crop checkpoints preserve the low crest, long deep toothless beak, neck outline, two arms, two legs, three-finger hands, feet, and single tail." },
        motionPlausibility: { status: "supported", note: "Two brief blinks and a rigid sub-degree head-and-neck tilt read as restrained micro-motion; 80.17% of blink change stays in the eye zone and 99.85% of tilt change stays in the head zone." },
        backgroundIntegrity: { status: "supported", note: "The body below the neck, ground, vegetation, sky, and camera remain locked outside the declared head-and-neck mask; protected-region mean differences are 0.0036 for blink and 0.0423 for tilt." },
        responsive: { status: "supported", note: "Click-to-play, muted inline playback, cross-lane pause, poster fallback, and no horizontal overflow passed at 1440x900, 390x844, 844x390, and 320x700 on 2026-08-03." },
        publication: { status: "published", note: "M1 pilot passed file, frame-anatomy, motion-locality, background-integrity, responsive, accessibility, and provenance gates on 2026-08-03." },
      },
      file: { sha256: "86689a99269e1300b447b35ab801991506e37b518ff4437f877e428704773b52", bytes: 338341, width: 960, height: 640, durationSeconds: 5, fps: 24, codec: "h264" },
    },
  ],
};
