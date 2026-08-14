"""Additive long-tail tool pack for Fonseca Tools.

Keeps build_site.py as the stable base and extends it at build time.
"""
import build_site as base

EXTRA_TOOLS = [
    {
        "id": "dias-uteis-entre-datas", "slug": "dias-uteis-entre-datas", "category": "Datas",
        "title": "Dias Úteis Entre Duas Datas",
        "description": "Conte dias de segunda a sexta entre duas datas, sem considerar feriados.",
        "kind": "two-date", "labels": ["Data inicial", "Data final"], "placeholders": ["", ""],
        "formula": "business_days_between", "button": "Calcular dias úteis",
        "intro": "Calcule quantos dias de segunda a sexta existem no intervalo. A data inicial não entra na contagem; a final entra se cair em dia útil. Feriados não são considerados.",
        "example": "Exemplo: de uma segunda-feira até a sexta-feira da mesma semana = 4 dias úteis após a data inicial.",
    },
    {
        "id": "somar-dias-uteis", "slug": "somar-dias-uteis", "category": "Datas",
        "title": "Somar Dias Úteis a uma Data",
        "description": "Encontre uma data futura ou passada pulando sábados e domingos.",
        "kind": "date-number", "labels": ["Data inicial", "Dias úteis (use negativo para subtrair)"], "placeholders": ["", "Ex.: 10"],
        "formula": "add_business_days", "button": "Calcular data útil",
        "intro": "Adicione ou subtraia dias úteis de uma data, considerando segunda a sexta-feira. Feriados não são considerados nesta versão.",
        "example": "Exemplo: somar 5 dias úteis a uma segunda-feira resulta na segunda-feira seguinte, se não houver feriado.",
    },
    {
        "id": "semanas-entre-datas", "slug": "semanas-entre-datas", "category": "Datas",
        "title": "Semanas Entre Duas Datas",
        "description": "Calcule o intervalo entre duas datas em semanas e dias.",
        "kind": "two-date", "labels": ["Data inicial", "Data final"], "placeholders": ["", ""],
        "formula": "weeks_between", "button": "Calcular semanas",
        "intro": "Veja a distância entre duas datas em semanas decimais e também em semanas completas mais dias restantes.",
        "example": "Exemplo: 17 dias correspondem a 2 semanas e 3 dias.",
    },
    {
        "id": "dias-ate-uma-data", "slug": "dias-ate-uma-data", "category": "Datas",
        "title": "Quantos Dias Faltam Até uma Data",
        "description": "Descubra quantos dias faltam para uma data futura ou quantos dias se passaram desde uma data.",
        "kind": "one-date", "labels": ["Data alvo"], "placeholders": [""],
        "formula": "days_until", "button": "Calcular dias",
        "intro": "Compare uma data com o dia de hoje no seu dispositivo e veja a diferença em dias corridos.",
        "example": "Útil para contagens regressivas, prazos pessoais e planejamento.",
    },
    {
        "id": "diferenca-entre-horarios", "slug": "diferenca-entre-horarios", "category": "Datas",
        "title": "Diferença Entre Dois Horários",
        "description": "Calcule quantas horas e minutos existem entre dois horários.",
        "kind": "two-time", "labels": ["Horário inicial", "Horário final"], "placeholders": ["", ""],
        "formula": "time_difference", "button": "Calcular diferença",
        "intro": "Informe dois horários. Se o horário final for menor que o inicial, a calculadora considera que ele ocorre no dia seguinte.",
        "example": "Exemplo: de 22:30 até 01:15 = 2 horas e 45 minutos.",
    },
    {
        "id": "horas-decimais-para-horas-minutos", "slug": "horas-decimais-para-horas-minutos", "category": "Conversão",
        "title": "Converter Horas Decimais em Horas e Minutos",
        "description": "Transforme horas decimais, como 2,5, no formato de horas e minutos.",
        "kind": "one-number", "labels": ["Horas decimais"], "placeholders": ["Ex.: 2,5"],
        "formula": "decimal_hours_to_hm", "button": "Converter horas",
        "intro": "Digite uma quantidade de horas em formato decimal para obter o equivalente em horas e minutos.",
        "example": "Exemplo: 2,5 horas = 2 horas e 30 minutos.",
    },
    {
        "id": "preco-antes-do-desconto", "slug": "preco-antes-do-desconto", "category": "Matemática",
        "title": "Calcular Preço Antes do Desconto",
        "description": "Descubra o preço original conhecendo o preço final e o percentual de desconto.",
        "kind": "two-number", "labels": ["Preço após o desconto", "Desconto (%)"], "placeholders": ["Ex.: 180", "Ex.: 10"],
        "formula": "original_before_discount", "button": "Descobrir preço original",
        "intro": "Informe quanto foi pago após o desconto e qual foi o percentual aplicado para recuperar o preço original.",
        "example": "Exemplo: se R$ 180 representa o valor após 10% de desconto, o preço original era R$ 200.",
    },
    {
        "id": "porcentagem-para-total", "slug": "porcentagem-para-total", "category": "Matemática",
        "title": "Descobrir o Total pela Porcentagem",
        "description": "Descubra o valor total quando você conhece uma parte e qual porcentagem ela representa.",
        "kind": "two-number", "labels": ["Valor da parte", "Porcentagem que a parte representa (%)"], "placeholders": ["Ex.: 30", "Ex.: 15"],
        "formula": "total_from_part_pct", "button": "Calcular total",
        "intro": "Use quando souber que um valor corresponde a determinada porcentagem e quiser descobrir o total de 100%.",
        "example": "Exemplo: se 30 corresponde a 15%, então 100% corresponde a 200.",
    },
    {
        "id": "desconto-sucessivo", "slug": "desconto-sucessivo", "category": "Matemática",
        "title": "Calculadora de Descontos Sucessivos",
        "description": "Calcule o preço final após dois descontos aplicados um depois do outro.",
        "kind": "three-number", "labels": ["Preço original", "Primeiro desconto (%)", "Segundo desconto (%)"], "placeholders": ["Ex.: 200", "Ex.: 10", "Ex.: 20"],
        "formula": "successive_discounts", "button": "Calcular descontos",
        "intro": "Dois descontos sucessivos não devem ser simplesmente somados. A ferramenta aplica o segundo desconto sobre o valor já reduzido pelo primeiro.",
        "example": "Exemplo: descontos de 10% e 20% equivalem a um desconto total de 28%, não 30%.",
    },
    {
        "id": "valor-antes-do-acrescimo", "slug": "valor-antes-do-acrescimo", "category": "Matemática",
        "title": "Calcular Valor Antes do Acréscimo",
        "description": "Descubra o valor original conhecendo o valor final e o percentual de acréscimo.",
        "kind": "two-number", "labels": ["Valor após o acréscimo", "Acréscimo (%)"], "placeholders": ["Ex.: 220", "Ex.: 10"],
        "formula": "original_before_increase", "button": "Descobrir valor original",
        "intro": "Informe o valor final e o percentual de aumento aplicado para recuperar o valor antes do acréscimo.",
        "example": "Exemplo: se R$ 220 é o resultado após acréscimo de 10%, o valor original era R$ 200.",
    },
]

