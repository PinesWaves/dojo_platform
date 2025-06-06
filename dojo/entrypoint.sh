#!/bin/sh

set -e

echo "Waiting for PostgreSQL at $DOJO_DB_HOST:$DOJO_DB_PORT..."

while ! nc -z "$DOJO_DB_HOST" "$DOJO_DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL is available"

mkdir -p /app/dojo/logs
chmod -R 777 /app/dojo/logs

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Iniciar Gunicorn en modo producción
gunicorn dojo.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile /app/dojo/logs/access.log \
    --error-logfile /app/dojo/logs/error.log \
    --capture-output \
    --log-level info

exec "$@"
