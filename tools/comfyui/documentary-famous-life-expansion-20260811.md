# Documentary-famous Paleozoic/Cenozoic expansion provenance

- Batch: `2026-08-11-documentary-famous-life-expansion-v1`
- Audience: Korean Dino Atlas users ages 5-14
- Taxa: 6
- Approved project assets: 18
- Representative S1 assets: 6
- Review/reference S2/S3 assets: 12
- Rejected or superseded attempts: 19
- Rejected source PNGs verified deleted: 19
- Rejected source pixels retained: 0

The JSON companion is canonical for exact revised prompts, call IDs, source lineage, seed availability, SHA-256 values, byte counts, PNG dimensions, source/licence boundaries, and review decisions. The app may reference only approved `assets/dinosaurs/...` paths; private `.codex/generated_images` paths are provenance-only.

## Approved records

| Record | Slot | Kind | Representative eligible | Dimensions | SHA-256 |
| --- | ---: | --- | --- | --- | --- |
| arthropleura-armata-representative-v1 | S1 | count-level pass | yes | 1672x941 | `5b27aff5f996...` |
| arthropleura-armata-pattern-v1 | S2 | review hold | no | 1122x1402 | `e47cef04443a...` |
| arthropleura-armata-ecology-v1 | S3 | anatomy review | no | 1672x941 | `eb2616ea9a9b...` |
| meganeura-monyi-representative-v1 | S1 | count-level pass | yes | 1672x941 | `8aa943748031...` |
| meganeura-monyi-samebody-pattern-v1 | S2 | review hold | no | 1672x941 | `dab058fa3446...` |
| meganeura-monyi-ecology-v1 | S3 | anatomy review | no | 1672x941 | `a8eb5eec83ef...` |
| inostrancevia-alexandri-representative-v1 | S1 | count-level pass | yes | 1672x941 | `49f4d56f0661...` |
| inostrancevia-alexandri-samebody-pattern-v1 | S2 | review hold | no | 1672x941 | `f3d2db1da54e...` |
| inostrancevia-alexandri-ecology-v1 | S3 | anatomy review | no | 1672x941 | `2d0a3c18e375...` |
| titanoboa-cerrejonensis-representative-v1 | S1 | count-level pass | yes | 1672x941 | `925b92b322f1...` |
| titanoboa-cerrejonensis-pattern-v1 | S2 | review hold | no | 1122x1402 | `b0f06525ae76...` |
| titanoboa-cerrejonensis-ecology-v1 | S3 | anatomy review | no | 1672x941 | `9bd2e587f59f...` |
| basilosaurus-isis-representative-v1 | S1 | count-level pass | yes | 1672x941 | `52d25a7be218...` |
| basilosaurus-isis-pattern-v1 | S2 | review hold | no | 1122x1402 | `1e3784b058e7...` |
| basilosaurus-isis-ecology-v1 | S3 | anatomy review | no | 1672x941 | `78eb6e444157...` |
| paraceratherium-transouralicum-representative-v1 | S1 | count-level pass | yes | 1672x941 | `20b9a91537da...` |
| paraceratherium-transouralicum-pattern-v1 | S2 | review hold | no | 1122x1402 | `d6ca231ba38c...` |
| paraceratherium-transouralicum-ecology-v1 | S3 | anatomy review | no | 1672x941 | `61ecd5736303...` |

S1 remains the basic full-body side or near-side identity view for every added taxon. Every S2 now satisfies the fixed same-body full-body color-pattern contract and remains review hold. Every S2/S3 is barred from representative promotion without a separate anatomy audit.

## Rights and evidence boundary

All accepted and rejected bitmaps were generated from original project prompts with OpenAI built-in image generation. No external artwork, documentary frame, published reconstruction, franchise frame, or named-artist style was supplied. Scientific papers and museum pages were used only for factual anatomy, occurrence, scale and uncertainty constraints. Colors, patterns, most soft tissue, exact poses and pictured moments remain reconstructions as detailed in the JSON evidence boundaries. Accepted private originals remain available for audit; rejected source pixels do not.

## Rejected attempts

