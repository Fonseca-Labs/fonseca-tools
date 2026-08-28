# GolScope domain decision / archived migration reference

## ACTIVE PRODUCT DECISION — 2026-08-28

- `PRODUCT_NAME = GOLSCOPE`
- `PUBLIC_DOMAIN = fonsecatools.com.br`
- `DOMAIN_MIGRATION_PLANNED = NO`
- `DOMAIN_MIGRATION = CANCELLED`
- `NEW_DOMAIN_PURCHASE_REQUIRED = NO`

The public product brand is **GolScope** / **GolScope — Live Intelligence** while the official public address remains:

`https://fonsecatools.com.br`

This is intentional. Do not purchase, register, configure, redirect to, or activate `golscope.com.br` under the current product decision.

## Active infrastructure rules

- Keep `site/CNAME` as `fonsecatools.com.br`.
- Keep DNS and GitHub Pages Custom Domain unchanged.
- Keep canonical, OpenGraph URL, sitemap and robots on `https://fonsecatools.com.br`.
- Keep Railway `FRONTEND_URL` on the currently functional public domain.
- Keep Mercado Pago `back_url` derived from the current `FRONTEND_URL`; do not change it for a new domain.
- Public frontend CORS must authorize `https://fonsecatools.com.br` plus only any separately configured technical origins that are demonstrably required. `golscope.com.br` and `www.golscope.com.br` are not default authorized origins.
- Keep checkout `localStorage` on the current origin; no cross-domain migration is required.
- Users, subscriptions, CPF/WhatsApp, Telegram linkage, databases and public performance API remain unchanged.

## Historical reference — NOT PLANNED / NOT ACTIVE

Earlier on 2026-08-28, `golscope.com.br` was checked as a possible future branded domain. That migration plan has been cancelled for the current product stage.

The previous availability finding or any historical migration notes must **not** be interpreted as authorization to:

- register or purchase a new domain;
- change DNS;
- change GitHub Pages Custom Domain or `site/CNAME`;
- broaden CORS for a GolScope domain;
- change Mercado Pago return URLs;
- change canonical/sitemap to a new domain;
- create redirects away from `fonsecatools.com.br`.

Any future domain migration would require a new explicit product decision and a fresh audit before execution.

## localStorage

`localStorage` remains on the same origin because the public domain remains `fonsecatools.com.br`. Therefore the current checkout continuity is preserved and no cross-origin storage migration is needed.
