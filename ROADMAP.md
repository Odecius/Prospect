# Roadmap do ABC Prospect

O roadmap indica sequência e critérios, mas não autoriza automaticamente a implementação de fases futuras. O escopo principal do produto interno compreende as Fases 1 a 13. A conclusão da Fase 13 encerra o projeto interno planejado e representa 100% do progresso principal.

A avaliação de uma possível evolução para SaaS é uma iniciativa futura independente. Ela não integra o percentual, os critérios de conclusão ou o compromisso de entrega do produto interno.

## Fase 1 — Fundação técnica

**Objetivo:** estabelecer uma base executável, segura e testável.

**Entregáveis:** estrutura monolítica modular; FastAPI; configuração; PostgreSQL/SQLAlchemy; Alembic; pytest; Docker Compose; healthcheck; autenticação mínima aprovada; documentação operacional.

**Critérios de conclusão:** ambiente sobe de forma reproduzível; migration inicial aplica e reverte em teste; autenticação protege rotas; separação entre HTTP, serviços e persistência está aplicada; testes e revisão de segurança passam; nenhum segredo rastreado.

**Riscos:** excesso de abstração, configuração insegura, divergência entre ambientes.

**Fora do escopo:** cadastro completo, integrações, score, IA e deploy de produção.

### Fase 1A — Infraestrutura técnica

**Escopo autorizado:** estrutura definitiva; ambiente Python e dependências; configuração por variáveis de ambiente; aplicação FastAPI; endpoint `/health`; OpenAPI; PostgreSQL/SQLAlchemy; Alembic configurado sem migrations; Docker e Compose; logging seguro; pytest; lint e formatação.

**Critérios de conclusão:** aplicação e testes executam de forma reproduzível; `/health` responde sem consultar entidades de negócio; configuração do PostgreSQL é validada; Alembic carrega metadata vazia e não possui revisions; logs não contêm dados sensíveis; árvore e dependências estão documentadas.

**Proibido nesta etapa:** autenticação, usuários, migrations, modelos de negócio, CRUD, empresas, score, pipeline, serviços, repositórios, integrações, IA e interface.

Os demais entregáveis da Fase 1, incluindo autenticação mínima, dependem de autorização posterior e não fazem parte da Fase 1A.

### Fase 1B — Autenticação local

O escopo aprovado está em [`docs/phase-1b.md`](docs/phase-1b.md). A implementação foi concluída e validada com PostgreSQL real em 2026-07-20.

## Fase 2 — Cadastro manual de empresas

**Objetivo:** permitir criar, consultar, editar e arquivar prospects manualmente.

**Entregáveis:** empresas, categorias, contatos, fontes e referências; categoria, cidade, UF e origem obrigatórias; status inicial `NEW`; validações; prevenção inicial de duplicidade; trilha básica de alterações; interface operacional mínima para executar o cadastro manual.

**Critérios de conclusão:** o fluxo manual de criar, consultar, editar e arquivar funciona pela interface operacional mínima; campos e erros são claros; CNPJ e referências de fonte duplicados são tratados; testes cobrem regras críticas; nenhuma empresa é confirmada sem categoria, cidade, UF e origem.

**Riscos:** modelo excessivo, dados inconsistentes, coleta desnecessária de dados pessoais.

**Fora do escopo:** design completo da interface, importação em massa, scraping, score automático e envio de mensagens.

## Fase 3 — Filtros e pesquisa

**Objetivo:** localizar rapidamente empresas por geografia, categoria e sinais comerciais.

**Entregáveis:** pesquisa textual; filtros combináveis; ordenação; paginação; consultas indexadas.

**Critérios de conclusão:** resultados corretos e reproduzíveis; desempenho aceitável com volume de teste acordado; filtros preservados na navegação.

**Riscos:** normalização insuficiente e consultas lentas.

**Fora do escopo:** busca geoespacial avançada, recomendação por IA e fontes externas.

## Fase 4 — Score de oportunidade

**Objetivo:** priorizar prospects com critérios transparentes.

**Entregáveis:** fórmula v1 aprovada; componentes visíveis; cálculo versionado; recálculo controlado; filtros por faixa.

