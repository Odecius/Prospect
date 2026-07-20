# Proposta da Fase 1B — Autenticação local

**Estado:** aprovada, implementada e validada em 2026-07-20.

Este documento delimita a etapa de autenticação prevista na Fase 1. A validação da Fase 1A e a aprovação explícita deste escopo foram concluídas em 2026-07-20.

## Objetivo

Adicionar autenticação local mínima para uma única pessoa administradora, protegendo futuras rotas de negócio sem antecipar CRUD de empresas, regras comerciais ou interface completa.

## Escopo proposto

- entidade técnica `users`, conforme `DATA_MODEL.md`;
- primeira migration limitada à tabela `users` e ao tipo controlado de status;
- senha armazenada somente como hash Argon2;
- sessão assinada em cookie `HttpOnly`;
- cookie `Secure` obrigatório em produção e `SameSite=Lax`;
- duração máxima inicial de sessão de oito horas;
- endpoints HTTP de login e logout, sem template HTML;
- token CSRF para operações mutáveis autenticadas;
- criação explícita do primeiro administrador por comando local e variáveis de ambiente;
- mensagens genéricas para credenciais inválidas;
- documentação OpenAPI desativada em produção;
- testes unitários, funcionais, de segurança e de migration;
- atualização da documentação operacional e de segurança.

## Variáveis de ambiente propostas

- `APP_SECRET_KEY`: segredo de assinatura com no mínimo 32 caracteres;
- `SESSION_HTTPS_ONLY`: força cookie seguro fora da detecção automática de produção;
- `ADMIN_EMAIL`: email fictício ou real fornecido somente no ambiente local de criação;
- `ADMIN_DISPLAY_NAME`: nome do primeiro administrador;
- `ADMIN_PASSWORD`: senha fornecida somente no ambiente e nunca registrada em logs.

Os valores de `ADMIN_*` serão usados apenas pelo comando explícito de criação e não serão necessários para iniciar a aplicação.

## Endpoints propostos

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/auth/login` | Validar credenciais e iniciar sessão |
| `POST` | `/auth/logout` | Encerrar a sessão atual |
| `GET` | `/auth/session` | Informar se a sessão atual está autenticada |

O endpoint `/health` continuará público. Não haverá página de login, painel ou frontend nesta fase.

## Migration proposta

A primeira revision será pequena, reversível e exclusiva da autenticação. Ela criará:

- enum de status `ACTIVE` e `DISABLED`;
- tabela `users` com UUID, email normalizado único, nome de exibição, hash da senha, status e timestamps previstos no modelo aprovado;
- índice único para email normalizado.

A migration deverá ser aplicada e revertida contra PostgreSQL real de teste. Não será considerada validada apenas por SQL offline.

## Critérios de conclusão

- migration aplica e reverte em PostgreSQL real;
- primeiro administrador é criado por comando explícito e não duplicável;
- senha em texto puro nunca é persistida ou registrada;
- login correto cria sessão e login incorreto retorna mensagem genérica;
- logout invalida a sessão;
- CSRF é exigido nas operações mutáveis autenticadas pertinentes;
- rotas protegidas rejeitam acesso sem sessão;
- cookies cumprem a configuração por ambiente;
- testes e revisão de segurança passam;
- nenhum segredo é rastreado;
- nenhuma entidade ou regra comercial é implementada.

## Fora do escopo

- empresas, categorias, contatos ou fontes;
- pipeline e score;
- CRUD de negócio;
- papéis múltiplos ou permissões comerciais;
- recuperação automática de senha;
- cadastro público;
- login social ou provedor externo;
- interface HTML, painel ou frontend;
- rate limiting distribuído, Redis ou filas;
- integrações externas.

## Dependências propostas

- `argon2-cffi`: hash moderno de senhas;
- `itsdangerous`: assinatura usada pela sessão Starlette.

Novas dependências somente serão adicionadas depois da aprovação desta proposta.

## Validação realizada

- migration aplicada, revertida e reaplicada em PostgreSQL real;
- conta administrativa fictícia criada pelo comando explícito e removida ao final do teste;
- login, sessão, rejeição por CSRF e logout validados por testes funcionais e HTTP real;
- hash Argon2, normalização de email e cookies cobertos por testes;
- nenhuma entidade comercial introduzida.
