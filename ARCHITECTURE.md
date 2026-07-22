# Arquitetura do ABC Prospect

## Objetivo arquitetural

Construir uma aplicação web interna simples, segura e evolutiva, mantendo API, regras de negócio, persistência e interface claramente separadas dentro de um único deploy.

O limite de responsabilidade é estrito: o ABC Prospect apoia prospecção e trabalho comercial. Ele não cria websites, landing pages, demos, código, logos, hosting nem publicações. Um eventual gerador desse tipo será outro produto, com arquitetura e repositório próprios.

## Estilo adotado

Será usado um **monólito modular** em FastAPI. Essa abordagem reduz custo operacional no MVP e preserva limites internos que permitem evolução sem introduzir microsserviços prematuramente.

## Componentes

1. **Interface web:** páginas renderizadas no servidor com Jinja2, complementadas por CSS e JavaScript simples.
2. **API/HTTP:** rotas FastAPI, validação de entrada e tradução de erros para respostas seguras.
3. **Aplicação/serviços:** coordenação dos casos de uso, transações e autorização.
4. **Domínio:** regras de duplicidade, score e fluxos comerciais, sem dependência da camada HTTP.
5. **Persistência:** modelos SQLAlchemy, repositórios e PostgreSQL.
6. **Integrações:** adaptadores futuros para fontes externas e IA, isolados do domínio.

Fluxo principal:

```text
Browser -> Rotas FastAPI -> Serviços de aplicação -> Domínio -> Repositórios -> PostgreSQL
                                      |
                                      +-> Adaptadores externos futuros
```

## Estrutura de pastas

```text
abc-prospect/
├── app/
│   ├── api/                 # rotas, dependências HTTP e tratamento de erros
│   ├── core/                # configuração, segurança e logging
│   ├── domain/              # regras e tipos do negócio
│   ├── services/            # casos de uso
│   ├── repositories/        # contratos e acesso a dados
│   ├── database/            # sessão, modelos SQLAlchemy e base das migrations
│   ├── integrations/        # integrações externas futuras
│   ├── templates/           # templates Jinja2
│   └── static/              # CSS, JavaScript e assets locais
├── migrations/              # Alembic
├── tests/
│   ├── unit/
│   ├── integration/
│   └── functional/
├── docs/
├── scripts/
└── arquivos de configuração
```

A estrutura representa o desenho arquitetural vigente. Parte dela já existe na fundação técnica; os módulos de domínio, serviços, repositórios, integrações e interface serão completados incrementalmente, apenas quando exigidos pela fase em execução.

## Limites e dependências

- rotas não devem conter regras de negócio;
- rotas não devem consultar ou persistir modelos SQLAlchemy diretamente;
- domínio não deve importar FastAPI, SQLAlchemy ou adaptadores externos;
- serviços controlam casos de uso e limites transacionais;
- repositórios encapsulam consultas;
- templates consomem dados preparados pela aplicação;
- integrações externas devem usar interfaces explícitas e ser substituíveis em testes.

## Configuração

Configuração tipada, carregada de variáveis de ambiente. Arquivos `.env` são apenas locais e ignorados pelo Git; `.env.example` contém somente nomes e valores fictícios. Ambientes previstos: desenvolvimento, teste e produção.

## Logs

- logs estruturados para saída padrão;
- nível configurável por ambiente;
- identificador de correlação por requisição;
- registro de eventos técnicos e de auditoria sem senhas, tokens, conteúdo integral de mensagens ou dados pessoais desnecessários;
- falhas externas registradas com contexto mínimo e seguro.

## Tratamento de erros

- exceções de domínio explícitas;
- tradução centralizada para códigos HTTP;
- mensagens úteis ao usuário sem stack trace ou detalhes internos em produção;
- rollback da transação em falhas;
- validação de entrada na borda e regras de negócio no domínio.

## Persistência e migrations

PostgreSQL será a fonte transacional. SQLAlchemy fará o mapeamento e Alembic controlará migrations pequenas, revisáveis e aplicadas explicitamente. Migrations não serão executadas automaticamente na inicialização da aplicação em produção.

O desenho vigente está em [DATA_MODEL.md](DATA_MODEL.md). As migrations são pequenas, explícitas e lineares; a cadeia validada alcança `20260722_0009`. Novas entidades permanecem proibidas até a sprint correspondente ser autorizada.

## Testes

- unitários para score, normalização, duplicidade e regras comerciais;
- integração para repositórios e migrations em PostgreSQL de teste;
- funcionais para autenticação, autorização e fluxos HTTP críticos;
- mocks apenas nos limites externos;
- regressões para bugs corrigidos.

Consulte [docs/testing.md](docs/testing.md).

## Docker Compose local

O Compose local define a aplicação e um PostgreSQL isolado, com healthchecks, volume de desenvolvimento e configuração sem segredos reais. A execução real e a validação de ida e volta da migration de autenticação foram concluídas em 2026-07-20.

## Evolução da interface

Uma interface operacional mínima poderá acompanhar as fases iniciais quando for necessária para executar e validar o cadastro manual. Essa interface deve permanecer simples, acessível e renderizada no servidor, sem antecipar trabalho de identidade visual ou um sistema de design completo.

A Fase 6 consolidou navegação, responsividade, estados visuais, acessibilidade e branding oficial. Novos fluxos devem preservar esses critérios.

## Preparação para Ubuntu Server

O deploy futuro deverá usar containers sem privilégios, proxy reverso com HTTPS, variáveis/segredos externos ao repositório, backups testados, logs com rotação, healthcheck e procedimento de rollback. Detalhes planejados em [docs/deployment.md](docs/deployment.md).

## Interface e branding

O rodapé apresenta o selo oficial ABC Solutions centralizado, responsivo e com texto alternativo descritivo. A assinatura é **“Developed by Abc Solutions | Built with quality and care”** e o asset é local.

## Complexidade deliberadamente evitada

Não serão introduzidos microsserviços, Kubernetes, Redis, filas, SPA ou abstrações de integração sem um caso de uso aprovado e medido.

## IA para rascunhos

O fluxo segue `API -> MessageDraftService -> MessageDraftProvider -> OpenAIResponsesClient`. O serviço controla minimização, `DO_NOT_CONTACT`, estados e persistência; o adaptador conhece somente o protocolo externo. Não há fila, agente, tool calling, memória ou mecanismo de envio.

Na Sprint 12, esse limite poderá ser estendido a diagnósticos comerciais e rascunhos de proposta estruturados, reutilizando o mesmo workflow humano e sem adicionar capacidade de envio, publicação ou criação de sites.
