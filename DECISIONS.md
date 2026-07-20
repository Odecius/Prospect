# Decisões do ABC Prospect

As decisões seguem o formato do `ABC-Development-Standard`. Itens ainda não aprovados aparecem em **Decisões pendentes** e não devem ser presumidos na implementação.

## 2026-07-19 — Projeto independente do website institucional

**Descrição:** O ABC Prospect é um repositório e uma aplicação independentes do website institucional e de outros projetos da ABC Solutions.

**Motivo:** Isolar ciclo de vida, dados, dependências, deploy e riscos.

**Alternativas consideradas:** Incorporar a ferramenta ao site institucional.

**Impacto:** Não haverá compartilhamento automático de código ou assets. Qualquer material reutilizado deverá ser autorizado e ter origem informada.

## 2026-07-19 — Uso interno no início

**Descrição:** A primeira versão será usada internamente por uma pessoa.

**Motivo:** Validar o processo comercial com baixo custo e menor superfície de risco.

**Alternativas consideradas:** Produto multiusuário ou SaaS desde o início.

**Impacto:** A interface e a operação podem ser simples, mas autenticação e proteção de dados continuam obrigatórias.

## 2026-07-19 — Monólito modular

**Descrição:** Backend, interface e persistência formarão um monólito modular com separação interna entre HTTP, aplicação, domínio, persistência e integrações.

**Motivo:** Adequação ao tamanho do MVP e facilidade de desenvolvimento, testes e deploy.

**Alternativas consideradas:** Microsserviços e arquitetura orientada a eventos.

**Impacto:** Um único deploy; módulos devem manter limites claros. Microsserviços, filas, Redis e Kubernetes ficam fora do escopo.

## 2026-07-19 — FastAPI e PostgreSQL

**Descrição:** Python/FastAPI será a plataforma da aplicação; PostgreSQL, SQLAlchemy e Alembic cuidarão da persistência.

**Motivo:** Stack solicitada, madura e adequada à API, validação e evolução do modelo relacional.

**Alternativas consideradas:** Django, .NET e bancos embarcados.

**Impacto:** Testes usarão pytest e deverão incluir integração real com PostgreSQL para consultas e migrations críticas.

## 2026-07-19 — Interface simples renderizada no servidor

**Descrição:** A interface inicial usará Jinja2, HTML, CSS e JavaScript simples.

**Motivo:** Reduzir complexidade e manter foco na validação do fluxo.

**Alternativas consideradas:** React ou outra SPA.

**Impacto:** Framework frontend só poderá ser introduzido mediante necessidade comprovada e nova decisão.

## 2026-07-19 — Desenvolvimento incremental

**Descrição:** O produto evoluirá em fases pequenas, cada uma com critérios de conclusão e limites explícitos.

**Motivo:** Reduzir risco e validar valor antes de automações caras.

**Alternativas consideradas:** Construir desde já o produto completo.

**Impacto:** Itens futuros não autorizam implementação antecipada. O roadmap é direção, não escopo automático.

## 2026-07-19 — Cadastro manual antes de integrações externas

**Descrição:** O MVP começará com dados inseridos manualmente. Fontes externas só serão integradas em fase futura.

**Motivo:** Validar dados e fluxo sem depender de contratos, custos ou permissões de terceiros.

**Alternativas consideradas:** Coleta automatizada desde a primeira versão.

**Impacto:** Nenhum scraping está autorizado. Cada integração exigirá avaliação de termos, segurança, privacidade e limites.

## 2026-07-19 — Nenhum envio em massa e revisão humana obrigatória

**Descrição:** O sistema não enviará contatos comerciais em massa. Qualquer mensagem gerada deverá ser revisada e enviada por ação humana explícita.

**Motivo:** Qualidade comercial, conformidade, prevenção de spam e proteção da reputação.

**Alternativas consideradas:** Campanhas e cadências automáticas.

**Impacto:** Automação futura poderá ajudar a redigir, nunca remover o controle humano sem uma nova decisão formal.

## 2026-07-19 — Foco inicial em empresas brasileiras

**Descrição:** Taxonomias, endereços e validações priorizarão o Brasil no MVP.

**Motivo:** Escopo comercial inicial.

**Alternativas consideradas:** Modelo internacional desde o início.

**Impacto:** O desenho deve evitar bloqueios desnecessários à expansão, mas não implementará requisitos internacionais prematuramente.

## 2026-07-19 — Score explicável e histórico

