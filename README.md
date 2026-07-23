# ABC Prospect

> Developed by Abc Solutions | Built with quality and care

## Visão geral

O **ABC Prospect** é uma ferramenta interna da ABC Solutions para localizar, cadastrar, avaliar e organizar empresas com boa reputação e presença digital fraca, especialmente empresas sem website.

O projeto é independente do website institucional e dos demais projetos da ABC Solutions. Nenhum código ou dado de outro projeto faz parte deste repositório.

## Problema

A prospecção manual dispersa informações entre buscas, anotações e contatos, dificultando priorização e acompanhamento. O ABC Prospect deverá reunir evidências comerciais, calcular oportunidades de forma explicável e preservar a revisão humana antes de qualquer abordagem.

## Status atual

As Sprints 1 a 13 estão implementadas e validadas, totalizando 90% do Produto Interno. Além da fundação, autenticação e cadastro, a aplicação oferece contatos, duplicidade revisável, pesquisa, score explicável, pipeline, interface responsiva, Google Places API (New), auditoria controlada de websites, conteúdo comercial assistido, dashboard e exportação CSV manual e auditada.

## Stack planejada

- Python e FastAPI;
- PostgreSQL;
- SQLAlchemy e Alembic;
- pytest;
- Docker e Docker Compose;
- configuração por variáveis de ambiente;
- Jinja2, HTML, CSS e JavaScript simples para a interface interna.

React e outros frameworks frontend não fazem parte do plano inicial.

## Escopo do produto interno

- acesso autenticado para uso interno;
- cadastro e edição manual de empresas e contatos, com categoria, cidade, UF e origem obrigatórias;
- funil comercial iniciado em `NEW`;
- filtros e pesquisa;
- score de oportunidade simples, versionado e explicável;
- histórico de atividades comerciais;
- prevenção e tratamento de possíveis duplicidades;
- diagnóstico comercial e rascunhos de proposta assistidos por IA, sempre sujeitos a revisão humana;
- dashboard de prospecção, segmentação e exportação ou cópia manual;
- interface responsiva com o selo oficial da ABC Solutions no rodapé.

## Fora do escopo inicial

- coleta automatizada ou scraping de plataformas externas;
- envio automático ou em massa de mensagens;
- geração de websites, landing pages, demonstrações, código, logos ou qualquer publicação/hosting;
- envio automático de mensagens ou propostas e tomada autônoma de decisões comerciais;
- envio automático ou em massa de conteúdo gerado por IA;
- microsserviços, Kubernetes, Redis e filas;
- oferta pública ou modelo SaaS antes de um novo projeto formal;
- deploy de produção antes da Fase 12.

## Evolução planejada

O desenvolvimento seguirá fases pequenas. As Fases 1 a 13 compõem o produto interno e a conclusão da Fase 13 representa 100% do escopo principal. Um eventual gerador de websites ou demonstrações é outro produto, com responsabilidade, arquitetura e repositório próprios; não integra este roadmap nem seu percentual. A eventual evolução do ABC Prospect para SaaS também depende de um projeto futuro independente. Consulte [ROADMAP.md](ROADMAP.md).

## Critérios de conclusão do MVP

O MVP estará concluído quando uma pessoa autenticada puder:

1. localizar ou cadastrar potenciais clientes;
2. verificar a existência e a adequação básica da presença digital;
3. classificar a oportunidade;
4. consultar score acompanhado de justificativa;
5. gerar diagnóstico comercial;
6. gerar rascunho de proposta;
7. editar, aprovar ou rejeitar o rascunho;
8. consultar o histórico das ações;
9. operar com bloqueios como `DO_NOT_CONTACT` efetivamente aplicados;
10. utilizar o sistema de forma segura e estável.

Os itens 1–9 possuem base implementada, com dashboard e exportação manual controlada. Preparação operacional e validação de uso real permanecem nas Sprints 14–15. O progresso aceito é 90%.

## Arquitetura e dados

- Arquitetura proposta: [ARCHITECTURE.md](ARCHITECTURE.md)
- Modelo de dados: [DATA_MODEL.md](DATA_MODEL.md)
- Contexto consolidado: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)
- Decisões: [DECISIONS.md](DECISIONS.md)
- Segurança: [SECURITY.md](SECURITY.md)
- Rastreabilidade entre decisões, dados e fases: [docs/traceability.md](docs/traceability.md)
- Glossário oficial: [docs/glossary.md](docs/glossary.md)
- Regras de negócio centralizadas: [docs/business_rules.md](docs/business_rules.md)
- Plano de execução em sprints: [docs/sprint_plan.md](docs/sprint_plan.md)

## Operação e desenvolvimento

As instruções operacionais estão em `docs/`. O Compose, os healthchecks, o acesso HTTP local, a migration de autenticação e o ciclo de login/sessão/logout foram validados com PostgreSQL real. O deployment permanece planejado para a Fase 12.

## Branding

A interface exibe no rodapé o selo oficial da ABC Solutions, centralizado e responsivo, com texto alternativo descritivo e a assinatura **“Developed by Abc Solutions | Built with quality and care”**.

O selo oficial está mantido localmente em `app/static/assets/abc-solutions-footer.png`, com origem registrada em `docs/branding.md`.

## Referência de desenvolvimento

Este projeto segue o `ABC-Development-Standard`, consultado somente para padrões de processo, documentação, arquitetura, segurança, testes e identidade visual.
