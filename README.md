# Fonseca Tools

MVP estático com 20 microferramentas gratuitas. O processamento dos valores e textos inseridos nas ferramentas ocorre no navegador, sem banco de dados e sem API paga. O Google Analytics 4 é carregado somente após consentimento explícito do visitante.

## Estrutura

- `index.html`: página inicial.
- `assets/styles.css`: visual compartilhado.
- `assets/app.js`: motor genérico das ferramentas.
- uma pasta por ferramenta, cada uma com seu `index.html`.
- `privacidade/`: política de privacidade, incluindo o uso consentido do Google Analytics 4.
- `sitemap.xml` e `robots.txt`: arquivos de indexação.
- `build_site.py`: fonte geradora das páginas.
- `postbuild.py`: pós-processamento do build, incluindo GA4 com consentimento e ajustes de SEO.
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

O workflow calcula automaticamente a URL `https://ORGANIZACAO.github.io/REPOSITORIO`, executa o gerador, aplica o pós-build e publica o site. O endereço atual é:

`https://fonseca-labs.github.io/fonseca-tools/`

O GitHub Pages usa **GitHub Actions** como fonte de publicação. Cada push em `main` dispara um novo deploy.

## Princípio do projeto

O site é propositalmente simples: cada visitante pode usar as ferramentas sem gerar custo de API. A monetização deve ser adicionada apenas depois de haver páginas indexadas e tráfego mensurável.
