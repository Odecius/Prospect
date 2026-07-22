# Estratégia de testes

## Estado atual

Existem testes unitários, funcionais, de segurança e de configuração. Com o ambiente virtual ativo, execute `ruff check .`, `ruff format --check .` e `pytest -q`. As migrations são exercitadas em ciclo reversível no PostgreSQL real. Integrações externas, auditorias e IA usam fakes nos testes e nunca acessam serviços reais por padrão.

## Pirâmide planejada

- **Unitários:** normalização, score, duplicidade, estados e validações de domínio.
- **Integração:** repositórios, constraints, transações e migrations contra PostgreSQL de teste.
- **Funcionais:** autenticação, autorização, formulários e rotas críticas FastAPI/Jinja2.
- **Segurança:** acessos negados, CSRF quando aplicável, validação, sanitização de logs e não exposição de detalhes.

## Regras

- cada bug corrigido recebe teste de regressão quando reproduzível;
- testes não usam serviços externos reais por padrão;
- fixtures usam somente dados fictícios;
- mocks ficam nos limites externos, não escondem o banco onde seu comportamento importa;
- testes devem ser determinísticos e independentes de ordem;
- qualquer migration deve ser exercitada em banco limpo e em cenário de upgrade pertinente;
- comandos reais só serão documentados depois de existirem e passarem localmente.

## Gate automático de pull request

O workflow `.github/workflows/ci.yml` executa em cada pull request:

1. instalação reproduzível das dependências de desenvolvimento;
2. `python -m ruff check .`;
3. `python -m ruff format --check .`;
4. `python -m pytest -q`;
5. `alembic upgrade head` em PostgreSQL 17.5 descartável;
6. `alembic downgrade base`;
7. novo `alembic upgrade head` e confirmação da revisão atual.

O job possui somente permissão de leitura do conteúdo, não recebe chaves reais e mantém IA e Google Places desativados. Um PR não deve ser mesclado enquanto esse gate estiver ausente, pendente ou falhando.

## Prioridades iniciais

1. constraints de CNPJ e referências de fonte;
2. candidatos a duplicidade sem merge automático;
3. categoria, cidade, UF, origem e estado inicial `NEW` obrigatórios;
4. autorização em todas as operações;
5. cálculo e versionamento de score somente a partir da Fase 4;
6. transições do funil e revisão humana de mensagens;
7. logs sem conteúdo sensível.

## Interface e branding

Interfaces operacionais mínimas das fases iniciais devem receber testes funcionais dos fluxos que habilitam. Na Fase 6, as verificações serão ampliadas para desktop, tablet e celular, ausência de overflow, navegação por teclado, alt text e presença do selo oficial centralizado no rodapé.

Os critérios do produto estão em [`../ROADMAP.md`](../ROADMAP.md), e os riscos em [`../SECURITY.md`](../SECURITY.md).
