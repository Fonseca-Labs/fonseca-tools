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

    # People-first editorial layer must exist on every tool page.
    required_markers = [
        'data-seo-content',
        'class="breadcrumb"',
        'data-breadcrumb-schema',
        '<h2>Como calcular</h2>',
        '<h2>Exemplo prático</h2>',
        '<h2>Dúvidas comuns</h2>',
        'Ferramenta grátis, sem cadastro e com processamento no navegador.',
    ]
    for marker in required_markers:
        if marker not in html:
            errors.append(f"{slug}: missing SEO marker {marker}")

about = ROOT / "sobre" / "index.html"
if not about.exists():
    errors.append("missing trust page: sobre/index.html")
else:
    about_html = about.read_text(encoding="utf-8")
    for marker in ["Sobre a Fonseca Tools", "Como as ferramentas são feitas", "Projeto público"]:
        if marker not in about_html:
            errors.append(f"sobre/index.html: missing {marker}")

sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
if "/sobre/</loc>" not in sitemap:
    errors.append("sitemap.xml: /sobre/ is missing")

# Every normal page should reference versioned local assets after postbuild.
normal_pages = [
    ROOT / "index.html",
    ROOT / "privacidade" / "index.html",
    ROOT / "sobre" / "index.html",
    *[ROOT / t["slug"] / "index.html" for t in TOOLS],
]
for page in normal_pages:
    if not page.exists():
        errors.append(f"missing page: {page.relative_to(ROOT)}")
        continue
    html = page.read_text(encoding="utf-8")
    if "app.js?v=" not in html:
        errors.append(f"{page.relative_to(ROOT)}: app.js is not cache-busted")
    if "styles.css?v=" not in html:
        errors.append(f"{page.relative_to(ROOT)}: styles.css is not cache-busted")

if errors:
    raise SystemExit("Build validation failed:\n- " + "\n- ".join(errors))

print(f"Build validation passed: {len(TOOLS)} tools, formulas mapped, SEO enriched, assets versioned")
