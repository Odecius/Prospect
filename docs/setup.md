# Setup de desenvolvimento

## Estado atual

A fundação técnica pode ser executada localmente com Docker. É necessário ter Docker Engine e Docker Compose disponíveis.

## Execução local

1. Copie `.env.example` para `.env` e substitua todas as credenciais fictícias.
2. Execute `docker compose up --build -d`.
3. Aplique a migration de autenticação com `docker compose exec app alembic upgrade head`.
4. Acesse `http://127.0.0.1:8000/health` e a documentação em `http://127.0.0.1:8000/docs`.

Para parar sem apagar o banco, use `docker compose down`. A remoção do volume nunca faz parte do fluxo padrão.

## Verificações da fundação técnica

Antes de concluir a Fase 1, o setup deverá verificar:

1. versões suportadas de Docker e Docker Compose;
2. cópia de `.env.example` para `.env` local, sem valores reais versionados;
3. inicialização do PostgreSQL e da aplicação via Compose;
4. aplicação e reversão controlada da migration de autenticação;
5. execução de testes;
6. parada e limpeza sem apagar volumes por padrão.

## Requisitos de reprodutibilidade

- versões de runtime e dependências fixadas;
- healthchecks para aplicação e banco;
- dados de desenvolvimento fictícios;
- banco de teste separado;
- instruções compatíveis com PowerShell e com o ambiente Linux de execução quando aplicável.

## Segurança

- `.env`, bancos locais, logs e credenciais deverão ser ignorados;
- documentação nunca mostrará senhas, tokens ou endpoints privados reais;
- PostgreSQL será acessível apenas pela rede necessária;
- scripts não deverão executar migrations destrutivas ou apagar volumes implicitamente.

O checklist detalhado está em [`../SECURITY.md`](../SECURITY.md). Em 2026-07-20, os comandos foram confirmados com Docker Desktop: ambos os containers ficaram saudáveis, `/health` respondeu localmente e a migration de autenticação aplicou, reverteu e reaplicou no PostgreSQL real.

## Autenticação local

Depois de aplicar `docker compose exec app alembic upgrade head`, crie o primeiro administrador explicitamente no PowerShell. A senha fica somente numa variável temporária do processo e não deve ser salva no repositório:

```powershell
$env:ADMIN_EMAIL = "seu-email@example.com"
$env:ADMIN_DISPLAY_NAME = "Seu nome"
$env:ADMIN_PASSWORD = [Net.NetworkCredential]::new("", (Read-Host "Senha" -AsSecureString)).Password
docker compose exec -e ADMIN_EMAIL -e ADMIN_DISPLAY_NAME -e ADMIN_PASSWORD app python -m scripts.create_admin
Remove-Item Env:ADMIN_EMAIL, Env:ADMIN_DISPLAY_NAME, Env:ADMIN_PASSWORD
```

O comando falha se o email já existir. Os endpoints disponíveis são `POST /auth/login`, `POST /auth/logout` e `GET /auth/session`; o token retornado pelo login deve ser enviado em `X-CSRF-Token` no logout e nas futuras operações mutáveis autenticadas.
