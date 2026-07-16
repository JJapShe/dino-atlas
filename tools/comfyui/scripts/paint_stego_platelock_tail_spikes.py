import argparse
from pathlib import Path

import paint_stego_plategate_tail_spikes as tail_painter


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
DEFAULT_SOURCE = ASSET_ROOT / "stegosaurus-stenops-plate-lock-ipcontrol-v1.png"
DEFAULT_OUT_DIR = ROOT / "tools" / "comfyui" / "outputs"


# Coordinates are tuned for the plate-lock Stegosaurus candidate. The earlier
# plate-gate tail overlay was too faint on this darker tail, so these variants
# use wider bases and slightly longer diagonals while staying inside frame.
VARIANTS = {
    "v1a": {
        "hub": [(1088, 358), (1118, 356), (1130, 366), (1117, 382), (1086, 380), (1075, 366)],
        "spikes": [
            ((1100, 354), (1116, 360), (1144, 318)),
            ((1118, 360), (1130, 367), (1150, 344)),
            ((1098, 376), (1114, 383), (1140, 424)),
            ((1116, 374), (1129, 381), (1150, 402)),
        ],
        "opacity": 1.0,
        "blur": 0.16,
        "seed": 2026062277,
    },
    "v1b": {
        "hub": [(1089, 360), (1116, 358), (1127, 367), (1116, 380), (1089, 378), (1079, 367)],
        "spikes": [
            ((1102, 357), (1116, 362), (1138, 326)),
            ((1117, 363), (1128, 369), (1148, 350)),
            ((1101, 374), (1115, 380), (1136, 416)),
            ((1117, 373), (1129, 379), (1148, 396)),
        ],
        "opacity": 0.96,
        "blur": 0.22,
        "seed": 2026062278,
    },
    "v1c": {
        "hub": [(1091, 361), (1114, 360), (1124, 368), (1114, 378), (1091, 377), (1082, 368)],
        "spikes": [
            ((1102, 358), (1114, 363), (1132, 332)),
            ((1116, 364), (1126, 369), (1144, 354)),
            ((1102, 373), (1114, 378), (1131, 408)),
            ((1116, 373), (1126, 378), (1144, 392)),
        ],
        "opacity": 0.9,
        "blur": 0.30,
        "seed": 2026062279,
    },
    "v2a": {
        "hub": [(1082, 356), (1118, 354), (1134, 367), (1118, 386), (1082, 383), (1068, 366)],
        "spikes": [
            ((1096, 353), (1116, 360), (1148, 306)),
            ((1118, 361), (1134, 369), (1150, 334)),
            ((1096, 380), (1116, 388), (1146, 436)),
            ((1118, 378), (1135, 386), (1150, 412)),
        ],
        "opacity": 1.0,
        "blur": 0.12,
        "seed": 2026062280,
    },
    "v2b": {
        "hub": [(1085, 358), (1119, 356), (1132, 367), (1119, 383), (1085, 381), (1072, 367)],
        "spikes": [
            ((1098, 355), (1117, 361), (1144, 316)),
            ((1118, 362), (1132, 369), (1150, 340)),
            ((1098, 377), (1117, 385), (1142, 426)),
            ((1118, 376), (1133, 383), (1150, 405)),
        ],
        "opacity": 0.98,
        "blur": 0.18,
        "seed": 2026062281,
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--prefix", default="stego_platelock_tailspike_guide_v1")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    tail_painter.VARIANTS = VARIANTS
    items = [(source, "source: plate-lock candidate")]
    for variant_name in VARIANTS:
        output = out_dir / f"{args.prefix}_{variant_name}.png"
        mask_output = out_dir / f"{args.prefix}_{variant_name}-mask.png"
        tail_painter.draw_variant(source, output, mask_output, variant_name)
        items.append((output, f"plate-lock thagomizer guide {variant_name}"))
        print(output)
        print(mask_output)

    sheet = out_dir / f"{args.prefix}-contact-sheet.png"
    crop_sheet = out_dir / f"{args.prefix}-tail-crops.png"
    tail_painter.make_contact_sheet(items, sheet, crop_sheet)
    print(sheet)
    print(crop_sheet)


if __name__ == "__main__":
    main()
