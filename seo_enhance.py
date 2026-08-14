from pathlib import Path
import json
import html

ROOT = Path(__file__).resolve().parent
SITE_URL = __import__('os').environ.get('SITE_URL', 'https://fonseca-labs.github.io/fonseca-tools').rstrip('/')
TOOLS = json.loads((ROOT / 'tools.json').read_text(encoding='utf-8'))

METHODS = {
    'pct_of': ('Fórmula', 'resultado = (porcentagem ÷ 100) × valor', 'A porcentagem pode ser maior que 100% ou negativa se isso fizer sentido no seu cálculo.'),
    'pct_change': ('Fórmula', 'variação (%) = ((valor final − valor inicial) ÷ |valor inicial|) × 100', 'O valor inicial não pode ser zero, porque a variação percentual ficaria indefinida.'),
    'discount': ('Fórmula', 'valor final = preço original × (1 − desconto ÷ 100)', 'A ferramenta também mostra quanto foi economizado em relação ao preço original.'),
    'increase': ('Fórmula', 'valor final = valor original × (1 + acréscimo ÷ 100)', 'O acréscimo é calculado sobre o valor original informado.'),
    'rule3': ('Fórmula', 'X = (B × C) ÷ A', 'A ferramenta considera a proporção A/B = C/X. O valor A não pode ser zero.'),
    'average': ('Método', 'soma de todos os valores ÷ quantidade de valores', 'Os números podem ser separados por vírgula, ponto e vírgula, espaço ou quebra de linha.'),
    'split_bill': ('Fórmula', 'valor por pessoa = total ÷ número de pessoas', 'O número de pessoas precisa ser um inteiro maior que zero.'),
    'simple_interest': ('Fórmula', 'juros = capital × (taxa ÷ 100) × períodos', 'A taxa e o número de períodos precisam estar na mesma unidade de tempo, por exemplo taxa mensal com períodos em meses.'),
    'days_between': ('Método', 'diferença absoluta entre as duas datas em dias corridos', 'O resultado não diferencia dias úteis, fins de semana ou feriados.'),
    'add_days': ('Método', 'a data inicial é deslocada pelo número inteiro de dias informado', 'Valores negativos subtraem dias. A contagem usa dias corridos.'),
    'age': ('Método', 'anos completos entre a data de nascimento e hoje, considerando se o aniversário já ocorreu', 'O cálculo usa a data configurada no seu dispositivo.'),
    'hours_minutes': ('Fórmula', 'minutos = horas × 60', 'Horas decimais são aceitas; por exemplo, 2,5 horas equivalem a 150 minutos.'),
    'minutes_hours': ('Fórmula', 'horas decimais = minutos ÷ 60', 'Além das horas decimais, a ferramenta separa o resultado em horas e minutos.'),
    'word_count': ('Método', 'palavras são grupos de caracteres separados por espaços ou quebras; caracteres e linhas são contados diretamente', 'A contagem é adequada para textos comuns, mas regras editoriais específicas podem contar palavras de forma diferente.'),
    'dedupe': ('Método', 'cada linha é comparada literalmente e apenas a primeira ocorrência é preservada', 'Linhas que diferem por maiúsculas, espaços ou acentos são consideradas diferentes.'),
    'sort_lines': ('Método', 'as linhas são ordenadas alfabeticamente no navegador', 'A ordenação atua sobre cada linha completa e permite alternar entre A→Z e Z→A.'),
    'case': ('Método', 'o texto é transformado para maiúsculas, minúsculas ou iniciais em maiúscula', 'A opção de título é uma transformação simples e pode não seguir regras editoriais específicas para preposições e siglas.'),
    'clean_spaces': ('Método', 'espaços repetidos e quebras excedentes são normalizados sem enviar o texto para um servidor', 'Revise o resultado se o texto original depender de espaçamento proposital para formatação.'),
    'json_format': ('Método', 'o navegador valida com JSON.parse e gera a saída formatada ou compactada com JSON.stringify', 'A entrada precisa ser JSON válido; comentários e vírgulas finais não fazem parte do padrão JSON.'),
    'csv_json': ('Método', 'a primeira linha é usada como cabeçalho e as linhas seguintes viram objetos JSON', 'É uma conversão de CSV simples. Arquivos complexos com separadores dentro de campos entre aspas podem exigir uma ferramenta especializada.'),
    'business_days_between': ('Método', 'conta somente segunda a sexta após a data inicial e até a data final', 'Feriados não são considerados; para prazos legais ou trabalhistas, confirme o calendário aplicável.'),
    'add_business_days': ('Método', 'avança ou recua a data contando apenas segunda a sexta', 'Feriados não são considerados nesta versão.'),
    'weeks_between': ('Fórmula', 'semanas decimais = dias corridos ÷ 7', 'A ferramenta também mostra semanas completas e dias restantes.'),
    'days_until': ('Método', 'compara a data alvo com a data de hoje no dispositivo', 'O resultado usa dias corridos e pode ser positivo, zero ou indicar quantos dias já se passaram.'),
    'time_difference': ('Método', 'subtrai o horário inicial do final; se o final for menor, considera que ocorreu no dia seguinte', 'A ferramenta calcula uma diferença de até 24 horas e não usa fuso horário.'),
    'decimal_hours_to_hm': ('Fórmula', 'minutos = parte decimal das horas × 60', 'Exemplo: 0,5 hora corresponde a 30 minutos.'),
    'original_before_discount': ('Fórmula', 'preço original = preço final ÷ (1 − desconto ÷ 100)', 'O desconto precisa ser menor que 100% para que exista um preço original finito.'),
    'total_from_part_pct': ('Fórmula', 'total = valor da parte ÷ (porcentagem ÷ 100)', 'A porcentagem precisa ser maior que zero.'),
    'successive_discounts': ('Fórmula', 'final = preço × (1 − d1/100) × (1 − d2/100)', 'Descontos sucessivos não são somados diretamente porque o segundo incide sobre um valor já reduzido.'),
    'original_before_increase': ('Fórmula', 'valor original = valor final ÷ (1 + acréscimo ÷ 100)', 'O cálculo desfaz o percentual aplicado ao valor original.'),
    'worked_hours_break': ('Método', 'jornada líquida = diferença entre saída e entrada − intervalo', 'Se a saída for anterior à entrada, considera-se virada de dia. O intervalo não pode ser maior que a jornada bruta.'),
    'hm_to_decimal': ('Fórmula', 'horas decimais = horas + (minutos ÷ 60)', 'Os minutos devem ficar entre 0 e 59.'),
    'age_in_days': ('Método', 'diferença em dias corridos completos entre a data de nascimento e hoje', 'O cálculo usa a data do dispositivo e não representa idade legal em contextos com regras próprias.'),
    'months_between': ('Método', 'conta meses completos de calendário e depois os dias restantes', 'Como os meses têm durações diferentes, o valor aproximado em meses decimais é apenas uma referência.'),
    'add_months': ('Método', 'adiciona ou subtrai meses de calendário preservando o dia quando possível', 'Se o mês de destino for mais curto, a data é ajustada para o último dia válido desse mês.'),
    'kmh_to_ms': ('Fórmula', 'm/s = km/h ÷ 3,6', 'A conversão é matemática e não depende de distância, tempo de percurso ou condições de movimento.'),
    'ms_to_kmh': ('Fórmula', 'km/h = m/s × 3,6', 'A conversão é o inverso exato de km/h para m/s.'),
    'part_as_percent': ('Fórmula', 'porcentagem = (parte ÷ total) × 100', 'O valor total não pode ser zero.'),
    'profit_margin': ('Fórmula', 'lucro = venda − custo; margem (%) = lucro ÷ preço de venda × 100', 'Margem sobre a venda é diferente de markup sobre o custo. Custos adicionais não informados não entram no cálculo.'),
    'markup_price': ('Fórmula', 'preço de venda = custo × (1 + markup ÷ 100)', 'Markup é aplicado sobre o custo. A margem resultante sobre a venda será diferente do percentual de markup.'),
}


