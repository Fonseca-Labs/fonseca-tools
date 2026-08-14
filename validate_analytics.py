from pathlib import Path

ROOT = Path(__file__).resolve().parent
app = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
privacy = (ROOT / "privacidade" / "index.html").read_text(encoding="utf-8")

errors = []

for marker in [
    "tool_calculation_success",
    "tool_calculation_error",
    "tool_name",
    "tool_category",
    "tool_action",
    "typeof window.gtag !== 'function'",
]:
    if marker not in app:
        errors.append(f"app.js: missing analytics marker {marker}")

start = app.find("const trackToolEvent")
end = app.find("const calculate", start)
if start < 0 or end < 0:
    errors.append("app.js: analytics helper block not found")
else:
    block = app[start:end]
    for forbidden in ["val(", "inputs", "data-input", "result.innerHTML", "result.textContent"]:
        if forbidden in block:
            errors.append(f"app.js: analytics helper must not reference user data via {forbidden}")

for marker in [
    "eventos de uso das ferramentas",
    "nome da ferramenta, sua categoria e a ação utilizada",
    "Os números, datas, textos digitados e os resultados calculados não são enviados",
]:
    if marker not in privacy:
        errors.append(f"privacy page: missing disclosure {marker}")

if errors:
    raise SystemExit("Analytics validation failed:\n- " + "\n- ".join(errors))

print("Analytics validation passed: consent-gated metadata-only tool events")
