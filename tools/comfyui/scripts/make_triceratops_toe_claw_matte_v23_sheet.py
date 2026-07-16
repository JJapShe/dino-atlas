import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSET_ROOT / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSET_ROOT / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V21_COMPARISON = ASSET_ROOT / "triceratops-horridus-allfeet-i2i-comparison-v21.png"
V20_CROPS = ASSET_ROOT / "triceratops-nonhoof-toes-lora-i2i-v20-crops.png"
MASK_SOURCE = OUTPUT_ROOT / "triceratops_toe_claw_matte_v23_custom_mask.png"
CONTACT_SOURCE = OUTPUT_ROOT / "triceratops_toe_claw_matte_v23-contact-sheet.png"
RESULTS_SOURCE = OUTPUT_ROOT / "triceratops_toe_claw_matte_v23-results.json"

SELECTED_LABEL = "seed 2026071121 d0.07"
SELECTED_SOURCE = OUTPUT_ROOT / "triceratops_toe_claw_matte_v23_custom_triceratops-horridus_seed2026071121_s04_d07.png"

COMPARISON_OUT = ASSET_ROOT / "triceratops-horridus-toe-claw-matte-i2i-v23.png"
MASK_OUT = ASSET_ROOT / "triceratops-toe-claw-highlight-i2i-mask-v23.png"
REVIEW_SHEET_OUT = ASSET_ROOT / "triceratops-toe-claw-matte-i2i-v23-review-sheet.png"
CROPS_OUT = ASSET_ROOT / "triceratops-toe-claw-matte-i2i-v23-crops.png"
FOOT_COMPARE_OUT = ASSET_ROOT / "triceratops-toe-claw-matte-i2i-v23-foot-compare.png"
REVIEW_OUT = REVIEW_ROOT / "trike_toe_claw_matte_i2i_v23_review.json"

FONT = ImageFont.load_default()


def fit(image, size):
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, max_chars=58, max_lines=2):
    x, y = xy
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 15), line, fill=(43, 39, 34), font=FONT)


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_outputs():
    data = json.loads(RESULTS_SOURCE.read_text(encoding="utf-8"))
    outputs = []
    for item in data:
        path = OUTPUT_ROOT / (
            "triceratops_toe_claw_matte_v23_custom_"
            f"triceratops-horridus_seed{item['seed']}_s04_d{int(item['denoise'] * 100):02d}.png"
        )
        outputs.append((f"seed {item['seed']} d{item['denoise']:.2f}", path))
    return outputs


def copy_assets():
    shutil.copyfile(SELECTED_SOURCE, COMPARISON_OUT)
    shutil.copyfile(MASK_SOURCE, MASK_OUT)


def make_review_sheet(outputs):
    items = [
        (
            CURRENT,
            "current v22: keep first unless v23 crops beat it",
            "Promoted all-feet weak-LoRA candidate; bright claw highlights remain the main foot risk.",
        ),
        (
            COMPARISON_OUT,
            "v23 toe-claw matte comparison",
            "Selected low-denoise claw-tip edit over v22; check if claws are less shiny without toe drift.",
        ),
        (
            CONTACT_SOURCE,
            "all v23 attempts",
            "Six tiny-mask probes over claw highlights only.",
        ),
        (
            MASK_OUT,
            "v23 claw-tip mask",
            "Tiny mask over bright claw highlights, not full toes.",
        ),
        (
            CURRENT_CROPS,
            "v21/v22 all-feet gate",
            "Baseline crop sheet for body, frill, tail, and all visible feet.",
        ),
        (
            V20_CROPS,
            "v20 foot-only comparison",
            "Previous weak-LoRA toe route; useful but not enough to replace the body gate.",
        ),
    ]
    for label, path in outputs:
        items.append((path, f"v23 {label}", "Check matte claw tips, separated non-hoofed toes, no body/head/frill regression."))

    cols = 3
    thumb_w, thumb_h, label_h = 430, 242, 74
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    for idx, (path, title, note) in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(path), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), title[:70], fill=(132, 61, 43), font=FONT)
        draw_wrapped(draw, (8, thumb_h + 31), note)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(REVIEW_SHEET_OUT)


