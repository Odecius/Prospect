# Plano de sprints

Este plano organiza o desenvolvimento do ABC Prospect até a conclusão do Produto Interno ao final da Fase 13. A cadência recomendada é de duas semanas por sprint, podendo ser ajustada mediante decisão documentada.

## Regras de execução

- cada sprint começa somente quando suas decisões bloqueadoras estiverem aprovadas;
- documentação afetada deve ser atualizada antes da implementação correspondente;
- nenhuma funcionalidade fora do escopo do sprint pode ser antecipada;
- cada regra implementada deve possuir testes proporcionais ao risco;
- uma sprint somente termina depois de revisão de segurança, testes e verificação do estado Git;
- pendências não concluídas retornam ao backlog e não são ocultadas;
- o status percentual geral será recalculado e informado somente no encerramento de cada sprint;
- SaaS não integra este plano nem o percentual do Produto Interno.

## Critério do percentual

O percentual representa entregas aceitas do Produto Interno, e não quantidade de código ou tempo transcorrido. Cada sprint possui um peso indicativo proporcional ao valor, risco e esforço esperados. O percentual só é incorporado depois que os critérios de aceite do sprint forem cumpridos.

| Sprint | Tema | Peso indicativo | Acumulado após aceite |
|---:|---|---:|---:|
| 1 | Fundação técnica — Fase 1A | 6% | 6% |
| 2 | Autenticação local — Fase 1B | 6% | 12% |
| 3 | Cadastro essencial | 9% | 21% |
| 4 | Contatos, fontes e duplicidade | 8% | 29% |
| 5 | Pesquisa, filtros e paginação | 7% | 36% |
| 6 | Score de oportunidade | 8% | 44% |
| 7 | Histórico e pipeline comercial | 8% | 52% |
| 8 | Interface interna consolidada | 8% | 60% |
| 9 | Fontes externas autorizadas | 7% | 67% |
| 10 | Auditoria de websites | 7% | 74% |
| 11 | IA para rascunhos | 6% | 80% |
| 12 | Demo Websites | 5% | 85% |
| 13 | Propostas comerciais | 5% | 90% |
| 14 | Deploy seguro | 6% | 96% |
| 15 | Validação comercial e encerramento | 4% | 100% |

Os pesos poderão ser recalibrados antes de uma sprint começar, desde que o total permaneça em 100% e a alteração seja registrada.

## Sprint 1 — Fundação técnica

**Roadmap:** Fase 1A.

**Objetivo:** validar a infraestrutura sem autenticação, entidades ou regras de negócio.

**Entregas:** estrutura de diretórios; Python e dependências; FastAPI; `/health`; OpenAPI; configuração; logging; SQLAlchemy; Alembic sem revisions; Docker; Compose; pytest; Ruff.

**Critérios de aceite:** testes e qualidade passam; servidor responde em `/health`; Compose sobe aplicação e PostgreSQL; healthchecks ficam saudáveis; conexão PostgreSQL é validada; Alembic permanece sem revisions; nenhuma implementação proibida existe.

**Situação:** concluída e aceita em 2026-07-20. Build, aplicação, PostgreSQL, healthchecks, acesso HTTP local e conexão do Alembic ao banco real foram validados; o progresso geral incorporado é 6%.

## Sprint 2 — Autenticação local

**Roadmap:** conclusão da Fase 1.

**Objetivo:** proteger as futuras rotas com uma conta administrativa local.

**Dependências:** aceite da Sprint 1 e aprovação de [`phase-1b.md`](phase-1b.md).

**Entregas propostas:** usuário técnico; migration de autenticação; Argon2; sessão; CSRF; login/logout; criação explícita do administrador; testes de segurança.

**Critérios de aceite:** migration aplica e reverte em PostgreSQL real; senha nunca é persistida ou registrada; sessão e logout funcionam; acessos sem sessão são rejeitados; nenhuma entidade comercial existe.

**Situação:** concluída e aceita em 2026-07-20. Migration, criação explícita de administrador, Argon2, login, sessão, CSRF, logout e proteção reutilizável foram validados; o progresso geral incorporado é 12%.

## Sprint 3 — Cadastro essencial

