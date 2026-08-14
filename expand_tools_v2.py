"""Second additive long-tail tool pack for Fonseca Tools.

Builds on expand_tools.py, preserving the stable 30-tool layer and adding 10
more browser-only utilities.
"""
import expand_tools as pack1

site = pack1.base

EXTRA_TOOLS_V2 = [
    {
        "id": "horas-trabalhadas-com-intervalo", "slug": "horas-trabalhadas-com-intervalo", "category": "Datas",
        "title": "Calculadora de Horas Trabalhadas com Intervalo",
        "description": "Calcule a jornada líquida entre entrada e saída descontando o intervalo em minutos.",
        "kind": "two-time-number", "labels": ["Horário de entrada", "Horário de saída", "Intervalo (minutos)"],
        "placeholders": ["", "", "Ex.: 60"], "formula": "worked_hours_break", "button": "Calcular horas trabalhadas",
        "intro": "Informe entrada, saída e o intervalo não trabalhado. Se a saída for anterior à entrada, a ferramenta considera que o expediente terminou no dia seguinte.",
        "example": "Exemplo: 08:00 às 17:30 com 60 minutos de intervalo = 8 horas e 30 minutos trabalhados.",
    },
    {
        "id": "horas-minutos-para-decimal", "slug": "horas-minutos-para-decimal", "category": "Conversão",
        "title": "Converter Horas e Minutos em Horas Decimais",
        "description": "Converta um tempo como 2 horas e 30 minutos para 2,5 horas decimais.",
        "kind": "two-number", "labels": ["Horas", "Minutos"], "placeholders": ["Ex.: 2", "Ex.: 30"],
        "formula": "hm_to_decimal", "button": "Converter para decimal",
        "intro": "Transforme horas e minutos em um único valor decimal, útil para planilhas, apontamentos e cálculos por hora.",
        "example": "Exemplo: 2 h 30 min = 2,5 horas decimais.",
    },
    {
        "id": "idade-em-dias", "slug": "idade-em-dias", "category": "Datas",
        "title": "Calculadora de Idade em Dias",
        "description": "Descubra quantos dias completos se passaram desde uma data de nascimento.",
        "kind": "one-date", "labels": ["Data de nascimento"], "placeholders": [""],
        "formula": "age_in_days", "button": "Calcular idade em dias",
        "intro": "Informe a data de nascimento para calcular o total de dias corridos até hoje, usando a data do seu dispositivo.",
        "example": "A ferramenta mostra o total de dias completos vividos até a data atual.",
    },
    {
        "id": "meses-entre-datas", "slug": "meses-entre-datas", "category": "Datas",
        "title": "Meses Entre Duas Datas",
        "description": "Calcule meses completos e dias restantes entre duas datas.",
        "kind": "two-date", "labels": ["Data inicial", "Data final"], "placeholders": ["", ""],
        "formula": "months_between", "button": "Calcular meses",
        "intro": "Compare duas datas pelo calendário e veja quantos meses completos existem entre elas, além dos dias restantes.",
        "example": "Útil para contratos, períodos, planejamento e acompanhamento de prazos mensais.",
    },
    {
        "id": "somar-meses-data", "slug": "somar-meses-data", "category": "Datas",
        "title": "Somar Meses a uma Data",
        "description": "Adicione ou subtraia meses de uma data preservando o dia quando possível.",
        "kind": "date-number", "labels": ["Data inicial", "Meses (use negativo para subtrair)"], "placeholders": ["", "Ex.: 6"],
        "formula": "add_months", "button": "Calcular nova data",
        "intro": "Informe uma data e um número inteiro de meses. Em meses mais curtos, a ferramenta ajusta para o último dia válido.",
        "example": "Exemplo: um mês após 31 de janeiro cai no último dia válido de fevereiro.",
    },
    {
        "id": "kmh-para-ms", "slug": "kmh-para-ms", "category": "Conversão",
        "title": "Converter km/h para m/s",
        "description": "Converta quilômetros por hora em metros por segundo.",
        "kind": "one-number", "labels": ["Velocidade (km/h)"], "placeholders": ["Ex.: 72"],
        "formula": "kmh_to_ms", "button": "Converter velocidade",
        "intro": "Digite uma velocidade em quilômetros por hora para obter o equivalente em metros por segundo.",
        "example": "Exemplo: 72 km/h = 20 m/s.",
    },
    {
        "id": "ms-para-kmh", "slug": "ms-para-kmh", "category": "Conversão",
        "title": "Converter m/s para km/h",
        "description": "Converta metros por segundo em quilômetros por hora.",
        "kind": "one-number", "labels": ["Velocidade (m/s)"], "placeholders": ["Ex.: 20"],
        "formula": "ms_to_kmh", "button": "Converter velocidade",
        "intro": "Digite uma velocidade em metros por segundo para obter o equivalente em quilômetros por hora.",
        "example": "Exemplo: 20 m/s = 72 km/h.",
    },
    {
        "id": "qual-porcentagem-um-valor-representa", "slug": "qual-porcentagem-um-valor-representa", "category": "Matemática",
        "title": "Qual Porcentagem um Valor Representa de Outro",
        "description": "Descubra qual percentual uma parte representa em relação a um valor total.",
        "kind": "two-number", "labels": ["Valor da parte", "Valor total"], "placeholders": ["Ex.: 30", "Ex.: 200"],
        "formula": "part_as_percent", "button": "Calcular porcentagem",
        "intro": "Use quando você conhece uma parte e o total e quer descobrir a porcentagem correspondente.",
        "example": "Exemplo: 30 representa 15% de 200.",
    },
    {
        "id": "margem-de-lucro", "slug": "margem-de-lucro", "category": "Financeiro",
        "title": "Calculadora de Margem de Lucro",
        "description": "Calcule lucro por unidade e margem percentual a partir do custo e do preço de venda.",
        "kind": "two-number", "labels": ["Custo", "Preço de venda"], "placeholders": ["Ex.: 50", "Ex.: 80"],
        "formula": "profit_margin", "button": "Calcular margem",
        "intro": "Informe custo e preço de venda para ver o lucro bruto por unidade e qual percentual do preço corresponde a esse lucro.",
        "example": "Exemplo: custo de R$ 50 e venda por R$ 80 geram lucro de R$ 30 e margem de 37,5%.",
    },
    {
        "id": "calculadora-markup", "slug": "calculadora-markup", "category": "Financeiro",
        "title": "Calculadora de Markup",
        "description": "Calcule preço de venda, lucro e margem a partir do custo e do markup desejado.",
        "kind": "two-number", "labels": ["Custo", "Markup (%)"], "placeholders": ["Ex.: 50", "Ex.: 60"],
        "formula": "markup_price", "button": "Calcular markup",
        "intro": "Aplique um percentual de markup sobre o custo para encontrar o preço de venda e visualizar a margem resultante.",
        "example": "Exemplo: custo de R$ 50 com markup de 60% resulta em preço de R$ 80.",
    },
]

