from pathlib import Path
import html
import json
import os
import re

ROOT = Path(__file__).resolve().parent
SITE_URL = os.environ.get("SITE_URL", "https://fonseca-labs.github.io/fonseca-tools").rstrip("/")
TOOLS = json.loads((ROOT / "tools.json").read_text(encoding="utf-8"))

CATEGORY_META = {
    "Matemática": {
        "slug": "matematica",
        "title": "Calculadoras de Matemática Online",
        "description": "Calculadoras gratuitas para porcentagem, descontos, acréscimos, média, regra de três e outros cálculos do dia a dia.",
        "intro": "Resolva cálculos matemáticos comuns sem planilha e sem cadastro. As páginas desta categoria explicam a fórmula usada e mostram exemplos práticos.",
    },
    "Datas": {
        "slug": "datas",
        "title": "Calculadoras de Datas e Horários",
        "description": "Ferramentas gratuitas para diferenças entre datas, idade, dias úteis, semanas, meses, horários e prazos.",
        "intro": "Compare datas, some períodos e calcule intervalos de tempo diretamente no navegador. Cada ferramenta informa suas regras e limitações.",
    },
    "Conversão": {
        "slug": "conversao",
        "title": "Conversores Online",
        "description": "Conversores gratuitos de tempo e velocidade, incluindo horas, minutos, horas decimais, km/h e m/s.",
        "intro": "Faça conversões rápidas com fórmulas transparentes e exemplos. Os cálculos são executados localmente no navegador.",
    },
    "Texto e dados": {
        "slug": "texto-e-dados",
        "title": "Ferramentas de Texto e Dados",
        "description": "Utilitários gratuitos para contar palavras, limpar e ordenar linhas, remover duplicados, formatar JSON e converter CSV.",
        "intro": "Trate pequenos textos e listas sem enviar o conteúdo para um servidor. As ferramentas priorizam tarefas rápidas e formatos simples.",
    },
    "Financeiro": {
        "slug": "financeiro",
        "title": "Calculadoras Financeiras Simples",
        "description": "Calculadoras gratuitas de margem de lucro e markup para simulações matemáticas de custo e preço de venda.",
        "intro": "Faça simulações matemáticas de precificação com fórmula e limitações descritas na própria página. Os resultados não substituem orientação contábil ou financeira.",
    },
}


def esc(value):
    return html.escape(str(value), quote=True)


categories = []
for tool in TOOLS:
    category = tool["category"]
    if category not in categories:
        categories.append(category)

unknown = [category for category in categories if category not in CATEGORY_META]
if unknown:
    raise SystemExit(f"Missing category metadata: {unknown}")


def tools_for(category):
    return [tool for tool in TOOLS if tool["category"] == category]


