import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"
OUTPUT_ROOT = ROOT / "tools" / "comfyui" / "outputs"

SOURCE = ASSET_ROOT / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
SOURCE_CROP = ASSET_ROOT / "velociraptor-small-sickle-crops-v9.png"
FOOT_GUIDE = ASSET_ROOT / "velociraptor-mongoliensis-foot-reference-guide-v1.png"
LARGE_CLAW_RISK = ASSET_ROOT / "velociraptor-mongoliensis-large-claw-risk-comparison-v9.png"
V1_RESULTS = OUTPUT_ROOT / "velociraptor_v9_foot_i2i_v1-results.json"
V2_RESULTS = OUTPUT_ROOT / "velociraptor_v9_foot_i2i_v2-results.json"

CONTACT_OUT = ASSET_ROOT / "velociraptor-review-options-v16.png"
CROP_OUT = ASSET_ROOT / "velociraptor-foot-i2i-v10-rejection-crops.png"


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
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


def load_rejections():
    by_key = {}
    for prefix, result_path in (
        ("velociraptor_v9_foot_i2i_v1", V1_RESULTS),
        ("velociraptor_v9_foot_i2i_v2", V2_RESULTS),
    ):
        for result in json.loads(result_path.read_text(encoding="utf-8")):
            key = (prefix, result["maskPreset"], result["seed"], result["denoise"])
            by_key[key] = copied_output(prefix, result)

    picks = [
        (
            by_key[("velociraptor_v9_foot_i2i_v1", "velociraptor_v9_feet_modest_sickle", 2026067401, 0.22)],
            "v1 full-foot mask: extra/metal claw risk",
            "Foot-area i2i creates sharper toe artifacts and does not improve the rear sickle gate.",
        ),
        (
            by_key[("velociraptor_v9_foot_i2i_v1", "velociraptor_v9_sickle_claw_tips", 2026067401, 0.30)],
            "v1 claw-tip mask: floating claw risk",
            "Tip-only i2i can detach the sickle cue into a floating crescent above the foot.",
        ),
        (
            by_key[("velociraptor_v9_foot_i2i_v2", "velociraptor_v9_front_hook_reduce_tight", 2026067403, 0.12)],
            "v2 tight hook-reduce: still oversized",
            "Tiny hook-reduction mask preserves the body but revives the oversized front hook.",
        ),
        (
            by_key[("velociraptor_v9_foot_i2i_v2", "velociraptor_v9_front_hook_reduce_tight", 2026067404, 0.18)],
            "v2 tight hook-reduce high denoise",
            "Higher denoise keeps the same failure mode and weakens the useful source foot read.",
        ),
    ]
    for path, _, _ in picks:
        if not path.exists():
            raise FileNotFoundError(path)
    return picks


def make_contact_sheet(rejections):
    items = [
        {
            "path": SOURCE,
            "title": "current v9: keep first",
            "note": "Still the best current compromise: body, tail, toothed snout, folded hands, and attached foot cue remain together.",
        },
        {
            "path": SOURCE_CROP,
            "title": "current v9 crop gate",
            "note": "Use as the reference gate for the current source foot and exact sickle-claw risk.",
        },
        {
            "path": LARGE_CLAW_RISK,
            "title": "existing large-claw risk",
            "note": "Prompt-only comparison showing why oversized hook-like claws must stay below the selected v9.",
        },
        {
            "path": FOOT_GUIDE,
            "title": "foot reference guide",
            "note": "Next route should use a stronger foot guide, ControlNet, or dromaeosaur LoRA rather than plain foot inpaint.",
        },
    ]
    items.extend({"path": path, "title": title, "note": note} for path, title, note in rejections)

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 66
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(Image.open(item["path"]), (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet(rejections):
    crops = [
        ("current v9 full body - keep first", SOURCE, (0, 0, 1672, 941)),
        ("current v9 front foot", SOURCE, (510, 620, 920, 920)),
        ("current v9 rear foot", SOURCE, (690, 590, 1080, 910)),
        ("current v9 feet pair", SOURCE, (500, 585, 1080, 930)),
    ]
    for path, title, _ in rejections:
        crops.extend(
            [
                (f"{title} full", path, (0, 0, 1672, 941)),
                (f"{title} front foot", path, (510, 620, 920, 920)),
                (f"{title} rear foot", path, (690, 590, 1080, 910)),
                (f"{title} feet pair", path, (500, 585, 1080, 930)),
            ]
        )
    crops.append(("foot reference guide", FOOT_GUIDE, (0, 0, 1536, 1024)))

    cols = 4
    thumb_w = 300
    thumb_h = 210
    label_h = 40
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (228, 224, 214))
    font = ImageFont.load_default()

    for idx, (label, path, box) in enumerate(crops):
        image = Image.open(path).convert("RGB").crop(box)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 7), label[:50], fill=(42, 39, 35), font=font)
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CROP_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CROP_OUT)


def main():
    for path in (SOURCE, SOURCE_CROP, FOOT_GUIDE, LARGE_CLAW_RISK, V1_RESULTS, V2_RESULTS):
        if not path.exists():
            raise FileNotFoundError(path)
    rejections = load_rejections()
    make_contact_sheet(rejections)
    make_crop_sheet(rejections)
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
