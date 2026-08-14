from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")
GA_ID = os.environ.get("GA_MEASUREMENT_ID", "").strip()

if not GA_ID:
    raise SystemExit("GA_MEASUREMENT_ID is required")

analytics_loader = f'''<script>
(function() {{
  const GA_ID = {GA_ID!r};
  function loadAnalytics() {{
    if (window.__fonsecaToolsGaLoaded) return;
    window.__fonsecaToolsGaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){{dataLayer.push(arguments);}};
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    document.head.appendChild(script);
  }}

  const key = 'fonseca_tools_analytics_consent';
  if (localStorage.getItem(key) === 'granted') loadAnalytics();

  window.fonsecaToolsSetAnalyticsConsent = function(accepted) {{
    localStorage.setItem(key, accepted ? 'granted' : 'denied');
    if (accepted) loadAnalytics();
    const banner = document.getElementById('analytics-consent');
    if (banner) banner.remove();
  }};
}})();
</script>'''

consent_banner = '''<div id="analytics-consent" hidden style="position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:760px;margin:auto;padding:16px;border:1px solid #d1d5db;border-radius:12px;background:#fff;box-shadow:0 8px 30px rgba(0,0,0,.16);font:14px/1.45 system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#111827">
  <strong>Privacidade e métricas</strong>
  <p style="margin:8px 0 12px">Podemos usar o Google Analytics para entender visitas e melhorar as ferramentas. O Analytics só é carregado se você aceitar. Os valores e textos digitados nas ferramentas continuam sendo processados localmente.</p>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <button type="button" onclick="fonsecaToolsSetAnalyticsConsent(true)" style="padding:9px 14px;border:0;border-radius:8px;cursor:pointer">Aceitar métricas</button>
    <button type="button" onclick="fonsecaToolsSetAnalyticsConsent(false)" style="padding:9px 14px;border:1px solid #9ca3af;border-radius:8px;background:#fff;cursor:pointer">Recusar</button>
    <a href="./privacidade/" data-privacy-link style="padding:9px 4px">Política de privacidade</a>
  </div>
</div>
<script>
(function(){
  const banner = document.getElementById('analytics-consent');
  if (!banner) return;
  if (localStorage.getItem('fonseca_tools_analytics_consent') === null) banner.hidden = false;
  const link = banner.querySelector('[data-privacy-link]');
  if (link && location.pathname !== '/' && !location.pathname.endsWith('/fonseca-tools/')) link.href = '../privacidade/';
})();
</script>'''

for path in ROOT.rglob("*.html"):
    if path.name.startswith("google"):
        continue
    text = path.read_text(encoding="utf-8")
    if "googletagmanager.com/gtag/js" not in text:
        text = text.replace("</head>", analytics_loader + "\n</head>", 1)
    if 'id="analytics-consent"' not in text:
        text = text.replace("</body>", consent_banner + "\n</body>", 1)
    path.write_text(text, encoding="utf-8")

privacy = ROOT / "privacidade" / "index.html"
text = privacy.read_text(encoding="utf-8")
if 'rel="canonical"' not in text and SITE_URL:
    marker = '<meta name="robots" content="index,follow">'
    text = text.replace(marker, marker + f'<link rel="canonical" href="{SITE_URL}/privacidade/">', 1)

text = text.replace(
    '<h2>Cookies e publicidade</h2><p>Esta versão não inclui anúncios, cookies de publicidade ou ferramentas de análise de terceiros. Se isso mudar, esta página deverá ser atualizada antes da ativação desses serviços.</p>',
    '<h2>Analytics, cookies e publicidade</h2><p>O site utiliza o Google Analytics 4 somente depois que o visitante aceita a coleta de métricas. A escolha é armazenada localmente no navegador. O Analytics pode registrar informações de navegação, como páginas visitadas e interações gerais, mas os valores e textos digitados nas ferramentas não são enviados pelo código das ferramentas ao Google Analytics.</p><p>Esta versão não inclui anúncios nem cookies de publicidade.</p>'
)
privacy.write_text(text, encoding="utf-8")

print(f"Post-build complete: GA4 {GA_ID} with explicit analytics consent")
