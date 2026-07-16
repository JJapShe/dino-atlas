import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_JS = ROOT / "app.js"
SUMMARY_JSON = ROOT / "tools" / "comfyui" / "outputs" / "generation-route-summary.json"

FIELD_MAP = {
    "focus": "focus",
    "route": "route",
    "control": "primaryControlReference",
    "pass": "passSummary",
    "reject": "rejectSummary",
}


def decode_js_string(value):
    return json.loads(f'"{value}"')


def extract_generation_routes(app_source):
    block_match = re.search(
        r"const generationRouteGuides = \{\n(?P<body>.*?)\n\};\n\nfunction getGenerationRouteGuide",
        app_source,
        re.S,
    )
    if not block_match:
        raise ValueError("Could not find generationRouteGuides block in app.js")

    routes = {}
    entry_pattern = re.compile(r'  "([^"]+)": \{\n(?P<body>.*?)\n  \},', re.S)
    field_pattern = re.compile(r'    (focus|route|control|pass|reject): "((?:\\.|[^"\\])*)",')

    for entry in entry_pattern.finditer(block_match.group("body")):
        taxon = entry.group(1)
        fields = {}
        for field, raw_value in field_pattern.findall(entry.group("body")):
            fields[field] = decode_js_string(raw_value)
        routes[taxon] = fields

    return routes


def main():
    app_routes = extract_generation_routes(APP_JS.read_text(encoding="utf-8"))
    summary_routes = {
        route["taxon"]: route
        for route in json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))["routes"]
    }

    problems = []
    app_taxa = set(app_routes)
    summary_taxa = set(summary_routes)

    for taxon in sorted(summary_taxa - app_taxa):
        problems.append({"taxon": taxon, "problem": "missing from app generationRouteGuides"})
    for taxon in sorted(app_taxa - summary_taxa):
        problems.append({"taxon": taxon, "problem": "missing from generation-route-summary.json"})

    for taxon in sorted(app_taxa & summary_taxa):
        app_route = app_routes[taxon]
        summary_route = summary_routes[taxon]
        for app_field, summary_field in FIELD_MAP.items():
            app_value = app_route.get(app_field)
            summary_value = summary_route.get(summary_field)
            if app_value != summary_value:
                problems.append(
                    {
                        "taxon": taxon,
                        "field": app_field,
                        "app": app_value,
                        "summary": summary_value,
                    }
                )

        control_path = app_route.get("control")
        if control_path and not (ROOT / control_path).exists():
            problems.append(
                {
                    "taxon": taxon,
                    "field": "control",
                    "problem": "control guide image does not exist",
                    "path": control_path,
                }
            )

    result = {
        "checked": len(app_taxa & summary_taxa),
        "appRoutes": len(app_taxa),
        "summaryRoutes": len(summary_taxa),
        "problems": problems,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
