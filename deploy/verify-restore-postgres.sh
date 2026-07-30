#!/bin/sh
set -eu

STACK_DIR="${STACK_DIR:-/srv/stacks/apps/prospect}"
COMPOSE_FILE="${COMPOSE_FILE:-${STACK_DIR}/compose.yaml}"
ENV_FILE="${ENV_FILE:-${STACK_DIR}/prospect.env}"

[ "${1:-}" = "--confirm-disposable" ] || {
  echo "Uso: $0 --confirm-disposable /caminho/backup.dump" >&2
  exit 1
}

backup_path="${2:-}"
[ -f "$backup_path" ] || {
  echo "Backup nao encontrado: $backup_path" >&2
  exit 1
}

restore_db="abc_prospect_restore_check_$(date -u +%Y%m%d%H%M%S)"
container_backup="/tmp/restore-check.dump"

cleanup() {
  docker exec abc-prospect-db rm -f "$container_backup" >/dev/null 2>&1 || true
  docker exec abc-prospect-db sh -ec \
    'dropdb -U "$POSTGRES_USER" --if-exists "$1"' sh "$restore_db" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

docker exec abc-prospect-db sh -ec \
  'createdb -U "$POSTGRES_USER" "$1"' sh "$restore_db"
docker cp "$backup_path" "abc-prospect-db:${container_backup}"
docker exec abc-prospect-db sh -ec \
  'pg_restore -U "$POSTGRES_USER" --dbname "$1" --exit-on-error --no-owner --no-acl "$2"' \
  sh "$restore_db" "$container_backup"

docker exec abc-prospect-db sh -ec \
  'psql -U "$POSTGRES_USER" -d "$1" -v ON_ERROR_STOP=1 -Atc "SELECT version_num FROM alembic_version;"' \
  sh "$restore_db"

echo "Restauracao descartavel validada: $restore_db"