existing = {tool["slug"] for tool in base.TOOLS}
base.TOOLS.extend(tool for tool in EXTRA_TOOLS if tool["slug"] not in existing)

_base_field_html = base.field_html

def field_html(tool):
    if tool["kind"] == "two-time":
        labels = tool["labels"]
        return ''.join(
            f'<label>{base.esc(labels[i])}<input type="time" data-input="{i}"></label>'
            for i in range(2)
        )
    return _base_field_html(tool)

base.field_html = field_html

HELPERS = r"""  const timeMinutes = s => { if(!/^\d{2}:\d{2}$/.test(s)) throw new Error('Informe um horário válido.'); const [h,m]=s.split(':').map(Number); if(h>23||m>59) throw new Error('Informe um horário válido.'); return h*60+m; };
  const isWeekday = d => d.getDay() !== 0 && d.getDay() !== 6;
"""

BASE_HELPER_ANCHOR = "  const lines = s => s.replace(/\\r/g,'').split('\\n');\n"
if HELPERS.strip() not in base.JS:
    if BASE_HELPER_ANCHOR not in base.JS:
        raise RuntimeError("JS helper insertion anchor not found")
    base.JS = base.JS.replace(BASE_HELPER_ANCHOR, BASE_HELPER_ANCHOR + HELPERS, 1)

