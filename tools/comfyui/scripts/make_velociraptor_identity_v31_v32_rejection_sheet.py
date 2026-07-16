import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
OUTPUTS = ROOT / "tools" / "comfyui" / "outputs"
REVIEW_ROOT = ROOT / "tools" / "comfyui" / "lora_training" / "dromaeosaur_feathered" / "review"

CURRENT = ASSETS / "velociraptor-mongoliensis-small-sickle-imagegen-v9.png"
CURRENT_CROPS = ASSETS / "velociraptor-small-sickle-crops-v9.png"
BODYLOCK_GUIDE = ASSETS / "velociraptor-mongoliensis-identity-bodylock-guide-clean-v1.png"
FOOT_GUIDE = ASSETS / "velociraptor-mongoliensis-foot-topology-guide-v1.png"
V30_CROPS = ASSETS / "velociraptor-second-toe-i2i-v30-crops.png"
V31_CONTACT = OUTPUTS / "velociraptor_identity_bodylock_v31-contact-sheet.png"
V31_RESULTS = OUTPUTS / "velociraptor_identity_bodylock_v31-results.json"
V32_CONTACT = OUTPUTS / "velociraptor_headfoot_lowdenoise_v32-contact-sheet.png"
V32_RESULTS = OUTPUTS / "velociraptor_headfoot_lowdenoise_v32-results.json"

V31_SAMPLE = OUTPUTS / "velociraptor_identity_bodylock_v31_style_transfer_velociraptor-mongoliensis_seed2026070131_iw24_cs24.png"
V32_SAMPLE = OUTPUTS / "velociraptor_headfoot_lowdenoise_v32_identity_bodylock_head_foot_01_seed2026070141_d18.png"

REJECTION_SHEET = ASSETS / "velociraptor-identity-v31-v32-rejection-sheet.png"
CROP_SHEET = ASSETS / "velociraptor-identity-v31-v32-rejection-crops.png"
REVIEW_JSON = REVIEW_ROOT / "velociraptor_identity_v31_v32_review.json"

FONT = ImageFont.load_default()


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def maybe_relative(path_text):
    path = Path(path_text)
    try:
        return relative(path)
    except ValueError:
        return path_text


def fit(image, size):
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (245, 243, 236))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
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
    for idx, wrapped in enumerate(lines[:max_lines]):
        draw.text((x, y + idx * 15), wrapped, fill=(43, 39, 34), font=FONT)


def tile(path, title, note, size=(430, 242)):
    panel = Image.new("RGB", (size[0], size[1] + 74), (245, 243, 236))
    panel.paste(fit(Image.open(path), size), (0, 0))
    draw = ImageDraw.Draw(panel)
    draw.text((8, size[1] + 8), title[:70], fill=(132, 61, 43), font=FONT)
    draw_wrapped(draw, (8, size[1] + 31), note)
    return panel


def fractional_crop(image, box):
    w, h = image.size
    left, top, right, bottom = box
    return image.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))


