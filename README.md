# ABC Prospect

> Developed by Abc Solutions | Built with quality and care

## Visão geral

O **ABC Prospect** é uma ferramenta interna da ABC Solutions para localizar, cadastrar, avaliar e organizar empresas com boa reputação e presença digital fraca, especialmente empresas sem website.

O projeto é independente do website institucional e dos demais projetos da ABC Solutions. Nenhum código ou dado de outro projeto faz parte deste repositório.

## Problema

A prospecção manual dispersa informações entre buscas, anotações e contatos, dificultando priorização e acompanhamento. O ABC Prospect deverá reunir evidências comerciais, calcular oportunidades de forma explicável e preservar a revisão humana antes de qualquer abordagem.

## Status atual

As Sprints 1 a 3 estão implementadas e validadas com Docker Desktop e PostgreSQL real. A base contém autenticação administrativa local e o fluxo operacional mínimo para cadastrar, consultar, editar e arquivar empresas com categoria, cidade, UF, origem e estado inicial `NEW`.

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
- interface responsiva com o selo oficial da ABC Solutions no rodapé.

## Fora do escopo inicial

- coleta automatizada ou scraping de plataformas externas;
- envio automático ou em massa de mensagens;
- geração de websites, demonstrações ou propostas;
- IA generativa;
- microsserviços, Kubernetes, Redis e filas;
- oferta pública ou modelo SaaS antes de um novo projeto formal;
- deploy de produção antes da Fase 12.

## Evolução planejada

O desenvolvimento seguirá fases pequenas. As Fases 1 a 13 compõem o produto interno e a conclusão da Fase 13 representa 100% do escopo principal. A eventual evolução para SaaS é um projeto futuro independente. Consulte [ROADMAP.md](ROADMAP.md).

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

A futura interface deverá exibir no rodapé o selo oficial da ABC Solutions, centralizado e responsivo, com texto alternativo descritivo e a assinatura **“Developed by Abc Solutions | Built with quality and care”**.

O asset de referência está atualmente em `C:\Projetos\Abc\developed by abc solutions.png`. Ele não foi copiado nesta fase; a futura cópia deverá ser mantida localmente neste repositório e sua origem registrada.

## Referência de desenvolvimento

Este projeto segue o `ABC-Development-Standard`, consultado somente para padrões de processo, documentação, arquitetura, segurança, testes e identidade visual.
