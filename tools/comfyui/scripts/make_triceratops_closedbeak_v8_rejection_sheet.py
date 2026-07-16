from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "assets" / "dinosaurs"

SELECTED = ASSET_ROOT / "triceratops-horridus-lowbody-toe-frame-imagegen-v7.png"
SELECTED_CROP = ASSET_ROOT / "triceratops-lowbody-toe-frame-crops-v7.png"
CLOSEDBEAK_V7 = ASSET_ROOT / "triceratops-horridus-closedbeak-body-comparison-v7.png"
V8_LONGBODY = ASSET_ROOT / "triceratops-horridus-closedbeak-longbody-imagegen-v8.png"
V8_TOE = ASSET_ROOT / "triceratops-horridus-closedbeak-toe-comparison-v8.png"
V8_HEAVY = ASSET_ROOT / "triceratops-horridus-heavybody-closedbeak-comparison-v8.png"
V8_LOWLONG = ASSET_ROOT / "triceratops-horridus-lowlong-closedbeak-bodyrisk-v8.png"
V8_RHINO = ASSET_ROOT / "triceratops-horridus-closedbeak-rhinorisk-comparison-v8.png"
PREVIOUS = ASSET_ROOT / "triceratops-horridus-closedbeak-toegate-imagegen-v6.png"
RHINO_REJECTION = ASSET_ROOT / "triceratops-horridus-natural-lora-inpaint-v2.png"

CONTACT_OUT = ASSET_ROOT / "triceratops-review-options-v14.png"
CROP_OUT = ASSET_ROOT / "triceratops-closedbeak-v8-rejection-crops.png"


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


def fit(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def make_contact_sheet():
    items = [
        {
            "path": SELECTED,
            "title": "selected v7: keep first",
            "note": "Best current low long ceratopsian body, long tail, three horns, frill, and non-hoofed toe read.",
        },
        {
            "path": CLOSEDBEAK_V7,
            "title": "v7 closed-beak comparison",
            "note": "Useful beak comparison, but the selected v7 keeps a better low/long body and toe frame.",
        },
        {
            "path": V8_LONGBODY,
            "title": "v8 closed-beak longbody rejection",
            "note": "Closed beak improves, but the torso becomes too high/round and mammal-like.",
        },
        {
            "path": V8_TOE,
            "title": "v8 closed-beak toe comparison rejection",
            "note": "Feet and beak are useful, but head/body mass drifts away from the selected low-body gate.",
        },
        {
            "path": V8_HEAVY,
            "title": "v8 heavy-body closed-beak rejection",
            "note": "Clear closed beak, but the body becomes too bulky and rhino-like for promotion.",
        },
        {
            "path": V8_LOWLONG,
            "title": "v8 low-long prompt body-risk rejection",
            "note": "Second-round prompt still returns a high rounded body, so keep it diagnostic only.",
        },
        {
            "path": V8_RHINO,
            "title": "v8 rhino-risk closed-beak rejection",
            "note": "Useful as a failure gate: closed beak cannot outweigh mammal-like body mass.",
        },
        {
            "path": PREVIOUS,
            "title": "previous v6 closed-beak gate",
            "note": "Cleaner beak gate retained below v7; body and tail remain less convincing than selected v7.",
        },
        {
            "path": RHINO_REJECTION,
            "title": "old rhino-drift rejection",
            "note": "Baseline failure reference for mammal torso, hoof-like feet, and weak dinosaur tail.",
        },
    ]

    cols = 3
    thumb_w = 430
    thumb_h = 286
    label_h = 66
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (232, 228, 218))
    font = ImageFont.load_default()

    for idx, item in enumerate(items):
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), (245, 243, 236))
        image = Image.open(item["path"])
        tile.paste(fit(image, (thumb_w, thumb_h)), (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, thumb_h + 8), item["title"][:70], fill=(132, 61, 43), font=font)
        draw_wrapped(draw, (8, thumb_h + 28), item["note"], font, (43, 39, 34))
        sheet.paste(tile, ((idx % cols) * thumb_w, (idx // cols) * (thumb_h + label_h)))

    CONTACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_OUT)


def make_crop_sheet():
    crops = [
        ("selected v7 full body - keep first", SELECTED, (0, 0, 1672, 941)),
        ("selected v7 beak / frill", SELECTED, (55, 130, 690, 575)),
        ("selected v7 feet / low body", SELECTED, (260, 520, 1320, 895)),
        ("v8 longbody closed beak", V8_LONGBODY, (0, 0, 1672, 941)),
        ("v8 longbody beak closeup", V8_LONGBODY, (80, 235, 520, 570)),
        ("v8 longbody feet/body risk", V8_LONGBODY, (300, 525, 1220, 910)),
        ("v8 toe comparison full body", V8_TOE, (0, 0, 1672, 941)),
        ("v8 heavy-body full body", V8_HEAVY, (0, 0, 1672, 941)),
        ("v8 lowlong body-risk full body", V8_LOWLONG, (0, 0, 1672, 941)),
        ("v8 rhino-risk full body", V8_RHINO, (0, 0, 1672, 941)),
        ("previous v7 crop audit", SELECTED_CROP, (0, 0, 760, 858)),
        ("old rhino-drift rejection", RHINO_REJECTION, (0, 0, 1536, 1024)),
    ]

    cols = 2
    thumb_w = 380
    thumb_h = 250
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
    for path in (
        SELECTED,
        SELECTED_CROP,
        CLOSEDBEAK_V7,
        V8_LONGBODY,
        V8_TOE,
        V8_HEAVY,
        V8_LOWLONG,
        V8_RHINO,
        PREVIOUS,
        RHINO_REJECTION,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    make_contact_sheet()
    make_crop_sheet()
    print(CONTACT_OUT)
    print(CROP_OUT)


if __name__ == "__main__":
    main()
