# Modelo de Dados do ABC Prospect

## Princípios

- PostgreSQL como fonte transacional;
- chaves primárias UUID;
- datas em UTC (`timestamptz`), exibidas no fuso do usuário;
- normalização de CNPJ, telefone, email, domínio e textos usados em busca;
- origem e horário de coleta registrados;
- exclusão lógica somente quando houver necessidade de auditoria definida;
- migrations Alembic pequenas e revisadas, criadas somente após aprovação do modelo documental da fase correspondente;
- score, auditoria e conteúdo gerado preservados como histórico versionado.

Campos comuns previstos, quando aplicáveis: `id`, `created_at`, `updated_at` e `created_by_user_id`. Os nomes são conceituais e poderão ser refinados antes da primeira migration.

## Usuários (`users`)

**Finalidade:** autenticar pessoas e atribuir ações.

**Obrigatórios:** `id`, `email_normalized`, `display_name`, `password_hash`, `status`, `created_at`, `updated_at`.

**Opcionais:** `last_login_at`, `disabled_at`.

**Relacionamentos:** cria/edita empresas, scores, atividades, mensagens e propostas.

**Índices e restrições:** email normalizado único; status limitado a valores aprovados; nunca armazenar senha em texto puro.

## Empresas (`companies`)

**Finalidade:** registro central de cada prospect.

**Obrigatórios:** `id`, `legal_or_trade_name`, `name_normalized`, `country_code` (inicialmente `BR`), `category_id`, `city`, `state_code`, `pipeline_status` (inicialmente `NEW`), `created_at`, `updated_at` e ao menos uma referência de origem criada na mesma operação de cadastro.

**Opcionais:** `legal_name`, `trade_name`, `tax_id_normalized` (CNPJ), `description`, `address_line`, `district`, `postal_code`, `latitude`, `longitude`, `rating`, `review_count`, `has_website`, `website_quality_status`, `notes`, `archived_at`.

**Relacionamentos:** uma categoria obrigatória; uma ou mais referências de fonte, sendo ao menos uma obrigatória desde o cadastro; muitos contatos, auditorias, scores, atividades, mensagens, demonstrações e propostas.

**Índices:** CNPJ normalizado; nome normalizado; cidade/UF/categoria; status do funil; `rating`; `review_count`; `has_website`; busca textual combinada.

**Restrições:** CNPJ único quando não nulo; avaliação dentro da escala definida; contagem de avaliações não negativa; código de país/UF validado; `has_website` deve refletir a existência de contato do tipo website após definição da regra. `pipeline_status` aceita somente `NEW`, `QUALIFIED`, `CONTACTED`, `REPLIED`, `MEETING`, `PROPOSAL_SENT`, `NEGOTIATION`, `WON`, `LOST`, `DO_NOT_CONTACT` e `ARCHIVED`.

O fluxo principal começa em `NEW` e pode avançar por `QUALIFIED`, `CONTACTED`, `REPLIED`, `MEETING`, `PROPOSAL_SENT` e `NEGOTIATION`, chegando a `WON` ou `LOST`. `DO_NOT_CONTACT` interrompe abordagens comerciais e `ARCHIVED` retira o registro do fluxo ativo. As transições e reaberturas permitidas serão detalhadas antes da implementação do histórico comercial.

## Categorias (`categories`)

**Finalidade:** taxonomia controlada para classificação e filtros.

**Obrigatórios:** `id`, `name`, `slug`, `active`.

**Opcionais:** `parent_id`, `external_code`, `description`.

**Relacionamentos:** categoria pai opcional e muitas empresas.

**Índices e restrições:** `slug` único; nome normalizado único dentro do mesmo pai; impedir ciclo na hierarquia.

## Fontes de dados (`data_sources`)

**Finalidade:** cadastrar a procedência, o tipo e as condições de uso de uma fonte.

**Obrigatórios:** `id`, `name`, `source_type`, `collection_method`, `active`, `created_at`.

