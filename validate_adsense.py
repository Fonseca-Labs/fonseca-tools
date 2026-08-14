from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
client = os.environ.get("ADSENSE_CLIENT", "").strip()

if not client or not client.startswith("ca-pub-"):
    raise SystemExit("AdSense validation failed: ADSENSE_CLIENT missing or invalid")

publisher_id = client.removeprefix("ca-")
expected_src = f"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client}"
errors = []
checked = 0

for path in ROOT.rglob("*.html"):
    if path.name.startswith("google"):
        continue
    checked += 1
    text = path.read_text(encoding="utf-8")
    if expected_src not in text:
        errors.append(f"{path.relative_to(ROOT)}: missing AdSense client snippet")
    if 'crossorigin="anonymous"' not in text:
        errors.append(f"{path.relative_to(ROOT)}: AdSense snippet missing crossorigin")

ads_txt = ROOT / "ads.txt"
expected_ads_txt = f"google.com, {publisher_id}, DIRECT, f08c47fec0942fa0"
if not ads_txt.exists():
    errors.append("ads.txt: missing")
elif expected_ads_txt not in ads_txt.read_text(encoding="utf-8"):
    errors.append("ads.txt: publisher line missing or incorrect")

privacy = (ROOT / "privacidade" / "index.html").read_text(encoding="utf-8")
for marker in ["Google AdSense", "eventual exibição de anúncios", "gestão de consentimento"]:
    if marker not in privacy:
        errors.append(f"privacy page: missing AdSense disclosure {marker}")

if errors:
    raise SystemExit("AdSense validation failed:\n- " + "\n- ".join(errors))

print(f"AdSense validation passed: {checked} HTML pages + ads.txt use {client}")
