from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
TOOLS = json.loads((ROOT / "tools.json").read_text(encoding="utf-8"))
APP_JS = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")

CATEGORY_SLUGS = {
    "Matemática": "matematica",
    "Datas": "datas",
    "Conversão": "conversao",
    "Texto e dados": "texto-e-dados",
    "Financeiro": "financeiro",
}

errors = []

for tool in TOOLS:
    slug = tool["slug"]
    formula = tool["formula"]
    category = tool["category"]
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

    category_slug = CATEGORY_SLUGS.get(category)
    if not category_slug:
        errors.append(f"{slug}: unknown category {category}")
    else:
        if f'href="../{category_slug}/"' not in html:
            errors.append(f"{slug}: missing link to category hub {category_slug}/")
        if 'data-category-link' not in html:
            errors.append(f"{slug}: missing category related-tools link")
        if f'"position": 2, "name": "{category}"' not in html:
            errors.append(f"{slug}: breadcrumb schema does not include category {category}")

about = ROOT / "sobre" / "index.html"
if not about.exists():
    errors.append("missing trust page: sobre/index.html")
else:
    about_html = about.read_text(encoding="utf-8")
    for marker in ["Sobre a Fonseca Tools", "Como as ferramentas são feitas", "Projeto público"]:
        if marker not in about_html:
            errors.append(f"sobre/index.html: missing {marker}")

# Category hubs must exist, be linked from home, and link every tool in their category.
home = ROOT / "index.html"
home_html = home.read_text(encoding="utf-8") if home.exists() else ""
if 'id="categorias"' not in home_html:
    errors.append("index.html: category directory is missing")

category_pages = []
for category, category_slug in CATEGORY_SLUGS.items():
    page = ROOT / category_slug / "index.html"
    category_pages.append(page)
    if not page.exists():
        errors.append(f"missing category hub: {category_slug}/index.html")
        continue
    html = page.read_text(encoding="utf-8")
    for marker in [
        f'data-category-hub="{category_slug}"',
        'data-breadcrumb-schema',
        'class="tool-grid"',
        f'href="../{category_slug}/"',
    ]:
        # The self-link marker is checked on home below, not in the category page itself.
        if marker == f'href="../{category_slug}/"':
            continue
        if marker not in html:
            errors.append(f"{category_slug}/index.html: missing {marker}")
    if f'href="{category_slug}/"' not in home_html:
        errors.append(f"index.html: missing link to category hub {category_slug}/")
    for tool in [t for t in TOOLS if t["category"] == category]:
        if f'href="../{tool["slug"]}/"' not in html:
            errors.append(f"{category_slug}/index.html: missing link to {tool['slug']}/")

sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
if "/sobre/</loc>" not in sitemap:
    errors.append("sitemap.xml: /sobre/ is missing")
for category_slug in CATEGORY_SLUGS.values():
    if f"/{category_slug}/</loc>" not in sitemap:
        errors.append(f"sitemap.xml: /{category_slug}/ is missing")

# Every normal page should reference versioned local assets after postbuild.
normal_pages = [
    ROOT / "index.html",
    ROOT / "privacidade" / "index.html",
    ROOT / "sobre" / "index.html",
    *category_pages,
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

print(
    f"Build validation passed: {len(TOOLS)} tools, {len(CATEGORY_SLUGS)} category hubs, "
    "formulas mapped, SEO enriched, internal links complete, assets versioned"
)