def category_breadcrumb_schema(category):
    meta = CATEGORY_META[category]
    canonical = f"{SITE_URL}/{meta['slug']}/"
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Fonseca Tools", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": category, "item": canonical},
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def tool_breadcrumb_schema(tool):
    category = tool["category"]
    meta = CATEGORY_META[category]
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Fonseca Tools", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": category, "item": f"{SITE_URL}/{meta['slug']}/"},
            {"@type": "ListItem", "position": 3, "name": tool["title"], "item": f"{SITE_URL}/{tool['slug']}/"},
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def category_page(category):
    meta = CATEGORY_META[category]
    items = tools_for(category)
    canonical = f"{SITE_URL}/{meta['slug']}/"
    cards = "".join(
        f'''<a class="tool-card" href="../{esc(tool['slug'])}/"><span class="card-category">{esc(category)}</span><h3>{esc(tool['title'])}</h3><p>{esc(tool['description'])}</p><span class="card-link">Abrir ferramenta →</span></a>'''
        for tool in items
    )
    other_categories = "".join(
        f'''<a class="category-mini" href="../{esc(CATEGORY_META[other]['slug'])}/"><strong>{esc(other)}</strong><span>{len(tools_for(other))} ferramenta{'s' if len(tools_for(other)) != 1 else ''}</span></a>'''
        for other in categories if other != category
    )
    collection_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": meta["title"],
        "url": canonical,
        "description": meta["description"],
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": index, "url": f"{SITE_URL}/{tool['slug']}/", "name": tool["title"]}
                for index, tool in enumerate(items, start=1)
            ],
        },
    }
    count_label = f"{len(items)} ferramenta{'s' if len(items) != 1 else ''}"
    return f'''<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta['title'])} — Fonseca Tools</title>
<meta name="description" content="{esc(meta['description'])}">
<link rel="canonical" href="{esc(canonical)}"><meta name="robots" content="index,follow">
<link rel="stylesheet" href="../assets/styles.css">
<script type="application/ld+json" data-breadcrumb-schema>{category_breadcrumb_schema(category)}</script>
<script type="application/ld+json">{json.dumps(collection_schema, ensure_ascii=False)}</script>
</head><body data-category-hub="{esc(meta['slug'])}">
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="../">Fonseca Tools</a><nav><a href="../#categorias">Categorias</a><a href="../sobre/">Sobre</a><a href="../privacidade/">Privacidade</a></nav></div></header>
<main>
<section class="hero category-hero"><div class="wrap">
<nav class="breadcrumb" aria-label="Navegação estrutural"><a href="../">Início</a><span aria-hidden="true">›</span><span>{esc(category)}</span></nav>
<div class="eyebrow">Categoria • {esc(count_label)}</div><h1>{esc(meta['title'])}</h1><p class="lead">{esc(meta['intro'])}</p>
</div></section>
<section class="wrap tools-section category-tools"><div class="section-heading"><span>{esc(category)}</span><h2>Ferramentas disponíveis</h2></div><div class="tool-grid">{cards}</div></section>
<section class="wrap category-context"><div class="info-card"><h2>Sobre esta categoria</h2><p>{esc(meta['description'])}</p><p>Escolha uma ferramenta acima para ver o cálculo, a fórmula ou método utilizado, exemplos e limitações específicas.</p></div></section>
<section class="wrap other-categories"><div class="section-heading"><span>Continuar explorando</span><h2>Outras categorias</h2></div><div class="category-mini-grid">{other_categories}</div></section>
</main>
<footer><div class="wrap footer-inner"><span>© <span data-year></span> Fonseca Tools</span><span>Um projeto da Fonseca Labs.</span></div></footer>
<script src="../assets/app.js" defer></script></body></html>'''


# Generate one crawlable hub per category.
for category in categories:
    meta = CATEGORY_META[category]
    directory = ROOT / meta["slug"]
    directory.mkdir(exist_ok=True)
    (directory / "index.html").write_text(category_page(category), encoding="utf-8")

# Add category directory to the homepage and make existing section headings links.
home = ROOT / "index.html"
home_html = home.read_text(encoding="utf-8")
if 'id="categorias"' not in home_html:
    cards = "".join(
        f'''<a class="category-card" href="{esc(CATEGORY_META[category]['slug'])}/"><span class="card-category">{esc(category)}</span><h3>{esc(CATEGORY_META[category]['title'])}</h3><p>{esc(CATEGORY_META[category]['description'])}</p><span class="card-link">Ver {len(tools_for(category))} ferramenta{'s' if len(tools_for(category)) != 1 else ''} →</span></a>'''
        for category in categories
    )
    directory = f'''<section id="categorias" class="wrap category-directory"><div class="section-heading"><span>Explorar por assunto</span><h2>Categorias de ferramentas</h2><p>Entre por uma categoria para encontrar ferramentas relacionadas e navegar por uma estrutura mais simples.</p></div><div class="category-grid">{cards}</div></section>'''
    anchor = '<section id="ferramentas" class="wrap tools-section">'
    if anchor not in home_html:
        raise SystemExit("Homepage tools anchor not found")
    home_html = home_html.replace(anchor, directory + anchor, 1)

for category in categories:
    slug = CATEGORY_META[category]["slug"]
    old = f'<section class="tool-category"><h2>{esc(category)}</h2>'
    new = f'<section class="tool-category"><h2><a class="category-heading-link" href="{esc(slug)}/">{esc(category)}</a></h2>'
    home_html = home_html.replace(old, new)

if '<a href="#categorias">Categorias</a>' not in home_html:
    home_html = home_html.replace('<a href="#ferramentas">Ferramentas</a>', '<a href="#categorias">Categorias</a><a href="#ferramentas">Ferramentas</a>', 1)
home.write_text(home_html, encoding="utf-8")