**Opcionais:** `base_url`, `terms_url`, `notes`, `last_compliance_review_at`.

**Relacionamentos:** muitas referências de empresa.

**Índices e restrições:** nome único; tipos controlados; fonte não implica autorização para coleta automatizada.

## Referências de fonte (`company_source_refs`)

**Finalidade:** ligar uma empresa ao identificador e aos dados observados em uma fonte.

**Obrigatórios:** `id`, `company_id`, `data_source_id`, `observed_at`, `created_at`.

**Opcionais:** `external_id`, `source_url`, `raw_name`, `rating`, `review_count`, `payload_fingerprint`, `last_verified_at`.

**Relacionamentos:** uma empresa e uma fonte.

**Índices e restrições:** único `(data_source_id, external_id)` quando `external_id` existir; índice por empresa/fonte; avaliação e contagens válidas; não armazenar payload bruto indiscriminadamente.

No cadastro manual, a origem obrigatória será representada por uma referência de fonte criada na mesma transação da empresa. A empresa não poderá ser confirmada sem uma referência válida, mas a fonte não implica autorização para coleta automatizada.

## Contatos (`contacts`)

**Finalidade:** guardar canais de contato da empresa ou de uma pessoa vinculada.

**Obrigatórios:** `id`, `company_id`, `contact_type`, `value`, `value_normalized`, `is_primary`, `created_at`.

**Opcionais:** `person_name`, `job_title`, `consent_or_basis_note`, `source_ref_id`, `verified_at`, `invalidated_at`, `notes`.

**Relacionamentos:** empresa obrigatória; referência de fonte opcional.

**Índices e restrições:** índice `(company_id, contact_type)`; unicidade de `(company_id, contact_type, value_normalized)`; somente um principal por empresa/tipo quando aplicável; tipos controlados (`phone`, `email`, `website`, `instagram`, outros aprovados).

## Auditorias de website (`website_audits`)

**Finalidade:** preservar avaliações pontuais da presença e qualidade do website.

**Obrigatórios:** `id`, `company_id`, `contact_id`, `requested_url`, `status`, `findings`, `performed_by_user_id`, `created_at`.

**Opcionais:** `final_url`, `http_status`, `error_code`, `duration_ms`.

**Relacionamentos:** empresa, contato `WEBSITE` e usuário responsável.

**Índices e restrições:** empresa/data; estados `COMPLETED` e `FAILED`; cada execução é imutável. HTML, cabeçalhos brutos e score automático não são armazenados.

## Scores (`opportunity_scores`)

**Finalidade:** registrar avaliações de oportunidade explicáveis ao longo do tempo.

**Obrigatórios:** `id`, `company_id`, `formula_version`, `components` (JSONB), `explanation`, `calculated_by_user_id`, `calculated_at`.

**Opcionais:** `total`, que permanece nulo enquanto algum componente estiver ausente.

**Relacionamentos:** empresa; auditoria e usuário opcionais.

**Índices e restrições:** empresa/data; valor em faixa aprovada; versão obrigatória; componentes validados; avaliações históricas não são sobrescritas. O score atual será obtido pela avaliação mais recente válida.

O score não é necessário para criar, editar, qualificar ou pesquisar uma empresa. A fórmula v1 humana usa adequação 40%, reputação 30% e lacuna digital 30%; consulte `docs/sprint-6-score-policy.md`.

## Atividades comerciais (`commercial_activities`)

**Finalidade:** registrar o histórico cronológico de pesquisa, tentativa de contato, resposta, reunião e mudança de etapa.

**Obrigatórios:** `id`, `company_id`, `activity_type`, `notes`, `performed_by_user_id`, `created_at`.

**Opcionais:** `previous_status`, `new_status`, `outcome` e `next_action_at`.

**Relacionamentos:** empresa, usuário e contato opcional.

**Índices e restrições:** empresa/data; próxima ação; tipo/resultado controlados; histórico preferencialmente append-only; conteúdo sensível minimizado.

## Mensagens geradas (`generated_messages`)