existing = {tool["slug"] for tool in site.TOOLS}
site.TOOLS.extend(tool for tool in EXTRA_TOOLS_V2 if tool["slug"] not in existing)

_previous_field_html = site.field_html

def field_html(tool):
    if tool["kind"] == "two-time-number":
        labels = tool["labels"]
        ph = tool["placeholders"]
        return (
            f'<label>{site.esc(labels[0])}<input type="time" data-input="0"></label>'
            f'<label>{site.esc(labels[1])}<input type="time" data-input="1"></label>'
            f'<label>{site.esc(labels[2])}<input inputmode="decimal" type="text" data-input="2" placeholder="{site.esc(ph[2])}" autocomplete="off"></label>'
        )
    return _previous_field_html(tool)

site.field_html = field_html

HELPERS_V2 = r"""  const daySerial = d => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000;
  const addMonthsClamped = (d, amount) => { const day=d.getDate(); const first=new Date(d.getFullYear(), d.getMonth()+amount, 1, 12, 0, 0); const last=new Date(first.getFullYear(), first.getMonth()+1, 0, 12, 0, 0).getDate(); first.setDate(Math.min(day,last)); return first; };
"""

HELPER_ANCHOR = "  const calculate = (action='calculate') => {"
if "const addMonthsClamped" not in site.JS:
    if HELPER_ANCHOR not in site.JS:
        raise RuntimeError("V2 JS helper insertion anchor not found")
    site.JS = site.JS.replace(HELPER_ANCHOR, HELPERS_V2 + "\n" + HELPER_ANCHOR, 1)

