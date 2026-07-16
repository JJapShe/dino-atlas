import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "ceratopsian_triceratops" / "review"

CURRENT = ASSETS / "triceratops-horridus-allfeet-lora-i2i-comparison-v22.png"
CURRENT_CROPS = ASSETS / "triceratops-allfeet-lora-i2i-v21-v22-crops.png"
V35 = ASSETS / "triceratops-horridus-imagegen-v35-source-candidate.png"
V37 = ASSETS / "triceratops-horridus-imagegen-v37-source-candidate.png"
V38 = ASSETS / "triceratops-horridus-imagegen-v38-source-candidate.png"
V39 = ASSETS / "triceratops-horridus-imagegen-v39-source-candidate.png"
GUIDE = ASSETS / "triceratops-horridus-skullfrill-bodylock-guide-v1.png"

REVIEW_SHEET = ASSETS / "triceratops-p5-v37-v39-review-sheet.png"
CROP_SHEET = ASSETS / "triceratops-p5-v37-v39-crops.png"
REVIEW_JSON = REVIEW_ROOT / "triceratops_p5_v37_v39_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def draw_wrapped(draw, xy, text, max_chars=58, max_lines=3):
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
    for idx, wrapped in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 15), wrapped, fill=(43, 39, 34), font=FONT)


def tile(path, title, note, size=(430, 242)):
    panel = Image.new("RGB", (size[0], size[1] + 82), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def fractional_crop(image, box):
    width, height = image.size
    left, top, right, bottom = box
    return image.crop((int(width * left), int(height * top), int(width * right), int(height * bottom)))


def make_review_sheet():
    items = [
        tile(CURRENT, "current v22 count-level pass", "Current first, but not final: useful horns/frill/feet with remaining rhino-body risk."),
        tile(V38, "v38 best P5 review hold", "Best new immediate Triceratops read with strong skull/frill, three horns, tail, and toes; torso still rounded."),
        tile(V39, "v39 secondary P5 hold", "Strong head/frill and long tail, but the body is more barrel-like and not promotion-safe."),
        tile(V37, "v37 secondary P5 hold", "Good tail and foot visibility with solid Triceratops identity; water scene and body volume are weaker."),
        tile(V35, "previous v35 P4 hold", "Earlier best prompt-only anti-rhino hold; kept for direct comparison against P5."),
        tile(GUIDE, "skull-frill body-lock guide", "Control target for skull-attached frill, three horns, closed beak, long tail, and anti-rhino body."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    REVIEW_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(REVIEW_SHEET)


def make_crop_sheet():
    rows = [
        ("current v22", CURRENT),
        ("v38 best P5 hold", V38),
        ("v39 secondary hold", V39),
        ("v37 secondary hold", V37),
        ("previous v35 hold", V35),
        ("body-lock guide", GUIDE),
        ("v22 existing crop gate", CURRENT_CROPS),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (430, 210)),
        ("head/frill/horns", (0.00, 0.08, 0.42, 0.62), (380, 210)),
        ("frill attachment", (0.14, 0.05, 0.42, 0.52), (330, 210)),
        ("body anti-rhino", (0.25, 0.16, 0.78, 0.78), (390, 210)),
        ("feet/toes", (0.10, 0.58, 0.72, 0.96), (390, 210)),
        ("tail length", (0.58, 0.28, 1.0, 0.72), (360, 210)),
    ]
    gap = 10
    label_h = 34
    col_w = 440
    row_h = 224
    sheet = Image.new(
        "RGB",
        (gap + len(crops) * (col_w + gap), gap + len(rows) * (row_h + label_h + gap)),
        (232, 228, 218),
    )
    for row_idx, (row_label, path) in enumerate(rows):
        image = Image.open(path).convert("RGB")
        y = gap + row_idx * (row_h + label_h + gap)
        if path == CURRENT_CROPS:
            sheet.paste(fit(image, (sheet.width - gap * 2, row_h + label_h)), (gap, y))
            continue
        for col_idx, (crop_label, box, size) in enumerate(crops):
            x = gap + col_idx * (col_w + gap)
            panel = Image.new("RGB", (col_w, row_h + label_h), (245, 243, 236))
            panel.paste(fit(fractional_crop(image, box), size), ((col_w - size[0]) // 2, 0))
            draw = ImageDraw.Draw(panel)
            draw.text((8, row_h + 8), f"{row_label}: {crop_label}"[:66], fill=(43, 39, 34), font=FONT)
            sheet.paste(panel, (x, y))
    sheet.save(CROP_SHEET)


def write_review_json():
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "triceratops-horridus",
                "experiment": "p5_v37_v39_antirhino_prompt_candidates",
                "currentPrimary": relative(CURRENT),
                "selectedReviewHold": relative(V38),
                "comparisonReviewHolds": [relative(V39), relative(V37), relative(V35)],
                "selectedRejectReferences": [],
                "reviewSheet": relative(REVIEW_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "keep_current_v22_with_v38_as_best_new_review_hold",
                "reason": (
                    "V38 is the best P5 review hold because it has the strongest immediate Triceratops read among the new candidates: skull-attached frill, exactly three facial horns, closed beak, long tail, and separated toes. "
                    "It still stays below promotion because the torso remains rounded/barrel-like and could still reinforce a mammal-body shortcut. V39 has strong head/frill identity but a heavier barrel body, while V37 keeps useful tail and toe visibility but the water scene and body volume are less atlas-clean. "
                    "Keep v22 first until a crop gate proves low elongated ceratopsian torso, closed beak, skull frill, long tail, and non-hoofed toes together."
                ),
                "nextRoute": (
                    "Use v38 as a prompt/style source hold for the next skull-frill body-lock i2i or ceratopsian LoRA branch, but keep it outside positive training. The next attempt should target lower torso volume and more dinosaur-like limb posture without losing the strong head/frill/horn identity."
                ),
                "rejectIfPromoting": [
                    "torso, shoulder mass, or feet read as rhinoceros-like",
                    "body is a round barrel rather than low elongated ceratopsian form",
                    "frill attaches to shoulders, back, or torso instead of skull",
                    "mouth opens or teeth appear",
                    "horn count is not exactly two brow horns plus one nasal horn",
                    "feet become hoof-like or hide toe separation",
                    "tail is cropped, hidden, or short",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    required = [CURRENT, CURRENT_CROPS, V35, V37, V38, V39, GUIDE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    make_review_sheet()
    make_crop_sheet()
    write_review_json()
    print(json.dumps({"reviewSheet": relative(REVIEW_SHEET), "cropSheet": relative(CROP_SHEET), "review": relative(REVIEW_JSON)}, indent=2))


if __name__ == "__main__":
    main()
