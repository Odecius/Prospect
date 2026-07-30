# Integração Google Places API (New)

## Arquitetura

`API interna → ExternalSearchService → BusinessSearchProvider → GooglePlacesClient/httpx`.

Endpoints autenticados:

- `POST /api/external/google-places/search`: pesquisa temporária, autenticada e protegida por CSRF;
- `POST /api/external/google-places/link`: vincula somente um Place ID a uma empresa interna após revisão e CSRF.

## Field Mask e custo

Máscara explícita: `places.id,places.displayName,places.formattedAddress,places.addressComponents,places.location,places.primaryType,places.types,places.businessStatus,places.rating,places.userRatingCount,places.websiteUri,places.googleMapsUri,places.attributions,nextPageToken`.

Não há `*`, fotos, reviews, resumos ou atmosfera. `rating`, `userRatingCount` e `websiteUri` acionam o nível Text Search Enterprise; os demais campos chegam até Pro/ID Only. O custo é pay-as-you-go e deve ser protegido também por quotas e alertas no Google Cloud antes de produção.

## Limites

- 10 resultados por página por padrão, máximo técnico 20;
- máximo configurado de 2 páginas e limite absoluto de 3;
- 5 requisições por minuto por utilizador/processo por padrão;
- timeout 5 segundos;
- até 2 retries somente para timeout, 408, 429 e 5xx, com backoff curto;
- nenhuma execução em background, cache, prefetch, busca em massa ou chamada automática;
- cursores assinados expiram em 10 minutos e não expõem o page token diretamente.

## Persistência e retenção

Resultados, endereço, coordenadas, tipos, status, rating, quantidade de avaliações, website, URI do Google Maps e atribuições são temporários, enviados apenas na resposta autenticada e retidos por **zero segundos no servidor**. A interface os descarta ao recarregar.

Somente `places.id` é persistido como `company_source_refs.external_id`, após uma pessoa selecionar uma empresa interna. Divergências não sobrescrevem dados internos. Place ID repetido gera conflito rastreável. Campos permanentes da empresa continuam dependentes de entrada/revisão humana independente.

## Conformidade

Resultados são identificados por `Google Maps` com `translate="no"`. `/privacy` e `/terms` referenciam as políticas Google. A conta de faturação no EEE deve revisar os termos EEA específicos. Validação jurídica profissional continua obrigatória antes da produção comercial.

Fontes oficiais revisadas em 2026-07-21:

- https://developers.google.com/maps/documentation/places/web-service/text-search
- https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places/searchText
- https://developers.google.com/maps/documentation/places/web-service/policies
- https://developers.google.com/maps/documentation/places/web-service/usage-and-billing