CASES = r"""        case 'business_days_between': { let a=dateLocal(val(0)), b=dateLocal(val(1)); if(a>b){ const t=a; a=b; b=t; } let count=0, d=new Date(a); while(d<b){ d.setDate(d.getDate()+1); if(isWeekday(d)) count++; } show(`${count} dias úteis\nFeriados não considerados`); break; }
        case 'add_business_days': { const d=dateLocal(val(0)); const amount=num(1); if(!Number.isInteger(amount)) throw new Error('Use um número inteiro de dias úteis.'); const step=amount<0?-1:1; let remaining=Math.abs(amount); while(remaining>0){ d.setDate(d.getDate()+step); if(isWeekday(d)) remaining--; } show(`${dateFmt(d)}\nFeriados não considerados`); break; }
        case 'weeks_between': { const a=dateLocal(val(0)), b=dateLocal(val(1)); const days=Math.round(Math.abs(b-a)/86400000); const weeks=Math.floor(days/7), rest=days%7; show(`${fmt(days/7)} semanas\n${weeks} semana${weeks===1?'':'s'} e ${rest} dia${rest===1?'':'s'}`); break; }
        case 'days_until': { const target=dateLocal(val(0)); const now=new Date(), today=new Date(now.getFullYear(),now.getMonth(),now.getDate(),12,0,0); const days=Math.round((target-today)/86400000); if(days>0) show(`Faltam ${days} dias`); else if(days<0) show(`Essa data foi há ${Math.abs(days)} dias`); else show('A data é hoje.'); break; }
        case 'time_difference': { const start=timeMinutes(val(0)), end=timeMinutes(val(1)); let diff=end-start; if(diff<0) diff+=1440; const h=Math.floor(diff/60), m=diff%60; show(`${h} hora${h===1?'':'s'} e ${m} minuto${m===1?'':'s'}\nTotal: ${diff} minutos`); break; }
        case 'decimal_hours_to_hm': { const raw=num(0), sign=raw<0?'-':'', abs=Math.abs(raw); let h=Math.floor(abs), m=Math.round((abs-h)*60); if(m===60){h++;m=0;} show(`${sign}${h} h ${m} min\n${fmt(raw*60)} minutos`); break; }
        case 'original_before_discount': { const finalValue=num(0), pct=num(1); if(pct<0||pct>=100) throw new Error('O desconto deve ficar entre 0% e menos de 100%.'); const original=finalValue/(1-pct/100); show(`Preço original: ${money(original)}\nDesconto aplicado: ${money(original-finalValue)}`); break; }
        case 'total_from_part_pct': { const part=num(0), pct=num(1); if(pct<=0) throw new Error('A porcentagem deve ser maior que zero.'); show(`Total (100%): ${fmt(part/(pct/100))}`); break; }
        case 'successive_discounts': { const price=num(0), p1=num(1), p2=num(2); if(p1<0||p2<0||p1>100||p2>100) throw new Error('Os descontos devem ficar entre 0% e 100%.'); const finalValue=price*(1-p1/100)*(1-p2/100); const eq=(1-(1-p1/100)*(1-p2/100))*100; show(`Valor final: ${money(finalValue)}\nDesconto equivalente: ${fmt(eq)}%\nEconomia: ${money(price-finalValue)}`); break; }
        case 'original_before_increase': { const finalValue=num(0), pct=num(1); if(pct<0) throw new Error('O acréscimo deve ser zero ou positivo.'); const original=finalValue/(1+pct/100); show(`Valor original: ${money(original)}\nAcréscimo aplicado: ${money(finalValue-original)}`); break; }
"""

CASE_ANCHOR = "        default: throw new Error('Ferramenta não configurada.');"
if "case 'business_days_between'" not in base.JS:
    if CASE_ANCHOR not in base.JS:
        raise RuntimeError("JS case insertion anchor not found")
    base.JS = base.JS.replace(CASE_ANCHOR, CASES + CASE_ANCHOR, 1)

base.README = base.README.replace(
    "MVP estático com 20 microferramentas gratuitas. Todo o processamento desta versão ocorre no navegador, sem banco de dados e sem API paga.",
    f"MVP estático com {len(base.TOOLS)} microferramentas gratuitas. Os valores e textos das ferramentas são processados no navegador, sem banco de dados e sem API paga. O Google Analytics 4 só é carregado após consentimento explícito.",
).replace(
    "- `privacidade/`: política compatível com a versão atual, que não usa analytics nem anúncios.",
    "- `privacidade/`: política de privacidade, incluindo o uso consentido do Google Analytics 4.",
).replace(
    "O workflow calcula automaticamente a URL `https://USUARIO.github.io/REPOSITORIO`, executa o gerador e publica o site. Para um repositório chamado `fonseca-tools` na conta `davdsmlqnt007-bot`, a URL prevista é:\n\n`https://davdsmlqnt007-bot.github.io/fonseca-tools/`",
    "O workflow calcula automaticamente a URL `https://ORGANIZACAO.github.io/REPOSITORIO`, executa o gerador e publica o site. O endereço atual é:\n\n`https://fonseca-labs.github.io/fonseca-tools/`",
)

if __name__ == "__main__":
    base.build()
    print(f"Built {len(base.TOOLS)} tools at {base.ROOT} (base + long-tail pack)")