# Upgrade each tool breadcrumb to Home > Category > Tool and link back to its hub.
breadcrumb_re = re.compile(r'<nav class="breadcrumb" aria-label="Navegação estrutural">.*?</nav>', re.S)
schema_re = re.compile(r'<script type="application/ld\+json" data-breadcrumb-schema>.*?</script>', re.S)
related_anchor = '<section class="wrap narrow related"><h2>Ferramentas relacionadas</h2><div class="related-grid">'

for tool in TOOLS:
    category = tool["category"]
    meta = CATEGORY_META[category]
    page = ROOT / tool["slug"] / "index.html"
    text = page.read_text(encoding="utf-8")
    visible = f'''<nav class="breadcrumb" aria-label="Navegação estrutural"><a href="../">Início</a><span aria-hidden="true">›</span><a href="../{esc(meta['slug'])}/">{esc(category)}</a><span aria-hidden="true">›</span><span>{esc(tool['title'])}</span></nav>'''
    text, count = breadcrumb_re.subn(visible, text, count=1)
    if count != 1:
        raise SystemExit(f"Breadcrumb replacement failed for {tool['slug']}")
    structured = f'<script type="application/ld+json" data-breadcrumb-schema>{tool_breadcrumb_schema(tool)}</script>'
    text, count = schema_re.subn(structured, text, count=1)
    if count != 1:
        raise SystemExit(f"Breadcrumb schema replacement failed for {tool['slug']}")
    if 'data-category-link' not in text:
        enhanced_related = f'''<section class="wrap narrow related"><div class="related-heading"><div><span class="card-category">{esc(category)}</span><h2>Mais ferramentas de {esc(category)}</h2></div><a class="category-back-link" data-category-link href="../{esc(meta['slug'])}/">Ver categoria completa →</a></div><div class="related-grid">'''
        if related_anchor not in text:
            raise SystemExit(f"Related-tools anchor not found for {tool['slug']}")
        text = text.replace(related_anchor, enhanced_related, 1)
    page.write_text(text, encoding="utf-8")

# Styles for category hubs and stronger internal navigation.
styles = ROOT / "assets" / "styles.css"
css = styles.read_text(encoding="utf-8")
if '.category-directory{' not in css:
    css += '''\n.category-directory{padding:54px 0 12px}.category-directory .section-heading p{max-width:720px;color:var(--muted)}.category-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px}.category-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;text-decoration:none;color:var(--ink);box-shadow:0 1px 0 rgba(20,35,70,.01);transition:.18s}.category-card:hover{transform:translateY(-3px);box-shadow:var(--shadow);border-color:#cfd7e8}.category-card h3{margin:8px 0;letter-spacing:-.02em}.category-card p{color:var(--muted);font-size:.94rem}.category-heading-link{color:var(--ink);text-decoration:none}.category-heading-link:hover{color:var(--accent)}.category-hero{padding-bottom:34px}.category-tools{padding-top:24px}.category-context{padding:4px 0 16px}.other-categories{padding:18px 0 72px}.category-mini-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:18px}.category-mini{display:grid;gap:3px;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;color:var(--ink);text-decoration:none}.category-mini span{color:var(--muted);font-size:.86rem}.related-heading{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:14px}.related-heading h2{margin:4px 0 0}.category-back-link{color:var(--accent);font-weight:800;text-decoration:none;font-size:.92rem;white-space:nowrap}.category-back-link:hover{text-decoration:underline}@media(max-width:800px){.category-grid{grid-template-columns:1fr 1fr}.category-mini-grid{grid-template-columns:1fr 1fr}}@media(max-width:560px){.category-grid,.category-mini-grid{grid-template-columns:1fr}.related-heading{align-items:start;flex-direction:column;gap:8px}.category-back-link{white-space:normal}}\n'''
    styles.write_text(css, encoding="utf-8")

# Add category hubs to sitemap.
sitemap = ROOT / "sitemap.xml"
xml = sitemap.read_text(encoding="utf-8")
for category in categories:
    url = f"{SITE_URL}/{CATEGORY_META[category]['slug']}/"
    if url not in xml:
        xml = xml.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
sitemap.write_text(xml, encoding="utf-8")

print(f"Architecture enhancement complete: {len(categories)} category hubs linking {len(TOOLS)} tools")