**Finalidade:** armazenar rascunhos futuros produzidos com assistência de IA, sempre sujeitos a revisão humana.

**Obrigatórios:** `id`, `company_id`, `channel`, `status`, `content`, `prompt_template_version`, `created_at`, `created_by_user_id`.

**Opcionais:** `contact_id`, `provider`, `model`, `input_fingerprint`, `reviewed_at`, `reviewed_by_user_id`, `rejection_reason`, `sent_activity_id`.

**Relacionamentos:** empresa, contato, autores/revisores e atividade de envio opcional.

**Índices e restrições:** empresa/status/data; status controlado; envio exige revisão humana registrada; não armazenar prompts com segredos ou dados excessivos; nenhuma implementação no MVP inicial.

## Propostas (`proposals`)

**Finalidade:** versionar propostas comerciais futuras.

**Obrigatórios:** `id`, `company_id`, `proposal_number`, `version`, `status`, `currency`, `created_at`, `created_by_user_id`.

**Opcionais:** `contact_id`, `title`, `scope`, `amount`, `valid_until`, `document_path`, `approved_at`, `sent_at`, `accepted_at`, `rejected_at`.

**Relacionamentos:** empresa, contato, usuário e possíveis atividades.

**Índices e restrições:** `(proposal_number, version)` único; valor não negativo; moeda ISO; transições de estado validadas; arquivos fora do banco com armazenamento e acesso definidos antes da implementação.

## Artefatos de demonstração (`demo_artifacts`)

**Finalidade:** registrar futuras demonstrações associadas a oportunidades selecionadas, sem confundi-las com o website oficial da empresa.

**Obrigatórios previstos:** `id`, `company_id`, `status`, `artifact_type`, `storage_reference`, `created_at`, `created_by_user_id`.

**Opcionais previstos:** `title`, `template_version`, `expires_at`, `published_at`, `removed_at`, `reviewed_at`, `reviewed_by_user_id`, `rights_or_attribution_note`.

**Relacionamentos:** empresa e usuários responsáveis pela criação e revisão.

**Restrições:** publicação exige revisão humana; localização e acesso devem ser protegidos; expiração e remoção devem ser rastreáveis; direitos de marca, conteúdo e assets precisam ser registrados antes da publicação. O armazenamento definitivo será decidido somente na Fase 10.

## Prevenção de empresas duplicadas

Estratégia em camadas:

1. **Identificador forte:** rejeitar ou vincular cadastro com CNPJ normalizado já existente.
2. **Identificador da fonte:** impedir que o mesmo `external_id` da mesma fonte crie duas empresas.
3. **Contatos normalizados:** sinalizar coincidência de telefone, email ou domínio.
4. **Chave geográfica:** comparar nome normalizado + cidade + UF + endereço/CEP quando disponíveis.
5. **Similaridade:** gerar candidatos por similaridade de nome/endereço, sem mesclar automaticamente.
6. **Revisão humana:** apresentar evidências, permitindo manter separado, vincular ou mesclar.
7. **Rastreabilidade:** registrar quem decidiu, quando, quais registros foram envolvidos e permitir correção segura.

Cadastros incompletos não devem ser bloqueados apenas por nomes iguais. A política e os limiares precisam ser aprovados antes da implementação.

## Dados derivados e histórico

- avaliação e quantidade de reviews observadas em fontes devem preservar data e origem;
- `companies` poderá manter uma projeção atual para filtros, derivada de registros históricos;
- score e auditoria são snapshots versionados;
- atividades comerciais não devem ser reescritas para representar um estado novo;
- JSONB será usado apenas para componentes versionados ou metadados variáveis, não como substituto do modelo relacional.

## Pontos pendentes

- necessidade futura de papéis além do usuário administrador inicial;
- avaliação futura da fórmula do score com uso real;
- taxonomia e governança de categorias;
- eventual ajuste da matriz de transições após uso real;
- política de retenção/exclusão;
- limites de similaridade e regras de merge;
- armazenamento futuro de documentos de proposta.