def esc(value):
    return html.escape(str(value), quote=True)


def seo_block(tool):
    label, method, limitation = METHODS[tool['formula']]
    labels = tool.get('labels') or []
    inputs = ', '.join(labels)
    return f'''<section class="seo-content" data-seo-content>
  <div class="info-card seo-section">
    <h2>Como calcular</h2>
    <p>{esc(tool['intro'])}</p>
    <ol class="steps">
      <li>Preencha os campos: <strong>{esc(inputs)}</strong>.</li>
      <li>Clique em <strong>{esc(tool['button'])}</strong>.</li>
      <li>Confira o resultado e, se necessário, altere os valores para simular outro cenário.</li>
    </ol>
  </div>
  <div class="info-card seo-section">
    <h2>{esc(label)} usada</h2>
    <p class="formula-box">{esc(method)}</p>
    <p><strong>Importante:</strong> {esc(limitation)}</p>
  </div>
  <div class="info-card seo-section">
    <h2>Exemplo prático</h2>
    <p>{esc(tool['example'])}</p>
  </div>
  <div class="info-card seo-section faq-block">
    <h2>Dúvidas comuns</h2>
    <details>
      <summary>O que preciso observar antes de usar o resultado?</summary>
      <p>{esc(limitation)}</p>
    </details>
    <details>
      <summary>Os valores digitados são enviados para algum servidor?</summary>
      <p>Não pelo código desta ferramenta. O cálculo é executado no seu navegador. O Google Analytics, quando aceito, registra métricas gerais de navegação, mas o código da ferramenta não envia os valores digitados ao Analytics.</p>
    </details>
  </div>
</section>'''


