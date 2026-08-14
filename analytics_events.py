from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "assets" / "app.js"
PRIVACY = ROOT / "privacidade" / "index.html"

app = APP.read_text(encoding="utf-8")

helper_anchor = "  const calculate = (action='calculate') => {"
helper = r"""  // Privacy-safe usage telemetry. Never include form inputs or result values here.
  const toolName = ($('h1')?.textContent || tool).trim();
  const toolCategory = ($('.eyebrow')?.textContent || 'Sem categoria').trim();
  const trackToolEvent = (eventName, action='calculate') => {
    // gtag exists only after the visitor has accepted Analytics in postbuild.py.
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, {
      tool_name: toolName,
      tool_category: toolCategory,
      tool_action: action || 'calculate'
    });
  };

"""

if "tool_calculation_success" not in app:
    if helper_anchor not in app:
        raise SystemExit("Analytics helper insertion anchor not found")
    app = app.replace(helper_anchor, helper + helper_anchor, 1)

    outcome_anchor = "      }\n    } catch(e){ fail(e); }\n"
    outcome = "      }\n      trackToolEvent('tool_calculation_success', action);\n    } catch(e){ fail(e); trackToolEvent('tool_calculation_error', action); }\n"
    if outcome_anchor not in app:
        raise SystemExit("Analytics outcome insertion anchor not found")
    app = app.replace(outcome_anchor, outcome, 1)

APP.write_text(app, encoding="utf-8")

privacy = PRIVACY.read_text(encoding="utf-8")
if "eventos de uso das ferramentas" not in privacy:
    disclosure = (
        '<section class="wrap narrow info-card" data-analytics-disclosure>'
        '<h2>Analytics e uso das ferramentas</h2>'
        '<p>O Google Analytics 4 é carregado somente depois que o visitante aceita a coleta de métricas. '
        'Além das informações gerais de navegação, o site pode registrar eventos de uso das ferramentas, '
        'como cálculo concluído ou tentativa com erro, identificando apenas o nome da ferramenta, sua categoria e a ação utilizada.</p>'
        '<p>Os números, datas, textos digitados e os resultados calculados não são enviados pelo código das ferramentas ao Google Analytics.</p>'
        '</section>'
    )
    if "</main>" in privacy:
        privacy = privacy.replace("</main>", disclosure + "</main>", 1)
    elif "</body>" in privacy:
        privacy = privacy.replace("</body>", disclosure + "</body>", 1)
    else:
        raise SystemExit("Privacy page has no insertion point")

PRIVACY.write_text(privacy, encoding="utf-8")

print("Analytics events enabled: success/error, metadata only, consent-gated")
