from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SELECTED = ASSET_ROOT / "brachiosaurus-altithorax-tail-reduced-i2i-v4.png"
SOURCE_V3 = ASSET_ROOT / "brachiosaurus-altithorax-highshoulder-shorttail-imagegen-v3.png"
TALL_FORELIMB_V3 = ASSET_ROOT / "brachiosaurus-altithorax-tallforelimb-shorttail-imagegen-v3.png"
PREVIOUS_V2 = ASSET_ROOT / "brachiosaurus-altithorax-balancedneck-imagegen-v2.png"
PROMPT_RETRY_SHEET = OUTPUT_ROOT / "brachiosaurus_shorttail_seed_v1-contact-sheet.png"
V1_CROP_SHEET = OUTPUT_ROOT / "brachiosaurus_v3_tail_reduce_i2i_v1_v2-crops.png"
V2_BLUNT_REJECT = (
    OUTPUT_ROOT
    / "brachiosaurus_v3_tail_reduce_i2i_v2_brachiosaurus_v3_tail_half_reduce_brachiosaurus-altithorax_seed2026067507_d46.png"
)
V2_HIGH_DENOISE_REVIEW = (
    OUTPUT_ROOT
    / "brachiosaurus_v3_tail_reduce_i2i_v2_brachiosaurus_v3_tail_half_reduce_brachiosaurus-altithorax_seed2026067508_d62.png"
)

CONTACT_OUT = ASSET_ROOT / "brachiosaurus-review-options-v7.png"
CROP_OUT = ASSET_ROOT / "brachiosaurus-tail-reduced-i2i-crops-v4.png"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (236, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, font, fill, max_chars=58, line_h=15, max_lines=2):
    x, y = xy
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    for idx, line in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * line_h), line, fill=fill, font=font)


def make_contact_sheet():
    items = [
        {
            "path": SELECTED,
            "title": "selected v4: tail-reduced i2i",
            "note": "Best tail refinement: preserves high shoulders, taller forelimbs, neck, feet, and a less whip-like tail.",
        },
        {
            "path": SOURCE_V3,
            "title": "source v3: strong body, long-tail risk",
            "note": "Good Brachiosaurus body plan, but the tail reads too long and thin for the current first image.",
        },
        {
            "path": V2_BLUNT_REJECT,
            "title": "reject: shortened but blunt tail end",
            "note": "Body survives, but the tail tip becomes too club-like and less natural than the selected v4.",
        },
        {
            "path": V2_HIGH_DENOISE_REVIEW,
            "title": "review only: higher-denoise tail pass",
            "note": "Useful comparison, but the hip/tail blend shifts more than the selected low-denoise pass.",
        },
        {
            "path": TALL_FORELIMB_V3,
            "title": "v3 tall-forelimb comparison",
            "note": "Similar body identity, kept below selected v4 because foot/tail edge review is weaker.",
        },
        {
            "path": PROMPT_RETRY_SHEET,
            "title": "diagnostic: prompt-only short-tail retry",
            "note": "Shorter-tail prompts broke body orientation, legs, or shoulder identity too often for promotion.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 242
    label_h = 72
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image = Image.open(item["path"])
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 30), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v4 full body", SELECTED, (0, 0, 1570, 1002)),
        ("selected v4 tail full", SELECTED, (780, 470, 1570, 850)),
        ("selected v4 hip / tail base", SELECTED, (770, 440, 1270, 800)),
        ("selected v4 feet / body preserved", SELECTED, (440, 690, 1190, 990)),
        ("source v3 full body", SOURCE_V3, (0, 0, 1570, 1002)),
        ("source v3 longer tail risk", SOURCE_V3, (780, 470, 1570, 850)),
        ("reject: blunt tail end", V2_BLUNT_REJECT, (780, 470, 1570, 850)),
        ("higher denoise tail review", V2_HIGH_DENOISE_REVIEW, (780, 470, 1570, 850)),
        ("previous v2 full body", PREVIOUS_V2, (0, 0, 1692, 929)),
        ("v1/v2 tail audit overview", V1_CROP_SHEET, (0, 2450, 2260, 3600)),
    ]

    cols = 2
    thumb_w = 390
    thumb_h = 236
    label_h = 36
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (label, path, box) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 10), label, fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def main():
    required = (
        SELECTED,
        SOURCE_V3,
        TALL_FORELIMB_V3,
        PREVIOUS_V2,
        PROMPT_RETRY_SHEET,
        V1_CROP_SHEET,
        V2_BLUNT_REJECT,
        V2_HIGH_DENOISE_REVIEW,
    )
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
