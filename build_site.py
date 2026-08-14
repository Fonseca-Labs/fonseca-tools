from pathlib import Path
import json, html, os

ROOT = Path(__file__).resolve().parent
SITE_NAME = "Fonseca Tools"
BASE_URL = os.environ.get("SITE_URL", "https://SEU-DOMINIO.com").rstrip("/")

TOOLS = [
    {
        "id":"porcentagem", "slug":"porcentagem", "category":"Matemática",
        "title":"Calculadora de Porcentagem", "description":"Descubra rapidamente quanto é uma porcentagem de qualquer valor.",
        "kind":"two-number", "labels":["Porcentagem (%)", "Valor"], "placeholders":["Ex.: 15", "Ex.: 250"],
        "formula":"pct_of", "button":"Calcular porcentagem",
        "intro":"Informe a porcentagem e o valor de referência. O cálculo é feito no próprio navegador, sem enviar seus números para um servidor.",
        "example":"Exemplo: 15% de 250 = 37,5."
    },
    {
        "id":"variacao-percentual", "slug":"variacao-percentual", "category":"Matemática",
        "title":"Calculadora de Variação Percentual", "description":"Calcule o aumento ou a redução percentual entre dois valores.",
        "kind":"two-number", "labels":["Valor inicial", "Valor final"], "placeholders":["Ex.: 100", "Ex.: 125"],
        "formula":"pct_change", "button":"Calcular variação",
        "intro":"Compare um valor inicial com um valor final e veja a variação percentual entre eles.",
        "example":"Exemplo: de 100 para 125 = aumento de 25%."
    },
    {
        "id":"desconto", "slug":"desconto", "category":"Matemática",
        "title":"Calculadora de Desconto", "description":"Calcule o valor final e quanto você economiza após aplicar um desconto percentual.",
        "kind":"two-number", "labels":["Preço original", "Desconto (%)"], "placeholders":["Ex.: 200", "Ex.: 10"],
        "formula":"discount", "button":"Calcular desconto",
        "intro":"Informe o preço original e a porcentagem de desconto para obter o valor final e a economia.",
        "example":"Exemplo: R$ 200 com 10% de desconto = R$ 180."
    },
    {
        "id":"acrescimo", "slug":"acrescimo", "category":"Matemática",
        "title":"Calculadora de Acréscimo", "description":"Calcule o valor final depois de aplicar um acréscimo percentual.",
        "kind":"two-number", "labels":["Valor original", "Acréscimo (%)"], "placeholders":["Ex.: 200", "Ex.: 10"],
        "formula":"increase", "button":"Calcular acréscimo",
        "intro":"Informe um valor e a porcentagem de acréscimo para calcular o novo total.",
        "example":"Exemplo: R$ 200 com acréscimo de 10% = R$ 220."
    },
    {
        "id":"regra-de-tres", "slug":"regra-de-tres", "category":"Matemática",
        "title":"Calculadora de Regra de Três", "description":"Resolva uma regra de três simples informando três valores conhecidos.",
        "kind":"three-number", "labels":["A", "B", "C"], "placeholders":["Ex.: 2", "Ex.: 10", "Ex.: 5"],
        "formula":"rule3", "button":"Resolver regra de três",
        "intro":"Para a proporção A/B = C/X, informe A, B e C. A calculadora encontra X.",
        "example":"Exemplo: 2 está para 10 assim como 5 está para 25."
    },
    {
        "id":"media", "slug":"media", "category":"Matemática",
        "title":"Calculadora de Média", "description":"Calcule a média aritmética de uma lista de números.",
        "kind":"number-list", "labels":["Números"], "placeholders":["Ex.: 10, 15, 20, 25"],
        "formula":"average", "button":"Calcular média",
        "intro":"Digite números separados por vírgula, ponto e vírgula, espaço ou quebra de linha.",
        "example":"Exemplo: 10, 15, 20 e 25 têm média 17,5."
    },
    {
        "id":"dividir-conta", "slug":"dividir-conta", "category":"Matemática",
        "title":"Calculadora para Dividir Conta", "description":"Divida um valor igualmente entre várias pessoas.",
        "kind":"two-number", "labels":["Valor total", "Número de pessoas"], "placeholders":["Ex.: 180", "Ex.: 4"],
        "formula":"split_bill", "button":"Dividir conta",
        "intro":"Informe o valor total e quantas pessoas participarão da divisão.",
        "example":"Exemplo: R$ 180 entre 4 pessoas = R$ 45 por pessoa."
    },
    {
        "id":"juros-simples", "slug":"juros-simples", "category":"Matemática",
        "title":"Calculadora de Juros Simples", "description":"Calcule juros simples a partir de capital, taxa e período.",
        "kind":"three-number", "labels":["Capital", "Taxa por período (%)", "Número de períodos"], "placeholders":["Ex.: 1000", "Ex.: 2", "Ex.: 6"],
        "formula":"simple_interest", "button":"Calcular juros",
        "intro":"Cálculo matemático de juros simples: juros = capital × taxa × períodos.",
        "example":"Exemplo: 1.000 a 2% por 6 períodos gera 120 de juros."
    },
    {
        "id":"dias-entre-datas", "slug":"dias-entre-datas", "category":"Datas",
        "title":"Dias Entre Duas Datas", "description":"Calcule quantos dias existem entre duas datas.",
        "kind":"two-date", "labels":["Data inicial", "Data final"], "placeholders":["", ""],
        "formula":"days_between", "button":"Calcular diferença",
        "intro":"Escolha duas datas para calcular a diferença absoluta em dias.",
        "example":"Útil para prazos, intervalos e planejamento."
    },
    {
        "id":"somar-dias", "slug":"somar-dias", "category":"Datas",
        "title":"Somar Dias a uma Data", "description":"Descubra a data resultante ao adicionar ou subtrair dias.",
        "kind":"date-number", "labels":["Data", "Dias (use negativo para subtrair)"], "placeholders":["", "Ex.: 30"],
        "formula":"add_days", "button":"Calcular nova data",
        "intro":"Escolha uma data e informe quantos dias deseja adicionar. Valores negativos subtraem dias.",
        "example":"Exemplo: adicionar 30 dias a uma data para encontrar um prazo futuro."
    },
    {
        "id":"idade", "slug":"idade", "category":"Datas",
        "title":"Calculadora de Idade", "description":"Calcule idade em anos completos a partir da data de nascimento.",
        "kind":"one-date", "labels":["Data de nascimento"], "placeholders":[""],
        "formula":"age", "button":"Calcular idade",
        "intro":"Informe a data de nascimento para calcular a idade atual em anos completos usando a data do dispositivo.",
        "example":"O cálculo considera se o aniversário deste ano já ocorreu."
    },
    {
        "id":"horas-para-minutos", "slug":"horas-para-minutos", "category":"Conversão",
        "title":"Converter Horas em Minutos", "description":"Converta horas para minutos instantaneamente.",
        "kind":"one-number", "labels":["Horas"], "placeholders":["Ex.: 2,5"],
        "formula":"hours_minutes", "button":"Converter",
        "intro":"Digite a quantidade de horas, inclusive valores decimais, para converter em minutos.",
        "example":"Exemplo: 2,5 horas = 150 minutos."
    },
    {
        "id":"minutos-para-horas", "slug":"minutos-para-horas", "category":"Conversão",
        "title":"Converter Minutos em Horas", "description":"Converta minutos para horas e minutos.",
        "kind":"one-number", "labels":["Minutos"], "placeholders":["Ex.: 150"],
        "formula":"minutes_hours", "button":"Converter",
        "intro":"Digite a quantidade de minutos para visualizar o equivalente em horas decimais e em horas/minutos.",
        "example":"Exemplo: 150 minutos = 2 horas e 30 minutos."
    },
    {
        "id":"contador-palavras", "slug":"contador-palavras", "category":"Texto e dados",
        "title":"Contador de Palavras", "description":"Conte palavras, caracteres e linhas de qualquer texto.",
        "kind":"textarea", "labels":["Texto"], "placeholders":["Cole ou digite seu texto aqui..."],
        "formula":"word_count", "button":"Contar",
        "intro":"Cole um texto para contar palavras, caracteres com e sem espaços e número de linhas.",
        "example":"O texto é processado localmente no navegador."
    },
    {
        "id":"remover-duplicados", "slug":"remover-duplicados", "category":"Texto e dados",
        "title":"Remover Linhas Duplicadas", "description":"Remova linhas repetidas de uma lista preservando a primeira ocorrência.",
        "kind":"textarea-output", "labels":["Lista"], "placeholders":["Uma linha por item..."],
        "formula":"dedupe", "button":"Remover duplicados",
        "intro":"Cole uma lista com um item por linha. A ferramenta remove repetições e preserva a ordem original.",
        "example":"Ideal para listas, códigos, nomes e pequenas limpezas de dados."
    },
    {
        "id":"ordenar-linhas", "slug":"ordenar-linhas", "category":"Texto e dados",
        "title":"Ordenar Linhas em Ordem Alfabética", "description":"Ordene uma lista de linhas de A a Z ou Z a A.",
        "kind":"textarea-sort", "labels":["Lista"], "placeholders":["Uma linha por item..."],
        "formula":"sort_lines", "button":"Ordenar A → Z",
        "intro":"Cole uma lista e ordene suas linhas alfabeticamente sem enviar o conteúdo para um servidor.",
        "example":"Também é possível inverter a ordem depois do primeiro resultado."
    },
    {
        "id":"maiusculas-minusculas", "slug":"maiusculas-minusculas", "category":"Texto e dados",
        "title":"Converter Maiúsculas e Minúsculas", "description":"Transforme texto em maiúsculas, minúsculas ou formato de título.",
        "kind":"textarea-case", "labels":["Texto"], "placeholders":["Digite ou cole o texto..."],
        "formula":"case", "button":"MAIÚSCULAS",
        "intro":"Converta rapidamente a capitalização do texto no próprio navegador.",
        "example":"Há opções para maiúsculas, minúsculas e iniciais em maiúscula."
    },
    {
        "id":"remover-espacos", "slug":"remover-espacos", "category":"Texto e dados",
        "title":"Remover Espaços Extras", "description":"Limpe espaços repetidos, recuos e linhas vazias extras de um texto.",
        "kind":"textarea-output", "labels":["Texto"], "placeholders":["Cole o texto para limpar..."],
        "formula":"clean_spaces", "button":"Limpar texto",
        "intro":"Reduza espaços repetidos e normalize quebras de linha sem alterar o conteúdo principal.",
        "example":"Útil para textos copiados de PDFs, páginas e sistemas antigos."
    },
    {
        "id":"formatar-json", "slug":"formatar-json", "category":"Texto e dados",
        "title":"Formatador de JSON", "description":"Valide, formate e compacte JSON diretamente no navegador.",
        "kind":"textarea-json", "labels":["JSON"], "placeholders":["{\n  \"exemplo\": true\n}"],
        "formula":"json_format", "button":"Formatar JSON",
        "intro":"Cole um JSON para validar e formatar com indentação legível. O conteúdo não sai do seu navegador.",
        "example":"Erros de sintaxe são mostrados sem alterar o texto original."
    },
    {
        "id":"csv-para-json", "slug":"csv-para-json", "category":"Texto e dados",
        "title":"Converter CSV para JSON", "description":"Converta CSV simples com cabeçalho para JSON no navegador.",
        "kind":"textarea-output", "labels":["CSV"], "placeholders":["nome,idade\nAna,30\nCarlos,42"],
        "formula":"csv_json", "button":"Converter para JSON",
        "intro":"Cole um CSV com cabeçalho na primeira linha para gerar uma lista de objetos JSON.",
        "example":"A ferramenta reconhece vírgula, ponto e vírgula ou tabulação como separadores simples."
    },
]


