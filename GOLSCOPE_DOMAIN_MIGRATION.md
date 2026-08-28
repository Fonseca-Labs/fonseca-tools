# GolScope domain migration runbook

Status em 2026-08-28:

- `golscope.com.br`: consulta oficial ISAVAIL/Registro.br retornou `Status 0 (Available)`.
- `golscope.com`: consulta RDAP Verisign retornou HTTP 404 e não há resolução DNS; confirmar novamente no registrador no momento da compra.
- Compra/registro não executados. Bloqueio: `DOMAIN_PURCHASE_BLOCKED_BY_HUMAN_PAYMENT`.
- Domínio público atual preservado: `fonsecatools.com.br`.

## Estado preparado no código

- Identidade visual pública: GolScope.
- Backend aceita, em transição, origens `https://fonsecatools.com.br`, `https://golscope.com.br` e `https://www.golscope.com.br`.
- `FRONTEND_URL` continua sendo a autoridade do retorno do Mercado Pago e não deve ser trocada antes do novo domínio estar funcional.
- `site/CNAME`, canonical, sitemap e robots continuam apontando para o domínio atual até a aquisição do GolScope.

## Migração após aquisição

1. Registrar e verificar `golscope.com.br` na conta autorizada.
2. Verificar o domínio no GitHub antes de ativá-lo no Pages.
3. Configurar DNS do apex para GitHub Pages (`A`/`AAAA` oficiais do GitHub) e `www` via CNAME para o host Pages da organização/usuário.
4. Validar propagação DNS e emissão HTTPS sem remover o domínio antigo.
5. Trocar o Custom Domain do GitHub Pages e `site/CNAME` para `golscope.com.br`.
6. Validar homepage, dashboard, assets e API via HTTPS.
7. Alterar Railway `FRONTEND_URL` para `https://golscope.com.br`; manter `FRONTEND_URLS` com domínio antigo + novo durante a janela de transição.
8. Validar CORS do novo domínio.
9. Validar checkout completo e o `back_url` do Mercado Pago no novo domínio.
10. Atualizar mensagens Telegram para apontar diretamente para `golscope.com.br`.
11. Trocar canonical, OpenGraph URL, robots e sitemap para o GolScope.
12. Configurar redirecionamento permanente do domínio antigo para o novo quando houver mecanismo de hosting/proxy adequado; GitHub Pages não deve ser usado como pressuposto para um 301 arbitrário entre dois domínios sem validar o comportamento real.
13. Manter o domínio antigo ativo durante a transição e monitorar acessos/retornos de pagamento.

## localStorage

`localStorage` é isolado por origem. As chaves do checkout no domínio atual não migram automaticamente para o GolScope. Usuários, assinaturas, CPF/WhatsApp, Telegram e pagamentos ficam preservados no backend; porém um checkout em andamento deve terminar no domínio em que começou. Por isso a troca de `FRONTEND_URL` só deve ocorrer depois da validação do novo domínio e com janela de coexistência.
