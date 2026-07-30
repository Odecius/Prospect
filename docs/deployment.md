# Operação segura

## Estado

A Sprint 14 preparou e validou localmente os artefatos operacionais. Nenhum servidor foi
alterado e nenhum deploy foi realizado. O primeiro uso em Ubuntu continua condicionado à
aprovação da infraestrutura, do acesso privado, do proxy HTTPS, do armazenamento de
segredos e dos objetivos de recuperação.

## Topologia preparada

O arquivo `compose.production.yaml` descreve uma implantação conservadora:

- imagem da aplicação identificada por versão ou digest imutável;
- aplicação sem privilégios adicionais, filesystem somente leitura e `/tmp` temporário;
- nenhuma porta da aplicação ou do banco publicada no host;
- aplicação conectada à rede Docker externa `proxy` como `abc-prospect-app`;
- rede `backend` interna e exclusiva da aplicação e do PostgreSQL;
- PostgreSQL sem porta publicada e dados persistidos em `POSTGRES_DATA_PATH`;
- PostgreSQL fixado em `postgres:17.5-alpine` pelo digest
  `sha256:6567bca8d7bc8c82c5922425a0baee57be8402df92bae5eacad5f01ae9544daa`;
- credenciais fornecidas externamente, sem valores padrão;
- integrações externas desativadas por padrão;
- logs JSON rotacionados em cinco arquivos de 10 MB;
- liveness em `/health` e readiness com consulta mínima ao banco em `/ready`;
- reinício automático e healthchecks com períodos de inicialização.

O proxy deverá ser o único componente exposto, exigir HTTPS e restringir o acesso por
VPN, rede privada ou uma camada de identidade aprovada. O Compose não instala nem
configura esse controle externo.

No servidor HP, o Proxy Host usará `abc-prospect-app:8000`. A Access List deverá permitir
somente o CIDR confirmado por `ip -4 addr show` e `ip route`, negando todo o restante.
Nenhum CIDR pode ser presumido ou liberado provisoriamente.

## Configuração

1. Construa, teste, publique e assine a imagem por um processo controlado.
2. Copie `deploy/production.env.example` para um arquivo fora do repositório.
3. Substitua todos os placeholders e use `APP_IMAGE` com digest `sha256`.
4. Gere `APP_SECRET_KEY` e `POSTGRES_PASSWORD` aleatórios e independentes.
   Em `DATABASE_URL`, aplique codificação URL aos caracteres reservados da senha.
5. Mantenha auditoria de websites e IA desativadas até seus controles específicos.
6. Valide sem iniciar serviços:

   `docker compose --env-file /caminho/seguro/production.env -f compose.production.yaml config --quiet`

Diretórios aprovados para o servidor HP:

- `/srv/apps/prospect` para o checkout;
- `/srv/stacks/apps/prospect` para Compose, ambiente e scripts;
- `/srv/data/apps/prospect/postgres` para dados persistentes;
- `/srv/backups/apps/prospect` para dumps e checksums.

Configuração de produção rejeita segredo conhecido de desenvolvimento, banco diferente de
PostgreSQL e a senha de desenvolvimento presente na URL. Valores de segredo nunca devem
ser impressos em logs ou anexados a tickets.

## Backup e restauração

Backups devem usar `pg_dump` no formato custom, ser criptografados antes de sair do host e
ser armazenados com menor privilégio em destino separado. O nome recomendado contém data,
ambiente e versão.

Para o piloto interno, `deploy/backup-postgres.sh` executa diariamente às 03:30 no horário
de Londres, valida o arquivo com `pg_restore --list`, grava checksum SHA-256 e mantém 30
dias. O RPO aprovado é 24 horas e o RTO aprovado é 4 horas.

`deploy/verify-restore-postgres.sh` exige `--confirm-disposable`, cria um banco temporário
com nome exclusivo, restaura e consulta `alembic_version`. O banco ativo nunca é substituído.

Uma restauração nunca deve ser testada sobre o banco ativo. Crie um PostgreSQL descartável,
restaure com `pg_restore --exit-on-error --no-owner --no-acl` e verifique migrations,
contagens mínimas, autenticação e fluxos críticos.

## Publicação e rollback

O procedimento completo está em [operations-runbook.md](operations-runbook.md). Em resumo:

1. registrar SHA do commit, digest da imagem e migration atual;
2. obter e verificar backup restaurável;
3. executar migrations como etapa única e explícita;
4. iniciar a imagem imutável;
5. validar `/health`, `/ready`, login, páginas autenticadas e logs;
6. interromper a publicação se algum critério falhar;
7. para rollback de código, restaurar o digest anterior;
8. para schema incompatível, seguir o plano específico da migration ou restaurar em uma
   instância separada; nunca executar downgrade destrutivo por reflexo.

## Decisões ainda externas ao código

- servidor, hardening e política de atualizações do Ubuntu;
- VPN/rede privada/camada de identidade;
- proxy, domínio e certificados;
- secret manager e responsáveis pelo acesso;
- RPO, RTO, retenção, criptografia e destino de backup;
- monitoramento, alertas e plantão;
- janela e responsável por migration, rollback e restauração.

Essas decisões são bloqueios do deploy real, não lacunas escondidas no código.