CASES_V2 = r"""        case 'worked_hours_break': { const start=timeMinutes(val(0)), end=timeMinutes(val(1)), pause=num(2); if(pause<0) throw new Error('O intervalo não pode ser negativo.'); let gross=end-start; if(gross<0) gross+=1440; if(pause>gross) throw new Error('O intervalo não pode ser maior que a jornada bruta.'); const net=gross-pause, h=Math.floor(net/60), m=Math.round(net%60); show(`${h} hora${h===1?'':'s'} e ${m} minuto${m===1?'':'s'} trabalhados\nTotal líquido: ${fmt(net/60)} horas decimais\nJornada bruta: ${gross} min • Intervalo: ${fmt(pause)} min`); break; }
        case 'hm_to_decimal': { const h=num(0), m=num(1); if(h<0) throw new Error('As horas não podem ser negativas.'); if(m<0||m>=60) throw new Error('Os minutos devem ficar entre 0 e 59.'); const total=h+m/60; show(`${fmt(total)} horas decimais\nTotal: ${fmt(h*60+m)} minutos`); break; }
        case 'age_in_days': { const birth=dateLocal(val(0)), now=new Date(), today=new Date(now.getFullYear(),now.getMonth(),now.getDate(),12,0,0); if(birth>today) throw new Error('A data de nascimento não pode estar no futuro.'); const days=Math.round(daySerial(today)-daySerial(birth)); show(`${days} dias completos`); break; }
        case 'months_between': { let a=dateLocal(val(0)), b=dateLocal(val(1)); if(a>b){ const t=a; a=b; b=t; } let months=(b.getFullYear()-a.getFullYear())*12+(b.getMonth()-a.getMonth()); let anchor=addMonthsClamped(a,months); if(anchor>b){ months--; anchor=addMonthsClamped(a,months); } const days=Math.round(daySerial(b)-daySerial(anchor)); show(`${months} mês${months===1?'':'es'} completo${months===1?'':'s'} e ${days} dia${days===1?'':'s'}\nTotal aproximado: ${fmt((daySerial(b)-daySerial(a))/30.436875)} meses`); break; }
        case 'add_months': { const d=dateLocal(val(0)), months=num(1); if(!Number.isInteger(months)) throw new Error('Use um número inteiro de meses.'); show(dateFmt(addMonthsClamped(d,months))); break; }
        case 'kmh_to_ms': { const speed=num(0); show(`${fmt(speed/3.6)} m/s`); break; }
        case 'ms_to_kmh': { const speed=num(0); show(`${fmt(speed*3.6)} km/h`); break; }
        case 'part_as_percent': { const part=num(0), total=num(1); if(total===0) throw new Error('O valor total não pode ser zero.'); show(`${fmt(part)} representa ${fmt(part/total*100)}% de ${fmt(total)}`); break; }
        case 'profit_margin': { const cost=num(0), price=num(1); if(price===0) throw new Error('O preço de venda não pode ser zero.'); const profit=price-cost, margin=profit/price*100; show(`Lucro por unidade: ${money(profit)}\nMargem sobre a venda: ${fmt(margin)}%`); break; }
        case 'markup_price': { const cost=num(0), markup=num(1); if(cost<0) throw new Error('O custo não pode ser negativo.'); if(markup<=-100) throw new Error('O markup deve ser maior que -100%.'); const price=cost*(1+markup/100), profit=price-cost, margin=price===0?0:profit/price*100; show(`Preço de venda: ${money(price)}\nLucro por unidade: ${money(profit)}\nMargem resultante: ${fmt(margin)}%`); break; }
"""

CASE_ANCHOR = "        default: throw new Error('Ferramenta não configurada.');"
if "case 'worked_hours_break'" not in site.JS:
    if CASE_ANCHOR not in site.JS:
        raise RuntimeError("V2 JS case insertion anchor not found")
    site.JS = site.JS.replace(CASE_ANCHOR, CASES_V2 + CASE_ANCHOR, 1)

site.README = site.README.replace(
    "MVP estático com 30 microferramentas gratuitas.",
    f"MVP estático com {len(site.TOOLS)} microferramentas gratuitas.",
)

if __name__ == "__main__":
    site.build()
    print(f"Built {len(site.TOOLS)} tools at {site.ROOT} (base + long-tail packs v1/v2)")
