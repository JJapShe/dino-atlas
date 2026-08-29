# Dino Atlas gallery composition similarity audit

> This report ranks visual-composition risk. It is not an anatomy pass and never authorizes representative promotion.

## Baseline

- Taxa in audit scope: 161
- Taxa with assigned gallery slots in scope: 161
- Total taxa in app data: 161
- Total taxa with assigned gallery slots: 161
- Audited unique approved images: 889
- Compared within-taxon pairs: 2121
- Reporting threshold: 0.45
- Pairs at or above threshold: 682

Fixed-threshold distribution:

- >= 0.45: 682
- >= 0.55: 131
- >= 0.65: 14
- >= 0.75: 8

## Priority taxa

| Rank | Taxon | LV | Flagged pairs | Max structural | Max priority | Critical | High | Mirrored | Recolor risk | Suggested route |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | meganeura-monyi | 1 | 1 | 0.965 | 1.14 | 1 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 2 | quetzalcoatlus-northropi | 1 | 5 | 0.997 | 1.092 | 1 | 0 | 0 | 2 | change-camera-distance-direction-subject-count-or-habitat |
| 3 | herrerasaurus-ischigualastensis | 3 | 7 | 0.98 | 1.075 | 1 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 4 | inostrancevia-alexandri | 2 | 3 | 0.924 | 1.059 | 1 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 5 | psittacosaurus-mongoliensis | 2 | 8 | 0.971 | 1.011 | 1 | 0 | 4 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 6 | dsungaripterus-weii | 3 | 8 | 0.902 | 0.997 | 1 | 0 | 2 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 7 | almas-ukhaa | 4 | 3 | 0.886 | 0.981 | 1 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 8 | ankylosaurus-magniventris | 1 | 9 | 0.783 | 0.878 | 1 | 1 | 6 | 0 | change-camera-distance-direction-subject-count-or-habitat |
| 9 | otodus-megalodon | 1 | 3 | 0.646 | 0.806 | 0 | 1 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 10 | therizinosaurus-cheloniformis | 1 | 7 | 0.677 | 0.772 | 0 | 0 | 5 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 11 | velociraptor-mongoliensis | 1 | 4 | 0.597 | 0.772 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 12 | spinosaurus-aegyptiacus | 1 | 6 | 0.595 | 0.77 | 0 | 0 | 4 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 13 | dilophosaurus-wetherilli | 1 | 6 | 0.58 | 0.755 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 14 | parasaurolophus-walkeri | 1 | 9 | 0.579 | 0.754 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 15 | carnotaurus-sastrei | 1 | 2 | 0.575 | 0.75 | 0 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 16 | utahceratops-gettyi | 4 | 15 | 0.654 | 0.749 | 0 | 1 | 5 | 3 | replace-pattern-slot-with-opposite-action-or-scale |
| 17 | nasutoceratops-titusi | 2 | 10 | 0.614 | 0.749 | 0 | 0 | 6 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 18 | goyocephale-lattimorei | 3 | 9 | 0.726 | 0.741 | 0 | 1 | 6 | 0 | avoid-mirror-variant-change-camera-height-and-pose |
| 19 | edmontosaurus-annectens | 2 | 8 | 0.604 | 0.739 | 0 | 0 | 0 | 2 | replace-pattern-slot-with-opposite-action-or-scale |
| 20 | ichthyosaurus-communis | 2 | 10 | 0.603 | 0.738 | 0 | 0 | 4 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 21 | agujaceratops-mariscalensis | 4 | 13 | 0.64 | 0.735 | 0 | 1 | 6 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 22 | saurolophus-angustirostris | 2 | 12 | 0.592 | 0.727 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 23 | centrosaurus-apertus | 2 | 6 | 0.587 | 0.722 | 0 | 0 | 3 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 24 | mammuthus-primigenius | 1 | 3 | 0.553 | 0.713 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 25 | apatosaurus-ajax | 1 | 4 | 0.615 | 0.71 | 0 | 0 | 2 | 0 | change-camera-distance-direction-subject-count-or-habitat |
| 26 | efraasia-minor | 4 | 6 | 0.614 | 0.709 | 0 | 0 | 2 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 27 | giganotosaurus-carolinii | 1 | 1 | 0.531 | 0.706 | 0 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 28 | kosmoceratops-richardsoni | 3 | 15 | 0.665 | 0.705 | 0 | 0 | 5 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 29 | tarbosaurus-bataar | 1 | 18 | 0.602 | 0.702 | 0 | 0 | 0 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 30 | avimimus-portentosus | 3 | 11 | 0.603 | 0.698 | 0 | 0 | 5 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 31 | coelodonta-antiquitatis | 2 | 3 | 0.578 | 0.698 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 32 | plesiosaurus-dolichodeirus | 2 | 7 | 0.561 | 0.696 | 0 | 0 | 1 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 33 | nyctosaurus-gracilis | 3 | 5 | 0.672 | 0.687 | 0 | 0 | 0 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 34 | allosaurus-fragilis | 1 | 3 | 0.589 | 0.684 | 0 | 0 | 0 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 35 | shonisaurus-popularis | 3 | 13 | 0.608 | 0.683 | 0 | 0 | 8 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 36 | byronosaurus-jaffei | 4 | 9 | 0.587 | 0.682 | 0 | 0 | 2 | 0 | replace-pattern-slot-with-opposite-action-or-scale |
| 37 | diplodocus-carnegiei | 1 | 7 | 0.583 | 0.678 | 0 | 0 | 2 | 1 | change-camera-distance-direction-subject-count-or-habitat |
| 38 | conchoraptor-gracilis | 4 | 5 | 0.583 | 0.678 | 0 | 0 | 3 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 39 | citipati-osmolskae | 3 | 4 | 0.581 | 0.676 | 0 | 0 | 2 | 1 | replace-pattern-slot-with-opposite-action-or-scale |
| 40 | stegosaurus-stenops | 1 | 4 | 0.579 | 0.674 | 0 | 0 | 2 | 0 | change-camera-distance-direction-subject-count-or-habitat |

## Ranked pairs

