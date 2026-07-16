import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_JS = ROOT / "app.js"
SUMMARY_JSON = ROOT / "tools" / "comfyui" / "outputs" / "generation-route-summary.json"
OUT_JSON = ROOT / "tools" / "comfyui" / "next-generation-batch-plan.json"
OUT_MD = ROOT / "tools" / "comfyui" / "next-generation-batch-plan.md"


PRIORITY = {
    "velociraptor-mongoliensis": 1,
    "stegosaurus-stenops": 2,
    "triceratops-horridus": 3,
    "ankylosaurus-magniventris": 4,
    "plateosaurus-engelhardti": 5,
    "tyrannosaurus-rex": 6,
    "allosaurus-fragilis": 7,
    "herrerasaurus-ischigualastensis": 8,
    "coelophysis-bauri": 9,
    "apatosaurus-ajax": 10,
    "brachiosaurus-altithorax": 11,
}

WHY_FIRST = {
    "velociraptor-mongoliensis": "highest identity risk: toothed non-bird head, feathers, and attached sickle toe must survive together",
    "stegosaurus-stenops": "signature plates still need stricter two-row topology and four-spike tail verification",
    "triceratops-horridus": "must keep the anti-rhinoceros gate: skull-attached frill, low body, long tail, and non-hoofed toes",
    "ankylosaurus-magniventris": "tail club is present but broad ankylosaur skull/body identity and armor layout still need tightening",
    "plateosaurus-engelhardti": "six-leg and forelimb-ground-contact risks are still the main promotion blockers",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode_js_string(value):
    return json.loads(f'"{value}"')


def extract_visual_variation_profiles(app_source):
    block_match = re.search(
        r"const visualVariationProfiles = \{\n(?P<body>.*?)\n\};\n\nfunction getVisualVariationProfile",
        app_source,
        re.S,
    )
    if not block_match:
        raise ValueError("Could not find visualVariationProfiles block in app.js")

    profiles = {}
    entry_pattern = re.compile(r'  "([^"]+)": \{\n(?P<body>.*?)\n  \},', re.S)
    field_pattern = re.compile(r'    (color|pattern|texture|anatomy|avoid): "((?:\\.|[^"\\])*)",')

    for entry in entry_pattern.finditer(block_match.group("body")):
        taxon = entry.group(1)
        profiles[taxon] = {
            field: decode_js_string(raw_value)
            for field, raw_value in field_pattern.findall(entry.group("body"))
        }

    return profiles


def rel_exists(path):
    return bool(path) and (ROOT / path).exists()


def prompt_count(schedule_path):
    path = ROOT / schedule_path
    if not path.exists():
        return 0
    data = load_json(path)
    return len(data.get("prompts", []))


def ps_quote(value):
    return "'" + value.replace("'", "''") + "'"


def make_commands(route, seed_base, prefix):
    taxon = route["taxon"]
    control = route.get("primaryControlReference", "")
    schedule = route.get("schedule", "")
    commands = {
        "controlnetProbe": (
            "python tools/comfyui/scripts/run_controlnet_experiment.py "
            f"--taxon-id {taxon} "
            f"--source-image {ps_quote(control)} "
            f"--seed {seed_base + 1} --seed {seed_base + 2} "
            "--strength 0.45 --strength 0.62 "
            "--end-percent 0.56 --end-percent 0.72 "
            f"--prefix {prefix}_controlnet --clean-corners"
        ),
        "scheduleProbe": (
            "python tools/comfyui/scripts/run_lora_seed_schedule.py "
            f"--schedule {ps_quote(schedule)} "
            "--limit 3 "
            f"--seed-base {seed_base + 20} "
            f"--prefix {prefix}_schedule"
        ),
        "i2iProbe": (
            "python tools/comfyui/scripts/run_schedule_i2i_experiment.py "
            f"--schedule {ps_quote(schedule)} "
            f"--source-image {ps_quote(control)} "
            f"--seed {seed_base + 40} --seed {seed_base + 41} "
            "--denoise 0.42 --denoise 0.56 "
            f"--prefix {prefix}_schedule_i2i"
        ),
    }
    return commands


def make_variation_prompt(profile):
    if not profile:
        return ""
    return (
        f"species-specific color: {profile['color']}; "
        f"pattern: {profile['pattern']}; "
        f"surface texture: {profile['texture']}; "
        f"signature anatomy: {profile['anatomy']}"
    )


def make_plan_item(route, variation_profiles):
    taxon = route["taxon"]
    variation_profile = variation_profiles.get(taxon, {})
    priority = PRIORITY.get(taxon, 99)
    safe_taxon = taxon.replace("-", "_")
    seed_base = 2026070100 + priority * 100
    prefix = f"next_{safe_taxon}_v1"
    control = route.get("primaryControlReference", "")
    schedule = route.get("schedule", "")
    prompts = prompt_count(schedule)
    missing = []
    for label, path in [
        ("primaryImage", route.get("primaryImage", "")),
        ("primaryControlReference", control),
        ("schedule", schedule),
    ]:
        if not rel_exists(path):
            missing.append({"field": label, "path": path})

    return {
        "priority": priority,
        "taxon": taxon,
        "label": route.get("label", taxon),
        "status": route.get("status", ""),
        "whyFirst": WHY_FIRST.get(taxon, "continue structure-guided polishing after higher-risk taxa"),
        "focus": route.get("focus", ""),
        "primaryImage": route.get("primaryImage", ""),
        "primaryControlReference": control,
        "schedule": schedule,
        "schedulePromptCount": prompts,
        "route": route.get("route", ""),
        "visualVariationProfile": variation_profile,
        "visualPromptAddendum": make_variation_prompt(variation_profile),
        "negativePromptAddendum": variation_profile.get("avoid", ""),
        "passSummary": route.get("passSummary", ""),
        "rejectSummary": route.get("rejectSummary", ""),
        "seedBase": seed_base,
        "prefix": prefix,
        "commands": make_commands(route, seed_base, prefix),
        "manualGate": [
            "do not auto-promote generated images",
            "compare full body first, then crop-check signature anatomy",
            "compare color, pattern, and surface texture against the species variation profile",
            "reject immediately if the hard rejection rule is visible at thumbnail scale",
        ],
        "missingInputs": missing,
    }


def write_markdown(items):
    lines = [
        "# Next Generation Batch Plan",
        "",
        "Use this queue after reviewing `assets/dinosaurs/generation-route-dashboard-v1.png` and the app review panel.",
        "Every output remains `needs_review` until manually checked against the identity gate and hard rejection rule.",
        "",
        "## Priority Queue",
        "",
    ]
    for item in items:
        lines.extend(
            [
                f"### {item['priority']}. {item['label']} (`{item['taxon']}`)",
                "",
                f"- Focus: {item['focus']}",
                f"- Why now: {item['whyFirst']}",
                f"- Current primary: `{item['primaryImage']}`",
                f"- Control guide: `{item['primaryControlReference']}`",
                f"- Schedule: `{item['schedule']}` ({item['schedulePromptCount']} prompts)",
                f"- Visual color: {item['visualVariationProfile'].get('color', '')}",
                f"- Visual pattern: {item['visualVariationProfile'].get('pattern', '')}",
                f"- Surface texture: {item['visualVariationProfile'].get('texture', '')}",
                f"- Signature anatomy: {item['visualVariationProfile'].get('anatomy', '')}",
                f"- Avoid similarity: {item['visualVariationProfile'].get('avoid', '')}",
                f"- Prompt addendum: {item['visualPromptAddendum']}",
                f"- Pass setup: {item['passSummary']}",
                f"- Hard reject: {item['rejectSummary']}",
                "",
                "ControlNet probe:",
                "",
                "```powershell",
                item["commands"]["controlnetProbe"],
                "```",
                "",
                "Schedule prompt probe:",
                "",
                "```powershell",
                item["commands"]["scheduleProbe"],
                "```",
                "",
                "Low-denoise i2i probe:",
                "",
                "```powershell",
                item["commands"]["i2iProbe"],
                "```",
                "",
            ]
        )
        if item["missingInputs"]:
            lines.append(f"- Missing inputs: `{json.dumps(item['missingInputs'], ensure_ascii=False)}`")
            lines.append("")
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    variation_profiles = extract_visual_variation_profiles(APP_JS.read_text(encoding="utf-8"))
    routes = load_json(SUMMARY_JSON)["routes"]
    items = sorted((make_plan_item(route, variation_profiles) for route in routes), key=lambda item: item["priority"])
    missing_profiles = [
        {"taxon": item["taxon"], "problem": "missing visualVariationProfile"}
        for item in items
        if not item["visualVariationProfile"]
    ]
    plan = {
        "source": str(SUMMARY_JSON.relative_to(ROOT)).replace("\\", "/"),
        "variationSource": str(APP_JS.relative_to(ROOT)).replace("\\", "/"),
        "reviewDashboard": "assets/dinosaurs/generation-route-dashboard-v1.png",
        "items": items,
        "problems": [
            {"taxon": item["taxon"], "missingInputs": item["missingInputs"]}
            for item in items
            if item["missingInputs"]
        ]
        + missing_profiles,
    }
    OUT_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(items)
    print(json.dumps({"json": str(OUT_JSON), "markdown": str(OUT_MD), "items": len(items), "problems": len(plan["problems"])}, indent=2))
    return 1 if plan["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