**Critérios de conclusão:** exemplos de negócio validados; dados ausentes tratados; histórico preservado; resultado explicável e testado.

**Riscos:** pesos enviesados, falsa precisão e baixa qualidade de dados.

**Fora do escopo:** machine learning, decisão autônoma e alteração silenciosa da fórmula.

## Fase 5 — Histórico comercial

**Objetivo:** acompanhar ações, resultados e próximos passos.

**Entregáveis:** timeline; tipos de atividade; estados do funil; lembretes internos; registro de revisão/contato humano.

**Critérios de conclusão:** cada ação relevante tem ator e horário; próximos passos podem ser filtrados; transições inválidas são impedidas.

**Riscos:** excesso de dados livres e exposição de conteúdo sensível.

**Fora do escopo:** CRM completo, discador, email automático e cadências em massa.

## Fase 6 — Interface interna

**Objetivo:** tornar os fluxos anteriores eficientes em desktop, tablet e celular.

**Entregáveis:** consolidação dos templates Jinja2 criados nas fases anteriores; navegação coerente; formulários acessíveis; estados de carregamento/erro; CSS responsivo; selo oficial no rodapé.

**Critérios de conclusão:** todos os fluxos principais acumulados funcionam por teclado e nos tamanhos acordados; não há overflow; navegação e feedback visual são consistentes; rodapé exibe selo centralizado, responsivo, com alt text e assinatura oficial.

**Riscos:** interface crescer sem sistema visual e regressões de acessibilidade.

**Fora do escopo:** SPA, design público, app móvel e novo branding.

## Fase 7 — Integração com fontes externas

**Objetivo:** reduzir entrada manual somente por meios autorizados.

**Entregáveis:** avaliação jurídica/técnica por fonte; adaptador isolado; limites, retry/backoff; proveniência; importação revisável.

**Critérios de conclusão:** termos e método aprovados; quotas respeitadas; falhas não corrompem dados; usuário confirma candidatos/mesclas.

**Riscos:** violação de termos, bloqueio, custo, dados incorretos e privacidade.

**Fora do escopo:** scraping não autorizado e coleta ilimitada.

## Fase 8 — Auditoria de websites

**Objetivo:** avaliar sinais técnicos e comerciais de sites existentes.

**Entregáveis:** critérios versionados; execução controlada; snapshots; explicação dos achados; limites por domínio.

**Critérios de conclusão:** auditorias são reproduzíveis, respeitam limites e distinguem falha técnica de ausência/baixa qualidade.

**Riscos:** falsos positivos, carga indevida e interpretação legal de conteúdo.

**Fora do escopo:** pentest, exploração de vulnerabilidades e monitoramento contínuo.

## Fase 9 — IA para mensagens

**Objetivo:** preparar rascunhos personalizados para revisão humana.

**Entregáveis:** templates versionados; minimização de dados; provider configurável; workflow de revisar/rejeitar/aprovar; custos e logs seguros.

**Critérios de conclusão:** nenhuma mensagem sai sem ação humana; conteúdos de teste cumprem políticas; dados enviados e retenção são conhecidos.

**Riscos:** alucinação, vazamento, tom inadequado, spam e dependência de fornecedor.

**Fora do escopo:** envio automático, campanhas em massa e decisão autônoma.

## Fase 10 — Diagnóstico comercial e rascunho de proposta

**Objetivo:** transformar evidências já registradas em diagnóstico comercial explicável e rascunho de proposta para revisão humana.

**Entregáveis:** tipos e prompts versionados; contexto empresarial minimizado; diagnóstico e proposta em formato estruturado; edição, aprovação e rejeição auditáveis; cópia manual.

**Critérios de conclusão:** cada afirmação deriva de dados e auditorias identificáveis; nenhuma saída é enviada ou publicada; revisão humana é obrigatória; `DO_NOT_CONTACT` é respeitado; versões permanecem auditáveis.

**Riscos:** alucinação, inferência indevida, exposição de dados, tom inadequado e proposta comercial inconsistente.