def esc(s):
    return html.escape(str(s), quote=True)


def field_html(tool):
    kind = tool["kind"]
    labels = tool["labels"]
    ph = tool["placeholders"]
    def num(i):
        return f'<label>{esc(labels[i])}<input inputmode="decimal" type="text" data-input="{i}" placeholder="{esc(ph[i])}" autocomplete="off"></label>'
    def date(i):
        return f'<label>{esc(labels[i])}<input type="date" data-input="{i}"></label>'
    if kind == "one-number": return num(0)
    if kind == "two-number": return num(0)+num(1)
    if kind == "three-number": return num(0)+num(1)+num(2)
    if kind == "two-date": return date(0)+date(1)
    if kind == "date-number": return date(0)+num(1)
    if kind == "one-date": return date(0)
    if kind == "number-list":
        return f'<label>{esc(labels[0])}<textarea data-input="0" rows="6" placeholder="{esc(ph[0])}"></textarea></label>'
    if kind.startswith("textarea"):
        return f'<label>{esc(labels[0])}<textarea data-input="0" rows="10" placeholder="{esc(ph[0])}"></textarea></label>'
    raise ValueError(kind)


def extra_buttons(tool):
    if tool["kind"] == "textarea-sort":
        return '<button class="secondary" type="button" data-action="sort-desc">Ordenar Z → A</button>'
    if tool["kind"] == "textarea-case":
        return '<button class="secondary" type="button" data-action="lower">minúsculas</button><button class="secondary" type="button" data-action="title">Iniciais Maiúsculas</button>'
    if tool["kind"] == "textarea-json":
        return '<button class="secondary" type="button" data-action="json-minify">Compactar JSON</button>'
    return ''


