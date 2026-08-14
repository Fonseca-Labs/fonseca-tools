from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
TOOLS = json.loads((ROOT / "tools.json").read_text(encoding="utf-8"))
APP_JS = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")

errors = []

for tool in TOOLS:
    slug = tool["slug"]
    formula = tool["formula"]
    page = ROOT / slug / "index.html"
    if not page.exists():
        errors.append(f"missing page: {slug}/index.html")
        continue
    html = page.read_text(encoding="utf-8")
    expected = f'data-tool="{formula}"'
    if expected not in html:
        errors.append(f"{slug}: expected {expected}")
    case_pattern = re.compile(r"case\s+['\"]" + re.escape(formula) + r"['\"]\s*:")
    if not case_pattern.search(APP_JS):
        errors.append(f"{slug}: JavaScript case missing for formula {formula}")

# Every normal page should reference versioned local assets after postbuild.
for page in [ROOT / "index.html", *[ROOT / t["slug"] / "index.html" for t in TOOLS]]:
    html = page.read_text(encoding="utf-8")
    if "app.js?v=" not in html:
        errors.append(f"{page.relative_to(ROOT)}: app.js is not cache-busted")
    if "styles.css?v=" not in html:
        errors.append(f"{page.relative_to(ROOT)}: styles.css is not cache-busted")

if errors:
    raise SystemExit("Build validation failed:\n- " + "\n- ".join(errors))

print(f"Build validation passed: {len(TOOLS)} tools, formulas mapped, assets versioned")