**Fora do escopo:** geração de sites, landing pages, código, logos, publicação, envio automático, precificação autônoma, assinatura ou aceite.

**Situação:** concluída em 2026-07-22 pela Sprint 12, sem nova entidade e com revisão humana obrigatória.

## Fase 11 — Dashboard, segmentação e exportação manual

**Objetivo:** consolidar a operação diária do MVP sem introduzir automação de contato.

**Entregáveis:** indicadores do funil e da qualidade dos dados; filtros úteis à prospecção; lista priorizada explicável; exportação limitada e cópia manual com auditoria e respeito ao acesso.

**Critérios de conclusão:** indicadores reconciliam com os registros; filtros são reproduzíveis; exportações exigem ação humana, aplicam minimização e não incluem envio; `DO_NOT_CONTACT` permanece visível e respeitado.

**Riscos:** exportação excessiva, interpretação incorreta dos indicadores e exposição de dados pessoais.

**Fora do escopo:** BI genérico, campanhas, cadências, disparos, CRM completo ou automação de decisões.

**Situação:** concluída em 2026-07-23 pela Sprint 13, com exportação manual minimizada e auditada.

## Fase 12 — Deploy no servidor

**Objetivo:** operar com segurança em Ubuntu Server.

**Entregáveis:** imagem versionada; proxy/HTTPS; secrets; backups; logs/rotação; healthcheck; monitoramento mínimo; rollback; runbook.

**Critérios de conclusão:** restore e rollback testados; banco não público; acesso restrito; checklist pós-deploy aprovado.

**Riscos:** indisponibilidade, perda de dados, exposição pública e configuração divergente.

**Fora do escopo:** Kubernetes, alta disponibilidade complexa e deploy multi-região.

**Situação:** preparação de software concluída em 2026-07-23 pela Sprint 14. Artefatos e recuperação foram validados sem tocar servidor ou dados reais. O deploy efetivo depende das decisões externas e do checklist no host.

## Fase 13 — Validação comercial

**Objetivo:** medir se o produto melhora a seleção e o acompanhamento de prospects.

**Entregáveis:** métricas aprovadas; período de teste; feedback; análise de qualidade do score; lista priorizada de melhorias.

**Critérios de conclusão:** dados suficientes para decidir continuar, corrigir ou interromper; resultados documentados sem métricas de vaidade; pendências críticas de segurança e operação resolvidas; decisão de encerramento do projeto interno registrada.

**Riscos:** amostra pequena, viés de seleção e incentivos para aumentar volume/spam.

**Fora do escopo:** expansão antes de evidência e automação baseada apenas em volume.

**Situação:** protocolo e instrumentação preparados em 2026-07-23. Execução do piloto, feedback e decisão final permanecem pendentes; o projeto não é declarado concluído antecipadamente.

Ao cumprir esses critérios, o ABC Prospect interno é considerado concluído. Melhorias posteriores serão tratadas como manutenção ou novos projetos, sem reabrir automaticamente o roadmap principal.

## Produto futuro separado — geração de websites ou demonstrações

Qualquer ferramenta para gerar websites, landing pages, demonstrações, código, logos, hosting ou publicação pertence a um produto futuro separado do ABC Prospect. Ela exigirá responsabilidade de produto, arquitetura, avaliação jurídica e repositório próprios. Não há sprint ativa, entidade, endpoint, migration ou percentual reservado para esse produto neste roadmap.

## Projeto futuro — Possível evolução para SaaS

**Relação com o produto interno:** iniciativa independente, não incluída no escopo principal nem no cálculo de progresso das Fases 1 a 13.

**Objetivo:** avaliar, não presumir, a transformação em produto multiempresa.

**Entregáveis:** pesquisa de mercado; requisitos multi-tenant; modelo comercial; análise legal, segurança, suporte, custos e migração.

**Critérios de conclusão:** decisão formal de avançar ou permanecer interno; isolamento de tenants e operação sustentável demonstrados antes de oferta pública.

**Riscos:** grande aumento de complexidade, compliance, suporte e segurança.

**Fora do escopo:** implementar SaaS como extensão direta do MVP sem redesenho aprovado.
