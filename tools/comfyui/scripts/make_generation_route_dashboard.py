import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "tools" / "comfyui" / "outputs" / "app-gallery-samples.json"
OUT_JSON = ROOT / "tools" / "comfyui" / "outputs" / "generation-route-summary.json"
OUT_IMAGE = ROOT / "assets" / "dinosaurs" / "generation-route-dashboard-v1.png"


ROUTES = [
    {
        "taxon": "tyrannosaurus-rex",
        "label": "Tyrannosaurus rex",
        "schedule": "tools/comfyui/lora_training/theropod_tyrannosaurus/twofinger_bodylock_prompt_schedule.json",
        "focus": "tiny arms, exactly two fingers, skull surface",
    },
    {
        "taxon": "triceratops-horridus",
        "label": "Triceratops",
        "schedule": "tools/comfyui/lora_training/ceratopsian_triceratops/skullfrill_bodylock_prompt_schedule.json",
        "focus": "cool color pattern, skull-attached frill, non-hoofed toes",
    },
    {
        "taxon": "velociraptor-mongoliensis",
        "label": "Velociraptor",
        "schedule": "tools/comfyui/lora_training/dromaeosaur_feathered/identity_bodylock_prompt_schedule.json",
        "focus": "dark-speckled plumage, toothed snout, modest attached sickle toe",
    },
    {
        "taxon": "stegosaurus-stenops",
        "label": "Stegosaurus",
        "schedule": "tools/comfyui/lora_training/stegosaur_plates_tailspikes/plate_topology_prompt_schedule.json",
        "focus": "ground-relative upward V thagomizer, bony plates, alternating plates",
    },
    {
        "taxon": "ankylosaurus-magniventris",
        "label": "Ankylosaurus",
        "schedule": "tools/comfyui/lora_training/ankylosaur_armor_tailclub/armor_tailclub_prompt_schedule.json",
        "focus": "armored skull, color pattern, single attached tail club",
    },
    {
        "taxon": "herrerasaurus-ischigualastensis",
        "label": "Herrerasaurus",
        "schedule": "tools/comfyui/lora_training/early_saurischian_herrerasaurus/bodylock_prompt_schedule.json",
        "focus": "compact hands, three main digits, two hind legs",
    },
    {
        "taxon": "coelophysis-bauri",
        "label": "Coelophysis",
        "schedule": "tools/comfyui/lora_training/small_theropod_coelophysis/bodylock_prompt_schedule.json",
        "focus": "slender S-neck, small hands, reviewable feet",
    },
        {
            "taxon": "plateosaurus-engelhardti",
            "label": "Plateosaurus",
            "schedule": "tools/comfyui/lora_training/early_sauropodomorph_plateosaurus/bodylock_prompt_schedule.json",
            "focus": "dark speckled color, no-six-leg gate, lifted hands, thumb claw",
        },
    {
        "taxon": "allosaurus-fragilis",
        "label": "Allosaurus",
        "schedule": "tools/comfyui/lora_training/theropod_allosaurus/threefinger_bodylock_prompt_schedule.json",
        "focus": "low skull, medium arms, three fingers",
    },
    {
        "taxon": "apatosaurus-ajax",
        "label": "Apatosaurus",
        "schedule": "tools/comfyui/lora_training/sauropod_apatosaurus/bodylock_prompt_schedule.json",
        "focus": "low neck, similar-height legs, full horizontal tail",
    },
    {
        "taxon": "brachiosaurus-altithorax",
        "label": "Brachiosaurus",
        "schedule": "tools/comfyui/lora_training/sauropod_brachiosaurus/bodylock_prompt_schedule.json",
        "focus": "high shoulders, taller forelimbs, short thick tail",
    },
]


KIND_RANK = {
    "primary generated": 0,
    "primary structure reference": 0,
    "count-level pass": 0,
    "anatomy review": 1,
    "structure reference": 2,
    "diagnostic only": 3,
}


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def select_primary(items):
    return sorted(items, key=lambda item: KIND_RANK.get(item.get("kind"), 9))[0] if items else None


def load_schedule(route):
    path = ROOT / route["schedule"]
    data = json.loads(path.read_text(encoding="utf-8"))
    return path, data


def control_refs(schedule):
    refs = []
    for key in ("controlReferences", "controlReference", "secondaryControlReference"):
        value = schedule.get(key)
        if not value:
            continue
        if isinstance(value, list):
            refs.extend(value)
        else:
            refs.append(value)
    for item in schedule.get("passes", []):
        for key in ("controlImage", "sourceImage", "styleReference"):
            value = item.get(key)
            if value and value not in refs:
                refs.append(value)
    return refs


def range_text(value):
    if not isinstance(value, list) or len(value) != 2:
        return ""
    return f"{value[0]}-{value[1]}"


def pass_summary(schedule):
    if schedule.get("passSummary"):
        return schedule["passSummary"]
    passes = schedule.get("passes") or []
    if passes:
        first = passes[0]
        bits = [first.get("id", "pass")]
        if first.get("mode"):
            bits.append(first["mode"])
        if first.get("denoiseRange"):
            bits.append(f"denoise {range_text(first['denoiseRange'])}")
        if first.get("controlStrengthRange"):
            bits.append(f"control {range_text(first['controlStrengthRange'])}")
        return " | ".join(bits)
    prompts = schedule.get("prompts") or []
    if prompts:
        return f"{len(prompts)} prompt variations | use guide as ControlNet/depth structure"
    return schedule.get("purpose", "manual review route")