**Descrição:** Scores serão armazenados como avaliações versionadas, com componentes, fórmula/versão e justificativa.

**Motivo:** Permitir auditoria e evitar que um número sobrescreva o contexto comercial.

**Alternativas consideradas:** Manter apenas o score atual na empresa.

**Impacto:** A fórmula poderá evoluir preservando avaliações anteriores. A fórmula e pesos iniciais ainda dependem de aprovação, mas o score não bloqueia o cadastro, a edição, a qualificação ou a pesquisa de empresas. O cálculo começa somente na Fase 4.

## 2026-07-19 — Estratégia de duplicidade em camadas

**Descrição:** Duplicidades serão prevenidas por identificadores fortes quando disponíveis e sinalizadas por chaves normalizadas/fuzzy para revisão humana.

**Motivo:** Empresas podem chegar de fontes diferentes com nomes e contatos inconsistentes.

**Alternativas consideradas:** Unicidade apenas pelo nome ou mesclagem totalmente automática.

**Impacto:** CNPJ normalizado poderá ser único quando informado; referências de fonte serão únicas por fonte; candidatos ambíguos não serão mesclados automaticamente.

## 2026-07-19 — Branding oficial no rodapé

**Descrição:** A futura interface exibirá no rodapé o selo oficial ABC Solutions, centralizado e responsivo, com texto alternativo e a assinatura **“Developed by Abc Solutions | Built with quality and care”**.

**Motivo:** Cumprir a identidade visual oficial.

**Alternativas consideradas:** Somente texto ou ausência de branding.

**Impacto:** O asset `C:\Projetos\Abc\developed by abc solutions.png` será copiado para este repositório apenas na fase de interface. Nesta etapa ele não foi copiado.

## 2026-07-19 — Documentação com responsabilidades separadas

**Descrição:** Documentos de raiz guardam decisões e especificações; `docs/` contém instruções operacionais concisas e referencia os documentos canônicos.

**Motivo:** Cumprir o padrão oficial sem duplicação desnecessária.

**Alternativas consideradas:** Repetir integralmente a arquitetura e segurança em vários arquivos.

**Impacto:** `ARCHITECTURE.md`, `DATA_MODEL.md`, `SECURITY.md`, `ROADMAP.md` e `DECISIONS.md` são fontes detalhadas; `docs/glossary.md` define termos, `docs/business_rules.md` centraliza regras e `docs/traceability.md` conecta decisões, entidades e fases. Os demais arquivos em `docs/` devem apontar para essas fontes sem duplicá-las integralmente.

## 2026-07-19 — Autenticação local inicial aprovada

**Descrição:** A primeira versão usará uma conta local, senha com Argon2 e sessão assinada em cookie `HttpOnly`, com HTTPS obrigatório em produção.

**Motivo:** Atender ao uso interno por uma pessoa sem introduzir um provedor de identidade antes da validação.

**Impacto:** Todas as rotas de negócio exigirão sessão; o healthcheck permanece público. Formulários mutáveis usam token CSRF. O primeiro usuário será criado por comando explícito e variáveis de ambiente.

## 2026-07-19 — Campos mínimos do cadastro manual aprovados

**Descrição:** O cadastro inicial exigirá nome da empresa, categoria, cidade/UF e origem. CNPJ, website, telefone/email corporativo e observações serão opcionais.

**Motivo:** Permitir registros úteis sem bloquear empresas com dados públicos incompletos.

**Impacto:** A origem continuará obrigatória; contatos pessoais não serão necessários no cadastro mínimo. As regras serão implementadas na Fase 2.

## 2026-07-19 — Estados iniciais do funil aprovados

**Descrição:** Toda empresa começa com `pipeline_status` igual a `NEW`. Os estados permitidos são `NEW`, `QUALIFIED`, `CONTACTED`, `REPLIED`, `MEETING`, `PROPOSAL_SENT`, `NEGOTIATION`, `WON`, `LOST`, `DO_NOT_CONTACT` e `ARCHIVED`.

**Motivo:** Padronizar a posição comercial de cada prospect desde o cadastro e permitir evolução incremental do histórico.

**Alternativas consideradas:** texto livre, ausência de estado inicial ou definição do funil somente após o cadastro.

**Impacto:** `DO_NOT_CONTACT` interrompe novas abordagens e `ARCHIVED` remove o registro do fluxo ativo. As transições detalhadas, reaberturas, tipos de atividade e motivos de encerramento serão aprovados antes da Fase 5.

