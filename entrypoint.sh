#!/bin/sh
set -e 

echo "Esperando a PostgreSQL... ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p 5432 -U "${POSTGRES_USER:-todo}" -q; do
  sleep 1
done

if [ -d /opt/static-dist ]; then
  echo "Sincronizando archivos estáticos para NGINX..."
  cp -r /opt/static-dist/. /app/app/static/
fi

if [ -d migrations ]; then
  echo "Aplicando migraciones..."
  flask db upgrade
fi

exec "$@"