def breadcrumb(tool):
    return f'''<nav class="breadcrumb" aria-label="Navegação estrutural"><a href="../">Início</a><span aria-hidden="true">›</span><span>{esc(tool['title'])}</span></nav>'''


def breadcrumb_schema(tool):
    canonical = f"{SITE_URL}/{tool['slug']}/"
    data = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Fonseca Tools', 'item': f'{SITE_URL}/'},
            {'@type': 'ListItem', 'position': 2, 'name': tool['title'], 'item': canonical},
        ],
    }
    return '<script type="application/ld+json" data-breadcrumb-schema>' + json.dumps(data, ensure_ascii=False) + '</script>'


for tool in TOOLS:
    page = ROOT / tool['slug'] / 'index.html'
    text = page.read_text(encoding='utf-8')
    if 'data-seo-content' not in text:
        old = f'<div class="info-card"><h2>Como funciona</h2><p>{esc(tool["example"])}</p><p>Esta ferramenta executa o cálculo localmente no seu dispositivo. Não é necessário criar conta.</p></div>'
        if old not in text:
            raise SystemExit(f'SEO insertion anchor not found for {tool["slug"]}')
        text = text.replace(old, seo_block(tool), 1)
    if 'class="breadcrumb"' not in text:
        hero = '<section class="hero tool-hero"><div class="wrap narrow">'
        text = text.replace(hero, hero + breadcrumb(tool), 1)
    if 'data-breadcrumb-schema' not in text:
        text = text.replace('</head>', breadcrumb_schema(tool) + '\n</head>', 1)
    meta = f'<meta name="description" content="{esc(tool["description"])}">'
    richer = f'<meta name="description" content="{esc(tool["description"] + " Ferramenta grátis, sem cadastro e com processamento no navegador.")}">'
    text = text.replace(meta, richer, 1)
    page.write_text(text, encoding='utf-8')

# Add styles for the new editorial blocks.
styles = ROOT / 'assets' / 'styles.css'
css = styles.read_text(encoding='utf-8')
if '.seo-content{' not in css:
    css += '''\n.breadcrumb{display:flex;align-items:center;gap:8px;margin-bottom:18px;font-size:.9rem;color:var(--muted)}.breadcrumb a{color:var(--accent);text-decoration:none}.breadcrumb a:hover{text-decoration:underline}.seo-content{display:grid;gap:0}.seo-section{margin:16px 0}.seo-section h2{margin-bottom:10px}.steps{padding-left:22px;color:var(--muted)}.steps li+li{margin-top:8px}.formula-box{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#f7f9fc;border:1px solid var(--line);border-radius:12px;padding:14px;color:var(--ink)!important;overflow-wrap:anywhere}.faq-block details{border-top:1px solid var(--line);padding:14px 0}.faq-block details:last-child{border-bottom:1px solid var(--line)}.faq-block summary{font-weight:800;cursor:pointer}.faq-block details p{margin-bottom:0}.about-note{color:var(--muted);font-size:.94rem}\n'''
    styles.write_text(css, encoding='utf-8')