def tool_page(tool):
    canonical = f"{BASE_URL}/{tool['slug']}/"
    schema = {
        "@context":"https://schema.org",
        "@type":"WebApplication",
        "name":tool["title"],
        "applicationCategory":"UtilitiesApplication",
        "operatingSystem":"Any",
        "isAccessibleForFree": True,
        "url": canonical,
        "description":tool["description"],
    }
    related = [t for t in TOOLS if t["category"] == tool["category"] and t["id"] != tool["id"]][:4]
    related_html = ''.join(f'<a class="related-card" href="../{esc(t["slug"])}/"><strong>{esc(t["title"])}</strong><span>{esc(t["description"])}</span></a>' for t in related)
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(tool['title'])} — {SITE_NAME}</title>
<meta name="description" content="{esc(tool['description'])}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="index,follow">
<meta property="og:title" content="{esc(tool['title'])}">
<meta property="og:description" content="{esc(tool['description'])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical)}">
<link rel="stylesheet" href="../assets/styles.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body data-tool="{esc(tool['formula'])}">
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="../">{SITE_NAME}</a><nav><a href="../#ferramentas">Ferramentas</a><a href="../privacidade/">Privacidade</a></nav></div></header>
<main>
<section class="hero tool-hero"><div class="wrap narrow"><div class="eyebrow">{esc(tool['category'])}</div><h1>{esc(tool['title'])}</h1><p>{esc(tool['intro'])}</p></div></section>
<section class="wrap narrow">
<div class="calculator" id="calculator">
<div class="fields">{field_html(tool)}</div>
<div class="actions"><button class="primary" type="button" data-action="calculate">{esc(tool['button'])}</button>{extra_buttons(tool)}</div>
<div class="result" data-result aria-live="polite"><span class="result-label">Resultado</span><strong>Preencha os campos acima.</strong></div>
</div>
<div class="info-card"><h2>Como funciona</h2><p>{esc(tool['example'])}</p><p>Esta ferramenta executa o cálculo localmente no seu dispositivo. Não é necessário criar conta.</p></div>
</section>
<section class="wrap narrow related"><h2>Ferramentas relacionadas</h2><div class="related-grid">{related_html}</div></section>
</main>
<footer><div class="wrap footer-inner"><span>© <span data-year></span> {SITE_NAME}</span><span>Ferramentas simples, rápidas e gratuitas.</span></div></footer>
<script src="../assets/app.js" defer></script>
</body></html>'''


def home_page():
    cats = []
    for t in TOOLS:
        if t["category"] not in cats: cats.append(t["category"])
    sections = []
    for c in cats:
        cards = ''.join(f'''<a class="tool-card" href="{esc(t['slug'])}/"><span class="card-category">{esc(c)}</span><h3>{esc(t['title'])}</h3><p>{esc(t['description'])}</p><span class="card-link">Abrir ferramenta →</span></a>''' for t in TOOLS if t["category"] == c)
        sections.append(f'<section class="tool-category"><h2>{esc(c)}</h2><div class="tool-grid">{cards}</div></section>')
    schema = {
        "@context":"https://schema.org","@type":"WebSite","name":SITE_NAME,"url":f"{BASE_URL}/",
        "description":"Ferramentas online gratuitas para cálculos, datas, conversões, texto e dados."
    }
    return f'''<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_NAME} — Ferramentas online gratuitas</title>