def make_rejection_sheet():
    items = [
        tile(CURRENT, "current v9: keep first", "Still the best balance of toothed snout, feathers, long tail, and modest sickle cue."),
        tile(CURRENT_CROPS, "current v9 crop gate", "Use these crops for head, hands, front/rear feet, and sickle-claw review."),
        tile(BODYLOCK_GUIDE, "clean identity body-lock guide", "Useful control reference, but direct IP-Control from it still strips feather identity."),
        tile(V31_CONTACT, "v31 body-lock IP-Control rejection", "Reject: stronger body-lock creates scaly generic theropods and weak foot evidence."),
        tile(V32_CONTACT, "v32 low-denoise i2i rejection", "Reject: preserves more of v9, but shrinks foot evidence and does not improve the head/foot gate."),
        tile(V30_CROPS, "previous v30 toe-topology failure", "Foot-only local i2i also failed to prove attached raised second-toe anatomy."),
    ]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * items[0].width, rows * items[0].height), (232, 228, 218))
    for idx, item in enumerate(items):
        sheet.paste(item, ((idx % cols) * item.width, (idx // cols) * item.height))
    sheet.save(REJECTION_SHEET)


def make_crop_sheet():
    rows = [
        ("current v9", CURRENT),
        ("v31 sample", V31_SAMPLE),
        ("v32 sample", V32_SAMPLE),
    ]
    crops = [
        ("full body", (0.0, 0.05, 1.0, 0.92), (420, 210)),
        ("head snout", (0.0, 0.08, 0.30, 0.42), (310, 210)),
        ("forelimbs", (0.12, 0.28, 0.44, 0.64), (310, 210)),
        ("near foot", (0.30, 0.55, 0.58, 0.96), (280, 210)),
        ("rear foot", (0.38, 0.55, 0.72, 0.98), (300, 210)),
    ]
    gap = 10
    label_h = 34
    col_w = 430
    row_h = 224
    sheet = Image.new("RGB", (gap + len(crops) * (col_w + gap), gap + len(rows) * (row_h + label_h + gap)), (232, 228, 218))
    for row_idx, (row_label, path) in enumerate(rows):
        image = Image.open(path).convert("RGB")
        y = gap + row_idx * (row_h + label_h + gap)
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
    v31_results = json.loads(V31_RESULTS.read_text(encoding="utf-8"))
    v32_results = json.loads(V32_RESULTS.read_text(encoding="utf-8"))
    REVIEW_JSON.write_text(
        json.dumps(
            {
                "taxonId": "velociraptor-mongoliensis",
                "experiment": "identity_bodylock_v31_v32",
                "currentPrimary": relative(CURRENT),
                "bodylockGuide": relative(BODYLOCK_GUIDE),
                "footGuide": relative(FOOT_GUIDE),
                "rejectionSheet": relative(REJECTION_SHEET),
                "cropSheet": relative(CROP_SHEET),
                "decision": "diagnostic_only",
                "routeSummary": [
                    "v31 used current v9 as style reference with clean identity body-lock line control; it lost feathered dromaeosaur identity and became scaly generic theropod-like",
                    "v32 used low-denoise i2i over current v9 with head/foot prompt pressure; it preserved the body better than v31 but did not improve attached second-toe sickle-claw proof",
                    "current v9 remains first; next useful route should use a curated dromaeosaur/foot mini-LoRA or multi-control workflow that locks foot topology without erasing plumage",
                ],
                "keepCurrentPrimary": relative(CURRENT),
                "rejectCriteriaConfirmed": [
                    "naked or scaly movie-raptor body",
                    "modern bird or generic theropod head drift",
                    "feet without visible attached raised second-toe sickle-claw proof",
                ],
                "v31Outputs": [
                    {
                        "seed": item["seed"],
                        "ipWeight": item["ipWeight"],
                        "controlStrength": item["controlStrength"],
                        "image": maybe_relative(item["image"]),
                    }
                    for item in v31_results
                ],
                "v32Outputs": [
                    {
                        "seed": item["seed"],
                        "denoise": item["denoise"],
                        "image": maybe_relative(item["image"]),
                    }
                    for item in v32_results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    for path in [
        CURRENT,
        CURRENT_CROPS,
        BODYLOCK_GUIDE,
        FOOT_GUIDE,
        V30_CROPS,
        V31_CONTACT,
        V31_RESULTS,
        V31_SAMPLE,
        V32_CONTACT,
        V32_RESULTS,
        V32_SAMPLE,
    ]:
        if not path.exists():
            raise FileNotFoundError(path)
    make_rejection_sheet()
    make_crop_sheet()
    write_review_json()
    print(REJECTION_SHEET)
    print(CROP_SHEET)
    print(REVIEW_JSON)


if __name__ == "__main__":
    main()