# Trust / methodology page.
about = ROOT / 'sobre'
about.mkdir(exist_ok=True)
about_html = f'''<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sobre a Fonseca Tools — metodologia e privacidade</title>
<meta name="description" content="Conheça a Fonseca Tools, projeto da Fonseca Labs: como as ferramentas são calculadas, testadas e publicadas, com foco em utilidade e processamento local.">
<link rel="canonical" href="{SITE_URL}/sobre/"><meta name="robots" content="index,follow">
<link rel="stylesheet" href="../assets/styles.css">
<script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@type':'Organization','name':'Fonseca Labs','url':f'{SITE_URL}/','sameAs':['https://github.com/Fonseca-Labs']}, ensure_ascii=False)}</script>
</head><body>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="../">Fonseca Tools</a><nav><a href="../#ferramentas">Ferramentas</a><a href="../sobre/">Sobre</a><a href="../privacidade/">Privacidade</a></nav></div></header>
<main class="privacy"><div class="wrap narrow">
<div class="eyebrow">Fonseca Labs</div><h1>Sobre a Fonseca Tools</h1>
<p>A Fonseca Tools é um projeto da Fonseca Labs criado para reunir pequenas ferramentas de cálculo, datas, conversão e tratamento de texto em páginas rápidas, gratuitas e sem cadastro.</p>
<h2>Como as ferramentas são feitas</h2><p>As fórmulas e regras ficam no próprio código do site. Cada publicação passa por validações automáticas que verificam a sintaxe do JavaScript, a associação entre cada página e sua fórmula e a geração dos arquivos necessários para o GitHub Pages.</p>
<h2>Como tratamos os dados digitados</h2><p>Os cálculos e transformações das ferramentas são executados no navegador. O código das ferramentas não envia os números ou textos digitados para um servidor. Métricas gerais do Google Analytics só são carregadas após consentimento.</p>
<h2>Limitações</h2><p>Ferramentas matemáticas e de conversão seguem as fórmulas descritas em cada página. Ferramentas de datas informam quando não consideram feriados ou regras especiais. Resultados financeiros são matemáticos e não substituem orientação contábil, tributária ou financeira profissional.</p>
<h2>Projeto público</h2><p>O código-fonte do projeto pode ser consultado no <a href="https://github.com/Fonseca-Labs/fonseca-tools" rel="noopener">repositório da Fonseca Labs no GitHub</a>.</p>
<p class="about-note">Objetivo do projeto: resolver tarefas simples com clareza, rapidez e o mínimo de coleta de dados.</p>
</div></main>
<footer><div class="wrap footer-inner"><span>© <span data-year></span> Fonseca Tools</span><span>Um projeto da Fonseca Labs.</span></div></footer>
<script src="../assets/app.js" defer></script></body></html>'''
(about / 'index.html').write_text(about_html, encoding='utf-8')

# Add Sobre to navigation throughout generated pages.
for page in [ROOT / 'index.html', ROOT / 'privacidade' / 'index.html', *[ROOT / t['slug'] / 'index.html' for t in TOOLS]]:
    text = page.read_text(encoding='utf-8')
    if '>Sobre<' not in text:
        if page == ROOT / 'index.html':
            text = text.replace('<a href="privacidade/">Privacidade</a>', '<a href="sobre/">Sobre</a><a href="privacidade/">Privacidade</a>')
        else:
            text = text.replace('<a href="../privacidade/">Privacidade</a>', '<a href="../sobre/">Sobre</a><a href="../privacidade/">Privacidade</a>')
    page.write_text(text, encoding='utf-8')

# Keep sitemap aligned with the new trust page.
sitemap = ROOT / 'sitemap.xml'
xml = sitemap.read_text(encoding='utf-8')
about_url = f'{SITE_URL}/sobre/'
if about_url not in xml:
    xml = xml.replace('</urlset>', f'  <url><loc>{about_url}</loc></url>\n</urlset>')
    sitemap.write_text(xml, encoding='utf-8')

print(f'SEO enhancement complete: {len(TOOLS)} tool pages + /sobre/')
