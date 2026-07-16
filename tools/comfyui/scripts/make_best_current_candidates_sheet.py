import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "tools" / "comfyui" / "outputs" / "app-gallery-samples.json"
OUT = ROOT / "assets" / "dinosaurs" / "best-current-candidates-v2-priority-sheet.png"


TAXON_LABELS = {
    "herrerasaurus-ischigualastensis": "Herrerasaurus",
    "coelophysis-bauri": "Coelophysis",
    "plateosaurus-engelhardti": "Plateosaurus",
    "allosaurus-fragilis": "Allosaurus",
    "apatosaurus-ajax": "Apatosaurus",
    "tyrannosaurus-rex": "Tyrannosaurus rex",
    "triceratops-horridus": "Triceratops",
    "stegosaurus-stenops": "Stegosaurus",
    "velociraptor-mongoliensis": "Velociraptor",
    "brachiosaurus-altithorax": "Brachiosaurus",
    "ankylosaurus-magniventris": "Ankylosaurus",
}


NOTES = {
    "herrerasaurus-ischigualastensis": "compact hands; fingers/toes pending",
    "coelophysis-bauri": "slender neck; fingers/toes pending",
    "plateosaurus-engelhardti": "safer limb count; hand anatomy pending",
    "allosaurus-fragilis": "smoother brow; fingers/toes pending",
    "apatosaurus-ajax": "small head; four open feet",
    "tyrannosaurus-rex": "hand refined; two-finger review pending",
    "triceratops-horridus": "low body; toes; beak closure pending",
    "stegosaurus-stenops": "alternating plates; spike count pending",
    "velociraptor-mongoliensis": "smaller sickle claws; toes pending",
    "brachiosaurus-altithorax": "high shoulders; tail refined; feet pending",
    "ankylosaurus-magniventris": "broad skull; single club; toes pending",
}


PRIORITIES = {
    "velociraptor-mongoliensis": ("P0", "bird-head and sickle-toe proof still weak"),
    "stegosaurus-stenops": ("P0", "plate topology and four-spike proof must align"),
    "plateosaurus-engelhardti": ("P1", "far forelimb and thumb-claw cue remain hidden"),
    "triceratops-horridus": ("P1", "toe/beak gate needs final crop approval"),
    "ankylosaurus-magniventris": ("P1", "skull breadth and non-lizard body need crop approval"),
    "herrerasaurus-ischigualastensis": ("P2", "compact hand digit topology still pending"),
    "coelophysis-bauri": ("P2", "tiny hands and rear feet need close crop proof"),
    "allosaurus-fragilis": ("P2", "three-finger hands still need crop proof"),
    "tyrannosaurus-rex": ("P2", "two-finger hand cue still needs crop proof"),
    "apatosaurus-ajax": ("P3", "feet and skull proportions are count-level"),
    "brachiosaurus-altithorax": ("P3", "feet and skull details are count-level"),
}


NEXT_ROUTES = {
    "velociraptor-mongoliensis": "dromaeosaur LoRA or multi-control head+foot route",
    "stegosaurus-stenops": "plate-topology LoRA/control with v6 body lock",
    "plateosaurus-engelhardti": "small hand/thumb mask plus no-six-leg body lock",
    "triceratops-horridus": "tip-local toe matte, keep anti-rhino body locked",
    "ankylosaurus-magniventris": "body-lock skull/feet crop route, avoid lizard drift",
    "herrerasaurus-ischigualastensis": "compact-hand micro route with digit crop gate",
    "coelophysis-bauri": "forelimb/feet crop route, keep slender S-neck",
    "allosaurus-fragilis": "hand micro route, preserve medium Allosaurus arms",
    "tyrannosaurus-rex": "two-finger hand micro route, preserve tiny arms",
    "apatosaurus-ajax": "feet crop route, preserve low neck and small head",
    "brachiosaurus-altithorax": "feet/head crop route, preserve high shoulders",
}


PRIORITY_COLORS = {
    "P0": (154, 55, 52),
    "P1": (166, 95, 42),
    "P2": (145, 112, 45),
    "P3": (58, 116, 82),
}


