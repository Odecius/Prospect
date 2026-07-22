# Changelog

## 2026-07-22 — Auditoria controlada de websites (Sprint 10)

- adicionados snapshots imutáveis de auditoria vinculados ao website cadastrado e ao ator;
- implementada consulta única da página inicial, sem JavaScript, assets, links ou comportamento de pentest;
- adicionados bloqueio de redes privadas/reservadas, portas restritas, limite de redirecionamentos, timeout, tamanho máximo, rate limit e cooldown;
- persistidos somente status, duração e sinais explicáveis, sem HTML ou cabeçalhos brutos;
- auditoria automaticamente desativada em produção até confirmação de controle de saída;
- adicionadas API, interface, migration reversível, política e testes;
- progresso geral elevado de 67% para 74%.

## 2026-07-21 — Google Places API (New) (Sprint 9)

- implementadas abstração de provedor, cliente HTTP oficial, serviço e API interna;
- adicionadas busca por termo/cidade/UF/região, paginação assinada, timeout, retry e limite de chamadas;
- adicionada revisão humana com vinculação exclusiva do Place ID, sem persistir conteúdo Google restrito;
- adicionadas atribuição Google Maps, páginas de termos/privacidade e documentação de custo/conformidade;
- adicionada migration reversível da fonte Google e testes totalmente simulados;
- progresso geral elevado de 60% para 67%.

## 2026-07-21 — Pesquisa, score, pipeline e interface (Sprints 5–8)

- adicionadas pesquisa normalizada, filtros, ordenação, paginação e índices;
- adicionado score humano v1, explicável, versionado e histórico;
- adicionadas atividades, próximos passos e transições auditadas com proteção `DO_NOT_CONTACT`;
- consolidada a interface responsiva, acessível e com branding oficial local;
- validados 31 testes, Ruff, PostgreSQL, migrations e breakpoints móvel, tablet e desktop;
- progresso geral elevado de 29% para 60%; Sprint 9 bloqueada por avaliação jurídica e técnica obrigatória da fonte.

## 2026-07-21 — Contatos, fontes e duplicidade (Sprint 4)

- adicionados contatos corporativos normalizados para telefone, email, website e Instagram, com invalidação lógica e contato principal por tipo;
- ampliada a proveniência com identificador externo, nome observado e última verificação;
- adicionados candidatos persistentes de duplicidade, sinais explicáveis e revisão humana obrigatória;
- implementada mesclagem explícita e auditada, sem exclusão física, preservando contatos e fontes conflitantes no cadastro arquivado;
- adicionadas API e interface operacional para contatos, revisão e mesclagem;
- validados Ruff, 23 testes, ciclo reversível da migration `20260721_0003`, PostgreSQL real e endpoint de saúde;
- incorporados os 8% da Sprint 4, totalizando 29% do Produto Interno.

## 2026-07-20 — Cadastro essencial (Sprint 3)

- aprovadas e documentadas as políticas conservadoras de taxonomia, privacidade/LGPD e duplicidade;
- adicionadas 15 categorias controladas, quatro origens manuais e migration reversível;
- implementados cadastro, consulta, edição e arquivamento de empresas com estado inicial `NEW`;
- adicionadas normalização de CNPJ, UF e nome, bloqueio por CNPJ e confirmação de provável duplicidade;
- adicionada interface operacional mínima autenticada e responsiva;
- validados testes, migration, fluxo HTTP real e interface no navegador; dados fictícios removidos;
- incorporados os 9% da Sprint 3, totalizando 21% do Produto Interno.

## 2026-07-20 — Autenticação local (Sprint 2)

- adicionados utilizador técnico e migration reversível exclusiva de autenticação;
- implementados hash Argon2, sessão assinada de oito horas, cookie seguro por ambiente e proteção CSRF;
- adicionados `/auth/login`, `/auth/logout`, `/auth/session` e dependência reutilizável de autenticação;
- adicionado comando explícito e não duplicável para criação do primeiro administrador;
- desativadas OpenAPI, Swagger UI e ReDoc em produção;
- validados migration, criação temporária do administrador e ciclo HTTP real; a conta fictícia foi removida;
- incorporados os 6% da Sprint 2, totalizando 12% do Produto Interno.

## 2026-07-20 — Validação da Sprint 1

- validado o build da aplicação e o PostgreSQL real com Docker Compose;
- confirmados os healthchecks da aplicação e do banco, o acesso local a `/health` e a conexão do Alembic sem revisions;
- separada a rede HTTP da rede interna do banco para publicar somente `127.0.0.1:8000` e manter o PostgreSQL não exposto;
- incorporados os 6% da Sprint 1; a Fase 1B permanece dependente de aprovação explícita.

## Em desenvolvimento — 2026-07-19

- criada a fundação FastAPI com configuração tipada e healthcheck;
- adicionada autenticação local com Argon2, sessão assinada e proteção CSRF;
- adicionados PostgreSQL, SQLAlchemy, Alembic, migration inicial e criação explícita do administrador;
- adicionados Dockerfile, Docker Compose, arquivos seguros de ambiente e testes iniciais.
- alinhados arquitetura, modelo de dados, roadmap, decisões e documentos auxiliares;
- definidos campos obrigatórios, estados do funil, interface operacional mínima e conclusão do produto interno na Fase 13;
- separada a eventual evolução SaaS como projeto futuro independente.
- adicionada matriz de rastreabilidade entre decisões, entidades e fases.
- adicionados glossário oficial e documento central de regras de negócio.

## Em desenvolvimento — 2026-07-20

- aprovada a Fase 1A restrita à infraestrutura técnica;
- adiada a autenticação e proibidas entidades, migrations, CRUD, regras de negócio e interface durante a Fase 1A.
- removidas a tentativa anterior de autenticação, usuários, migration, script administrativo e templates HTML;
- configurados FastAPI, `/health`, OpenAPI, logging, SQLAlchemy, Alembic sem revisions, Docker, Compose, pytest, Ruff e estrutura definitiva de diretórios.
- documentada a proposta da Fase 1B de autenticação local, ainda sem autorização de implementação.
- criado o plano de 15 sprints até a conclusão do Produto Interno na Fase 13.

Todas as mudanças relevantes deste projeto serão registradas neste arquivo.

## [Não lançado]

### Adicionado — 2026-07-19

- documentação inicial do produto, arquitetura, roadmap, tarefas, decisões, segurança, IA e modelo de dados;
- contexto consolidado e notas de continuidade;
- guias operacionais planejados em `docs/`;
- exigência de branding oficial da ABC Solutions para a futura interface;
- adoção do `ABC-Development-Standard` como referência oficial;
- branch local principal renomeada de `master` para `main`.

### Observação histórica

Na etapa documental inicial ainda não existiam código, dependências, banco de dados, migration, integração ou deploy. A fundação técnica foi criada posteriormente; o deployment e as integrações externas continuam inexistentes e fora da fase atual.