Seventeen failed attempts were never copied into the project. Two cropped S2 structure references were briefly copied before the same-body contract review, then removed from runtime and superseded by full-body variants. Under the standing complete-reject policy, all nineteen rejected source PNGs were moved out of the private generation cache and are verified absent. Their exact prompts, call IDs, lineages, and pre-deletion SHA-256/byte/dimension facts remain. The deleted PNGs may be recoverable from the Windows Recycle Bin until it is emptied; after purge, the embedded metadata is the only retained evidence.

| Taxon | Intended role | Call ID | Pre-deletion SHA / dimensions | Rejection reason |
| --- | --- | --- | --- | --- |
| Arthropleura armata | S1 representative | `exec-e9d46802-2c2c-472c-aef0-fe71e3741efe` | `6c878f5e64cd...` / 1672x941 | Superseded after the 2024 head evidence review: the prompt and output used an obsolete plain rounded head/no-large-eye boundary and did not preserve the paired stalked-eye plus diplotergite two-successive-leg-pair gate required by the corrected S1 route. |
| Arthropleura armata | S2 color-pattern | `exec-970907d4-ea26-4f2c-878c-ef150165754c` | `2df03f704697...` / 1122x1402 | Inherited the rejected first S1's obsolete plain-head identity boundary, so it could not remain in the gallery after the stalked-eye and diplotergite correction. |
| Arthropleura armata | S3 habitat-ecology | `exec-09769592-eabd-4ffb-bd8f-2e96bbabb0ee` | `aace26d442ea...` / 1672x941 | Inherited the rejected first S1's obsolete head and trunk/leg identity boundary; broad ecology value did not override the focal-animal identity gate. |
| Meganeura monyi | S1 representative | `exec-9dc10616-169f-405c-91e3-76e7cdc43d9e` | `6447fe6dda1d...` / 1672x941 | Failed the original-size appendage gate: four independently connected wing roots and exactly six separately connected thoracic legs were not all reliably countable. |
| Meganeura monyi | S1 representative | `exec-48c4dad6-d5b8-4238-8614-0616929b31d2` | `2aa531366d4c...` / 1672x941 | The second whole-body attempt still did not make the required four wing attachments and six thoracic legs unambiguous at original size. |
| Meganeura monyi | S2 color-pattern | `exec-86d9ecf5-88c5-40d7-bdd3-933ff196f046` | `f7a876d4cc56...` / 1122x1402 | The low ventral flight attempt failed exact six-leg readability; overlapping or accessory leg-like forms made count-level use unsafe. |
| Meganeura monyi | S2 color-pattern | `exec-ac000020-80f6-4be9-8771-c4a137d86b4a` | `c02c587a3289...` / 1122x1402 | Original-size review found seven leg-like appendages rather than exactly six thoracic legs. |
| Meganeura monyi | S2 color-pattern repair | `exec-c7fabaa3-d3b8-4bb9-951f-518fa018b079` | `719f8ca16e01...` / 1122x1402 | The targeted seventh-leg repair still did not yield six fully separate, unambiguous thoracic legs without attachment/fusion uncertainty. |
| Meganeura monyi | S2 color-pattern | `exec-efe5d7d9-e81d-466d-a22b-fb9a3867e26b` | `fd346eb1fd86...` / 1122x1402 | The cropped dorsal close-up was useful for four wing-root structure and color only, but it showed no legs and omitted wing tips/body extent, so it violated the fixed same-body full-body S2 color-pattern contract. |
| Inostrancevia alexandri | S1 representative | `exec-08daa434-e18c-49a8-8a7a-00c903794523` | `26970f79262a...` / 1672x941 | The first side-profile attempt did not keep the saber pair, all four connected limbs/feet and complete tail sufficiently unambiguous for the count-level identity gate. |
| Inostrancevia alexandri | S2 color-pattern | `exec-7ed9e867-2522-48fe-9ded-c3db55a4d9fe` | `1b64c240e575...` / 1122x1402 | The rear three-quarter route did not make all four connected feet and their five-digit groups reliably readable; no color variant may bypass the limb/foot gate. |
| Inostrancevia alexandri | S2 color-pattern | `exec-603f66bd-f8ad-433d-81b0-658d447eba33` | `ba8dfe95da32...` / 1122x1402 | The elevated full-body attempt again failed the four separate pentadactyl-foot readability requirement through occlusion, fusion or uncertain toe counts. |
| Inostrancevia alexandri | S2 color-pattern | `exec-ea848bd8-b0c1-444b-941a-21f567a73ef7` | `66bb61819ab4...` / 1672x941 | Even with separated ground patches, all four five-toed feet were not simultaneously trustworthy at original size. |
| Inostrancevia alexandri | S2 color-pattern | `exec-094c6e07-7d24-4ae9-92ea-c996eb41382e` | `045a0df604f6...` / 1122x1402 | The cropped head-neck close-up was useful for color, texture and the upper saber pair only, but it contained no limbs, feet or full body, so it violated the fixed same-body full-body S2 color-pattern contract. |
| Titanoboa cerrejonensis | S1 representative | `exec-54a3dfb1-d26c-4695-8565-8d8e713ad5e6` | `b0f6556d5cc0...` / 1672x941 | The first bank-and-water route did not keep the entire head-to-tail body path continuously traceable through every bend at original size. |
| Titanoboa cerrejonensis | S3 habitat-ecology | `exec-4626d0c5-fafa-4c35-8f45-48a73c424557` | `37f475e35393...` / 1672x941 | The first ecology route did not keep both full snake-body continuity and distant non-contact turtle separation unambiguous enough for the ecology gate. |
| Basilosaurus isis | S1 representative | `exec-28f11e33-cab7-4f6b-89d7-09756265ecda` | `5c68f42bcf5b...` / 1672x941 | The otherwise useful first whole-body draft ended in a vertical fish-like caudal fin rather than a small horizontal archaeocete fluke. |
| Basilosaurus isis | S3 habitat-ecology | `exec-60680e54-90d0-49ef-9362-242d2b3b84de` | `5d3f80d33d71...` / 1672x941 | The first wide ecology draft repeated a caudal-fluke orientation/continuity error, so its fish-school composition could not override the tail anatomy gate. |
| Paraceratherium transouralicum | S2 color-pattern | `exec-8e0a9271-8d79-42ca-a776-4b50cf488a04` | `3d9d06b441bf...` / 1122x1402 | The rear three-quarter look-back route hid or fused a far limb/foot, producing an unreliable four-leg/four-foot read. |