def make_crop_sheet(outputs):
    crop_defs = [
        ("full body", (0, 75, 1672, 830), (390, 176)),
        ("head/frill/beak", (0, 190, 610, 580), (320, 190)),
        ("feet strip", (350, 675, 1255, 825), (430, 160)),
        ("front toes", (390, 705, 570, 805), (320, 178)),
        ("middle toes", (585, 705, 735, 805), (300, 178)),
        ("rear toes", (875, 690, 1210, 805), (360, 178)),
        ("tail/body", (780, 245, 1665, 630), (390, 170)),
    ]
    rows = [("v22 current", CURRENT), ("v21 no-LoRA all-feet", V21_COMPARISON)] + [
        (f"v23 {label}", path) for label, path in outputs
    ]
    rows.extend([("v22 crop audit", CURRENT_CROPS), ("v20 toe route", V20_CROPS)])

    cols = 2
    thumb_w, thumb_h, label_h = 430, 260, 38
    tiles = []
    for label, path in rows:
        if path in (CURRENT_CROPS, V20_CROPS):
            source = Image.open(path)
            tiles.append((label, path, (0, 0, source.width, min(source.height, 900)), (420, 250)))
            continue
        for title, box, size in crop_defs:
            tiles.append((f"{label} {title}", path, box, size))

    sheet_rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, sheet_rows * (thumb_h + label_h)), (232, 228, 218))
    for idx, (label, path, box, size) in enumerate(tiles):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, size), ((thumb_w - size[0]) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label[:68], fill=(43, 39, 34), font=FONT)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))
    sheet.save(CROPS_OUT)


def make_foot_compare_sheet():
    crop_defs = [
        ("feet strip", (350, 675, 1255, 825), (760, 148)),
        ("front toes", (390, 705, 570, 805), (360, 190)),
        ("middle toes", (585, 705, 735, 805), (320, 190)),
        ("rear toes", (875, 690, 1210, 805), (500, 190)),
    ]
    rows = [("v22 current", CURRENT), ("v23 matte toe-claw edit", COMPARISON_OUT)]
    label_h = 30
    gap = 12
    sheet_w = max(size[0] for _, _, size in crop_defs) + 220
    sheet_h = 40 + len(crop_defs) * (max(size[1] for _, _, size in crop_defs) * 2 + label_h * 2 + gap * 3)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (232, 228, 218))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (14, 12),
        "Triceratops v23 toe-claw matte check: compare only the masked claw highlights against v22",
        fill=(24, 24, 22),
        font=FONT,
    )

    y = 40
    for title, box, size in crop_defs:
        crop_h = size[1]
        draw.rectangle((0, y, sheet_w, y + crop_h * 2 + label_h * 2 + gap * 3), fill=(248, 247, 242))
        draw.text((14, y + 8), title, fill=(132, 61, 43), font=FONT)
        x = 190
        tile_y = y + 8
        for label, path in rows:
            crop = Image.open(path).convert("RGB").crop(box)
            draw.text((14, tile_y + 6), label, fill=(43, 39, 34), font=FONT)
            sheet.paste(fit(crop, size), (x, tile_y))
            tile_y += crop_h + label_h + gap
        y += crop_h * 2 + label_h * 2 + gap * 3

    sheet.save(FOOT_COMPARE_OUT)


def write_review(outputs):
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.write_text(
        json.dumps(
            {
                "taxonId": "triceratops-horridus",
                "experiment": "toe_claw_matte_i2i_v23",
                "sourceImage": relative(CURRENT),
                "maskImage": relative(MASK_OUT),
                "comparisonImage": relative(COMPARISON_OUT),
                "reviewSheet": relative(REVIEW_SHEET_OUT),
                "cropSheet": relative(CROPS_OUT),
                "footCompareSheet": relative(FOOT_COMPARE_OUT),
                "decision": "anatomy_review",
                "lora": "TriceratopsXL0_4.safetensors",
                "loraStrength": 0.04,
                "clipStrength": 0.03,
                "selectedLabel": SELECTED_LABEL,
                "editMode": "triceratops_matte_toe_claws",
                "outputs": [{"label": label, "image": relative(path)} for label, path in outputs],
                "reasons": [
                    "tiny claw-tip masking preserves the v22 low body, long tail, closed beak, three horns, skull-attached frill, and all-feet topology",
                    "the selected output slightly reduces shiny claw highlights but should remain a comparison until human crop review confirms it beats v22",
                    "future toe edits should stay tip-local and must not reopen the rhino body or mouth/teeth gates",
                ],
                "keepCurrentPrimaryUntilReview": relative(CURRENT),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in (CURRENT, CURRENT_CROPS, V21_COMPARISON, V20_CROPS, MASK_SOURCE, CONTACT_SOURCE, RESULTS_SOURCE, SELECTED_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)
    outputs = load_outputs()
    copy_assets()
    make_review_sheet(outputs)
    make_crop_sheet(outputs)
    make_foot_compare_sheet()
    write_review(outputs)
    print(COMPARISON_OUT)
    print(REVIEW_SHEET_OUT)
    print(CROPS_OUT)
    print(FOOT_COMPARE_OUT)
    print(REVIEW_OUT)


if __name__ == "__main__":
    main()
