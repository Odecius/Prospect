# AI Notes

## Resumo para retomada

- Projeto: ABC Prospect.
- Estado: Sprints 1 a 3 concluídas e validadas com Docker Desktop e PostgreSQL real. Cadastro essencial, taxonomia inicial, origem, duplicidade forte, auditoria básica e interface operacional estão implementados.
- Objetivo imediato: Sprint 4 — contatos, fontes avançadas e candidatos persistentes de duplicidade, após aprovação detalhada do escopo.
- Operação pendente: a pessoa responsável deve criar a conta administrativa real pelo comando documentado em `docs/setup.md`; a conta fictícia usada nos testes foi removida.
- Arquitetura escolhida: monólito modular FastAPI + PostgreSQL.
- Interface planejada: operação mínima nas fases iniciais; consolidação responsiva e branding na Fase 6, com Jinja2, HTML, CSS e JavaScript simples.
- Escopo principal: Fases 1 a 13; SaaS é um projeto futuro independente.
- Foco inicial: uso interno e empresas brasileiras.
- Contato comercial: sempre revisado e iniciado por pessoa; sem envio em massa.

## Leitura obrigatória

Leia `AI_GUIDELINES.md`, `PROJECT_CONTEXT.md`, `docs/glossary.md` e `docs/business_rules.md` antes de agir. Consulte `TODO.md`, `ROADMAP.md`, `DECISIONS.md`, `docs/traceability.md` e `docs/sprint_plan.md` para escopo, pendências, execução e relação entre decisões e fases.

## Restrições relevantes

- Não acessar ou alterar outros projetos, exceto consultar o padrão oficial quando autorizado.
- Não copiar implementações existentes.
- Não fazer commit, push ou deploy sem solicitação explícita.
- Não criar integrações externas nem assumir permissão de scraping.
- Não armazenar segredos ou dados reais em exemplos/testes.

## Branding

O selo ainda não foi copiado. Quando a interface for implementada, copiar o asset oficial para este repositório com origem documentada e inseri-lo no rodapé centralizado e responsivo, com texto alternativo e assinatura oficial.

## Decisões e bloqueios

Autenticação local, campos mínimos, estados do funil, interface operacional mínima e término na Fase 13 foram aprovados. As pendências restantes bloqueiam somente as fases indicadas em `DECISIONS.md`; o score, em particular, não bloqueia o cadastro da Fase 2.