## Deleted rejected-source paths

The builder requires every path below to remain absent and performs no deletion itself.

- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-e9d46802-2c2c-472c-aef0-fe71e3741efe.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-970907d4-ea26-4f2c-878c-ef150165754c.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-09769592-eabd-4ffb-bd8f-2e96bbabb0ee.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-9dc10616-169f-405c-91e3-76e7cdc43d9e.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-48c4dad6-d5b8-4238-8614-0616929b31d2.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-86d9ecf5-88c5-40d7-bdd3-933ff196f046.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-ac000020-80f6-4be9-8771-c4a137d86b4a.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-c7fabaa3-d3b8-4bb9-951f-518fa018b079.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-efe5d7d9-e81d-466d-a22b-fb9a3867e26b.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-08daa434-e18c-49a8-8a7a-00c903794523.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-7ed9e867-2522-48fe-9ded-c3db55a4d9fe.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-603f66bd-f8ad-433d-81b0-658d447eba33.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-ea848bd8-b0c1-444b-941a-21f567a73ef7.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-094c6e07-7d24-4ae9-92ea-c996eb41382e.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-54a3dfb1-d26c-4695-8565-8d8e713ad5e6.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-4626d0c5-fafa-4c35-8f45-48a73c424557.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-28f11e33-cab7-4f6b-89d7-09756265ecda.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-60680e54-90d0-49ef-9362-242d2b3b84de.png`
- `C:/Users/USER/.codex/generated_images/019fbda2-6313-7010-a45d-5c6c6e3f5169/exec-8e0a9271-8d79-42ca-a776-4b50cf488a04.png`

## Research sources

| Taxon | Source | Use |
| --- | --- | --- |
| arthropleura-armata | [Lheritier et al. 2024. The head of the largest arthropod, Arthropleura, and its phylogenetic significance. Science Advances 10:eadp6362.](https://doi.org/10.1126/sciadv.adp6362) | Head, stalked-eye, antenna and mixed centipede/millipede affinity constraints; adult A. armata head extrapolation remains explicit. |
| arthropleura-armata | [Natural History Museum. Largest-ever millipede head revealed.](https://www.nhm.ac.uk/discover/news/2024/october/largest-ever-millipede-head-revealed.html) | Museum cross-check for the newly described head and uncertainty boundary. |
| arthropleura-armata | [Natural History Museum. World's largest terrestrial arthropod was a car-sized millipede.](https://www.nhm.ac.uk/discover/news/2021/december/worlds-largest-terrestrial-arthropod-was-car-sized-millipede.html) | Size and Carboniferous terrestrial occurrence context. |
| meganeura-monyi | [Museum national d'Histoire naturelle. Meganeura monyi, libellule geante.](https://www.mnhn.fr/fr/meganeura-monyi-libellule-geante) | Museum-level identity, Commentry occurrence and giant wing-span context. |
| meganeura-monyi | [Wootton et al. 2024. Integrative and Comparative Biology 64(2):598-614.](https://academic.oup.com/icb/article/64/2/598/7687824) | Comparative griffinfly wing structure, venation and flight-boundary context. |
| inostrancevia-alexandri | Kammerer et al. 2023, Current Biology, and Ivakhnenko 2008, Paleontological Journal, as recorded in the Dino Atlas taxon source list. | Gorgonopsian skull, enlarged upper-canine pair, limb posture and extinction-interval context. |
| inostrancevia-alexandri | [Netflix Tudum. Life on Our Planet: What did prehistoric animals look like?](https://www.netflix.com/tudum/articles/life-on-our-planet-what-did-dinosaurs-look-like) | Documentary-audience exposure rationale only, not an anatomical authority. |
| titanoboa-cerrejonensis | [Head et al. 2009. Giant boid snake from the Palaeocene neotropics. Nature 457:715-717.](https://www.nature.com/articles/nature07671) | Vertebral evidence, giant size estimate and Paleocene Cerrejon setting. |
| titanoboa-cerrejonensis | [Smithsonian Institution. Titanoboa: Monster Snake.](https://www.si.edu/exhibitions/titanoboa-monster-snake-event-event-exhib-4820) | Museum-level public identity and documentary-recognition cross-check. |
| titanoboa-cerrejonensis | [Florida Museum. Titanoboa.](https://www.floridamuseum.ufl.edu/science/titanoboa/) | Cerrejon fossil and rainforest context cross-check. |
| basilosaurus-isis | [University of Michigan Museum of Paleontology. Basilosaurus isis.](https://lsa.umich.edu/paleontology/resources/beyond-exhibits/basilosaurus-isis.html) | Species-level archaeocete skeleton, elongate body and reduced hind-limb context. |
| basilosaurus-isis | [PBS NOVA. This massive skeleton belongs to an ancient whale.](https://www.pbs.org/video/this-massive-skeleton-belongs-to-an-ancient-whale-xta0ta/) | Documentary-audience exposure and broad ancient-whale identity context. |
| paraceratherium-transouralicum | [Deng et al. 2021. An Oligocene giant rhino provides insights into Paraceratherium evolution. Communications Biology 4:639.](https://www.nature.com/articles/s42003-021-02170-6) | Paraceratheriid relationships, giant hornless rhinocerotoid anatomy and distribution. |
| paraceratherium-transouralicum | [Natural History Museum. Why were prehistoric animals so big?](https://www.nhm.ac.uk/discover/why-were-dinosaurs-so-big.html) | Museum educational cross-check for Paraceratherium as a giant land mammal. |

## Rebuild and verification

Run with the bundled Node runtime:

```powershell
& 'C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' tools/comfyui/scripts/build_documentary_famous_life_manifest.mjs
```

The builder streams the current rollout log instead of loading its multi-gigabyte JSONL into memory. It requires exactly 37 completed image-generation events, preserves each event's exact `revised_prompt`, validates all retained accepted private PNGs, and refuses to write if any approved project copy differs from its generated original in SHA-256, byte count or dimensions. It also refuses to write while any rejected source PNG remains, validates complete coverage of the embedded pre-deletion facts, and attaches those facts to every deleted rejected input-reference lineage.