| Rank | Taxon | LV | Risk | Structural | Mode | Slots | Roles | Same composition | Recolor risk | Sources |
| ---: | --- | ---: | --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | meganeura-monyi | 1 | critical | 0.965 | direct | 1/2 | representative/color-pattern | no | no | meganeura-monyi-fourwing-sixleg-representative-imagegen-v1.png<br>meganeura-monyi-petrol-copper-samebody-pattern-imagegen-v1.png |
| 2 | quetzalcoatlus-northropi | 1 | critical | 0.997 | direct | 1/5 | representative/interaction | no | no | quetzalcoatlus-northropi-ventral-ankle-membrane-representative-imagegen-v3.png<br>quetzalcoatlus-northropi-alamosaurus-separated-ventral-ecology-imagegen-v3.png |
| 3 | herrerasaurus-ischigualastensis | 3 | critical | 0.98 | direct | 1/2 | representative/color-pattern | no | no | herrerasaurus-ischigualastensis-canonical-redbed-representative-imagegen-v3.png<br>herrerasaurus-ischigualastensis-charcoal-russet-mottling-pattern-imagegen-v3.png |
| 4 | inostrancevia-alexandri | 2 | critical | 0.924 | direct | 1/2 | representative/color-pattern | no | no | inostrancevia-alexandri-lowskull-saberpair-representative-imagegen-v1.png<br>inostrancevia-alexandri-charcoal-sienna-samebody-pattern-imagegen-v1.png |
| 5 | psittacosaurus-mongoliensis | 2 | critical | 0.971 | direct | 1/7 | representative/alternate-habitat-behavior | no | yes | psittacosaurus-mongoliensis-smallskull-jugalhorn-representative-imagegen-v1.png<br>psittacosaurus-mongoliensis-genus-tail-bristle-anatomy-imagegen-v1.png |
| 6 | dsungaripterus-weii | 3 | critical | 0.902 | direct | 1/2 | representative/color-pattern | no | yes | dsungaripterus-weii-toothless-upturned-rostrum-posterior-crusher-representative-imagegen-v2.png<br>dsungaripterus-weii-iron-red-turquoise-wing-pattern-imagegen-v2.png |
| 7 | almas-ukhaa | 4 | critical | 0.886 | direct | 1/2 | representative/color-pattern | no | no | almas-ukhaa-short-deep-skull-olive-unbanded-representative-imagegen-v2.png<br>almas-ukhaa-short-deep-skull-aubergine-unbanded-pattern-imagegen-v2.png |
| 8 | ankylosaurus-magniventris | 1 | critical | 0.783 | direct | 1/5 | representative/interaction | no | no | ankylosaurus-magniventris-hell-creek-broadskull-singleclub-representative-imagegen-v2.png<br>ankylosaurus-magniventris-oxbow-edmontosaurus-coexistence-ecology-imagegen-v2.png |
| 9 | ankylosaurus-magniventris | 1 | high | 0.724 | direct | 1/6 | representative/social-growth-defense | no | no | ankylosaurus-magniventris-hell-creek-broadskull-singleclub-representative-imagegen-v2.png<br>ankylosaurus-magniventris-lateral-tail-sweep-defense-imagegen-v2.png |
| 10 | otodus-megalodon | 1 | high | 0.646 | mirrored | 1/2 | representative/color-pattern | no | no | otodus-megalodon-elongated-blunt-rostrum-representative-imagegen-v1.png<br>otodus-megalodon-rightfacing-slate-bronze-pattern-imagegen-v1.png |
| 11 | quetzalcoatlus-northropi | 1 | medium | 0.6 | direct | 1/2 | representative/color-pattern | no | yes | quetzalcoatlus-northropi-ventral-ankle-membrane-representative-imagegen-v3.png<br>quetzalcoatlus-northropi-indigo-jade-ventral-ankle-pattern-imagegen-v3.png |
| 12 | therizinosaurus-cheloniformis | 1 | medium | 0.677 | direct | 1/4 | representative/identity-anatomy | no | no | therizinosaurus-cheloniformis-giant-scythe-claws-imagegen-v1.png<br>therizinosaurus-cheloniformis-straight-triclaw-fourtoe-anatomy-imagegen-v1.png |
| 13 | velociraptor-mongoliensis | 1 | medium | 0.597 | mirrored | 1/2 | representative/color-pattern | no | no | velociraptor-mongoliensis-djadokhta-raised-second-toe-representative-imagegen-v1.png<br>velociraptor-mongoliensis-dawn-slate-celadon-pattern-imagegen-v1.png |
| 14 | spinosaurus-aegyptiacus | 1 | medium | 0.595 | mirrored | 1/2 | representative/color-pattern | no | yes | spinosaurus-aegyptiacus-kemkem-shortleg-deeptail-threefinger-representative-imagegen-v1.png<br>spinosaurus-aegyptiacus-rainflat-indigo-vermilion-turquoise-pattern-imagegen-v1.png |
| 15 | dilophosaurus-wetherilli | 1 | medium | 0.58 | mirrored | 1/2 | representative/color-pattern | no | no | dilophosaurus-wetherilli-kayenta-twincrest-fourdigit-representative-imagegen-v2.png<br>dilophosaurus-wetherilli-petrol-violet-celadon-pattern-imagegen-v2.png |
| 16 | parasaurolophus-walkeri | 1 | watch | 0.579 | mirrored | 1/2 | representative/color-pattern | no | no | parasaurolophus-walkeri-dinosaurpark-lowcrest-mittenmanus-representative-imagegen-v2.png<br>parasaurolophus-walkeri-petrol-celadon-russet-pattern-imagegen-v2.png |
| 17 | carnotaurus-sastrei | 1 | watch | 0.575 | mirrored | 1/2 | representative/color-pattern | no | no | carnotaurus-sastrei-browhorn-shortskull-representative-imagegen-v2.png<br>carnotaurus-sastrei-rust-charcoal-pattern-variant-imagegen-v2.png |
| 18 | utahceratops-gettyi | 4 | high | 0.654 | direct | 1/2 | representative/color-pattern | no | no | utahceratops-gettyi-notched-frill-lateral-browhorns-imagegen-v1.png<br>utahceratops-gettyi-moss-rust-pattern-imagegen-v1.png |
| 19 | nasutoceratops-titusi | 2 | medium | 0.614 | mirrored | 1/2 | representative/color-pattern | no | yes | nasutoceratops-titusi-hugenaris-twisted-browhorn-representative-imagegen-v1.png<br>nasutoceratops-titusi-slate-teal-rust-reverse-pattern-imagegen-v1.png |
| 20 | goyocephale-lattimorei | 3 | high | 0.726 | mirrored | 1/6 | representative/social-growth-defense | no | no | goyocephale-lattimorei-table-skull-gracile-representative-imagegen-v2.png<br>goyocephale-lattimorei-tendon-tail-brisk-walk-anatomy-imagegen-v1.png |
| 21 | edmontosaurus-annectens | 2 | medium | 0.604 | direct | 1/2 | representative/color-pattern | no | yes | edmontosaurus-annectens-lance-softcrest-hooves-representative-imagegen-v1.png<br>edmontosaurus-annectens-petrol-celadon-russet-pattern-imagegen-v3.png |
| 22 | ichthyosaurus-communis | 2 | medium | 0.603 | direct | 1/2 | representative/color-pattern | no | no | ichthyosaurus-communis-streamlined-sideprofile-imagegen-v1.png<br>ichthyosaurus-communis-indigo-slate-pattern-imagegen-v1.png |
| 23 | agujaceratops-mariscalensis | 4 | high | 0.64 | direct | 1/2 | representative/color-pattern | no | no | agujaceratops-mariscalensis-heartfrill-longhorns-imagegen-v1.png<br>agujaceratops-mariscalensis-teal-sienna-pattern-imagegen-v1.png |
| 24 | saurolophus-angustirostris | 2 | medium | 0.592 | direct | 1/2 | representative/color-pattern | no | no | saurolophus-angustirostris-spike-crest-fullbody-imagegen-v1.png<br>saurolophus-angustirostris-copper-spruce-pattern-imagegen-v1.png |
| 25 | therizinosaurus-cheloniformis | 1 | watch | 0.552 | mirrored | 1/2 | representative/color-pattern | no | no | therizinosaurus-cheloniformis-giant-scythe-claws-imagegen-v1.png<br>therizinosaurus-cheloniformis-bilateral-triclaw-petrol-dawn-pattern-imagegen-v4.png |
| 26 | centrosaurus-apertus | 2 | medium | 0.587 | mirrored | 1/2 | representative/color-pattern | no | no | centrosaurus-apertus-procurved-nasalhorn-p1-p2-representative-imagegen-v1.png<br>centrosaurus-apertus-moss-ochre-teal-pattern-imagegen-v1.png |
| 27 | mammuthus-primigenius | 1 | watch | 0.553 | mirrored | 1/2 | representative/color-pattern | no | no | mammuthus-primigenius-high-shoulder-spiral-tusks-representative-imagegen-v1.png<br>mammuthus-primigenius-right-facing-charcoal-coat-review-imagegen-v2.png |
| 28 | apatosaurus-ajax | 1 | medium | 0.615 | direct | 1/4 | representative/identity-anatomy | no | no | apatosaurus-ajax-robust-lowneck-morrison-representative-imagegen-v1.png<br>apatosaurus-ajax-thumbclaw-threehindclaw-anatomy-imagegen-v1.png |
| 29 | efraasia-minor | 4 | medium | 0.614 | direct | 1/2 | representative/color-pattern | no | yes | efraasia-minor-slender-sauropodomorph-imagegen-v1.png<br>efraasia-minor-teal-ochre-pattern-imagegen-v1.png |
| 30 | giganotosaurus-carolinii | 1 | watch | 0.531 | direct | 1/2 | representative/color-pattern | no | no | giganotosaurus-carolinii-lowskull-lacrimal-ridge-representative-imagegen-v1.png<br>giganotosaurus-carolinii-charcoal-russet-pattern-variant-imagegen-v1.png |
| 31 | kosmoceratops-richardsoni | 3 | medium | 0.61 | direct | 1/2 | representative/color-pattern | no | no | kosmoceratops-richardsoni-ornate-solid-frill-imagegen-v1.png<br>kosmoceratops-richardsoni-indigo-ochre-pattern-imagegen-v1.png |
| 32 | tarbosaurus-bataar | 1 | watch | 0.527 | direct | 1/2 | representative/color-pattern | no | no | tarbosaurus-bataar-narrow-skull-two-fingers-imagegen-v1.png<br>tarbosaurus-bataar-basalt-rust-pattern-imagegen-v1.png |
| 33 | avimimus-portentosus | 3 | medium | 0.603 | direct | 1/2 | representative/color-pattern | no | no | avimimus-portentosus-beaked-feathered-imagegen-v1.png<br>avimimus-portentosus-violet-amber-pattern-imagegen-v1.png |
| 34 | coelodonta-antiquitatis | 2 | watch | 0.578 | mirrored | 1/2 | representative/color-pattern | no | no | coelodonta-antiquitatis-laterally-compressed-bladehorn-representative-imagegen-v2.png<br>coelodonta-antiquitatis-leftfacing-tawny-patch-pattern-imagegen-v1.png |
| 35 | tarbosaurus-bataar | 1 | medium | 0.602 | direct | 1/4 | representative/identity-anatomy | no | no | tarbosaurus-bataar-narrow-skull-two-fingers-imagegen-v1.png<br>tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png |
| 36 | plesiosaurus-dolichodeirus | 2 | watch | 0.561 | mirrored | 1/2 | representative/color-pattern | no | no | plesiosaurus-dolichodeirus-longneck-sideprofile-imagegen-v1.png<br>plesiosaurus-dolichodeirus-teal-copper-pattern-imagegen-v1.png |
| 37 | quetzalcoatlus-northropi | 1 | medium | 0.598 | direct | 2/5 | color-pattern/interaction | no | yes | quetzalcoatlus-northropi-indigo-jade-ventral-ankle-pattern-imagegen-v3.png<br>quetzalcoatlus-northropi-alamosaurus-separated-ventral-ecology-imagegen-v3.png |
| 38 | nyctosaurus-gracilis | 3 | medium | 0.672 | direct | 1/4 | representative/identity-anatomy | no | yes | nyctosaurus-gracilis-crestless-seaway-representative-imagegen-v2.png<br>nyctosaurus-gracilis-clawless-three-phalange-anatomy-imagegen-v2.png |
| 39 | allosaurus-fragilis | 1 | medium | 0.589 | direct | 1/4 | representative/identity-anatomy | no | yes | allosaurus-fragilis-morrison-lowhorn-threefinger-representative-imagegen-v1.png<br>allosaurus-fragilis-threefinger-lowhorn-anatomy-imagegen-v1.png |
| 40 | shonisaurus-popularis | 3 | medium | 0.588 | mirrored | 1/2 | representative/color-pattern | no | yes | shonisaurus-popularis-nevada-giant-shastasaurid-imagegen-v1.png<br>shonisaurus-popularis-indigo-opal-pattern-imagegen-v1.png |
| 41 | byronosaurus-jaffei | 4 | medium | 0.587 | direct | 1/2 | representative/color-pattern | no | no | byronosaurus-jaffei-unserrated-teeth-troodontid-imagegen-v1.png<br>byronosaurus-jaffei-indigo-jade-pattern-imagegen-v1.png |
| 42 | therizinosaurus-cheloniformis | 1 | medium | 0.586 | mirrored | 2/4 | color-pattern/identity-anatomy | no | yes | therizinosaurus-cheloniformis-bilateral-triclaw-petrol-dawn-pattern-imagegen-v4.png<br>therizinosaurus-cheloniformis-straight-triclaw-fourtoe-anatomy-imagegen-v1.png |
| 43 | kosmoceratops-richardsoni | 3 | medium | 0.665 | direct | 3/4 | habitat-ecology/identity-anatomy | no | yes | kosmoceratops-richardsoni-kaiparowits-herd-ecology-imagegen-v1.png<br>kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png |
| 44 | diplodocus-carnegiei | 1 | medium | 0.583 | direct | 1/5 | representative/interaction | no | yes | diplodocus-carnegiei-lowbody-imagegen-v1.png<br>diplodocus-carnegiei-distant-allosaurus-tail-posture-interaction-imagegen-v2.png |
| 45 | conchoraptor-gracilis | 4 | medium | 0.583 | mirrored | 1/2 | representative/color-pattern | no | yes | conchoraptor-gracilis-flat-skull-nuchal-step-representative-imagegen-v2.png<br>conchoraptor-gracilis-charcoal-rust-dawn-pattern-imagegen-v2.png |
| 46 | citipati-osmolskae | 3 | medium | 0.581 | mirrored | 1/2 | representative/color-pattern | no | yes | citipati-osmolskae-vertical-premaxilla-deepbeak-lowcrest-representative-imagegen-v1.png<br>citipati-osmolskae-petrol-saffron-cream-pattern-imagegen-v1.png |
| 47 | stegosaurus-stenops | 1 | watch | 0.579 | direct | 1/4 | representative/identity-anatomy | no | no | stegosaurus-stenops-copperplate-upward-v-thagomizer-representative-imagegen-v1.png<br>stegosaurus-stenops-alternating-plate-upward-v-identity-imagegen-v1.png |
| 48 | riojasaurus-incertus | 4 | watch | 0.577 | mirrored | 1/2 | representative/color-pattern | no | no | riojasaurus-incertus-long-low-skull-robust-forelimb-representative-imagegen-v1.png<br>riojasaurus-incertus-plum-petrol-celadon-pattern-imagegen-v1.png |
| 49 | hesperosaurus-mjosi | 4 | watch | 0.577 | mirrored | 1/2 | representative/color-pattern | no | no | hesperosaurus-mjosi-broadskull-lowplates-fourspike-representative-imagegen-v1.png<br>hesperosaurus-mjosi-petrol-plum-grooved-plate-pattern-imagegen-v1.png |
| 50 | ankylosaurus-magniventris | 1 | watch | 0.574 | direct | 5/6 | interaction/social-growth-defense | no | no | ankylosaurus-magniventris-oxbow-edmontosaurus-coexistence-ecology-imagegen-v2.png<br>ankylosaurus-magniventris-lateral-tail-sweep-defense-imagegen-v2.png |
| 51 | kronosaurus-queenslandicus | 2 | watch | 0.532 | direct | 1/2 | representative/color-pattern | no | no | kronosaurus-queenslandicus-eromanga-giant-skull-pliosaur-imagegen-v1.png<br>kronosaurus-queenslandicus-bottlegreen-ivory-ocelli-pattern-imagegen-v2.png |
| 52 | dilophosaurus-wetherilli | 1 | watch | 0.57 | direct | 2/6 | color-pattern/social-growth-defense | no | no | dilophosaurus-wetherilli-petrol-violet-celadon-pattern-imagegen-v2.png<br>dilophosaurus-wetherilli-subadult-dawn-growth-imagegen-v2.png |
| 53 | yutyrannus-huali | 2 | medium | 0.609 | direct | 1/4 | representative/identity-anatomy | no | yes | yutyrannus-huali-yixian-white-mottled-feathered-representative-imagegen-v1.png<br>yutyrannus-huali-cold-dawn-breath-threefinger-anatomy-imagegen-v1.png |
| 54 | saturnalia-tupiniquim | 4 | watch | 0.569 | mirrored | 1/2 | representative/color-pattern | no | no | saturnalia-tupiniquim-bottlegreen-brickred-waldsanga-representative-imagegen-v2.png<br>saturnalia-tupiniquim-aubergine-turquoise-bluehour-pattern-imagegen-v2.png |
| 55 | deinocheirus-mirificus | 2 | medium | 0.608 | direct | 1/3 | representative/habitat-ecology | no | yes | deinocheirus-mirificus-tridactyl-broadfoot-anatomy-imagegen-v1.png<br>deinocheirus-mirificus-bilateral-tridactyl-rainwet-habitat-imagegen-v3.png |
| 56 | diplodocus-carnegiei | 1 | watch | 0.485 | mirrored | 1/2 | representative/color-pattern | no | no | diplodocus-carnegiei-lowbody-imagegen-v1.png<br>diplodocus-carnegiei-teal-saddle-pattern-imagegen-v1.png |
| 57 | edmontosaurus-annectens | 2 | medium | 0.604 | direct | 5/6 | interaction/social-growth-defense | no | yes | edmontosaurus-annectens-tyrannosaurus-channel-standoff-ecology-imagegen-v1.png<br>edmontosaurus-annectens-adult-juvenile-drychannel-growth-ecology-imagegen-v1.png |
| 58 | otodus-megalodon | 1 | watch | 0.577 | mirrored | 1/3 | representative/habitat-ecology | no | no | otodus-megalodon-elongated-blunt-rostrum-representative-imagegen-v1.png<br>otodus-megalodon-neogene-whale-distance-ecology-imagegen-v1.png |
| 59 | sauropelta-edwardsorum | 3 | medium | 0.641 | mirrored | 4/6 | identity-anatomy/social-growth-defense | no | no | sauropelta-edwardsorum-shoulder-spine-anatomy-imagegen-v2.png<br>sauropelta-edwardsorum-solitary-shoulder-brace-ecology-imagegen-v2.png |
| 60 | bagualosaurus-agudoensis | 4 | watch | 0.56 | direct | 1/2 | representative/color-pattern | no | no | bagualosaurus-agudoensis-robust-herbivore-imagegen-v1.png<br>bagualosaurus-agudoensis-bluegray-copper-pattern-imagegen-v1.png |
| 61 | tyrannosaurus-rex | 1 | watch | 0.56 | mirrored | 1/6 | representative/social-growth-defense | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-triceratops-misty-channel-standoff-ecology-imagegen-v1.png |
| 62 | plateosaurus-engelhardti | 2 | watch | 0.52 | direct | 1/2 | representative/color-pattern | no | no | plateosaurus-engelhardti-imagegen-v25-source-candidate.png<br>plateosaurus-engelhardti-imagegen-v28-source-candidate.png |
| 63 | kosmoceratops-richardsoni | 3 | medium | 0.639 | mirrored | 3/5 | habitat-ecology/interaction | no | no | kosmoceratops-richardsoni-kaiparowits-herd-ecology-imagegen-v1.png<br>kosmoceratops-richardsoni-channel-separated-hadrosaurid-ecology-imagegen-v1.png |
| 64 | ichthyosaurus-communis | 2 | medium | 0.599 | direct | 1/5 | representative/interaction | no | no | ichthyosaurus-communis-streamlined-sideprofile-imagegen-v1.png<br>ichthyosaurus-communis-fish-chase-ecology-imagegen-v1.png |
| 65 | zanabazar-junior | 4 | watch | 0.559 | direct | 1/2 | representative/color-pattern | no | no | zanabazar-junior-large-nemegt-troodontid-imagegen-v1.png<br>zanabazar-junior-teal-plum-pattern-imagegen-v1.png |
| 66 | monolophosaurus-jiangi | 2 | watch | 0.519 | direct | 1/2 | representative/color-pattern | no | no | monolophosaurus-jiangi-single-midline-crest-representative-imagegen-v3.png<br>monolophosaurus-jiangi-cobalt-celadon-pattern-imagegen-v2.png |
| 67 | dunkleosteus-terrelli | 1 | watch | 0.494 | direct | 1/2 | representative/color-pattern | no | no | dunkleosteus-terrelli-single-dorsal-compact-armor-representative-imagegen-v2.png<br>dunkleosteus-terrelli-leftfacing-single-dorsal-copper-pattern-imagegen-v2.png |
| 68 | spinosaurus-aegyptiacus | 1 | watch | 0.557 | direct | 1/6 | representative/social-growth-defense | no | no | spinosaurus-aegyptiacus-kemkem-shortleg-deeptail-threefinger-representative-imagegen-v1.png<br>spinosaurus-aegyptiacus-sunrise-sail-display-ecology-imagegen-v1.png |
| 69 | placodus-gigas | 3 | watch | 0.556 | direct | 1/2 | representative/color-pattern | no | no | placodus-gigas-three-premaxillary-teeth-representative-imagegen-v3.png<br>placodus-gigas-blackberry-jade-rust-closed-mouth-pattern-imagegen-v3.png |
| 70 | carcharodontosaurus-saharicus | 2 | watch | 0.516 | mirrored | 1/2 | representative/color-pattern | no | no | carcharodontosaurus-saharicus-longskull-kemkem-representative-imagegen-v2.png<br>carcharodontosaurus-saharicus-slate-copper-pattern-variant-imagegen-v2.png |
| 71 | sarahsaurus-aurifontanalis | 4 | watch | 0.554 | mirrored | 1/2 | representative/color-pattern | no | no | sarahsaurus-aurifontanalis-powerful-hands-fullbody-imagegen-v1.png<br>sarahsaurus-aurifontanalis-bluegray-copper-pattern-imagegen-v1.png |
| 72 | tarbosaurus-bataar | 1 | watch | 0.554 | direct | 3/6 | habitat-ecology/social-growth-defense | no | no | tarbosaurus-bataar-nemegt-ecology-imagegen-v1.png<br>tarbosaurus-bataar-adult-juvenile-riverbar-growth-ecology-imagegen-v1.png |
| 73 | kosmoceratops-richardsoni | 3 | medium | 0.632 | mirrored | 4/5 | identity-anatomy/interaction | no | no | kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png<br>kosmoceratops-richardsoni-channel-separated-hadrosaurid-ecology-imagegen-v1.png |
| 74 | leptoceratops-gracilis | 3 | medium | 0.632 | direct | 1/4 | representative/identity-anatomy | no | no | leptoceratops-gracilis-modest-frill-imagegen-v1.png<br>leptoceratops-gracilis-low-solid-frill-four-foot-anatomy-imagegen-v1.png |
| 75 | styracosaurus-albertensis | 2 | medium | 0.592 | direct | 3/6 | habitat-ecology/social-growth-defense | no | no | styracosaurus-albertensis-meander-pointbar-low-browse-ecology-imagegen-v2.png<br>styracosaurus-albertensis-separated-adult-subadult-growth-ecology-imagegen-v2.png |
| 76 | tarbosaurus-bataar | 1 | watch | 0.552 | direct | 2/4 | color-pattern/identity-anatomy | no | no | tarbosaurus-bataar-basalt-rust-pattern-imagegen-v1.png<br>tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png |
| 77 | tarbosaurus-bataar | 1 | watch | 0.552 | direct | 4/6 | identity-anatomy/social-growth-defense | no | no | tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png<br>tarbosaurus-bataar-adult-juvenile-riverbar-growth-ecology-imagegen-v1.png |
| 78 | brachiosaurus-altithorax | 1 | watch | 0.472 | mirrored | 1/2 | representative/color-pattern | no | no | brachiosaurus-altithorax-nasal-mound-fullbody-imagegen-v18.png<br>brachiosaurus-altithorax-nasal-mound-slate-moss-rearthreequarter-pattern-imagegen-v2.png |
| 79 | leptoceratops-gracilis | 3 | watch | 0.551 | direct | 1/2 | representative/color-pattern | no | no | leptoceratops-gracilis-modest-frill-imagegen-v1.png<br>leptoceratops-gracilis-slate-speckle-pattern-imagegen-v1.png |
| 80 | tyrannosaurus-rex | 1 | watch | 0.55 | direct | 1/3 | representative/habitat-ecology | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-dawn-channel-crossing-ecology-imagegen-v1.png |
| 81 | sinornithosaurus-millenii | 3 | watch | 0.549 | direct | 1/2 | representative/color-pattern | no | no | sinornithosaurus-millenii-longarm-filament-representative-imagegen-v2.png<br>sinornithosaurus-millenii-plum-lichen-bluehour-pattern-imagegen-v1.png |
| 82 | pachycephalosaurus-wyomingensis | 1 | watch | 0.468 | mirrored | 1/2 | representative/color-pattern | no | no | pachycephalosaurus-wyomingensis-hellcreek-dome-representative-imagegen-v1.png<br>pachycephalosaurus-wyomingensis-bluehour-blueblack-ochre-pattern-imagegen-v1.png |
| 83 | quetzalcoatlus-northropi | 1 | watch | 0.546 | direct | 1/3 | representative/habitat-ecology | no | no | quetzalcoatlus-northropi-ventral-ankle-membrane-representative-imagegen-v3.png<br>quetzalcoatlus-northropi-postrain-stream-ventral-habitat-ecology-imagegen-v3.png |
| 84 | tyrannosaurus-rex | 1 | watch | 0.466 | mirrored | 1/2 | representative/color-pattern | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-pointbar-bluecharcoal-lichen-copper-pattern-imagegen-v1.png |
| 85 | ankylosaurus-magniventris | 1 | watch | 0.466 | mirrored | 1/2 | representative/color-pattern | no | no | ankylosaurus-magniventris-hell-creek-broadskull-singleclub-representative-imagegen-v2.png<br>ankylosaurus-magniventris-pointbar-petrol-lavender-russet-pattern-imagegen-v2.png |
| 86 | dilophosaurus-wetherilli | 1 | watch | 0.545 | mirrored | 1/6 | representative/social-growth-defense | no | no | dilophosaurus-wetherilli-kayenta-twincrest-fourdigit-representative-imagegen-v2.png<br>dilophosaurus-wetherilli-subadult-dawn-growth-imagegen-v2.png |
| 87 | quetzalcoatlus-northropi | 1 | watch | 0.545 | direct | 3/5 | habitat-ecology/interaction | no | no | quetzalcoatlus-northropi-postrain-stream-ventral-habitat-ecology-imagegen-v3.png<br>quetzalcoatlus-northropi-alamosaurus-separated-ventral-ecology-imagegen-v3.png |
| 88 | glyptodon-reticulatus | 2 | watch | 0.52 | direct | 1/2 | representative/color-pattern | no | no | glyptodon-reticulatus-rigid-carapace-ringed-tail-representative-imagegen-v1.png<br>glyptodon-reticulatus-four-visible-feet-review-imagegen-v2.png |
| 89 | diplodocus-carnegiei | 1 | watch | 0.544 | direct | 3/4 | habitat-ecology/identity-anatomy | no | no | diplodocus-carnegiei-morrison-ecology-imagegen-v1.png<br>diplodocus-carnegiei-twilight-mudflat-violet-mint-tailrings-ecology-imagegen-v1.png |
| 90 | homalocephale-calathocercos | 3 | watch | 0.542 | direct | 1/2 | representative/color-pattern | no | no | homalocephale-calathocercos-low-flat-teal-fullbody-imagegen-v4.png<br>homalocephale-calathocercos-umber-coral-browse-pattern-imagegen-v4.png |
| 91 | coelophysis-bauri | 2 | medium | 0.581 | direct | 1/4 | representative/identity-anatomy | no | no | coelophysis-bauri-slenderneck-smallhands-imagegen-v3.png<br>coelophysis-bauri-slenderneck-openfeet-imagegen-v3.png |
| 92 | adasaurus-mongoliensis | 4 | watch | 0.541 | mirrored | 1/2 | representative/color-pattern | no | no | adasaurus-mongoliensis-reduced-digit-ii-representative-imagegen-v2.png<br>adasaurus-mongoliensis-soot-indigo-dusty-teal-pattern-imagegen-v1.png |
| 93 | pentaceratops-sternbergii | 3 | watch | 0.541 | direct | 1/2 | representative/color-pattern | no | no | pentaceratops-sternbergii-pentagonal-frill-imagegen-v1.png<br>pentaceratops-sternbergii-sienna-teal-pattern-imagegen-v1.png |
| 94 | parasaurolophus-walkeri | 1 | watch | 0.54 | mirrored | 1/4 | representative/identity-anatomy | no | no | parasaurolophus-walkeri-dinosaurpark-lowcrest-mittenmanus-representative-imagegen-v2.png<br>parasaurolophus-walkeri-lowcamera-mittenmanus-anatomy-imagegen-v2.png |
| 95 | kosmoceratops-richardsoni | 3 | medium | 0.619 | direct | 2/4 | color-pattern/identity-anatomy | no | no | kosmoceratops-richardsoni-indigo-ochre-pattern-imagegen-v1.png<br>kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png |
| 96 | camptosaurus-dispar | 3 | watch | 0.539 | direct | 1/2 | representative/color-pattern | no | no | camptosaurus-dispar-beaked-iguanodontian-imagegen-v1.png<br>camptosaurus-dispar-teal-ochre-pattern-imagegen-v1.png |
| 97 | torosaurus-latus | 2 | watch | 0.499 | direct | 1/2 | representative/color-pattern | no | no | torosaurus-latus-skin-covered-frill-representative-imagegen-v2.png<br>torosaurus-latus-copper-covered-fenestra-pattern-imagegen-v2.png |
| 98 | anomalocaris-canadensis | 1 | watch | 0.474 | mirrored | 1/2 | representative/color-pattern | no | no | anomalocaris-canadensis-softbody-tailfan-representative-imagegen-v2.png<br>anomalocaris-canadensis-rightfacing-softflap-indigo-copper-imagegen-v2.png |
| 99 | tyrannosaurus-rex | 1 | watch | 0.538 | direct | 5/6 | interaction/social-growth-defense | no | no | tyrannosaurus-rex-edmontosaurus-braided-river-distance-ecology-imagegen-v1.png<br>tyrannosaurus-rex-triceratops-misty-channel-standoff-ecology-imagegen-v1.png |
| 100 | homalocephale-calathocercos | 3 | medium | 0.616 | direct | 1/3 | representative/habitat-ecology | no | yes | homalocephale-calathocercos-low-flat-teal-fullbody-imagegen-v4.png<br>homalocephale-calathocercos-charcoal-flatcap-overcast-anatomy-imagegen-v4.png |
| 101 | ichthyosaurus-communis | 2 | watch | 0.576 | direct | 2/5 | color-pattern/interaction | no | no | ichthyosaurus-communis-indigo-slate-pattern-imagegen-v1.png<br>ichthyosaurus-communis-fish-chase-ecology-imagegen-v1.png |
| 102 | utahceratops-gettyi | 4 | medium | 0.614 | direct | 2/4 | color-pattern/identity-anatomy | no | yes | utahceratops-gettyi-moss-rust-pattern-imagegen-v1.png<br>utahceratops-gettyi-slate-moss-lateral-pattern-imagegen-v1.png |
| 103 | othnielosaurus-consors | 4 | watch | 0.534 | direct | 1/2 | representative/color-pattern | no | no | othnielosaurus-consors-small-beaked-runner-imagegen-v1.png<br>othnielosaurus-consors-teal-sienna-pattern-imagegen-v1.png |
| 104 | stygimoloch-spinifer | 2 | watch | 0.493 | mirrored | 1/2 | representative/color-pattern | no | no | stygimoloch-spinifer-single-spike-dome-imagegen-v1.png<br>stygimoloch-spinifer-brick-mantle-copper-bars-pattern-imagegen-v2.png |
| 105 | triceratops-horridus | 1 | watch | 0.547 | direct | 5/7 | interaction/alternate-habitat-behavior | no | no | triceratops-horridus-misty-channel-tyrannosaurus-standoff-ecology-imagegen-v2.png<br>triceratops-horridus-edmontosaurus-lower-hellcreek-portrait-ecology-imagegen-v2.png |
| 106 | therizinosaurus-cheloniformis | 1 | watch | 0.531 | mirrored | 2/5 | color-pattern/interaction | no | no | therizinosaurus-cheloniformis-bilateral-triclaw-petrol-dawn-pattern-imagegen-v4.png<br>therizinosaurus-cheloniformis-bilateral-triclaw-tarbosaurus-watergap-ecology-imagegen-v4.png |
| 107 | yutyrannus-huali | 2 | watch | 0.49 | direct | 1/2 | representative/color-pattern | no | no | yutyrannus-huali-yixian-white-mottled-feathered-representative-imagegen-v1.png<br>yutyrannus-huali-ash-white-slate-countershading-pattern-imagegen-v1.png |
| 108 | enigmacursor-mollyborthwickae | 4 | watch | 0.529 | direct | 1/2 | representative/color-pattern | no | no | enigmacursor-mollyborthwickae-runner-fullbody-imagegen-v1.png<br>enigmacursor-mollyborthwickae-bluegray-copper-pattern-imagegen-v1.png |
| 109 | mammut-americanum | 2 | watch | 0.504 | mirrored | 1/2 | representative/color-pattern | no | no | mammut-americanum-level-back-upcurved-tusks-representative-imagegen-v1.png<br>mammut-americanum-left-rear-woodland-review-imagegen-v1.png |
| 110 | shonisaurus-popularis | 3 | medium | 0.608 | mirrored | 2/4 | color-pattern/identity-anatomy | no | no | shonisaurus-popularis-indigo-opal-pattern-imagegen-v1.png<br>shonisaurus-popularis-nevada-offshore-cruise-imagegen-v2.png |
| 111 | zanabazar-junior | 4 | medium | 0.608 | direct | 1/5 | representative/interaction | no | no | zanabazar-junior-large-nemegt-troodontid-imagegen-v1.png<br>zanabazar-junior-channel-separated-tyrannosaurid-ecology-imagegen-v1.png |
| 112 | kosmoceratops-richardsoni | 3 | medium | 0.608 | direct | 1/4 | representative/identity-anatomy | no | no | kosmoceratops-richardsoni-ornate-solid-frill-imagegen-v1.png<br>kosmoceratops-richardsoni-bilateral-browhorn-anatomy-imagegen-v1.png |
| 113 | tylocephale-gilmorei | 4 | watch | 0.528 | direct | 1/2 | representative/color-pattern | no | no | tylocephale-gilmorei-barun-goyot-tall-dome-imagegen-v1.png<br>tylocephale-gilmorei-aubergine-umber-natural-saddle-pattern-imagegen-v3.png |
| 114 | pachycephalosaurus-wyomingensis | 1 | watch | 0.527 | direct | 1/3 | representative/habitat-ecology | no | no | pachycephalosaurus-wyomingensis-hellcreek-dome-representative-imagegen-v1.png<br>pachycephalosaurus-wyomingensis-crevasse-splay-browse-habitat-imagegen-v1.png |
| 115 | bagualosaurus-agudoensis | 4 | medium | 0.605 | direct | 2/3 | color-pattern/habitat-ecology | no | yes | bagualosaurus-agudoensis-bluegray-copper-pattern-imagegen-v1.png<br>bagualosaurus-agudoensis-santa-maria-group-ecology-imagegen-v1.png |
| 116 | almas-ukhaa | 4 | medium | 0.604 | direct | 4/5 | identity-anatomy/interaction | no | no | almas-ukhaa-short-deep-skull-postrain-anatomy-imagegen-v2.png<br>almas-ukhaa-channel-separated-ceratopsian-context-imagegen-v2.png |
| 117 | prenocephale-prenes | 3 | medium | 0.604 | direct | 3/6 | habitat-ecology/social-growth-defense | no | yes | prenocephale-prenes-nemegt-parallel-display-ecology-imagegen-v1.png<br>prenocephale-prenes-nemegt-channel-growth-stage-ecology-imagegen-v6.png |
| 118 | yutyrannus-huali | 2 | watch | 0.564 | direct | 5/6 | interaction/social-growth-defense | no | no | yutyrannus-huali-cold-breath-bloodfleck-unnamed-herbivore-hunt-ecology-imagegen-v1.png<br>yutyrannus-huali-cold-lakemargin-adult-subadult-growth-ecology-imagegen-v1.png |
| 119 | dimetrodon-grandis | 1 | watch | 0.459 | mirrored | 1/2 | representative/color-pattern | no | no | dimetrodon-grandis-clearfork-sail-canine-representative-imagegen-v1.png<br>dimetrodon-grandis-rightfacing-indigo-ochre-pattern-imagegen-v1.png |
| 120 | spinosaurus-aegyptiacus | 1 | watch | 0.523 | direct | 2/4 | color-pattern/identity-anatomy | no | no | spinosaurus-aegyptiacus-rainflat-indigo-vermilion-turquoise-pattern-imagegen-v1.png<br>spinosaurus-aegyptiacus-shortleg-threefinger-deeptail-anatomy-imagegen-v1.png |
| 121 | tarbosaurus-bataar | 1 | watch | 0.523 | direct | 1/6 | representative/social-growth-defense | no | no | tarbosaurus-bataar-narrow-skull-two-fingers-imagegen-v1.png<br>tarbosaurus-bataar-adult-juvenile-riverbar-growth-ecology-imagegen-v1.png |
| 122 | amtocephale-gobiensis | 4 | watch | 0.521 | direct | 1/2 | representative/color-pattern | no | no | amtocephale-gobiensis-baynshire-thick-dome-imagegen-v1.png<br>amtocephale-gobiensis-charcoal-turquoise-ochre-saddle-pattern-imagegen-v2.png |
| 123 | utahceratops-gettyi | 4 | medium | 0.6 | direct | 2/6 | color-pattern/social-growth-defense | no | no | utahceratops-gettyi-moss-rust-pattern-imagegen-v1.png<br>utahceratops-gettyi-postrain-channel-group-ecology-imagegen-v1.png |
| 124 | tarbosaurus-bataar | 1 | watch | 0.52 | direct | 1/3 | representative/habitat-ecology | no | no | tarbosaurus-bataar-narrow-skull-two-fingers-imagegen-v1.png<br>tarbosaurus-bataar-nemegt-ecology-imagegen-v1.png |
| 125 | otodus-megalodon | 1 | watch | 0.534 | direct | 2/3 | color-pattern/habitat-ecology | no | no | otodus-megalodon-rightfacing-slate-bronze-pattern-imagegen-v1.png<br>otodus-megalodon-neogene-whale-distance-ecology-imagegen-v1.png |
| 126 | diplodocus-carnegiei | 1 | watch | 0.519 | direct | 4/6 | identity-anatomy/social-growth-defense | no | no | diplodocus-carnegiei-twilight-mudflat-violet-mint-tailrings-ecology-imagegen-v1.png<br>diplodocus-carnegiei-separated-adult-juvenile-growth-imagegen-v1.png |
| 127 | riojasaurus-incertus | 4 | medium | 0.598 | mirrored | 2/6 | color-pattern/social-growth-defense | no | yes | riojasaurus-incertus-plum-petrol-celadon-pattern-imagegen-v1.png<br>riojasaurus-incertus-two-size-classes-separated-floodplain-ecology-imagegen-v1.png |
| 128 | utahceratops-gettyi | 4 | medium | 0.598 | mirrored | 2/5 | color-pattern/interaction | no | no | utahceratops-gettyi-moss-rust-pattern-imagegen-v1.png<br>utahceratops-gettyi-deep-notch-frill-rear-structure-imagegen-v1.png |
| 129 | eudimorphodon-ranzii | 3 | watch | 0.518 | mirrored | 1/2 | representative/color-pattern | no | no | eudimorphodon-ranzii-claret-seaglass-neutral-glide-representative-imagegen-v2.png<br>eudimorphodon-ranzii-seaglass-limestone-dawn-pattern-imagegen-v2.png |
| 130 | tarbosaurus-bataar | 1 | watch | 0.518 | direct | 3/4 | habitat-ecology/identity-anatomy | no | no | tarbosaurus-bataar-nemegt-ecology-imagegen-v1.png<br>tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png |
| 131 | goyocephale-lattimorei | 3 | watch | 0.518 | direct | 1/2 | representative/color-pattern | no | no | goyocephale-lattimorei-table-skull-gracile-representative-imagegen-v2.png<br>goyocephale-lattimorei-plum-lichen-bluehour-pattern-imagegen-v1.png |
| 132 | apatosaurus-ajax | 1 | watch | 0.517 | mirrored | 2/5 | color-pattern/interaction | no | no | apatosaurus-ajax-aubergine-olive-clouds-pattern-imagegen-v2.png<br>apatosaurus-ajax-distant-allosaurus-awareness-ecology-imagegen-v1.png |
| 133 | sauropelta-edwardsorum | 3 | medium | 0.596 | direct | 1/4 | representative/identity-anatomy | no | yes | sauropelta-edwardsorum-cloverly-shoulder-spine-nodosaurid-imagegen-v1.png<br>sauropelta-edwardsorum-shoulder-spine-anatomy-imagegen-v2.png |
| 134 | basilosaurus-isis | 2 | watch | 0.476 | direct | 1/2 | representative/color-pattern | no | no | basilosaurus-isis-longbody-tinyhindlimb-representative-imagegen-v1.png<br>basilosaurus-isis-ventral-ascent-petrol-pattern-imagegen-v1.png |
| 135 | therizinosaurus-cheloniformis | 1 | watch | 0.515 | mirrored | 4/5 | identity-anatomy/interaction | no | no | therizinosaurus-cheloniformis-straight-triclaw-fourtoe-anatomy-imagegen-v1.png<br>therizinosaurus-cheloniformis-bilateral-triclaw-tarbosaurus-watergap-ecology-imagegen-v4.png |
| 136 | tarbosaurus-bataar | 1 | watch | 0.515 | direct | 4/5 | identity-anatomy/interaction | no | no | tarbosaurus-bataar-shallow-channel-two-finger-walk-imagegen-v1.png<br>tarbosaurus-bataar-saurolophus-river-standoff-ecology-imagegen-v1.png |
| 137 | plesiosaurus-dolichodeirus | 2 | watch | 0.554 | direct | 1/3 | representative/habitat-ecology | no | no | plesiosaurus-dolichodeirus-longneck-sideprofile-imagegen-v1.png<br>plesiosaurus-dolichodeirus-fish-school-ecology-imagegen-v1.png |
| 138 | tarbosaurus-bataar | 1 | watch | 0.514 | direct | 2/6 | color-pattern/social-growth-defense | no | no | tarbosaurus-bataar-basalt-rust-pattern-imagegen-v1.png<br>tarbosaurus-bataar-adult-juvenile-riverbar-growth-ecology-imagegen-v1.png |
| 139 | camptosaurus-dispar | 3 | medium | 0.593 | direct | 2/5 | color-pattern/interaction | no | no | camptosaurus-dispar-teal-ochre-pattern-imagegen-v1.png<br>camptosaurus-dispar-allosaurus-thumb-brace-defense-ecology-imagegen-v1.png |
| 140 | gargoyleosaurus-parkpinorum | 4 | watch | 0.513 | direct | 1/2 | representative/color-pattern | no | no | gargoyleosaurus-parkpinorum-armored-no-club-imagegen-v1.png<br>gargoyleosaurus-parkpinorum-slate-ochre-pattern-imagegen-v1.png |
| 141 | kosmoceratops-richardsoni | 3 | medium | 0.59 | direct | 1/6 | representative/social-growth-defense | no | no | kosmoceratops-richardsoni-ornate-solid-frill-imagegen-v1.png<br>kosmoceratops-richardsoni-front-frill-anatomy-imagegen-v1.png |
| 142 | ichthyosaurus-communis | 2 | watch | 0.55 | mirrored | 4/6 | identity-anatomy/social-growth-defense | no | no | ichthyosaurus-communis-large-eye-tail-fin-identity-imagegen-v2.png<br>ichthyosaurus-communis-belemnite-fish-community-ecology-imagegen-v2.png |
| 143 | enigmacursor-mollyborthwickae | 4 | medium | 0.589 | direct | 2/4 | color-pattern/identity-anatomy | no | no | enigmacursor-mollyborthwickae-bluegray-copper-pattern-imagegen-v1.png<br>enigmacursor-mollyborthwickae-eye-mask-runner-identity-imagegen-v2.png |
| 144 | nasutoceratops-titusi | 2 | watch | 0.549 | direct | 1/5 | representative/interaction | no | no | nasutoceratops-titusi-hugenaris-twisted-browhorn-representative-imagegen-v1.png<br>nasutoceratops-titusi-gryposaurus-channel-separated-fauna-ecology-imagegen-v1.png |
| 145 | diplodocus-carnegiei | 1 | watch | 0.509 | mirrored | 2/5 | color-pattern/interaction | no | no | diplodocus-carnegiei-teal-saddle-pattern-imagegen-v1.png<br>diplodocus-carnegiei-distant-allosaurus-tail-posture-interaction-imagegen-v2.png |
| 146 | camarasaurus-lentus | 2 | watch | 0.469 | mirrored | 1/2 | representative/color-pattern | no | no | camarasaurus-lentus-morrison-box-skull-tubular-manus-representative-imagegen-v2.png<br>camarasaurus-lentus-aubergine-celadon-cloud-pattern-imagegen-v2.png |
| 147 | ankylosaurus-magniventris | 1 | watch | 0.508 | mirrored | 2/4 | color-pattern/identity-anatomy | no | no | ankylosaurus-magniventris-pointbar-petrol-lavender-russet-pattern-imagegen-v2.png<br>ankylosaurus-magniventris-broadskull-ventrolateral-naris-anatomy-imagegen-v2.png |
| 148 | spinosaurus-aegyptiacus | 1 | watch | 0.507 | mirrored | 2/6 | color-pattern/social-growth-defense | no | no | spinosaurus-aegyptiacus-rainflat-indigo-vermilion-turquoise-pattern-imagegen-v1.png<br>spinosaurus-aegyptiacus-sunrise-sail-display-ecology-imagegen-v1.png |
| 149 | megatherium-americanum | 2 | watch | 0.481 | mirrored | 1/2 | representative/color-pattern | no | no | megatherium-americanum-thick-tail-fourlimb-representative-imagegen-v2.png<br>megatherium-americanum-right-streambank-review-imagegen-v1.png |
| 150 | tyrannosaurus-rex | 1 | watch | 0.505 | direct | 1/5 | representative/interaction | no | no | tyrannosaurus-rex-hell-creek-deepskull-twofinger-representative-imagegen-v1.png<br>tyrannosaurus-rex-edmontosaurus-braided-river-distance-ecology-imagegen-v1.png |

## Gate

- Treat high similarity as a review signal, not proof of duplication; inspect original-size images before acting.
- A new candidate must materially change pose/action, camera family, spatial layout, subject count, or habitat; palette-only and mirror-only changes do not count.
- Keep candidates in the ignored local review queue until provenance and anatomy review are complete.
- Do not promote a representative from this report alone.