## 2026-07-19 — Interface operacional mínima nas fases iniciais

**Descrição:** As fases iniciais poderão incluir templates e formulários mínimos para permitir a execução e validação do cadastro manual.

**Motivo:** Um fluxo operacional precisa ser utilizável antes da consolidação visual completa.

**Alternativas consideradas:** concluir as fases de negócio apenas por API ou antecipar todo o design da interface.

**Impacto:** A interface mínima deve ser simples, acessível e renderizada no servidor. Responsividade abrangente, navegação consolidada, estados visuais e branding continuam como critérios da Fase 6.

## 2026-07-19 — Conclusão do produto interno na Fase 13

**Descrição:** O escopo principal do ABC Prospect compreende as Fases 1 a 13. A conclusão aprovada da Fase 13 representa 100% do produto interno planejado.

**Motivo:** Separar a entrega interna validada de uma eventual transformação comercial e multiempresa.

**Alternativas consideradas:** incluir a avaliação SaaS no percentual principal ou deixar o término do projeto indefinido.

**Impacto:** A possível evolução para SaaS é um projeto futuro independente, não uma Fase 14 obrigatória. Melhorias posteriores ao produto interno serão classificadas como manutenção ou novos projetos.

## Decisões pendentes por fase

As pendências abaixo bloqueiam somente a fase indicada e não impedem trabalhos aprovados de fases anteriores.

### Antes de concluir a Fase 2

As decisões iniciais de duplicidade, taxonomia e privacidade foram aprovadas em 2026-07-20 e estão consolidadas em `docs/sprint-3-policies.md`. Contatos, candidatos persistentes e mesclagem permanecem para aprovação detalhada na Sprint 4.

### Antes de iniciar a Fase 4

1. **Score v1:** componentes, pesos, faixas, versão inicial e tratamento de dados ausentes.

### Antes de iniciar a Fase 5

1. **Funil detalhado:** transições permitidas, reaberturas, tipos de atividade, resultados e motivos de encerramento.

### Antes de iniciar a Fase 7

1. **Fontes externas:** avaliação jurídica e técnica individual, termos de uso, método permitido, quotas e proveniência.

### Antes de iniciar a Fase 10

1. **Demonstrações:** armazenamento, controle de acesso, expiração, remoção, publicação e direitos de uso.

### Antes de iniciar a Fase 12

1. **Deploy inicial:** servidor, domínio ou rede privada, proxy reverso, backups, RPO e RTO.

### Antes de iniciar a Fase 13

1. **Critérios de validação:** métricas e período de teste para decidir se a prospecção ficou mais rápida, consistente e útil.

## 2026-07-20 — Fase 1A restrita à infraestrutura

**Descrição:** A Fase 1A implementa somente estrutura de diretórios, ambiente Python, configuração, FastAPI, `/health`, OpenAPI, PostgreSQL/SQLAlchemy, Alembic sem migrations, Docker, Compose, testes, lint, formatação e logging seguro.

**Motivo:** Validar a base técnica antes de introduzir entidades, autenticação ou regras de negócio.

**Alternativas consideradas:** manter a tentativa anterior de autenticação e usuários dentro da fundação técnica.

**Impacto:** autenticação, usuários, migrations, modelos, CRUD, empresas, score, pipeline, serviços, repositórios, integrações e qualquer interface ficam proibidos na Fase 1A. A autenticação local já aprovada permanece uma decisão futura e será implementada somente em etapa posterior explicitamente autorizada.

## 2026-07-20 — Políticas conservadoras da Sprint 3

**Descrição:** foram aprovadas uma taxonomia plana de 15 categorias, a limitação da Sprint 3 a dados empresariais mínimos e uma detecção de duplicidade sem eliminação ou mesclagem automática.

**Motivo:** habilitar o cadastro essencial com baixo risco, explicabilidade e possibilidade de expansão sem antecipar contatos ou automações.

**Alternativas consideradas:** taxonomia livre ou extensa; inclusão imediata de contatos; bloqueio por qualquer semelhança; mesclagem automática.

**Impacto:** CNPJ exato repetido bloqueia o cadastro; nome igual na mesma cidade/UF gera aviso confirmável; contatos e sinais avançados ficam para a Sprint 4. A base legal definitiva e os prazos permanecem sujeitos a validação jurídica antes da produção. A especificação completa está em `docs/sprint-3-policies.md`.