TAXON_ORDER = list(TAXON_LABELS)
KIND_COLORS = {
    "count-level pass": (43, 105, 78),
    "primary generated": (135, 82, 45),
    "primary structure reference": (57, 91, 139),
    "anatomy review": (145, 93, 48),
    "diagnostic only": (145, 64, 58),
}

DISPLAY_RANK = {
    "count-level pass": 0,
    "primary generated": 1,
    "anatomy review": 2,
    "primary structure reference": 3,
    "structure reference": 4,
    "diagnostic only": 5,
}


def draw_wrapped(draw, xy, text, font, fill, max_chars=42, line_h=16, max_lines=2):
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


def fit_image(image, size):
    target_w, target_h = size
    image = image.convert("RGB")
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (235, 232, 224))
    canvas.paste(image, ((target_w - image.width) // 2, (target_h - image.height) // 2))
    return canvas


def make_tile(taxon_id, item, size, font):
    tile_w, image_h, label_h = size
    tile = Image.new("RGB", (tile_w, image_h + label_h), (245, 243, 236))
    image_path = ROOT / item["src"]
    if image_path.exists():
        tile.paste(fit_image(Image.open(image_path), (tile_w, image_h)), (0, 0))

    draw = ImageDraw.Draw(tile)
    status_color = KIND_COLORS.get(item.get("kind"), (92, 91, 84))
    draw.rectangle((0, image_h, tile_w, image_h + label_h), fill=(245, 243, 236))
    draw.rectangle((0, image_h, 6, image_h + label_h), fill=status_color)
    priority, priority_note = PRIORITIES.get(taxon_id, ("P3", "review after higher-risk taxa"))
    priority_color = PRIORITY_COLORS.get(priority, (58, 116, 82))
    draw.rectangle((tile_w - 54, image_h + 8, tile_w - 10, image_h + 28), fill=priority_color)
    draw.text((tile_w - 45, image_h + 13), priority, fill=(250, 248, 239), font=font)
    draw.text((14, image_h + 10), TAXON_LABELS.get(taxon_id, taxon_id), fill=(38, 35, 30), font=font)
    draw.text((14, image_h + 30), item.get("kind", ""), fill=status_color, font=font)
    draw_wrapped(draw, (14, image_h + 50), priority_note, font, (116, 63, 45), 44, 15, 2)
    draw_wrapped(draw, (14, image_h + 80), NEXT_ROUTES.get(taxon_id, NOTES.get(taxon_id, "")), font, (74, 68, 58), 44, 15, 2)
    return tile


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    samples = data["samples"]
    selected = []
    for taxon_id in TAXON_ORDER:
        items = samples.get(taxon_id) or []
        if not items:
            continue
        selected.append((taxon_id, sorted(items, key=lambda item: DISPLAY_RANK.get(item.get("kind"), 6))[0]))

    cols = 4
    tile_w = 360
    image_h = 236
    label_h = 120
    gap = 14
    header_h = 92
    rows = (len(selected) + cols - 1) // cols
    sheet_w = cols * tile_w + (cols + 1) * gap
    sheet_h = header_h + rows * (image_h + label_h + gap) + gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (226, 222, 212))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    draw.rectangle((0, 0, sheet_w, header_h), fill=(26, 59, 45))
    draw.text((24, 22), "Dinosaur Atlas - representative improvement priorities", fill=(246, 244, 236), font=font)
    draw.text(
        (24, 48),
        "Current app-leading images only. P0/P1 cards should drive the next generation and i2i loops.",
        fill=(218, 226, 214),
        font=font,
    )
    draw.text((24, 68), f"{len(selected)} taxa / generated from app-gallery-samples.json", fill=(190, 205, 190), font=font)

    for idx, (taxon_id, item) in enumerate(selected):
        tile = make_tile(taxon_id, item, (tile_w, image_h, label_h), font)
        x = gap + (idx % cols) * (tile_w + gap)
        y = header_h + gap + (idx // cols) * (image_h + label_h + gap)
        sheet.paste(tile, (x, y))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
