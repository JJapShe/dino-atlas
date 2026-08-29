# Dino Atlas gallery composition similarity audit

> This report ranks visual-composition risk. It is not an anatomy pass and never authorizes representative promotion.

## Baseline

- Taxa in audit scope: 155
- Taxa with assigned gallery slots in scope: 155
- Total taxa in app data: 155
- Total taxa with assigned gallery slots: 155
- Audited unique approved images: 871
- Compared within-taxon pairs: 2103
- Reporting threshold: 0.45
- Pairs at or above threshold: 677

Fixed-threshold distribution:

- >= 0.45: 677
- >= 0.55: 129
- >= 0.65: 12
- >= 0.75: 6

## Priority taxa

| Rank | Taxon | LV | Flagged pairs | Max structural | Max priority | Critical | High | Mirrored | Recolor risk | Suggested route |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | quetzalcoatlus-northropi | 1 | 5 | 0.997 | 1.092 | 1 | 0 | 0 | 2 | change-camera-distance-direction-subject-count-or-habitat |
| 2 | herrerasaurus-ischigualastensis | 3 | 7 | 0.98 | 1.075 | 1 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 3 | psittacosaurus-mongoliensis | 2 | 8 | 0.971 | 1.011 | 1 | 0 | 4 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 4 | dsungaripterus-weii | 3 | 8 | 0.902 | 0.997 | 1 | 0 | 2 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 5 | almas-ukhaa | 4 | 3 | 0.886 | 0.981 | 1 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 6 | ankylosaurus-magniventris | 1 | 9 | 0.783 | 0.878 | 1 | 1 | 6 | 0 | change-camera-distance-direction-subject-count-or-habitat |
| 7 | otodus-megalodon | 1 | 3 | 0.646 | 0.806 | 0 | 1 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 8 | therizinosaurus-cheloniformis | 1 | 7 | 0.677 | 0.772 | 0 | 0 | 5 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 9 | velociraptor-mongoliensis | 1 | 4 | 0.597 | 0.772 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 10 | spinosaurus-aegyptiacus | 1 | 6 | 0.595 | 0.77 | 0 | 0 | 4 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 11 | dilophosaurus-wetherilli | 1 | 6 | 0.58 | 0.755 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 12 | parasaurolophus-walkeri | 1 | 9 | 0.579 | 0.754 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 13 | carnotaurus-sastrei | 1 | 2 | 0.575 | 0.75 | 0 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 14 | utahceratops-gettyi | 4 | 15 | 0.654 | 0.749 | 0 | 1 | 5 | 3 | replace-pattern-slot-with-opposite-action-or-scale |
| 15 | nasutoceratops-titusi | 2 | 10 | 0.614 | 0.749 | 0 | 0 | 6 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 16 | goyocephale-lattimorei | 3 | 9 | 0.726 | 0.741 | 0 | 1 | 6 | 0 | avoid-mirror-variant-change-camera-height-and-pose |
| 17 | edmontosaurus-annectens | 2 | 8 | 0.604 | 0.739 | 0 | 0 | 0 | 2 | replace-pattern-slot-with-opposite-action-or-scale |
| 18 | ichthyosaurus-communis | 2 | 10 | 0.603 | 0.738 | 0 | 0 | 4 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 19 | agujaceratops-mariscalensis | 4 | 13 | 0.64 | 0.735 | 0 | 1 | 6 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 20 | saurolophus-angustirostris | 2 | 12 | 0.592 | 0.727 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 21 | centrosaurus-apertus | 2 | 6 | 0.587 | 0.722 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 22 | mammuthus-primigenius | 1 | 3 | 0.553 | 0.713 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 23 | apatosaurus-ajax | 1 | 4 | 0.615 | 0.71 | 0 | 0 | 2 | 0 | change-camera-distance-direction-subject-count-or-habitat |
| 24 | efraasia-minor | 4 | 6 | 0.614 | 0.709 | 0 | 0 | 2 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 25 | giganotosaurus-carolinii | 1 | 1 | 0.531 | 0.706 | 0 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 26 | kosmoceratops-richardsoni | 3 | 15 | 0.665 | 0.705 | 0 | 0 | 5 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 27 | tarbosaurus-bataar | 1 | 18 | 0.602 | 0.702 | 0 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 28 | avimimus-portentosus | 3 | 11 | 0.603 | 0.698 | 0 | 0 | 5 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 29 | coelodonta-antiquitatis | 2 | 3 | 0.578 | 0.698 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 30 | plesiosaurus-dolichodeirus | 2 | 7 | 0.561 | 0.696 | 0 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 31 | nyctosaurus-gracilis | 3 | 5 | 0.672 | 0.687 | 0 | 0 | 0 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 32 | allosaurus-fragilis | 1 | 3 | 0.589 | 0.684 | 0 | 0 | 0 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 33 | shonisaurus-popularis | 3 | 13 | 0.608 | 0.683 | 0 | 0 | 8 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 34 | byronosaurus-jaffei | 4 | 9 | 0.587 | 0.682 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 35 | diplodocus-carnegiei | 1 | 7 | 0.583 | 0.678 | 0 | 0 | 2 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 36 | conchoraptor-gracilis | 4 | 5 | 0.583 | 0.678 | 0 | 0 | 3 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 37 | citipati-osmolskae | 3 | 4 | 0.581 | 0.676 | 0 | 0 | 2 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 38 | stegosaurus-stenops | 1 | 4 | 0.579 | 0.674 | 0 | 0 | 2 | 0 | change-camera-distance-direction-subject-count-or-habitat |
| 39 | riojasaurus-incertus | 4 | 6 | 0.598 | 0.672 | 0 | 0 | 3 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 40 | hesperosaurus-mjosi | 4 | 5 | 0.577 | 0.672 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 41 | kronosaurus-queenslandicus | 2 | 2 | 0.532 | 0.667 | 0 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 42 | yutyrannus-huali | 2 | 8 | 0.609 | 0.664 | 0 | 0 | 5 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 43 | saturnalia-tupiniquim | 4 | 5 | 0.569 | 0.664 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 44 | deinocheirus-mirificus | 2 | 7 | 0.608 | 0.663 | 0 | 0 | 3 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 45 | sauropelta-edwardsorum | 3 | 8 | 0.641 | 0.656 | 0 | 0 | 2 | 1 | avoid-mirror-variant-change-camera-height-and-pose |
| 46 | tyrannosaurus-rex | 1 | 12 | 0.56 | 0.655 | 0 | 0 | 7 | 0 | avoid-mirror-variant-change-camera-height-and-pose |
| 47 | bagualosaurus-agudoensis | 4 | 7 | 0.605 | 0.655 | 0 | 0 | 0 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 48 | plateosaurus-engelhardti | 2 | 4 | 0.52 | 0.655 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 49 | zanabazar-junior | 4 | 9 | 0.608 | 0.654 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 50 | monolophosaurus-jiangi | 2 | 4 | 0.519 | 0.654 | 0 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |

