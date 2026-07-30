# Runbook operacional

## Escopo e regra de parada

Este runbook prepara uma operação interna de instância única. Ele não autoriza exposição
pública, uso de dados reais em testes nem ativação automática de integrações. Pare o
procedimento diante de segredo exposto, backup não restaurável, migration sem plano,
healthcheck instável, acesso além da rede aprovada ou divergência entre SHA, imagem e
documentação.

## Pré-publicação

- [ ] revisão e CI aprovados no SHA exato;
- [ ] imagem vinculada ao SHA e referenciada por digest imutável;
- [ ] inventário de dependências e vulnerabilidades revisado;
- [ ] arquivo de ambiente fora do repositório, permissões restritas e sem placeholders;
- [ ] `id odecio` mostra o grupo `docker`;
- [ ] `sudo -u odecio docker info >/dev/null` termina com sucesso;
- [ ] `DATABASE_URL` usa credencial codificada para URL e conecta somente ao serviço `db`;
- [ ] banco sem porta publicada;
- [ ] proxy HTTPS e acesso privado validados;
- [ ] CIDR local confirmado no HP com `ip -4 addr show` e `ip route`;
- [ ] Access List permite somente o CIDR confirmado e nega todo o restante;
- [ ] aplicação e PostgreSQL não publicam portas no host;
- [ ] integrações externas desativadas ou aprovadas individualmente;
- [ ] migration atual e migration alvo registradas;
- [ ] backup recente restaurado com sucesso em ambiente descartável;
- [ ] digest anterior e procedimento de rollback disponíveis;
- [ ] janela, responsáveis e critérios de abortar registrados.

## Publicação controlada

1. Registre horário, operador, SHA, digest anterior e novo digest.
2. Confirme espaço em disco, saúde do banco e validade do certificado.
3. Produza o backup e valide seu checksum e criptografia.
4. Execute `alembic upgrade head` uma única vez, em processo controlado.
5. Atualize somente a imagem da aplicação e aguarde `/ready`.
6. Valide login/logout, dashboard, pesquisa, cadastro e um fluxo de leitura.
7. Confirme ausência de erros, segredos e conteúdo pessoal desnecessário nos logs.
8. Registre o resultado e encerre a janela.

No primeiro deploy, `alembic upgrade head` somente pode ser executado depois de revisar
`alembic current`, `alembic heads` e o SQL das migrations. Não executar downgrade,
remoção de volume ou restauração sobre o banco ativo.

### Checkout reproduzível

O mesmo procedimento atende primeiro deploy e atualizações:

```bash
APPROVED_SHA="<SHA_APROVADO>"
REPO=/srv/apps/prospect

if [ -d "$REPO/.git" ]; then
  git -C "$REPO" fetch --prune origin
else
  git clone --no-checkout https://github.com/Odecius/Prospect.git "$REPO"
  git -C "$REPO" fetch --prune origin
fi

git -C "$REPO" cat-file -e "${APPROVED_SHA}^{commit}"
git -C "$REPO" checkout --detach "$APPROVED_SHA"
test "$(git -C "$REPO" rev-parse HEAD)" = "$APPROVED_SHA"
```

Não usar apenas `git pull origin main`, pois a branch pode mudar depois da aprovação.

### Preservação do arquivo de ambiente

```bash
ENV_FILE=/srv/stacks/apps/prospect/prospect.env
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

if sudo test -f "$ENV_FILE"; then
  sudo cp -a "$ENV_FILE" "${ENV_FILE}.pre-update.${STAMP}"
  sudo chmod 600 "${ENV_FILE}.pre-update.${STAMP}"
else
  sudo install -m 0600 -o odecio -g odecio /dev/null "$ENV_FILE"
fi

sudo chown odecio:odecio "$ENV_FILE"
sudo chmod 600 "$ENV_FILE"

sudo find "$(dirname "$ENV_FILE")" -maxdepth 1 -type f \
  -name 'prospect.env.pre-update.*' -exec chmod 600 {} +

sudo sh -c '
  find "$1" -maxdepth 1 -type f -name "prospect.env.pre-update.*" \
    -printf "%T@ %p\0" |
  sort -z -nr |
  tail -z -n +6 |
  cut -z -d " " -f 2- |
  xargs -0 -r rm --
' sh "$(dirname "$ENV_FILE")"
```

O arquivo nunca é recriado incondicionalmente. Em atualizações, seu conteúdo é preservado
e uma cópia datada com permissão `600` é criada antes de qualquer edição. A rotação mantém
somente as cinco cópias mais recentes.

### Acesso do operador ao Docker

Antes de criar diretórios, imagens ou containers:

```bash
id odecio
sudo -u odecio docker info >/dev/null
```

O grupo `docker` deve aparecer em `id odecio` e o segundo comando deve terminar com
sucesso. Não alterar diretamente proprietário, grupo ou modo do socket Docker.

### Imagem anterior e rollback

