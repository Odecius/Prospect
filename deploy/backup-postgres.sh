#!/bin/sh
set -eu

umask 077

STACK_DIR="${STACK_DIR:-/srv/stacks/apps/prospect}"
COMPOSE_FILE="${COMPOSE_FILE:-${STACK_DIR}/compose.yaml}"
ENV_FILE="${ENV_FILE:-${STACK_DIR}/prospect.env}"
BACKUP_DIR="${BACKUP_DIR:-/srv/backups/apps/prospect}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

case "$BACKUP_RETENTION_DAYS" in
  ''|*[!0-9]*) echo "BACKUP_RETENTION_DAYS deve ser um numero inteiro." >&2; exit 1 ;;
esac

[ "$BACKUP_RETENTION_DAYS" -ge 1 ] || {
  echo "BACKUP_RETENTION_DAYS deve ser maior que zero." >&2
  exit 1
}

[ -f "$COMPOSE_FILE" ] || {
  echo "Compose nao encontrado: $COMPOSE_FILE" >&2
  exit 1
}

[ -f "$ENV_FILE" ] || {
  echo "Arquivo de ambiente nao encontrado: $ENV_FILE" >&2
  exit 1
}

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

timestamp="$(date -u +%Y-%m-%dT%H%M%SZ)"
final_path="${BACKUP_DIR}/abc-prospect.production.${timestamp}.dump"
temporary_path="${final_path}.partial"

cleanup() {
  rm -f "$temporary_path"
}
trap cleanup EXIT INT TERM

docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  exec -T db \
  sh -ec 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$temporary_path"

[ -s "$temporary_path" ] || {
  echo "Backup vazio; publicacao abortada." >&2
  exit 1
}

docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  exec -T db \
  pg_restore --list < "$temporary_path" > /dev/null

mv "$temporary_path" "$final_path"
sha256sum "$final_path" > "${final_path}.sha256"

find "$BACKUP_DIR" -maxdepth 1 -type f \
  \( -name 'abc-prospect.production.*.dump' -o -name 'abc-prospect.production.*.dump.sha256' \) \
  -mtime "+${BACKUP_RETENTION_DAYS}" -delete

trap - EXIT INT TERM
echo "Backup concluido: $(basename "$final_path")"
