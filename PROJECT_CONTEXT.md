# Contexto do Projeto

## Produto

O ABC Prospect será uma aplicação interna da ABC Solutions para organizar a identificação e qualificação de empresas brasileiras com boa reputação e presença digital fraca. O valor inicial está em substituir anotações dispersas por um fluxo manual, rastreável e priorizado.

## Estado

Em 2026-07-22, as Sprints 1 a 11 estão implementadas e validadas, totalizando 80%. Além da infraestrutura, autenticação e cadastro, existem contatos, duplicidade revisável, pesquisa, score explicável, pipeline, interface responsiva, Google Places API (New), auditoria controlada de websites e rascunhos de IA revisáveis. As migrations formam uma cadeia linear até `20260722_0009`.

## Usuário e mercado iniciais

- uso por uma única pessoa no início;
- foco inicial em empresas brasileiras;
- expansão geográfica e multiusuário somente após validação.

## Princípios do produto

- simplicidade antes de escala;
- cadastro manual antes de automação;
- score explicável, não uma decisão automática;
- origem e qualidade dos dados sempre visíveis;
- revisão humana antes de contato comercial;
- privacidade, termos de uso e prevenção de spam como restrições de produto.

## Limites atuais

Permanecem fora do escopo: scraping, pentest, envio em massa e infraestrutura complexa. IA, demonstrações e propostas pertencem somente às sprints futuras correspondentes. O produto interno termina na Fase 13; SaaS é um projeto futuro independente.

## Decisões operacionais vigentes

- autenticação local inicial com sessão;
- categoria, cidade, UF e origem obrigatórias no cadastro;
- `pipeline_status` iniciado em `NEW`, com estados controlados;
- score calculado posteriormente, sem bloquear o cadastro;
- interface operacional mínima permitida antes da consolidação visual da Fase 6.

## Referências internas

- Visão e escopo: `README.md`
- Arquitetura detalhada: `ARCHITECTURE.md`
- Modelo de dados: `DATA_MODEL.md`
- Fases: `ROADMAP.md`
- Decisões: `DECISIONS.md`
- Segurança: `SECURITY.md`
- Matriz de rastreabilidade: `docs/traceability.md`
- Glossário oficial: `docs/glossary.md`
- Regras de negócio: `docs/business_rules.md`
- Plano de sprints: `docs/sprint_plan.md`

## Padrão ABC Solutions

O projeto herda do `ABC-Development-Standard`: documentação em português do Brasil, simplicidade arquitetural, separação de responsabilidades, registros de decisão, segurança por padrão, testes proporcionais ao risco, Git disciplinado e branding oficial.

## Branding futuro

A interface futura usará, no rodapé, o selo oficial centralizado e responsivo e a assinatura **“Developed by Abc Solutions | Built with quality and care”**. O arquivo de origem `C:\Projetos\Abc\developed by abc solutions.png` será copiado somente na fase autorizada de interface.
