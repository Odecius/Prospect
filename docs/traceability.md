# Matriz de rastreabilidade

Este documento conecta decisões aprovadas às especificações e fases do ABC Prospect. Ele não substitui as fontes canônicas: [`../DECISIONS.md`](../DECISIONS.md) registra decisões, [`../DATA_MODEL.md`](../DATA_MODEL.md) define o modelo conceitual, [`../ARCHITECTURE.md`](../ARCHITECTURE.md) define responsabilidades, [`../ROADMAP.md`](../ROADMAP.md) define sequência e critérios de conclusão, [`glossary.md`](glossary.md) define os termos oficiais e [`business_rules.md`](business_rules.md) centraliza as regras de negócio.

## Decisões aprovadas

| Decisão | Arquitetura ou modelo relacionado | Fase principal | Estado |
|---|---|---:|---|
| Projeto independente do website institucional | Repositório, dados, deploy e assets isolados | Todas | Aprovada |
| Uso interno inicialmente por uma pessoa | Autenticação local e operação simplificada | 1–13 | Aprovada |
| Monólito modular | HTTP → serviços → domínio → repositórios → PostgreSQL | 1 | Aprovada |
| FastAPI e PostgreSQL | FastAPI, SQLAlchemy, Alembic, pytest e Compose | 1 | Aprovada |
| Interface renderizada no servidor | Jinja2, HTML, CSS e JavaScript simples | 2–6 | Aprovada |
| Desenvolvimento incremental | Cada fase possui entregáveis, critérios e limites próprios | 1–13 | Aprovada |
| Cadastro manual antes de fontes externas | `companies`, `categories`, `data_sources`, `company_source_refs` e `contacts` | 2 | Aprovada |
| Nenhum envio em massa | Atividades e mensagens exigem revisão e ação humana | 5 e 9 | Aprovada |
| Foco inicial no Brasil | `country_code=BR`, cidade e UF obrigatórias | 2 | Aprovada |
| Score explicável e histórico | `opportunity_scores` versionados e opcionais para a empresa | 4 | Aprovada |
| Duplicidade em camadas | CNPJ e referência de fonte fortes; candidatos ambíguos revisados por pessoa | 2 | Aprovada; regras operacionais pendentes |
| Branding oficial | Asset local, rodapé responsivo, alt text e assinatura oficial | 6 | Aprovada |
| Autenticação local inicial | `users.password_hash`, Argon2, sessão e CSRF | 1 | Aprovada |
| Campos mínimos do cadastro | Nome, categoria, cidade, UF e origem; demais campos opcionais | 2 | Aprovada |
| Estados iniciais do funil | `pipeline_status` controlado e iniciado em `NEW` | 2 e 5 | Aprovada; transições detalhadas pendentes |
| Interface operacional mínima | Formulários mínimos antecipados; consolidação visual mantida na Fase 6 | 2–6 | Aprovada |
| Conclusão do produto interno | Fases 1–13 representam 100%; SaaS é projeto futuro | 13 | Aprovada |
| Fase 1A restrita à infraestrutura | FastAPI, `/health`, OpenAPI, PostgreSQL/SQLAlchemy, Alembic sem revisions, Docker, testes e logs | 1A | Aprovada |

## Regras essenciais por entidade

| Entidade | Regra rastreável | Decisão ou fase de origem |
|---|---|---|
| `users` | Email único, senha Argon2 e estado controlado | Autenticação local; Fase 1 |
| `companies` | Nome, categoria, cidade, UF, origem e `pipeline_status` obrigatórios | Campos mínimos e estados do funil; Fase 2 |
| `companies` | Estado inicial `NEW` | Estados iniciais do funil; Fase 2 |
| `company_source_refs` | Ao menos uma referência criada com o cadastro | Origem obrigatória; Fase 2 |
| `opportunity_scores` | Ausência de score não impede operações da empresa | Score posterior; Fase 4 |
| `commercial_activities` | Ator e horário preservados; transições controladas | Histórico comercial; Fase 5 |
| `generated_messages` | Nenhuma mensagem sai sem revisão e ação humana | Revisão humana; Fase 9 |
| `demo_artifacts` | Revisão, expiração, remoção e direitos rastreáveis | Demonstrações; Fase 10 |
| `proposals` | Numeração e versões auditáveis | Propostas; Fase 11 |

## Bloqueios documentais por fase

| Fase | Decisão ainda necessária | O que permanece liberado |
|---:|---|---|
| 2 | Duplicidade inicial, taxonomia e privacidade | Conclusão e validação da Fase 1 |
| 4 | Fórmula, pesos, faixas e dados ausentes do score | Cadastro, pesquisa e filtros sem score |
| 5 | Transições, reaberturas, atividades e encerramentos | Fases 1–4 aprovadas |
| 7 | Avaliação jurídica e técnica de cada fonte | Operação manual interna |
| 10 | Armazenamento, acesso, expiração e direitos das demonstrações | Fases 1–9 aprovadas |
| 12 | Infraestrutura, acesso, backups, RPO e RTO | Desenvolvimento e testes locais |
| 13 | Métricas e período de validação | Fases anteriores aprovadas |

## Regra de precedência

Em caso de divergência, prevalece a decisão mais recente registrada em `DECISIONS.md`. A alteração deve então ser refletida em `DATA_MODEL.md`, `ARCHITECTURE.md`, `ROADMAP.md` e nesta matriz antes de qualquer implementação relacionada.
