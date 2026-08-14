# Fonseca Tools

MVP estático com 20 microferramentas gratuitas. Todo o processamento desta versão ocorre no navegador, sem banco de dados e sem API paga.

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