## Ranked pairs

| Rank | Taxon | LV | Risk | Structural | Mode | Slots | Roles | Same composition | Recolor risk | Sources |
| ---: | --- | ---: | --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | quetzalcoatlus-northropi | 1 | critical | 0.997 | direct | 1/5 | representative/interaction | no | no | quetzalcoatlus-northropi-ventral-ankle-membrane-representative-imagegen-v3.png<br>quetzalcoatlus-northropi-alamosaurus-separated-ventral-ecology-imagegen-v3.png |
| 2 | herrerasaurus-ischigualastensis | 3 | critical | 0.98 | direct | 1/2 | representative/color-pattern | no | no | herrerasaurus-ischigualastensis-canonical-redbed-representative-imagegen-v3.png<br>herrerasaurus-ischigualastensis-charcoal-russet-mottling-pattern-imagegen-v3.png |
| 3 | psittacosaurus-mongoliensis | 2 | critical | 0.971 | direct | 1/7 | representative/alternate-habitat-behavior | no | yes | psittacosaurus-mongoliensis-smallskull-jugalhorn-representative-imagegen-v1.png<br>psittacosaurus-mongoliensis-genus-tail-bristle-anatomy-imagegen-v1.png |
| 4 | dsungaripterus-weii | 3 | critical | 0.902 | direct | 1/2 | representative/color-pattern | no | yes | dsungaripterus-weii-toothless-upturned-rostrum-posterior-crusher-representative-imagegen-v2.png<br>dsungaripterus-weii-iron-red-turquoise-wing-pattern-imagegen-v2.png |
| 5 | almas-ukhaa | 4 | critical | 0.886 | direct | 1/2 | representative/color-pattern | no | no | almas-ukhaa-short-deep-skull-olive-unbanded-representative-imagegen-v2.png<br>almas-ukhaa-short-deep-skull-aubergine-unbanded-pattern-imagegen-v2.png |
| 6 | ankylosaurus-magniventris | 1 | critical | 0.783 | direct | 1/5 | representative/interaction | no | no | ankylosaurus-magniventris-hell-creek-broadskull-singleclub-representative-imagegen-v2.png<br>ankylosaurus-magniventris-oxbow-edmontosaurus-coexistence-ecology-imagegen-v2.png |
| 7 | ankylosaurus-magniventris | 1 | high | 0.724 | direct | 1/6 | representative/social-growth-defense | no | no | ankylosaurus-magniventris-hell-creek-broadskull-singleclub-representative-imagegen-v2.png<br>ankylosaurus-magniventris-lateral-tail-sweep-defense-imagegen-v2.png |
| 8 | otodus-megalodon | 1 | high | 0.646 | mirrored | 1/2 | representative/color-pattern | no | no | otodus-megalodon-elongated-blunt-rostrum-representative-imagegen-v1.png<br>otodus-megalodon-rightfacing-slate-bronze-pattern-imagegen-v1.png |
| 9 | quetzalcoatlus-northropi | 1 | medium | 0.6 | direct | 1/2 | representative/color-pattern | no | yes | quetzalcoatlus-northropi-ventral-ankle-membrane-representative-imagegen-v3.png<br>quetzalcoatlus-northropi-indigo-jade-ventral-ankle-pattern-imagegen-v3.png |
| 10 | therizinosaurus-cheloniformis | 1 | medium | 0.677 | direct | 1/4 | representative/identity-anatomy | no | no | therizinosaurus-cheloniformis-giant-scythe-claws-imagegen-v1.png<br>therizinosaurus-cheloniformis-straight-triclaw-fourtoe-anatomy-imagegen-v1.png |
| 11 | velociraptor-mongoliensis | 1 | medium | 0.597 | mirrored | 1/2 | representative/color-pattern | no | no | velociraptor-mongoliensis-djadokhta-raised-second-toe-representative-imagegen-v1.png<br>velociraptor-mongoliensis-dawn-slate-celadon-pattern-imagegen-v1.png |
| 12 | spinosaurus-aegyptiacus | 1 | medium | 0.595 | mirrored | 1/2 | representative/color-pattern | no | yes | spinosaurus-aegyptiacus-kemkem-shortleg-deeptail-threefinger-representative-imagegen-v1.png<br>spinosaurus-aegyptiacus-rainflat-indigo-vermilion-turquoise-pattern-imagegen-v1.png |
| 13 | dilophosaurus-wetherilli | 1 | medium | 0.58 | mirrored | 1/2 | representative/color-pattern | no | no | dilophosaurus-wetherilli-kayenta-twincrest-fourdigit-representative-imagegen-v2.png<br>dilophosaurus-wetherilli-petrol-violet-celadon-pattern-imagegen-v2.png |
| 14 | parasaurolophus-walkeri | 1 | watch | 0.579 | mirrored | 1/2 | representative/color-pattern | no | no | parasaurolophus-walkeri-dinosaurpark-lowcrest-mittenmanus-representative-imagegen-v2.png<br>parasaurolophus-walkeri-petrol-celadon-russet-pattern-imagegen-v2.png |
| 15 | carnotaurus-sastrei | 1 | watch | 0.575 | mirrored | 1/2 | representative/color-pattern | no | no | carnotaurus-sastrei-browhorn-shortskull-representative-imagegen-v2.png<br>carnotaurus-sastrei-rust-charcoal-pattern-variant-imagegen-v2.png |
| 16 | utahceratops-gettyi | 4 | high | 0.654 | direct | 1/2 | representative/color-pattern | no | no | utahceratops-gettyi-notched-frill-lateral-browhorns-imagegen-v1.png<br>utahceratops-gettyi-moss-rust-pattern-imagegen-v1.png |
| 17 | nasutoceratops-titusi | 2 | medium | 0.614 | mirrored | 1/2 | representative/color-pattern | no | yes | nasutoceratops-titusi-hugenaris-twisted-browhorn-representative-imagegen-v1.png<br>nasutoceratops-titusi-slate-teal-rust-reverse-pattern-imagegen-v1.png |
| 18 | goyocephale-lattimorei | 3 | high | 0.726 | mirrored | 1/6 | representative/social-growth-defense | no | no | goyocephale-lattimorei-table-skull-gracile-representative-imagegen-v2.png<br>goyocephale-lattimorei-tendon-tail-brisk-walk-anatomy-imagegen-v1.png |
| 19 | edmontosaurus-annectens | 2 | medium | 0.604 | direct | 1/2 | representative/color-pattern | no | yes | edmontosaurus-annectens-lance-softcrest-hooves-representative-imagegen-v1.png<br>edmontosaurus-annectens-petrol-celadon-russet-pattern-imagegen-v3.png |
| 20 | ichthyosaurus-communis | 2 | medium | 0.603 | direct | 1/2 | representative/color-pattern | no | no | ichthyosaurus-communis-streamlined-sideprofile-imagegen-v1.png<br>ichthyosaurus-communis-indigo-slate-pattern-imagegen-v1.png |
| 21 | agujaceratops-mariscalensis | 4 | high | 0.64 | direct | 1/2 | representative/color-pattern | no | no | agujaceratops-mariscalensis-heartfrill-longhorns-imagegen-v1.png<br>agujaceratops-mariscalensis-teal-sienna-pattern-imagegen-v1.png |
| 22 | saurolophus-angustirostris | 2 | medium | 0.592 | direct | 1/2 | representative/color-pattern | no | no | saurolophus-angustirostris-spike-crest-fullbody-imagegen-v1.png<br>saurolophus-angustirostris-copper-spruce-pattern-imagegen-v1.png |
| 23 | therizinosaurus-cheloniformis | 1 | watch | 0.552 | mirrored | 1/2 | representative/color-pattern | no | no | therizinosaurus-cheloniformis-giant-scythe-claws-imagegen-v1.png<br>therizinosaurus-cheloniformis-bilateral-triclaw-petrol-dawn-pattern-imagegen-v4.png |
| 24 | centrosaurus-apertus | 2 | medium | 0.587 | mirrored | 1/2 | representative/color-pattern | no | no | centrosaurus-apertus-procurved-nasalhorn-p1-p2-representative-imagegen-v1.png<br>centrosaurus-apertus-moss-ochre-teal-pattern-imagegen-v1.png |
| 25 | mammuthus-primigenius | 1 | watch | 0.553 | mirrored | 1/2 | representative/color-pattern | no | no | mammuthus-primigenius-high-shoulder-spiral-tusks-representative-imagegen-v1.png<br>mammuthus-primigenius-right-facing-charcoal-coat-review-imagegen-v2.png |
| 26 | apatosaurus-ajax | 1 | medium | 0.615 | direct | 1/4 | representative/identity-anatomy | no | no | apatosaurus-ajax-robust-lowneck-morrison-representative-imagegen-v1.png<br>apatosaurus-ajax-thumbclaw-threehindclaw-anatomy-imagegen-v1.png |
| 27 | efraasia-minor | 4 | medium | 0.614 | direct | 1/2 | representative/color-pattern | no | yes | efraasia-minor-slender-sauropodomorph-imagegen-v1.png<br>efraasia-minor-teal-ochre-pattern-imagegen-v1.png |
| 28 | giganotosaurus-carolinii | 1 | watch | 0.531 | direct | 1/2 | representative/color-pattern | no | no | giganotosaurus-carolinii-lowskull-lacrimal-ridge-representative-imagegen-v1.png<br>giganotosaurus-carolinii-charcoal-russet-pattern-variant-imagegen-v1.png |
| 29 | kosmoceratops-richardsoni | 3 | medium | 0.61 | direct | 1/2 | representative/color-pattern | no | no | kosmoceratops-richardsoni-ornate-solid-frill-imagegen-v1.png<br>kosmoceratops-richardsoni-indigo-ochre-pattern-imagegen-v1.png |
| 30 | tarbosaurus-bataar | 1 | watch | 0.527 | direct | 1/2 | representative/color-pattern | no | no | tarbosaurus-bataar-narrow-skull-two-fingers-imagegen-v1.png<br>tarbosaurus-bataar-basalt-rust-pattern-imagegen-v1.png |
| 31 | avimimus-portentosus | 3 | medium | 0.603 | direct | 1/2 | representative/color-pattern | no | no | avimimus-portentosus-beaked-feathered-imagegen-v1.png<br>avimimus-portentosus-violet-amber-pattern-imagegen-v1.png |
| 32 | coelodonta-antiquitatis | 2 | watch | 0.578 | mirrored | 1/2 | representative/color-pattern | no | no | coelodonta-antiquitatis-laterally-compressed-bladehorn-representative-imagegen-v2.png<br>coelodonta-antiquitatis-leftfacing-tawny-patch-pattern-imagegen-v1.png |
| 33 | tarbosaurus-bataar | 1 | medium | 0.602 | direct | 1/4 | representative/identity-anatomy | no | no | tarbosaurus-bataar-narrow-skull-two-fingers-imagegen-v1.png<br>tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png |
| 34 | plesiosaurus-dolichodeirus | 2 | watch | 0.561 | mirrored | 1/2 | representative/color-pattern | no | no | plesiosaurus-dolichodeirus-longneck-sideprofile-imagegen-v1.png<br>plesiosaurus-dolichodeirus-teal-copper-pattern-imagegen-v1.png |
| 35 | quetzalcoatlus-northropi | 1 | medium | 0.598 | direct | 2/5 | color-pattern/interaction | no | yes | quetzalcoatlus-northropi-indigo-jade-ventral-ankle-pattern-imagegen-v3.png<br>quetzalcoatlus-northropi-alamosaurus-separated-ventral-ecology-imagegen-v3.png |
| 36 | nyctosaurus-gracilis | 3 | medium | 0.672 | direct | 1/4 | representative/identity-anatomy | no | yes | nyctosaurus-gracilis-crestless-seaway-representative-imagegen-v2.png<br>nyctosaurus-gracilis-clawless-three-phalange-anatomy-imagegen-v2.png |
| 37 | allosaurus-fragilis | 1 | medium | 0.589 | direct | 1/4 | representative/identity-anatomy | no | yes | allosaurus-fragilis-morrison-lowhorn-threefinger-representative-imagegen-v1.png<br>allosaurus-fragilis-threefinger-lowhorn-anatomy-imagegen-v1.png |
| 38 | shonisaurus-popularis | 3 | medium | 0.588 | mirrored | 1/2 | representative/color-pattern | no | yes | shonisaurus-popularis-nevada-giant-shastasaurid-imagegen-v1.png<br>shonisaurus-popularis-indigo-opal-pattern-imagegen-v1.png |
| 39 | byronosaurus-jaffei | 4 | medium | 0.587 | direct | 1/2 | representative/color-pattern | no | no | byronosaurus-jaffei-unserrated-teeth-troodontid-imagegen-v1.png<br>byronosaurus-jaffei-indigo-jade-pattern-imagegen-v1.png |
| 40 | therizinosaurus-cheloniformis | 1 | medium | 0.586 | mirrored | 2/4 | color-pattern/identity-anatomy | no | yes | therizinosaurus-cheloniformis-bilateral-triclaw-petrol-dawn-pattern-imagegen-v4.png<br>therizinosaurus-cheloniformis-straight-triclaw-fourtoe-anatomy-imagegen-v1.png |
| 41 | kosmoceratops-richardsoni | 3 | medium | 0.665 | direct | 3/4 | habitat-ecology/identity-anatomy | no | yes | kosmoceratops-richardsoni-kaiparowits-herd-ecology-imagegen-v1.png<br>kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png |
| 42 | diplodocus-carnegiei | 1 | medium | 0.583 | direct | 1/5 | representative/interaction | no | yes | diplodocus-carnegiei-lowbody-imagegen-v1.png<br>diplodocus-carnegiei-distant-allosaurus-tail-posture-interaction-imagegen-v2.png |
| 43 | conchoraptor-gracilis | 4 | medium | 0.583 | mirrored | 1/2 | representative/color-pattern | no | yes | conchoraptor-gracilis-flat-skull-nuchal-step-representative-imagegen-v2.png<br>conchoraptor-gracilis-charcoal-rust-dawn-pattern-imagegen-v2.png |
| 44 | citipati-osmolskae | 3 | medium | 0.581 | mirrored | 1/2 | representative/color-pattern | no | yes | citipati-osmolskae-vertical-premaxilla-deepbeak-lowcrest-representative-imagegen-v1.png<br>citipati-osmolskae-petrol-saffron-cream-pattern-imagegen-v1.png |
| 45 | stegosaurus-stenops | 1 | watch | 0.579 | direct | 1/4 | representative/identity-anatomy | no | no | stegosaurus-stenops-copperplate-upward-v-thagomizer-representative-imagegen-v1.png<br>stegosaurus-stenops-alternating-plate-upward-v-identity-imagegen-v1.png |
| 46 | riojasaurus-incertus | 4 | watch | 0.577 | mirrored | 1/2 | representative/color-pattern | no | no | riojasaurus-incertus-long-low-skull-robust-forelimb-representative-imagegen-v1.png<br>riojasaurus-incertus-plum-petrol-celadon-pattern-imagegen-v1.png |
| 47 | hesperosaurus-mjosi | 4 | watch | 0.577 | mirrored | 1/2 | representative/color-pattern | no | no | hesperosaurus-mjosi-broadskull-lowplates-fourspike-representative-imagegen-v1.png<br>hesperosaurus-mjosi-petrol-plum-grooved-plate-pattern-imagegen-v1.png |
| 48 | ankylosaurus-magniventris | 1 | watch | 0.574 | direct | 5/6 | interaction/social-growth-defense | no | no | ankylosaurus-magniventris-oxbow-edmontosaurus-coexistence-ecology-imagegen-v2.png<br>ankylosaurus-magniventris-lateral-tail-sweep-defense-imagegen-v2.png |
| 49 | kronosaurus-queenslandicus | 2 | watch | 0.532 | direct | 1/2 | representative/color-pattern | no | no | kronosaurus-queenslandicus-eromanga-giant-skull-pliosaur-imagegen-v1.png<br>kronosaurus-queenslandicus-bottlegreen-ivory-ocelli-pattern-imagegen-v2.png |
| 50 | dilophosaurus-wetherilli | 1 | watch | 0.57 | direct | 2/6 | color-pattern/social-growth-defense | no | no | dilophosaurus-wetherilli-petrol-violet-celadon-pattern-imagegen-v2.png<br>dilophosaurus-wetherilli-subadult-dawn-growth-imagegen-v2.png |
| 51 | yutyrannus-huali | 2 | medium | 0.609 | direct | 1/4 | representative/identity-anatomy | no | yes | yutyrannus-huali-yixian-white-mottled-feathered-representative-imagegen-v1.png<br>yutyrannus-huali-cold-dawn-breath-threefinger-anatomy-imagegen-v1.png |
| 52 | saturnalia-tupiniquim | 4 | watch | 0.569 | mirrored | 1/2 | representative/color-pattern | no | no | saturnalia-tupiniquim-bottlegreen-brickred-waldsanga-representative-imagegen-v2.png<br>saturnalia-tupiniquim-aubergine-turquoise-bluehour-pattern-imagegen-v2.png |
| 53 | deinocheirus-mirificus | 2 | medium | 0.608 | direct | 1/3 | representative/habitat-ecology | no | yes | deinocheirus-mirificus-tridactyl-broadfoot-anatomy-imagegen-v1.png<br>deinocheirus-mirificus-bilateral-tridactyl-rainwet-habitat-imagegen-v3.png |
| 54 | diplodocus-carnegiei | 1 | watch | 0.485 | mirrored | 1/2 | representative/color-pattern | no | no | diplodocus-carnegiei-lowbody-imagegen-v1.png<br>diplodocus-carnegiei-teal-saddle-pattern-imagegen-v1.png |
| 55 | edmontosaurus-annectens | 2 | medium | 0.604 | direct | 5/6 | interaction/social-growth-defense | no | yes | edmontosaurus-annectens-tyrannosaurus-channel-standoff-ecology-imagegen-v1.png<br>edmontosaurus-annectens-adult-juvenile-drychannel-growth-ecology-imagegen-v1.png |
| 56 | otodus-megalodon | 1 | watch | 0.577 | mirrored | 1/3 | representative/habitat-ecology | no | no | otodus-megalodon-elongated-blunt-rostrum-representative-imagegen-v1.png<br>otodus-megalodon-neogene-whale-distance-ecology-imagegen-v1.png |
| 57 | sauropelta-edwardsorum | 3 | medium | 0.641 | mirrored | 4/6 | identity-anatomy/social-growth-defense | no | no | sauropelta-edwardsorum-shoulder-spine-anatomy-imagegen-v2.png<br>sauropelta-edwardsorum-solitary-shoulder-brace-ecology-imagegen-v2.png |
| 58 | bagualosaurus-agudoensis | 4 | watch | 0.56 | direct | 1/2 | representative/color-pattern | no | no | bagualosaurus-agudoensis-robust-herbivore-imagegen-v1.png<br>bagualosaurus-agudoensis-bluegray-copper-pattern-imagegen-v1.png |
| 59 | tyrannosaurus-rex | 1 | watch | 0.56 | mirrored | 1/6 | representative/social-growth-defense | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-triceratops-misty-channel-standoff-ecology-imagegen-v1.png |
| 60 | plateosaurus-engelhardti | 2 | watch | 0.52 | direct | 1/2 | representative/color-pattern | no | no | plateosaurus-engelhardti-imagegen-v25-source-candidate.png<br>plateosaurus-engelhardti-imagegen-v28-source-candidate.png |
| 61 | kosmoceratops-richardsoni | 3 | medium | 0.639 | mirrored | 3/5 | habitat-ecology/interaction | no | no | kosmoceratops-richardsoni-kaiparowits-herd-ecology-imagegen-v1.png<br>kosmoceratops-richardsoni-channel-separated-hadrosaurid-ecology-imagegen-v1.png |
| 62 | ichthyosaurus-communis | 2 | medium | 0.599 | direct | 1/5 | representative/interaction | no | no | ichthyosaurus-communis-streamlined-sideprofile-imagegen-v1.png<br>ichthyosaurus-communis-fish-chase-ecology-imagegen-v1.png |
| 63 | zanabazar-junior | 4 | watch | 0.559 | direct | 1/2 | representative/color-pattern | no | no | zanabazar-junior-large-nemegt-troodontid-imagegen-v1.png<br>zanabazar-junior-teal-plum-pattern-imagegen-v1.png |
| 64 | monolophosaurus-jiangi | 2 | watch | 0.519 | direct | 1/2 | representative/color-pattern | no | no | monolophosaurus-jiangi-single-midline-crest-representative-imagegen-v3.png<br>monolophosaurus-jiangi-cobalt-celadon-pattern-imagegen-v2.png |
| 65 | dunkleosteus-terrelli | 1 | watch | 0.494 | direct | 1/2 | representative/color-pattern | no | no | dunkleosteus-terrelli-single-dorsal-compact-armor-representative-imagegen-v2.png<br>dunkleosteus-terrelli-leftfacing-single-dorsal-copper-pattern-imagegen-v2.png |
| 66 | spinosaurus-aegyptiacus | 1 | watch | 0.557 | direct | 1/6 | representative/social-growth-defense | no | no | spinosaurus-aegyptiacus-kemkem-shortleg-deeptail-threefinger-representative-imagegen-v1.png<br>spinosaurus-aegyptiacus-sunrise-sail-display-ecology-imagegen-v1.png |
| 67 | placodus-gigas | 3 | watch | 0.556 | direct | 1/2 | representative/color-pattern | no | no | placodus-gigas-three-premaxillary-teeth-representative-imagegen-v3.png<br>placodus-gigas-blackberry-jade-rust-closed-mouth-pattern-imagegen-v3.png |
| 68 | carcharodontosaurus-saharicus | 2 | watch | 0.516 | mirrored | 1/2 | representative/color-pattern | no | no | carcharodontosaurus-saharicus-longskull-kemkem-representative-imagegen-v2.png<br>carcharodontosaurus-saharicus-slate-copper-pattern-variant-imagegen-v2.png |
| 69 | sarahsaurus-aurifontanalis | 4 | watch | 0.554 | mirrored | 1/2 | representative/color-pattern | no | no | sarahsaurus-aurifontanalis-powerful-hands-fullbody-imagegen-v1.png<br>sarahsaurus-aurifontanalis-bluegray-copper-pattern-imagegen-v1.png |
| 70 | tarbosaurus-bataar | 1 | watch | 0.554 | direct | 3/6 | habitat-ecology/social-growth-defense | no | no | tarbosaurus-bataar-nemegt-ecology-imagegen-v1.png<br>tarbosaurus-bataar-adult-juvenile-riverbar-growth-ecology-imagegen-v1.png |
| 71 | kosmoceratops-richardsoni | 3 | medium | 0.632 | mirrored | 4/5 | identity-anatomy/interaction | no | no | kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png<br>kosmoceratops-richardsoni-channel-separated-hadrosaurid-ecology-imagegen-v1.png |
| 72 | leptoceratops-gracilis | 3 | medium | 0.632 | direct | 1/4 | representative/identity-anatomy | no | no | leptoceratops-gracilis-modest-frill-imagegen-v1.png<br>leptoceratops-gracilis-low-solid-frill-four-foot-anatomy-imagegen-v1.png |
| 73 | styracosaurus-albertensis | 2 | medium | 0.592 | direct | 3/6 | habitat-ecology/social-growth-defense | no | no | styracosaurus-albertensis-meander-pointbar-low-browse-ecology-imagegen-v2.png<br>styracosaurus-albertensis-separated-adult-subadult-growth-ecology-imagegen-v2.png |
| 74 | tarbosaurus-bataar | 1 | watch | 0.552 | direct | 2/4 | color-pattern/identity-anatomy | no | no | tarbosaurus-bataar-basalt-rust-pattern-imagegen-v1.png<br>tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png |
| 75 | tarbosaurus-bataar | 1 | watch | 0.552 | direct | 4/6 | identity-anatomy/social-growth-defense | no | no | tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png<br>tarbosaurus-bataar-adult-juvenile-riverbar-growth-ecology-imagegen-v1.png |
| 76 | brachiosaurus-altithorax | 1 | watch | 0.472 | mirrored | 1/2 | representative/color-pattern | no | no | brachiosaurus-altithorax-nasal-mound-fullbody-imagegen-v18.png<br>brachiosaurus-altithorax-nasal-mound-slate-moss-rearthreequarter-pattern-imagegen-v2.png |
| 77 | leptoceratops-gracilis | 3 | watch | 0.551 | direct | 1/2 | representative/color-pattern | no | no | leptoceratops-gracilis-modest-frill-imagegen-v1.png<br>leptoceratops-gracilis-slate-speckle-pattern-imagegen-v1.png |
| 78 | tyrannosaurus-rex | 1 | watch | 0.55 | direct | 1/3 | representative/habitat-ecology | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-dawn-channel-crossing-ecology-imagegen-v1.png |
| 79 | sinornithosaurus-millenii | 3 | watch | 0.549 | direct | 1/2 | representative/color-pattern | no | no | sinornithosaurus-millenii-longarm-filament-representative-imagegen-v2.png<br>sinornithosaurus-millenii-plum-lichen-bluehour-pattern-imagegen-v1.png |
| 80 | pachycephalosaurus-wyomingensis | 1 | watch | 0.468 | mirrored | 1/2 | representative/color-pattern | no | no | pachycephalosaurus-wyomingensis-hellcreek-dome-representative-imagegen-v1.png<br>pachycephalosaurus-wyomingensis-bluehour-blueblack-ochre-pattern-imagegen-v1.png |
| 81 | quetzalcoatlus-northropi | 1 | watch | 0.546 | direct | 1/3 | representative/habitat-ecology | no | no | quetzalcoatlus-northropi-ventral-ankle-membrane-representative-imagegen-v3.png<br>quetzalcoatlus-northropi-postrain-stream-ventral-habitat-ecology-imagegen-v3.png |
| 82 | tyrannosaurus-rex | 1 | watch | 0.466 | mirrored | 1/2 | representative/color-pattern | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-pointbar-bluecharcoal-lichen-copper-pattern-imagegen-v1.png |
| 83 | ankylosaurus-magniventris | 1 | watch | 0.466 | mirrored | 1/2 | representative/color-pattern | no | no | ankylosaurus-magniventris-hell-creek-broadskull-singleclub-representative-imagegen-v2.png<br>ankylosaurus-magniventris-pointbar-petrol-lavender-russet-pattern-imagegen-v2.png |
| 84 | dilophosaurus-wetherilli | 1 | watch | 0.545 | mirrored | 1/6 | representative/social-growth-defense | no | no | dilophosaurus-wetherilli-kayenta-twincrest-fourdigit-representative-imagegen-v2.png<br>dilophosaurus-wetherilli-subadult-dawn-growth-imagegen-v2.png |
| 85 | quetzalcoatlus-northropi | 1 | watch | 0.545 | direct | 3/5 | habitat-ecology/interaction | no | no | quetzalcoatlus-northropi-postrain-stream-ventral-habitat-ecology-imagegen-v3.png<br>quetzalcoatlus-northropi-alamosaurus-separated-ventral-ecology-imagegen-v3.png |
| 86 | glyptodon-reticulatus | 2 | watch | 0.52 | direct | 1/2 | representative/color-pattern | no | no | glyptodon-reticulatus-rigid-carapace-ringed-tail-representative-imagegen-v1.png<br>glyptodon-reticulatus-four-visible-feet-review-imagegen-v2.png |
| 87 | diplodocus-carnegiei | 1 | watch | 0.544 | direct | 3/4 | habitat-ecology/identity-anatomy | no | no | diplodocus-carnegiei-morrison-ecology-imagegen-v1.png<br>diplodocus-carnegiei-twilight-mudflat-violet-mint-tailrings-ecology-imagegen-v1.png |
| 88 | homalocephale-calathocercos | 3 | watch | 0.542 | direct | 1/2 | representative/color-pattern | no | no | homalocephale-calathocercos-low-flat-teal-fullbody-imagegen-v4.png<br>homalocephale-calathocercos-umber-coral-browse-pattern-imagegen-v4.png |
| 89 | coelophysis-bauri | 2 | medium | 0.581 | direct | 1/4 | representative/identity-anatomy | no | no | coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png<br>coelophysis-bauri-slenderneck-openfeet-imagegen-v3.png |
| 90 | adasaurus-mongoliensis | 4 | watch | 0.541 | mirrored | 1/2 | representative/color-pattern | no | no | adasaurus-mongoliensis-reduced-digit-ii-representative-imagegen-v2.png<br>adasaurus-mongoliensis-soot-indigo-dusty-teal-pattern-imagegen-v1.png |
| 91 | pentaceratops-sternbergii | 3 | watch | 0.541 | direct | 1/2 | representative/color-pattern | no | no | pentaceratops-sternbergii-pentagonal-frill-imagegen-v1.png<br>pentaceratops-sternbergii-sienna-teal-pattern-imagegen-v1.png |
| 92 | parasaurolophus-walkeri | 1 | watch | 0.54 | mirrored | 1/4 | representative/identity-anatomy | no | no | parasaurolophus-walkeri-dinosaurpark-lowcrest-mittenmanus-representative-imagegen-v2.png<br>parasaurolophus-walkeri-lowcamera-mittenmanus-anatomy-imagegen-v2.png |
| 93 | kosmoceratops-richardsoni | 3 | medium | 0.619 | direct | 2/4 | color-pattern/identity-anatomy | no | no | kosmoceratops-richardsoni-indigo-ochre-pattern-imagegen-v1.png<br>kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png |
| 94 | camptosaurus-dispar | 3 | watch | 0.539 | direct | 1/2 | representative/color-pattern | no | no | camptosaurus-dispar-beaked-iguanodontian-imagegen-v1.png<br>camptosaurus-dispar-teal-ochre-pattern-imagegen-v1.png |
| 95 | torosaurus-latus | 2 | watch | 0.499 | direct | 1/2 | representative/color-pattern | no | no | torosaurus-latus-skin-covered-frill-representative-imagegen-v2.png<br>torosaurus-latus-copper-covered-fenestra-pattern-imagegen-v2.png |
| 96 | anomalocaris-canadensis | 1 | watch | 0.474 | mirrored | 1/2 | representative/color-pattern | no | no | anomalocaris-canadensis-softbody-tailfan-representative-imagegen-v2.png<br>anomalocaris-canadensis-rightfacing-softflap-indigo-copper-imagegen-v2.png |
| 97 | tyrannosaurus-rex | 1 | watch | 0.538 | direct | 5/6 | interaction/social-growth-defense | no | no | tyrannosaurus-rex-edmontosaurus-braided-river-distance-ecology-imagegen-v1.png<br>tyrannosaurus-rex-triceratops-misty-channel-standoff-ecology-imagegen-v1.png |
| 98 | homalocephale-calathocercos | 3 | medium | 0.616 | direct | 1/3 | representative/habitat-ecology | no | yes | homalocephale-calathocercos-low-flat-teal-fullbody-imagegen-v4.png<br>homalocephale-calathocercos-charcoal-flatcap-overcast-anatomy-imagegen-v4.png |
| 99 | ichthyosaurus-communis | 2 | watch | 0.576 | direct | 2/5 | color-pattern/interaction | no | no | ichthyosaurus-communis-indigo-slate-pattern-imagegen-v1.png<br>ichthyosaurus-communis-fish-chase-ecology-imagegen-v1.png |
| 100 | utahceratops-gettyi | 4 | medium | 0.614 | direct | 2/4 | color-pattern/identity-anatomy | no | yes | utahceratops-gettyi-moss-rust-pattern-imagegen-v1.png<br>utahceratops-gettyi-slate-moss-lateral-pattern-imagegen-v1.png |

## Gate

- Treat high similarity as a review signal, not proof of duplication; inspect original-size images before acting.
- A new candidate must materially change pose/action, camera family, spatial layout, subject count, or habitat; palette-only and mirror-only changes do not count.
- Keep candidates in the ignored local review queue until provenance and anatomy review are complete.
- Do not promote a representative from this report alone.

## Execution summary (B1-B9)

- The full baseline audit covered 155 taxa, 871 approved images, and 2,103 within-taxon pairs.
- Nine small review batches covered 27 distinct taxa and 47 generated attempts: 21 candidates were retained in the ignored pending review queue and 26 failed attempts were rejected and removed from the checked generated-cache, staging, and pending surfaces after exact-hash verification.
- Every retained candidate remains `review-hold`, non-representative, and ineligible for automatic promotion. Anatomy approval and app integration remain separate manual gates.
- Existing S1 representative side/full-body images, public `assets/dinosaurs/` assignments, `app.js`, and `gallery-slots.js` were not changed by this pass.
- This pass completes candidate generation and intake for the highest-priority and child-recognizable review set. It does not claim that public gallery duplication is already fixed; Tier B watch items and semantic identity/reference exceptions remain queued for later manual review.
