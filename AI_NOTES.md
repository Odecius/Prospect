# AI Notes

## Resumo para retomada

- Projeto: ABC Prospect.
- Estado: Sprints 1 a 11 concluídas e validadas, totalizando 80%. Google Places, auditoria controlada de websites e rascunhos comerciais assistidos estão implementados sem chamadas reais nos testes.
- Objetivo imediato: Sprint 12, diagnóstico comercial e rascunho de proposta com revisão humana; antes de produção, concluir controles de custo, saída de rede e validações jurídicas aplicáveis.
- Operação pendente: a pessoa responsável deve criar a conta administrativa real pelo comando documentado em `docs/setup.md`; a conta fictícia usada nos testes foi removida.
- Arquitetura escolhida: monólito modular FastAPI + PostgreSQL.
- Interface planejada: operação mínima nas fases iniciais; consolidação responsiva e branding na Fase 6, com Jinja2, HTML, CSS e JavaScript simples.
- Escopo principal: Fases 1 a 13; SaaS é um projeto futuro independente.
- Foco inicial: uso interno e empresas brasileiras.
- Contato comercial: sempre revisado e iniciado por pessoa; sem envio em massa.
- Limite arquitetural: o ABC Prospect não gera sites, landing pages, demos, código, logos nem publicações. Um eventual gerador é outro produto, com arquitetura e repositório próprios.

## Leitura obrigatória

Leia `AI_GUIDELINES.md`, `PROJECT_CONTEXT.md`, `docs/glossary.md` e `docs/business_rules.md` antes de agir. Consulte `TODO.md`, `ROADMAP.md`, `DECISIONS.md`, `docs/traceability.md` e `docs/sprint_plan.md` para escopo, pendências, execução e relação entre decisões e fases.

## Restrições relevantes

- Não acessar ou alterar outros projetos, exceto consultar o padrão oficial quando autorizado.
- Não copiar implementações existentes.
- Não fazer commit, push ou deploy sem solicitação explícita.
- Não criar integrações externas nem assumir permissão de scraping.
- Não armazenar segredos ou dados reais em exemplos/testes.
- Avançar sprints sem solicitar aprovações ordinárias; interromper somente diante de segurança, privacidade, credenciais, perda de dados ou efeito externo relevante.

## Branding

O selo oficial já está armazenado localmente, com origem documentada, e é exibido no rodapé responsivo da interface.

## Decisões e bloqueios

Autenticação local, campos mínimos, estados do funil, interface operacional mínima e término na Fase 13 foram aprovados. As pendências restantes bloqueiam somente as fases indicadas em `DECISIONS.md`; o score, em particular, não bloqueia o cadastro da Fase 2.
