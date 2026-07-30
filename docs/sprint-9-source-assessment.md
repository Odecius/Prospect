# Avaliação obrigatória para a Sprint 9

**Estado:** Google Places API (New) aprovada em 2026-07-21; integração conservadora implementada.

Nenhuma fonte externa foi escolhida ou acessada. Antes do primeiro adaptador, é obrigatório aprovar individualmente:

- fornecedor e API específicos;
- termos de uso e permissão para a finalidade comercial;
- base legal e transparência aplicáveis;
- categorias de dados, minimização, retenção e exclusão;
- credenciais, quotas, custos, retry/backoff e resposta a incidentes;
- proibição de scraping não autorizado;
- fluxo de pré-visualização e confirmação humana antes da importação.

A fonte aprovada é o endpoint oficial `POST https://places.googleapis.com/v1/places:searchText`. A revisão oficial confirmou que o Place ID pode ser armazenado indefinidamente, mas o restante do conteúdo não será persistido. Consulte `google-places-integration.md`.