**Roadmap:** primeira parte da Fase 2.

**Objetivo:** cadastrar, consultar, editar e arquivar empresas com os campos mínimos aprovados.

**Dependências:** taxonomia inicial, privacidade e comportamento básico de duplicidade aprovados.

**Entregas:** categorias; empresas; nome, categoria, cidade, UF e origem obrigatórios; estado inicial `NEW`; validações; auditoria básica; interface operacional mínima.

**Critérios de aceite:** fluxo manual essencial funciona; nenhum cadastro é confirmado sem os campos obrigatórios; dados inválidos geram erros claros; score permanece ausente e não bloqueia operações.

**Situação:** concluída e aceita em 2026-07-20. Cadastro, consulta, edição, arquivamento, taxonomia, origem, validações, duplicidade conservadora, auditoria básica e interface operacional foram validados; o progresso geral incorporado é 21%.

## Sprint 4 — Contatos, fontes e duplicidade

**Roadmap:** conclusão da Fase 2.

**Objetivo:** completar o cadastro manual e tratar registros repetidos com revisão humana.

**Entregas:** contatos; fontes; referências; normalização; CNPJ opcional; restrições fortes; candidatos de duplicidade; fluxo de revisão e mesclagem aprovado.

**Critérios de aceite:** CNPJ e referências repetidos são tratados; casos ambíguos não são mesclados automaticamente; proveniência e decisões permanecem rastreáveis; fluxo completo da Fase 2 é aprovado.

**Situação:** concluída e aceita em 2026-07-21. Contatos normalizados, proveniência avançada, candidatos persistentes, revisão humana, mesclagem auditada, API, interface, migration reversível e PostgreSQL real foram validados; o progresso geral incorporado é 29%.

## Sprint 5 — Pesquisa e filtros

**Roadmap:** Fase 3.

**Objetivo:** localizar rapidamente empresas cadastradas.

**Entregas:** pesquisa textual; filtros combináveis; ordenação; paginação; índices; preservação dos filtros na navegação.

**Critérios de aceite:** resultados corretos e reproduzíveis; consultas cumprem o volume de teste acordado; paginação e filtros possuem testes.

**Situação:** concluída e aceita em 2026-07-21; progresso geral 36%.

## Sprint 6 — Score de oportunidade

**Roadmap:** Fase 4.

**Objetivo:** priorizar empresas com critérios transparentes.

**Dependências:** fórmula, pesos, faixas, arredondamento e dados ausentes aprovados.

**Entregas:** score v1; componentes explicáveis; histórico; recálculo controlado; filtros por faixa.

**Critérios de aceite:** exemplos são validados; avaliações antigas não são sobrescritas; ausência de dados é explícita; resultado é explicável e testado.

**Situação:** concluída e aceita em 2026-07-21 com fórmula `v1-human-40-30-30`; progresso geral 44%.

## Sprint 7 — Histórico e pipeline

**Roadmap:** Fase 5.

**Objetivo:** acompanhar atividades, estados e próximos passos.

**Dependências:** matriz de transições, reaberturas, atividades e encerramentos aprovada.

**Entregas:** timeline; atividades; transições controladas; motivos; lembretes internos; próximos passos.

**Critérios de aceite:** toda ação possui ator e horário; transições inválidas são recusadas; `DO_NOT_CONTACT` impede abordagem; arquivamento preserva histórico.

**Situação:** concluída e aceita em 2026-07-21; progresso geral 52%.

## Sprint 8 — Interface interna

**Roadmap:** Fase 6.

**Objetivo:** consolidar a experiência operacional criada nas fases anteriores.

**Entregas:** navegação; formulários acessíveis; estados visuais; responsividade; CSS; branding e selo oficial.

**Critérios de aceite:** fluxos funcionam por teclado; desktop, tablet e celular são verificados; não há overflow; branding, alt text e assinatura estão corretos.

**Situação:** concluída e aceita em 2026-07-21, validada em 375, 768 e 1440 px; progresso geral 60%.

## Sprint 9 — Fontes externas autorizadas

**Roadmap:** Fase 7.

**Objetivo:** reduzir entrada manual somente por integrações permitidas.

**Dependências:** avaliação jurídica e técnica individual de cada fonte.