<meta name="description" content="Ferramentas online gratuitas para cálculos, datas, conversões, texto e dados. Sem cadastro e com processamento local sempre que possível.">
<link rel="canonical" href="{esc(BASE_URL)}/"><meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/styles.css"><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head><body>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="./">{SITE_NAME}</a><nav><a href="#ferramentas">Ferramentas</a><a href="privacidade/">Privacidade</a></nav></div></header>
<main>
<section class="hero"><div class="wrap"><div class="eyebrow">Rápido • Gratuito • Sem cadastro</div><h1>Ferramentas úteis que resolvem pequenas tarefas em segundos.</h1><p class="lead">Cálculos, datas, conversões e utilitários de texto. A maioria funciona inteiramente no seu navegador.</p><a class="cta" href="#ferramentas">Ver ferramentas</a></div></section>
<section id="ferramentas" class="wrap tools-section"><div class="section-heading"><span>{len(TOOLS)} ferramentas disponíveis</span><h2>Escolha uma ferramenta</h2></div>{''.join(sections)}</section>
<section class="wrap trust"><div><strong>Sem conta</strong><span>Abra e use.</span></div><div><strong>Leve</strong><span>Sem frameworks pesados.</span></div><div><strong>Privacidade</strong><span>Processamento local sempre que possível.</span></div></section>
</main>
<footer><div class="wrap footer-inner"><span>© <span data-year></span> {SITE_NAME}</span><span>Ferramentas simples, rápidas e gratuitas.</span></div></footer>
<script src="assets/app.js" defer></script></body></html>'''

CSS = r'''
:root{--bg:#f6f7fb;--surface:#fff;--ink:#16181d;--muted:#666d78;--line:#e4e7ec;--accent:#1f64ff;--accent2:#174bc1;--soft:#eef4ff;--radius:18px;--shadow:0 12px 34px rgba(20,35,70,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}.wrap{width:min(1120px,calc(100% - 32px));margin:auto}.narrow{width:min(760px,calc(100% - 32px))}.site-header{position:sticky;top:0;z-index:20;background:rgba(246,247,251,.9);backdrop-filter:blur(14px);border-bottom:1px solid rgba(228,231,236,.8)}.header-inner{height:66px;display:flex;align-items:center;justify-content:space-between}.brand{font-weight:850;color:var(--ink);text-decoration:none;letter-spacing:-.02em}.site-header nav{display:flex;gap:20px}.site-header nav a{font-size:.94rem;color:var(--muted);text-decoration:none}.site-header nav a:hover{color:var(--ink)}.hero{padding:86px 0 58px;background:radial-gradient(circle at 20% 10%,#e7efff 0,rgba(231,239,255,0) 35%)}.hero h1{max-width:850px;font-size:clamp(2.4rem,6vw,5.25rem);line-height:1.02;letter-spacing:-.055em;margin:.4rem 0 1.2rem}.tool-hero{padding:62px 0 30px}.tool-hero h1{font-size:clamp(2.1rem,6vw,4rem)}.tool-hero p{font-size:1.08rem;color:var(--muted)}.eyebrow{font-weight:800;text-transform:uppercase;letter-spacing:.1em;font-size:.73rem;color:var(--accent)}.lead{max-width:700px;color:var(--muted);font-size:1.16rem}.cta,.primary{display:inline-flex;align-items:center;justify-content:center;border:0;background:var(--accent);color:white;text-decoration:none;font-weight:800;padding:13px 18px;border-radius:12px;cursor:pointer;transition:.15s}.cta:hover,.primary:hover{background:var(--accent2);transform:translateY(-1px)}.tools-section{padding:52px 0 34px}.section-heading span{color:var(--accent);font-weight:800;font-size:.85rem}.section-heading h2,.tool-category h2,.related h2{font-size:clamp(1.55rem,3vw,2.1rem);letter-spacing:-.03em}.tool-category{margin-top:48px}.tool-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.tool-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;text-decoration:none;color:var(--ink);box-shadow:0 1px 0 rgba(20,35,70,.01);transition:.18s}.tool-card:hover{transform:translateY(-3px);box-shadow:var(--shadow);border-color:#cfd7e8}.tool-card h3{margin:8px 0 8px;letter-spacing:-.02em}.tool-card p{color:var(--muted);font-size:.94rem;min-height:67px}.card-category{font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--accent)}.card-link{font-size:.9rem;font-weight:800;color:var(--accent)}.calculator{background:var(--surface);border:1px solid var(--line);border-radius:24px;padding:26px;box-shadow:var(--shadow);margin:10px 0 26px}.fields{display:grid;gap:16px}.fields label{display:grid;gap:7px;font-weight:760;font-size:.93rem}.fields input,.fields textarea{width:100%;border:1px solid #d8dce4;background:#fbfcfe;border-radius:12px;padding:13px 14px;font:inherit;color:var(--ink);outline:none}.fields textarea{resize:vertical;min-height:130px}.fields input:focus,.fields textarea:focus{border-color:#9bb7ff;box-shadow:0 0 0 4px rgba(31,100,255,.09)}.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.secondary{border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:750;padding:12px 15px;border-radius:12px;cursor:pointer}.secondary:hover{background:#f6f7fb}.result{margin-top:20px;background:var(--soft);border:1px solid #d8e5ff;border-radius:14px;padding:17px;display:grid;gap:4px}.result-label{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:#4d6cae;font-weight:850}.result strong{font-size:1.12rem;white-space:pre-wrap;overflow-wrap:anywhere}.result.error{background:#fff1f1;border-color:#ffd1d1}.result.error .result-label{color:#a43e3e}.info-card{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:22px;margin:20px 0}.info-card h2{margin-top:0;letter-spacing:-.02em}.info-card p{color:var(--muted)}.related{padding:18px 0 68px}.related-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.related-card{background:#fff;border:1px solid var(--line);border-radius:15px;padding:16px;text-decoration:none;color:var(--ink);display:grid;gap:4px}.related-card span{font-size:.9rem;color:var(--muted)}.trust{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:32px 0 76px}.trust div{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:20px;display:grid}.trust span{color:var(--muted);font-size:.92rem}footer{border-top:1px solid var(--line);padding:28px 0;background:#fff}.footer-inner{display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-size:.9rem}.privacy{padding:62px 0 80px}.privacy h1{font-size:clamp(2.1rem,5vw,3.6rem);letter-spacing:-.04em}.privacy h2{margin-top:34px}.privacy p{color:var(--muted)}
@media(max-width:800px){.tool-grid{grid-template-columns:1fr 1fr}.hero{padding-top:58px}.hero h1{font-size:clamp(2.4rem,12vw,4.2rem)}}@media(max-width:560px){.tool-grid,.related-grid,.trust{grid-template-columns:1fr}.site-header nav a:first-child{display:none}.calculator{padding:18px}.footer-inner{flex-direction:column}.tool-card p{min-height:auto}}
'''

JS = r'''
(() => {
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
  const root = document.body;
  const tool = root.dataset.tool;
  if (!tool) return;
  const result = $('[data-result]');
  const inputs = $$('[data-input]');
  const val = i => (inputs[i]?.value ?? '').trim();
  const num = i => {
    let s = val(i).replace(/\s/g,'');
    if (s.includes(',') && s.includes('.')) {
      if (s.lastIndexOf(',') > s.lastIndexOf('.')) s = s.replace(/\./g,'').replace(',','.');
      else s = s.replace(/,/g,'');
    } else s = s.replace(',','.');
    const n = Number(s);
    if (!Number.isFinite(n)) throw new Error('Informe um número válido.');
    return n;
  };
  const fmt = n => new Intl.NumberFormat('pt-BR',{maximumFractionDigits:8}).format(n);
  const money = n => new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(n);
  const show = text => { result.classList.remove('error'); result.innerHTML = `<span class="result-label">Resultado</span><strong>${escapeHtml(text)}</strong>`; };
  const fail = err => { result.classList.add('error'); result.innerHTML = `<span class="result-label">Verifique os dados</span><strong>${escapeHtml(err.message || String(err))}</strong>`; };
  const escapeHtml = s => String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const dateLocal = s => { if(!s) throw new Error('Selecione uma data.'); const [y,m,d]=s.split('-').map(Number); return new Date(y,m-1,d,12,0,0); };
  const dateFmt = d => new Intl.DateTimeFormat('pt-BR',{dateStyle:'long'}).format(d);
  const lines = s => s.replace(/\r/g,'').split('\n');

  const calculate = (action='calculate') => {
    try {
      switch(tool){
        case 'pct_of': { const a=num(0), b=num(1); show(`${fmt(a)}% de ${fmt(b)} = ${fmt(a*b/100)}`); break; }
        case 'pct_change': { const a=num(0), b=num(1); if(a===0) throw new Error('O valor inicial não pode ser zero.'); const p=(b-a)/Math.abs(a)*100; show(`${p>=0?'Aumento':'Redução'} de ${fmt(Math.abs(p))}%`); break; }
        case 'discount': { const price=num(0), pct=num(1); const saved=price*pct/100; show(`Valor final: ${money(price-saved)}\nEconomia: ${money(saved)}`); break; }
        case 'increase': { const value=num(0), pct=num(1); const inc=value*pct/100; show(`Valor final: ${money(value+inc)}\nAcréscimo: ${money(inc)}`); break; }
        case 'rule3': { const a=num(0), b=num(1), c=num(2); if(a===0) throw new Error('A não pode ser zero.'); show(`X = ${fmt((b*c)/a)}`); break; }
        case 'average': { const arr=val(0).split(/[;,\s]+/).map(x=>x.trim()).filter(Boolean).map(x=>Number(x.replace(',','.'))); if(!arr.length||arr.some(x=>!Number.isFinite(x))) throw new Error('Informe uma lista válida de números.'); show(`Média = ${fmt(arr.reduce((a,b)=>a+b,0)/arr.length)}\nQuantidade de valores: ${arr.length}`); break; }
        case 'split_bill': { const total=num(0), people=num(1); if(people<=0||!Number.isInteger(people)) throw new Error('O número de pessoas deve ser um inteiro maior que zero.'); show(`${money(total/people)} por pessoa`); break; }
        case 'simple_interest': { const capital=num(0), rate=num(1), periods=num(2); const interest=capital*(rate/100)*periods; show(`Juros: ${money(interest)}\nMontante: ${money(capital+interest)}`); break; }
        case 'days_between': { const a=dateLocal(val(0)), b=dateLocal(val(1)); show(`${Math.round(Math.abs(b-a)/86400000)} dias`); break; }
        case 'add_days': { const d=dateLocal(val(0)), days=num(1); if(!Number.isInteger(days)) throw new Error('Use um número inteiro de dias.'); d.setDate(d.getDate()+days); show(dateFmt(d)); break; }
        case 'age': { const birth=dateLocal(val(0)), now=new Date(); if(birth>now) throw new Error('A data de nascimento não pode estar no futuro.'); let age=now.getFullYear()-birth.getFullYear(); const before=now.getMonth()<birth.getMonth()||(now.getMonth()===birth.getMonth()&&now.getDate()<birth.getDate()); if(before) age--; show(`${age} anos completos`); break; }
        case 'hours_minutes': { const h=num(0); show(`${fmt(h*60)} minutos`); break; }
        case 'minutes_hours': { const m=num(0); const sign=m<0?'-':''; const abs=Math.abs(m); const h=Math.floor(abs/60), rem=Math.round((abs-h*60)*1e8)/1e8; show(`${fmt(m/60)} horas\n${sign}${h} h ${fmt(rem)} min`); break; }
        case 'word_count': { const s=val(0); const words=(s.match(/\S+/g)||[]).length; const chars=s.length; const noSpaces=s.replace(/\s/g,'').length; const lineCount=s?lines(s).length:0; show(`Palavras: ${words}\nCaracteres: ${chars}\nCaracteres sem espaços: ${noSpaces}\nLinhas: ${lineCount}`); break; }
        case 'dedupe': { const out=[...new Set(lines(val(0)))].join('\n'); show(out || 'Nenhuma linha informada.'); break; }
        case 'sort_lines': { const arr=lines(val(0)).filter((x,i,a)=>!(a.length===1&&x==='')); const desc=action==='sort-desc'; arr.sort((a,b)=>a.localeCompare(b,'pt-BR',{sensitivity:'base'})); if(desc) arr.reverse(); show(arr.join('\n') || 'Nenhuma linha informada.'); break; }
        case 'case': { let s=val(0); if(action==='lower') s=s.toLocaleLowerCase('pt-BR'); else if(action==='title') s=s.toLocaleLowerCase('pt-BR').replace(/(^|\s)\S/g,m=>m.toLocaleUpperCase('pt-BR')); else s=s.toLocaleUpperCase('pt-BR'); show(s || 'Nenhum texto informado.'); break; }
        case 'clean_spaces': { const s=val(0).replace(/[ \t]+/g,' ').replace(/ *\n */g,'\n').replace(/\n{3,}/g,'\n\n').trim(); show(s || 'Nenhum texto informado.'); break; }
        case 'json_format': { const obj=JSON.parse(val(0)); show(JSON.stringify(obj,null,action==='json-minify'?0:2)); break; }
        case 'csv_json': { const raw=val(0).replace(/\r/g,'').trim(); if(!raw) throw new Error('Cole um CSV para converter.'); const rows=raw.split('\n'); const first=rows[0]; const candidates=[',',';','\t']; const delim=candidates.sort((a,b)=>first.split(b).length-first.split(a).length)[0]; const parse=line=>{ const out=[]; let cur='', q=false; for(let i=0;i<line.length;i++){ const c=line[i]; if(c==='"'){ if(q&&line[i+1]==='"'){cur+='"';i++;} else q=!q; } else if(c===delim&&!q){out.push(cur);cur='';} else cur+=c; } out.push(cur); return out; }; const headers=parse(rows[0]).map(x=>x.trim()); if(headers.length<2) throw new Error('Não foi possível identificar as colunas do CSV.'); const data=rows.slice(1).filter(Boolean).map(r=>{ const cells=parse(r); return Object.fromEntries(headers.map((h,i)=>[h,cells[i]??''])); }); show(JSON.stringify(data,null,2)); break; }
        default: throw new Error('Ferramenta não configurada.');
      }
    } catch(e){ fail(e); }
  };
  $$('[data-action]').forEach(btn => btn.addEventListener('click', () => calculate(btn.dataset.action)));
  inputs.forEach(el => el.addEventListener('keydown', e => { if(e.key==='Enter' && el.tagName!=='TEXTAREA'){ e.preventDefault(); calculate(); } }));
})();
'''

PRIVACY = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacidade — {SITE_NAME}</title><meta name="description" content="Política de privacidade do {SITE_NAME}."><meta name="robots" content="index,follow"><link rel="stylesheet" href="../assets/styles.css"></head><body><header class="site-header"><div class="wrap header-inner"><a class="brand" href="../">{SITE_NAME}</a><nav><a href="../#ferramentas">Ferramentas</a></nav></div></header><main class="wrap narrow privacy"><div class="eyebrow">Privacidade</div><h1>Política de privacidade</h1><p>Nesta versão inicial, as ferramentas do {SITE_NAME} executam seus cálculos e transformações diretamente no navegador e não exigem cadastro.</p><h2>Dados inseridos nas ferramentas</h2><p>Os valores e textos digitados são processados localmente pelas páginas desta versão e não são enviados por elas a um servidor de aplicação.</p><h2>Cookies e publicidade</h2><p>Esta versão não inclui anúncios, cookies de publicidade ou ferramentas de análise de terceiros. Se isso mudar, esta página deverá ser atualizada antes da ativação desses serviços.</p><h2>Alterações</h2><p>A política poderá ser atualizada conforme novas funcionalidades forem adicionadas.</p></main><footer><div class="wrap footer-inner"><span>© <span data-year></span> {SITE_NAME}</span><span>Ferramentas simples, rápidas e gratuitas.</span></div></footer><script src="../assets/app.js" defer></script></body></html>'''

README = f'''# {SITE_NAME}

MVP estático com {len(TOOLS)} microferramentas gratuitas. Todo o processamento desta versão ocorre no navegador, sem banco de dados e sem API paga.

## Estrutura

- `index.html`: página inicial.
- `assets/styles.css`: visual compartilhado.
- `assets/app.js`: motor genérico das ferramentas.
- uma pasta por ferramenta, cada uma com seu `index.html`.
- `privacidade/`: política compatível com a versão atual, que não usa analytics nem anúncios.
- `sitemap.xml` e `robots.txt`: arquivos de indexação.
- `build_site.py`: fonte geradora das páginas.
- `.github/workflows/pages.yml`: deploy automático no GitHub Pages.

## Rodar localmente

```bash
python -m http.server 8000
```

Depois abra `http://localhost:8000`.

## Gerar para qualquer URL pública

Defina `SITE_URL` com a URL pública final e execute o gerador:

```bash
SITE_URL=https://exemplo.com python build_site.py
```

No PowerShell:

```powershell
$env:SITE_URL="https://exemplo.com"
python build_site.py
```

## GitHub Pages

O workflow calcula automaticamente a URL `https://USUARIO.github.io/REPOSITORIO`, executa o gerador e publica o site. Para um repositório chamado `fonseca-tools` na conta `davdsmlqnt007-bot`, a URL prevista é:

`https://davdsmlqnt007-bot.github.io/fonseca-tools/`

Depois de criar o repositório público e enviar estes arquivos, abra **Settings → Pages** e selecione **GitHub Actions** como fonte de publicação. A partir daí, cada push em `main` dispara novo deploy.

## Princípio do projeto

O site é propositalmente simples: cada visitante pode usar as ferramentas sem gerar custo de API. A monetização deve ser adicionada apenas depois de haver páginas indexadas e tráfego mensurável.
'''


def build():
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets' / 'styles.css').write_text(CSS.strip()+"\n", encoding='utf-8')
    (ROOT / 'assets' / 'app.js').write_text(JS.strip()+"\n", encoding='utf-8')
    (ROOT / 'index.html').write_text(home_page(), encoding='utf-8')
    for t in TOOLS:
        d=ROOT/t['slug']; d.mkdir(exist_ok=True)
        (d/'index.html').write_text(tool_page(t), encoding='utf-8')
    p=ROOT/'privacidade'; p.mkdir(exist_ok=True); (p/'index.html').write_text(PRIVACY, encoding='utf-8')
    urls=[f'{BASE_URL}/', f'{BASE_URL}/privacidade/']+[f"{BASE_URL}/{t['slug']}/" for t in TOOLS]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{esc(u)}</loc></url>\n' for u in urls)+'</urlset>\n'
    (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n',encoding='utf-8')
    (ROOT/'README.md').write_text(README,encoding='utf-8')
    (ROOT/'tools.json').write_text(json.dumps(TOOLS,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__':
    build()
    print(f'Built {len(TOOLS)} tools at {ROOT}')
