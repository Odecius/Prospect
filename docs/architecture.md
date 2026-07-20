# Visão operacional da arquitetura

Este documento orienta a navegação da arquitetura durante a implementação. A especificação canônica está em [`../ARCHITECTURE.md`](../ARCHITECTURE.md), e o modelo conceitual em [`../DATA_MODEL.md`](../DATA_MODEL.md).

## Mapa de responsabilidades

| Área | Responsabilidade | Não deve fazer |
|---|---|---|
| `app/api` | HTTP, validação de borda, dependências e respostas | regra de negócio ou SQL direto |
| `app/services` | casos de uso, autorização e transações | depender de templates |
| `app/domain` | regras de negócio e tipos centrais | importar FastAPI/SQLAlchemy |
| `app/repositories` | contratos e consultas de persistência | decidir fluxo comercial |
| `app/database` | sessão, modelos e infraestrutura Alembic | expor detalhes ao domínio |
| `app/integrations` | provedores externos futuros | acoplar domínio a fornecedor |
| `app/templates` e `app/static` | apresentação interna responsiva | aplicar autorização apenas no cliente |

## Fluxo de alteração

1. identificar o caso de uso e a decisão relacionada;
2. alterar primeiro regra/contrato, depois adaptadores;
3. criar migration explícita quando o schema mudar;
4. cobrir regra com teste unitário e persistência/HTTP conforme o risco;
5. atualizar documentação e changelog;
6. revisar segurança e estado Git.

## Regras arquiteturais

- monólito modular e um deploy;
- dependências apontam das bordas para regras centrais;
- transações delimitadas no caso de uso;
- integrações sempre isoladas e desativadas por padrão até aprovação;
- eventos de auditoria não substituem logs técnicos;
- nenhuma complexidade futura será criada apenas “para preparar”.

## Branding

Interfaces operacionais mínimas podem existir antes do trabalho visual completo. Na Fase 6, o asset oficial será mantido localmente e exibido em rodapé centralizado e responsivo com texto alternativo. Consulte a decisão de branding em [`../DECISIONS.md`](../DECISIONS.md).