**Entregas:** primeiro adaptador aprovado; limites; retry/backoff; proveniência; importação revisável.

**Critérios de aceite:** termos e quotas são respeitados; falhas não corrompem dados; importações e mesclagens exigem confirmação humana.

**Situação:** concluída e aceita em 2026-07-21 com Google Places API (New), pesquisa temporária, limites, atribuição, revisão humana e persistência exclusiva do Place ID; progresso geral 67%.

## Sprint 10 — Auditoria de websites

**Roadmap:** Fase 8.

**Objetivo:** avaliar sinais técnicos e comerciais de websites.

**Entregas:** critérios versionados; execução controlada; snapshots; limites por domínio; explicação dos resultados.

**Critérios de aceite:** auditorias são reproduzíveis; falhas técnicas são diferenciadas de ausência ou baixa qualidade; nenhum comportamento de pentest é introduzido.

**Situação:** concluída e aceita em 2026-07-22 com consulta exclusiva da página inicial cadastrada, limites de rede e tamanho, bloqueio de destinos privados, snapshots imutáveis e resultados explicáveis; progresso geral 74%.

## Sprint 11 — IA para rascunhos

**Roadmap:** Fase 9.

**Objetivo:** preparar mensagens para revisão humana.

**Dependências:** provedor, minimização, retenção, custos e política de dados aprovados.

**Entregas:** templates versionados; provider configurável; geração de rascunho; revisar, rejeitar e aprovar; logs seguros.

**Critérios de aceite:** nenhuma mensagem é enviada automaticamente; dados enviados ao provedor são conhecidos; revisão humana é obrigatória e auditável.

**Situação:** concluída e aceita em 2026-07-22 com OpenAI Responses API desativada por padrão, `store=false`, contexto empresarial minimizado, saída estruturada, histórico imutável e revisão humana sem qualquer operação de envio; progresso geral 80%.

## Sprint 12 — Demo Websites

**Roadmap:** Fase 10.

**Objetivo:** gerar demonstrações controladas para oportunidades selecionadas.

**Dependências:** armazenamento, acesso, expiração, remoção e direitos aprovados.

**Entregas:** templates; criação isolada; revisão; expiração; remoção; atribuição de assets.

**Critérios de aceite:** demonstração não se confunde com site oficial; publicação exige aprovação; direitos e ciclo de vida são rastreáveis.

## Sprint 13 — Propostas comerciais

**Roadmap:** Fase 11.

**Objetivo:** criar e acompanhar propostas versionadas.

**Dependências:** modelo comercial, numeração, estados, armazenamento e aprovação definidos.

**Entregas:** propostas; versões; itens; valores; validade; documento protegido.

**Critérios de aceite:** valores e versões são auditáveis; envio exige revisão; acesso e armazenamento são protegidos.

## Sprint 14 — Deploy seguro

**Roadmap:** Fase 12.

**Objetivo:** operar o Produto Interno em Ubuntu Server.

**Dependências:** servidor, acesso, domínio, proxy, secrets, backups, RPO e RTO aprovados.

**Entregas:** imagem versionada; proxy/HTTPS; secrets; backups; logs; monitoramento; rollback; runbook.

**Critérios de aceite:** restore e rollback são testados; PostgreSQL não é público; acesso é restrito; checklist pós-deploy passa.

## Sprint 15 — Validação comercial e encerramento

**Roadmap:** Fase 13.

**Objetivo:** medir o valor do produto interno e encerrar formalmente o projeto principal.

**Dependências:** métricas, período e amostra aprovados.

**Entregas:** período de uso; métricas; feedback; avaliação do score; melhorias priorizadas; decisão final.

**Critérios de aceite:** resultados suficientes e documentados; pendências críticas resolvidas; decisão de continuar, corrigir ou interromper registrada; Produto Interno declarado 100% concluído.

## Encerramento de cada sprint

Cada entrega final de sprint deve informar:

1. objetivo e escopo realizado;
2. arquivos alterados;
3. decisões e regras atendidas;
4. testes e verificações executados;
5. riscos, limitações e pendências;
6. estado Git;
7. percentual incorporado e percentual geral atualizado;
8. próximo sprint proposto.
