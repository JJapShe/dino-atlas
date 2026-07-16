import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SELECTED = ASSET_ROOT / "tyrannosaurus-rex-twofinger-hand-i2i-v4.png"
SOURCE_V3 = ASSET_ROOT / "tyrannosaurus-rex-smoothbrow-twofinger-imagegen-v3.png"
SOURCE_CROP = ASSET_ROOT / "tyrannosaurus-smoothbrow-twofinger-crops-v3.png"
CALMJAW = ASSET_ROOT / "tyrannosaurus-rex-calmjaw-twofinger-comparison-v3.png"
VISIBLEARMS = ASSET_ROOT / "tyrannosaurus-rex-visiblearms-comparison-v3.png"
PREVIOUS_V2 = ASSET_ROOT / "tyrannosaurus-rex-visible-twofinger-imagegen-v2.png"
RESULTS = OUTPUT_ROOT / "trex_v3_hand_i2i_v4-results.json"
HAND_CROPS = OUTPUT_ROOT / "trex_v3_hand_i2i_v4-hand-crops.png"

CONTACT_OUT = ASSET_ROOT / "tyrannosaurus-review-options-v7.png"
CROP_OUT = ASSET_ROOT / "tyrannosaurus-twofinger-hand-i2i-crops-v4.png"


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


def copied_output(prefix, result):
    return OUTPUT_ROOT / (
        f"{prefix}_{result['maskPreset']}_{result['taxonId']}_seed{result['seed']}_d{int(result['denoise'] * 100):02d}.png"
    )


def load_outputs():
    by_key = {}
    for result in json.loads(RESULTS.read_text(encoding="utf-8")):
        key = (result["maskPreset"], result["seed"], result["denoise"])
        path = copied_output("trex_v3_hand_i2i_v4", result)
        if not path.exists():
            raise FileNotFoundError(path)
        by_key[key] = path
    return by_key


def make_contact_sheet(outputs):
    tinyarms_d22 = outputs[("trex_v3_tinyarms_current", 2026067701, 0.22)]
    tight_d22 = outputs[("trex_v3_twofinger_hands_tight", 2026067702, 0.22)]
    items = [
        {
            "path": SELECTED,
            "title": "selected v4: hand i2i, compact two-finger cue",
            "note": "Promoted because it preserves v3 body/head/feet/tail while making the tiny hands read slightly cleaner.",
        },
        {
            "path": SOURCE_V3,
            "title": "source v3: strong body, softer hand crop",
            "note": "Still a strong T. rex body and head; demoted only because v4 gives a cleaner compact-hand cue.",
        },
        {
            "path": SOURCE_CROP,
            "title": "source v3 crop gate",
            "note": "Previous close-review gate for head, arms, feet, full tail, and v3/v2 hand risks.",
        },
        {
            "path": HAND_CROPS,
            "title": "v4 i2i hand comparison crops",
            "note": "Shows why low-denoise tiny-arm i2i was selected and higher-denoise/tight masks stayed below it.",
        },
        {
            "path": tinyarms_d22,
            "title": "review only: wider mask, higher denoise",
            "note": "Hand remains readable but body texture shifts more than the selected d0.14 pass.",
        },
        {
            "path": tight_d22,
            "title": "review only: tight hand mask",
            "note": "Preserves the body, but the hand shape is not cleaner enough to beat the selected wider low-denoise pass.",
        },
        {
            "path": CALMJAW,
            "title": "v3 calm-jaw comparison",
            "note": "Useful comparison, but the selected v4 keeps the stronger full-body gate.",
        },
        {
            "path": VISIBLEARMS,
            "title": "v3 visible-arms comparison",
            "note": "Arms are visible, but hand count and brow texture are less balanced than the selected v4.",
        },
        {
            "path": PREVIOUS_V2,
            "title": "previous v2 primary",
            "note": "Strong earlier hand cue, but the head and brow read are weaker than the current v4.",
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
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 30), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet(outputs):
    tinyarms_d22 = outputs[("trex_v3_tinyarms_current", 2026067701, 0.22)]
    tight_d22 = outputs[("trex_v3_twofinger_hands_tight", 2026067702, 0.22)]
    crops = [
        ("selected v4 full body", SELECTED, (0, 0, 1774, 887)),
        ("selected v4 massive head", SELECTED, (85, 135, 500, 380)),
        ("selected v4 tiny arms", SELECTED, (360, 320, 650, 650)),
        ("selected v4 two-finger hands", SELECTED, (420, 380, 620, 650)),
        ("selected v4 feet preserved", SELECTED, (630, 605, 1125, 820)),
        ("selected v4 tail preserved", SELECTED, (900, 300, 1774, 530)),
        ("source v3 full body", SOURCE_V3, (0, 0, 1774, 887)),
        ("source v3 hands", SOURCE_V3, (420, 380, 620, 650)),
        ("review: tinyarms d0.22 hands", tinyarms_d22, (420, 380, 620, 650)),
        ("review: tight d0.22 hands", tight_d22, (420, 380, 620, 650)),
        ("v3 calm-jaw hand risk", CALMJAW, (420, 350, 680, 625)),
        ("previous v2 hand / brow risk", PREVIOUS_V2, (1015, 185, 1525, 690)),
    ]

    cols = 3
    thumb_w = 340
    thumb_h = 220
    label_h = 38
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, (label, path, box) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 9), label[:52], fill=(43, 39, 34), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def main():
    required = (SELECTED, SOURCE_V3, SOURCE_CROP, CALMJAW, VISIBLEARMS, PREVIOUS_V2, RESULTS, HAND_CROPS)
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    outputs = load_outputs()
    make_contact_sheet(outputs)
    make_crop_sheet(outputs)
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