Antes de uma atualização, se o container existir:

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
CURRENT_IMAGE="$(docker inspect --format='{{.Config.Image}}' abc-prospect-app)"
CURRENT_IMAGE_ID="$(docker image inspect --format='{{.Id}}' "$CURRENT_IMAGE")"
ROLLBACK_TAG="abc-prospect:rollback-${STAMP}"

docker tag "$CURRENT_IMAGE" "$ROLLBACK_TAG"
printf '%s\n' \
  "current_image=${CURRENT_IMAGE}" \
  "current_image_id=${CURRENT_IMAGE_ID}" \
  "rollback_tag=${ROLLBACK_TAG}"
```

Para rollback sem alteração incompatível de schema, definir `APP_IMAGE` com
`ROLLBACK_TAG` e recriar somente `app`. Não remover volumes.

### UID/GID do PostgreSQL

O Compose usa exatamente:

```text
postgres:17.5-alpine@sha256:6567bca8d7bc8c82c5922425a0baee57be8402df92bae5eacad5f01ae9544daa
```

O diretório persistente deve usar UID/GID obtidos dessa mesma referência:

```bash
POSTGRES_IMAGE='postgres:17.5-alpine@sha256:6567bca8d7bc8c82c5922425a0baee57be8402df92bae5eacad5f01ae9544daa'
PG_UID="$(docker run --rm "$POSTGRES_IMAGE" id -u postgres)"
PG_GID="$(docker run --rm "$POSTGRES_IMAGE" id -g postgres)"
```

### Registro das migrations

Antes do upgrade:

```bash
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic heads
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic current
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic history
```

Após checkpoint específico, executar uma única vez:

```bash
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic upgrade head
```

Depois do upgrade:

```bash
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic heads
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic current
docker compose --env-file prospect.env -f compose.yaml run --rm app alembic history
```

Não executar `alembic downgrade`.

## Checklist pós-publicação

- [ ] `/health` retorna somente `{"status":"ok"}`;
- [ ] `/ready` retorna `200` e passa a `503` quando o banco está indisponível;
- [ ] documentação OpenAPI não está disponível em produção;
- [ ] cookie de sessão possui `HttpOnly`, `Secure` e `SameSite=Lax`;
- [ ] HSTS, CSP, `X-Content-Type-Options` e `X-Frame-Options` estão presentes;
- [ ] aplicação é acessível somente pelo caminho de rede aprovado;
- [ ] PostgreSQL não possui porta publicada;
- [ ] containers executam sem novos privilégios e a aplicação não executa como root;
- [ ] logs rotacionam e não contêm credenciais;
- [ ] auditoria e IA permanecem no estado explicitamente aprovado;
- [ ] métricas básicas de disponibilidade, disco e falha de backup estão ativas.

## Rollback

Para falha sem mudança incompatível de schema, restaure `APP_IMAGE` ao digest anterior e
repita o checklist. Para mudança de schema incompatível, interrompa a escrita, preserve a
instância e siga o plano específico da migration. Restaure o backup em banco separado,
valide-o e só então planeje a troca. Downgrade e restauração sobre o banco ativo exigem
decisão humana explícita porque podem apagar dados.

## Teste de recuperação da Sprint 14

Em 2026-07-23, um PostgreSQL 17.5 descartável recebeu uma tabela e um registro sentinela,
gerou dump custom com `pg_dump`, teve o banco recriado, restaurou com `pg_restore` e
recuperou o valor esperado. O teste não usou o volume de desenvolvimento nem dados reais.

Repetir o exercício após mudanças relevantes e periodicamente no ambiente operacional.
Registrar duração, tamanho, checksum, resultado e responsável, sem registrar conteúdo do
backup.

No HP, o teste aprovado usa:

```bash
LATEST_BACKUP="$(find /srv/backups/apps/prospect -maxdepth 1 -type f \
  -name 'abc-prospect.production.*.dump' | sort | tail -n 1)"

if [ -z "$LATEST_BACKUP" ] || [ ! -f "$LATEST_BACKUP" ]; then
  echo "Nenhum backup valido encontrado." >&2
  exit 1
fi

sha256sum --check "${LATEST_BACKUP}.sha256"

/srv/stacks/apps/prospect/verify-restore-postgres.sh \
  --confirm-disposable "$LATEST_BACKUP"
```

O script cria e remove somente o banco descartável que ele próprio nomeou. O banco
`abc_prospect` e o volume persistente não são removidos.

## Incidente

1. Restrinja o acesso e preserve evidências técnicas mínimas.
2. Não copie tokens, cookies, dumps ou dados pessoais para chat/ticket.
3. Registre início, impacto, versão e ações.
4. Rotacione credenciais potencialmente expostas.
5. Recupere primeiro em ambiente isolado.
6. Avalie obrigações contratuais e de LGPD com responsável e apoio jurídico.
7. Documente causa, correção e prevenção antes de reabrir o serviço.