def reject_summary(schedule):
    if schedule.get("rejectSummary"):
        return schedule["rejectSummary"]
    manual = schedule.get("manualGate") or schedule.get("workflowNotes") or []
    for item in manual:
        if "reject" in item.lower():
            return item
    negative = schedule.get("baseNegative", "")
    if negative:
        return "reject: " + ", ".join(negative.split(",")[:5]).strip()
    return "reject if guide traits are lost"


def fit_image(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (236, 233, 224))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def paste_image(sheet, rel_path, xy, size):
    x, y = xy
    path = ROOT / rel_path
    if path.exists():
        sheet.paste(fit_image(path, size), (x, y))
        return
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((x, y, x + size[0], y + size[1]), fill=(222, 218, 208))
    draw.text((x + 14, y + 14), "missing", fill=(106, 81, 70))


def draw_wrapped(draw, xy, text, font, fill, max_chars=45, line_h=15, max_lines=3):
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


def build_summary():
    manifest = load_manifest()
    samples = manifest["samples"]
    entries = []
    for route in ROUTES:
        schedule_path, schedule = load_schedule(route)
        primary = select_primary(samples.get(route["taxon"], []))
        refs = control_refs(schedule)
        guide = refs[0] if refs else ""
        entries.append(
            {
                "taxon": route["taxon"],
                "label": route["label"],
                "focus": route["focus"],
                "status": primary.get("kind", "") if primary else "missing primary",
                "primaryImage": primary.get("src", "") if primary else "",
                "primaryTitle": primary.get("title", "") if primary else "",
                "schedule": str(schedule_path.relative_to(ROOT)).replace("\\", "/"),
                "datasetId": schedule.get("datasetId", ""),
                "route": schedule.get("route") or schedule.get("purpose", ""),
                "trigger": schedule.get("trigger", ""),
                "controlReferences": refs,
                "primaryControlReference": guide,
                "passSummary": pass_summary(schedule),
                "rejectSummary": reject_summary(schedule),
            }
        )
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"routes": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entries


def draw_card(sheet, entry, xy, size, font):
    x, y = xy
    w, h = size
    draw = ImageDraw.Draw(sheet)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=6, fill=(246, 244, 237))
    draw.text((x + 14, y + 12), entry["label"], fill=(31, 36, 31), font=font)
    draw.rectangle((x + 14, y + 34, x + 118, y + 54), fill=(42, 103, 75))
    draw.text((x + 20, y + 39), entry["status"][:20], fill=(250, 248, 239), font=font)

    image_y = y + 64
    paste_image(sheet, entry["primaryImage"], (x + 14, image_y), (226, 142))
    if entry["primaryControlReference"]:
        paste_image(sheet, entry["primaryControlReference"], (x + 254, image_y), (226, 142))
    draw.text((x + 14, image_y + 150), "current", fill=(95, 88, 78), font=font)
    draw.text((x + 254, image_y + 150), "control guide", fill=(95, 88, 78), font=font)

    text_y = image_y + 176
    draw.text((x + 14, text_y), "Focus", fill=(95, 88, 78), font=font)
    draw_wrapped(draw, (x + 14, text_y + 18), entry["focus"], font, (45, 44, 39), max_chars=54, max_lines=2)
    draw.text((x + 14, text_y + 58), "Next route", fill=(95, 88, 78), font=font)
    draw_wrapped(draw, (x + 14, text_y + 76), entry["passSummary"], font, (45, 44, 39), max_chars=62, max_lines=2)
    draw.text((x + 14, text_y + 118), "Reject first if", fill=(95, 88, 78), font=font)
    draw_wrapped(draw, (x + 14, text_y + 136), entry["rejectSummary"], font, (45, 44, 39), max_chars=62, max_lines=3)
    draw.text((x + 14, y + h - 24), Path(entry["schedule"]).name, fill=(115, 101, 84), font=font)


def draw_dashboard(entries):
    font = ImageFont.load_default()
    cols = 2
    card_w = 520
    card_h = 470
    gap = 16
    header_h = 106
    rows = (len(entries) + cols - 1) // cols
    sheet_w = cols * card_w + (cols + 1) * gap
    sheet_h = header_h + rows * (card_h + gap) + gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (224, 220, 211))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet_w, header_h), fill=(28, 62, 48))
    draw.text((22, 18), "Dinosaur Atlas - generation route dashboard v1", fill=(248, 246, 238), font=font)
    draw.text((22, 44), "Current app-leading candidate plus the next guide-conditioned ComfyUI route for each taxon.", fill=(219, 228, 216), font=font)
    draw.text((22, 70), "Use this as the run queue before promoting any naturalized output.", fill=(190, 207, 190), font=font)
    for idx, entry in enumerate(entries):
        x = gap + (idx % cols) * (card_w + gap)
        y = header_h + gap + (idx // cols) * (card_h + gap)
        draw_card(sheet, entry, (x, y), (card_w, card_h), font)
    OUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_IMAGE)
    print(OUT_JSON)
    print(OUT_IMAGE)


def main():
    entries = build_summary()
    draw_dashboard(entries)


if __name__ == "__main__":
    main()
